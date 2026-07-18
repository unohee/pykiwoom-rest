from unittest.mock import Mock, patch
from datetime import datetime, timedelta

import pytest

from pykiwoom_rest.kiwoom_rest import KiwoomRest


def _rest():
    rest = object.__new__(KiwoomRest)
    for name in ("auth_api", "stock_api", "investor_api", "program_api", "chart_api", "ranking_api", "account_api", "order_api", "sector_api"):
        api = Mock()
        api.access_token = None
        api.token_expires = None
        setattr(rest, name, api)
    rest._websocket_api = None
    rest._websocket_enabled = False
    return rest


def test_legacy_stock_investor_program_chart_and_ranking_delegates():
    rest = _rest()
    cases = [
        ("stock_api", "get_stock_basic_info", "get_stock_price", ("005930",)),
        ("stock_api", "get_stock_quote", "get_stock_orderbook", ("005930",)),
        ("stock_api", "get_execution_info", "get_execution_info", ("005930",)),
        ("stock_api", "get_credit_trend", "get_credit_trend", ("005930", "20240101", "2")),
        ("stock_api", "get_daily_trading_detail", "get_daily_trading_detail", ("20240101",)),
        ("stock_api", "get_new_high_low", "get_new_high_low", ()),
        ("investor_api", "get_foreign_trading", "get_foreign_trading", ("005930",)),
        ("investor_api", "get_stock_investor_trading", "get_stock_investor_trading", ()),
        ("program_api", "get_program_trading_daily", "get_program_trading_daily", ("005930",)),
        ("stock_api", "get_stock_program_trading", "get_stock_program_trading", ("005930",)),
        ("program_api", "get_stock_trade_volume_power", "get_stock_trade_volume_power", ("005930",)),
        ("chart_api", "get_tick_chart", "get_tick_chart", ("005930", 10)),
        ("chart_api", "get_minute_chart", "get_minute_chart", ("005930", 5, "a", "b", 10)),
        ("chart_api", "get_daily_chart", "get_daily_chart", ("005930", "a", "b")),
        ("chart_api", "get_weekly_chart", "get_weekly_chart", ("005930", "a", "b")),
        ("chart_api", "get_monthly_chart", "get_monthly_chart", ("005930", "a", "b")),
        ("chart_api", "get_yearly_chart", "get_yearly_chart", ("005930", "a", "b")),
        ("ranking_api", "get_volume_top", "get_volume_top", ("KOSPI", 5)),
        ("ranking_api", "get_hourly_program_trading", "get_hourly_program_trading", ("005930", "20240101", "2")),
        ("ranking_api", "get_trading_amount_top", "get_trading_amount_top", ()),
        ("ranking_api", "get_previous_volume_top", "get_previous_volume_top", ()),
    ]
    for api_name, target, wrapper, args in cases:
        method = getattr(rest, wrapper)
        mocked = getattr(rest, api_name)
        getattr(mocked, target).return_value = {wrapper: True}
        assert method(*args) == {wrapper: True}


def test_legacy_account_order_sector_auth_and_utilities_delegates():
    rest = _rest()
    cases = [
        ("account_api", "get_deposit_detail", "get_deposit_detail", ()),
        ("account_api", "get_account_evaluation", "get_account_evaluation", ()),
        ("account_api", "get_balance_detail", "get_balance_detail", ()),
        ("account_api", "get_unfilled_orders", "get_unfilled_orders", ()),
        ("account_api", "get_executed_orders", "get_executed_orders", ()),
        ("account_api", "get_account_return", "get_account_return", ("a", "b")),
        ("order_api", "buy_stock", "buy_stock", ("005930", 1)),
        ("order_api", "sell_stock", "sell_stock", ("005930", 1)),
        ("order_api", "modify_order", "modify_order", ("1", "005930", 1)),
        ("order_api", "cancel_order", "cancel_order", ("1", "005930", 1)),
        ("sector_api", "get_sector_current_price", "get_sector_current_price", ()),
        ("sector_api", "get_all_sector_index", "get_all_sector_index", ()),
        ("sector_api", "get_sector_daily_chart", "get_sector_daily_chart", ("001",)),
        ("auth_api", "get_access_token", "get_access_token", ()),
        ("auth_api", "revoke_token", "revoke_token", ()),
        ("auth_api", "refresh_token", "refresh_token", ()),
        ("auth_api", "logout", "logout", ()),
    ]
    for api_name, target, wrapper, args in cases:
        getattr(getattr(rest, api_name), target).return_value = {wrapper: True}
        assert getattr(rest, wrapper)(*args) == {wrapper: True}


