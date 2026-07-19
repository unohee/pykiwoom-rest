"""
AuthAPI 테스트
작성일: 2025-10-21
목적: OAuth 인증 API 기능 검증
"""

import contextlib
import os
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest


class TestAuthAPIBasic(unittest.TestCase):
    """AuthAPI 기본 기능 테스트"""

    def setUp(self):
        """테스트 환경 초기화"""
        self.test_appkey = "TEST_APPKEY"
        self.test_appsecret = "TEST_APPSECRET"
        self.test_account_no = "12345678"

    @patch.dict(os.environ, {
        "KIWOOM_APPKEY": "TEST_APPKEY",
        "KIWOOM_APPSECRET": "TEST_APPSECRET",
        "ACCOUNT_NO": "12345678"
    })
    @patch("pykiwoom_rest.auth_api.AuthAPI._make_request")
    def test_get_access_token_success(self, mock_request):
        """토큰 발급 성공 테스트"""
        from pykiwoom_rest.auth_api import AuthAPI

        # Mock 응답 설정
        mock_request.return_value = MagicMock(json=lambda: {
            "rt_cd": "0",
            "msg1": "success",
            "token": "test_access_token_12345",
            "token_type": "Bearer",
            "expires_in": 86400,
        })

        # AuthAPI 초기화
        auth = AuthAPI()

        # 토큰 발급
        result = auth.get_access_token()

        # 검증
        assert result["token"] == "test_access_token_12345"
        assert result["status"] == "valid"
        assert "issued_at" in result
        assert "expires_at" in result

    @patch.dict(os.environ, {
        "KIWOOM_APPKEY": "TEST_APPKEY",
        "KIWOOM_APPSECRET": "TEST_APPSECRET",
        "ACCOUNT_NO": "12345678"
    })
    def test_token_status_no_token(self):
        """토큰 없을 때 상태 조회 테스트"""
        from pykiwoom_rest.auth_api import AuthAPI

        auth = AuthAPI(use_mock=True)  # Mock 모드

        # 토큰 상태 조회
        status = auth.get_token_status()

        # 검증
        assert status["has_token"] is False
        assert status["is_valid"] is False
        assert status["token_prefix"] == "None"

    @patch.dict(os.environ, {
        "KIWOOM_APPKEY": "TEST_APPKEY",
        "KIWOOM_APPSECRET": "TEST_APPSECRET",
        "ACCOUNT_NO": "12345678"
    })
    def test_get_token_status_with_valid_token(self):
        """유효한 토큰으로 상태 조회 테스트"""
        from pykiwoom_rest.auth_api import AuthAPI

        auth = AuthAPI(use_mock=True)

        # 토큰 수동 설정
        auth.access_token = "test_token_12345"
        auth.token_expires = datetime.now() + timedelta(hours=10)

        # 상태 조회
        status = auth.get_token_status()

        # 검증
        assert status["has_token"] is True
        assert status["is_valid"] is True
        assert status["token_prefix"] == "REDACTED"
        assert status["time_to_expiry"] > 0
        assert status["needs_refresh"] is False

    @patch.dict(os.environ, {
        "KIWOOM_APPKEY": "TEST_APPKEY",
        "KIWOOM_APPSECRET": "TEST_APPSECRET",
        "ACCOUNT_NO": "12345678"
    })
    def test_revoke_token_without_token(self):
        """토큰 없이 폐기 시도 테스트 (에러)"""
        from pykiwoom_rest.auth_api import AuthAPI

        auth = AuthAPI(use_mock=True)

        # 폐기 시도 (토큰 없음)
        with pytest.raises(ValueError):
            auth.revoke_token()

    @patch.dict(os.environ, {
        "KIWOOM_APPKEY": "TEST_APPKEY",
        "KIWOOM_APPSECRET": "TEST_APPSECRET",
        "ACCOUNT_NO": "12345678"
    })
    @patch("pykiwoom_rest.auth_api.AuthAPI.request")
    def test_revoke_token_success(self, mock_request):
        """토큰 폐기 성공 테스트"""
        from pykiwoom_rest.auth_api import AuthAPI

        # Mock 응답
        mock_request.return_value = {
            "rt_cd": "0",
            "msg1": "success"
        }

        auth = AuthAPI(use_mock=True)

        # 토큰 수동 설정
        auth.access_token = "test_token_to_revoke"
        auth.token_expires = datetime.now() + timedelta(hours=10)

        # 폐기
        result = auth.revoke_token()

        # 검증
        assert result["status"] == "revoked"
        assert auth.access_token is None
        assert auth.token_expires is None
        acquired = auth._token_lock.acquire(blocking=False)
        assert acquired
        if acquired:
            auth._token_lock.release()

    @patch.dict(os.environ, {
        "KIWOOM_APPKEY": "TEST_APPKEY",
        "KIWOOM_APPSECRET": "TEST_APPSECRET",
        "ACCOUNT_NO": "12345678"
    })
    def test_logout(self):
        """로그아웃 테스트"""
        from pykiwoom_rest.auth_api import AuthAPI

        auth = AuthAPI(use_mock=True)

        # 토큰 설정
        auth.access_token = "test_token_logout"
        auth.token_expires = datetime.now() + timedelta(hours=10)
        auth._token_cache = {"token": "test_token_logout"}

        # 로그아웃 (revoke_token 호출될 예정)
        # Note: revoke_token이 request를 호출하므로 실제 구현에서는 Mock 필요
        with contextlib.suppress(Exception):
            auth.logout()

        # 캐시 초기화 검증
        assert auth._token_cache == {}

    @patch.dict(os.environ, {
        "KIWOOM_APPKEY": "TEST_APPKEY",
        "KIWOOM_APPSECRET": "TEST_APPSECRET",
        "ACCOUNT_NO": "12345678"
    })
    @patch("pykiwoom_rest.auth_api.AuthAPI.request")
    def test_logout_clears_cache_when_revoke_fails(self, mock_request):
        """폐기 요청 실패 시에도 로컬 캐시는 초기화"""
        from pykiwoom_rest.auth_api import AuthAPI
        from pykiwoom_rest.kiwoom_base import KiwoomAPIError

        mock_request.side_effect = RuntimeError("network unavailable")
        auth = AuthAPI(use_mock=True)
        auth.access_token = "test_token_logout"
        auth.token_expires = datetime.now() + timedelta(hours=10)
        auth._token_cache = {"token": "test_token_logout"}

        with pytest.raises(KiwoomAPIError):
            auth.logout()

        assert auth._token_cache == {}


