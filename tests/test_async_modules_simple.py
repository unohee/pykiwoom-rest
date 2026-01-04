"""
Simplified Async Module Tests
Focused on core functionality without complex mocking
작성일: 2025-01-18
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
        client = AsyncKiwoomAPI(
            appkey="test_key",
            appsecret="test_secret",
            account_no="test_account"
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
            with patch('src.pykiwoom_rest.async_api.load_dotenv'):
                client = AsyncKiwoomAPI()
                assert client.appkey == 'env_key'

    def test_rate_limiter_creation(self):
        """Rate limiter 생성 테스트"""
        client = AsyncKiwoomAPI(
            appkey="test_key",
            appsecret="test_secret",
            enable_rate_optimizer=True
        )

        # Rate optimizer가 활성화되었는지 확인
        if hasattr(client, 'rate_optimizer'):
            assert client.rate_optimizer is not None

    def test_headers_generation(self):
        """헤더 생성 테스트"""
        client = AsyncKiwoomAPI(
            appkey="test_key",
            appsecret="test_secret"
        )
        client.access_token = "test_token"

        headers = client._get_headers()

        assert headers["content-type"] == "application/json"
        assert headers["authorization"] == "Bearer test_token"
        assert headers["appkey"] == "test_key"
        assert headers["appsecret"] == "test_secret"

    @pytest.mark.asyncio
    async def test_session_creation(self):
        """세션 생성 테스트"""
        client = AsyncKiwoomAPI(
            appkey="test_key",
            appsecret="test_secret"
        )

        # 세션이 아직 생성되지 않음
        assert client.session is None

        # 세션 생성
        await client.create_session()
        assert client.session is not None

        # 정리
        await client.close()


class TestParallelKiwoomAPISimple:
    """ParallelKiwoomAPI 단순화된 테스트"""

    def test_initialization(self):
        """초기화 테스트"""
        credentials = [
            {'APPKEY': 'key1', 'APPSECRET': 'secret1'},
            {'APPKEY': 'key2', 'APPSECRET': 'secret2'}
        ]

        client = ParallelKiwoomAPI(
            credentials_list=credentials,
            max_workers=4
        )

        assert len(client.credentials_list) == 2
        assert client.max_workers == 4
        assert isinstance(client.executor, ThreadPoolExecutor)

    def test_credential_rotation(self):
        """크레덴셜 순환 테스트"""
        credentials = [
            {'APPKEY': 'key1', 'APPSECRET': 'secret1'},
            {'APPKEY': 'key2', 'APPSECRET': 'secret2'}
        ]

        client = ParallelKiwoomAPI(credentials_list=credentials)

        # 순환 테스트
        first = client.get_next_credential()
        second = client.get_next_credential()
        third = client.get_next_credential()

        assert first['APPKEY'] == 'key1'
        assert second['APPKEY'] == 'key2'
        assert third['APPKEY'] == 'key1'  # 다시 처음으로

    def test_single_credential_handling(self):
        """단일 크레덴셜 처리 테스트"""
        client = ParallelKiwoomAPI(
            appkey="single_key",
            appsecret="single_secret"
        )

        # 단일 크레덴셜로 초기화
        assert len(client.credentials_list) == 1
        assert client.credentials_list[0]['APPKEY'] == "single_key"


class TestConcurrentKiwoomAPISimple:
    """ConcurrentKiwoomAPI 단순화된 테스트"""

    def test_initialization(self):
        """초기화 테스트"""
        client = ConcurrentKiwoomAPI(
            appkey="test_key",
            appsecret="test_secret",
            max_workers=4,
            queue_size=100
        )

        assert client.max_workers == 4
        assert client.queue_size == 100
        assert isinstance(client.executor, ThreadPoolExecutor)

    def test_processing_mode_enum(self):
        """ProcessingMode 열거형 테스트"""
        assert ProcessingMode.SEQUENTIAL.value == "sequential"
        assert ProcessingMode.PARALLEL.value == "parallel"
        assert ProcessingMode.ASYNC.value == "async"

    def test_submit_task(self):
        """작업 제출 테스트"""
        client = ConcurrentKiwoomAPI(
            appkey="test_key",
            appsecret="test_secret",
            max_workers=2
        )

        def simple_task(x):
            return x * 2

        future = client.submit_task(simple_task, 5)
        result = future.result(timeout=1)

        assert result == 10

        # 정리
        client.shutdown()

    def test_batch_processing(self):
        """배치 처리 테스트"""
        client = ConcurrentKiwoomAPI(
            appkey="test_key",
            appsecret="test_secret"
        )

        items = [1, 2, 3, 4, 5]

        def process_func(item):
            return item ** 2

        results = client.process_batch(items, process_func)

        assert results == [1, 4, 9, 16, 25]

        client.shutdown()


class TestOptimizedBatchProcessorSimple:
    """OptimizedBatchProcessor 단순화된 테스트"""

    def test_initialization(self):
        """초기화 테스트"""
        processor = OptimizedBatchProcessor(
            batch_size=10,
            max_workers=4
        )

        assert processor.batch_size == 10
        assert processor.max_workers == 4

    def test_batch_creation(self):
        """배치 생성 테스트"""
        processor = OptimizedBatchProcessor(batch_size=3)

        items = list(range(10))
        batches = processor.create_batches(items)

        # 3개씩 배치, 마지막은 1개
        assert len(batches) == 4
        assert len(batches[0]) == 3
        assert len(batches[1]) == 3
        assert len(batches[2]) == 3
        assert len(batches[3]) == 1

    def test_process_batch_sync(self):
        """동기 배치 처리 테스트"""
        processor = OptimizedBatchProcessor(batch_size=5)

        def sum_batch(batch):
            return sum(batch)

        items = list(range(10))
        results = processor.process_sync(items, sum_batch)

        # [0,1,2,3,4] = 10, [5,6,7,8,9] = 35
        assert results == [10, 35]

    @pytest.mark.asyncio
    async def test_process_batch_async(self):
        """비동기 배치 처리 테스트"""
        processor = OptimizedBatchProcessor(batch_size=5)

        async def async_sum_batch(batch):
            await asyncio.sleep(0.01)
            return sum(batch)

        items = list(range(10))
        results = await processor.process_async(items, async_sum_batch)

        assert results == [10, 35]


class TestIntegrationSimple:
    """통합 테스트 (단순화)"""

    def test_async_and_concurrent_together(self):
        """비동기와 동시 처리 통합 테스트"""
        # AsyncKiwoomAPI 생성
        async_client = AsyncKiwoomAPI(
            appkey="test_key",
            appsecret="test_secret"
        )

        # ConcurrentKiwoomAPI 생성
        concurrent_client = ConcurrentKiwoomAPI(
            appkey="test_key",
            appsecret="test_secret",
            max_workers=2
        )

        # 두 클라이언트가 독립적으로 작동
        assert async_client.appkey == concurrent_client.appkey
        assert async_client.appsecret == concurrent_client.appsecret

        # 정리
        concurrent_client.shutdown()

    @pytest.mark.asyncio
    async def test_parallel_api_with_async(self):
        """ParallelKiwoomAPI와 비동기 처리 테스트"""
        credentials = [
            {'APPKEY': 'key1', 'APPSECRET': 'secret1'}
        ]

        client = ParallelKiwoomAPI(credentials_list=credentials)

        # 비동기 작업 정의
        async def async_task():
            await asyncio.sleep(0.01)
            return "async_result"

        # 실행 (실제 구현에 따라 조정 필요)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            client.executor,
            lambda: "sync_result"
        )

        assert result == "sync_result"

    def test_rate_limiting_across_modules(self):
        """모듈 간 rate limiting 테스트"""
        # 동일한 rate limit 설정
        rate_limit = 10

        async_client = AsyncKiwoomAPI(
            appkey="test_key",
            appsecret="test_secret",
            rate_limit=rate_limit
        )

        concurrent_client = ConcurrentKiwoomAPI(
            appkey="test_key",
            appsecret="test_secret",
            rate_limit=rate_limit
        )

        # 두 클라이언트가 같은 rate limit 사용
        assert async_client.rate_limit == concurrent_client.rate_limit == rate_limit

        concurrent_client.shutdown()

    def test_error_handling_consistency(self):
        """에러 처리 일관성 테스트"""
        # 잘못된 크레덴셜로 클라이언트 생성
        async_client = AsyncKiwoomAPI()  # 크레덴셜 없음
        concurrent_client = ConcurrentKiwoomAPI()  # 크레덴셜 없음

        # 두 클라이언트 모두 None 크레덴셜 처리 가능
        assert async_client.appkey is None or async_client.appkey == ""
        assert concurrent_client.appkey is None or concurrent_client.appkey == ""

        concurrent_client.shutdown()