def test_remaining_legacy_ranking_account_and_sector_delegates():
    rest = _rest()
    cases = [
        ("ranking_api", "get_hourly_program_trading_paginated", "get_hourly_program_trading_paginated", ("005930", "20240101")),
        ("ranking_api", "get_foreign_period_trading_top", "get_foreign_top_buy", ("1",)),
        ("ranking_api", "get_trading_volume_surge", "get_trading_volume_surge", ()),
        ("ranking_api", "get_previous_day_rate_top", "get_previous_day_rate_top", ()),
        ("ranking_api", "get_daily_volume_top", "get_daily_volume_top", ()),
        ("ranking_api", "get_foreign_window_trading_top", "get_foreign_window_trading_top", ()),
        ("ranking_api", "get_stock_securities_ranking", "get_stock_securities_ranking", ("005930",)),
        ("ranking_api", "get_daily_top_departure", "get_daily_top_departure", ()),
        ("ranking_api", "get_same_net_trading_ranking", "get_same_net_trading_ranking", ()),
        ("ranking_api", "get_foreign_institution_trading_top", "get_foreign_institution_trading_top", ()),
        ("ranking_api", "get_bid_ask_volume_top", "get_bid_ask_volume_top", ()),
        ("ranking_api", "get_bid_ask_volume_surge", "get_bid_ask_volume_surge", ()),
        ("ranking_api", "get_remaining_volume_surge", "get_remaining_volume_surge", ()),
        ("ranking_api", "get_expected_execution_rate_top", "get_expected_execution_rate_top", ()),
        ("ranking_api", "get_intraday_investor_trading_top", "get_intraday_investor_trading_top", ()),
        ("ranking_api", "get_overtime_single_price_rate_ranking", "get_overtime_single_price_rate_ranking", ()),
        ("account_api", "get_estimated_asset", "get_estimated_asset", ()),
        ("account_api", "get_execution_balance", "get_execution_balance", ()),
        ("account_api", "get_daily_estimated_asset", "get_daily_estimated_asset", ()),
        ("account_api", "get_realized_profit_detail", "get_realized_profit_detail", ()),
        ("account_api", "get_daily_trading_diary", "get_daily_trading_diary", ()),
        ("account_api", "get_trading_history", "get_trading_history", ()),
        ("sector_api", "get_sector_minute_chart", "get_sector_minute_chart", ("001",)),
        ("sector_api", "get_sector_weekly_chart", "get_sector_weekly_chart", ("001",)),
        ("sector_api", "get_sector_monthly_chart", "get_sector_monthly_chart", ("001",)),
        ("sector_api", "get_sector_yearly_chart", "get_sector_yearly_chart", ("001",)),
        ("sector_api", "get_sector_tick_chart", "get_sector_tick_chart", ("001",)),
        ("sector_api", "get_sector_program_trading", "get_sector_program_trading", ("001",)),
        ("sector_api", "get_sector_investor_trading", "get_sector_investor_trading", ("001",)),
        ("sector_api", "get_sector_stock_price", "get_sector_stock_price", ()),
        ("sector_api", "get_sector_daily_current", "get_sector_daily_current", ("001",)),
        ("stock_api", "get_stock_financial", "get_stock_financial", ("005930",)),
        ("sector_api", "get_index_daily_price", "get_index_daily_price", ("001",)),
        ("program_api", "get_pbar_concentration", "get_pbar_concentration", ()),
    ]
    for api_name, target, wrapper, args in cases:
        getattr(getattr(rest, api_name), target).return_value = {wrapper: True}
        assert getattr(rest, wrapper)(*args) == {wrapper: True}


def test_token_status_stats_lifecycle_and_properties():
    rest = _rest()
    expiry = datetime.now() + timedelta(seconds=120)
    rest.stock_api.access_token = "x" * 24
    rest.stock_api.token_expires = expiry
    for api in (rest.stock_api, rest.chart_api, rest.ranking_api):
        api.get_stats.return_value = {"request_count": 2, "error_count": 1}
        api.rate_limiter = Mock()
    assert rest.get_token_status()["needs_refresh"] is True
    assert rest.verify_connection() == rest.stock_api.health_check.return_value
    stats = rest.get_stats()
    assert stats["total_requests"] == 6 and stats["total_errors"] == 3
    rest.reset_rate_limiter()
    rest.close()
    with rest as entered:
        assert entered is rest
    assert rest.auth is rest.auth_api and rest.stock is rest.stock_api
    assert rest.chart is rest.chart_api and rest.ranking is rest.ranking_api


