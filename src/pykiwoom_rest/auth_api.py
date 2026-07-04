"""
OAuth2 Authentication API
키움증권 OAuth2 인증 관련 API 클래스
작성일: 2025-10-21
목적: OAuth 토큰 발급/폐기 기능 제공
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from .kiwoom_base import KiwoomAPIBase, KiwoomAPIError


class AuthAPI(KiwoomAPIBase):
    """
    OAuth2 인증 API

    au10001: 토큰 발급 (get_access_token)
    au10002: 토큰 폐기 (revoke_token)
    """

    # TR 코드 매핑
    TR_CODES = {
        "token_issuance": "au10001",  # 접근토큰발급
        "token_revocation": "au10002",  # 접근토큰폐기
    }

    def __init__(self, **kwargs):
        """
        AuthAPI 초기화

        Args:
            **kwargs: KiwoomAPIBase 초기화 인자
        """
        super().__init__(**kwargs)

        # 토큰 캐시 메타데이터
        self._token_cache = {}
        self._token_lock = None

    def get_access_token(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        OAuth2 액세스 토큰 발급 (au10001)

        기존 _get_access_token의 공개 래퍼 메서드
        캐싱 및 자동 갱신 기능 제공

        Args:
            force_refresh: 강제 갱신 여부 (기본값: False)

        Returns:
            토큰 정보 딕셔너리
            {
                'token': 'access_token_string',
                'token_type': 'Bearer',
                'expires_in': 86400,  # 초 단위
                'scope': 'openapi',
                'issued_at': '2025-01-01T12:00:00',
                'expires_at': '2025-01-02T12:00:00'
            }

        Raises:
            KiwoomAPIError: 토큰 발급 실패 시

        Examples:
            >>> auth = AuthAPI()
            >>> token_info = auth.get_access_token()
            >>> print(token_info['token'])
            'eyJ0eXAiOiJKV1QiLCJhbGc...'
        """
        try:
            # 기존 _get_access_token 메서드 호출
            token = self._get_access_token(force_refresh=force_refresh)

            if not token:
                raise KiwoomAPIError(
                    "토큰 발급 실패: 토큰 값이 없음",
                    error_code="NULL_TOKEN",
                    error_msg="Access token is null",
                )

            # 토큰 메타데이터 구성
            now = datetime.now()
            expires_at = self.token_expires or (now + timedelta(hours=24))

            token_info = {
                "tr_code": self.TR_CODES["token_issuance"],
                "token": token,
                "token_type": "Bearer",
                "expires_in": 86400,  # 24시간 (초 단위)
                "issued_at": now.isoformat(),
                "expires_at": expires_at.isoformat(),
                "status": "valid",
            }

            # 캐시에 저장
            self._token_cache = token_info

            return token_info

        except KiwoomAPIError:
            raise
        except Exception as e:
            raise KiwoomAPIError(
                f"토큰 발급 중 오류: {str(e)}",
                error_code="TOKEN_ISSUE_ERROR",
                error_msg=str(e),
            )

    def revoke_token(self, token: Optional[str] = None) -> Dict[str, Any]:
        """
        OAuth2 액세스 토큰 폐기 (au10002)

        발급된 토큰을 폐기하고 로그아웃 처리
        기본값: 현재 활성 토큰 폐기

        Args:
            token: 폐기할 토큰 (기본값: 현재 활성 토큰)

        Returns:
            토큰 폐기 결과 딕셔너리
            {
                'tr_code': 'au10002',
                'status': 'revoked',
                'revoked_token': 'token_prefix...',
                'revoked_at': '2025-01-02T12:00:00',
                'message': 'Token successfully revoked'
            }

        Raises:
            KiwoomAPIError: 토큰 폐기 실패 시
            ValueError: 폐기할 토큰이 없을 때

        Examples:
            >>> auth = AuthAPI()
            >>> auth.get_access_token()
            >>> result = auth.revoke_token()
            >>> print(result['status'])
            'revoked'
        """
        try:
            # 폐기할 토큰 결정
            revoke_target = token or self.access_token

            if not revoke_target:
                raise ValueError(
                    "폐기할 토큰이 없습니다. "
                    "먼저 get_access_token()으로 토큰을 발급받거나 "
                    "token 매개변수를 지정하세요."
                )

            # 토큰 폐기 요청
            revoke_data = {"token": revoke_target, "token_type_hint": "access_token"}

            # 폐기 요청 전 현재 토큰 백업
            backup_token = self.access_token
            backup_expires = self.token_expires

            try:
                response = self.request(
                    method="POST",
                    endpoint="/oauth2/revoke",
                    json_data=revoke_data,
                    use_rate_limit=False,  # 인증 요청은 rate limit 제외
                )

                # 폐기 성공 여부 판정
                # 키움 API는 정상 폐기 시 HTTP 200 또는 204 반환
                success = response.get("rt_cd") == "0" or response.get("status") == "success"

                if success or response.get("error") is None:
                    # 토큰 초기화
                    if revoke_target == self.access_token:
                        self.access_token = None
                        self.token_expires = None

                    # 캐시 초기화
                    self._token_cache = {}

                    now = datetime.now()
                    revoke_result = {
                        "tr_code": self.TR_CODES["token_revocation"],
                        "status": "revoked",
                        "revoked_token": (
                            f"{revoke_target[:20]}..." if len(revoke_target) > 20 else revoke_target
                        ),
                        "revoked_at": now.isoformat(),
                        "message": "Token successfully revoked",
                        "raw_response": response,
                    }

                    return revoke_result
                else:
                    raise KiwoomAPIError(
                        f"토큰 폐기 실패: {response.get('msg1', 'Unknown error')}",
                        error_code=response.get("error_code", "REVOKE_ERROR"),
                        error_msg=response.get("error", "Token revocation failed"),
                    )

            except Exception:
                # 폐기 요청 실패 시 토큰 복구
                self.access_token = backup_token
                self.token_expires = backup_expires
                raise

        except ValueError:
            raise
        except KiwoomAPIError:
            raise
        except Exception as e:
            raise KiwoomAPIError(
                f"토큰 폐기 중 오류: {str(e)}",
                error_code="TOKEN_REVOKE_ERROR",
                error_msg=str(e),
            )

    def get_token_status(self) -> Dict[str, Any]:
        """
        현재 토큰 상태 조회

        현재 활성 토큰의 유효성 및 만료 시간 확인

        Returns:
            토큰 상태 정보 딕셔너리
            {
                'has_token': bool,
                'is_valid': bool,
                'token_prefix': str,
                'expires_at': str (ISO format),
                'time_to_expiry': int (초),
                'needs_refresh': bool
            }

        Examples:
            >>> auth = AuthAPI()
            >>> status = auth.get_token_status()
            >>> print(f"Token valid: {status['is_valid']}")
            'Token valid: True'
        """
        try:
            now = datetime.now()

            has_token = bool(self.access_token)
            is_valid = False
            time_to_expiry = 0
            needs_refresh = False

            if has_token and self.token_expires:
                is_valid = now < self.token_expires
                time_to_expiry = int((self.token_expires - now).total_seconds())
                # 5분 미만 남으면 갱신 필요
                needs_refresh = time_to_expiry < 300

            token_prefix = (
                f"{self.access_token[:20]}..."
                if self.access_token and len(self.access_token) > 20
                else self.access_token
            )

            return {
                "has_token": has_token,
                "is_valid": is_valid,
                "token_prefix": token_prefix or "None",
                "expires_at": (self.token_expires.isoformat() if self.token_expires else None),
                "time_to_expiry": time_to_expiry,
                "needs_refresh": needs_refresh,
            }

        except Exception as e:
            raise KiwoomAPIError(
                f"토큰 상태 조회 중 오류: {str(e)}",
                error_code="STATUS_CHECK_ERROR",
                error_msg=str(e),
            )

    def refresh_token(self) -> Dict[str, Any]:
        """
        토큰 갱신

        현재 토큰을 만료하고 새 토큰 발급

        Returns:
            새로 발급된 토큰 정보 (get_access_token과 동일한 형식)

        Examples:
            >>> auth = AuthAPI()
            >>> new_token = auth.refresh_token()
            >>> print("Token refreshed")
        """
        try:
            return self.get_access_token(force_refresh=True)
        except Exception as e:
            raise KiwoomAPIError(
                f"토큰 갱신 중 오류: {str(e)}",
                error_code="TOKEN_REFRESH_ERROR",
                error_msg=str(e),
            )

    def logout(self) -> Dict[str, Any]:
        """
        로그아웃 (토큰 폐기 + 세션 정리)

        현재 세션의 토큰을 폐기하고 모든 캐시 초기화

        Returns:
            로그아웃 결과 (revoke_token과 동일한 형식)

        Examples:
            >>> auth = AuthAPI()
            >>> auth.get_access_token()
            >>> result = auth.logout()
            >>> print(result['status'])
            'revoked'
        """
        try:
            # 토큰 폐기
            return self.revoke_token()

        except Exception as e:
            raise KiwoomAPIError(
                f"로그아웃 중 오류: {str(e)}",
                error_code="LOGOUT_ERROR",
                error_msg=str(e),
            )
        finally:
            # 폐기 요청 실패 시에도 로컬 세션 캐시는 남기지 않는다.
            self._token_cache = {}
