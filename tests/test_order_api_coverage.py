from unittest.mock import Mock

import pytest

from pykiwoom_rest.order_api import OrderAPI


@pytest.fixture
def order_api():
    api = OrderAPI(appkey="key", appsecret="secret", account_no="12345678")
    api.make_tr_request = Mock(return_value={"rt_cd": "0"})
    return api


@pytest.mark.parametrize(
    "method_name, args, tr_code, endpoint, expected",
    [
        ("buy_stock", ("005930", 1), "kt10000", "order", {"ord_qty": "1", "ord_prc": "0"}),
        ("sell_stock", ("005930", 2), "kt10001", "order", {"ord_qty": "2", "ord_prc": "0"}),
        ("modify_order", (" 123 ", "005930", 1), "kt10002", "order", {"orgn_ord_no": "123", "mdf_qty": "1"}),
        ("cancel_order", ("123", "005930", 1), "kt10003", "order", {"orgn_ord_no": "123", "cncl_qty": "1"}),
        ("buy_credit", ("005930", 1), "kt10006", "credit_order", {"crdt_tp": "02"}),
        ("sell_credit", ("005930", 1), "kt10007", "credit_order", {"crdt_tp": "02"}),
        ("modify_credit_order", ("123", "005930", 1), "kt10008", "credit_order", {"orgn_ord_no": "123"}),
        ("cancel_credit_order", ("123", "005930", 1), "kt10009", "credit_order", {"cncl_qty": "1"}),
    ],
)
def test_order_submission_contracts(order_api, method_name, args, tr_code, endpoint, expected):
    assert getattr(order_api, method_name)(*args) == {"rt_cd": "0"}
    kwargs = order_api.make_tr_request.call_args.kwargs
    assert kwargs["tr_code"] == tr_code
    assert kwargs["endpoint"] == endpoint
    assert kwargs["data"]["acnt_no"] == "12345678"
    assert kwargs["data"]["stk_cd"] == "005930"
    assert all(kwargs["data"][key] == value for key, value in expected.items())


@pytest.mark.parametrize("market, code", [("ALL", "0"), ("KOSPI", "1"), ("KOSDAQ", "2"), ("1", "1")])
def test_credit_availability_contracts(order_api, market, code):
    order_api.get_credit_available_stocks(market)
    assert order_api.make_tr_request.call_args.kwargs["data"] == {"mrkt_tp": code}
    order_api.check_credit_available("005930")
    assert order_api.make_tr_request.call_args.kwargs["data"] == {"stk_cd": "005930"}


def test_order_validation_rejects_invalid_inputs(order_api):
    order_api.account_no = ""
    with pytest.raises(ValueError, match="account_no"):
        order_api.buy_stock("005930", 1)
    order_api.account_no = "12345678"
    for invalid in (0, -1, True, "1"):
        with pytest.raises(ValueError, match="quantity"):
            order_api.buy_stock("005930", invalid)
    for order_type, price in (("00", 0), ("03", 1)):
        with pytest.raises(ValueError, match="price"):
            order_api.buy_stock("005930", 1, price=price, order_type=order_type)
    with pytest.raises(ValueError, match="order_type"):
        order_api.buy_stock("005930", 1, order_type="99")
    with pytest.raises(ValueError, match="price_type"):
        order_api.buy_stock("005930", 1, price_type="99")
    with pytest.raises(ValueError, match="credit_type"):
        order_api.buy_credit("005930", 1, credit_type="00")
    with pytest.raises(ValueError, match="original_order_no"):
        order_api.cancel_order("", "005930", 1)
    with pytest.raises(ValueError, match="market"):
        order_api.get_credit_available_stocks("NASDAQ")


def test_limit_order_and_static_validators(order_api):
    order_api.buy_stock("005930", 1, price=70000, order_type="00", price_type="00")
    assert order_api.make_tr_request.call_args.kwargs["data"]["ord_prc"] == "70000"
    with pytest.raises(ValueError, match="non-negative"):
        OrderAPI._validate_non_negative_int(-1, "price")
    with pytest.raises(ValueError, match="documented"):
        OrderAPI._validate_code("00", "unknown")
