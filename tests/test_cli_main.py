import importlib
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

cli = importlib.import_module("pykiwoom_rest.cli.main")


@pytest.fixture(autouse=True)
def reset_market_notice():
    cli._market_status["notice"] = None


def _args(**overrides):
    defaults = {
        "pretty": False,
        "raw": False,
        "format": "json",
        "yes": True,
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def test_chart_daily_passes_count_to_api(monkeypatch, capsys):
    client = Mock()
    client.get_daily_chart.return_value = {"output2": [{"dt": "20260703"}]}
    monkeypatch.setattr(cli, "_create_client", lambda: client)

    cli.cmd_chart(
        _args(
            code="005930",
            minute=False,
            weekly=False,
            monthly=False,
            yearly=False,
            interval=None,
            from_date=None,
            to_date=None,
            count=500,
        )
    )

    client.get_daily_chart.assert_called_once_with("005930", None, None, 500)
    assert json.loads(capsys.readouterr().out)["data"]["chart"]["count"] == 1


@pytest.mark.parametrize(
    ("flag", "method_name"),
    [
        ("weekly", "get_weekly_chart"),
        ("monthly", "get_monthly_chart"),
        ("yearly", "get_yearly_chart"),
    ],
)
def test_chart_period_commands_pass_count_to_api(monkeypatch, capsys, flag, method_name):
    client = Mock()
    getattr(client, method_name).return_value = {"output2": [{"dt": "20260703"}]}
    monkeypatch.setattr(cli, "_create_client", lambda: client)

    args = {
        "code": "005930",
        "minute": False,
        "weekly": False,
        "monthly": False,
        "yearly": False,
        "interval": None,
        "from_date": None,
        "to_date": None,
        "count": 500,
    }
    args[flag] = True

    cli.cmd_chart(_args(**args))

    getattr(client, method_name).assert_called_once_with("005930", None, None, 500)
    assert json.loads(capsys.readouterr().out)["data"]["chart"]["count"] == 1


def test_chart_minute_preserves_kiwoom_timestamp(monkeypatch, capsys):
    client = Mock()
    client.get_minute_chart.return_value = {
        "stk_min_pole_chart_qry": [
            {
                "cntr_tm": "20260704123000",
                "cur_prc": "70000",
                "open_pric": "69900",
                "high_pric": "70100",
                "low_pric": "69800",
                "trde_qty": "12345",
            }
        ]
    }
    monkeypatch.setattr(cli, "_create_client", lambda: client)

    cli.cmd_chart(
        _args(
            code="005930",
            minute=True,
            weekly=False,
            monthly=False,
            yearly=False,
            interval=5,
            from_date=None,
            to_date=None,
            count=100,
        )
    )

    row = json.loads(capsys.readouterr().out)["data"]["chart"]["data"][0]
    assert row["timestamp"] == "20260704123000"
    assert row["close"] == "70000"


def test_chart_minute_passes_date_range_to_api(monkeypatch, capsys):
    client = Mock()
    client.get_minute_chart.return_value = {"stk_min_pole_chart_qry": []}
    monkeypatch.setattr(cli, "_create_client", lambda: client)

    cli.cmd_chart(
        _args(
            code="005930",
            minute=True,
            weekly=False,
            monthly=False,
            yearly=False,
            interval=5,
            from_date="20260112",
            to_date="20260113",
            count=100,
        )
    )

    client.get_minute_chart.assert_called_once_with("005930", 5, "20260112", "20260113", 100)


@pytest.mark.parametrize(
    "argv",
    [
        ["chart", "005930", "--count", "0"],
        ["chart", "005930", "--count", "-1"],
        ["order", "buy", "005930", "--qty", "0"],
        ["order", "buy", "005930", "--qty", "-1"],
        ["order", "buy", "005930", "--qty", "1", "--price", "-1"],
    ],
)
def test_parser_rejects_invalid_numeric_arguments(argv):
    parser = cli.build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(argv)


def test_order_handler_rejects_invalid_qty_before_client_creation(monkeypatch, capsys):
    create_client = Mock()
    monkeypatch.setattr(cli, "_create_client", create_client)

    with pytest.raises(SystemExit):
        cli.cmd_order(_args(action="buy", code="005930", qty=-1, price=0))

    create_client.assert_not_called()
    assert "positive integer" in capsys.readouterr().err


def test_cancel_order_uses_code_and_order_no_contract(monkeypatch, capsys):
    client = Mock()
    client.cancel_order.return_value = {"return_code": 0}
    monkeypatch.setattr(cli, "_create_client", lambda: client)

    cli.cmd_order(
        _args(action="cancel", code="005930", order_no="123456", qty=1, price=0)
    )

    client.cancel_order.assert_called_once_with("123456", "005930", 1)
    assert json.loads(capsys.readouterr().out)["data"]["order"]["action"] == "cancel"


def test_cancel_order_requires_order_no_before_client_creation(monkeypatch, capsys):
    create_client = Mock()
    monkeypatch.setattr(cli, "_create_client", create_client)

    with pytest.raises(SystemExit):
        cli.cmd_order(_args(action="cancel", code="005930", order_no=None, qty=1, price=0))

    create_client.assert_not_called()
    assert "--order-no" in capsys.readouterr().err


def test_query_rejects_dangerous_domain_before_client_creation(monkeypatch, capsys):
    create_client = Mock()
    monkeypatch.setattr(cli, "_create_client", create_client)

    with pytest.raises(SystemExit):
        cli.cmd_query(_args(domain="order", method="buy_stock", args=[]))

    create_client.assert_not_called()
    output = json.loads(capsys.readouterr().err)
    assert output["error"] == "Unsupported query domain: order"
    assert "order" not in output["available"]


def test_query_rejects_unsafe_method_on_safe_domain(monkeypatch, capsys):
    client = Mock()
    client.stock.request = Mock()
    monkeypatch.setattr(cli, "_create_client", lambda: client)

    with pytest.raises(SystemExit):
        cli.cmd_query(_args(domain="stock", method="request", args=[]))

    client.stock.request.assert_not_called()
    assert "Unsafe or unsupported query method" in capsys.readouterr().err


def test_account_balance_handles_flat_kt00018_response(monkeypatch, capsys):
    client = Mock()
    client.get_balance_detail.return_value = {
        "tot_pur_amt": "000000017598258",
        "tot_evlt_amt": "000000025789890",
        "tot_evlt_pl": "000000008138825",
        "tot_prft_rt": "46.25",
        "acnt_evlt_remn_indv_tot": [
            {
                "stk_cd": "A005930",
                "stk_nm": "삼성전자",
                "rmnd_qty": "000000000000003",
                "pur_pric": "000000000124500",
                "cur_prc": "000000059000",
                "evlt_amt": "000000000177000",
                "evltv_prft": "-00000000196888",
                "prft_rt": "-52.71",
            }
        ],
        "return_code": 0,
        "return_msg": "조회가 완료되었습니다",
    }
    monkeypatch.setattr(cli, "_create_client", lambda: client)

    cli.cmd_account(_args(type="balance"))

    account = json.loads(capsys.readouterr().out)["data"]["account"]
    assert account["summary"]["totalPurchase"] == "000000017598258"
    assert account["summary"]["totalEvalAmount"] == "000000025789890"
    assert account["holdings"][0]["code"] == "A005930"
    assert account["holdings"][0]["quantity"] == "000000000000003"


def test_order_rejects_missing_price_before_client(monkeypatch):
    client = Mock()
    monkeypatch.setattr(cli, "_create_client", lambda: client)

    with pytest.raises(SystemExit):
        cli.cmd_order(_args(action="buy", code="005930", qty=1, price=None))

    client.buy_stock.assert_not_called()


def test_cancel_rejects_invalid_qty_but_does_not_require_price(monkeypatch):
    client = Mock()
    monkeypatch.setattr(cli, "_create_client", lambda: client)

    with pytest.raises(SystemExit):
        cli.cmd_order(_args(action="cancel", code="005930", order_no="1", qty=0, price=0))
    cli.cmd_order(_args(action="cancel", code="005930", order_no="1", qty=1, price=None))

    client.cancel_order.assert_called_once_with("1", "005930", 1)


def test_cancel_parser_contract_success_and_failures():
    parser = cli.build_parser()

    args = parser.parse_args(["order", "cancel", "005930", "--order-no", "123", "--qty", "1", "--price", "0", "--yes"])
    assert args.action == "cancel"
    assert args.code == "005930"
    assert args.order_no == "123"
    assert args.qty == 1
    assert args.price == 0

    with pytest.raises(SystemExit):
        parser.parse_args(["order", "cancel", "005930", "--order-no", "123", "--qty", "0", "--price", "0"])
    with pytest.raises(SystemExit):
        parser.parse_args(["order", "cancel", "005930", "--order-no", "123", "--qty", "1", "--price", "-1"])


def test_query_blocks_token_method_before_client_creation(monkeypatch):
    create_client = Mock()
    monkeypatch.setattr(cli, "_create_client", create_client)

    with pytest.raises(SystemExit):
        cli.cmd_query(_args(domain="stock", method="get_access_token", args=[]))

    create_client.assert_not_called()


def test_chart_count_bounds_parser():
    parser = cli.build_parser()
    assert parser.parse_args(["chart", "005930", "--count", "1"]).count == 1
    assert parser.parse_args(["chart", "005930", "--count", "1000"]).count == 1000
    with pytest.raises(SystemExit):
        parser.parse_args(["chart", "005930", "--count", "0"])
    with pytest.raises(SystemExit):
        parser.parse_args(["chart", "005930", "--count", "1001"])
