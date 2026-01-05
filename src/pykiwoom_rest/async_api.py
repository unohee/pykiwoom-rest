"""
Async API Client for Kiwoom REST API
비동기 처리를 위한 API 클라이언트
작성일: 2025-01-05
"""

import asyncio
import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import PriorityQueue, Queue
from typing import Any, Callable, Dict, List, Optional

import aiohttp
from dotenv import load_dotenv

from .rate_limit_optimizer import RateLimitOptimizer
from .response_model import APIResponse

logger = logging.getLogger(__name__)


class AsyncKiwoomAPI:
    """비동기 Kiwoom API 클라이언트"""

    def __init__(
        self,
        appkey: str = None,
        appsecret: str = None,
        account_no: str = None,
        rate_limit: int = 20,
        max_concurrent: int = 10,
        enable_rate_optimizer: bool = True,
        credentials_list: List[Dict[str, str]] = None,
    ):
        """
        초기화

        Args:
            appkey: 앱키
            appsecret: 앱시크릿
            account_no: 계좌번호
            rate_limit: 초당 최대 요청 수
            max_concurrent: 최대 동시 요청 수
            enable_rate_optimizer: Rate limiting 최적화 활성화
            credentials_list: 다중 크레덴셜 리스트
        """
        self._load_credentials(appkey, appsecret, account_no)

        self.base_url = "https://api.kiwoom.com/uapi/v1"
        self.rate_limit = rate_limit
        self.max_concurrent = max_concurrent

        # 비동기 세션 (재사용)
        self.session: Optional[aiohttp.ClientSession] = None

        # 토큰 관리
        self.access_token = None
        self.token_expires = None
        self.token_lock = asyncio.Lock()

        # Rate limiting
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.rate_limiter = asyncio.Semaphore(rate_limit)
        self.last_request_time = 0

        # Rate optimizer
        self.enable_rate_optimizer = enable_rate_optimizer
        self.rate_optimizer = None
        if enable_rate_optimizer:
            self._setup_rate_optimizer(credentials_list)

    def _load_credentials(self, appkey: str, appsecret: str, account_no: str):
        """인증 정보 로드"""
        load_dotenv()

        self.appkey = appkey or os.getenv("KIWOOM_APPKEY")
        self.appsecret = appsecret or os.getenv("KIWOOM_APPSECRET")
        self.account_no = account_no or os.getenv("ACCOUNT_NO")

        if not all([self.appkey, self.appsecret, self.account_no]):
            raise ValueError("인증 정보가 필요합니다")

    def _setup_rate_optimizer(self, credentials_list: List[Dict[str, str]] = None):
        """Rate optimizer 설정"""
        all_credentials = []

        # 기본 크레덴셜
        all_credentials.append(
            {
                "APPKEY": self.appkey,
                "APPSECRET": self.appsecret,
                "ACCOUNT_NO": self.account_no,
            }
        )

        # 추가 크레덴셜
        if credentials_list:
            all_credentials.extend(credentials_list)

        self.rate_optimizer = RateLimitOptimizer(
            credentials_list=all_credentials,
            base_rate_limit=self.rate_limit,
            enable_rotation=len(all_credentials) > 1,
        )

    async def __aenter__(self):
        """Context manager 진입"""
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=100, limit_per_host=30, ttl_dns_cache=300),
            timeout=aiohttp.ClientTimeout(total=30),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        if self.session:
            await self.session.close()

    async def _get_access_token(self) -> str:
        """비동기 토큰 발급"""
        async with self.token_lock:
            # 토큰이 유효하면 재사용
            if self.access_token and self.token_expires and time.time() < self.token_expires:
                return self.access_token

            # 토큰 발급
            url = f"{self.base_url}/oauth2/token"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {
                "grant_type": "client_credentials",
                "client_id": self.appkey,
                "client_secret": self.appsecret,
            }

            async with self.session.post(url, headers=headers, data=data) as response:
                result = await response.json()

                self.access_token = result["access_token"]
                expires_in = result.get("expires_in", 86400)
                self.token_expires = time.time() + expires_in - 60

                return self.access_token

    async def _make_request(
        self,
        endpoint: str,
        tr_code: str,
        params: Dict[str, Any] = None,
        method: str = "POST",
    ) -> Dict[str, Any]:
        """비동기 API 요청"""
        # Rate limiting
        async with self.semaphore:
            # 토큰 획득
            token = await self._get_access_token()

            # 요청 준비
            url = f"{self.base_url}{endpoint}"
            headers = {
                "authorization": f"Bearer {token}",
                "Content-Type": "application/json;charset=UTF-8",
                "api-id": tr_code,
            }

            # Rate limit 적용
            async with self.rate_limiter:
                # 최소 간격 유지
                current_time = time.time()
                time_since_last = current_time - self.last_request_time
                if time_since_last < (1.0 / self.rate_limit):
                    await asyncio.sleep((1.0 / self.rate_limit) - time_since_last)

                self.last_request_time = time.time()

                # 요청 실행
                if method == "GET":
                    async with self.session.get(url, headers=headers, params=params) as response:
                        return await response.json()
                else:
                    async with self.session.post(url, headers=headers, json=params) as response:
                        return await response.json()

    async def get_stock_price(self, stock_code: str) -> Dict[str, Any]:
        """주식 시세 조회 (비동기)"""
        params = {"stk_cd": stock_code}

        result = await self._make_request(
            endpoint="/stock/kr-stk/stock-info", tr_code="ka10001", params=params
        )

        return APIResponse.create_success(result)

    async def get_multiple_stock_prices(self, stock_codes: List[str]) -> List[Dict[str, Any]]:
        """여러 종목 시세 동시 조회"""
        tasks = []
        for code in stock_codes:
            task = self.get_stock_price(code)
            tasks.append(task)

        # 모든 요청 동시 실행
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 에러 처리
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"종목 {stock_codes[i]} 조회 실패: {result}")
                processed_results.append(None)
            else:
                processed_results.append(result)

        return processed_results

    async def stream_stock_prices(
        self, stock_codes: List[str], interval: float = 1.0, callback: Callable = None
    ):
        """실시간 시세 스트리밍 (폴링 방식)"""
        while True:
            try:
                # 병렬 조회
                results = await self.get_multiple_stock_prices(stock_codes)

                # 콜백 실행
                if callback:
                    for code, result in zip(stock_codes, results):
                        if result:
                            await callback(code, result)

                # 대기
                await asyncio.sleep(interval)

            except Exception as e:
                logger.error(f"스트리밍 에러: {e}")
                await asyncio.sleep(5)  # 에러 시 긴 대기


