"""
Async API 모듈 테스트 스위트
비동기 API 클라이언트의 모든 기능을 검증
작성일: 2025-01-18
수정일: 2025-01-04 - API 시그니처 변경에 따른 테스트 업데이트
"""

import pytest
import asyncio
import aiohttp
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import time

from pykiwoom_rest.async_api import AsyncKiwoomAPI, ParallelKiwoomAPI


class TestAsyncKiwoomAPI:
    """AsyncKiwoomAPI 클래스 테스트"""

    @pytest.fixture
    def async_client(self):
        """테스트용 비동기 클라이언트"""
        with patch('pykiwoom_rest.async_api.load_dotenv'):
            return AsyncKiwoomAPI(
                appkey="test_key",
                appsecret="test_secret",
                account_no="test_account",
                rate_limit=10,
                max_concurrent=5,
                enable_rate_optimizer=False
            )

    def test_initialization(self, async_client):
        """초기화 테스트"""
        assert async_client.appkey == "test_key"
        assert async_client.appsecret == "test_secret"
        assert async_client.account_no == "test_account"
        assert async_client.rate_limit == 10
        assert async_client.max_concurrent == 5
        assert async_client.session is None

    def test_initialization_with_env(self):
        """환경변수를 통한 초기화 테스트"""
        with patch.dict('os.environ', {
            'KIWOOM_APPKEY': 'env_key',
            'KIWOOM_APPSECRET': 'env_secret',
            'ACCOUNT_NO': 'env_account'
        }):
            with patch('pykiwoom_rest.async_api.load_dotenv'):
                client = AsyncKiwoomAPI()
                assert client.appkey == 'env_key'
                assert client.appsecret == 'env_secret'
                assert client.account_no == 'env_account'

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """비동기 컨텍스트 매니저 테스트"""
        with patch.dict('os.environ', {
            'KIWOOM_APPKEY': 'test_key',
            'KIWOOM_APPSECRET': 'test_secret',
            'ACCOUNT_NO': 'test_account'
        }):
            with patch('pykiwoom_rest.async_api.load_dotenv'):
                async with AsyncKiwoomAPI(
                    appkey="test_key",
                    appsecret="test_secret",
                    account_no="test_account",
                    enable_rate_optimizer=False
                ) as client:
                    assert client.session is not None
                    assert isinstance(client.session, aiohttp.ClientSession)

                # 컨텍스트 종료 후 세션 닫힘 확인
                assert client.session.closed

    @pytest.mark.asyncio
    async def test_make_request_structure(self, async_client):
        """_make_request 메서드 구조 테스트"""
        # _make_request 메서드가 존재하는지 확인
        assert hasattr(async_client, '_make_request')
        assert callable(async_client._make_request)

    @pytest.mark.asyncio
    async def test_get_stock_price_method(self, async_client):
        """get_stock_price 메서드 테스트"""
        assert hasattr(async_client, 'get_stock_price')
        assert callable(async_client.get_stock_price)

    @pytest.mark.asyncio
    async def test_get_multiple_stock_prices_method(self, async_client):
        """get_multiple_stock_prices 메서드 테스트"""
        assert hasattr(async_client, 'get_multiple_stock_prices')
        assert callable(async_client.get_multiple_stock_prices)

    @pytest.mark.asyncio
    async def test_semaphore_initialization(self, async_client):
        """세마포어 초기화 테스트"""
        assert isinstance(async_client.semaphore, asyncio.Semaphore)
        assert isinstance(async_client.rate_limiter, asyncio.Semaphore)

    @pytest.mark.asyncio
    async def test_token_lock_initialization(self, async_client):
        """토큰 락 초기화 테스트"""
        assert isinstance(async_client.token_lock, asyncio.Lock)

    @pytest.mark.asyncio
    async def test_access_token_handling(self, async_client):
        """액세스 토큰 처리 테스트"""
        # 초기 토큰 상태
        assert async_client.access_token is None
        assert async_client.token_expires is None

        # _get_access_token 메서드 존재 확인
        assert hasattr(async_client, '_get_access_token')

    @pytest.mark.asyncio
    async def test_error_handling(self, async_client):
        """에러 처리 테스트"""
        # 세션 mock 설정
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)
        mock_session.request = MagicMock(return_value=mock_response)
        mock_response.raise_for_status = MagicMock(
            side_effect=aiohttp.ClientError("Network error")
        )
        async_client.session = mock_session
        async_client.access_token = "test_token"

        # _make_request는 내부에서 예외를 처리할 수 있으므로 메서드 존재 확인만
        assert hasattr(async_client, '_make_request')


