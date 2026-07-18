from unittest.mock import Mock, patch

import pytest

from pykiwoom_rest.ranking_api import RankingAPI


@pytest.fixture
def ranking():
    with patch.object(RankingAPI, "_get_access_token", return_value="token"):
        api = RankingAPI(appkey="key", appsecret="secret", account_no="12345678")
    api.make_tr_request = Mock(return_value={"ok": True})
    return api


def test_market_and_count_validation(ranking):
    with pytest.raises(ValueError, match="market"):
        ranking._get_market_code("NYSE")
    for count in (True, 0, 101, "10"):
        with pytest.raises(ValueError, match="count"):
            ranking._validate_count(count)
    with pytest.raises(ValueError, match="period"):
        ranking.get_foreign_period_trading_top(period="2")


def test_remaining_ranking_endpoints_delegate_with_valid_inputs(ranking):
    calls = [
        (ranking.get_overtime_rate_ranking, ()),
        (ranking.get_previous_volume_top, ()),
        (ranking.get_foreign_window_trading_top, ()),
        (ranking.get_stock_securities_ranking, ("005930",)),
        (ranking.get_daily_top_departure, ()),
        (ranking.get_same_net_trading_ranking, ()),
        (ranking.get_foreign_institution_trading_top, ()),
        (ranking.get_bid_ask_volume_top, ()),
        (ranking.get_bid_ask_volume_surge, ()),
        (ranking.get_remaining_volume_surge, ()),
        (ranking.get_expected_execution_rate_top, ()),
        (ranking.get_intraday_investor_trading_top, ()),
        (ranking.get_overtime_single_price_rate_ranking, ()),
    ]
    for method, args in calls:
        assert method(*args) == {"ok": True}
    assert ranking.make_tr_request.call_count == len(calls)


def test_hourly_program_pagination_combines_pages_and_handles_empty(ranking):
    ranking.make_tr_request_continuous = Mock(
        side_effect=[
            {"data": {"output": [{"id": 1}]}, "cont_yn": "Y", "next_key": "next"},
            {"data": {"output": [{"id": 2}]}, "cont_yn": "N", "next_key": ""},
        ]
    )
    result = ranking.get_hourly_program_trading_paginated("005930", "20240101", max_records=5)
    assert result["output"] == [{"id": 1}, {"id": 2}]

    ranking.make_tr_request_continuous = Mock(return_value={"data": {"output": []}})
    assert ranking.get_hourly_program_trading_paginated("005930", "20240101")["output"] == []


def test_hourly_program_pagination_handles_response_shapes_limits_and_retries(ranking, monkeypatch):
    monkeypatch.setattr("time.sleep", lambda _: None)
    ranking.make_tr_request_continuous = Mock(return_value={"data": {"output": {"id": 1}}, "cont_yn": "N"})
    assert ranking.get_hourly_program_trading_paginated("005930", "20240101")["output"] == [{"id": 1}]

    ranking.make_tr_request_continuous = Mock(return_value={"data": {"records": [{"id": 1}, {"id": 2}]}, "cont_yn": "N"})
    assert ranking.get_hourly_program_trading_paginated("005930", "20240101", max_records=1)["output"] == [{"id": 1}]

    ranking.make_tr_request_continuous = Mock(side_effect=[RuntimeError("429"), {"data": [], "cont_yn": "N"}])
    assert ranking.get_hourly_program_trading_paginated("005930", "20240101")["output"] == []

    ranking.make_tr_request_continuous = Mock(side_effect=RuntimeError("broken"))
    with pytest.raises(RuntimeError, match="broken"):
        ranking.get_hourly_program_trading_paginated("005930", "20240101")

    ranking.make_tr_request_continuous = Mock(return_value={"data": {"value": "not records"}, "cont_yn": "N"})
    assert ranking.get_hourly_program_trading_paginated("005930", "20240101")["output"] == []
    ranking.make_tr_request_continuous = Mock(return_value={})
    assert ranking.get_hourly_program_trading_paginated("005930", "20240101")["output"] == []