class ParallelKiwoomAPI:
    """병렬 처리 Kiwoom API 클라이언트 (ThreadPoolExecutor)"""

    def __init__(
        self,
        max_workers: int = 10,
        enable_rate_optimizer: bool = True,
        credentials_list: List[Dict[str, str]] = None,
    ):
        """
        초기화

        Args:
            max_workers: 최대 워커 스레드 수
            enable_rate_optimizer: Rate limiting 최적화 활성화
            credentials_list: 다중 크레덴셜 리스트
        """
        # KiwoomRest 인스턴스를 워커별로 생성
        from .kiwoom_rest import KiwoomRest

        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        # 워커별 API 클라이언트 풀
        self.api_pool = Queue()
        for _ in range(max_workers):
            api = KiwoomRest(
                enable_rate_optimizer=enable_rate_optimizer,
                credentials_list=credentials_list,
            )
            self.api_pool.put(api)

        # 요청 큐
        self.request_queue = PriorityQueue()
        self.result_queue = Queue()

        # 통계
        self.total_requests = 0
        self.total_errors = 0
        self.start_time = time.time()

    def _worker_task(self, func: Callable, *args, **kwargs) -> Any:
        """워커 태스크 실행"""
        api = self.api_pool.get()
        try:
            result = func(api, *args, **kwargs)
            self.total_requests += 1
            return result
        except Exception as e:
            self.total_errors += 1
            logger.error(f"워커 에러: {e}")
            raise
        finally:
            self.api_pool.put(api)

    def get_stock_prices_parallel(self, stock_codes: List[str]) -> Dict[str, Any]:
        """여러 종목 병렬 조회"""
        futures = []

        for code in stock_codes:
            future = self.executor.submit(
                self._worker_task, lambda api, c: api.get_stock_price(c), code
            )
            futures.append((code, future))

        # 결과 수집
        results = {}
        for code, future in futures:
            try:
                result = future.result(timeout=10)
                results[code] = result
            except Exception as e:
                logger.error(f"종목 {code} 조회 실패: {e}")
                results[code] = None

        return results

    def batch_process(self, tasks: List[Dict[str, Any]], callback: Callable = None) -> List[Any]:
        """배치 작업 병렬 처리

        Args:
            tasks: 작업 리스트 [{'method': 'get_stock_price', 'args': ['005930']}, ...]
            callback: 각 작업 완료 시 콜백
        """
        futures = []

        for task in tasks:
            method_name = task["method"]
            args = task.get("args", [])
            kwargs = task.get("kwargs", {})

            future = self.executor.submit(
                self._worker_task,
                lambda api, m, a, k: getattr(api, m)(*a, **k),
                method_name,
                args,
                kwargs,
            )
            futures.append(future)

        # 완료된 순서대로 처리
        results = []
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)

                if callback:
                    callback(result)

            except Exception as e:
                logger.error(f"배치 작업 실패: {e}")
                results.append(None)

        return results

    def map_reduce(self, map_func: Callable, reduce_func: Callable, data: List[Any]) -> Any:
        """Map-Reduce 패턴 구현

        Args:
            map_func: 각 데이터에 적용할 함수
            reduce_func: 결과를 집계할 함수
            data: 입력 데이터 리스트
        """
        # Map 단계 - 병렬 처리
        map_futures = []
        for item in data:
            future = self.executor.submit(map_func, item)
            map_futures.append(future)

        # 결과 수집
        map_results = []
        for future in as_completed(map_futures):
            result = future.result()
            map_results.append(result)

        # Reduce 단계
        return reduce_func(map_results)

    def get_stats(self) -> Dict[str, Any]:
        """통계 반환"""
        elapsed = time.time() - self.start_time
        rps = self.total_requests / elapsed if elapsed > 0 else 0

        return {
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "elapsed_time": elapsed,
            "requests_per_second": rps,
            "error_rate": self.total_errors / max(self.total_requests, 1),
        }

    def shutdown(self):
        """Executor 종료"""
        self.executor.shutdown(wait=True)


