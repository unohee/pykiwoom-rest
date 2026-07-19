from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from pykiwoom_rest.auth_api import AuthAPI, KiwoomAPIError


@pytest.fixture
def auth():
    with patch.object(AuthAPI, "_get_access_token", return_value="token"):
        return AuthAPI(appkey="test-key", appsecret="test-secret", account_no="12345678", use_mock=True)


def test_get_access_token_uses_cache_and_rejects_null_token(auth, monkeypatch):
    auth._token_cache = {"token": "token", "status": "valid"}
    monkeypatch.setattr(auth, "_get_access_token", Mock(return_value="token"))
    assert auth.get_access_token() is auth._token_cache

    monkeypatch.setattr(auth, "_get_access_token", Mock(return_value=None))
    with pytest.raises(KiwoomAPIError, match="토큰 발급 실패") as error:
        auth.get_access_token(force_refresh=True)
    assert error.value.error_code == "NULL_TOKEN"


def test_get_access_token_wraps_unexpected_error(auth, monkeypatch):
    monkeypatch.setattr(auth, "_get_access_token", Mock(side_effect=RuntimeError("network")))
    with pytest.raises(KiwoomAPIError, match="토큰 발급 중 오류") as error:
        auth.get_access_token()
    assert error.value.error_code == "TOKEN_ISSUE_ERROR"


@pytest.mark.parametrize(
    "response",
    [
        {"rt_cd": "1", "msg1": "denied", "error_code": "DENIED", "error": "nope"},
        "malformed response",
    ],
)
def test_revoke_token_rejects_unsuccessful_response(auth, response, monkeypatch):
    auth.access_token = "token"
    monkeypatch.setattr(auth, "request", Mock(return_value=response))
    with pytest.raises(KiwoomAPIError, match="토큰 폐기 실패"):
        auth.revoke_token()


def test_revoke_token_wraps_transport_error(auth, monkeypatch):
    auth.access_token = "token"
    monkeypatch.setattr(auth, "request", Mock(side_effect=RuntimeError("offline")))
    with pytest.raises(KiwoomAPIError, match="토큰 폐기 중 오류") as error:
        auth.revoke_token()
    assert error.value.error_code == "TOKEN_REVOKE_ERROR"


def test_token_status_error_and_refresh_error_are_wrapped(auth, monkeypatch):
    class BrokenExpiry:
        def isoformat(self):
            raise RuntimeError("broken expiry")

    auth.access_token = "token"
    auth.token_expires = BrokenExpiry()
    with pytest.raises(KiwoomAPIError, match="토큰 상태 조회 중 오류"):
        auth.get_token_status()

    monkeypatch.setattr(auth, "get_access_token", Mock(side_effect=RuntimeError("refresh failed")))
    with pytest.raises(KiwoomAPIError, match="토큰 갱신 중 오류") as error:
        auth.refresh_token()
    assert error.value.error_code == "TOKEN_REFRESH_ERROR"


def test_token_status_near_expiry_and_refresh_success(auth, monkeypatch):
    auth.access_token = "token"
    auth.token_expires = datetime.now() + timedelta(seconds=60)
    assert auth.get_token_status()["needs_refresh"]

    monkeypatch.setattr(auth, "get_access_token", Mock(return_value={"token": "new"}))
    assert auth.refresh_token() == {"token": "new"}
    auth.get_access_token.assert_called_once_with(force_refresh=True)
