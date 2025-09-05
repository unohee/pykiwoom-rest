"""
Concurrent API Processing for Kiwoom REST API
동시 처리를 위한 실용적인 API 클라이언트
작성일: 2025-01-05
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import Dict, Any, List, Optional, Callable, Union, Tuple
import threading
from queue import Queue, Empty
import logging
from dataclasses import dataclass
from enum import Enum
import multiprocessing as mp

logger = logging.getLogger(__name__)


class ProcessingMode(Enum):
    """처리 모드"""
    SEQUENTIAL = "sequential"
    THREAD_POOL = "thread_pool"
    PROCESS_POOL = "process_pool"
    ASYNC_BATCH = "async_batch"


@dataclass
class BatchResult:
    """배치 처리 결과"""
    success_count: int
    error_count: int
    total_time: float
    results: List[Any]
    errors: List[Tuple[int, Exception]]
    
    @property
    def throughput(self) -> float:
        """처리량 (req/s)"""
        total = self.success_count + self.error_count
        return total / self.total_time if self.total_time > 0 else 0
    
    @property
    def success_rate(self) -> float:
        """성공률"""
        total = self.success_count + self.error_count
        return self.success_count / total if total > 0 else 0


class ConcurrentKiwoomAPI:
    """동시 처리 최적화 Kiwoom API"""
    
    def __init__(
        self,
        mode: ProcessingMode = ProcessingMode.THREAD_POOL,
        max_workers: int = None,
        enable_rate_optimizer: bool = True
    ):
        """
        초기화
        
        Args:
            mode: 처리 모드
            max_workers: 최대 워커 수 (None이면 자동 설정)
            enable_rate_optimizer: Rate limiting 최적화
        """
        self.mode = mode
        
        # 워커 수 자동 설정
        if max_workers is None:
            if mode == ProcessingMode.THREAD_POOL:
                max_workers = min(32, (mp.cpu_count() or 1) * 5)
            elif mode == ProcessingMode.PROCESS_POOL:
                max_workers = mp.cpu_count() or 1
            else:
                max_workers = 10
        
        self.max_workers = max_workers
        self.enable_rate_optimizer = enable_rate_optimizer
        
        # API 클라이언트 풀
        self._api_pool = None
        self._executor = None
        
        # 통계
        self.stats = {
            'total_requests': 0,
            'total_errors': 0,
            'total_time': 0,
            'start_time': time.time()
        }
        
        self._initialize()
    
    def _initialize(self):
        """초기화"""
        if self.mode == ProcessingMode.THREAD_POOL:
            self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
            self._api_pool = self._create_api_pool()
            
        elif self.mode == ProcessingMode.PROCESS_POOL:
            self._executor = ProcessPoolExecutor(max_workers=self.max_workers)
            # 프로세스는 pickle 가능한 함수만 사용
            
        elif self.mode == ProcessingMode.ASYNC_BATCH:
            # AsyncIO 기반 처리
            pass
    
    def _create_api_pool(self) -> Queue:
        """API 클라이언트 풀 생성"""
        from .kiwoom_rest import KiwoomRest
        
        pool = Queue()
        for _ in range(self.max_workers):
            api = KiwoomRest(enable_rate_optimizer=self.enable_rate_optimizer)
            pool.put(api)
        
        return pool
    
    def _get_api_client(self):
        """API 클라이언트 획득"""
        if self._api_pool:
            return self._api_pool.get()
        else:
            from .kiwoom_rest import KiwoomRest
            return KiwoomRest(enable_rate_optimizer=self.enable_rate_optimizer)
    
    def _return_api_client(self, client):
        """API 클라이언트 반환"""
        if self._api_pool:
            self._api_pool.put(client)
    
    def fetch_stock_prices(
        self,
        stock_codes: List[str],
        chunk_size: int = None
    ) -> BatchResult:
        """여러 종목 시세 동시 조회
        
        Args:
            stock_codes: 종목 코드 리스트
            chunk_size: 청크 크기 (병렬 처리 단위)
            
        Returns:
            BatchResult 객체
        """
        start_time = time.time()
        
        if self.mode == ProcessingMode.SEQUENTIAL:
            return self._fetch_sequential(stock_codes)
            
        elif self.mode == ProcessingMode.THREAD_POOL:
            return self._fetch_with_threads(stock_codes)
            
        elif self.mode == ProcessingMode.PROCESS_POOL:
            return self._fetch_with_processes(stock_codes, chunk_size)
            
        elif self.mode == ProcessingMode.ASYNC_BATCH:
            return self._fetch_async_batch(stock_codes)
    
    def _fetch_sequential(self, stock_codes: List[str]) -> BatchResult:
        """순차 처리"""
        api = self._get_api_client()
        
        results = []
        errors = []
        start_time = time.time()
        
        try:
            for i, code in enumerate(stock_codes):
                try:
                    result = api.get_stock_price(code)
                    results.append(result)
                    self.stats['total_requests'] += 1
                except Exception as e:
                    errors.append((i, e))
                    self.stats['total_errors'] += 1
        finally:
            self._return_api_client(api)
        
        elapsed = time.time() - start_time
        
        return BatchResult(
            success_count=len(results),
            error_count=len(errors),
            total_time=elapsed,
            results=results,
            errors=errors
        )
    
    def _fetch_with_threads(self, stock_codes: List[str]) -> BatchResult:
        """스레드 풀 병렬 처리"""
        def fetch_one(code: str):
            api = self._get_api_client()
            try:
                result = api.get_stock_price(code)
                return ('success', result)
            except Exception as e:
                return ('error', e)
            finally:
                self._return_api_client(api)
        
        results = []
        errors = []
        start_time = time.time()
        
        # 병렬 실행
        futures = {
            self._executor.submit(fetch_one, code): (i, code)
            for i, code in enumerate(stock_codes)
        }
        
        # 결과 수집
        for future in as_completed(futures):
            i, code = futures[future]
            try:
                status, data = future.result(timeout=10)
                if status == 'success':
                    results.append(data)
                    self.stats['total_requests'] += 1
                else:
                    errors.append((i, data))
                    self.stats['total_errors'] += 1
            except Exception as e:
                errors.append((i, e))
                self.stats['total_errors'] += 1
        
        elapsed = time.time() - start_time
        
        return BatchResult(
            success_count=len(results),
            error_count=len(errors),
            total_time=elapsed,
            results=results,
            errors=errors
        )
    
    def _fetch_with_processes(
        self,
        stock_codes: List[str],
        chunk_size: int = None
    ) -> BatchResult:
        """프로세스 풀 병렬 처리"""
        if chunk_size is None:
            chunk_size = max(1, len(stock_codes) // self.max_workers)
        
        # 청크로 분할
        chunks = [
            stock_codes[i:i+chunk_size]
            for i in range(0, len(stock_codes), chunk_size)
        ]
        
        results = []
        errors = []
        start_time = time.time()
        
        # 프로세스별 처리 함수 (pickle 가능해야 함)
        futures = {
            self._executor.submit(_process_chunk, chunk): (i, chunk)
            for i, chunk in enumerate(chunks)
        }
        
        # 결과 수집
        for future in as_completed(futures):
            i, chunk = futures[future]
            try:
                chunk_results = future.result(timeout=30)
                results.extend(chunk_results)
                self.stats['total_requests'] += len(chunk_results)
            except Exception as e:
                errors.append((i, e))
                self.stats['total_errors'] += len(chunk)
        
        elapsed = time.time() - start_time
        
        return BatchResult(
            success_count=len(results),
            error_count=len(errors),
            total_time=elapsed,
            results=results,
            errors=errors
        )
    
    def _fetch_async_batch(self, stock_codes: List[str]) -> BatchResult:
        """비동기 배치 처리"""
        # 이벤트 루프에서 실행
        import asyncio
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(
                self._async_fetch_batch(stock_codes)
            )
        finally:
            loop.close()
    
    async def _async_fetch_batch(self, stock_codes: List[str]) -> BatchResult:
        """비동기 배치 처리 구현"""
        from .async_api import AsyncKiwoomAPI
        
        results = []
        errors = []
        start_time = time.time()
        
        async with AsyncKiwoomAPI(max_concurrent=self.max_workers) as api:
            batch_results = await api.get_multiple_stock_prices(stock_codes)
            
            for i, result in enumerate(batch_results):
                if result:
                    results.append(result)
                    self.stats['total_requests'] += 1
                else:
                    errors.append((i, Exception("Failed to fetch")))
                    self.stats['total_errors'] += 1
        
        elapsed = time.time() - start_time
        
        return BatchResult(
            success_count=len(results),
            error_count=len(errors),
            total_time=elapsed,
            results=results,
            errors=errors
        )
    
    def process_with_pipeline(
        self,
        data: List[Any],
        stages: List[Callable]
    ) -> List[Any]:
        """파이프라인 처리
        
        Args:
            data: 입력 데이터
            stages: 처리 단계 함수들
            
        Returns:
            처리된 결과
        """
        result = data
        
        for stage in stages:
            if self.mode == ProcessingMode.THREAD_POOL:
                # 각 단계를 병렬 처리
                futures = [
                    self._executor.submit(stage, item)
                    for item in result
                ]
                result = [f.result() for f in futures]
            else:
                # 순차 처리
                result = [stage(item) for item in result]
        
        return result
    
    def map_reduce(
        self,
        data: List[Any],
        map_func: Callable,
        reduce_func: Callable
    ) -> Any:
        """Map-Reduce 패턴 구현
        
        Args:
            data: 입력 데이터
            map_func: Map 함수
            reduce_func: Reduce 함수
            
        Returns:
            집계된 결과
        """
        # Map 단계
        if self.mode in [ProcessingMode.THREAD_POOL, ProcessingMode.PROCESS_POOL]:
            futures = [
                self._executor.submit(map_func, item)
                for item in data
            ]
            mapped = [f.result() for f in futures]
        else:
            mapped = [map_func(item) for item in data]
        
        # Reduce 단계
        return reduce_func(mapped)
    
    def get_stats(self) -> Dict[str, Any]:
        """통계 반환"""
        elapsed = time.time() - self.stats['start_time']
        total = self.stats['total_requests'] + self.stats['total_errors']
        
        return {
            'mode': self.mode.value,
            'max_workers': self.max_workers,
            'total_requests': self.stats['total_requests'],
            'total_errors': self.stats['total_errors'],
            'success_rate': self.stats['total_requests'] / max(total, 1),
            'elapsed_time': elapsed,
            'throughput': total / elapsed if elapsed > 0 else 0
        }
    
    def shutdown(self):
        """종료"""
        if self._executor:
            self._executor.shutdown(wait=True)
    
    def __enter__(self):
        """Context manager 진입"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        self.shutdown()


