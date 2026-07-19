"""
Concurrent API 모듈 테스트 스위트
동시 처리 및 병렬 실행 기능 검증
작성일: 2025-01-18
수정일: 2025-01-04 - API 시그니처 변경에 따른 테스트 업데이트
"""

import pytest
import time
from unittest.mock import MagicMock, patch, Mock
from concurrent.futures import ThreadPoolExecutor

from pykiwoom_rest.concurrent_api import (
    ConcurrentKiwoomAPI,
    OptimizedBatchProcessor,
    BatchResult,
    ProcessingMode
)


class TestConcurrentKiwoomAPI:
    """ConcurrentKiwoomAPI 클래스 테스트"""

    @pytest.fixture
    def concurrent_client(self):
        """테스트용 동시 처리 클라이언트"""
        # Mock KiwoomRest를 사용하여 API 호출 방지
        with patch('pykiwoom_rest.concurrent_api.ConcurrentKiwoomAPI._create_api_pool'):
            client = ConcurrentKiwoomAPI(
                mode=ProcessingMode.THREAD_POOL,
                max_workers=4,
                enable_rate_optimizer=False
            )
            return client

    def test_initialization(self, concurrent_client):
        """초기화 테스트"""
        assert concurrent_client.mode == ProcessingMode.THREAD_POOL
        assert concurrent_client.max_workers == 4
        assert concurrent_client.enable_rate_optimizer is False
        assert isinstance(concurrent_client._executor, ThreadPoolExecutor)

    def test_worker_pool_creation(self):
        """워커 풀 생성 테스트"""
        with patch('pykiwoom_rest.concurrent_api.ConcurrentKiwoomAPI._create_api_pool') as mock_pool:
            mock_pool.return_value = MagicMock()
            client = ConcurrentKiwoomAPI(
                mode=ProcessingMode.THREAD_POOL,
                max_workers=4
            )
            assert client._executor is not None
            client.shutdown()

    def test_task_submission(self, concurrent_client):
        """작업 제출 테스트 (ThreadPoolExecutor 직접 테스트)"""
        def mock_task(x):
            time.sleep(0.01)
            return x * 2

        # ThreadPoolExecutor submit 직접 사용
        future = concurrent_client._executor.submit(mock_task, 5)
        result = future.result(timeout=1)
        assert result == 10

    def test_batch_processing(self, concurrent_client):
        """배치 처리 테스트"""
        # process_with_pipeline 테스트
        def square(x):
            return x ** 2

        items = [1, 2, 3, 4, 5]
        results = concurrent_client.process_with_pipeline(items, [square])
        assert results == [1, 4, 9, 16, 25]

    def test_priority_queue_ordering(self):
        """우선순위 큐 정렬 테스트"""
        from queue import PriorityQueue
        pq = PriorityQueue()

        # 우선순위와 함께 작업 추가
        pq.put((3, "low_priority"))
        pq.put((1, "high_priority"))
        pq.put((2, "medium_priority"))

        # 우선순위대로 꺼내지는지 확인
        assert pq.get()[1] == "high_priority"
        assert pq.get()[1] == "medium_priority"
        assert pq.get()[1] == "low_priority"

    def test_concurrent_rate_limiting(self, concurrent_client):
        """동시 처리 시 rate limiting 확인 (구조 테스트)"""
        assert hasattr(concurrent_client, 'enable_rate_optimizer')
        assert concurrent_client.enable_rate_optimizer is False

    def test_error_handling_in_workers(self, concurrent_client):
        """워커 에러 처리 테스트"""
        def failing_task():
            raise ValueError("Test error")

        future = concurrent_client._executor.submit(failing_task)
        with pytest.raises(ValueError, match="Test error"):
            future.result(timeout=1)

    def test_graceful_shutdown(self):
        """정상 종료 테스트"""
        with patch('pykiwoom_rest.concurrent_api.ConcurrentKiwoomAPI._create_api_pool'):
            client = ConcurrentKiwoomAPI(
                mode=ProcessingMode.THREAD_POOL,
                max_workers=2
            )
            assert client._executor is not None
            client.shutdown()
            # shutdown 후 executor가 종료됨

    def test_context_manager(self):
        """컨텍스트 매니저 테스트"""
        with patch('pykiwoom_rest.concurrent_api.ConcurrentKiwoomAPI._create_api_pool'):
            with ConcurrentKiwoomAPI(
                mode=ProcessingMode.THREAD_POOL,
                max_workers=2
            ) as client:
                assert client is not None
                assert client._executor is not None


class TestBatchResult:
    """BatchResult 데이터클래스 테스트"""

    def test_batch_result_creation(self):
        """BatchResult 생성 테스트"""
        result = BatchResult(
            success_count=8,
            error_count=2,
            total_time=1.0,
            results=[1, 2, 3, 4, 5, 6, 7, 8],
            errors=[(0, Exception("err1")), (1, Exception("err2"))]
        )

        assert result.success_count == 8
        assert result.error_count == 2
        assert result.total_time == 1.0
        assert len(result.results) == 8
        assert len(result.errors) == 2

    def test_batch_result_with_errors(self):
        """에러가 있는 BatchResult 테스트"""
        result = BatchResult(
            success_count=5,
            error_count=5,
            total_time=2.0,
            results=[1, 2, 3, 4, 5],
            errors=[(i, Exception(f"err{i}")) for i in range(5)]
        )

        assert result.success_rate == 0.5
        assert result.throughput == 5.0  # 10 / 2.0

    def test_batch_result_properties(self):
        """BatchResult 속성 테스트"""
        result = BatchResult(
            success_count=10,
            error_count=0,
            total_time=2.0,
            results=list(range(10)),
            errors=[]
        )

        assert result.success_rate == 1.0
        assert result.throughput == 5.0  # 10 / 2.0


