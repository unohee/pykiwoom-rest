from types import SimpleNamespace
from unittest.mock import patch

import pytest

from pykiwoom_rest.investor_api import InvestorAPI


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        ({"success": False, "data": {"x": 1}, "error": "failed", "metadata": {"id": 1}}, False),
        ({"status_code": 500, "data": {}, "msg1": "server error"}, False),
        ({"rt_cd": "1", "msg1": "denied"}, False),
        ({"rt_cd": "0", "payload": "ok"}, True),
        (SimpleNamespace(success=True, data={"x": 1}, error="ignored", metadata={"id": 1}), True),
        (SimpleNamespace(success=False, data={}, error="failed", metadata={"id": 1}), False),
        (object(), False),
    ],
)
def test_data_or_error_normalizes_every_supported_response_shape(response, expected):
    result = InvestorAPI._data_or_error(response)

    assert result["success"] is expected
    if response is not None and not isinstance(response, (dict, SimpleNamespace)):
        assert result["error"].startswith("Unexpected response type")


def test_invalid_consecutive_market_is_rejected_before_request():
    with patch.object(InvestorAPI, "_get_access_token", return_value="token"):
        api = InvestorAPI(appkey="test-key", appsecret="test-secret", account_no="12345678")

    with pytest.raises(ValueError, match="Invalid market: NASDAQ"):
        api.get_institutional_foreign_consecutive_trading("NASDAQ")
