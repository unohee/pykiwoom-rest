#!/usr/bin/env python3
"""
통합 API 파사드 클래스
모든 API 호출을 단일 지점으로 집중화하여 Rate Limiting을 정확하게 관리

작성일: 2025-01-28
목적:
- 모든 API 호출을 단일 파사드로 통합
- Rate Limiting 중앙 집중 관리
- 싱글턴 패턴으로 인스턴스 관리
- 요청 추적 및 모니터링
"""

import contextlib
import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .base_api import BaseAPIClient


class RequestPriority(Enum):
    """API 요청 우선순위"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class APIRequest:
    """API 요청 정보"""

    method: str
    endpoint: str
    headers: Dict[str, str]
    data: Optional[Dict[str, Any]] = None
    priority: RequestPriority = RequestPriority.NORMAL
    created_at: float = None
    retries: int = 0
    max_retries: int = 3

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


class GlobalRateLimiter:
    """전역 Rate Limiter - 모든 API 호출 통합 관리"""

    def __init__(self, max_requests_per_second: int = 20):
        self.max_requests_per_second = max_requests_per_second
        self.request_times: List[float] = []
        self.lock = threading.RLock()

        # 통계
        self.total_requests = 0
        self.blocked_requests = 0
        self.last_block_time = None

    def can_make_request(self) -> bool:
        """요청 가능 여부 확인"""
        with self.lock:
            now = time.time()

            # 1초 이전 요청들 제거
            self.request_times = [t for t in self.request_times if now - t <= 1.0]

            return len(self.request_times) < self.max_requests_per_second

    def wait_for_slot(self, timeout: float = 10.0) -> bool:
        """요청 슬롯이 생길 때까지 대기"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.can_make_request():
                return True

            with self.lock:
                if self.request_times:
                    # 가장 오래된 요청 시간 기준으로 대기
                    oldest_request = min(self.request_times)
                    wait_time = max(0.05, 1.1 - (time.time() - oldest_request))
                else:
                    wait_time = 0.05

            time.sleep(wait_time)

        return False

    def record_request(self):
        """요청 기록"""
        with self.lock:
            now = time.time()
            self.request_times.append(now)
            self.total_requests += 1

    def record_block(self):
        """차단 기록"""
        with self.lock:
            self.blocked_requests += 1
            self.last_block_time = time.time()

    def get_stats(self) -> Dict[str, Any]:
        """통계 정보 반환"""
        with self.lock:
            return {
                "total_requests": self.total_requests,
                "blocked_requests": self.blocked_requests,
                "current_queue_size": len(self.request_times),
                "max_requests_per_second": self.max_requests_per_second,
                "block_rate": self.blocked_requests / max(1, self.total_requests),
                "last_block_time": self.last_block_time,
            }