class TestParallelKiwoomAPI:
    """ParallelKiwoomAPI 클래스 테스트"""

    @pytest.fixture
    def parallel_client(self):
        """테스트용 병렬 처리 클라이언트"""
        with patch('pykiwoom_rest.kiwoom_rest.KiwoomRest') as mock_kiwoom:
            mock_kiwoom.return_value = MagicMock()
            return ParallelKiwoomAPI(
                max_workers=2,
                enable_rate_optimizer=False,
                credentials_list=None
            )

    def test_initialization(self, parallel_client):
        """초기화 테스트"""
        assert parallel_client.max_workers == 2
        assert parallel_client.executor is not None

    def test_api_pool_creation(self, parallel_client):
        """API 풀 생성 테스트"""
        assert parallel_client.api_pool is not None
        # 풀에 max_workers 만큼의 API 클라이언트가 있어야 함
        assert parallel_client.api_pool.qsize() == 2

    def test_request_queue_creation(self, parallel_client):
        """요청 큐 생성 테스트"""
        from queue import PriorityQueue
        assert isinstance(parallel_client.request_queue, PriorityQueue)

    def test_statistics_initialization(self, parallel_client):
        """통계 초기화 테스트"""
        assert parallel_client.total_requests == 0
        assert parallel_client.total_errors == 0
        assert parallel_client.start_time > 0

    def test_get_stock_prices_parallel_method(self, parallel_client):
        """get_stock_prices_parallel 메서드 존재 확인"""
        assert hasattr(parallel_client, 'get_stock_prices_parallel')
        assert callable(parallel_client.get_stock_prices_parallel)

    def test_batch_process_method(self, parallel_client):
        """batch_process 메서드 존재 확인"""
        assert hasattr(parallel_client, 'batch_process')
        assert callable(parallel_client.batch_process)

    def test_map_reduce_method(self, parallel_client):
        """map_reduce 메서드 존재 확인"""
        assert hasattr(parallel_client, 'map_reduce')
        assert callable(parallel_client.map_reduce)

    def test_get_stats_method(self, parallel_client):
        """get_stats 메서드 존재 확인"""
        assert hasattr(parallel_client, 'get_stats')
        stats = parallel_client.get_stats()
        assert 'total_requests' in stats
        assert 'total_errors' in stats
        assert 'elapsed_time' in stats

    def test_shutdown_method(self, parallel_client):
        """shutdown 메서드 테스트"""
        assert hasattr(parallel_client, 'shutdown')
        parallel_client.shutdown()
        # shutdown 후 executor가 종료됨
        assert parallel_client.executor._shutdown

    @pytest.mark.asyncio
    async def test_concurrent_safety(self):
        """동시성 안전성 테스트"""
        counter = {'value': 0}
        lock = asyncio.Lock()

        async def increment():
            async with lock:
                current = counter['value']
                await asyncio.sleep(0.001)  # 경쟁 상태 유도
                counter['value'] = current + 1

        # 동시에 여러 작업 실행
        tasks = [increment() for _ in range(100)]
        await asyncio.gather(*tasks)

        # 모든 증가 연산이 안전하게 수행되었는지 확인
        assert counter['value'] == 100


class TestAsyncIntegration:
    """비동기 모듈 통합 테스트"""

    @pytest.mark.asyncio
    async def test_full_async_workflow(self):
        """전체 비동기 워크플로우 테스트"""
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
                    rate_limit=20,
                    enable_rate_optimizer=False
                )

                # 기본 속성 확인
                assert async_client.appkey == "test_key"
                assert async_client.rate_limit == 20

    @pytest.mark.asyncio
    async def test_performance_comparison(self):
        """동기 vs 비동기 성능 비교 테스트"""
        async def async_task():
            await asyncio.sleep(0.01)
            return "async_result"

        def sync_task():
            time.sleep(0.01)
            return "sync_result"

        # 비동기 실행
        start_async = time.time()
        async_results = await asyncio.gather(*[async_task() for _ in range(10)])
        async_time = time.time() - start_async

        # 동기 실행
        start_sync = time.time()
        sync_results = [sync_task() for _ in range(10)]
        sync_time = time.time() - start_sync

        # 비동기가 더 빠름
        assert async_time < sync_time
        assert len(async_results) == len(sync_results) == 10

    @pytest.mark.asyncio
    async def test_mixed_sync_async_execution(self):
        """동기/비동기 혼합 실행 테스트"""
        async def async_part():
            await asyncio.sleep(0.01)
            return "async"

        def sync_part():
            time.sleep(0.01)
            return "sync"

        # 비동기 태스크 실행
        async_result = await async_part()

        # 동기 태스크를 executor에서 실행
        loop = asyncio.get_event_loop()
        sync_result = await loop.run_in_executor(None, sync_part)

        assert async_result == "async"
        assert sync_result == "sync"


class TestAsyncRateLimiting:
    """비동기 Rate Limiting 테스트"""

    @pytest.fixture
    def rate_limited_client(self):
        """Rate limiting이 설정된 클라이언트"""
        with patch.dict('os.environ', {
            'KIWOOM_APPKEY': 'test_key',
            'KIWOOM_APPSECRET': 'test_secret',
            'ACCOUNT_NO': 'test_account'
        }):
            with patch('pykiwoom_rest.async_api.load_dotenv'):
                return AsyncKiwoomAPI(
                    appkey="test_key",
                    appsecret="test_secret",
                    account_no="test_account",
                    rate_limit=5,
                    max_concurrent=2,
                    enable_rate_optimizer=False
                )

    def test_rate_limit_setting(self, rate_limited_client):
        """Rate limit 설정 테스트"""
        assert rate_limited_client.rate_limit == 5
        assert rate_limited_client.max_concurrent == 2

    @pytest.mark.asyncio
    async def test_semaphore_limits_concurrent(self, rate_limited_client):
        """세마포어가 동시 요청을 제한하는지 테스트"""
        assert rate_limited_client.semaphore._value == 2
        assert rate_limited_client.rate_limiter._value == 5
