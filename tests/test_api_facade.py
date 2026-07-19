import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import requests

from pykiwoom_rest.api_facade import (
    APIRequest,
    GlobalRateLimiter,
    KiwoomAPIFacade,
    RequestPriority,
    _FacadeBaseClient,
)


@pytest.fixture(autouse=True)
def reset_facade():
    KiwoomAPIFacade.reset_instance()
    yield
    KiwoomAPIFacade.reset_instance()


def response(status_code=200, payload=None, text=None):
    payload = {} if payload is None else payload
    return SimpleNamespace(
        status_code=status_code,
        text=json.dumps(payload) if text is None else text,
        json=Mock(return_value=payload),
    )


def test_request_and_limiter_basics(monkeypatch):
    now = iter((100.0,) * 10 + (101.1,))
    monkeypatch.setattr("pykiwoom_rest.api_facade.time.time", lambda: next(now))
    request = APIRequest("GET", "/prices", {}, priority=RequestPriority.HIGH)
    assert request.created_at == 100.0
    limiter = GlobalRateLimiter(1)
    assert limiter.can_make_request()
    assert limiter.wait_for_slot(timeout=1)
    limiter.record_request()
    assert not limiter.can_make_request()
    assert limiter.get_stats()["total_requests"] == 1
    limiter.record_block()
    limiter.reset()
    assert limiter.get_stats()["blocked_requests"] == 0


def test_facade_base_client_and_full_limiter_wait_path(monkeypatch):
    client = _FacadeBaseClient(base_url="https://example.test")
    assert client._prepare_headers({"X-Test": "yes"}) == {"X-Test": "yes"}
    assert client._prepare_headers() == {}
    marker = object()
    assert client._process_response(marker) is marker

    limiter = GlobalRateLimiter(1)
    limiter.request_times = [0.0]
    clock = iter([0.0, 0.0, 0.0, 0.0, 2.0])
    monkeypatch.setattr("pykiwoom_rest.api_facade.time.time", lambda: next(clock))
    monkeypatch.setattr("pykiwoom_rest.api_facade.time.sleep", lambda _: None)
    assert not limiter.wait_for_slot(timeout=1)

    empty_limiter = GlobalRateLimiter(0)
    empty_clock = iter([0.0, 0.0, 0.0, 2.0])
    monkeypatch.setattr("pykiwoom_rest.api_facade.time.time", lambda: next(empty_clock))
    assert not empty_limiter.wait_for_slot(timeout=1)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_requests_per_second": 0},
        {"max_requests_per_second": True},
        {"request_timeout": 0},
        {"request_timeout": False},
    ],
)
def test_facade_rejects_invalid_configuration(kwargs):
    with pytest.raises(ValueError):
        KiwoomAPIFacade(**kwargs)


def test_facade_singleton_requires_matching_configuration():
    facade = KiwoomAPIFacade(appkey="key", appsecret="secret", account_no="account")
    assert KiwoomAPIFacade(appkey="key", appsecret="secret", account_no="account") is facade
    assert KiwoomAPIFacade.get_instance(appkey="key", appsecret="secret", account_no="account") is facade
    with pytest.raises(ValueError, match="different configuration"):
        KiwoomAPIFacade(appkey="other", appsecret="secret", account_no="account")


def test_get_instance_reset_rate_limiter_and_retry_helpers():
    facade = KiwoomAPIFacade.get_instance()
    facade.global_rate_limiter.record_request()
    facade.reset_rate_limiter()
    assert facade.global_rate_limiter.get_stats()["total_requests"] == 0
    assert KiwoomAPIFacade._is_retryable_request("delete")
    assert not KiwoomAPIFacade._is_retryable_request("post")
    assert KiwoomAPIFacade._is_retryable_status(503)
    assert not KiwoomAPIFacade._is_retryable_status(404)