class KiwoomAPIFacade:
    """키움증권 API 통합 파사드 클래스 (싱글턴)"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """싱글턴 패턴 구현"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        account_no: str = None,
        appkey: str = None,
        appsecret: str = None,
        env_path: str = None,
        use_mock: bool = False,
        max_requests_per_second: int = 20,
        request_timeout: float = 30.0,
    ):
        # 이미 초기화된 경우 재초기화 방지
        if hasattr(self, "_initialized"):
            return

        self.logger = logging.getLogger(__name__)

        # Rate Limiter 초기화
        self.global_rate_limiter = GlobalRateLimiter(max_requests_per_second)

        # Base API 인스턴스 - URL은 나중에 동적으로 설정
        self.base_url = (
            "https://mockapi.kiwoom.com" if use_mock else "https://api.kiwoom.com"
        )
        self.base_api = BaseAPIClient(
            base_url=self.base_url,
            rate_limit=max_requests_per_second,
            timeout=int(request_timeout),
        )

        # 설정
        self.request_timeout = request_timeout

        # 통계
        self.facade_stats = {
            "total_facade_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "rate_limited_requests": 0,
            "start_time": time.time(),
        }

        # 요청 히스토리 (최근 1000개)
        self.request_history: List[Dict[str, Any]] = []
        self.history_lock = threading.Lock()

        self._initialized = True

        self.logger.info("KiwoomAPIFacade 초기화 완료 (싱글턴)")

    @classmethod
    def get_instance(cls, **kwargs) -> "KiwoomAPIFacade":
        """싱글턴 인스턴스 반환"""
        if cls._instance is None:
            cls._instance = cls(**kwargs)
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """싱글턴 인스턴스 리셋 (테스트용)"""
        with cls._lock:
            if cls._instance:
                with contextlib.suppress(Exception):
                    cls._instance.close()
            cls._instance = None

    def _record_request_history(
        self,
        request: APIRequest,
        response_time: float,
        success: bool,
        error: str = None,
    ):
        """요청 히스토리 기록"""
        with self.history_lock:
            record = {
                "timestamp": datetime.now().isoformat(),
                "method": request.method,
                "endpoint": request.endpoint,
                "priority": request.priority.name,
                "response_time": response_time,
                "success": success,
                "retries": request.retries,
                "error": error,
            }

            self.request_history.append(record)

            # 최근 1000개만 유지
            if len(self.request_history) > 1000:
                self.request_history = self.request_history[-1000:]

    def make_request(
        self,
        method: str,
        endpoint: str,
        headers: Dict[str, str] = None,
        data: Dict[str, Any] = None,
        priority: RequestPriority = RequestPriority.NORMAL,
        use_rate_limit: bool = True,
    ) -> Dict[str, Any]:
        """통합 API 요청 메서드"""

        # 요청 객체 생성
        api_request = APIRequest(
            method=method,
            endpoint=endpoint,
            headers=headers or {},
            data=data,
            priority=priority,
        )

        start_time = time.time()
        error_msg = None

        try:
            self.facade_stats["total_facade_requests"] += 1

            # Rate Limiting 적용
            if use_rate_limit:
                if not self.global_rate_limiter.wait_for_slot(
                    timeout=self.request_timeout
                ):
                    self.facade_stats["rate_limited_requests"] += 1
                    self.global_rate_limiter.record_block()
                    raise Exception(f"Rate limit timeout after {self.request_timeout}s")

                self.global_rate_limiter.record_request()

            # 실제 API 호출
            response = self.base_api._make_request(
                method=method,
                endpoint=endpoint,
                headers=headers,
                json_data=data,  # data -> json_data로 변경
                use_rate_limit=False,  # 이미 파사드에서 처리했으므로
            )

            # 성공 처리
            if response.status_code == 200:
                result = response.json() if hasattr(response, "json") else {}
                self.facade_stats["successful_requests"] += 1

                # 히스토리 기록
                response_time = time.time() - start_time
                self._record_request_history(api_request, response_time, True)

                return result
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")

        except Exception as e:
            error_msg = str(e)
            self.facade_stats["failed_requests"] += 1

            # 429 에러 처리
            if "429" in error_msg:
                self.facade_stats["rate_limited_requests"] += 1

            # 재시도 로직
            if api_request.retries < api_request.max_retries:
                api_request.retries += 1

                # 재시도 대기 시간 (지수 백오프)
                wait_time = (2**api_request.retries) * 0.1
                time.sleep(wait_time)

                self.logger.debug(
                    f"API 요청 재시도 {api_request.retries}/{api_request.max_retries}: {endpoint}"
                )
                return self.make_request(
                    method, endpoint, headers, data, priority, use_rate_limit
                )

            # 히스토리 기록
            response_time = time.time() - start_time
            self._record_request_history(api_request, response_time, False, error_msg)

            raise e

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """종합 통계 정보"""
        uptime = time.time() - self.facade_stats["start_time"]

        return {
            "facade_stats": {
                **self.facade_stats,
                "uptime_seconds": uptime,
                "requests_per_second": self.facade_stats["total_facade_requests"]
                / max(1, uptime),
                "success_rate": self.facade_stats["successful_requests"]
                / max(1, self.facade_stats["total_facade_requests"]),
            },
            "rate_limiter_stats": self.global_rate_limiter.get_stats(),
            "base_api_stats": self.base_api.get_stats(),
            "recent_requests": len(self.request_history),
            "instance_info": {
                "singleton_id": id(self),
                "initialized_at": datetime.fromtimestamp(
                    self.facade_stats["start_time"]
                ).isoformat(),
            },
        }

    def get_recent_requests(self, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 요청 히스토리"""
        with self.history_lock:
            return self.request_history[-limit:] if self.request_history else []

    def health_check(self) -> Dict[str, Any]:
        """헬스 체크"""
        try:
            # 간단한 API 호출로 연결 상태 확인 (실제 API endpoint로 교체 필요)
            stats = self.get_comprehensive_stats()

            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "facade_healthy": True,
                "rate_limiter_healthy": self.global_rate_limiter.can_make_request(),
                "base_api_healthy": True,
                "stats_summary": {
                    "total_requests": stats["facade_stats"]["total_facade_requests"],
                    "success_rate": stats["facade_stats"]["success_rate"],
                    "current_rate_limit_queue": stats["rate_limiter_stats"][
                        "current_queue_size"
                    ],
                },
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "facade_healthy": False,
            }

    def close(self):
        """리소스 정리"""
        try:
            if hasattr(self, "base_api"):
                self.base_api.close()

            self.logger.info("KiwoomAPIFacade 정리 완료")
        except Exception as e:
            self.logger.error(f"KiwoomAPIFacade 정리 중 오류: {e}")

    def __enter__(self):
        """Context manager 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        # 싱글턴이므로 실제로 close하지 않음
        pass
