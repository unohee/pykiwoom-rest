from unittest.mock import Mock, patch

import pytest

from pykiwoom_rest.chart_api import ChartAPI


@pytest.fixture
def chart():
    with patch.object(ChartAPI, "_get_access_token", return_value="token"):
        return ChartAPI(appkey="key", appsecret="secret", account_no="12345678")


def test_chart_response_helpers_cover_empty_filter_and_limits():
    assert not ChartAPI._date_in_range({}, "dt", "20240101", None)
    assert ChartAPI._filter_chart_response({"output": []}, "dt") == {"output": []}
    assert ChartAPI._filter_chart_response("not-a-dict", "dt", "20240101") == "not-a-dict"
    assert ChartAPI._limit_chart_response({"output": [1, 2]}, count=0) == {"output": [1, 2]}


def test_paginated_minute_stops_for_repeated_next_key_and_empty_page(chart):
    chart.make_tr_request_continuous = Mock(
        side_effect=[
            {"data": {"output2": [{"cntr_tm": "20240102100000"}]}, "cont_yn": "Y", "next_key": "same"},
            {"data": {"output2": [{"cntr_tm": "20240102090000"}]}, "cont_yn": "Y", "next_key": "same"},
        ]
    )
    result = chart.get_minute_chart_paginated("005930", max_pages=5)
    assert len(result["output2"]) == 2
    assert chart.make_tr_request_continuous.call_count == 2

    chart.make_tr_request_continuous = Mock(return_value={"data": {"output2": []}})
    assert chart.get_minute_chart_paginated("005930")["output2"] == []


def test_minute_chart_by_date_handles_missing_response_target_and_non_target(chart):
    chart.make_tr_request_continuous = Mock(return_value={})
    empty = chart.get_minute_chart_with_date("005930", target_date="20240102")
    assert not empty["success"] and empty["pages"] == 1

    chart.make_tr_request_continuous = Mock(
        return_value={
            "data": {"stk_min_pole_chart_qry": [{"cntr_tm": "20240102100000"}, {"cntr_tm": "20240102090000"}]},
            "cont_yn": "N",
            "next_key": "",
        }
    )
    target = chart.get_minute_chart_with_date("005930", target_date="20240102")
    assert target["success"] and target["date_range"]["start"] == "20240102"

    chart.make_tr_request_continuous = Mock(
        return_value={"data": {"stk_min_pole_chart_qry": [{"cntr_tm": "20240102100000"}]}, "cont_yn": "N"}
    )
    all_dates = chart.get_minute_chart_with_date("005930")
    assert all_dates["total"] == 1

    chart.make_tr_request_continuous = Mock(return_value={"data": {"stk_min_pole_chart_qry": []}})
    assert not chart.get_minute_chart_with_date("005930", target_date="20240102")["success"]

    chart.make_tr_request_continuous = Mock(
        return_value={
            "data": {"stk_min_pole_chart_qry": [{"cntr_tm": "20240101100000"}]},
            "cont_yn": "Y",
            "next_key": "next",
        }
    )
    assert not chart.get_minute_chart_with_date("005930", target_date="20240102")["success"]

    chart.make_tr_request_continuous = Mock(
        return_value={
            "data": {"stk_min_pole_chart_qry": [{"cntr_tm": "20240102100000"}]},
            "cont_yn": "Y",
            "next_key": "",
        }
    )
    assert chart.get_minute_chart_with_date("005930", target_date="20240102")["success"]

    chart.make_tr_request_continuous = Mock(
        side_effect=[
            {
                "data": {"stk_min_pole_chart_qry": [{"cntr_tm": "20240102100000"}]},
                "cont_yn": "Y",
                "next_key": "next",
            },
            {
                "data": {"stk_min_pole_chart_qry": [{"cntr_tm": "20240102090000"}]},
                "cont_yn": "N",
                "next_key": "",
            },
        ]
    )
    assert chart.get_minute_chart_with_date("005930", target_date="20240102")["total"] == 2


def test_unified_chart_builds_optional_parameters(chart):
    chart.make_tr_request = Mock(return_value={"ok": True})
    assert chart.get_daily_weekly_monthly_minute_chart(
        "005930", period="T", start_date="20240101", end_date="20240102", interval=5
    ) == {"ok": True}
    assert chart.make_tr_request.call_args.kwargs["data"] == {
        "stk_cd": "005930", "start_date": "20240101", "end_date": "20240102", "period": "T", "interval": "5"
    }
