from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from pykiwoom_rest.api_facade import KiwoomAPIFacade
from pykiwoom_rest.unified_kiwoom_base import KiwoomAPIError, UnifiedKiwoomAPIBase


@pytest.fixture(autouse=True)
def reset_singleton():
    KiwoomAPIFacade.reset_instance()
    UnifiedKiwoomAPIBase._facade_ref_counts.clear()
    yield
    KiwoomAPIFacade.reset_instance()
    UnifiedKiwoomAPIBase._facade_ref_counts.clear()


@pytest.fixture
def base():
    return UnifiedKiwoomAPIBase(account_no="12345678", appkey="key", appsecret="secret")


def test_rejects_remaining_unsupported_configuration_and_missing_token(base):
    with pytest.raises(ValueError, match="credentials_list"):
        UnifiedKiwoomAPIBase(account_no="a", appkey="k", appsecret="s", credentials_list=[{}])
    base.facade.make_request = Mock(return_value={"error": "denied"})
    with pytest.raises(KiwoomAPIError, match="토큰 발급 실패"):
        base._get_access_token()


def test_loads_explicit_env_file_without_overriding_direct_credentials(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("ACCOUNT_NO=ignored\n")
    base = UnifiedKiwoomAPIBase(
        account_no="12345678", appkey="key", appsecret="secret", env_path=str(env_file)
    )
    assert base.account_no == "12345678"


def test_tr_request_closed_rate_error_and_wrapped_error(base, monkeypatch):
    base._closed = True
    with pytest.raises(KiwoomAPIError, match="종료"):
        base.make_tr_request("ka", "stock_info")
    base._closed = False
    monkeypatch.setattr(base, "_get_access_token", Mock(side_effect=RuntimeError("rate limited")))
    with pytest.raises(RuntimeError, match="rate"):
        base.make_tr_request("ka", "stock_info")

    monkeypatch.setattr(base, "_get_access_token", Mock(side_effect=RuntimeError("broken")))
    with pytest.raises(RuntimeError, match="broken"):
        base.make_tr_request("ka", "stock_info")

    monkeypatch.setattr(base, "_get_access_token", Mock(return_value="token"))
    base.facade.make_request = Mock(return_value={"ok": True})
    assert base.make_tr_request("ka", "/direct") == {"ok": True}


def test_continuous_request_get_direct_endpoint_and_error_paths(base, monkeypatch):
    monkeypatch.setattr(base, "_get_access_token", Mock(return_value="token"))
    base.facade.make_request = Mock(return_value={"value": 1})
    result = base.make_tr_request_continuous("ka", "stock_info", method="GET")
    assert result == {"data": {"value": 1}, "cont_yn": "N", "next_key": ""}

    base._closed = True
    with pytest.raises(KiwoomAPIError, match="종료"):
        base.make_tr_request_continuous("ka", "stock_info")
    base._closed = False
    monkeypatch.setattr(base, "_get_access_token", Mock(side_effect=RuntimeError("rate limited")))
    with pytest.raises(RuntimeError, match="rate"):
        base.make_tr_request_continuous("ka", "stock_info")
    monkeypatch.setattr(base, "_get_access_token", Mock(side_effect=RuntimeError("broken")))
    with pytest.raises(RuntimeError, match="broken"):
        base.make_tr_request_continuous("ka", "stock_info")


def test_health_close_wait_revoke_and_rate_reset(base, monkeypatch):
    base.facade.health_check = Mock(side_effect=RuntimeError("unavailable"))
    assert base.health_check()["status"] == "unhealthy"
    base.facade.reset_rate_limiter = Mock()
    base.reset_rate_limiter()
    base.facade.reset_rate_limiter.assert_called_once()

    base.access_token = "token"
    base.token_expires = datetime.now() + timedelta(hours=1)
    base.facade.make_request = Mock(side_effect=RuntimeError("revoke failure"))
    base.close()
    assert base.access_token is None
    assert base.token_expires is None
    base.close()


def test_close_timeout_with_active_request(base, monkeypatch):
    base._active_requests = 1
    clock = iter([0.0, 1.0, 6.0])
    monkeypatch.setattr("pykiwoom_rest.unified_kiwoom_base.time.monotonic", lambda: next(clock))
    base.close()
    assert base._closed
