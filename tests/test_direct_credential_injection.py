"""
Direct Credential Injection Tests
직접 인증 정보 주입 기능 테스트

작성일: 2025-01-27
"""

import os
import pytest

from pykiwoom_rest import KiwoomRest
from pykiwoom_rest.kiwoom_base import KiwoomAPIBase


class TestDirectCredentialInjection:
    """직접 인증 정보 주입 기능 테스트"""

    @pytest.fixture(autouse=True)
    def clear_env_vars(self, monkeypatch):
        """각 테스트 전 환경변수 초기화"""
        # 모든 관련 환경변수 제거
        env_vars = [
            "ACC_NO", "ACCOUNT_NO",
            "APPKEY", "KIWOOM_APPKEY",
            "APPSECRET", "KIWOOM_SECRETKEY", "KIWOOM_APPSECRET"
        ]
        for var in env_vars:
            monkeypatch.delenv(var, raising=False)

    def test_direct_injection_all_params(self):
        """모든 파라미터를 직접 주입하는 경우"""
        kiwoom = KiwoomRest(
            account_no="test-account",
            appkey="test-key",
            appsecret="test-secret"
        )

        assert kiwoom.stock_api.account_no == "test-account"
        assert kiwoom.stock_api.appkey == "test-key"
        assert kiwoom.stock_api.appsecret == "test-secret"

    def test_env_vars_fallback(self, monkeypatch):
        """환경변수 폴백이 작동하는지 테스트"""
        # 환경변수 설정
        monkeypatch.setenv("ACCOUNT_NO", "env-account")
        monkeypatch.setenv("KIWOOM_APPKEY", "env-key")
        monkeypatch.setenv("KIWOOM_APPSECRET", "env-secret")

        kiwoom = KiwoomRest()

        assert kiwoom.stock_api.account_no == "env-account"
        assert kiwoom.stock_api.appkey == "env-key"
        assert kiwoom.stock_api.appsecret == "env-secret"

    def test_direct_injection_overrides_env(self, monkeypatch):
        """직접 주입이 환경변수보다 우선하는지 테스트"""
        # 환경변수 설정
        monkeypatch.setenv("ACCOUNT_NO", "env-account")
        monkeypatch.setenv("KIWOOM_APPKEY", "env-key")
        monkeypatch.setenv("KIWOOM_APPSECRET", "env-secret")

        # 직접 주입 (환경변수 덮어쓰기)
        kiwoom = KiwoomRest(
            account_no="direct-account",
            appkey="direct-key",
            appsecret="direct-secret"
        )

        assert kiwoom.stock_api.account_no == "direct-account"
        assert kiwoom.stock_api.appkey == "direct-key"
        assert kiwoom.stock_api.appsecret == "direct-secret"

    def test_partial_injection(self, monkeypatch):
        """일부만 직접 주입하고 나머지는 환경변수 사용"""
        # 계좌번호만 환경변수에 설정
        monkeypatch.setenv("ACCOUNT_NO", "env-account")

        kiwoom = KiwoomRest(
            appkey="direct-key",
            appsecret="direct-secret"
        )

        assert kiwoom.stock_api.account_no == "env-account"
        assert kiwoom.stock_api.appkey == "direct-key"
        assert kiwoom.stock_api.appsecret == "direct-secret"

    def test_missing_credentials_raises_error(self):
        """필수 인증 정보 누락 시 에러 발생"""
        with pytest.raises(ValueError) as exc_info:
            KiwoomRest(
                appkey="test-key"
                # account_no, appsecret 누락
            )

        error_message = str(exc_info.value)
        assert "필수 인증 정보가 누락되었습니다" in error_message
        assert "account_no" in error_message
        assert "appsecret" in error_message

    def test_alternative_env_var_names(self, monkeypatch):
        """대체 환경변수 이름 지원 테스트"""
        # 다양한 이름으로 환경변수 설정
        monkeypatch.setenv("ACC_NO", "alt-account")
        monkeypatch.setenv("APPKEY", "alt-key")
        monkeypatch.setenv("KIWOOM_SECRETKEY", "alt-secret")

        kiwoom = KiwoomRest()

        assert kiwoom.stock_api.account_no == "alt-account"
        assert kiwoom.stock_api.appkey == "alt-key"
        assert kiwoom.stock_api.appsecret == "alt-secret"

    def test_priority_of_env_vars(self, monkeypatch):
        """여러 환경변수가 있을 때 우선순위 테스트"""
        # 두 가지 이름으로 다른 값 설정
        monkeypatch.setenv("ACC_NO", "acc-no-value")
        monkeypatch.setenv("ACCOUNT_NO", "account-no-value")
        monkeypatch.setenv("APPKEY", "appkey-value")
        monkeypatch.setenv("KIWOOM_APPKEY", "kiwoom-appkey-value")
        monkeypatch.setenv("APPSECRET", "appsecret-value")
        monkeypatch.setenv("KIWOOM_APPSECRET", "kiwoom-appsecret-value")

        kiwoom = KiwoomRest()

        # ACC_NO가 ACCOUNT_NO보다 우선
        assert kiwoom.stock_api.account_no == "acc-no-value"
        # APPKEY가 KIWOOM_APPKEY보다 우선
        assert kiwoom.stock_api.appkey == "appkey-value"
        # APPSECRET이 KIWOOM_APPSECRET보다 우선
        assert kiwoom.stock_api.appsecret == "appsecret-value"

    def test_base_api_class_direct_injection(self):
        """KiwoomAPIBase 클래스 직접 사용 시에도 동작하는지 테스트"""
        base_api = KiwoomAPIBase(
            account_no="base-account",
            appkey="base-key",
            appsecret="base-secret"
        )

        assert base_api.account_no == "base-account"
        assert base_api.appkey == "base-key"
        assert base_api.appsecret == "base-secret"

    def test_empty_string_values_not_accepted(self):
        """빈 문자열은 유효하지 않은 값으로 처리"""
        with pytest.raises(ValueError):
            KiwoomRest(
                account_no="",
                appkey="test-key",
                appsecret="test-secret"
            )

    def test_none_values_fallback_to_env(self, monkeypatch):
        """None 값은 환경변수로 폴백"""
        monkeypatch.setenv("ACCOUNT_NO", "env-account")
        monkeypatch.setenv("KIWOOM_APPKEY", "env-key")
        monkeypatch.setenv("KIWOOM_APPSECRET", "env-secret")

        kiwoom = KiwoomRest(
            account_no=None,
            appkey=None,
            appsecret=None
        )

        assert kiwoom.stock_api.account_no == "env-account"
        assert kiwoom.stock_api.appkey == "env-key"
        assert kiwoom.stock_api.appsecret == "env-secret"
