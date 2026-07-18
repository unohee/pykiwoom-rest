"""CLI 핸들러가 실제로 안전한 조회 API만 호출하는지 검증한다."""

import importlib
import runpy
import sys
import warnings
from io import StringIO
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

cli = importlib.import_module("pykiwoom_rest.cli.main")


def args(**values):
    defaults = {"pretty": False, "raw": True, "format": "json", "yes": True}
    defaults.update(values)
    return SimpleNamespace(**defaults)


@pytest.fixture
def captured(monkeypatch):
    output = []
    monkeypatch.setattr(cli, "_out", lambda data, *unused, **kwargs: output.append(data))
    return output


class TestCliCommandCoverage:
    def test_table_output_recursion_boundaries(self):
        """테이블 탐색기의 깊이 제한과 스칼라 리스트 fallback을 검증한다."""
        for payload in (
            ["not-a-row"],
            {"plain": 1},
            {"a": {"b": {"c": {"d": []}}}},
            {"a": {"b": {"c": {"d": {"e": {"value": 1}}}}}},
        ):
            stream = StringIO()
            cli._out(payload, fmt="table", stream=stream)
            assert stream.getvalue()

    def test_price_rank_sector_and_investor_variants(self, monkeypatch, captured):
        client = MagicMock()
        client.get_stock_price.return_value = {"output": {"price": "1"}}
        client.get_stock_orderbook.return_value = {"output": {"bid": "1"}}
        client.get_daily_volume_top.return_value = {"output2": [{"stk_cd": "005930"}]}
        client.get_all_sector_index.return_value = {"output2": [{"sector": "1"}]}
        client.get_sector_current_price.return_value = {"output": {"sector": "1"}}
        client.get_institutional_trading_trend.return_value = {"output2": [{"date": "1"}]}
        client.get_stock_program_trading.return_value = {"output": {"date": "1"}}
        monkeypatch.setattr(cli, "_create_client", lambda: client)

        cli.cmd_price(args(code="005930", orderbook=True))
        cli.cmd_rank(args(type="volume", market="KOSPI"))
        cli.cmd_sector(args(all=True, code=None))
        cli.cmd_sector(args(all=False, code="0002"))
        cli.cmd_investor(args(code="005930", institution=True, program=False))
        cli.cmd_investor(args(code="005930", institution=False, program=True))
        assert len(captured) == 6

    def test_account_order_status_token_and_query_success(self, monkeypatch, captured):
        target = MagicMock()
        target.get_quote.return_value = {"output": {"price": "1"}}
        client = MagicMock()
        client.stock = target
        client.get_deposit_detail.return_value = {"output2": {"cash": "1"}}
        client.sell_stock.return_value = {"return_code": 0}
        client.verify_connection.return_value = {"ok": True}
        client.get_stats.return_value = {"requests": 1}
        client.get_token_status.return_value = {"valid": True}
        monkeypatch.setattr(cli, "_create_client", lambda: client)

        cli.cmd_account(args(type="deposit"))
        cli.cmd_order(args(action="sell", code="005930", qty=1, price=0))
        cli.cmd_status(args())
        cli.cmd_token(args())
        cli.cmd_query(args(domain="stock", method="get_quote", args=["code=005930"]))
        target.get_quote.assert_called_once_with(code="005930")
        assert len(captured) == 5

    def test_query_and_output_helpers_errors(self, monkeypatch, captured):
        client = MagicMock()
        client.stock = MagicMock()
        client.stock.get_quote.side_effect = RuntimeError("down")
        monkeypatch.setattr(cli, "_create_client", lambda: client)
        with pytest.raises(SystemExit):
            cli.cmd_query(args(domain="stock", method="get_quote", args=["malformed"]))
        with pytest.raises(SystemExit):
            cli.cmd_query(args(domain="stock", method="get_quote", args=[]))
        assert captured

        assert cli._extract_output({"data": {"output": {"x": 1}}}) == {"data": {"output": {"x": 1}}}
        assert cli._find_list_in_response({"metadata": {}, "nested": [{"x": 1}]}) == [{"x": 1}]
        summary, holdings = cli._split_account_balance({"output1": {"cash": 1}, "output2": [{"stk_cd": "x"}]})
        assert summary == {"cash": 1} and holdings == [{"stk_cd": "x"}]

    def test_parser_helpers_schema_and_main_dispatch(self, monkeypatch, capsys):
        assert cli._positive_int_arg("2") == 2
        assert cli._non_negative_int_arg("0") == 0
        assert cli._is_safe_query_method("get_quote")
        assert not cli._is_safe_query_method("buy_stock")
        with pytest.raises(Exception):
            cli._chart_interval_arg("2")

        monkeypatch.setattr(cli, "list_types", lambda: ["Stock"])
        cli.cmd_schema(args(json=True, type_name=None))
        assert "Stock" in capsys.readouterr().out

        called = []
        monkeypatch.setattr(cli, "build_parser", lambda: MagicMock(parse_args=lambda: args(command="token"), print_help=MagicMock()))
        monkeypatch.setattr(cli, "cmd_token", lambda parsed: called.append(parsed.command))
        monkeypatch.setattr(cli, "_close_clients", lambda: None)
        cli.main()
        assert called == ["token"]

    def test_output_market_client_and_close_helpers(self, monkeypatch):
        cli._market_status.update(checked=False, is_holiday=None, last_business_day=None, notice="notice")
        stream = StringIO()
        cli._out({"data": {"rows": [{"x": 1}]}}, fmt="table", stream=stream)
        assert "notice" in stream.getvalue()
        stream = StringIO()
        cli._out({"data": {"value": {"x": 1}}}, fmt="table", stream=stream)
        assert "x" in stream.getvalue()
        stream = StringIO()
        cli._out({"data": {"x": 1}}, pretty=True, stream=stream)
        assert '"_notice"' in stream.getvalue()

        client = MagicMock()
        monkeypatch.setattr("pykiwoom_rest.KiwoomRest", lambda: client)
        cli._CLIENTS.clear()
        assert cli._create_client() is client
        cli._close_clients()
        client.close.assert_called_once()

    def test_helper_error_and_empty_response_paths(self, captured):
        assert cli._extract_output(None) is None
        assert cli._extract_output({"rt_cd": "0"}) is None
        assert cli._api_empty_payload(None)["error"] == "empty API response"
        assert cli._api_empty_payload([1])["error"] == "unexpected API response"
        assert cli._api_empty_payload({"rt_cd": "1", "msg1": "bad"})["code"] == "1"
        assert cli._split_account_balance(None) == (None, None)
        assert cli._find_list_in_response([1]) is None
        assert cli._find_list_in_response("no") is None
        with pytest.raises(SystemExit):
            cli._validate_positive_int("count", None, args())

    def test_command_error_and_interactive_cancel_paths(self, monkeypatch, captured):
        client = MagicMock()
        client.get_stock_price.return_value = None
        client.get_stock_orderbook.return_value = {"output": {}}
        client.get_daily_chart.return_value = {"return_code": "E"}
        client.get_all_sector_index.return_value = {"output2": {}}
        client.get_sector_current_price.return_value = {"output": {}}
        client.get_foreign_trading.return_value = {"output": {}}
        monkeypatch.setattr(cli, "_create_client", lambda: client)

        cli.cmd_price(args(code="005930", orderbook=True))
        cli.cmd_chart(args(code="005930", minute=False, weekly=False, monthly=False, yearly=False, count=1))
        cli.cmd_sector(args(all=True, code=None))
        cli.cmd_sector(args(all=False, code="0001"))
        cli.cmd_investor(args(code="005930", institution=False, program=False))
        with pytest.raises(SystemExit):
            cli.cmd_rank(args(type="invalid", market="ALL"))
        with pytest.raises(SystemExit):
            cli.cmd_account(args(type="invalid"))

        monkeypatch.setattr("builtins.input", lambda _: "n")
        cli.cmd_order(args(action="buy", code="005930", qty=1, price=0, yes=False))
        cli.cmd_order(args(action="cancel", code="005930", order_no="1", qty=1, price=0, yes=False))
        assert client.buy_stock.call_count == 0 and client.cancel_order.call_count == 0

    def test_remaining_query_and_status_failure_paths(self, monkeypatch, captured):
        client = MagicMock()
        client.stock = None
        client.verify_connection.side_effect = RuntimeError("offline")
        client.get_stats.side_effect = RuntimeError("stats")
        monkeypatch.setattr(cli, "_create_client", lambda: client)
        with pytest.raises(SystemExit):
            cli.cmd_query(args(domain="stock", method="get_quote", args=[]))
        cli.cmd_status(args())
        assert captured[-1]["data"]["status"]["connection"]["error"] == "offline"
        with pytest.raises(SystemExit):
            cli.cmd_query(args(domain="stock", method="get_quote", args=["=value"]))

    def test_schema_parser_and_main_failure_branches(self, monkeypatch, capsys):
        class SchemaError(cli.SchemaTypeNotFound):
            pass

        monkeypatch.setattr(cli, "get_schema", lambda _: (_ for _ in ()).throw(SchemaError("missing", ["Stock"])))
        with pytest.raises(SystemExit):
            cli.cmd_schema(args(json=False, type_name="Missing"))
        assert "missing" in capsys.readouterr().err

        parser = cli.build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["chart", "005930", "--daily", "--weekly"])
        with pytest.raises(SystemExit):
            parser.parse_args(["order", "cancel", "005930", "--qty", "1"])

        no_command = MagicMock(parse_args=lambda: args(command=None), print_help=MagicMock())
        monkeypatch.setattr(cli, "build_parser", lambda: no_command)
        with pytest.raises(SystemExit):
            cli.main()
        no_command.print_help.assert_called_once()

        unknown = MagicMock(parse_args=lambda: args(command="unknown"), print_help=MagicMock())
        monkeypatch.setattr(cli, "build_parser", lambda: unknown)
        with pytest.raises(SystemExit):
            cli.main()
        unknown.print_help.assert_called_once()

    def test_main_exception_reports_and_closes_client(self, monkeypatch, captured):
        parser = MagicMock(parse_args=lambda: args(command="price", code="005930", orderbook=False))
        monkeypatch.setattr(cli, "build_parser", lambda: parser)
        monkeypatch.setattr(cli, "cmd_price", lambda _: (_ for _ in ()).throw(RuntimeError("boom")))
        closed = []
        monkeypatch.setattr(cli, "_close_clients", lambda: closed.append(True))
        with pytest.raises(SystemExit):
            cli.main()
        assert closed == [True]
        assert captured[-1]["error"] == "boom"

    @pytest.mark.parametrize("fn,value", [(cli._positive_int_arg, "0"), (cli._positive_int_arg, "bad"), (cli._non_negative_int_arg, "-1"), (cli._non_negative_int_arg, "bad")])
    def test_numeric_argument_errors(self, fn, value):
        with pytest.raises(Exception):
            fn(value)

    def test_remapped_list_fallbacks_and_query_unknown_method(self, monkeypatch, captured):
        client = MagicMock()
        client.get_daily_chart.return_value = {"nested": [{"cntr_tm": "20250101", "cur_prc": "1"}]}
        client.get_daily_volume_top.return_value = {"nested": [{"stk_cd": "005930"}]}
        client.get_all_sector_index.return_value = {"nested": [{"indx_nm": "KOSPI"}]}
        client.get_foreign_trading.return_value = {"nested": [{"dt": "20250101"}]}
        client.get_deposit_detail.return_value = {"output": {"cash": "1"}}
        client.stock = MagicMock()
        monkeypatch.setattr(cli, "_create_client", lambda: client)
        rich = {"raw": False}
        cli.cmd_chart(args(code="005930", minute=False, weekly=False, monthly=False, yearly=False, count=2, **rich))
        cli.cmd_rank(args(type="volume", market="ALL", **rich))
        cli.cmd_sector(args(all=True, code=None, **rich))
        cli.cmd_investor(args(code="005930", institution=False, program=False, **rich))
        cli.cmd_account(args(type="deposit", **rich))
        with pytest.raises(SystemExit):
            cli.cmd_query(args(domain="stock", method="get_missing", args=[]))
        assert len(captured) >= 6

    def test_close_failure_and_market_status_variants(self, monkeypatch, capsys):
        broken = MagicMock()
        broken.close.side_effect = RuntimeError("close")
        cli._CLIENTS[:] = [broken]
        cli._close_clients()
        assert "failed to close" in capsys.readouterr().err

        class Weekend:
            @classmethod
            def now(cls):
                return __import__("datetime").datetime(2026, 7, 18, 12)

        cli._market_status.update(checked=False, notice=None)
        monkeypatch.setattr(cli, "datetime", Weekend)
        cli._check_market_status()
        assert cli._market_status["is_holiday"] is True

    def test_remaining_validation_and_query_safety_helpers(self):
        assert cli._chart_interval_arg("5") == 5
        assert cli._chart_count_arg("1000") == 1000
        assert cli._validate_non_negative_int("price", None, args()) == 0
        assert cli._validate_non_negative_int("price", "0", args()) == 0
        for value in ("bad", "-1"):
            with pytest.raises(SystemExit):
                cli._validate_non_negative_int("price", value, args())
        with pytest.raises(SystemExit):
            cli._validate_chart_count("count", 1001, args())
        with pytest.raises(SystemExit):
            cli._validate_order_price("price", None, args())
        for method in ("_private", "cancel_order", "order_status", "get_token", "buy-stock"):
            assert not cli._is_safe_query_method(method)

    def test_parser_market_weekday_and_module_entrypoint(self, monkeypatch, capsys):
        parser = cli.CliArgumentParser()
        parser.add_argument("command")
        parser.add_argument("action")
        parser.add_argument("code", nargs="?")
        parser.add_argument("--qty", type=int)
        parser.add_argument("--order-no")
        with pytest.raises(SystemExit):
            parser.parse_args(["order", "cancel"])

        class Weekday:
            @classmethod
            def now(cls):
                return __import__("datetime").datetime(2026, 7, 20, 8)

        cli._market_status.update(checked=False, notice=None)
        monkeypatch.setattr(cli, "datetime", Weekday)
        cli._check_market_status()
        assert "장 시작 전" in cli._market_status["notice"]
        cli._check_market_status()

        monkeypatch.setattr(sys, "argv", ["kiwoom", "--help"])
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=RuntimeWarning, module="runpy")
            with pytest.raises(SystemExit):
                runpy.run_module("pykiwoom_rest.cli.main", run_name="__main__")
        assert "usage:" in capsys.readouterr().out

    def test_remaining_response_fallback_command_paths(self, monkeypatch, captured):
        client = MagicMock()
        client.get_stock_price.return_value = {"output": {}}
        client.get_stock_orderbook.return_value = None
        client.get_daily_chart.return_value = {"output": {"raw": "chart"}}
        client.get_trading_amount_top.return_value = {"output": {"raw": "rank"}}
        client.get_all_sector_index.return_value = {"output": {"raw": "sector"}}
        client.get_sector_current_price.return_value = {"output": {"raw": "sector"}}
        client.get_foreign_trading.return_value = {"output": {"raw": "investor"}}
        monkeypatch.setattr(cli, "_create_client", lambda: client)
        cli.cmd_price(args(code="005930", orderbook=True))
        cli.cmd_chart(args(code="005930", minute=False, weekly=False, monthly=False, yearly=False, count=1))
        cli.cmd_rank(args(type="amount", market="ALL"))
        cli.cmd_sector(args(all=True, code=None))
        cli.cmd_sector(args(all=False, code="0001"))
        cli.cmd_investor(args(code="005930", institution=False, program=False))
        with pytest.raises(SystemExit):
            cli.cmd_order(args(action="buy", code=None, qty=1, price=0))
        assert len(captured) >= 6

    def test_final_cli_boundary_paths(self, monkeypatch, captured):
        """환경 의존성 및 빈 응답처럼 일반 호출에서 드문 경계를 실행한다."""
        with pytest.raises(SystemExit):
            cli._validate_positive_int("count", "not-a-number", args())

        class AfterClose:
            @classmethod
            def now(cls):
                return __import__("datetime").datetime(2026, 7, 20, 16)

        cli._market_status.update(checked=False, notice=None)
        monkeypatch.setattr(cli, "datetime", AfterClose)
        cli._check_market_status()
        assert "장 마감 후" in cli._market_status["notice"]

        import builtins

        real_import = builtins.__import__

        def missing_dotenv(name, *args, **kwargs):
            if name == "dotenv":
                raise ImportError("missing dotenv")
            return real_import(name, *args, **kwargs)

        client = MagicMock()
        monkeypatch.setattr(builtins, "__import__", missing_dotenv)
        monkeypatch.setattr("pykiwoom_rest.KiwoomRest", lambda: client)
        cli._CLIENTS.clear()
        assert cli._create_client() is client
        cli._close_clients()

        for payload in ([], ["not-a-row"], {"x": 1}, {"x": {"y": {"z": {"q": {"r": 1}}}}}):
            cli._out(payload, fmt="table", stream=StringIO())
        assert cli._split_account_balance({"output": "not-a-dict", "cash": 1}) == ({"output": "not-a-dict", "cash": 1}, None)
        assert cli._find_list_in_response(None) is None
        assert cli._find_list_in_response({"output2": [{"row": 1}]}) == [{"row": 1}]

        empty_client = MagicMock()
        empty_client.get_daily_volume_top.return_value = {"output": {}}
        empty_client.get_all_sector_index.return_value = {"output": {}}
        empty_client.buy_stock.return_value = {"ok": True}
        monkeypatch.setattr(cli, "_create_client", lambda: empty_client)
        cli.cmd_rank(args(type="volume", market="ALL"))
        cli.cmd_sector(args(all=True, code=None))
        cli.cmd_order(args(action="buy", code="005930", qty=1, price=0))
        assert empty_client.buy_stock.called

        query_client = MagicMock()
        query_client.stock = object()
        monkeypatch.setattr(cli, "_create_client", lambda: query_client)
        monkeypatch.setattr(cli, "_safe_query_methods", lambda _: ["get_quote"])
        with pytest.raises(SystemExit):
            cli.cmd_query(args(domain="stock", method="get_quote", args=[]))

        parser = MagicMock(parse_args=lambda: args(command="price", code="005930", orderbook=False))
        monkeypatch.setattr(cli, "build_parser", lambda: parser)
        monkeypatch.setattr(cli, "cmd_price", lambda _: (_ for _ in ()).throw(SystemExit(1)))
        monkeypatch.setattr(cli, "_close_clients", lambda: None)
        with pytest.raises(SystemExit):
            cli.main()
