import asyncio
import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from pykiwoom_rest.websocket_client import WebSocketClient


@pytest.fixture
def client():
    return WebSocketClient("wss://api.example.test", "token", "key", "secret", ping_interval=1, ping_timeout=1)


def test_client_configuration_and_message_helpers(client):
    assert not client.is_connected
    client._connected = True
    client._ws = object()
    assert client.is_connected
    assert client._connect_headers("0A")["api-id"] == "0A"
    assert client._subscription_key("0A", "005930") == "0A:005930"
    assert client._build_subscription_message("0A", "005930", "REG")["refresh"] == "1"
    assert "refresh" not in client._build_subscription_message("0A", "005930", "REMOVE")
    with pytest.raises(ValueError, match="wss"):
        WebSocketClient("ws://insecure.test", "t", "k", "s")
    client._connected = True
    client._ws = Mock(closed=True, close_code=1000)
    assert not client.is_connected
    with patch("pykiwoom_rest.websocket_client.inspect.signature", side_effect=ValueError):
        assert "extra_headers" in client._connect_header_kwargs({"x": "y"})
    with patch("pykiwoom_rest.websocket_client.inspect.signature", return_value=Mock(parameters={"additional_headers": object()})):
        assert "additional_headers" in client._connect_header_kwargs({"x": "y"})


@pytest.mark.asyncio
async def test_ack_send_wait_and_resolution(client):
    client._ws = Mock()
    client._ws.send = AsyncMock()
    future = client._create_ack_future("REG", "0A", "005930")
    assert client._resolve_ack({"trnm": "REG", "data": [{"type": ["0A"], "item": ["005930"]}], "return_code": "0"})
    assert await client._wait_for_ack("REG", "0A", "005930", future)

    client._ack_timeout = 0
    future = client._create_ack_future("REG", "0A", "005930")
    assert not await client._wait_for_ack("REG", "0A", "005930", future)
    client._clear_ack_future("REG", "0A", "005930", future)
    assert not client._resolve_ack({"trnm": "OTHER"})
    assert not client._resolve_ack({"trnm": "REG", "data": [{"type": ["x"], "item": ["y"]}]})
    failed = asyncio.get_running_loop().create_future()
    client._pending_acks["failed"] = failed
    client._fail_pending_acks()
    assert isinstance(failed.exception(), ConnectionError)

    client._ws = Mock()
    client._ws.send = AsyncMock()
    client._wait_for_ack = AsyncMock(return_value=True)
    assert await client._send_subscription_message("REG", "0A", "005930")
    client._wait_for_ack = WebSocketClient._wait_for_ack.__get__(client, WebSocketClient)
    failed_future = asyncio.get_running_loop().create_future()
    failed_future.set_exception(ConnectionError("closed"))
    assert not await client._wait_for_ack("REG", "0A", "005930", failed_future)
    bad_future = asyncio.get_running_loop().create_future()
    bad_future.set_result({"return_code": "1", "return_msg": "no"})
    assert not await client._wait_for_ack("REG", "0A", "005930", bad_future)


@pytest.mark.asyncio
async def test_subscribe_unsubscribe_and_message_dispatch(client):
    client._connected = True
    client._ws = Mock(closed=False, close_code=None)
    client._send_subscription_message = AsyncMock(return_value=True)
    callback = Mock()
    assert await client.subscribe("0A", "005930", callback)
    assert await client.subscribe("0A", "005930", callback)
    assert await client.unsubscribe("0A", "005930")
    assert await client.unsubscribe("0A", "005930")

    client.register_callback("0A", callback)
    await client._handle_message(json.dumps({"trnm": "REAL", "data": [{"type": "0A", "item": "005930", "values": {}}]}))
    assert callback.called
    await client._handle_message("not-json")
    await client._handle_message(json.dumps({"type": "0A", "item": "005930"}))
    client._connected = False
    assert not await client.subscribe("0A", "005930")
    assert not await client.unsubscribe("0A", "005930")
    client._connected = True
    client._ws = Mock(closed=False, close_code=None)
    client._send_subscription_message = AsyncMock(side_effect=RuntimeError("send failed"))
    assert not await client.subscribe("0B", "005930")
    client._subscriptions.add("0B:005930")
    assert not await client.unsubscribe("0B", "005930")
    client._send_subscription_message = AsyncMock(return_value=False)
    assert not await client.subscribe("0C", "005930")
    client._subscriptions.add("0C:005930")
    assert not await client.unsubscribe("0C", "005930")
    client._callbacks["0D"] = callback
    client._send_subscription_message = AsyncMock(return_value=True)
    assert await client.subscribe("0D", "005930")


