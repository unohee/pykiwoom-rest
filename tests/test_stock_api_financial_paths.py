from unittest.mock import Mock, patch

import pytest

from pykiwoom_rest.stock_api import StockAPI


@pytest.fixture
def stock():
    with patch.object(StockAPI, "_get_access_token", return_value="token"):
        return StockAPI(appkey="key", appsecret="secret", account_no="12345678")


def test_date_and_query_validation(stock):
    for date in (None, 20240101, "2024-01-01", "20240230"):
        with pytest.raises(ValueError):
            stock._validate_yyyymmdd(date, "date")
    stock.make_tr_request = Mock()
    with pytest.raises(ValueError, match="query_type"):
        stock.get_credit_trend("005930", "20240101", "3")


def test_stock_price_and_orderbook_aliases(stock):
    stock.get_stock_basic_info = Mock(return_value={"price": 1})
    stock.get_stock_quote = Mock(return_value={"asks": []})
    assert stock.get_stock_price("005930") == {"price": 1}
    assert stock.get_stock_orderbook("005930") == {"asks": []}


@pytest.mark.parametrize(
    "basic_info, expected",
    [
        (None, {"rt_cd": "1", "msg1": "FINANCIAL_DATA_ERROR", "output": []}),
        ({"rt_cd": "1", "msg1": "failed"}, {"rt_cd": "1", "msg1": "failed"}),
        ({"rt_cd": "0"}, {"rt_cd": "1", "msg1": "FINANCIAL_DATA_SOURCE_MISSING", "output": []}),
    ],
)
def test_financial_handles_missing_and_error_sources(stock, basic_info, expected):
    stock.get_stock_basic_info = Mock(return_value=basic_info)
    result = stock.get_stock_financial("005930")
    for key, value in expected.items():
        assert result[key] == value


@pytest.mark.parametrize(
    "basic_info",
    [
        {"rt_cd": "0", "output1": {"eps": "10", "bps": "20", "per": "3", "pbr": "4", "stk_divi_rate": "5"}},
        {"rt_cd": "0", "stk_prpr_qry": {"stck_eps": "10", "stck_bps": "20", "stck_per": "3", "stck_pbr": "4", "dvdn_rate": "5"}},
        {"rt_cd": "0", "eps": "10", "bps": "20", "per": "3", "pbr": "4"},
    ],
)
def test_financial_normalizes_all_supported_basic_info_shapes(stock, basic_info):
    stock.get_stock_basic_info = Mock(return_value=basic_info)
    result = stock.get_stock_financial("005930")
    assert result["rt_cd"] == "0"
    assert result["output"][0]["eps"] == "10"
    assert result["output"][0]["bps"] == "20"
    assert result["output"][0]["per"] == "3"
    assert result["output"][0]["pbr"] == "4"