class RealtimeWebSocketClient:
    """WebSocket 기반 실시간 데이터 클라이언트"""

    def __init__(self, appkey: str = None, appsecret: str = None):
        """
        초기화

        Args:
            appkey: 앱키
            appsecret: 앱시크릿
        """
        load_dotenv()

        self.appkey = appkey or os.getenv("KIWOOM_APPKEY")
        self.appsecret = appsecret or os.getenv("KIWOOM_APPSECRET")

        # WebSocket URL (예시 - 실제 키움 WebSocket URL 확인 필요)
        self.ws_url = "wss://api.kiwoom.com/ws/v1/realtime"

        self.ws = None
        self.callbacks = {}
        self.running = False

    async def connect(self):
        """WebSocket 연결"""
        import websockets

        self.ws = await websockets.connect(self.ws_url)
        self.running = True

        # 인증
        auth_msg = {"type": "auth", "appkey": self.appkey, "appsecret": self.appsecret}
        await self.ws.send(json.dumps(auth_msg))

        # 응답 처리 루프 시작
        asyncio.create_task(self._message_handler())

    async def _message_handler(self):
        """메시지 처리 루프"""
        while self.running:
            try:
                message = await self.ws.recv()
                data = json.loads(message)

                # 메시지 타입별 처리
                msg_type = data.get("type")
                if msg_type in self.callbacks:
                    await self.callbacks[msg_type](data)

            except Exception as e:
                logger.error(f"WebSocket 메시지 처리 에러: {e}")
                if not self.running:
                    break

    async def subscribe_stock(self, stock_code: str, callback: Callable):
        """종목 구독"""
        # 구독 메시지 전송
        sub_msg = {"type": "subscribe", "channel": "stock", "codes": [stock_code]}
        await self.ws.send(json.dumps(sub_msg))

        # 콜백 등록
        self.callbacks[f"stock_{stock_code}"] = callback

    async def unsubscribe_stock(self, stock_code: str):
        """구독 해제"""
        unsub_msg = {"type": "unsubscribe", "channel": "stock", "codes": [stock_code]}
        await self.ws.send(json.dumps(unsub_msg))

        # 콜백 제거
        self.callbacks.pop(f"stock_{stock_code}", None)

    async def disconnect(self):
        """연결 종료"""
        self.running = False
        if self.ws:
            await self.ws.close()


# 헬퍼 함수들
def create_async_client(**kwargs) -> AsyncKiwoomAPI:
    """비동기 클라이언트 생성 헬퍼"""
    return AsyncKiwoomAPI(**kwargs)


def create_parallel_client(max_workers: int = 10, **kwargs) -> ParallelKiwoomAPI:
    """병렬 클라이언트 생성 헬퍼"""
    return ParallelKiwoomAPI(max_workers=max_workers, **kwargs)


async def run_async_example():
    """비동기 사용 예제"""
    async with AsyncKiwoomAPI() as api:
        # 단일 조회
        result = await api.get_stock_price("005930")
        print(f"삼성전자: {result}")

        # 다중 조회
        codes = ["005930", "000660", "035720", "005380", "051910"]
        results = await api.get_multiple_stock_prices(codes)
        for code, result in zip(codes, results):
            if result:
                print(f"{code}: {result.data.get('stk_nm')}")


def run_parallel_example():
    """병렬 처리 예제"""
    client = ParallelKiwoomAPI(max_workers=5)

    try:
        # 병렬 조회
        codes = ["005930", "000660", "035720", "005380", "051910"]
        results = client.get_stock_prices_parallel(codes)

        for code, result in results.items():
            if result:
                print(f"{code}: 조회 성공")

        # 통계
        stats = client.get_stats()
        print(f"처리량: {stats['requests_per_second']:.2f} req/s")

    finally:
        client.shutdown()


if __name__ == "__main__":
    # 비동기 예제 실행
    asyncio.run(run_async_example())

    # 병렬 처리 예제 실행
    run_parallel_example()
