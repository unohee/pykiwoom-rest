"""Async API의 실제 제어 흐름을 네트워크 없이 검증한다."""

import asyncio
import json
import runpy
import warnings
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pykiwoom_rest.async_api import (
    AsyncKiwoomAPI,
    ParallelKiwoomAPI,
    RealtimeWebSocketClient,
    create_async_client,
    create_parallel_client,
    run_async_example,
    run_parallel_example,
)


def make_async_client(**kwargs):
    return AsyncKiwoomAPI(
        appkey="key", appsecret="secret", account_no="12345678", enable_rate_optimizer=False, **kwargs
    )


def response(status=200, payload=None, content_type="application/json"):
    value = AsyncMock()
    value.status = status
    value.headers = {"Content-Type": content_type}
    value.text.return_value = json.dumps(payload if payload is not None else {})
    return value


def async_context(value):
    manager = MagicMock()
    manager.__aenter__ = AsyncMock(return_value=value)
    manager.__aexit__ = AsyncMock(return_value=False)
    return manager


class TestAsyncKiwoomAPIExecution:
    def test_validates_constructor_and_builds_optimizer_credentials(self):
        with pytest.raises(ValueError, match="rate_limit"):
            make_async_client(rate_limit=True)
        with pytest.raises(ValueError, match="max_concurrent"):
            make_async_client(max_concurrent=0)

        client = AsyncKiwoomAPI(
            appkey="key", appsecret="secret", account_no="12345678", credentials_list=[{"APPKEY": "other"}]
        )
        assert client.rate_optimizer.enable_rotation is True

    @patch("pykiwoom_rest.async_api.load_dotenv")
    def test_requires_credentials(self, _load_dotenv, monkeypatch):
        monkeypatch.delenv("KIWOOM_APPKEY", raising=False)
        monkeypatch.delenv("KIWOOM_APPSECRET", raising=False)
        monkeypatch.delenv("ACCOUNT_NO", raising=False)
        with pytest.raises(ValueError, match="인증 정보"):
            AsyncKiwoomAPI(enable_rate_optimizer=False)

    @pytest.mark.asyncio
    async def test_context_manager_closes_session(self):
        client = make_async_client()
        async with client:
            assert client.session is not None
            assert not client.session.closed
        assert client.session.closed

    @pytest.mark.asyncio
    async def test_token_reuse_and_token_error_responses(self):
        client = make_async_client()
        client.access_token = "cached"
        client.token_expires = 10**12
        assert await client._get_access_token() == "cached"

        client.access_token = None
        session = MagicMock()
        token_response = response(payload={"access_token": "fresh", "expires_in": 3600})
        session.closed = False
        session.post.return_value = async_context(token_response)
        client.session = session
        assert await client._get_access_token() == "fresh"
        assert await client._get_access_token() == "fresh"
        assert session.post.call_count == 1

        client.access_token = None
        for token_response, message in [
            (response(503, {"error": "down"}), "HTTP 503"),
            (response(200, {}, "text/html"), "non-JSON"),
            (response(200, {"no_token": True}), "missing access_token"),
        ]:
            session.post.return_value = async_context(token_response)
            with pytest.raises(RuntimeError, match=message):
                await client._get_access_token()

        invalid_json_response = response()
        invalid_json_response.text.return_value = "not-json"
        session.post.return_value = async_context(invalid_json_response)
        with pytest.raises(RuntimeError, match="invalid JSON"):
            await client._get_access_token()

        client.session = None
        with pytest.raises(RuntimeError, match="async with"):
            await client._get_access_token()

    @pytest.mark.asyncio
    async def test_parse_and_make_get_post_requests(self):
        client = make_async_client(rate_limit=1000000)
        client.access_token = "token"
        client.token_expires = 10**12
        session = MagicMock()
        session.closed = False
        session.get.return_value = async_context(response(payload={"get": True}))
        session.post.return_value = async_context(response(payload={"post": True}))
        client.session = session

        assert await client._make_request("/get", "tr", {"a": 1}, "GET") == {"get": True}
        assert await client._make_request("/post", "tr", {"a": 1}) == {"post": True}
        assert session.get.call_args.kwargs["params"] == {"a": 1}
        assert session.post.call_args.kwargs["json"] == {"a": 1}

        client.last_request_time = 100.0
        with (
            patch("pykiwoom_rest.async_api.time.monotonic", side_effect=[100.0, 100.0]),
            patch("pykiwoom_rest.async_api.asyncio.sleep", new=AsyncMock()) as sleep,
        ):
            await client._make_request("/post", "tr", {"a": 1})
        sleep.assert_awaited_once()

        for value, message in [
            (response(400, {"message": "bad"}), "HTTP 400 bad"),
            (response(200, None), "invalid JSON"),
        ]:
            if "invalid" in message:
                value.text.return_value = "not-json"
            with pytest.raises(RuntimeError, match=message):
                await client._parse_response(value)

    @pytest.mark.asyncio
    async def test_price_batch_and_stream_paths(self):
        client = make_async_client()
        client._make_request = AsyncMock(return_value={"return_code": 0, "data": {"price": 1}})
        one = await client.get_stock_price("005930")
        assert one["success"] is True

        async def lookup(code):
            if code == "bad":
                raise RuntimeError("bad")
            return {"code": code}

        client.get_stock_price = lookup
        assert await client.get_multiple_stock_prices(["good", "bad"]) == [{"code": "good"}, None]

        received = []
        client.get_multiple_stock_prices = AsyncMock(side_effect=[[{"ok": 1}], RuntimeError("stop")])

        async def callback(code, result):
            received.append((code, result))
            raise asyncio.CancelledError()

        with pytest.raises(asyncio.CancelledError):
            await client.stream_stock_prices(["005930"], 0, callback)
        assert received == [("005930", {"ok": 1})]

        client.get_multiple_stock_prices = AsyncMock(side_effect=RuntimeError("retry"))
        with patch("pykiwoom_rest.async_api.asyncio.sleep", new=AsyncMock(side_effect=asyncio.CancelledError)):
            with pytest.raises(asyncio.CancelledError):
                await client.stream_stock_prices(["005930"], 0)

        client.get_multiple_stock_prices = AsyncMock(return_value=[None])
        with patch("pykiwoom_rest.async_api.asyncio.sleep", new=AsyncMock(side_effect=asyncio.CancelledError)):
            with pytest.raises(asyncio.CancelledError):
                await client.stream_stock_prices(["005930"], 0)