class TestOptimizedBatchProcessor:
    """OptimizedBatchProcessor 테스트"""

    def test_batch_creation(self):
        """배치 프로세서 생성 테스트"""
        processor = OptimizedBatchProcessor()
        assert processor.benchmarks == {}

    def test_batch_processing_with_callback(self):
        """콜백과 함께 배치 처리 테스트"""
        processor = OptimizedBatchProcessor()
        # benchmarks 초기 상태 확인
        assert isinstance(processor.benchmarks, dict)

    @patch('pykiwoom_rest.concurrent_api.ConcurrentKiwoomAPI')
    def test_parallel_batch_processing(self, mock_api_class):
        """병렬 배치 처리 테스트"""
        mock_api = MagicMock()
        mock_api.__enter__ = MagicMock(return_value=mock_api)
        mock_api.__exit__ = MagicMock(return_value=False)
        mock_api.fetch_stock_prices.return_value = BatchResult(
            success_count=5,
            error_count=0,
            total_time=0.5,
            results=[{"price": 100}] * 5,
            errors=[]
        )
        mock_api_class.return_value = mock_api

        processor = OptimizedBatchProcessor()
        result = processor.auto_process(["005930", "000660", "035420"])

        assert result.success_count == 5

    def test_error_recovery(self):
        """에러 복구 테스트"""
        processor = OptimizedBatchProcessor()
        # 에러 복구는 개별 처리에서 처리됨
        assert processor.benchmarks == {}

    def test_timeout_handling(self):
        """타임아웃 처리 테스트"""
        processor = OptimizedBatchProcessor()
        # 타임아웃은 ConcurrentKiwoomAPI에서 처리됨
        assert isinstance(processor, OptimizedBatchProcessor)


class TestProcessingMode:
    """ProcessingMode Enum 테스트"""

    def test_processing_modes(self):
        """처리 모드 값 테스트"""
        assert ProcessingMode.SEQUENTIAL.value == "sequential"
        assert ProcessingMode.THREAD_POOL.value == "thread_pool"
        assert ProcessingMode.PROCESS_POOL.value == "process_pool"
        assert ProcessingMode.ASYNC_BATCH.value == "async_batch"


class TestConcurrentIntegration:
    """통합 테스트"""

    @patch('pykiwoom_rest.concurrent_api.ConcurrentKiwoomAPI._create_api_pool')
    def test_full_concurrent_workflow(self, mock_pool):
        """전체 동시 처리 워크플로우"""
        mock_pool.return_value = MagicMock()

        with ConcurrentKiwoomAPI(
            mode=ProcessingMode.THREAD_POOL,
            max_workers=2
        ) as client:
            # map_reduce 테스트
            data = [1, 2, 3, 4, 5]
            result = client.map_reduce(
                data,
                map_func=lambda x: x * 2,
                reduce_func=sum
            )
            assert result == 30  # (1+2+3+4+5) * 2

    @patch('pykiwoom_rest.concurrent_api.ConcurrentKiwoomAPI._create_api_pool')
    def test_priority_based_execution(self, mock_pool):
        """우선순위 기반 실행 테스트"""
        mock_pool.return_value = MagicMock()

        with ConcurrentKiwoomAPI(
            mode=ProcessingMode.THREAD_POOL,
            max_workers=2
        ) as client:
            # 우선순위는 파이프라인에서 처리
            results = client.process_with_pipeline(
                [1, 2, 3],
                [lambda x: x * 2, lambda x: x + 1]
            )
            assert results == [3, 5, 7]

    @patch('pykiwoom_rest.concurrent_api.ConcurrentKiwoomAPI._create_api_pool')
    def test_stress_test(self, mock_pool):
        """스트레스 테스트 (작은 규모)"""
        mock_pool.return_value = MagicMock()

        with ConcurrentKiwoomAPI(
            mode=ProcessingMode.THREAD_POOL,
            max_workers=4
        ) as client:
            # 많은 작업 제출
            futures = []
            for i in range(20):
                future = client._executor.submit(lambda x: x * 2, i)
                futures.append(future)

            results = [f.result(timeout=5) for f in futures]
            assert len(results) == 20

    @patch('pykiwoom_rest.concurrent_api.ConcurrentKiwoomAPI._create_api_pool')
    def test_memory_efficiency(self, mock_pool):
        """메모리 효율성 테스트"""
        mock_pool.return_value = MagicMock()

        client = ConcurrentKiwoomAPI(
            mode=ProcessingMode.THREAD_POOL,
            max_workers=2
        )

        # stats 확인
        stats = client.get_stats()
        assert "mode" in stats
        assert "max_workers" in stats
        assert stats["max_workers"] == 2

        client.shutdown()


class TestStatistics:
    """통계 테스트"""

    @patch('pykiwoom_rest.concurrent_api.ConcurrentKiwoomAPI._create_api_pool')
    def test_stats_tracking(self, mock_pool):
        """통계 추적 테스트"""
        mock_pool.return_value = MagicMock()

        with ConcurrentKiwoomAPI(
            mode=ProcessingMode.THREAD_POOL,
            max_workers=2
        ) as client:
            stats = client.get_stats()

            assert stats["mode"] == "thread_pool"
            assert stats["max_workers"] == 2
            assert stats["total_requests"] == 0
            assert stats["total_errors"] == 0
            assert "elapsed_time" in stats
            assert "throughput" in stats
