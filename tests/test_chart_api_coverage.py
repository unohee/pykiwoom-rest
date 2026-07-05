"""
chart_api.py 모듈 단위 테스트

자동 생성됨 - boost-coverage 스킬
생성일: 2026-01-13
목표: 커버리지 18% → 70%
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from pykiwoom_rest.chart_api import ChartAPI

OFFICIAL_DOC = Path(__file__).resolve().parents[1] / "docs" / "kiwoom_rest_api_full.md"


def assert_official_api_url(api_id: str, expected_url: str) -> None:
    doc = OFFICIAL_DOC.read_text(encoding="utf-8")
    section_start = doc.index(f"API ID {api_id}")
    section = doc[section_start : section_start + 700]
    assert f"URL {expected_url}" in section


class TestChartAPI:
    """ChartAPI 클래스 테스트"""

    @pytest.fixture
    def mock_chart_api(self):
        """모의 ChartAPI 인스턴스"""
        with patch.object(ChartAPI, "_get_access_token", return_value="mock_token"), patch.object(
            ChartAPI, "make_tr_request"
        ) as mock_tr_request, patch.object(
            ChartAPI, "make_tr_request_continuous"
        ) as mock_continuous:
            mock_tr_request.return_value = {
                "rt_cd": "0",
                "output": [{"stck_bsop_date": "20260113", "stck_clpr": "70000"}],
            }
            mock_continuous.return_value = {
                "rt_cd": "0",
                "output": [{"stck_bsop_date": "20260113", "stck_clpr": "70000"}],
                "cont_yn": "N",
            }
            api = ChartAPI(appkey="test_key", appsecret="test_secret", account_no="12345678")
            api.make_tr_request = mock_tr_request
            api.make_tr_request_continuous = mock_continuous
            yield api

    @pytest.mark.parametrize("api_id", ["ka10081", "ka10082", "ka10083", "ka10094"])
    def test_stock_chart_methods_match_official_chart_endpoint(self, mock_chart_api, api_id):
        """주식 차트 TR은 공식 문서의 chart endpoint와 구현 endpoint key가 일치"""
        assert_official_api_url(api_id, "/api/dostk/chart")
        assert mock_chart_api.ENDPOINTS["chart"] == "/api/dostk/chart"

    # ========== 틱 차트 테스트 ==========

    def test_get_tick_chart_default(self, mock_chart_api):
        """틱 차트 조회 - 기본값"""
        mock_chart_api.get_tick_chart("005930")

        mock_chart_api.make_tr_request.assert_called_once()
        call_kwargs = mock_chart_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10079"
        assert call_kwargs["endpoint"] == "chart"
        assert call_kwargs["data"] == {
            "stk_cd": "005930",
            "tic_scope": "1",
            "upd_stkpc_tp": "1",
        }

    def test_get_tick_chart_custom_count(self, mock_chart_api):
        """틱 차트 count 호환성 인자는 공식 요청 body에 포함하지 않음"""
        mock_chart_api.get_tick_chart("005930", count=50)

        call_kwargs = mock_chart_api.make_tr_request.call_args[1]
        assert call_kwargs["data"] == {
            "stk_cd": "005930",
            "tic_scope": "1",
            "upd_stkpc_tp": "1",
        }

    # ========== 분봉 차트 테스트 ==========

    def test_get_minute_chart_default(self, mock_chart_api):
        """분봉 차트 조회 - 기본값"""
        mock_chart_api.get_minute_chart("005930")

        mock_chart_api.make_tr_request.assert_called_once()
        call_kwargs = mock_chart_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10080"
        assert call_kwargs["data"]["stk_cd"] == "005930"
        assert call_kwargs["data"]["tic_scope"] == "1"

    def test_get_minute_chart_5min_interval(self, mock_chart_api):
        """분봉 차트 조회 - 5분봉"""
        mock_chart_api.get_minute_chart("005930", interval=5)

        call_kwargs = mock_chart_api.make_tr_request.call_args[1]
        assert call_kwargs["data"]["tic_scope"] == "5"

    def test_get_minute_chart_with_dates(self, mock_chart_api):
        """분봉 날짜 범위는 연속조회 기반 pagination으로 위임"""
        with patch.object(
            mock_chart_api, "get_minute_chart_paginated", return_value={"output2": []}
        ) as mock_paginated:
            mock_chart_api.get_minute_chart(
                "005930",
                interval=5,
                start_date="20260101",
                end_date="20260113",
                count=200,
            )

        mock_paginated.assert_called_once_with(
            stock_code="005930",
            interval=5,
            start_date="20260101",
            end_date="20260113",
            max_records=200,
        )

    def test_get_minute_chart_count_is_client_side_compatibility(self, mock_chart_api):
        """분봉 count 호환성 인자는 공식 요청 body에 포함하지 않음"""
        mock_chart_api.get_minute_chart("005930", count=500)

        call_kwargs = mock_chart_api.make_tr_request.call_args[1]
        assert "req_cnt" not in call_kwargs["data"]

    @pytest.mark.parametrize("interval", [1, 3, 5, 10, 15, 30, 60])
    def test_get_minute_chart_all_intervals(self, mock_chart_api, interval):
        """분봉 차트 조회 - 모든 분봉 간격"""
        mock_chart_api.get_minute_chart("005930", interval=interval)

        call_kwargs = mock_chart_api.make_tr_request.call_args[1]
        assert call_kwargs["data"]["tic_scope"] == str(interval)

    # ========== 일봉 차트 테스트 ==========

    def test_get_daily_chart_default(self, mock_chart_api):
        """일봉 차트 조회 - 기본값"""
        mock_chart_api.get_daily_chart("005930")

        mock_chart_api.make_tr_request.assert_called_once()
        call_kwargs = mock_chart_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10081"
        assert call_kwargs["data"]["stk_cd"] == "005930"

    def test_get_daily_chart_with_dates(self, mock_chart_api):
        """일봉 차트 조회 - 기준일 지정"""
        mock_chart_api.make_tr_request.return_value = {
            "stk_dt_pole_chart_qry": [
                {"dt": "20260113", "cur_prc": "70000"},
                {"dt": "20250101", "cur_prc": "60000"},
            ]
        }
        mock_chart_api.get_daily_chart(
            "005930",
            start_date="20260101",
            end_date="20260113",
        )

        call_kwargs = mock_chart_api.make_tr_request.call_args[1]
        assert call_kwargs["data"] == {
            "stk_cd": "005930",
            "base_dt": "20260113",
            "upd_stkpc_tp": "1",
        }
        result = mock_chart_api.get_daily_chart(
            "005930",
            start_date="20260101",
            end_date="20260113",
        )
        assert result["stk_dt_pole_chart_qry"] == [{"dt": "20260113", "cur_prc": "70000"}]

    def test_get_daily_chart_custom_count(self, mock_chart_api):
        """일봉 count 호환성 인자는 공식 요청 body에 포함하지 않음"""
        mock_chart_api.get_daily_chart("005930", count=200)

        call_kwargs = mock_chart_api.make_tr_request.call_args[1]
        assert "req_cnt" not in call_kwargs["data"]

    # ========== 주봉 차트 테스트 ==========

    def test_get_weekly_chart_default(self, mock_chart_api):
        """주봉 차트 조회 - 기본값"""
        mock_chart_api.get_weekly_chart("005930")

        mock_chart_api.make_tr_request.assert_called_once()
        call_kwargs = mock_chart_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10082"

    def test_get_weekly_chart_with_dates(self, mock_chart_api):
        """주봉 차트 조회 - 날짜 지정"""
        mock_chart_api.get_weekly_chart(
            "005930",
            start_date="20250101",
            end_date="20260113",
        )

        call_kwargs = mock_chart_api.make_tr_request.call_args[1]
        assert call_kwargs["data"] == {
            "stk_cd": "005930",
            "base_dt": "20260113",
            "upd_stkpc_tp": "1",
        }

    # ========== 월봉 차트 테스트 ==========

    def test_get_monthly_chart_default(self, mock_chart_api):
        """월봉 차트 조회 - 기본값"""
        mock_chart_api.get_monthly_chart("005930")

        mock_chart_api.make_tr_request.assert_called_once()
        call_kwargs = mock_chart_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10083"

    def test_get_monthly_chart_with_dates(self, mock_chart_api):
        """월봉 차트 조회 - 날짜 지정"""
        mock_chart_api.get_monthly_chart(
            "005930",
            start_date="20200101",
            end_date="20260113",
        )

        call_kwargs = mock_chart_api.make_tr_request.call_args[1]
        assert call_kwargs["data"] == {
            "stk_cd": "005930",
            "base_dt": "20260113",
            "upd_stkpc_tp": "1",
        }

    # ========== 년봉 차트 테스트 ==========

    def test_get_yearly_chart_default(self, mock_chart_api):
        """년봉 차트 조회 - 기본값"""
        mock_chart_api.get_yearly_chart("005930")

        mock_chart_api.make_tr_request.assert_called_once()
        call_kwargs = mock_chart_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10094"

    def test_get_yearly_chart_with_dates(self, mock_chart_api):
        """년봉 차트 조회 - 날짜 지정"""
        mock_chart_api.get_yearly_chart(
            "005930",
            start_date="20100101",
            end_date="20260113",
        )

        call_kwargs = mock_chart_api.make_tr_request.call_args[1]
        assert call_kwargs["data"] == {
            "stk_cd": "005930",
            "base_dt": "20260113",
            "upd_stkpc_tp": "1",
        }


class TestChartAPIPagination:
    """차트 API 페이지네이션 테스트"""

    @pytest.fixture
    def mock_chart_api_pagination(self):
        """페이지네이션용 모의 ChartAPI"""
        with patch.object(ChartAPI, "_get_access_token", return_value="mock_token"), patch.object(
            ChartAPI, "make_tr_request_continuous"
        ) as mock_request:
            mock_request.return_value = {
                "data": {
                    "return_code": 0,
                    "rt_cd": "0",
                    "stk_min_pole_chart_qry": [
                        {"cntr_tm": "20260113100000", "cur_prc": "70000"}
                    ] * 50,
                },
                "cont_yn": "N",
                "next_key": "",
            }
            api = ChartAPI(appkey="test_key", appsecret="test_secret", account_no="12345678")
            api.make_tr_request_continuous = mock_request
            yield api

    def test_get_minute_chart_paginated_basic(self, mock_chart_api_pagination):
        """분봉 차트 페이지네이션 - 기본"""
        result = mock_chart_api_pagination.get_minute_chart_paginated(
            stock_code="005930",
            interval=5,
            max_records=50,
        )

        # 결과 확인 - stk_min_pole_chart_qry 또는 output2 키 확인
        assert "stk_min_pole_chart_qry" in result or "output2" in result
        assert mock_chart_api_pagination.make_tr_request_continuous.call_count == 1

    def test_get_minute_chart_paginated_with_max_records(self, mock_chart_api_pagination):
        """분봉 차트 페이지네이션 - 최대 레코드 제한"""
        result = mock_chart_api_pagination.get_minute_chart_paginated(
            stock_code="005930",
            interval=5,
            max_records=50,
        )

        # 결과 확인 - 데이터 키 존재 확인
        data = result.get("stk_min_pole_chart_qry") or result.get("output2") or []
        assert len(data) <= 50

    def test_get_minute_chart_paginated_follows_next_key_and_trims(self, mock_chart_api_pagination):
        """분봉 페이지네이션은 next-key 연속조회로 다음 페이지를 요청하고 max_records로 자름"""
        first_page = [{"cntr_tm": f"2026011310{i:04d}", "cur_prc": str(i)} for i in range(100)]
        second_page = [{"cntr_tm": f"2026011309{i:04d}", "cur_prc": str(i)} for i in range(100)]
        mock_chart_api_pagination.make_tr_request_continuous.side_effect = [
            {
                "data": {"return_code": 0, "stk_min_pole_chart_qry": first_page},
                "cont_yn": "Y",
                "next_key": "NEXT123",
            },
            {
                "data": {"return_code": 0, "stk_min_pole_chart_qry": second_page},
                "cont_yn": "N",
                "next_key": "",
            },
        ]

        result = mock_chart_api_pagination.get_minute_chart_paginated(
            stock_code="005930",
            interval=5,
            max_records=150,
        )

        assert len(result["output2"]) == 150
        first_call = mock_chart_api_pagination.make_tr_request_continuous.call_args_list[0].kwargs
        second_call = mock_chart_api_pagination.make_tr_request_continuous.call_args_list[1].kwargs
        assert first_call["cont_yn"] == "N"
        assert first_call["next_key"] == ""
        assert second_call["cont_yn"] == "Y"
        assert second_call["next_key"] == "NEXT123"

    def test_get_minute_chart_paginated_filters_start_and_end_date(
        self, mock_chart_api_pagination
    ):
        """분봉 pagination은 cntr_tm 기준 start/end 날짜 범위를 보존"""
        mock_chart_api_pagination.make_tr_request_continuous.side_effect = [
            {
                "data": {
                    "return_code": 0,
                    "stk_min_pole_chart_qry": [
                        {"cntr_tm": "20260114100000", "cur_prc": "71000"},
                        {"cntr_tm": "20260113100000", "cur_prc": "70000"},
                    ],
                },
                "cont_yn": "Y",
                "next_key": "NEXT123",
            },
            {
                "data": {
                    "return_code": 0,
                    "stk_min_pole_chart_qry": [
                        {"cntr_tm": "20260112100000", "cur_prc": "69000"},
                        {"cntr_tm": "20260111100000", "cur_prc": "68000"},
                    ],
                },
                "cont_yn": "N",
                "next_key": "",
            },
        ]

        result = mock_chart_api_pagination.get_minute_chart_paginated(
            stock_code="005930",
            interval=5,
            start_date="20260112",
            end_date="20260113",
            max_records=10,
        )

        assert result["output2"] == [
            {"cntr_tm": "20260113100000", "cur_prc": "70000"},
            {"cntr_tm": "20260112100000", "cur_prc": "69000"},
        ]


class TestChartAPIStockCodes:
    """다양한 종목코드 테스트"""

    @pytest.fixture
    def mock_chart_api(self):
        """모의 ChartAPI 인스턴스"""
        with patch.object(ChartAPI, "_get_access_token", return_value="mock_token"), patch.object(
            ChartAPI, "make_tr_request"
        ) as mock_tr_request:
            mock_tr_request.return_value = {"rt_cd": "0", "output": []}
            api = ChartAPI(appkey="test_key", appsecret="test_secret", account_no="12345678")
            api.make_tr_request = mock_tr_request
            yield api

    @pytest.mark.parametrize(
        "stock_code",
        [
            "005930",  # 삼성전자
            "000660",  # SK하이닉스
            "035420",  # NAVER
            "373220",  # LG에너지솔루션
        ],
    )
    def test_tick_chart_various_stocks(self, mock_chart_api, stock_code):
        """틱 차트 - 다양한 종목"""
        mock_chart_api.get_tick_chart(stock_code)

        call_kwargs = mock_chart_api.make_tr_request.call_args[1]
        assert call_kwargs["data"]["stk_cd"] == stock_code

    @pytest.mark.parametrize(
        "stock_code",
        [
            "005930",
            "000660",
            "035420",
        ],
    )
    def test_minute_chart_various_stocks(self, mock_chart_api, stock_code):
        """분봉 차트 - 다양한 종목"""
        mock_chart_api.get_minute_chart(stock_code)

        call_kwargs = mock_chart_api.make_tr_request.call_args[1]
        assert call_kwargs["data"]["stk_cd"] == stock_code

    @pytest.mark.parametrize(
        "stock_code",
        [
            "005930",
            "000660",
            "035420",
        ],
    )
    def test_daily_chart_various_stocks(self, mock_chart_api, stock_code):
        """일봉 차트 - 다양한 종목"""
        mock_chart_api.get_daily_chart(stock_code)

        call_kwargs = mock_chart_api.make_tr_request.call_args[1]
        assert call_kwargs["data"]["stk_cd"] == stock_code