class TestParallelKiwoomAPIExecution:
    @pytest.fixture
    def client(self):
        with patch("pykiwoom_rest.kiwoom_rest.KiwoomRest") as api_class:
            api = MagicMock()
            api.get_stock_price.side_effect = lambda code: {"code": code}
            api.echo.side_effect = lambda value: value
            api.fail.side_effect = RuntimeError("failed")
            api_class.return_value = api
            value = ParallelKiwoomAPI(max_workers=2, enable_rate_optimizer=False)
            yield value
            value.shutdown()

    def test_worker_parallel_batch_map_reduce_and_stats(self, client):
        assert client._worker_task(lambda api, value: value * 2, 3) == 6
        with pytest.raises(RuntimeError, match="boom"):
            client._worker_task(lambda api: (_ for _ in ()).throw(RuntimeError("boom")))

        assert client.get_stock_prices_parallel(["005930", "000660"]) == {
            "005930": {"code": "005930"}, "000660": {"code": "000660"}
        }
        callbacks = []
        results = client.batch_process(
            [{"method": "echo", "args": [1]}, {"method": "fail"}], callbacks.append
        )
        assert sorted(results, key=lambda value: value is None) == [1, None]
        assert callbacks == [1]
        assert client.map_reduce(lambda value: value * 2, sum, [1, 2, 3]) == 12
        stats = client.get_stats()
        assert stats["total_requests"] >= 4
        assert stats["total_errors"] >= 2

    def test_parallel_failure_and_helpers(self, client):
        client.executor.submit = MagicMock(return_value=MagicMock(result=MagicMock(side_effect=RuntimeError("nope"))))
        assert client.get_stock_prices_parallel(["bad"]) == {"bad": None}
        assert create_async_client(appkey="key", appsecret="secret", account_no="12345678").appkey == "key"
        with patch("pykiwoom_rest.async_api.ParallelKiwoomAPI") as parallel_class:
            assert create_parallel_client(3, marker=True) is parallel_class.return_value
            parallel_class.assert_called_once_with(max_workers=3, marker=True)