@pytest.mark.asyncio
async def test_restore_and_close_connection(client):
    client._subscriptions = {"0A:005930"}
    callback = Mock()
    client._callbacks["0A:005930"] = callback
    client._send_subscription_message = AsyncMock(return_value=True)
    assert await client._restore_subscriptions()
    client._subscriptions = {"bad"}
    assert not await client._restore_subscriptions()
    client._subscriptions = {"0A:005930"}
    client._send_subscription_message = AsyncMock(return_value=False)
    assert not await client._restore_subscriptions()
    client._send_subscription_message = AsyncMock(return_value=False)
    assert not await client._restore_subscriptions()

    pending = asyncio.get_running_loop().create_future()
    client._pending_acks["x"] = pending
    client._ws = Mock()
    client._ws.close = AsyncMock()
    await client._close_connection(clear_subscriptions=True)
    assert pending.done() and not client._subscriptions
    assert await client._restore_subscriptions()


@pytest.mark.asyncio
async def test_connect_success_failure_and_reconnect_exhaustion(client, monkeypatch):
    ws = Mock(closed=False, close_code=None)
    ws.close = AsyncMock()
    with patch("pykiwoom_rest.websocket_client.websockets.connect", AsyncMock(return_value=ws)):
        client._restore_subscriptions = AsyncMock(return_value=True)
        assert await client.connect()
    await client.disconnect()

    with patch("pykiwoom_rest.websocket_client.websockets.connect", AsyncMock(side_effect=RuntimeError("offline"))):
        assert not await client.connect()
    client._restore_subscriptions = AsyncMock(return_value=False)
    with patch("pykiwoom_rest.websocket_client.websockets.connect", AsyncMock(return_value=Mock(closed=False, close_code=None))):
        assert not await client.connect()
    client._reconnect_attempts_exhausted = True
    assert not await client._attempt_reconnect()
    client._reconnect_attempts_exhausted = False
    client._connected = True
    client._ws = Mock(closed=False, close_code=None)
    assert await client.connect()


@pytest.mark.asyncio
async def test_receive_ping_reconnect_and_callback_management(client, monkeypatch):
    class Messages:
        def __init__(self):
            self.messages = [json.dumps({"type": "0A", "item": "005930"})]

        def __aiter__(self):
            return self

        async def __anext__(self):
            if self.messages:
                return self.messages.pop(0)
            raise RuntimeError("socket failed")

    client._ws = Messages()
    client.auto_reconnect = True
    client._handle_message = AsyncMock()
    client._attempt_reconnect = AsyncMock(return_value=True)
    await client._receive_loop()
    client._handle_message.assert_awaited_once()
    client._attempt_reconnect.assert_awaited_once()
    client._handle_message = WebSocketClient._handle_message.__get__(client, WebSocketClient)

    client._connected = True
    client._ws = Mock(closed=False, close_code=None)
    client._last_message_time = client._last_message_time.replace(year=2000)
    client._attempt_reconnect = AsyncMock(return_value=True)
    monkeypatch.setattr("pykiwoom_rest.websocket_client.asyncio.sleep", AsyncMock())
    await client._ping_loop()
    client._attempt_reconnect.assert_awaited_once()

    client.register_callback("0A", Mock())
    client.register_callback("0A:005930", Mock())
    client.unregister_callback("0A")
    assert not client._callbacks

    async_callback = AsyncMock()
    client.register_callback("0A", async_callback)
    await client._dispatch_callback("0A", None, {"x": 1})
    async_callback.assert_awaited_once()
    await client._dispatch_callback(None, None, {})
    await client._dispatch_callback("0B", "005930", {})
    client._resolve_ack = Mock(return_value=True)
    await client._handle_message(json.dumps({"trnm": "REG"}))
    client._resolve_ack = Mock(return_value=False)
    client._dispatch_callback = AsyncMock(side_effect=RuntimeError("broken handler"))
    await client._handle_message(json.dumps({}))

    class CancelledMessages:
        def __aiter__(self):
            return self

        async def __anext__(self):
            raise asyncio.CancelledError()

    client._ws = CancelledMessages()
    with pytest.raises(asyncio.CancelledError):
        await client._receive_loop()


@pytest.mark.asyncio
async def test_reconnect_success_and_exhaustion_paths(client, monkeypatch):
    monkeypatch.setattr("pykiwoom_rest.websocket_client.asyncio.sleep", AsyncMock())
    client._close_connection = AsyncMock()
    client._restore_subscriptions = AsyncMock(return_value=True)
    ws = Mock(closed=False, close_code=None)
    with patch("pykiwoom_rest.websocket_client.websockets.connect", AsyncMock(return_value=ws)):
        assert await client._attempt_reconnect()
    client._reconnect_count = 0
    client.max_reconnect_attempts = 1
    client._restore_subscriptions = AsyncMock(return_value=False)
    with patch("pykiwoom_rest.websocket_client.websockets.connect", AsyncMock(return_value=ws)):
        assert not await client._attempt_reconnect()
    assert client._reconnect_attempts_exhausted
