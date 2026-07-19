"""
Rate Limiting 회피 최적화 모듈
작성일: 2025-01-13

키움 API의 유량 제한을 효율적으로 회피하기 위한 최적화 전략:
1. 다중 앱키/시크릿 로테이션
2. 지능형 백오프 알고리즘
3. 요청 분산 및 큐잉
4. 429 에러 자동 감지 및 대응
"""

import logging
import math
import queue
import random
import threading
import time
from collections import defaultdict, deque
from itertools import count
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class RateLimitOptimizer:
    """고급 Rate Limiting 회피 최적화 클래스"""

    def __init__(
        self,
        credentials_list: Optional[List[Dict[str, str]]] = None,
        base_rate_limit: int = 20,  # 초당 기본 제한
        burst_capacity: int = 50,  # 버스트 허용량
        recovery_time: int = 60,  # 회복 시간(초)
        enable_rotation: bool = True,
        request_queue_maxsize: int = 10000,
    ):
        """
        Args:
            credentials_list: 여러 앱키/시크릿 리스트
            base_rate_limit: 기본 초당 요청 제한
            burst_capacity: 버스트 모드 최대 허용량
            recovery_time: 제한 도달 후 회복 시간
            enable_rotation: 크레덴셜 로테이션 활성화
            request_queue_maxsize: 요청 큐 최대 크기
        """
        if base_rate_limit <= 0:
            raise ValueError("base_rate_limit must be positive")
        if burst_capacity <= 0:
            raise ValueError("burst_capacity must be positive")
        if recovery_time <= 0:
            raise ValueError("recovery_time must be positive")
        if request_queue_maxsize <= 0:
            raise ValueError("request_queue_maxsize must be positive")

        self.credentials_list = credentials_list or []
        self.base_rate_limit = base_rate_limit
        self.burst_capacity = burst_capacity
        self.recovery_time = recovery_time
        self.enable_rotation = enable_rotation and len(self.credentials_list) > 1

        # 현재 활성 크레덴셜 인덱스
        self.current_credential_idx = 0
        self.credential_locks = [threading.Lock() for _ in self.credentials_list]

        # 각 크레덴셜별 토큰 버킷
        self.token_buckets = {}
        self.request_history = defaultdict(deque)  # 요청 이력
        self.error_counts = defaultdict(int)  # 에러 카운트
        self.last_429_time = {}  # 마지막 429 에러 시간

        # 글로벌 통계
        self.total_requests = 0
        self.total_429_errors = 0
        self.total_rotations = 0

        # 요청 큐 (우선순위 큐)
        self.request_queue = queue.PriorityQueue(maxsize=request_queue_maxsize)
        self._queue_sequence = count()
        self.queue_processor_thread = None
        self._stop_queue_processor = threading.Event()

        # 초기화
        self._initialize_token_buckets()

    def _initialize_token_buckets(self):
        """각 크레덴셜별 토큰 버킷 초기화"""
        for i, cred in enumerate(self.credentials_list):
            key = f"{cred.get('APPKEY', '')}_{i}"
            self.token_buckets[key] = {
                "tokens": self.base_rate_limit,
                "max_tokens": self.burst_capacity,
                "last_refill": time.time(),
                "is_blocked": False,
                "block_until": None,
                "consecutive_errors": 0,
            }

    def get_optimal_credential(self) -> Tuple[int, Optional[Dict[str, str]]]:
        """
        최적의 크레덴셜 선택 (로드 밸런싱)

        Returns:
            (인덱스, 크레덴셜 딕셔너리)
        """
        if not self.credentials_list:
            return -1, None

        now = time.time()

        if not self.enable_rotation:
            cred = self.credentials_list[0]
            key = f"{cred.get('APPKEY', '')}_0"
            with self.credential_locks[0]:
                bucket = self.token_buckets.get(key, {})

                if bucket.get("is_blocked"):
                    block_until = bucket.get("block_until")
                    if block_until and now > block_until:
                        bucket["is_blocked"] = False
                        bucket["block_until"] = None
                        bucket["consecutive_errors"] = 0
                    else:
                        if block_until is None:
                            logger.warning("크레덴셜 0 차단: 해제 시간이 없습니다.")
                        else:
                            wait_time = max(0, block_until - now)
                            logger.warning(f"크레덴셜 0 차단. {wait_time:.1f}초 후 재시도 가능")
                        return -1, None

            return 0, cred

        best_idx = -1
        best_score = -1

        for i, cred in enumerate(self.credentials_list):
            key = f"{cred.get('APPKEY', '')}_{i}"
            with self.credential_locks[i]:
                bucket = self.token_buckets.get(key, {})

                # 차단된 크레덴셜 스킵
                if bucket.get("is_blocked"):
                    block_until = bucket.get("block_until")
                    if block_until and now > block_until:
                        # 차단 해제
                        bucket["is_blocked"] = False
                        bucket["block_until"] = None
                        bucket["consecutive_errors"] = 0
                    else:
                        continue

                # 점수 계산 (토큰 수 + 에러 페널티)
                score = bucket.get("tokens", 0) - (bucket.get("consecutive_errors", 0) * 10)

            if score > best_score:
                best_score = score
                best_idx = i

        if best_idx >= 0:
            self.total_rotations += 1
            return best_idx, self.credentials_list[best_idx]

        # 모든 크레덴셜이 차단된 경우, 가장 빨리 해제되는 것 선택
        earliest_unblock = float("inf")

        for i, cred in enumerate(self.credentials_list):
            key = f"{cred.get('APPKEY', '')}_{i}"
            with self.credential_locks[i]:
                bucket = self.token_buckets.get(key, {})
                unblock_time = bucket.get("block_until")

            if (
                isinstance(unblock_time, (int, float))
                and math.isfinite(unblock_time)
                and unblock_time < earliest_unblock
            ):
                earliest_unblock = unblock_time

        # 차단 상태에서는 호출자를 블로킹하지 않고 실패 신호를 반환한다.
        wait_time = max(0, earliest_unblock - now)
        if not math.isfinite(wait_time):
            logger.warning("모든 크레덴셜의 차단 해제 시간이 유효하지 않습니다.")
            return -1, None
        logger.warning(f"모든 크레덴셜 차단. {wait_time:.1f}초 후 재시도 가능")

        return -1, None

    def acquire_token_result(
        self, credential_idx: Optional[int] = None, priority: int = 5
    ) -> Tuple[bool, Optional[int]]:
        """
        토큰 획득 및 실제 사용된 크레덴셜 반환 (우선순위 기반)

        Args:
            credential_idx: 특정 크레덴셜 지정
            priority: 요청 우선순위 (1=최고, 10=최저)

        Returns:
            (토큰 획득 성공 여부, 사용된 크레덴셜 인덱스)
        """
        if not self.credentials_list:
            return False, None

        if credential_idx is not None and (
            credential_idx < 0 or credential_idx >= len(self.credentials_list)
        ):
            return False, None

        while True:
            if credential_idx is None:
                selected_idx, _ = self.get_optimal_credential()
                if selected_idx < 0 or selected_idx >= len(self.credentials_list):
                    return False, None

                candidate_indices = [selected_idx]
                if self.enable_rotation:
                    candidate_indices.extend(
                        idx for idx in range(len(self.credentials_list)) if idx != selected_idx
                    )
            else:
                candidate_indices = [credential_idx]

            shortest_wait = None

            for idx in candidate_indices:
                cred = self.credentials_list[idx]
                key = f"{cred.get('APPKEY', '')}_{idx}"
                bucket = self.token_buckets[key]

                with self.credential_locks[idx]:
                    if bucket.get("is_blocked"):
                        block_until = bucket.get("block_until")
                        if block_until and time.time() >= block_until:
                            bucket["is_blocked"] = False
                            bucket["block_until"] = None
                            bucket["consecutive_errors"] = 0
                        else:
                            if block_until:
                                wait_time = max(0, block_until - time.time())
                                shortest_wait = (
                                    wait_time
                                    if shortest_wait is None
                                    else min(shortest_wait, wait_time)
                                )
                            continue

                    # 토큰 리필
                    self._refill_tokens(bucket)

                    # 토큰 확인
                    if bucket["tokens"] >= 1:
                        bucket["tokens"] -= 1
                        self.total_requests += 1

                        # 요청 이력 기록
                        self.request_history[key].append(time.time())
                        if len(self.request_history[key]) > 100:
                            self.request_history[key].popleft()

                        return True, idx

                    # 토큰 부족 - 락 밖에서 대기 또는 다른 크레덴셜 시도
                    wait_time = self._calculate_wait_time(bucket)
                    shortest_wait = (
                        wait_time if shortest_wait is None else min(shortest_wait, wait_time)
                    )

            if shortest_wait is None:
                return False, None

            logger.debug(f"토큰 대기: {shortest_wait:.3f}초")
            time.sleep(shortest_wait)

    def acquire_token(self, credential_idx: Optional[int] = None, priority: int = 5) -> bool:
        """토큰 획득 (우선순위 기반)."""
        acquired, _ = self.acquire_token_result(credential_idx, priority)
        return acquired

    def _refill_tokens(self, bucket: Dict[str, Any]):
        """토큰 버킷 리필"""
        now = time.time()
        time_passed = now - bucket["last_refill"]

        # 토큰 리필 계산
        tokens_to_add = time_passed * self.base_rate_limit
        bucket["tokens"] = min(bucket["max_tokens"], bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = now

    def _calculate_wait_time(self, bucket: Dict[str, Any]) -> float:
        """필요한 대기 시간 계산"""
        tokens_needed = 1 - bucket["tokens"]
        if tokens_needed <= 0:
            return 0

        # 지능형 백오프
        base_wait = tokens_needed / self.base_rate_limit

        # 연속 에러에 따른 추가 대기
        error_penalty = bucket.get("consecutive_errors", 0) * 0.5

        # 랜덤 지터 추가 (충돌 방지)
        jitter = random.uniform(0, 0.1)  # nosec B311 - rate limit jitter, not security

        return base_wait + error_penalty + jitter

    def handle_429_error(self, credential_idx: int):
        """429 (Too Many Requests) 에러 처리"""
        if credential_idx < 0 or credential_idx >= len(self.credentials_list):
            logger.warning("Invalid credential_idx for 429 handling: %s", credential_idx)
            return

        self.total_429_errors += 1

        cred = self.credentials_list[credential_idx]
        key = f"{cred.get('APPKEY', '')}_{credential_idx}"
        bucket = self.token_buckets[key]

        with self.credential_locks[credential_idx]:
            bucket["consecutive_errors"] += 1
            bucket["tokens"] = 0  # 토큰 고갈

            # 지수 백오프
            backoff_time = min(300, self.recovery_time * (2 ** (bucket["consecutive_errors"] - 1)))
            bucket["is_blocked"] = True
            bucket["block_until"] = time.time() + backoff_time

            logger.warning(f"429 에러 - 크레덴셜 {credential_idx} 차단 ({backoff_time:.1f}초)")

            # 다른 크레덴셜로 자동 전환
            if self.enable_rotation:
                self.current_credential_idx = (credential_idx + 1) % len(self.credentials_list)

    def reset_error_count(self, credential_idx: int):
        """에러 카운트 리셋 (성공 시 호출)"""
        if credential_idx < 0 or credential_idx >= len(self.credentials_list):
            return

        cred = self.credentials_list[credential_idx]
        key = f"{cred.get('APPKEY', '')}_{credential_idx}"
        bucket = self.token_buckets[key]

        with self.credential_locks[credential_idx]:
            bucket["consecutive_errors"] = 0
            if bucket.get("is_blocked"):
                bucket["is_blocked"] = False
                bucket["block_until"] = None

    def get_stats(self) -> Dict[str, Any]:
        """통계 정보 반환"""
        now = time.time()
        for i, cred in enumerate(self.credentials_list):
            key = f"{cred.get('APPKEY', '')}_{i}"
            with self.credential_locks[i]:
                bucket = self.token_buckets.get(key, {})
                block_until = bucket.get("block_until")
                if bucket.get("is_blocked") and block_until and now > block_until:
                    bucket["is_blocked"] = False
                    bucket["block_until"] = None
                    bucket["consecutive_errors"] = 0

        active_credentials = sum(
            1 for bucket in self.token_buckets.values() if not bucket.get("is_blocked")
        )

        total_tokens = sum(bucket.get("tokens", 0) for bucket in self.token_buckets.values())

        avg_error_rate = (
            self.total_429_errors / self.total_requests * 100 if self.total_requests > 0 else 0
        )

        return {
            "total_requests": self.total_requests,
            "total_429_errors": self.total_429_errors,
            "total_rotations": self.total_rotations,
            "active_credentials": active_credentials,
            "total_credentials": len(self.credentials_list),
            "total_available_tokens": total_tokens,
            "avg_error_rate": f"{avg_error_rate:.2f}%",
            "rotation_enabled": self.enable_rotation,
        }

    def optimize_request_pattern(
        self, requests_batch: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        요청 패턴 최적화 (배치 처리)

        Args:
            requests_batch: 요청 배치 리스트

        Returns:
            최적화된 요청 순서
        """
        # 우선순위별 정렬 (nosec B311 - shuffle, not security)
        sorted_requests = sorted(
            (req.copy() for req in requests_batch),
            key=lambda x: (x.get("priority", 5), random.random()),  # nosec B311
        )
        if sorted_requests and not self.credentials_list:
            raise RuntimeError("No credentials available for request optimization")

        simulated_tokens: Dict[int, float] = {}
        simulated_blocked: Dict[int, bool] = {}
        now = time.time()
        for idx, cred in enumerate(self.credentials_list):
            key = f"{cred.get('APPKEY', '')}_{idx}"
            with self.credential_locks[idx]:
                bucket = self.token_buckets.get(key, {})
                simulated_tokens[idx] = float(bucket.get("tokens", 0))
                simulated_blocked[idx] = bool(bucket.get("is_blocked"))
                block_until = bucket.get("block_until")
                if simulated_blocked[idx] and block_until and now > block_until:
                    bucket["is_blocked"] = False
                    bucket["block_until"] = None
                    bucket["consecutive_errors"] = 0
                    simulated_blocked[idx] = False

        # 시간 분산
        optimized = []
        credential_load = defaultdict(int)
        for i, optimized_req in enumerate(sorted_requests):
            # 크레덴셜 할당: 배치 내에서 토큰을 시뮬레이션 차감해 한 곳으로 몰리지 않게 한다.
            available_indices = [
                idx
                for idx in range(len(self.credentials_list))
                if not simulated_blocked.get(idx, False) and simulated_tokens.get(idx, 0) > 0
            ]
            if available_indices:
                cred_idx = max(
                    available_indices,
                    key=lambda idx: (simulated_tokens[idx] - credential_load[idx], -idx),
                )
                simulated_tokens[cred_idx] = max(0.0, simulated_tokens[cred_idx] - 1)
                cred = self.credentials_list[cred_idx]
            else:
                cred_idx, cred = self.get_optimal_credential()
                if cred_idx < 0 or cred is None:
                    raise RuntimeError("No available credentials for request optimization")

            optimized_req["credential_idx"] = cred_idx
            optimized_req["credential"] = cred
            credential_load[cred_idx] += 1

            # 지연 시간 계산
            if i > 0:
                # 요청 간 최소 간격
                min_interval = 1.0 / self.base_rate_limit
                optimized_req["delay"] = min_interval * (1 + random.uniform(0, 0.2))  # nosec B311
            else:
                optimized_req["delay"] = 0

            optimized.append(optimized_req)

        return optimized

    def adaptive_rate_adjustment(self, success_rate: float):
        """
        성공률 기반 적응형 레이트 조정

        Args:
            success_rate: 최근 성공률 (0-1)
        """
        if not math.isfinite(success_rate) or not 0 <= success_rate <= 1:
            raise ValueError("success_rate must be a finite number between 0 and 1")

        if success_rate > 0.95:
            # 성공률 높음 - 레이트 증가
            self.base_rate_limit = min(
                30, max(self.base_rate_limit + 1, int(self.base_rate_limit * 1.1))
            )
            self.burst_capacity = min(
                100, max(self.burst_capacity + 1, int(self.burst_capacity * 1.1))
            )
            self._sync_token_bucket_capacity()
            logger.info(f"레이트 증가: {self.base_rate_limit}/초")

        elif success_rate < 0.8:
            # 성공률 낮음 - 레이트 감소
            self.base_rate_limit = max(5, int(self.base_rate_limit * 0.9))
            self.burst_capacity = max(20, int(self.burst_capacity * 0.9))
            self._sync_token_bucket_capacity()
            logger.info(f"레이트 감소: {self.base_rate_limit}/초")

    def _sync_token_bucket_capacity(self):
        """현재 burst_capacity를 기존 토큰 버킷에 반영"""
        for bucket in self.token_buckets.values():
            bucket["max_tokens"] = self.burst_capacity
            bucket["tokens"] = min(bucket.get("tokens", 0), self.burst_capacity)

    def start_queue_processor(self):
        """백그라운드 큐 프로세서 시작"""
        if self.queue_processor_thread and self.queue_processor_thread.is_alive():
            return

        self._stop_queue_processor.clear()
        self.queue_processor_thread = threading.Thread(
            target=self._process_request_queue, daemon=True
        )
        self.queue_processor_thread.start()

    def _get_next_due_queue_item(self, timeout: float = 1.0):
        """다음 실행 가능 큐 항목을 가져오며, 예약 시간이 될 때까지 재삽입 없이 대기"""
        with self.request_queue.not_empty:
            while not self._stop_queue_processor.is_set():
                if not self.request_queue.queue:
                    self.request_queue.not_empty.wait(timeout)
                    continue

                scheduled_time = self.request_queue.queue[0][0]
                wait_time = scheduled_time - time.time()
                if wait_time <= 0:
                    item = self.request_queue._get()
                    self.request_queue.not_full.notify()
                    return item

                self.request_queue.not_empty.wait(min(wait_time, timeout))

        raise queue.Empty

    def _process_request_queue(self):
        """요청 큐 처리 (백그라운드)"""
        while not self._stop_queue_processor.is_set():
            try:
                _scheduled_time, priority, _, request = self._get_next_due_queue_item(timeout=1)
            except queue.Empty:
                continue

            try:
                credential_idx = request.get("credential_idx")
                if self.acquire_token(credential_idx, priority):
                    if "callback" in request:
                        try:
                            request["callback"](request)
                        except Exception as exc:
                            self._retry_or_fail_queue_request(request, priority, "콜백 처리 실패", exc)
                            continue

                    if credential_idx is not None:
                        self.reset_error_count(credential_idx)
                else:
                    self._retry_or_fail_queue_request(request, priority, "토큰 획득 실패")

            except Exception as e:
                self._retry_or_fail_queue_request(request, priority, "큐 처리 오류", e)
            finally:
                self.request_queue.task_done()

    def _retry_or_fail_queue_request(
        self,
        request: Dict[str, Any],
        priority: int,
        reason: str,
        exc: Optional[Exception] = None,
    ) -> None:
        """큐 요청 실패 시 재시도하거나 최종 실패 콜백을 호출"""
        retry_count = request.get("_retry_count", 0) + 1
        max_retries = request.get("max_retries", 3)

        if retry_count <= max_retries:
            request["_retry_count"] = retry_count
            delay = self._calculate_queue_retry_delay(retry_count)
            scheduled_time = time.time() + delay
            try:
                self.request_queue.put(
                    (scheduled_time, priority, next(self._queue_sequence), request), timeout=1.0
                )
                logger.warning(
                    f"{reason}: 큐 요청 재시도 예약 ({retry_count}/{max_retries}, {delay:.2f}초 후)"
                )
                return
            except queue.Full:
                logger.error(f"{reason}: 재시도 큐가 가득 차 요청을 실패 처리합니다.")

        error_detail = f": {exc}" if exc is not None else ""
        logger.error(f"{reason}{error_detail}; queued request failed after {retry_count - 1} retries")
        if "error_callback" in request:
            try:
                request["error_callback"](request)
            except Exception as callback_exc:
                logger.error(f"큐 실패 콜백 처리 오류: {callback_exc}")

    def _calculate_queue_retry_delay(self, retry_count: int) -> float:
        """큐 재시도 지연 시간 계산"""
        return min(30.0, (2 ** retry_count) / max(self.base_rate_limit, 1)) + random.uniform(0, 0.1)

    def stop_queue_processor(self, timeout: float = 5.0) -> bool:
        """백그라운드 큐 프로세서 중지 및 종료 대기"""
        self._stop_queue_processor.set()
        with self.request_queue.not_empty:
            self.request_queue.not_empty.notify_all()
        return self.join_queue_processor(timeout=timeout)

    def close(self, timeout: float = 5.0) -> bool:
        """명시적으로 큐 프로세서 리소스를 정리"""
        return self.stop_queue_processor(timeout=timeout)

    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료 시 큐 프로세서 정리"""
        self.close()
        return False

    def join_queue_processor(self, timeout: float = 5.0) -> bool:
        """백그라운드 큐 프로세서 종료 대기"""
        if self.queue_processor_thread:
            self.queue_processor_thread.join(timeout=timeout)
            return not self.queue_processor_thread.is_alive()
        return True

    def add_request_to_queue(
        self, request: Dict[str, Any], priority: int = 5, timeout: float = 1.0
    ) -> bool:
        """요청을 큐에 추가"""
        timestamp = time.time()
        try:
            self.request_queue.put(
                (timestamp, priority, next(self._queue_sequence), request), timeout=timeout
            )
        except queue.Full:
            logger.warning("Rate-limit request queue is full; rejecting queued request")
            if "error_callback" in request:
                request["error_callback"](request)
            return False
        return True


class SmartRetryStrategy:
    """지능형 재시도 전략"""

    def __init__(self):
        self.retry_patterns = {
            429: {"base_delay": 60, "multiplier": 2, "max_delay": 300},
            503: {"base_delay": 5, "multiplier": 1.5, "max_delay": 60},
            "default": {"base_delay": 1, "multiplier": 1.5, "max_delay": 30},
        }

    def calculate_retry_delay(
        self, error_code: int, attempt: int, response_headers: Dict[str, str] = None
    ) -> float:
        """
        재시도 지연 시간 계산

        Args:
            error_code: HTTP 에러 코드
            attempt: 재시도 횟수
            response_headers: 응답 헤더 (Retry-After 등)

        Returns:
            대기 시간 (초)
        """
        # 에러 코드별 패턴
        pattern = self.retry_patterns.get(error_code, self.retry_patterns["default"])

        # Retry-After 헤더 확인
        if response_headers and "Retry-After" in response_headers:
            try:
                retry_after = float(response_headers["Retry-After"])
                if math.isfinite(retry_after) and retry_after >= 0:
                    return min(retry_after, pattern["max_delay"])
            except (ValueError, TypeError):
                pass

        # 지수 백오프 계산
        delay = pattern["base_delay"] * (pattern["multiplier"] ** attempt)
        delay = min(delay, pattern["max_delay"])

        # 랜덤 지터 추가
        jitter = random.uniform(0, delay * 0.1)  # nosec B311 - retry jitter, not security

        return delay + jitter