class TestAuthAPIIntegration(unittest.TestCase):
    """AuthAPI 통합 테스트"""

    @patch.dict(os.environ, {
        "KIWOOM_APPKEY": "TEST_APPKEY",
        "KIWOOM_APPSECRET": "TEST_APPSECRET",
        "ACCOUNT_NO": "12345678"
    })
    def test_auth_api_import(self):
        """AuthAPI 임포트 테스트"""
        try:
            from pykiwoom_rest.auth_api import AuthAPI
            auth = AuthAPI(use_mock=True)
            assert auth is not None
            print("✓ AuthAPI import successful")
        except ImportError as e:
            pytest.fail(f"AuthAPI import failed: {e}")

    @patch.dict(os.environ, {
        "KIWOOM_APPKEY": "TEST_APPKEY",
        "KIWOOM_APPSECRET": "TEST_APPSECRET",
        "ACCOUNT_NO": "12345678"
    })
    def test_auth_api_tr_codes(self):
        """AuthAPI TR 코드 매핑 테스트"""
        from pykiwoom_rest.auth_api import AuthAPI

        auth = AuthAPI(use_mock=True)

        # TR 코드 검증
        assert auth.TR_CODES["token_issuance"] == "au10001"
        assert auth.TR_CODES["token_revocation"] == "au10002"

    @patch.dict(os.environ, {
        "KIWOOM_APPKEY": "TEST_APPKEY",
        "KIWOOM_APPSECRET": "TEST_APPSECRET",
        "ACCOUNT_NO": "12345678"
    })
    def test_auth_api_methods_exist(self):
        """AuthAPI 필수 메서드 존재 테스트"""
        from pykiwoom_rest.auth_api import AuthAPI

        auth = AuthAPI(use_mock=True)

        # 필수 메서드 확인
        assert hasattr(auth, "get_access_token")
        assert hasattr(auth, "revoke_token")
        assert hasattr(auth, "get_token_status")
        assert hasattr(auth, "refresh_token")
        assert hasattr(auth, "logout")

        # 메서드가 호출 가능한지 확인
        assert callable(auth.get_access_token)
        assert callable(auth.revoke_token)
        assert callable(auth.get_token_status)
        assert callable(auth.refresh_token)
        assert callable(auth.logout)


if __name__ == "__main__":
    unittest.main()
