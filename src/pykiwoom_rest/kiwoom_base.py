"""
Kiwoom Securities REST API Base Client
키움증권 REST API 특화 기능 제공
작성일: 2025-01-27
"""

import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List

from .base_api import APIError, BaseAPIClient, RateLimitExceededError
from .exception_utils import RaiseWithTraceMixin, rethrow_with_trace
from .rate_limit_optimizer import RateLimitOptimizer, SmartRetryStrategy
from .response_utils import normalize_data_values, normalize_response


class KiwoomAPIError(APIError):
    """키움증권 API 전용 예외 클래스"""

    def __init__(self, message: str, error_code: str = None, error_msg: str = None):
        super().__init__(message)
        self.error_code = error_code
        self.error_msg = error_msg


class KiwoomAPIBase(BaseAPIClient, RaiseWithTraceMixin):
    """
    키움증권 REST API 기본 클래스
    OAuth 인증, 해시키 생성, TR 코드 매핑 등 키움 특화 기능 제공
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
        "mrkcond": "/api/dostk/mrkcond",  # 종목시간별프로그램매매추이 등
        "chart": "/api/dostk/chart",
        "foreign_institution": "/api/dostk/frgnistt",
        "ranking": "/api/dostk/rkinfo",
        "account": "/api/dostk/acnt",
        "order": "/api/dostk/ordr",
        "sector": "/api/dostk/sect",
        "etf": "/api/dostk/etf",
        "elw": "/api/dostk/elw",
        "short_sale": "/api/dostk/shsa",
        "securities_lending": "/api/dostk/slb",
        "theme": "/api/dostk/thme",
        "credit_order": "/api/dostk/crdordr",
        "websocket": "/api/dostk/websocket",
    }

    def __init__(
        self,
        account_no: str = None,
        appkey: str = None,
        appsecret: str = None,
        env_path: str = None,
        use_mock: bool = False,
        enable_rate_optimizer: bool = False,
        credentials_list: List[Dict[str, str]] = None,
        normalize_data: bool = False,
        **kwargs,
    ):
        """
        초기화

        Args:
            account_no: 계좌번호
            appkey: 앱키
            appsecret: 앱시크릿
            env_path: .env 파일 경로
            use_mock: 모의투자 API 사용 여부
            enable_rate_optimizer: 고급 rate limiting 최적화 활성화
            credentials_list: 크레덴셜 리스트 (다중 토큰 로테이션)
            normalize_data: 응답 숫자 문자열 정규화 여부
            **kwargs: BaseAPIClient 추가 인자
        """
        base_url = self.BASE_URL
        if use_mock:
            base_url = self.MOCK_BASE_URL

        self.normalize_data = bool(kwargs.pop("normalize_data", False))

        # 키움 API는 초당 20회 제한
        kwargs.setdefault("rate_limit", 20)

        # BaseAPIClient에 전달하지 않을 매개변수 제거
        filtered_kwargs = {
            k: v
            for k, v in kwargs.items()
            if k not in ["enable_rate_optimizer", "credentials_list"]
        }

        super().__init__(base_url=base_url, **filtered_kwargs)

        # 환경변수 로드
        self._load_env_file(env_path)

        # 인증 정보 설정
        self._setup_credentials(account_no, appkey, appsecret, credentials_list)

        # 토큰 상태 초기화
        self.access_token = None
        self.token_expires = None
        self._credential_token_cache = {}

        # Rate Limiting 최적화 설정
        self.enable_rate_optimizer = enable_rate_optimizer
        self.normalize_data = normalize_data
        self.rate_optimizer = None
        self.retry_strategy = SmartRetryStrategy()

        # API base 참조 (KiwoomRest에서 접근용)
        self.api_base = self

        if enable_rate_optimizer:
            self._setup_rate_optimizer(credentials_list)

    def _load_env_file(self, env_path: str = None) -> None:
        """환경 파일 로드"""
        if env_path is None:
            # 프로젝트 루트에서 .env 파일 찾기
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            env_path = os.path.join(project_root, ".env")

        if os.path.exists(env_path):
            try:
                import dotenv

                dotenv.load_dotenv(env_path)
            except ImportError:
                # dotenv 없으면 수동 파싱
                self._manual_load_env(env_path)

    def _manual_load_env(self, env_path: str) -> None:
        """dotenv 라이브러리 없이 수동으로 환경변수 로드"""
        def parse_value(raw_value: str) -> str:
            value = raw_value.strip()
            if not value:
                return ""

            if value[0] in ('"', "'"):
                quote = value[0]
                chars = []
                escaped = False
                for ch in value[1:]:
                    if escaped:
                        chars.append({"n": "\n", "r": "\r", "t": "\t"}.get(ch, ch))
                        escaped = False
                    elif ch == "\\" and quote == '"':
                        escaped = True
                    elif ch == quote:
                        return "".join(chars)
                    else:
                        chars.append(ch)
                return "".join(chars)

            chars = []
            escaped = False
            for ch in value:
                if escaped:
                    chars.append(ch)
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == "#" and (not chars or chars[-1].isspace()):
                    break
                else:
                    chars.append(ch)
            return "".join(chars).strip()

        try:
            with open(env_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("export "):
                        line = line[len("export ") :].lstrip()
                    if "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    key = key.strip()
                    if key and key not in os.environ:
                        os.environ[key] = parse_value(value)
        except (FileNotFoundError, PermissionError):
            # .env 파일 없음 - 환경변수에서 직접 로드 진행
            # 의도적으로 예외 무시 (선택적 기능)
            pass

    def _setup_credentials(
        self,
        account_no: str = None,
        appkey: str = None,
        appsecret: str = None,
        credentials_list: List[Dict[str, str]] = None,
    ) -> None:
        """
        인증 정보 설정

        우선순위:
        1. 직접 전달된 파라미터 (account_no, appkey, appsecret)
        2. credentials_list[0]
        3. 환경변수 (ACC_NO/ACCOUNT_NO, APPKEY/KIWOOM_APPKEY, APPSECRET/KIWOOM_SECRETKEY/KIWOOM_APPSECRET)

        Args:
            account_no: 계좌번호 (선택)
            appkey: 앱키 (선택)
            appsecret: 앱시크릿 (선택)

        Raises:
            ValueError: 필수 인증 정보가 없을 경우
        """
        primary_credentials = credentials_list[0] if credentials_list else {}
        self.account_no = (
            account_no
            or primary_credentials.get("ACCOUNT_NO")
            or primary_credentials.get("account_no")
            or os.getenv("ACC_NO")
            or os.getenv("ACCOUNT_NO")
        )
        self.appkey = (
            appkey
            or primary_credentials.get("APPKEY")
            or primary_credentials.get("appkey")
            or os.getenv("APPKEY")
            or os.getenv("KIWOOM_APPKEY")
        )
        self.appsecret = (
            appsecret
            or primary_credentials.get("APPSECRET")
            or primary_credentials.get("appsecret")
            or os.getenv("APPSECRET")
            or os.getenv("KIWOOM_SECRETKEY")
            or os.getenv("KIWOOM_APPSECRET")
        )

        if not all([self.account_no, self.appkey, self.appsecret]):
            missing = []
            if not self.account_no:
                missing.append("account_no (또는 환경변수 ACC_NO/ACCOUNT_NO)")
            if not self.appkey:
                missing.append("appkey (또는 환경변수 APPKEY/KIWOOM_APPKEY)")
            if not self.appsecret:
                missing.append(
                    "appsecret (또는 환경변수 APPSECRET/KIWOOM_SECRETKEY/KIWOOM_APPSECRET)"
                )

            raise ValueError(
                f"필수 인증 정보가 누락되었습니다: {', '.join(missing)}\n"
                "클래스 초기화 시 직접 전달하거나 환경변수/credentials_list로 설정하세요.\n"
                "예: KiwoomRest(account_no='...', appkey='...', appsecret='...')"
            )

    def _prepare_headers(self, headers: Dict[str, str] = None) -> Dict[str, str]:
        """키움 API 요청 헤더 준비"""
        base_headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json",
        }

        # 토큰이 있으면 Authorization 헤더 추가
        if self.access_token:
            base_headers["Authorization"] = f"Bearer {self.access_token}"

        # 커스텀 헤더 병합
        if headers:
            base_headers.update(headers)

        return base_headers

    @rethrow_with_trace()
    def _process_response(
        self,
        response,
        *,
        tr_code: str = None,
        endpoint: str = None,
        request_start_time: float = None,
    ) -> Dict[str, Any]:
        """키움 API 응답 처리 - 원시 JSON(dict) 반환"""
        start_time = request_start_time if request_start_time is not None else time.time()
        processing_time = time.time() - start_time

        try:
            data = response.json()
            # 응답 구조 일원화: 기본 키/메타데이터를 부여하고 원본은 보존
            normalized = normalize_response(
                data,
                tr_code=tr_code,
                endpoint=endpoint,
                processing_time=processing_time,
                normalize_data=self.normalize_data,
            )
            if self.normalize_data:
                return normalize_data_values(
                    normalized,
                    tr_code=tr_code,
                    endpoint=endpoint,
                )
            return normalized

        except ValueError:
            # JSON이 아닌 응답 - 에러로 처리 (원문은 민감정보/대용량 보존 방지를 위해 제한)
            raw_response = getattr(response, "text", "")
            if len(raw_response) > 2048:
                raw_response = raw_response[:2048] + "...[truncated]"
            return {
                "rt_cd": "1",
                "msg1": "INVALID_JSON",
                "error": "Invalid JSON response",
                "raw_response": raw_response,
            }

    def _setup_rate_optimizer(self, additional_credentials_list: List[Dict[str, str]] = None):
        """Rate Limiting 최적화 설정"""
        all_credentials = []

        # 기본 크레덴셜
        main_cred = {
            "APPKEY": self.appkey,
            "APPSECRET": self.appsecret,
            "ACCOUNT_NO": self.account_no,
        }
        all_credentials.append(main_cred)

        # 추가 크레덴셜
        if additional_credentials_list:
            all_credentials.extend(additional_credentials_list[1:])
        else:
            # 환경변수에서 추가 크레덴셜 검색
            for i in range(2, 5):  # 최대 4개까지 지원
                appkey = os.getenv(f"KIWOOM_APPKEY_{i}")
                appsecret = os.getenv(f"KIWOOM_APPSECRET_{i}")
                account = os.getenv(f"ACCOUNT_NO_{i}")

                if appkey and appsecret:
                    all_credentials.append(
                        {
                            "APPKEY": appkey,
                            "APPSECRET": appsecret,
                            "ACCOUNT_NO": account or self.account_no,
                        }
                    )

        # Rate Optimizer 초기화
        self.rate_optimizer = RateLimitOptimizer(
            credentials_list=all_credentials,
            base_rate_limit=20,
            burst_capacity=50,
            recovery_time=60,
            enable_rotation=len(all_credentials) > 1,
        )

        self.logger.info(f"Rate Optimizer 활성화: {len(all_credentials)}개 크레덴셜")

    @rethrow_with_trace()
    def _get_access_token(self, force_refresh: bool = False) -> str:
        """OAuth2 액세스 토큰 발급/갱신"""
        # 토큰이 유효하고 강제 갱신이 아니면 기존 토큰 사용
        if (
            not force_refresh
            and self.access_token
            and self.token_expires
            and datetime.now() < self.token_expires - timedelta(minutes=5)
        ):
            return self.access_token

        # 토큰 발급 요청
        token_data = {
            "grant_type": "client_credentials",
            "appkey": self.appkey,
            "secretkey": self.appsecret,  # 키움은 secretkey 사용
        }

        try:
            response = self._make_request(
                method="POST",
                endpoint="/oauth2/token",  # 키움증권 토큰 엔드포인트
                json_data=token_data,
                headers={"Content-Type": "application/json"},
                use_rate_limit=False,  # 인증 요청은 rate limit 제외
            ).json()

            token_payload = response.get("data") if isinstance(response.get("data"), dict) else response

            # 키움증권은 'token' 키 사용 (access_token 아님)
            if token_payload.get("token"):
                self.access_token = token_payload["token"]
                self.token_expires = self._calculate_token_expires(token_payload)
                return self.access_token
            else:
                raise KiwoomAPIError(
                    "토큰 발급 실패",
                    error_code=token_payload.get("return_code") or response.get("return_code"),
                    error_msg=token_payload.get("return_msg") or response.get("return_msg"),
                )

        except Exception:
            raise

    def _calculate_token_expires(self, token_payload: Dict[str, Any]) -> datetime:
        """OAuth 응답의 만료 정보를 기준으로 토큰 만료 시각 계산."""
        expires_in = token_payload.get("expires_in") or token_payload.get("expires")
        if expires_in is not None:
            try:
                return datetime.now() + timedelta(seconds=int(expires_in))
            except (TypeError, ValueError):
                self.logger.warning("토큰 만료 시간 파싱 실패: %s", expires_in)

        expires_at = token_payload.get("expires_at") or token_payload.get("expires_dt")
        if expires_at:
            try:
                return datetime.fromisoformat(str(expires_at).replace("Z", "+00:00")).replace(tzinfo=None)
            except ValueError:
                self.logger.warning("토큰 만료 시각 파싱 실패: %s", expires_at)

        raise KiwoomAPIError("토큰 만료 정보가 응답에 없습니다")

    def _get_cached_credential_token(self, appkey: str, appsecret: str, force_refresh: bool = False) -> str:
        """Rate optimizer 크레덴셜별 OAuth 토큰 캐시 조회/발급."""
        cache_key = (appkey, appsecret)
        cached = self._credential_token_cache.get(cache_key)
        if (
            not force_refresh
            and cached
            and datetime.now() < cached["expires_at"] - timedelta(minutes=5)
        ):
            return cached["token"]

        token_payload = self._issue_access_token(appkey, appsecret)
        token = token_payload["token"]
        self._credential_token_cache[cache_key] = {
            "token": token,
            "expires_at": self._calculate_token_expires(token_payload),
        }
        return token

    def _issue_access_token(self, appkey: str, appsecret: str) -> Dict[str, Any]:
        """요청 스코프용 OAuth2 액세스 토큰 발급 (공유 토큰 캐시 미변경)."""
        token_data = {
            "grant_type": "client_credentials",
            "appkey": appkey,
            "secretkey": appsecret,
        }

        response = self._make_request(
            method="POST",
            endpoint="/oauth2/token",
            json_data=token_data,
            headers={"Content-Type": "application/json"},
            use_rate_limit=False,
        ).json()
        token_payload = response.get("data") if isinstance(response.get("data"), dict) else response

        if token_payload.get("token"):
            return token_payload

        raise KiwoomAPIError(
            "토큰 발급 실패",
            error_code=token_payload.get("return_code") or response.get("return_code"),
            error_msg=token_payload.get("return_msg") or response.get("return_msg"),
        )

    @rethrow_with_trace()
    def _get_hashkey(self, data: Dict[str, Any]) -> str:
        """
        POST 요청용 해시키 생성
        키움 API의 일부 POST 요청에 필요
        """
        try:
            # 토큰 확보
            token = self._get_access_token()

            # 해시키 요청
            hash_response = self.request(
                method="POST",
                endpoint="/uapi/hashkey",
                json_data=data,
                headers={"Authorization": f"Bearer {token}"},
                use_rate_limit=False,
            )

            hash_payload = hash_response.get("data") if isinstance(hash_response.get("data"), dict) else hash_response
            hash_value = hash_payload.get("HASH") if isinstance(hash_payload, dict) else None
            if not hash_value:
                raise KiwoomAPIError(
                    "해시키 생성 실패: 응답에 HASH가 없습니다",
                    error_code=hash_payload.get("return_code") if isinstance(hash_payload, dict) else None,
                    error_msg=hash_payload.get("return_msg") if isinstance(hash_payload, dict) else None,
                )
            return hash_value

        except Exception as e:
            self.raise_with_trace(e, "해시키 생성 중 오류")

    @rethrow_with_trace()
    def make_tr_request(
        self,
        tr_code: str,
        endpoint: str,
        data: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
        method: str = "POST",
        cont_yn: str = "N",
        next_key: str = "",
        _retry_count: int = 0,
    ) -> Dict[str, Any]:
        """
        TR 코드를 사용한 API 요청

        Args:
            tr_code: 키움 TR 코드
            endpoint: API 엔드포인트 키
            data: POST 요청 데이터
            params: GET 요청 파라미터
            method: HTTP 메서드

        Returns:
            APIResponse 객체
        """
        max_429_retries = 3
        retry_count = 0

        while True:
            try:
                request_start_time = time.time()

                # Rate Optimizer가 활성화된 경우 토큰 획득 대기
                if self.enable_rate_optimizer and self.rate_optimizer:
                    # 최적 크레덴셜 선택 및 토큰 획득
                    cred_idx, credential = self.rate_optimizer.get_optimal_credential()

                    # 선택된 크레덴셜은 요청 스코프에서만 사용 (공유 필드 변경 금지)
                    if credential and credential.get("APPKEY") != self.appkey:
                        token = self._get_cached_credential_token(
                            credential["APPKEY"],
                            credential["APPSECRET"],
                        )
                    else:
                        token = self._get_access_token()

                    # Rate limiting 토큰 획득
                    if not self.rate_optimizer.acquire_token(cred_idx):
                        self.logger.warning("Rate limit 토큰 획득 실패")
                        raise RateLimitExceededError("Rate optimizer 토큰 획득 실패")
                else:
                    # 기본 rate limiting 사용
                    token = self._get_access_token()

                # 엔드포인트 URL 가져오기
                endpoint_url = self.ENDPOINTS.get(endpoint)
                if not endpoint_url:
                    raise ValueError(f"알 수 없는 엔드포인트: {endpoint}")

                # 헤더 준비
                headers = {
                    "authorization": f"Bearer {token}",
                    "Content-Type": "application/json;charset=UTF-8",
                    "api-id": tr_code,
                    "cont-yn": cont_yn,
                    "next-key": next_key,
                }

                # 해시키는 필요시에만 추가 (현재는 불필요)

                # API 요청 실행 (지능형 재시도 포함)
                try:
                    raw_response = self._make_request(
                        method=method,
                        endpoint=endpoint_url,
                        headers=headers,
                        params=params,
                        json_data=data if method.upper() == "POST" else None,
                        use_rate_limit=True,
                    )
                    response = self._process_response(
                        raw_response,
                        tr_code=tr_code,
                        endpoint=endpoint,
                        request_start_time=request_start_time,
                    )

                    # 성공 시 에러 카운트 리셋
                    if self.enable_rate_optimizer and self.rate_optimizer:
                        self.rate_optimizer.reset_error_count(cred_idx if "cred_idx" in locals() else 0)

                    # 헤더 정보 추가
                    if isinstance(response, dict):
                        response_headers = raw_response.headers
                        response["header"] = {
                            "cont-yn": response_headers.get("cont-yn", "N"),
                            "next-key": response_headers.get("next-key", ""),
                        }

                    return response

                except APIError as e:
                    # 429 에러 특별 처리
                    if e.status_code == 429 and self.enable_rate_optimizer and self.rate_optimizer:
                        self.rate_optimizer.handle_429_error(cred_idx if "cred_idx" in locals() else 0)

                        max_retries = 3
                        if _retry_count >= max_retries:
                            raise

                        # 지능형 재시도
                        retry_delay = self.retry_strategy.calculate_retry_delay(429, _retry_count + 1)
                        self.logger.warning(f"429 에러 - {retry_delay:.1f}초 후 재시도")
                        time.sleep(retry_delay)

                        # 다른 크레덴셜로 재시도
                        return self.make_tr_request(
                            tr_code,
                            endpoint,
                            data,
                            params,
                            method,
                            cont_yn,
                            next_key,
                            _retry_count + 1,
                        )
                    raise

            except Exception:
                raise

    def make_tr_request_continuous(
        self,
        tr_code: str,
        endpoint: str,
        data: Dict[str, Any] = None,
        cont_yn: str = "N",
        next_key: str = "",
        method: str = "POST",
    ) -> Dict[str, Any]:
        """
        연속조회를 지원하는 TR 요청

        Args:
            tr_code: 키움 TR 코드
            endpoint: API 엔드포인트 키
            data: POST 요청 데이터
            cont_yn: 연속조회 여부 ('Y' or 'N')
            next_key: 연속조회 키
            method: HTTP 메서드

        Returns:
            응답 딕셔너리 (data, cont_yn, next_key 포함)
        """
        try:
            # 토큰 확보
            token = self._get_access_token()

            # 엔드포인트 URL 가져오기
            endpoint_url = self.ENDPOINTS.get(endpoint)
            if not endpoint_url:
                raise ValueError(f"알 수 없는 엔드포인트: {endpoint}")

            # 헤더 준비 (연속조회 지원)
            headers = {
                "authorization": f"Bearer {token}",
                "Content-Type": "application/json;charset=UTF-8",
                "api-id": tr_code,
                "cont-yn": cont_yn,
                "next-key": next_key,
            }

            # API 요청 실행 (base_api의 request 직접 사용)
            response = self._make_request(
                method=method,
                endpoint=endpoint_url,
                headers=headers,
                json_data=data if method.upper() == "POST" else None,
                use_rate_limit=True,
            )

            # 응답 처리
            result = response.json() if hasattr(response, "json") else {}
            if self.normalize_data:
                result = normalize_data_values(
                    result,
                    tr_code=tr_code,
                    endpoint=endpoint,
                )

            # 연속조회 정보 추출
            response_headers = response.headers if hasattr(response, "headers") else {}

            return {
                "data": result,
                "cont_yn": response_headers.get("cont-yn", "N"),
                "next_key": response_headers.get("next-key", ""),
            }

        except Exception as e:
            # 429 Rate Limiting 에러는 조용히 처리
            if "429" in str(e) or "rate" in str(e).lower():
                raise  # 에러 메시지 출력 없이 예외만 재발생
            else:
                self.raise_with_trace(e, "연속조회 요청 실패")

    def health_check(self) -> Dict[str, Any]:
        """
        API 연결 상태 확인
        간단한 종목 조회로 API 상태 체크
        """
        try:
            # 삼성전자 기본 정보 조회로 연결 테스트
            test_params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": "005930"}

            result = self.make_tr_request(
                tr_code="ka10001",  # 주식기본정보요청
                endpoint="stock_info",
                data=test_params,
                method="POST",
            )

            if result and result.get("rt_cd") == "0":
                return {
                    "status": "healthy",
                    "connected": True,
                    "api_responsive": True,
                    "test_response": result.get("msg1", "Success"),
                    "token_valid": bool(self.access_token),
                    "stats": self.get_stats(),
                }
            else:
                return {
                    "status": "unhealthy",
                    "connected": False,
                    "api_responsive": False,
                    "error": result.get("msg1") if result else "No response",
                    "response_code": result.get("rt_cd") if result else None,
                }

        except Exception as e:
            self.logger.exception("Health check 실패")
            return {
                "status": "unhealthy",
                "connected": False,
                "error": "Health check failed",
            }

    def convert_stock_code_param(
        self, stock_code: str, legacy_format: bool = False
    ) -> Dict[str, str]:
        """종목코드 파라미터 변환 헬퍼"""
        if legacy_format:
            return {"FID_INPUT_ISCD": stock_code}
        else:
            return {"stk_cd": stock_code}

    # to_dataframe 폐기: 더 이상 지원하지 않음 (사용자 변환 권장)