def test_make_request_success_records_stats_and_history():
    facade = KiwoomAPIFacade(request_timeout=1)
    facade.base_api._make_request = Mock(return_value=response(payload={"price": 70000}))

    result = facade.make_request("GET", "/api/price", data={"code": "005930"})

    assert result == {"price": 70000}
    facade.base_api._make_request.assert_called_once_with(
        method="GET",
        endpoint="/api/price",
        headers=None,
        json_data={"code": "005930"},
        use_rate_limit=False,
    )
    stats = facade.get_comprehensive_stats()
    assert stats["facade_stats"]["successful_requests"] == 1
    assert stats["recent_requests"] == 1
    assert facade.get_recent_requests()[0]["success"]


def test_make_request_parses_non_json_response_and_health_check():
    facade = KiwoomAPIFacade()
    raw_response = response(text="not json")
    raw_response.json = Mock(side_effect=json.JSONDecodeError("bad json", "not json", 0))
    facade.base_api._make_request = Mock(return_value=raw_response)

    assert facade.make_request("GET", "/api/text", use_rate_limit=False) == {"text": "not json"}
    assert facade.health_check()["status"] == "healthy"


def test_make_request_retries_idempotent_transient_failure(monkeypatch):
    facade = KiwoomAPIFacade()
    facade.base_api._make_request = Mock(
        side_effect=[requests.ConnectionError("offline"), response(payload={"ok": True})]
    )
    monkeypatch.setattr("pykiwoom_rest.api_facade.time.sleep", lambda _: None)

    assert facade.make_request("GET", "/api/retry", use_rate_limit=False) == {"ok": True}
    assert facade.base_api._make_request.call_count == 2
    assert facade.get_recent_requests()[0]["retries"] == 1


def test_make_request_retries_retryable_http_status(monkeypatch):
    facade = KiwoomAPIFacade()
    facade.base_api._make_request = Mock(side_effect=[response(status_code=503), response(payload={"ok": True})])
    monkeypatch.setattr("pykiwoom_rest.api_facade.time.sleep", lambda _: None)

    assert facade.make_request("GET", "/api/retry-status", use_rate_limit=False) == {"ok": True}
    assert facade.base_api._make_request.call_count == 2


def test_make_request_does_not_retry_post_and_records_failure():
    facade = KiwoomAPIFacade()
    failure = requests.ConnectionError("offline")
    facade.base_api._make_request = Mock(side_effect=failure)

    with pytest.raises(requests.ConnectionError):
        facade.make_request("POST", "/api/order", use_rate_limit=False)

    assert facade.base_api._make_request.call_count == 1
    assert facade.facade_stats["failed_requests"] == 1
    assert not facade.get_recent_requests()[0]["success"]


def test_rate_limit_timeout_records_block(monkeypatch):
    facade = KiwoomAPIFacade(request_timeout=0.1)
    monkeypatch.setattr(facade.global_rate_limiter, "wait_for_slot", lambda timeout: False)

    with pytest.raises(Exception, match="Rate limit timeout"):
        facade.make_request("GET", "/api/blocked")

    assert facade.facade_stats["rate_limited_requests"] == 1
    assert facade.global_rate_limiter.blocked_requests == 1


def test_history_is_limited_and_close_resets_singleton():
    facade = KiwoomAPIFacade()
    request = APIRequest("GET", "/api", {})
    for _ in range(1001):
        facade._record_request_history(request, 0.01, True)
    assert len(facade.request_history) == 1000
    facade.close()
    assert KiwoomAPIFacade._instance is None


def test_health_check_failure_and_context_manager_close_error(monkeypatch):
    facade = KiwoomAPIFacade()
    monkeypatch.setattr(facade, "get_comprehensive_stats", Mock(side_effect=RuntimeError("stats failed")))
    health = facade.health_check()
    assert health["status"] == "unhealthy"
    assert health["timestamp"]
    assert health["error"] == "stats failed"
    assert not health["facade_healthy"]

    facade.base_api.close = Mock(side_effect=RuntimeError("close failed"))
    with facade as entered:
        assert entered is facade
    assert KiwoomAPIFacade._instance is None
