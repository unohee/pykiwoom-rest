from unittest.mock import Mock

import pytest

from pykiwoom_rest.api_facade import KiwoomAPIFacade
from pykiwoom_rest.stock_api import StockAPI
from pykiwoom_rest.unified_kiwoom_base import UnifiedKiwoomAPIBase
from pykiwoom_rest.unified_kiwoom_rest import UnifiedKiwoomRest


@pytest.fixture
def rest():
    KiwoomAPIFacade.reset_instance()
    UnifiedKiwoomAPIBase._facade_ref_counts.clear()
    instance = UnifiedKiwoomRest(account_no="12345678", appkey="key", appsecret="secret")
    for api in (instance.stock_api, instance.chart_api, instance.ranking_api, instance.account_api, instance.order_api, instance.sector_api):
        api.close = Mock()
    yield instance
    instance.close()
    KiwoomAPIFacade.reset_instance()
    UnifiedKiwoomAPIBase._facade_ref_counts.clear()


def test_all_public_delegates_and_properties(rest):
    stock = rest.stock_api
    chart = rest.chart_api
    ranking = rest.ranking_api
    account = rest.account_api
    order = rest.order_api
    sector = rest.sector_api
    for api, names in (
        (stock, ["get_stock_basic_info", "get_stock_quote", "get_execution_info", "get_foreign_trading", "get_program_trading_daily", "get_institutional_trading_trend"]),
        (chart, ["get_tick_chart", "get_minute_chart", "get_daily_chart", "get_weekly_chart", "get_monthly_chart", "get_yearly_chart", "get_minute_chart_paginated", "get_minute_chart_with_date"]),
        (ranking, ["get_volume_top", "get_hourly_program_trading", "get_hourly_program_trading_paginated", "get_foreign_period_trading_top", "get_trading_volume_surge", "get_previous_day_rate_top", "get_daily_volume_top", "get_trading_amount_top"]),
        (account, ["get_deposit_detail", "get_account_evaluation", "get_balance_detail", "get_unfilled_orders", "get_executed_orders", "get_account_return"]),
        (order, ["buy_stock", "sell_stock", "modify_order", "cancel_order"]),
        (sector, ["get_sector_current_price", "get_all_sector_index", "get_sector_daily_chart"]),
    ):
        for name in names:
            setattr(api, name, Mock(return_value={name: True}))

    assert rest.get_stock_price("005930") == {"get_stock_basic_info": True}
    assert rest.get_stock_orderbook("005930") == {"get_stock_quote": True}
    assert rest.get_execution_info("005930") == {"get_execution_info": True}
    assert rest.get_foreign_trading("005930") == {"get_foreign_trading": True}
    assert rest.get_program_trading_daily("005930") == {"get_program_trading_daily": True}
    assert rest.get_institutional_trading_trend("005930", "20240101", "20240102") == {"get_institutional_trading_trend": True}
    assert rest.get_tick_chart("005930", 10) == {"get_tick_chart": True}
    assert rest.get_minute_chart("005930", 5, "20240101", "20240102", 20) == {"get_minute_chart": True}
    assert rest.get_daily_chart("005930", "a", "b") == {"get_daily_chart": True}
    assert rest.get_weekly_chart("005930", "a", "b") == {"get_weekly_chart": True}
    assert rest.get_monthly_chart("005930", "a", "b") == {"get_monthly_chart": True}
    assert rest.get_yearly_chart("005930", "a", "b") == {"get_yearly_chart": True}
    assert rest.get_volume_top("KOSPI", 5) == {"get_volume_top": True}
    assert rest.get_hourly_program_trading("005930", "20240101", "2") == {"get_hourly_program_trading": True}
    assert rest.get_hourly_program_trading_paginated("005930", "20240101", "2", 5) == {"get_hourly_program_trading_paginated": True}
    assert rest.get_foreign_top_buy("5") == {"get_foreign_period_trading_top": True}
    assert rest.get_trading_volume_surge() == {"get_trading_volume_surge": True}
    assert rest.get_previous_day_rate_top() == {"get_previous_day_rate_top": True}
    assert rest.get_daily_volume_top() == {"get_daily_volume_top": True}
    assert rest.get_trading_amount_top() == {"get_trading_amount_top": True}
    assert rest.get_deposit_detail() == {"get_deposit_detail": True}
    assert rest.get_account_evaluation() == {"get_account_evaluation": True}
    assert rest.get_balance_detail() == {"get_balance_detail": True}
    assert rest.get_unfilled_orders() == {"get_unfilled_orders": True}
    assert rest.get_executed_orders() == {"get_executed_orders": True}
    assert rest.get_account_return("a", "b") == {"get_account_return": True}
    assert rest.buy_stock("005930", 1) == {"buy_stock": True}
    assert rest.sell_stock("005930", 1) == {"sell_stock": True}
    assert rest.modify_order("1", "005930", 1) == {"modify_order": True}
    assert rest.cancel_order("1", "005930", 1) == {"cancel_order": True}
    assert rest.get_sector_current_price() == {"get_sector_current_price": True}
    assert rest.get_all_sector_index() == {"get_all_sector_index": True}
    assert rest.get_sector_daily_chart("001", "a", "b") == {"get_sector_daily_chart": True}
    assert rest.get_minute_chart_paginated("005930") == {"get_minute_chart_paginated": True}
    assert rest.get_minute_chart_with_date("005930") == {"get_minute_chart_with_date": True}
    assert rest.stock is stock and rest.chart is chart and rest.ranking is ranking and rest.facade is rest.api_base.facade


def test_rest_utilities_stats_connection_reset_and_close(rest):
    rest.api_base.health_check = Mock(return_value={"status": "healthy"})
    rest.api_base.get_stats = Mock(return_value={"base": True})
    rest.api_base.reset_rate_limiter = Mock()
    rest.api_base.facade.get_comprehensive_stats = Mock(return_value={"facade": True})
    assert rest.verify_connection() == {"status": "healthy"}
    assert rest.get_stats()["base"]
    assert rest.get_facade_stats() == {"facade": True}
    rest.reset_rate_limiter()
    rest.api_base.reset_rate_limiter.assert_called_once()
    with rest as entered:
        assert entered is rest
    assert rest._closed


def test_shared_api_attribute_resolution_uses_base_module_and_fallback(rest):
    assert rest.stock_api.account_no == "12345678"
    assert callable(rest.stock_api.get_stock_basic_info)
    assert rest.stock_api.TR_CODES["stock_basic_info"] == "ka10001"
    with pytest.raises(AttributeError):
        rest.stock_api.not_a_real_attribute
    assert rest._create_shared_api(StockAPI).close() is None