class TestRealtimeWebSocketClientExecution:
    @pytest.mark.asyncio
    async def test_connect_subscribe_message_and_disconnect(self):
        ws = AsyncMock()
        ws.closed = False
        callback = AsyncMock()
        completed_task = asyncio.get_running_loop().create_future()
        completed_task.set_result(None)
        with (
            patch("websockets.connect", new=AsyncMock(return_value=ws)),
            patch(
                "pykiwoom_rest.async_api.asyncio.create_task",
                side_effect=lambda coroutine: (coroutine.close(), completed_task)[1],
            ),
        ):
            client = RealtimeWebSocketClient("key", "secret")
            await client.connect()
            await client.subscribe_stock("005930", callback)
            await client.unsubscribe_stock("005930")
            await client.disconnect()

        assert ws.close.await_count == 1
        assert client.callbacks == {}

    @pytest.mark.asyncio
    async def test_connection_guards_and_receive_str_path(self):
        client = RealtimeWebSocketClient("key", "secret")
        with pytest.raises(ConnectionError):
            await client.subscribe_stock("005930", lambda data: None)
        client.ws = AsyncMock()
        client.ws.closed = True
        client.running = True
        with pytest.raises(ConnectionError):
            await client.unsubscribe_stock("005930")

        client.ws.closed = False
        callback = AsyncMock()
        client.callbacks["stock_005930"] = callback

        async def stop_after_unknown_message():
            client.running = False
            return json.dumps({"type": "stock_005930"})

        client.ws.receive_str.side_effect = stop_after_unknown_message
        client.running = True
        await client._message_handler()
        callback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_recv_and_error_message_paths(self):
        client = RealtimeWebSocketClient("key", "secret")
        ws = MagicMock(spec=["recv"])

        async def stop_after_recv():
            client.running = False
            return json.dumps({"type": "unknown"})

        ws.recv = AsyncMock(side_effect=stop_after_recv)
        client.ws = ws
        client.running = True
        await client._message_handler()

        client.ws = MagicMock()

        async def fail_and_stop():
            client.running = False
            raise RuntimeError("closed")

        client.ws.receive_str = AsyncMock(side_effect=fail_and_stop)
        client.running = True
        await client._message_handler()


class TestAsyncExamples:
    @pytest.mark.asyncio
    async def test_async_example(self):
        api = MagicMock()
        api.__aenter__ = AsyncMock(return_value=api)
        api.__aexit__ = AsyncMock(return_value=False)
        api.get_stock_price = AsyncMock(return_value={"price": 1})
        api.get_multiple_stock_prices = AsyncMock(return_value=[MagicMock(data={"stk_nm": "name"})] * 5)
        with patch("pykiwoom_rest.async_api.AsyncKiwoomAPI", return_value=api):
            await run_async_example()

    def test_parallel_example(self):
        client = MagicMock()
        client.get_stock_prices_parallel.return_value = {"005930": {"ok": True}, "000660": None}
        client.get_stats.return_value = {"requests_per_second": 1.5}
        with patch("pykiwoom_rest.async_api.ParallelKiwoomAPI", return_value=client):
            run_parallel_example()
        client.shutdown.assert_called_once()

    def test_module_entrypoint(self):
        def close_example(coroutine):
            coroutine.close()

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=RuntimeWarning, module="runpy")
            with (
                patch("asyncio.run", side_effect=close_example),
                patch("pykiwoom_rest.kiwoom_rest.KiwoomRest", return_value=MagicMock()),
            ):
                runpy.run_module("pykiwoom_rest.async_api", run_name="__main__")
