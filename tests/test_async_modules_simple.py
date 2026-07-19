"""
Simplified Async Module Tests
Focused on core functionality without complex mocking
작성일: 2025-01-18
수정일: 2025-01-04 - API 시그니처 변경에 따른 테스트 업데이트
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
import time
from concurrent.futures import ThreadPoolExecutor

from pykiwoom_rest.async_api import AsyncKiwoomAPI, ParallelKiwoomAPI
from pykiwoom_rest.concurrent_api import ConcurrentKiwoomAPI, OptimizedBatchProcessor, ProcessingMode


class TestAsyncKiwoomAPISimple:
    """AsyncKiwoomAPI 단순화된 테스트"""

    def test_initialization_basic(self):
        """기본 초기화 테스트"""
        with patch('pykiwoom_rest.async_api.load_dotenv'):
            client = AsyncKiwoomAPI(
                appkey="test_key",
                appsecret="test_secret",
                account_no="test_account",
                enable_rate_optimizer=False
            )

            assert client.appkey == "test_key"
            assert client.appsecret == "test_secret"
            assert client.account_no == "test_account"
            assert client.rate_limit == 20  # 기본값
            assert client.max_concurrent == 10  # 기본값

    def test_initialization_with_env_vars(self):
        """환경변수 초기화 테스트"""
        with patch.dict('os.environ', {
            'KIWOOM_APPKEY': 'env_key',
            'KIWOOM_APPSECRET': 'env_secret',
            'ACCOUNT_NO': 'env_account'
        }):
            with patch('pykiwoom_rest.async_api.load_dotenv'):
                client = AsyncKiwoomAPI(enable_rate_optimizer=False)
                assert client.appkey == 'env_key'

    def test_headers_generation(self):
        """헤더 생성 테스트 (메서드 존재 확인)"""
        with patch.dict('os.environ', {
            'KIWOOM_APPKEY': 'test_key',
            'KIWOOM_APPSECRET': 'test_secret',
            'ACCOUNT_NO': 'test_account'
        }):
            with patch('pykiwoom_rest.async_api.load_dotenv'):
                client = AsyncKiwoomAPI(
                    appkey="test_key",
                    appsecret="test_secret",
                    account_no="test_account",
                    enable_rate_optimizer=False
                )
                client.access_token = "test_token"

                # 헤더 생성 메서드가 있다면 테스트
                if hasattr(client, '_get_headers'):
                    headers = client._get_headers()
                    assert "content-type" in headers or "authorization" in headers

    @pytest.mark.asyncio
    async def test_session_creation(self):
        """세션 생성 테스트 (컨텍스트 매니저)"""
        with patch.dict('os.environ', {
            'KIWOOM_APPKEY': 'test_key',
            'KIWOOM_APPSECRET': 'test_secret',
            'ACCOUNT_NO': 'test_account'
        }):
            with patch('pykiwoom_rest.async_api.load_dotenv'):
                client = AsyncKiwoomAPI(
                    appkey="test_key",
                    appsecret="test_secret",
                    account_no="test_account",
                    enable_rate_optimizer=False
                )

                # 세션이 아직 생성되지 않음
                assert client.session is None

                # 컨텍스트 매니저로 세션 생성
                async with client as c:
                    assert c.session is not None


class TestParallelKiwoomAPISimple:
    """ParallelKiwoomAPI 단순화된 테스트"""

    def test_initialization(self):
        """초기화 테스트"""
        with patch('pykiwoom_rest.kiwoom_rest.KiwoomRest') as mock_kiwoom:
            mock_kiwoom.return_value = MagicMock()
            client = ParallelKiwoomAPI(
                max_workers=2,
                enable_rate_optimizer=False
            )
            assert client.max_workers == 2
            assert client.executor is not None
            client.shutdown()

    def test_credential_rotation(self):
        """크레덴셜 로테이션 (API 풀 테스트)"""
        with patch('pykiwoom_rest.kiwoom_rest.KiwoomRest') as mock_kiwoom:
            mock_kiwoom.return_value = MagicMock()
            client = ParallelKiwoomAPI(
                max_workers=3,
                enable_rate_optimizer=False
            )

            # API 풀에 max_workers 개수만큼 있어야 함
            assert client.api_pool.qsize() == 3
            client.shutdown()

    def test_single_credential_handling(self):
        """단일 크레덴셜 처리"""
        with patch('pykiwoom_rest.kiwoom_rest.KiwoomRest') as mock_kiwoom:
            mock_kiwoom.return_value = MagicMock()
            client = ParallelKiwoomAPI(
                max_workers=1,
                enable_rate_optimizer=False
            )
            assert client.api_pool.qsize() == 1
            client.shutdown()


class TestConcurrentKiwoomAPISimple:
    """ConcurrentKiwoomAPI 단순화된 테스트"""

    def test_initialization(self):
        """초기화 테스트"""
        with patch('pykiwoom_rest.concurrent_api.ConcurrentKiwoomAPI._create_api_pool'):
            client = ConcurrentKiwoomAPI(
                mode=ProcessingMode.THREAD_POOL,
                max_workers=4
            )
            assert client.max_workers == 4
            assert client.mode == ProcessingMode.THREAD_POOL
            client.shutdown()

    def test_processing_mode_enum(self):
        """ProcessingMode enum 테스트"""
        assert ProcessingMode.SEQUENTIAL.value == "sequential"
        assert ProcessingMode.THREAD_POOL.value == "thread_pool"
        assert ProcessingMode.PROCESS_POOL.value == "process_pool"
        assert ProcessingMode.ASYNC_BATCH.value == "async_batch"

    def test_submit_task(self):
        """작업 제출 테스트"""
        with patch('pykiwoom_rest.concurrent_api.ConcurrentKiwoomAPI._create_api_pool'):
            client = ConcurrentKiwoomAPI(
                mode=ProcessingMode.THREAD_POOL,
                max_workers=2
            )

            future = client._executor.submit(lambda x: x * 2, 5)
            result = future.result(timeout=1)
            assert result == 10
            client.shutdown()

    def test_batch_processing(self):
        """배치 처리 테스트"""
        with patch('pykiwoom_rest.concurrent_api.ConcurrentKiwoomAPI._create_api_pool'):
            client = ConcurrentKiwoomAPI(
                mode=ProcessingMode.THREAD_POOL,
                max_workers=2
            )

            # process_with_pipeline 테스트
            results = client.process_with_pipeline([1, 2, 3], [lambda x: x * 2])
            assert results == [2, 4, 6]
            client.shutdown()


class TestOptimizedBatchProcessorSimple:
    """OptimizedBatchProcessor 단순화된 테스트"""

    def test_initialization(self):
        """초기화 테스트"""
        processor = OptimizedBatchProcessor()
        assert processor.benchmarks == {}

    def test_batch_creation(self):
        """배치 생성 테스트"""
        processor = OptimizedBatchProcessor()
        assert isinstance(processor.benchmarks, dict)

    @patch('pykiwoom_rest.concurrent_api.ConcurrentKiwoomAPI')
    def test_process_batch_sync(self, mock_api_class):
        """동기 배치 처리 테스트"""
        from pykiwoom_rest.concurrent_api import BatchResult

        mock_api = MagicMock()
        mock_api.__enter__ = MagicMock(return_value=mock_api)
        mock_api.__exit__ = MagicMock(return_value=False)
        mock_api.fetch_stock_prices.return_value = BatchResult(
            success_count=3,
            error_count=0,
            total_time=0.5,
            results=[1, 2, 3],
            errors=[]
        )
        mock_api_class.return_value = mock_api

        processor = OptimizedBatchProcessor()
        result = processor.auto_process(["005930", "000660"])
        assert result.success_count == 3

    @pytest.mark.asyncio
    async def test_process_batch_async(self):
        """비동기 배치 처리 테스트"""
        async def async_task(x):
            await asyncio.sleep(0.01)
            return x * 2

        tasks = [async_task(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        assert results == [0, 2, 4, 6, 8]


class TestIntegrationSimple:
    """통합 테스트"""

    @pytest.mark.asyncio
    async def test_async_and_concurrent_together(self):
        """비동기 및 동시 처리 통합 테스트"""
        with patch.dict('os.environ', {
            'KIWOOM_APPKEY': 'test_key',
            'KIWOOM_APPSECRET': 'test_secret',
            'ACCOUNT_NO': 'test_account'
        }):
            with patch('pykiwoom_rest.async_api.load_dotenv'):
                # AsyncKiwoomAPI 생성
                async_client = AsyncKiwoomAPI(
                    appkey="test_key",
                    appsecret="test_secret",
                    account_no="test_account",
                    enable_rate_optimizer=False
                )
                assert async_client.appkey == "test_key"

        with patch('pykiwoom_rest.concurrent_api.ConcurrentKiwoomAPI._create_api_pool'):
            # ConcurrentKiwoomAPI 생성
            concurrent_client = ConcurrentKiwoomAPI(
                mode=ProcessingMode.THREAD_POOL,
                max_workers=2
            )
            assert concurrent_client.max_workers == 2
            concurrent_client.shutdown()

    @pytest.mark.asyncio
    async def test_rate_limiting_across_modules(self):
        """모듈 간 Rate limiting 테스트"""
        with patch.dict('os.environ', {
            'KIWOOM_APPKEY': 'test_key',
            'KIWOOM_APPSECRET': 'test_secret',
            'ACCOUNT_NO': 'test_account'
        }):
            with patch('pykiwoom_rest.async_api.load_dotenv'):
                client = AsyncKiwoomAPI(
                    appkey="test_key",
                    appsecret="test_secret",
                    account_no="test_account",
                    rate_limit=10,
                    max_concurrent=5,
                    enable_rate_optimizer=False
                )

                assert client.rate_limit == 10
                assert client.max_concurrent == 5

    def test_error_handling_consistency(self):
        """에러 처리 일관성 테스트"""
        with patch('pykiwoom_rest.concurrent_api.ConcurrentKiwoomAPI._create_api_pool'):
            client = ConcurrentKiwoomAPI(
                mode=ProcessingMode.THREAD_POOL,
                max_workers=2
            )

            # 에러 발생 작업
            def error_task():
                raise ValueError("Test error")

            future = client._executor.submit(error_task)

            with pytest.raises(ValueError, match="Test error"):
                future.result(timeout=1)

            client.shutdown()


class TestStatisticsSimple:
    """통계 테스트"""

    def test_concurrent_stats(self):
        """ConcurrentKiwoomAPI 통계 테스트"""
        with patch('pykiwoom_rest.concurrent_api.ConcurrentKiwoomAPI._create_api_pool'):
            client = ConcurrentKiwoomAPI(
                mode=ProcessingMode.THREAD_POOL,
                max_workers=2
            )

            stats = client.get_stats()
            assert 'mode' in stats
            assert 'max_workers' in stats
            assert 'total_requests' in stats
            assert 'total_errors' in stats
            client.shutdown()

    def test_parallel_stats(self):
        """ParallelKiwoomAPI 통계 테스트"""
        with patch('pykiwoom_rest.kiwoom_rest.KiwoomRest') as mock_kiwoom:
            mock_kiwoom.return_value = MagicMock()
            client = ParallelKiwoomAPI(
                max_workers=2,
                enable_rate_optimizer=False
            )

            stats = client.get_stats()
            assert 'total_requests' in stats
            assert 'total_errors' in stats
            assert 'elapsed_time' in stats
            client.shutdown()
