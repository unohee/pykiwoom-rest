"""
통합 Kiwoom API Base - API Facade 사용
기존 KiwoomAPIBase를 파사드 패턴으로 리팩토링

작성일: 2025-01-28
목적:
- 모든 API 호출을 KiwoomAPIFacade로 통합
- Rate Limiting 중앙 집중 관리
- 기존 인터페이스 호환성 유지
"""

import contextlib
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from .api_facade import KiwoomAPIFacade, RequestPriority
from .base_api import APIError
from .exception_utils import RaiseWithTraceMixin


class KiwoomAPIError(APIError):
    """키움증권 API 전용 예외 클래스"""

    def __init__(self, message: str, error_code: str = None, error_msg: str = None):
        super().__init__(message)
        self.error_code = error_code
        self.error_msg = error_msg


class UnifiedKiwoomAPIBase(RaiseWithTraceMixin):
    """
    통합 키움증권 REST API 기본 클래스 (Facade 패턴)
    모든 API 호출을 KiwoomAPIFacade를 통해 수행
    """

    # 키움증권 REST API URL
    BASE_URL = "https://api.kiwoom.com"  # 실전투자
    MOCK_BASE_URL = "https://mockapi.kiwoom.com"  # 모의투자

    # API 엔드포인트 매핑
    ENDPOINTS = {
        "auth_token": "/oauth2/token",
        "auth_revoke": "/oauth2/revoke",
        "hashkey": "/uapi/hashkey",
        "stock_info": "/api/dostk/stkinfo",
        "market_condition": "/api/dostk/mrkcond",
        "mrkcond": "/api/dostk/mrkcond",
        "chart": "/api/dostk/chart",
        "foreign_institution": "/api/dostk/frgnistt",
        "ranking": "/api/dostk/rkinfo",
        "account": "/api/dostk/acnt",
        "order": "/api/dostk/ordr",
        "sector": "/api/dostk/sector",
    }

    def __init__(
        self,
        account_no: str = None,
        appkey: str = None,
        appsecret: str = None,
        env_path: str = None,
        use_mock: bool = False,
        rate_limit: int = 20,
        max_retries: int = 3,
        enable_rate_optimizer: bool = False,
        credentials_list: list = None,
    ):
        """
        초기화

        Args:
            account_no: 계좌번호
            appkey: 앱키
            appsecret: 앱시크릿
            env_path: .env 파일 경로
            use_mock: 모의투자 API 사용 여부
            rate_limit: 초당 최대 요청 수
            max_retries: 최대 재시도 횟수
            enable_rate_optimizer: Rate limiting 최적화 활성화
            credentials_list: 다중 크레덴셜 리스트
        """

        # API Facade 인스턴스 가져오기 (싱글턴)
        self.facade = KiwoomAPIFacade.get_instance(
            account_no=account_no,
            appkey=appkey,
            appsecret=appsecret,
            env_path=env_path,
            use_mock=use_mock,
            max_requests_per_second=rate_limit,
        )

        # 설정 저장
        self.use_mock = use_mock
        self.max_retries = max_retries

        # 기본 URL 설정
        self.base_url = self.MOCK_BASE_URL if use_mock else self.BASE_URL

        # 인증 관련
        self.access_token = None
        self.token_expires = None

        # 계좌 정보
        self.account_no = account_no or self._load_from_env("ACCOUNT_NO")
        self.appkey = appkey or self._load_from_env("KIWOOM_APPKEY")
        self.appsecret = appsecret or self._load_from_env("KIWOOM_APPSECRET")

        if not all([self.account_no, self.appkey, self.appsecret]):
            raise ValueError("계좌번호, APPKEY, SECRETKEY가 필요합니다. .env 파일을 확인하세요.")

    def _load_from_env(self, key: str) -> Optional[str]:
        """환경변수에서 값 로드"""
        return os.getenv(key)

    def _get_access_token(self) -> str:
        """OAuth2 액세스 토큰 발급/갱신"""
        if (
            self.access_token
            and self.token_expires
            and datetime.now() < self.token_expires - timedelta(minutes=5)
        ):
            return self.access_token

        # 토큰 발급 요청
        token_data = {
            "grant_type": "client_credentials",
            "appkey": self.appkey,
            "appsecret": self.appsecret,
        }

        response = self.facade.make_request(
            method="POST",
            endpoint=self.ENDPOINTS["auth_token"],
            data=token_data,
            priority=RequestPriority.HIGH,
        )

        if "access_token" not in response:
            raise KiwoomAPIError("토큰 발급 실패", response.get("error", "unknown"))

        self.access_token = response["access_token"]
        expires_in = response.get("expires_in", 86400)
        self.token_expires = datetime.now() + timedelta(seconds=expires_in)

        return self.access_token

    def _get_hashkey(self, data: Dict[str, Any]) -> str:
        """POST 요청용 해시키 생성"""
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "appkey": self.appkey,
            "appsecret": self.appsecret,
            "Content-Type": "application/json;charset=UTF-8",
        }

        response = self.facade.make_request(
            method="POST",
            endpoint=self.ENDPOINTS["hashkey"],
            headers=headers,
            data=data,
            priority=RequestPriority.NORMAL,
        )

        if "HASH" not in response:
            raise KiwoomAPIError("해시키 생성 실패")

        return response["HASH"]

    def make_tr_request(
        self,
        tr_code: str,
        endpoint: str,
        data: Dict[str, Any] = None,
        method: str = "GET",
        priority: RequestPriority = RequestPriority.NORMAL,
    ) -> Dict[str, Any]:
        """TR 요청 통합 메서드 (Facade 사용)"""

        # 인증 헤더 구성
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "appkey": self.appkey,
            "appsecret": self.appsecret,
            "api-id": tr_code,
            "Content-Type": "application/json;charset=UTF-8",
        }

        # POST 요청시 해시키 추가
        if method.upper() == "POST" and data:
            headers["hashkey"] = self._get_hashkey(data)

        # endpoint URL 구성
        if endpoint.startswith("/"):
            endpoint_url = endpoint
        else:
            endpoint_url = self.ENDPOINTS.get(endpoint, f"/api/dostk/{endpoint}")

        try:
            # Facade를 통한 API 호출
            response = self.facade.make_request(
                method=method,
                endpoint=endpoint_url,
                headers=headers,
                data=data,
                priority=priority,
            )

            return response

        except Exception as e:
            # 429 Rate Limiting 에러는 조용히 처리
            if "429" in str(e) or "rate" in str(e).lower():
                raise e
            else:
                self.raise_with_trace(e, f"TR 요청 실패: {tr_code}")

    def make_tr_request_continuous(
        self,
        tr_code: str,
        endpoint: str,
        data: Dict[str, Any] = None,
        cont_yn: str = "N",
        next_key: str = "",
        method: str = "GET",
        priority: RequestPriority = RequestPriority.NORMAL,
    ) -> Dict[str, Any]:
        """연속조회 TR 요청 (Facade 사용)"""

        # 인증 헤더 구성
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "appkey": self.appkey,
            "appsecret": self.appsecret,
            "Content-Type": "application/json;charset=UTF-8",
            "api-id": tr_code,
            "cont-yn": cont_yn,
            "next-key": next_key,
        }

        # POST 요청시 해시키 추가
        if method.upper() == "POST" and data:
            headers["hashkey"] = self._get_hashkey(data)

        # endpoint URL 구성
        if endpoint.startswith("/"):
            endpoint_url = endpoint
        else:
            endpoint_url = self.ENDPOINTS.get(endpoint, f"/api/dostk/{endpoint}")

        try:
            # Facade를 통한 API 호출
            response_data = self.facade.make_request(
                method=method,
                endpoint=endpoint_url,
                headers=headers,
                data=data,
                priority=priority,
            )

            # 연속조회 정보는 실제 HTTP 응답 헤더에서 가져와야 하지만
            # 현재 Facade에서는 JSON 데이터만 반환하므로 기본값 사용
            return {
                "data": response_data,
                "cont_yn": "N",  # 기본값
                "next_key": "",  # 기본값
            }

        except Exception as e:
            # 429 Rate Limiting 에러는 조용히 처리
            if "429" in str(e) or "rate" in str(e).lower():
                raise e
            else:
                self.raise_with_trace(e, "연속조회 요청 실패")

    def health_check(self) -> Dict[str, Any]:
        """API 연결 상태 확인"""
        try:
            # Facade 헬스체크 사용
            facade_health = self.facade.health_check()

            return {
                "status": "healthy",
                "facade_status": facade_health["status"],
                "authentication": "valid" if self.access_token else "required",
                "base_url": self.base_url,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def get_stats(self) -> Dict[str, Any]:
        """통계 정보 반환 (Facade 통계 포함)"""
        facade_stats = self.facade.get_comprehensive_stats()

        return {
            "unified_kiwoom_base": {
                "use_mock": self.use_mock,
                "base_url": self.base_url,
                "has_token": bool(self.access_token),
                "token_expires": (self.token_expires.isoformat() if self.token_expires else None),
            },
            "facade_stats": facade_stats,
        }

    def close(self):
        """리소스 정리"""
        # 토큰 무효화 (선택사항)
        if self.access_token:
            with contextlib.suppress(Exception):
                self.facade.make_request(
                    method="POST",
                    endpoint=self.ENDPOINTS["auth_revoke"],
                    data={"token": self.access_token},
                    priority=RequestPriority.LOW,
                )

        # Facade는 싱글턴이므로 직접 정리하지 않음
        self.access_token = None
        self.token_expires = None