# 프로세스 풀용 함수 (최상위 레벨에 정의)
def _process_chunk(stock_codes: List[str]) -> List[Any]:
    """프로세스에서 청크 처리"""
    from .kiwoom_rest import KiwoomRest
    
    api = KiwoomRest()
    results = []
    
    for code in stock_codes:
        try:
            result = api.get_stock_price(code)
            results.append(result)
        except Exception as e:
            logger.error(f"Error fetching {code}: {e}")
    
    return results


class OptimizedBatchProcessor:
    """최적화된 배치 처리기"""
    
    def __init__(self):
        """초기화"""
        self.benchmarks = {}
    
    def benchmark_modes(
        self,
        stock_codes: List[str],
        sample_size: int = 5
    ) -> ProcessingMode:
        """각 모드 벤치마크 후 최적 모드 선택
        
        Args:
            stock_codes: 테스트할 종목 코드
            sample_size: 샘플 크기
            
        Returns:
            최적 처리 모드
        """
        sample = stock_codes[:sample_size]
        results = {}
        
        # 각 모드 테스트
        for mode in ProcessingMode:
            with ConcurrentKiwoomAPI(mode=mode) as api:
                result = api.fetch_stock_prices(sample)
                results[mode] = result.throughput
                
                logger.info(
                    f"{mode.value}: {result.throughput:.2f} req/s "
                    f"(성공률: {result.success_rate*100:.1f}%)"
                )
        
        # 최적 모드 선택
        best_mode = max(results, key=results.get)
        self.benchmarks = results
        
        return best_mode
    
    def auto_process(
        self,
        stock_codes: List[str]
    ) -> BatchResult:
        """자동 최적화 처리
        
        Args:
            stock_codes: 종목 코드 리스트
            
        Returns:
            처리 결과
        """
        # 최적 모드 선택
        if len(stock_codes) > 20:
            # 많은 경우 벤치마크
            best_mode = self.benchmark_modes(stock_codes)
        else:
            # 적은 경우 기본 스레드 풀
            best_mode = ProcessingMode.THREAD_POOL
        
        # 최적 모드로 처리
        with ConcurrentKiwoomAPI(mode=best_mode) as api:
            return api.fetch_stock_prices(stock_codes)


# 편의 함수들
def fetch_stocks_parallel(
    stock_codes: List[str],
    max_workers: int = 10
) -> Dict[str, Any]:
    """병렬로 여러 종목 조회 (간편 함수)"""
    with ConcurrentKiwoomAPI(
        mode=ProcessingMode.THREAD_POOL,
        max_workers=max_workers
    ) as api:
        result = api.fetch_stock_prices(stock_codes)
        
        # 딕셔너리로 변환
        stock_dict = {}
        for i, code in enumerate(stock_codes):
            if i < len(result.results):
                stock_dict[code] = result.results[i]
        
        return stock_dict


def benchmark_all_modes(stock_codes: List[str]) -> Dict[str, float]:
    """모든 모드 벤치마크"""
    processor = OptimizedBatchProcessor()
    processor.benchmark_modes(stock_codes, sample_size=min(10, len(stock_codes)))
    return processor.benchmarks