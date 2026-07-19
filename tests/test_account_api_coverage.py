from unittest.mock import Mock

import pytest

from pykiwoom_rest.account_api import AccountAPI


@pytest.fixture
def account_api():
    api = AccountAPI(appkey="key", appsecret="secret", account_no="12345678")
    api.make_tr_request = Mock(return_value={"rt_cd": "0"})
    return api


@pytest.mark.parametrize(
    "method_name",
    [
        "get_deposit_detail",
        "get_estimated_asset",
        "get_account_evaluation",
        "get_execution_balance",
        "get_next_day_settlement",
        "get_order_execution_status",
        "get_withdrawable_amount",
        "get_margin_detail",
        "get_current_day_status",
        "get_balance_detail",
        "get_unfilled_orders",
        "get_executed_orders",
        "get_realized_profit_detail",
    ],
)
def test_account_methods_submit_account_number(account_api, method_name):
    result = getattr(account_api, method_name)()

    assert result == {"rt_cd": "0"}
    assert account_api.make_tr_request.call_args.kwargs["data"] == {"acnt_no": "12345678"}


@pytest.mark.parametrize(
    "method_name, kwargs, expected_data",
    [
        ("get_daily_estimated_asset", {"base_date": "20260102"}, {"base_dt": "20260102"}),
        ("get_daily_return_detail", {"base_date": "20260102"}, {"base_dt": "20260102"}),
        ("get_daily_trading_diary", {"base_date": "20260102"}, {"base_dt": "20260102"}),
        ("get_order_execution_detail", {"start_date": "20260101", "end_date": "20260102"}, {"start_dt": "20260101", "end_dt": "20260102"}),
        ("get_trading_history", {"start_date": "20260101", "end_date": "20260102"}, {"start_dt": "20260101", "end_dt": "20260102"}),
        ("get_account_return", {"start_date": "20260101", "end_date": "20260102"}, {"start_dt": "20260101", "end_dt": "20260102"}),
    ],
)
def test_account_date_methods_validate_and_forward_parameters(account_api, method_name, kwargs, expected_data):
    getattr(account_api, method_name)(**kwargs)

    submitted = account_api.make_tr_request.call_args.kwargs["data"]
    assert submitted == {"acnt_no": "12345678", **expected_data}


@pytest.mark.parametrize("method_name", ["get_orderable_quantity_by_margin", "get_orderable_quantity_by_credit"])
def test_orderable_quantity_methods_validate_price_and_normalize_stock(account_api, method_name):
    getattr(account_api, method_name)("005930", 70000)

    submitted = account_api.make_tr_request.call_args.kwargs["data"]
    assert submitted == {"acnt_no": "12345678", "stk_cd": "005930", "ord_prc": "70000"}
    with pytest.raises(ValueError, match="positive"):
        getattr(account_api, method_name)("005930", 0)


def test_split_order_detail_and_date_validation_errors(account_api):
    assert AccountAPI._validate_date(None, "base_date") is None
    for invalid in (20260101, "2026010"):
        with pytest.raises(ValueError, match="YYYYMMDD"):
            AccountAPI._validate_date(invalid, "base_date")
    with pytest.raises(ValueError, match="positive integer"):
        AccountAPI._validate_positive_price(True)
    account_api.get_unfilled_split_order_detail(" 12345 ")
    assert account_api.make_tr_request.call_args.kwargs["data"]["ord_no"] == "12345"
    for invalid in ("", "12-A", None):
        with pytest.raises(ValueError):
            account_api.get_unfilled_split_order_detail(invalid)
    with pytest.raises(ValueError, match="before"):
        account_api.get_trading_history("20260102", "20260101")
    with pytest.raises(ValueError, match="valid"):
        account_api.get_daily_estimated_asset("20260230")
