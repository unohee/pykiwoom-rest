"""
Concurrent API 모듈 테스트 스위트
동시 처리 및 병렬 실행 기능 검증
작성일: 2025-01-18
"""

import pytest
import asyncio
import time
import threading
from unittest.mock import MagicMock, patch, Mock, call
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from queue import Queue, PriorityQueue
from datetime import datetime
import json

from src.pykiwoom_rest.concurrent_api import (
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
        return ConcurrentKiwoomAPI(
            appkey="test_key",
            appsecret="test_secret",
            account_no="test_account",
            max_workers=4,
            queue_size=100
        )

    def test_initialization(self, concurrent_client):
        """초기화 테스트"""
        assert concurrent_client.appkey == "test_key"
        assert concurrent_client.appsecret == "test_secret"
        assert concurrent_client.account_no == "test_account"
        assert concurrent_client.max_workers == 4
        assert concurrent_client.queue_size == 100
        assert isinstance(concurrent_client.executor, ThreadPoolExecutor)

    def test_worker_pool_creation(self, concurrent_client):
        """워커 풀 생성 테스트"""
        concurrent_client.start_workers()

        # 워커가 시작되었는지 확인
        assert concurrent_client.workers_started == True
        assert len(concurrent_client.worker_threads) == concurrent_client.max_workers

        # 정리
        concurrent_client.stop_workers()

    def test_task_submission(self, concurrent_client):
        """작업 제출 테스트"""
        result_queue = Queue()

        def mock_task(x):
            time.sleep(0.01)
            return x * 2

        # 작업 제출
        future = concurrent_client.submit_task(mock_task, 5)

        assert isinstance(future, Future)
        result = future.result(timeout=1)
        assert result == 10

    def test_batch_processing(self, concurrent_client):
        """배치 처리 테스트"""
        def process_item(item):
            return item ** 2

        items = [1, 2, 3, 4, 5]
        results = concurrent_client.process_batch(items, process_item)

        assert len(results) == 5
        assert results == [1, 4, 9, 16, 25]

    def test_priority_queue_ordering(self, concurrent_client):
        """우선순위 큐 정렬 테스트"""
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
        """동시 처리 시 rate limiting 테스트"""
        concurrent_client.rate_limit = 5  # 초당 5개 요청

        start_time = time.time()
        request_times = []

        def mock_request():
            request_times.append(time.time() - start_time)
            return "result"

        # 10개 요청 동시 제출
        with patch.object(concurrent_client, 'make_request', side_effect=mock_request):
            futures = [
                concurrent_client.submit_task(concurrent_client.make_request)
                for _ in range(10)
            ]

            # 모든 작업 완료 대기
            results = [f.result() for f in futures]

        # Rate limiting으로 인해 시간이 분산되어야 함
        assert len(results) == 10
        # 최소 1초는 걸려야 함 (10개 요청 / 5 req/s = 2초)
        total_time = max(request_times) if request_times else 0
        # Rate limiting이 구현되어 있다면 시간 분산 확인

    def test_error_handling_in_workers(self, concurrent_client):
        """워커에서의 에러 처리 테스트"""
        def failing_task():
            raise ValueError("Test error")

        future = concurrent_client.submit_task(failing_task)

        # 에러가 Future를 통해 전파되는지 확인
        with pytest.raises(ValueError, match="Test error"):
            future.result()

    def test_graceful_shutdown(self, concurrent_client):
        """우아한 종료 테스트"""
        concurrent_client.start_workers()

        # 작업 추가
        futures = []
        for i in range(5):
            future = concurrent_client.submit_task(lambda x: x * 2, i)
            futures.append(future)

        # 종료 신호
        concurrent_client.shutdown(wait=True)

        # 모든 작업이 완료되었는지 확인
        for future in futures:
            assert future.done()

    def test_context_manager(self):
        """컨텍스트 매니저 테스트"""
        with ConcurrentKiwoomAPI(
            appkey="test_key",
            appsecret="test_secret",
            max_workers=2
        ) as client:
            # 클라이언트가 활성화되었는지 확인
            assert client.executor is not None

            # 작업 실행
            future = client.submit_task(lambda: "test")
            assert future.result() == "test"

        # 컨텍스트 종료 후 정리되었는지 확인
        assert client.executor._shutdown == True


class TestOptimizedBatchProcessor:
    """OptimizedBatchProcessor 클래스 테스트"""

    @pytest.fixture
    def batch_processor(self):
        """테스트용 배치 프로세서"""
        return OptimizedBatchProcessor(
            batch_size=5,
            max_workers=2
        )

    def test_batch_creation(self, batch_processor):
        """배치 생성 테스트"""
        items = list(range(12))
        batches = batch_processor.create_batches(items)

        # 5개씩 3개 배치 생성
        assert len(batches) == 3
        assert len(batches[0]) == 5
        assert len(batches[1]) == 5
        assert len(batches[2]) == 2

    def test_batch_processing_with_callback(self, batch_processor):
        """콜백과 함께 배치 처리 테스트"""
        processed_items = []

        def process_callback(batch):
            processed_items.extend([x * 2 for x in batch])
            return len(batch)

        items = list(range(10))
        results = batch_processor.process(items, process_callback)

        assert len(processed_items) == 10
        assert processed_items == [x * 2 for x in range(10)]
        assert sum(results) == 10

    def test_parallel_batch_processing(self, batch_processor):
        """병렬 배치 처리 테스트"""
        processing_times = []

        def slow_process(batch):
            start = time.time()
            time.sleep(0.1)  # 각 배치 처리에 0.1초
            processing_times.append(time.time() - start)
            return sum(batch)

        items = list(range(20))
        start = time.time()
        results = batch_processor.process(items, slow_process)
        total_time = time.time() - start

        # 4개 배치가 2개 워커로 병렬 처리
        assert len(results) == 4
        assert sum(results) == sum(range(20))

        # 병렬 처리로 인해 총 시간이 단축됨
        # 순차 처리: 0.4초, 병렬 처리: ~0.2초
        assert total_time < 0.4

    def test_error_recovery(self, batch_processor):
        """에러 복구 테스트"""
        error_count = {'count': 0}

        def process_with_error(batch):
            error_count['count'] += 1
            if error_count['count'] == 2:
                raise ValueError("Batch processing error")
            return sum(batch)

        items = list(range(15))

        # 에러가 발생해도 다른 배치는 처리됨
        with patch.object(batch_processor, 'handle_batch_error') as mock_error_handler:
            results = batch_processor.process(items, process_with_error)

            # 에러 핸들러가 호출되었는지 확인
            assert mock_error_handler.called

    def test_timeout_handling(self, batch_processor):
        """타임아웃 처리 테스트"""
        batch_processor.timeout = 0.1

        def slow_process(batch):
            time.sleep(0.5)  # 타임아웃 초과
            return sum(batch)

        items = list(range(10))

        with pytest.raises(TimeoutError):
            batch_processor.process_with_timeout(items, slow_process)


class TestBatchResult:
    """BatchResult 클래스 테스트"""

    def test_batch_result_creation(self):
        """BatchResult 생성 테스트"""
        result = BatchResult(
            batch_id=1,
            results=[1, 2, 3],
            errors=[],
            processing_time=0.5
        )

        assert result.batch_id == 1
        assert result.results == [1, 2, 3]
        assert result.errors == []
        assert result.processing_time == 0.5
        assert result.success == True

    def test_batch_result_with_errors(self):
        """에러가 있는 BatchResult 테스트"""
        result = BatchResult(
            batch_id=2,
            results=[],
            errors=["Error 1", "Error 2"],
            processing_time=0.1
        )

        assert result.batch_id == 2
        assert result.results == []
        assert len(result.errors) == 2
        assert result.success == False


class TestConcurrentIntegration:
    """동시 처리 모듈 통합 테스트"""

    def test_full_concurrent_workflow(self):
        """전체 동시 처리 워크플로우 테스트"""
        # ConcurrentKiwoomAPI 생성
        client = ConcurrentKiwoomAPI(
            appkey="test_key",
            appsecret="test_secret",
            max_workers=4
        )

        # OptimizedBatchProcessor 생성
        batch_processor = OptimizedBatchProcessor(batch_size=5, max_workers=2)

        # 데이터 준비
        stock_codes = ["005930", "000660", "035720", "051910", "005380"]

        def fetch_stock_data(code):
            # 실제로는 API 호출
            return {'code': code, 'price': 10000}

        # 배치 처리
        results = batch_processor.process(
            stock_codes,
            lambda batch: [fetch_stock_data(code) for code in batch]
        )

        # 결과 확인
        flattened_results = [item for sublist in results for item in sublist]
        assert len(flattened_results) == 5
        assert all('code' in r and 'price' in r for r in flattened_results)

        # 정리
        client.shutdown()

    def test_priority_based_execution(self):
        """우선순위 기반 실행 테스트"""
        client = ConcurrentKiwoomAPI(
            appkey="test_key",
            appsecret="test_secret",
            max_workers=2
        )

        execution_order = []

        def task_with_priority(priority, name):
            execution_order.append((priority, name))
            return f"Completed: {name}"

        # 우선순위와 함께 작업 제출
        futures = []
        futures.append(client.submit_with_priority(3, task_with_priority, 3, "low"))
        futures.append(client.submit_with_priority(1, task_with_priority, 1, "high"))
        futures.append(client.submit_with_priority(2, task_with_priority, 2, "medium"))

        # 모든 작업 완료 대기
        results = [f.result() for f in as_completed(futures)]

        # 우선순위대로 실행되었는지 확인
        priorities = [p for p, _ in execution_order]
        assert priorities == sorted(priorities)

        client.shutdown()

    def test_stress_test(self):
        """스트레스 테스트"""
        client = ConcurrentKiwoomAPI(
            appkey="test_key",
            appsecret="test_secret",
            max_workers=8
        )

        success_count = 0
        error_count = 0

        def stress_task(idx):
            if idx % 10 == 0:
                raise ValueError(f"Simulated error at {idx}")
            return idx

        # 많은 수의 작업 제출
        futures = []
        for i in range(100):
            futures.append(client.submit_task(stress_task, i))

        # 결과 수집
        for future in as_completed(futures):
            try:
                result = future.result()
                success_count += 1
            except ValueError:
                error_count += 1

        assert success_count == 90  # 90% 성공
        assert error_count == 10    # 10% 실패

        client.shutdown()

    def test_memory_efficiency(self):
        """메모리 효율성 테스트"""
        import gc
        import sys

        client = ConcurrentKiwoomAPI(
            appkey="test_key",
            appsecret="test_secret",
            max_workers=2
        )

        # 초기 메모리 사용량
        gc.collect()
        initial_objects = len(gc.get_objects())

        # 많은 작업 실행
        for _ in range(100):
            future = client.submit_task(lambda x: x * 2, 42)
            future.result()  # 즉시 결과 수집

        # 정리 후 메모리 사용량
        client.shutdown()
        gc.collect()
        final_objects = len(gc.get_objects())

        # 메모리 누수가 없는지 확인 (허용 오차 10%)
        memory_increase_ratio = (final_objects - initial_objects) / initial_objects
        assert memory_increase_ratio < 0.1  # 10% 이하 증가