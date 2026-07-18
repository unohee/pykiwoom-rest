import argparse

import pytest

import importlib

cli = importlib.import_module("pykiwoom_rest.cli.main")


class DummyClient:
    def __init__(self):
        self.calls = []

    def get_daily_chart(self, code, from_date=None, to_date=None, count=100):
        self.calls.append(("daily", code, from_date, to_date, count))
        return {"output2": [{"date": str(i)} for i in range(count + 2)]}

    def get_weekly_chart(self, code, from_date=None, to_date=None, count=100):
        self.calls.append(("weekly", code, from_date, to_date, count))
        return {"output2": [{"date": str(i)} for i in range(count + 2)]}

    def get_monthly_chart(self, code, from_date=None, to_date=None, count=100):
        self.calls.append(("monthly", code, from_date, to_date, count))
        return {"output2": [{"date": str(i)} for i in range(count + 2)]}

    def get_yearly_chart(self, code, from_date=None, to_date=None, count=100):
        self.calls.append(("yearly", code, from_date, to_date, count))
        return {"output2": [{"date": str(i)} for i in range(count + 2)]}

    def cancel_order(self, order_no, stock_code, qty):
        self.calls.append(("cancel", order_no, stock_code, qty))
        return {"ok": True}

    def buy_stock(self, code, qty, price):
        self.calls.append(("buy", code, qty, price))
        return {"ok": True}


class CapturedOutput:
    def __init__(self):
        self.payloads = []

    def __call__(self, data, pretty=False, raw=False, format="json"):
        self.payloads.append(data)


def ns(**kwargs):
    defaults = {
        "pretty": False,
        "raw": True,
        "format": "json",
        "from_date": None,
        "to_date": None,
        "minute": False,
        "weekly": False,
        "monthly": False,
        "yearly": False,
        "interval": None,
        "count": 100,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.mark.parametrize(
    ("flag", "expected_call"),
    [
        ({}, "daily"),
        ({"weekly": True}, "weekly"),
        ({"monthly": True}, "monthly"),
        ({"yearly": True}, "yearly"),
    ],
)
def test_chart_count_is_validated_passed_and_sliced(monkeypatch, flag, expected_call):
    client = DummyClient()
    captured = CapturedOutput()
    monkeypatch.setattr(cli, "_create_client", lambda: client)
    monkeypatch.setattr(cli, "_out", captured)

    cli.cmd_chart(ns(code="005930", count=3, **flag))

    assert client.calls == [(expected_call, "005930", None, None, 3)]
    chart = captured.payloads[0]["data"]["chart"]
    assert chart["count"] == 3
    assert len(chart["data"]) == 3


@pytest.mark.parametrize("bad_count", [0, -1])
def test_chart_rejects_non_positive_count(bad_count):
    with pytest.raises(SystemExit):
        cli.cmd_chart(ns(code="005930", count=bad_count))


@pytest.mark.parametrize(
    "kwargs",
    [
        {"action": "buy", "code": "005930", "qty": 0, "price": 0},
        {"action": "buy", "code": "005930", "qty": -1, "price": 0},
        {"action": "buy", "code": "005930", "qty": 1, "price": -10},
        {"action": "cancel", "code": "005930", "qty": 0, "order_no": "123"},
        {"action": "cancel", "code": "005930", "qty": 1, "order_no": None},
    ],
)
def test_order_rejects_invalid_quantity_price_and_cancel_contract(kwargs):
    with pytest.raises(SystemExit):
        cli.cmd_order(argparse.Namespace(pretty=False, raw=False, format="json", yes=True, **kwargs))


def test_cancel_uses_stock_code_and_order_no(monkeypatch):
    client = DummyClient()
    captured = CapturedOutput()
    monkeypatch.setattr(cli, "_create_client", lambda: client)
    monkeypatch.setattr(cli, "_out", captured)

    cli.cmd_order(
        argparse.Namespace(
            pretty=False,
            raw=False,
            format="json",
            yes=True,
            action="cancel",
            code="005930",
            order_no="123456",
            qty=1,
            price=0,
        )
    )

    assert client.calls == [("cancel", "123456", "005930", 1)]


@pytest.mark.parametrize(
    ("domain", "method"),
    [
        ("order", "buy_stock"),
        ("client", "buy_stock"),
        ("stock", "buy_stock"),
        ("account", "delete_token"),
    ],
)
def test_query_rejects_unsafe_domains_and_methods(domain, method):
    with pytest.raises(SystemExit):
        cli.cmd_query(argparse.Namespace(domain=domain, method=method, args=[], pretty=False, raw=False, format="json"))
