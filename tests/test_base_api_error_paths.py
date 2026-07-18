from unittest.mock import Mock, patch

import pytest
import requests

from pykiwoom_rest.base_api import APIError, BaseAPIClient, TokenBucketRateLimiter


class Client(BaseAPIClient):
    def _prepare_headers(self, headers=None):
        return dict(headers or {})

    def _process_response(self, response):
        return response


def test_rate_limiter_validates_every_numeric_input():
    with pytest.raises(ValueError, match="rate"):
        TokenBucketRateLimiter(rate=0)
    with pytest.raises(ValueError, match="per_seconds"):
        TokenBucketRateLimiter(per_seconds=0)
    limiter = TokenBucketRateLimiter()
    with pytest.raises(ValueError, match="tokens"):
        limiter.acquire(tokens=0)


def test_rate_limiter_timeout_and_reset(monkeypatch):
    limiter = TokenBucketRateLimiter(rate=1)
    limiter.tokens = 0
    limiter.last_update = 0
    clock = iter([0.0, 0.0, 2.0])
    monkeypatch.setattr("pykiwoom_rest.base_api.time.monotonic", lambda: next(clock))
    assert not limiter.acquire(timeout=1)

    reset_clock = iter([3.0])
    monkeypatch.setattr("pykiwoom_rest.base_api.time.monotonic", lambda: next(reset_clock))
    limiter.reset()
    assert limiter.tokens == limiter.max_tokens
    assert limiter.last_update == 3.0


def test_url_builder_rejects_invalid_and_foreign_absolute_urls():
    client = Client("https://api.example.test")
    for endpoint in (None, "", "   ", "https://evil.example.test/path"):
        with pytest.raises(ValueError):
            client._build_url(endpoint)
    assert client._build_url(" https://api.example.test/path ") == "https://api.example.test/path"
    assert client._build_url("path") == "https://api.example.test/path"


def test_retry_converts_client_errors_and_non_retryable_exceptions(monkeypatch):
    client = Client("https://api.example.test", max_retries=1)
    response = Mock(status_code=404)
    response.json.side_effect = ValueError("not json")
    response.text = "missing"
    error = requests.HTTPError("404 missing", response=response)
    with pytest.raises(APIError) as raised:
        client.with_retry(Mock(side_effect=error))
    assert raised.value.status_code == 404
    assert raised.value.response == {"text": "missing"}

    with pytest.raises(RuntimeError, match="unexpected"):
        client.with_retry(Mock(side_effect=RuntimeError("unexpected")))


@pytest.mark.parametrize("message", ["400 bad", "401 denied", "403 forbidden"])
def test_retry_extracts_client_status_from_error_message(message):
    client = Client("https://api.example.test", max_retries=1)
    with pytest.raises(APIError) as raised:
        client.with_retry(Mock(side_effect=requests.HTTPError(message)))
    assert raised.value.status_code in {400, 401, 403}


def test_retry_rejects_invalid_retry_count_and_reraises_server_error():
    client = Client("https://api.example.test", max_retries=0)
    with pytest.raises(APIError, match="max_retries"):
        client.with_retry(lambda: None)

    client.max_retries = 1
    with pytest.raises(requests.HTTPError, match="500"):
        client.with_retry(Mock(side_effect=requests.HTTPError("500 server")))


def test_request_no_retry_rate_limit_and_429_stats(monkeypatch):
    client = Client("https://api.example.test")
    monkeypatch.setattr(client.rate_limiter, "acquire", Mock(return_value=False))
    with pytest.raises(Exception, match="Rate limit"):
        client._make_request("GET", "/path")

    client.session.request = Mock(side_effect=requests.HTTPError("limited", response=Mock(status_code=429)))
    with pytest.raises(requests.HTTPError):
        client._make_request("GET", "/path", use_rate_limit=False)
    assert client.error_count == 1

    response = Mock()
    client._make_request = Mock(return_value=response)
    assert client.request("GET", "/path", use_retry=False) is response


def test_base_helpers_reset_context_and_abstract_defaults():
    client = Client("https://api.example.test")
    client.request_count = 3
    client.error_count = 1
    client.reset_stats()
    assert client.get_stats()["request_count"] == 0
    assert client.health_check()
    assert BaseAPIClient._prepare_headers(client) is None
    assert BaseAPIClient._process_response(client, object()) is None
    client.close = Mock()
    client.__exit__(None, None, None)
    client.close.assert_called_once()