def test_websocket_requires_enablement_before_subscription():
    rest = _rest()
    with pytest.raises(RuntimeError, match="활성화"):
        rest.subscribe_realtime_quote("005930")
    with pytest.raises(RuntimeError, match="활성화"):
        rest.subscribe_realtime_orderbook("005930")
    with pytest.raises(RuntimeError, match="활성화"):
        rest.subscribe_realtime_trade("005930")
    assert rest.unsubscribe_realtime_all() is None


def test_initialization_auth_sync_and_websocket_lifecycle():
    api_instances = [Mock() for _ in range(9)]
    for api in api_instances:
        api.access_token = None
        api.token_expires = None
    api_instances[0].access_token = "newest"
    api_instances[0].token_expires = datetime.now() + timedelta(hours=1)
    api_instances[1].api_base.appkey = "key"
    api_instances[1].api_base.appsecret = "secret"
    with (
        patch("pykiwoom_rest.kiwoom_rest.AuthAPI", return_value=api_instances[0]),
        patch("pykiwoom_rest.kiwoom_rest.StockAPI", return_value=api_instances[1]),
        patch("pykiwoom_rest.kiwoom_rest.InvestorAPI", return_value=api_instances[2]),
        patch("pykiwoom_rest.kiwoom_rest.ProgramAPI", return_value=api_instances[3]),
        patch("pykiwoom_rest.kiwoom_rest.ChartAPI", return_value=api_instances[4]),
        patch("pykiwoom_rest.kiwoom_rest.RankingAPI", return_value=api_instances[5]),
        patch("pykiwoom_rest.kiwoom_rest.AccountAPI", return_value=api_instances[6]),
        patch("pykiwoom_rest.kiwoom_rest.OrderAPI", return_value=api_instances[7]),
        patch("pykiwoom_rest.kiwoom_rest.SectorAPI", return_value=api_instances[8]),
        patch("pykiwoom_rest.kiwoom_rest.WebSocketAPI") as websocket_class,
    ):
        rest = KiwoomRest(account_no="account", appkey="key", appsecret="secret")
        assert rest.stock_api.access_token == "newest"
        socket = rest.websocket
        assert socket is websocket_class.return_value
        loop = Mock()
        loop.run_until_complete.return_value = True
        with patch("asyncio.get_event_loop", return_value=loop):
            assert rest.enable_websocket() is True
            assert rest.subscribe_realtime_quote("005930") is True
            assert rest.subscribe_realtime_orderbook("005930") is True
            assert rest.subscribe_realtime_trade("005930") is True
            rest.unsubscribe_realtime_all()
            rest.disable_websocket()
        assert rest._websocket_enabled is False


def test_remaining_investor_delegates_and_token_sync_without_expiry():
    rest = _rest()
    cases = [
        ("get_stock_member_trading", ("005930",)),
        ("get_institutional_foreign_consecutive_trading", ("ALL", "a", "b")),
        ("get_institutional_request", ("005930",)),
        ("get_institutional_daily_trading", ("005930", "a", "b")),
        ("get_sector_code_list", ()),
        ("get_member_company_list", ()),
    ]
    for method, arguments in cases:
        target = getattr(rest.investor_api, method)
        target.return_value = {method: True}
        assert getattr(rest, method)(*arguments) == {method: True}

    rest.stock_api.access_token = "token-without-expiry"
    rest.stock_api.token_expires = None
    rest._sync_authentication()
    assert rest.account_api.access_token == "token-without-expiry"


def test_remaining_rest_wrappers_and_new_event_loop_fallback():
    rest = _rest()
    rest.investor_api.get_institutional_trading_trend.return_value = {"trend": True}
    rest.stock_api.get_stock_elapsed_time.return_value = {"elapsed": True}
    rest.chart_api.get_minute_chart_paginated.return_value = {"pages": True}
    rest.chart_api.get_minute_chart_with_date.return_value = {"date": True}
    assert rest.get_institutional_trading_trend("005930") == {"trend": True}
    assert rest.get_stock_elapsed_time("005930") == {"elapsed": True}
    assert rest.get_minute_chart_paginated("005930") == {"pages": True}
    assert rest.get_minute_chart_with_date("005930") == {"date": True}
    assert rest.get_token_status()["has_token"] is False
    rest.stock_api.access_token = "token-no-expiry"
    rest.stock_api.token_expires = None
    assert rest.get_token_status()["token_prefix"] == "token-no-expiry"

    rest._websocket_api = Mock()
    loop = Mock()
    loop.run_until_complete.return_value = True
    with patch("asyncio.get_event_loop", side_effect=RuntimeError), patch(
        "asyncio.new_event_loop", return_value=loop
    ), patch("asyncio.set_event_loop"):
        assert rest.enable_websocket() is True
        rest.disable_websocket()
