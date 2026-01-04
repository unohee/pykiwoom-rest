"""
Base API Client with Rate Limiting and Error Handling
작성일: 2025-01-27
목적: 모든 API 클라이언트의 기본 클래스 제공
"""

import logging
import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Dict, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class RateLimitExceededError(Exception):
    """Rate limit 초과 시 발생하는 예외"""

    pass


class APIError(Exception):
    """API 호출 관련 일반 예외"""

    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class TokenBucketRateLimiter:
    """
    Token Bucket 알고리즘 기반 Rate Limiter
    초당 최대 요청 수를 제한
    """

    def __init__(self, rate: int = 20, per_seconds: float = 1.0):
        """
        Args:
            rate: 허용되는 요청 수
            per_seconds: 시간 단위 (초)
        """
        self.rate = rate
        self.per_seconds = per_seconds
        self.max_tokens = rate
        self.tokens = rate
        self.last_update = time.monotonic()
        self.lock = threading.Lock()

    def acquire(self, tokens: int = 1, blocking: bool = True, timeout: float = None) -> bool:
        """
        토큰 획득 시도

        Args:
            tokens: 필요한 토큰 수
            blocking: 토큰이 없을 때 대기 여부
            timeout: 최대 대기 시간

        Returns:
            토큰 획득 성공 여부
        """
        if tokens > self.max_tokens:
            raise ValueError(f"요청한 토큰 수({tokens})가 최대값({self.max_tokens})을 초과")

        deadline = None
        if timeout is not None:
            deadline = time.monotonic() + timeout

        while True:
            with self.lock:
                self._refill()

                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return True

                if not blocking:
                    return False

                # 다음 토큰 보충까지 필요한 시간 계산
                tokens_needed = tokens - self.tokens
                wait_time = (tokens_needed / self.rate) * self.per_seconds

            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                wait_time = min(wait_time, remaining)

            time.sleep(wait_time)

    def _refill(self):
        """토큰 버킷 보충"""
        now = time.monotonic()
        elapsed = now - self.last_update

        # 경과 시간에 따라 토큰 보충
        tokens_to_add = elapsed * (self.rate / self.per_seconds)
        self.tokens = min(self.max_tokens, self.tokens + tokens_to_add)
        self.last_update = now

    def reset(self):
        """Rate limiter 초기화"""
        with self.lock:
            self.tokens = self.max_tokens
            self.last_update = time.monotonic()


class ErrorHandlerMixin:
    """에러 처리 및 재시도 로직 Mixin"""

    def __init__(self, max_retries: int = 3, backoff_factor: float = 1.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.logger = logging.getLogger(self.__class__.__name__)

    def with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        재시도 로직이 적용된 함수 실행

        Args:
            func: 실행할 함수
            *args, **kwargs: 함수 인자

        Returns:
            함수 실행 결과
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)

            except requests.exceptions.Timeout as e:
                last_exception = e
                wait_time = self.backoff_factor * (2**attempt)
                # 전체 traceback 기록 후 재시도
                self.logger.exception(
                    f"Timeout 발생 (시도 {attempt + 1}/{self.max_retries}). {wait_time}초 후 재시도..."
                )
                time.sleep(wait_time)

            except requests.exceptions.ConnectionError as e:
                last_exception = e
                wait_time = self.backoff_factor * (2**attempt)
                self.logger.exception(
                    f"연결 오류 (시도 {attempt + 1}/{self.max_retries}). {wait_time}초 후 재시도..."
                )
                time.sleep(wait_time)

            except requests.exceptions.HTTPError as e:
                # 4xx 에러는 재시도하지 않음
                # 에러 메시지에서 상태 코드 추출 시도
                status_code = None
                if hasattr(e, "response") and e.response:
                    status_code = e.response.status_code
                elif "404" in str(e):
                    status_code = 404
                elif "400" in str(e):
                    status_code = 400
                elif "401" in str(e):
                    status_code = 401
                elif "403" in str(e):
                    status_code = 403

                if status_code and 400 <= status_code < 500:
                    # 전체 traceback 포함 로깅 후 APIError로 재발생
                    self.logger.exception("클라이언트 에러")
                    raise APIError(
                        str(e),
                        status_code=status_code,
                        response=(
                            e.response.json() if hasattr(e, "response") and e.response else None
                        ),
                    )

                # 5xx 에러는 재시도
                last_exception = e
                wait_time = self.backoff_factor * (2**attempt)
                self.logger.exception(
                    f"서버 에러 (시도 {attempt + 1}/{self.max_retries}). {wait_time}초 후 재시도..."
                )
                time.sleep(wait_time)

            except Exception:
                # 예외 삼킴 없이 전체 traceback 로깅 후 재발생
                self.logger.exception("예상치 못한 에러")
                raise

        # 모든 재시도 실패
        self.logger.exception(f"모든 재시도 실패: {last_exception}")

        # Timeout과 ConnectionError는 APIError로 래핑
        if isinstance(
            last_exception,
            (requests.exceptions.Timeout, requests.exceptions.ConnectionError),
        ):
            # 전체 traceback은 위에서 기록됨. APIError로 래핑하여 재발생
            raise APIError(str(last_exception), status_code=None, response=None)
        raise last_exception


