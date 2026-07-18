"""Concurrent API의 mode별 실행과 자원 회수를 검증한다."""

from queue import Queue
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pykiwoom_rest.concurrent_api import (
    BatchResult,
    ConcurrentKiwoomAPI,
    OptimizedBatchProcessor,
    ProcessingMode,
    _process_chunk,
    benchmark_all_modes,
    fetch_stocks_parallel,
)


def api_pool(*clients):
    pool = Queue()
    for client in clients:
        pool.put(client)
    return pool


class TestConcurrentExecution:
    def test_pool_creation_fallback_and_context_managers(self):
        created = MagicMock()
        with patch("pykiwoom_rest.kiwoom_rest.KiwoomRest", return_value=created):
            api = ConcurrentKiwoomAPI(ProcessingMode.THREAD_POOL, max_workers=2)
            assert api._api_pool.qsize() == 2
            api.close()

            fallback = ConcurrentKiwoomAPI(ProcessingMode.SEQUENTIAL)
            assert fallback._get_api_client() is created
            created.get_stock_price.return_value = {"code": "one"}
            assert fallback.fetch_stock_prices(["one"]).success_count == 1
            assert fallback.process_with_pipeline([1, 2], [lambda value: value + 1]) == [2, 3]
            assert fallback.map_reduce([1, 2], lambda value: value * 2, sum) == 6
            with fallback as entered:
                assert entered is fallback
            fallback.close()

        exhausted = ConcurrentKiwoomAPI(ProcessingMode.SEQUENTIAL)
        exhausted._api_pool = MagicMock()
        exhausted._api_pool.get.side_effect = __import__("queue").Empty
        with pytest.raises(RuntimeError, match="Timed out"):
            exhausted._get_api_client()

    def test_batch_result_edge_properties_and_worker_defaults(self):
        assert BatchResult(0, 0, 0, [], []).throughput == 0
        assert BatchResult(0, 0, 1, [], []).success_rate == 0
        assert ConcurrentKiwoomAPI(ProcessingMode.SEQUENTIAL).max_workers == 10
        sequential = ConcurrentKiwoomAPI(ProcessingMode.SEQUENTIAL)
        sequential.close()
        with patch("pykiwoom_rest.concurrent_api.mp.cpu_count", return_value=2), patch.object(
            ConcurrentKiwoomAPI, "_create_api_pool", return_value=api_pool(MagicMock())
        ):
            threaded = ConcurrentKiwoomAPI(ProcessingMode.THREAD_POOL)
            process = ConcurrentKiwoomAPI(ProcessingMode.PROCESS_POOL)
            assert threaded.max_workers == 10
            assert process.max_workers == 2
            threaded.close()
            process.close()

    def test_pool_lifecycle_sequential_dispatch_and_close(self):
        client = MagicMock()
        client.get_stock_price.side_effect = [{"code": "ok"}, RuntimeError("bad")]
        pool = api_pool(client)
        with patch.object(ConcurrentKiwoomAPI, "_create_api_pool", return_value=pool):
            api = ConcurrentKiwoomAPI(ProcessingMode.THREAD_POOL, max_workers=1)
            assert api._get_api_client() is client
            api._return_api_client(client)
            result = api._fetch_sequential(["ok", "bad"])
            assert result.success_count == result.error_count == 1
            assert result.results == [{"code": "ok"}]
            api.close()
            assert client.close.called
            with pytest.raises(RuntimeError, match="closed"):
                api._get_api_client()
            api.close()

    def test_threaded_fetch_pipeline_map_reduce_and_stats(self):
        client = MagicMock()
        client.get_stock_price.side_effect = lambda code: (
            (_ for _ in ()).throw(RuntimeError("bad")) if code == "bad" else {"code": code}
        )
        with patch.object(ConcurrentKiwoomAPI, "_create_api_pool", return_value=api_pool(client, client)):
            api = ConcurrentKiwoomAPI(ProcessingMode.THREAD_POOL, max_workers=2)
            result = api.fetch_stock_prices(["one", "bad"])
            assert result.success_count == result.error_count == 1
            assert api.process_with_pipeline([1, 2], [lambda x: x + 1, lambda x: x * 2]) == [4, 6]
            assert api.map_reduce([1, 2, 3], lambda x: x * 2, sum) == 12
            assert api.get_stats()["total_errors"] == 1
            api.shutdown()

    def test_thread_future_result_exception(self):
        future = MagicMock()
        future.result.side_effect = RuntimeError("future")
        with patch.object(ConcurrentKiwoomAPI, "_create_api_pool", return_value=api_pool(MagicMock())), patch(
            "pykiwoom_rest.concurrent_api.as_completed", side_effect=lambda futures: list(futures)
        ):
            api = ConcurrentKiwoomAPI(ProcessingMode.THREAD_POOL, max_workers=1)
            api._executor.submit = MagicMock(return_value=future)
            assert api._fetch_with_threads(["one"]).error_count == 1
            api.shutdown()

    def test_process_fetch_success_missing_and_exception(self):
        executor = MagicMock()
        first, second = MagicMock(), MagicMock()
        first.result.return_value = [{"code": "one"}]
        second.result.side_effect = RuntimeError("worker")
        executor.submit.side_effect = [first, second]
        with patch("pykiwoom_rest.concurrent_api.ProcessPoolExecutor", return_value=executor), patch(
            "pykiwoom_rest.concurrent_api.as_completed", side_effect=lambda futures: list(futures)
        ):
            api = ConcurrentKiwoomAPI(ProcessingMode.PROCESS_POOL, max_workers=2)
            result = api.fetch_stock_prices(["one", "two", "three"], chunk_size=2)
            assert result.success_count == 1
            assert result.error_count == 2
            executor.submit.side_effect = lambda function, value: MagicMock(
                result=MagicMock(return_value=function(value))
            )
            assert api.map_reduce([1, 2], lambda x: x + 1, sum) == 5
            api.close()

    def test_process_default_chunk_size(self):
        executor = MagicMock()
        future = MagicMock()
        future.result.return_value = [{"code": "one"}]
        executor.submit.return_value = future
        with patch("pykiwoom_rest.concurrent_api.ProcessPoolExecutor", return_value=executor), patch(
            "pykiwoom_rest.concurrent_api.as_completed", side_effect=lambda futures: list(futures)
        ):
            api = ConcurrentKiwoomAPI(ProcessingMode.PROCESS_POOL, max_workers=2)
            assert api._fetch_with_processes(["one"]).success_count == 1
            api.shutdown()

    @pytest.mark.asyncio
    async def test_async_batch_implementation(self):
        fake_client = MagicMock()
        fake_client.__aenter__ = __import__("unittest").mock.AsyncMock(return_value=fake_client)
        fake_client.__aexit__ = __import__("unittest").mock.AsyncMock(return_value=False)
        fake_client.get_multiple_stock_prices = __import__("unittest").mock.AsyncMock(return_value=[{"ok": 1}, None])
        with patch("pykiwoom_rest.async_api.AsyncKiwoomAPI", return_value=fake_client):
            api = ConcurrentKiwoomAPI(ProcessingMode.ASYNC_BATCH, max_workers=2)
            result = await api._async_fetch_batch(["one", "two"])
        assert (result.success_count, result.error_count) == (1, 1)

    def test_async_sync_wrapper_and_non_pool_client_close(self):
        api = ConcurrentKiwoomAPI(ProcessingMode.ASYNC_BATCH)
        api._async_fetch_batch = AsyncMock(return_value=BatchResult(1, 0, 1, ["ok"], []))
        assert api.fetch_stock_prices(["one"]).results == ["ok"]
        standalone = MagicMock()
        api._return_api_client(standalone)
        standalone.close.assert_called_once()


