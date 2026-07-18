import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from pykiwoom_rest.websocket_api import WebSocketAPI, WebSocketContextManager


@pytest.fixture
def ws():
    with patch("pykiwoom_rest.websocket_api.WebSocketClient") as client_cls:
        client = client_cls.return_value
        client.is_connected = True
        client.connect = AsyncMock(return_value=True)
        client.disconnect = AsyncMock()
        client.subscribe = AsyncMock(return_value=True)
        client.unsubscribe = AsyncMock(return_value=True)
        client.register_callback = Mock()
        client._subscriptions = set()
        api = WebSocketAPI("token", "key", "secret")
        api._client = client
        yield api


@pytest.mark.asyncio
async def test_connect_subscribe_callbacks_and_unsubscribe_paths(ws):
    quote_cb = Mock()
    orderbook_cb = Mock()
    trade_cb = Mock()
    assert ws.is_connected and await ws.connect("0A")
    await ws.disconnect()
    assert await ws.subscribe_quote("005930", quote_cb)
    assert await ws.subscribe_orderbook("005930", orderbook_cb)
    assert await ws.subscribe_trade("005930", trade_cb)

    callbacks = [call.args[1] for call in ws._client.register_callback.call_args_list]
    payload = {"values": {"stk_cd": "005930", "stck_prpr": "100", "prdy_vrss": "-2", "prdy_ctrt": "-1.0", "acml_vol": "10"}}
    await callbacks[0](payload)
    await callbacks[1]({"values": {"stk_cd": "005930"}})
    await callbacks[2]({"values": {"stk_cd": "005930", "stck_prpr": "100", "cntg_vol": "2", "stck_cntg_hour": "120000"}})
    assert quote_cb.called and orderbook_cb.called and trade_cb.called
    await callbacks[0]({"values": {"stk_cd": "000660"}})

    assert await ws.unsubscribe_quote("005930")
    assert await ws.unsubscribe_orderbook("005930")
    assert await ws.unsubscribe_trade("005930")
    assert not ws._quote_callbacks and not ws._orderbook_callbacks and not ws._trade_callbacks


@pytest.mark.asyncio
async def test_async_callback_errors_and_unsubscribe_all(ws):
    async def broken(_):
        raise RuntimeError("callback broken")
    await ws.subscribe_quote("005930", broken)
    callback = ws._client.register_callback.call_args.args[1]
    await callback({"values": {"stk_cd": "005930"}})
    ws._client._subscriptions = {"0A:005930", "0D:005930"}
    ws._quote_callbacks["005930"] = Mock()
    ws._orderbook_callbacks["005930"] = Mock()
    await ws.unsubscribe_all()
    assert not ws._quote_callbacks and not ws._orderbook_callbacks


@pytest.mark.asyncio
async def test_orderbook_and_trade_callback_async_error_branches(ws):
    async def orderbook_callback(_):
        return None

    async def broken_trade(_):
        raise RuntimeError("trade callback broken")

    await ws.subscribe_orderbook("005930", orderbook_callback)
    await ws.subscribe_trade("005930", broken_trade)
    orderbook_callback_fn = ws._client.register_callback.call_args_list[0].args[1]
    trade_callback_fn = ws._client.register_callback.call_args_list[1].args[1]
    await orderbook_callback_fn({"values": {"stk_cd": "005930"}})
    await orderbook_callback_fn({"values": {"stk_cd": "000660"}})
    ws._orderbook_callbacks["005930"] = Mock(side_effect=RuntimeError("orderbook callback broken"))
    await orderbook_callback_fn({"values": {"stk_cd": "005930"}})
    await trade_callback_fn({"values": {"stk_cd": "005930"}})
    await trade_callback_fn({"values": {"stk_cd": "000660"}})


def test_parsers_and_numeric_helpers_cover_fallback_shapes(ws):
    assert ws._realtime_values({"body": {"output": {"10": "1"}}}) == {"10": "1"}
    assert ws._realtime_values({"body": {"output": []}}) == {}
    assert ws._first_value({"a": ""}, "a", "b", default="x") == "x"
    assert ws._to_int(None) == 0 and ws._to_int("1.5") == 1
    quote = ws._parse_quote("005930", {"body": {"output": {"10": "-100", "11": "-2", "12": "-1.5", "13": "5"}}})
    assert quote.current_price == 100 and quote.change_price == -2
    orderbook = ws._parse_orderbook("005930", {"values": {}})
    assert len(orderbook.ask_prices) == 10 and orderbook.total_ask_volume == 0
    trade = ws._parse_trade("005930", {"values": {"10": "100", "15": "3", "20": "101010"}})
    assert trade.trade_price == 100 and trade.trade_time == "101010"


def test_context_manager_connect_failure_and_success(ws):
    ws.connect = AsyncMock(side_effect=RuntimeError("connect failed"))
    with pytest.raises(RuntimeError, match="connect failed"):
        with WebSocketContextManager(ws):
            pass
    ws.connect = AsyncMock(return_value=True)
    ws.disconnect = AsyncMock()
    with WebSocketContextManager(ws) as manager:
        assert manager.run(asyncio.sleep(0, result="ok")) == "ok"