class BaseAPIClient(ABC, ErrorHandlerMixin):
    """
    모든 API 클라이언트의 기본 클래스
    Rate limiting, 에러 처리, 연결 관리 제공
    """

    def __init__(
        self,
        base_url: str,
        rate_limit: int = 20,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
        timeout: int = 30,
    ):
        """
        Args:
            base_url: API 기본 URL
            rate_limit: 초당 최대 요청 수
            max_retries: 최대 재시도 횟수
            backoff_factor: 재시도 대기 시간 증가율
            timeout: 요청 타임아웃 (초)
        """
        super().__init__(max_retries=max_retries, backoff_factor=backoff_factor)

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.rate_limiter = TokenBucketRateLimiter(rate=rate_limit)

        # Session 설정 (Connection Pooling)
        self.session = self._create_session()

        # 요청 통계
        self.request_count = 0
        self.error_count = 0
        self.last_request_time = None

        # stats 속성 추가 (테스트 호환성)
        self.stats = {
            "total_requests": 0,
            "total_errors": 0,
            "success_rate": 0.0,
            "last_request_time": None,
        }

        # Logger 설정
        self.logger = logging.getLogger(self.__class__.__name__)

    def _create_session(self) -> requests.Session:
        """HTTP Session 생성 및 설정"""
        session = requests.Session()

        # Retry 전략 설정
        retry = Retry(
            total=0,  # ErrorHandlerMixin에서 처리하므로 여기서는 비활성화
            backoff_factor=0.3,
            status_forcelist=[502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=20)

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _make_request(
        self,
        method: str,
        endpoint: str,
        headers: Dict[str, str] = None,
        params: Dict[str, Any] = None,
        data: Dict[str, Any] = None,
        json_data: Dict[str, Any] = None,
        use_rate_limit: bool = True,
    ) -> requests.Response:
        """
        HTTP 요청 실행 (내부 메서드)

        Args:
            method: HTTP 메서드
            endpoint: API 엔드포인트
            headers: 요청 헤더
            params: Query 파라미터
            data: Form 데이터
            json_data: JSON 데이터
            use_rate_limit: Rate limiting 적용 여부

        Returns:
            Response 객체
        """
        # Rate limiting 적용
        if use_rate_limit and not self.rate_limiter.acquire(blocking=True, timeout=60):
            raise RateLimitExceededError("Rate limit 대기 시간 초과")

        # URL 생성
        url = f"{self.base_url}{endpoint}"

        # 요청 실행
        self.last_request_time = datetime.now()
        self.request_count += 1

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json_data,
                timeout=self.timeout,
            )

            response.raise_for_status()

            # 통계 업데이트
            self.request_count += 1
            self.stats["total_requests"] += 1
            self.stats["last_request_time"] = time.time()
            if self.stats["total_requests"] > 0:
                self.stats["success_rate"] = 1 - (
                    self.stats["total_errors"] / self.stats["total_requests"]
                )

            return response

        except Exception as e:
            # 예외 삼킴 없이 전체 traceback 로깅 후 재발생
            self.error_count += 1
            self.stats["total_errors"] += 1
            self.stats["total_requests"] += 1
            if self.stats["total_requests"] > 0:
                self.stats["success_rate"] = 1 - (
                    self.stats["total_errors"] / self.stats["total_requests"]
                )

            # 429 Rate Limiting 에러는 조용히 처리 (일반적인 현상)
            if hasattr(e, "response") and e.response is not None and e.response.status_code == 429:
                pass  # 429 에러는 로그 출력 생략
            else:
                self.logger.exception("요청 처리 실패")
            raise

    def request(
        self,
        method: str,
        endpoint: str,
        headers: Dict[str, str] = None,
        params: Dict[str, Any] = None,
        data: Dict[str, Any] = None,
        json_data: Dict[str, Any] = None,
        use_retry: bool = True,
        use_rate_limit: bool = True,
    ) -> Union[Dict[str, Any], Any]:
        """
        API 요청 실행 (공개 메서드)

        Args:
            method: HTTP 메서드
            endpoint: API 엔드포인트
            headers: 요청 헤더
            params: Query 파라미터
            data: Form 데이터
            json_data: JSON 데이터
            use_retry: 재시도 로직 적용 여부
            use_rate_limit: Rate limiting 적용 여부

        Returns:
            API 응답 (dict)
        """
        # 헤더 준비
        headers = self._prepare_headers(headers)

        # 요청 실행
        if use_retry:
            response = self.with_retry(
                self._make_request,
                method=method,
                endpoint=endpoint,
                headers=headers,
                params=params,
                data=data,
                json_data=json_data,
                use_rate_limit=use_rate_limit,
            )
        else:
            response = self._make_request(
                method=method,
                endpoint=endpoint,
                headers=headers,
                params=params,
                data=data,
                json_data=json_data,
                use_rate_limit=use_rate_limit,
            )

        # 응답 처리
        return self._process_response(response)

    @abstractmethod
    def _prepare_headers(self, headers: Dict[str, str] = None) -> Dict[str, str]:
        """
        요청 헤더 준비 (하위 클래스에서 구현)

        Args:
            headers: 기본 헤더

        Returns:
            완성된 헤더
        """
        pass

    @abstractmethod
    def _process_response(self, response: requests.Response) -> Union[Dict[str, Any], Any]:
        """
        응답 처리 (하위 클래스에서 구현)

        Args:
            response: HTTP 응답

        Returns:
            처리된 응답 데이터 (Dict 또는 다른 타입)
        """
        pass

    def get_stats(self) -> Dict[str, Any]:
        """API 호출 통계 반환"""
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(self.request_count, 1),
            "last_request_time": self.last_request_time,
            "rate_limit_tokens": self.rate_limiter.tokens,
        }

    def reset_stats(self):
        """통계 초기화"""
        self.request_count = 0
        self.error_count = 0
        self.last_request_time = None

    def close(self):
        """세션 종료"""
        if self.session:
            self.session.close()

    def __enter__(self):
        """Context manager 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        self.close()

    def health_check(self) -> bool:
        """
        API 연결 상태 확인
        하위 클래스에서 구체적인 구현 제공
        """
        return True