class TestConcurrentHelpers:
    def test_process_chunk_and_fetch_helper(self):
        client = MagicMock()
        client.get_stock_price.side_effect = [{"code": "one"}, RuntimeError("bad")]
        with patch("pykiwoom_rest.kiwoom_rest.KiwoomRest", return_value=client):
            assert _process_chunk(["one", "bad"]) == [{"code": "one"}]
        assert client.close.called

        instance = MagicMock()
        instance.__enter__.return_value = instance
        instance.fetch_stock_prices.return_value = BatchResult(
            3, 0, 1, [{"stock_code": "one"}, {"stk_cd": "two"}, "ignored"], []
        )
        with patch("pykiwoom_rest.concurrent_api.ConcurrentKiwoomAPI", return_value=instance):
            assert fetch_stocks_parallel(["one", "two"]) == {
                "one": {"stock_code": "one"}, "two": {"stk_cd": "two"}
            }

    def test_optimized_benchmark_auto_and_helper(self):
        created = []

        def fake_api(mode, **kwargs):
            api = MagicMock()
            api.__enter__.return_value = api
            api.fetch_stock_prices.return_value = BatchResult(
                1, 0, 0.25 if mode is ProcessingMode.THREAD_POOL else 1, [], []
            )
            created.append(api)
            return api

        processor = OptimizedBatchProcessor()
        with patch("pykiwoom_rest.concurrent_api.ConcurrentKiwoomAPI", side_effect=fake_api):
            assert processor.benchmark_modes(list(map(str, range(8))), 3) is ProcessingMode.THREAD_POOL
            assert processor.auto_process(["one"]).success_count == 1
            processor.benchmark_modes = MagicMock(return_value=ProcessingMode.SEQUENTIAL)
            assert processor.auto_process([str(i) for i in range(21)]).success_count == 1

        with patch.object(OptimizedBatchProcessor, "benchmark_modes") as benchmark:
            benchmark.return_value = None
            assert benchmark_all_modes(["one"]) == {}
            benchmark.assert_called_once_with(["one"], sample_size=1)
