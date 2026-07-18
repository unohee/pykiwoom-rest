"""Kiwoom base의 인증 및 TR 요청 계약을 외부 호출 없이 검증한다."""

from datetime import datetime, timedelta
import builtins
import types
from unittest.mock import MagicMock

import pytest

from pykiwoom_rest.base_api import APIError, RateLimitExceededError
from pykiwoom_rest.kiwoom_base import KiwoomAPIBase, KiwoomAPIError


def base(**kwargs):
    return KiwoomAPIBase(account_no="account", appkey="key", appsecret="secret", **kwargs)


def response(payload, headers=None):
    value = MagicMock()
    value.json.return_value = payload
    value.headers = headers or {}
    return value


class TestKiwoomBaseRequestExecution:
    def test_headers_response_and_token_expiry_parsing(self):
        api = base(normalize_data=True)
        api.access_token = "token"
        assert api._prepare_headers({"x-test": "yes"})["Authorization"] == "Bearer token"
        assert api._process_response(response({"return_code": 0}), tr_code="ka", endpoint="stock")["rt_cd"] == "0"
        bad = MagicMock()
        bad.json.side_effect = ValueError("bad")
        bad.text = "x" * 3000
        assert api._process_response(bad)["raw_response"].endswith("...[truncated]")

        assert api._calculate_token_expires({"expires_in": "60"}) > datetime.now()
        assert api._calculate_token_expires({"expires_at": "2099-01-01T00:00:00Z"}).year == 2099
        with pytest.raises(KiwoomAPIError, match="만료 정보"):
            api._calculate_token_expires({"expires_in": "invalid"})

    def test_token_issue_cache_and_error_contracts(self):
        api = base()
        api._make_request = MagicMock(return_value=response({"data": {"token": "fresh", "expires_in": 3600}}))
        assert api._get_access_token() == "fresh"
        assert api._get_access_token() == "fresh"
        assert api._make_request.call_count == 1

        api._issue_access_token = MagicMock(return_value={"token": "other", "expires_in": 3600})
        assert api._get_cached_credential_token("other-key", "other-secret") == "other"
        assert api._get_cached_credential_token("other-key", "other-secret") == "other"
        assert api._issue_access_token.call_count == 1

        failing_api = base()
        failing_api._make_request = MagicMock(return_value=response({"return_code": "E", "return_msg": "no"}))
        with pytest.raises(KiwoomAPIError, match="토큰 발급 실패"):
            failing_api._issue_access_token("key", "secret")
        with pytest.raises(KiwoomAPIError, match="토큰 발급 실패"):
            failing_api._get_access_token()

    def test_hashkey_and_tr_request_success_paths(self):
        api = base()
        api._get_access_token = MagicMock(return_value="token")
        api.request = MagicMock(return_value={"data": {"HASH": "hash"}})
        assert api._get_hashkey({"order": 1}) == "hash"
        api.request.return_value = {"return_code": "E"}
        with pytest.raises(KiwoomAPIError, match="HASH"):
            api._get_hashkey({})

        raw = response({"return_code": 0, "data": {"ok": True}}, {"cont-yn": "Y", "next-key": "next"})
        api._make_request = MagicMock(return_value=raw)
        result = api.make_tr_request("ka10001", "stock_info", data={"stk_cd": "005930"})
        assert result["header"] == {"cont-yn": "Y", "next-key": "next"}
        assert api.make_tr_request_continuous("ka", "stock_info", data={})["next_key"] == "next"
        with pytest.raises(ValueError, match="알 수 없는"):
            api.make_tr_request("ka", "missing")

    def test_rate_optimizer_token_failure_and_429_retry(self, monkeypatch):
        api = base(enable_rate_optimizer=True)
        api._get_access_token = MagicMock(return_value="token")
        api.rate_optimizer.get_optimal_credential = MagicMock(return_value=(0, {"APPKEY": "key"}))
        api.rate_optimizer.acquire_token = MagicMock(return_value=False)
        api.rate_optimizer.handle_429_error = MagicMock()
        with pytest.raises(RateLimitExceededError):
            api.make_tr_request("ka", "stock_info")

        api.rate_optimizer.acquire_token.return_value = True
        api._make_request = MagicMock(side_effect=[APIError("slow", status_code=429), response({"return_code": 0})])
        api.retry_strategy.calculate_retry_delay = MagicMock(return_value=0)
        monkeypatch.setattr("pykiwoom_rest.kiwoom_base.time.sleep", lambda _: None)
        assert api.make_tr_request("ka", "stock_info")["rt_cd"] == "0"
        assert api.rate_optimizer.handle_429_error.called

    def test_health_and_stock_code_outcomes(self):
        api = base()
        api.access_token = "token"
        api.make_tr_request = MagicMock(return_value={"rt_cd": "0", "msg1": "ok"})
        assert api.health_check()["status"] == "healthy"
        api.make_tr_request.return_value = {"rt_cd": "1", "msg1": "bad"}
        assert api.health_check()["status"] == "unhealthy"
        api.make_tr_request.side_effect = RuntimeError("down")
        assert api.health_check()["error"] == "Health check failed"
        assert api.convert_stock_code_param("005930") == {"stk_cd": "005930"}
        assert api.convert_stock_code_param("005930", legacy_format=True) == {"FID_INPUT_ISCD": "005930"}

    def test_manual_env_fallback_and_continuous_error_paths(self, tmp_path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text(
            "# comment\nexport TEST_BASE_KEY='quoted value'\nESCAPED=hello\\ world # tail\nINVALID\n",
            encoding="utf-8",
        )
        api = object.__new__(KiwoomAPIBase)
        monkeypatch.delenv("TEST_BASE_KEY", raising=False)
        monkeypatch.delenv("ESCAPED", raising=False)
        api._manual_load_env(str(env_file))
        assert __import__("os").environ["TEST_BASE_KEY"] == "quoted value"
        assert __import__("os").environ["ESCAPED"] == "hello world"

        real_import = builtins.__import__

        def no_dotenv(name, *args, **kwargs):
            if name == "dotenv":
                raise ImportError("missing")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", no_dotenv)
        api._load_env_file(str(env_file))

        request_api = base()
        request_api._get_access_token = MagicMock(return_value="token")
        request_api._make_request = MagicMock(return_value=response({"ok": True}, {"cont-yn": "Y"}))
        assert request_api.make_tr_request_continuous("ka", "stock_info", data={})["cont_yn"] == "Y"
        with pytest.raises(ValueError, match="알 수 없는"):
            request_api.make_tr_request_continuous("ka", "missing")
        request_api._make_request.side_effect = RuntimeError("network failure")
        with pytest.raises(RuntimeError, match="network failure"):
            request_api.make_tr_request_continuous("ka", "stock_info")

    def test_remaining_base_configuration_and_retry_contracts(self, monkeypatch):
        api = KiwoomAPIBase(
            account_no="account", appkey="key", appsecret="secret", use_mock=True,
            enable_rate_optimizer=True, credentials_list=[{"APPKEY": "key"}, {"APPKEY": "other", "APPSECRET": "other-secret"}],
        )
        assert api.base_url == api.MOCK_BASE_URL
        assert len(api.rate_optimizer.credentials_list) == 2
        api._get_cached_credential_token = MagicMock(return_value="other-token")
        api.rate_optimizer.get_optimal_credential = MagicMock(return_value=(1, {"APPKEY": "other", "APPSECRET": "other-secret"}))
        api.rate_optimizer.acquire_token = MagicMock(return_value=True)
        api._make_request = MagicMock(return_value=response({"return_code": 0}))
        assert api.make_tr_request("ka", "stock_info")["rt_cd"] == "0"
        api._get_cached_credential_token.assert_called_once()

        with pytest.raises(KiwoomAPIError, match="만료 정보"):
            api._calculate_token_expires({"expires_at": "not-a-date"})
        for name in ("ACC_NO", "ACCOUNT_NO", "APPKEY", "KIWOOM_APPKEY", "APPSECRET", "KIWOOM_SECRETKEY", "KIWOOM_APPSECRET"):
            monkeypatch.delenv(name, raising=False)
        with pytest.raises(ValueError, match="필수 인증"):
            KiwoomAPIBase(account_no=None, appkey=None, appsecret=None, env_path="/does-not-exist")

        api._make_request.side_effect = APIError("429", status_code=429)
        with pytest.raises(APIError):
            api.make_tr_request("ka", "stock_info", _retry_count=3)
        api._make_request.side_effect = RuntimeError("rate failure")
        with pytest.raises(RuntimeError, match="rate failure"):
            api.make_tr_request_continuous("ka", "stock_info")

    def test_remaining_env_and_token_payload_paths(self, tmp_path, monkeypatch):
        api = base()
        env_file = tmp_path / ".env"
        env_file.write_text('DOUBLE="line\\nnext"\nSINGLE=\'value\'\n', encoding="utf-8")
        monkeypatch.delenv("DOUBLE", raising=False)
        monkeypatch.delenv("SINGLE", raising=False)
        api._manual_load_env(str(env_file))
        assert __import__("os").environ["DOUBLE"] == "line\nnext"
        assert __import__("os").environ["SINGLE"] == "value"

        loaded = []
        dotenv = types.SimpleNamespace(load_dotenv=lambda path: loaded.append(path))
        monkeypatch.setitem(__import__("sys").modules, "dotenv", dotenv)
        api._load_env_file(str(env_file))
        assert loaded == [str(env_file)]

        monkeypatch.setenv("KIWOOM_APPKEY_2", "extra")
        monkeypatch.setenv("KIWOOM_APPSECRET_2", "extra-secret")
        api._setup_rate_optimizer()
        assert len(api.rate_optimizer.credentials_list) == 2
        api._make_request = MagicMock(return_value=response({"data": {"return_code": "E"}}))
        with pytest.raises(KiwoomAPIError):
            api._issue_access_token("key", "secret")

    def test_final_manual_env_and_request_exception_paths(self, tmp_path):
        api = base()
        env_file = tmp_path / ".env"
        env_file.write_text('UNCLOSED="value\nEMPTY=\n', encoding="utf-8")
        __import__("os").environ.pop("UNCLOSED", None)
        __import__("os").environ.pop("EMPTY", None)
        api._manual_load_env(str(env_file))
        assert __import__("os").environ["UNCLOSED"] == "value"
        api._manual_load_env(str(tmp_path / "missing"))

        api._make_request = MagicMock(return_value=response({"data": {"token": "ok", "expires_in": 1}}))
        assert api._issue_access_token("key", "secret")["token"] == "ok"
        api._get_access_token = MagicMock(return_value="token")
        api._make_request = MagicMock(side_effect=APIError("server", status_code=500))
        with pytest.raises(APIError, match="server"):
            api.make_tr_request("ka", "stock_info")
