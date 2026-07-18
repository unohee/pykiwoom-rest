"""
ranking_api.py 모듈 단위 테스트

자동 생성됨 - boost-coverage 스킬
생성일: 2026-01-13
목표: 커버리지 22% → 70%
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from pykiwoom_rest.ranking_api import RankingAPI
from pykiwoom_rest.response_model import APIResponse

OFFICIAL_DOC = Path(__file__).resolve().parents[1] / "docs" / "kiwoom_rest_api_full.md"


def assert_official_api_url(api_id: str, expected_url: str) -> None:
    doc = OFFICIAL_DOC.read_text(encoding="utf-8")
    section_start = doc.index(f"API ID {api_id}")
    section = doc[section_start : section_start + 700]
    assert f"URL {expected_url}" in section


class TestRankingAPI:
    """RankingAPI 클래스 테스트"""

    @pytest.fixture
    def mock_ranking_api(self):
        """모의 RankingAPI 인스턴스"""
        with patch.object(RankingAPI, "_get_access_token", return_value="mock_token"), patch.object(
            RankingAPI, "request"
        ) as mock_request, patch.object(
            RankingAPI, "make_tr_request"
        ) as mock_tr_request:
            mock_request.return_value = APIResponse(
                success=True, data={"rt_cd": "0", "output": [{"stk_cd": "005930"}]}
            )
            mock_tr_request.return_value = {"rt_cd": "0", "output": [{"stk_cd": "005930"}]}
            api = RankingAPI(appkey="test_key", appsecret="test_secret", account_no="12345678")
            api.request = mock_request
            api.make_tr_request = mock_tr_request
            yield api

    @pytest.mark.parametrize("api_id", ["ka10020", "ka10034"])
    def test_ranking_methods_match_official_ranking_endpoint(self, mock_ranking_api, api_id):
        """순위 TR은 공식 문서의 ranking endpoint와 구현 endpoint key가 일치"""
        assert_official_api_url(api_id, "/api/dostk/rkinfo")
        assert mock_ranking_api.ENDPOINTS["ranking"] == "/api/dostk/rkinfo"

    # ========== 시장 코드 변환 테스트 ==========

    def test_get_market_code_all(self, mock_ranking_api):
        """시장 코드 변환 - ALL"""
        assert mock_ranking_api._get_market_code("ALL") == "0000"

    def test_get_market_code_kospi(self, mock_ranking_api):
        """시장 코드 변환 - KOSPI"""
        assert mock_ranking_api._get_market_code("KOSPI") == "0001"

    def test_get_market_code_kosdaq(self, mock_ranking_api):
        """시장 코드 변환 - KOSDAQ"""
        assert mock_ranking_api._get_market_code("KOSDAQ") == "1001"

    def test_get_market_code_unknown(self, mock_ranking_api):
        """시장 코드 변환 - 알 수 없는 시장"""
        with pytest.raises(ValueError):
            mock_ranking_api._get_market_code("UNKNOWN")

    # ========== 호가잔량 관련 테스트 ==========

    def test_get_volume_top_default(self, mock_ranking_api):
        """호가잔량 상위 조회 - 기본값"""
        mock_ranking_api.get_volume_top()

        mock_ranking_api.make_tr_request.assert_called_once()
        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10020"
        assert call_kwargs["endpoint"] == "ranking"
        assert call_kwargs["data"]["FID_INPUT_ISCD"] == "0000"

    def test_get_volume_top_kospi(self, mock_ranking_api):
        """호가잔량 상위 조회 - KOSPI"""
        mock_ranking_api.get_volume_top(market="KOSPI", count=30)

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["data"]["FID_INPUT_ISCD"] == "0001"
        assert call_kwargs["data"]["FID_INPUT_CNT_1"] == "30"

    def test_get_volume_surge_default(self, mock_ranking_api):
        """호가잔량 급증 조회 - 기본값"""
        mock_ranking_api.get_volume_surge()

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10021"

    def test_get_volume_rate_surge_default(self, mock_ranking_api):
        """거래량 증가율 상위 조회 - 기본값"""
        mock_ranking_api.get_volume_rate_surge()

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10022"

    # ========== 거래량/대금 관련 테스트 ==========

    def test_get_trading_volume_surge_default(self, mock_ranking_api):
        """거래대금 급증 조회 - 기본값"""
        mock_ranking_api.get_trading_volume_surge()

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10023"

    def test_get_daily_volume_top_default(self, mock_ranking_api):
        """당일 거래량 상위 조회 - 기본값"""
        mock_ranking_api.get_daily_volume_top()

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10030"

    def test_get_trading_amount_top_default(self, mock_ranking_api):
        """거래대금 상위 조회 - 기본값"""
        mock_ranking_api.get_trading_amount_top()

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10032"

    # ========== 등락률 관련 테스트 ==========

    def test_get_previous_day_rate_top_default(self, mock_ranking_api):
        """전일 대비 등락률 상위 조회 - 기본값"""
        mock_ranking_api.get_previous_day_rate_top()

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10027"

    def test_get_expected_rate_top_default(self, mock_ranking_api):
        """예상체결 등락률 상위 조회 - 기본값"""
        mock_ranking_api.get_expected_rate_top()

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10029"

    # ========== 신용비율 관련 테스트 ==========

    def test_get_credit_ratio_top_default(self, mock_ranking_api):
        """신용비율 상위 조회 - 기본값"""
        mock_ranking_api.get_credit_ratio_top()

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10033"

    # ========== 외국인 관련 테스트 ==========

    def test_get_foreign_period_trading_top_default(self, mock_ranking_api):
        """외인 기간별 매매 상위 조회 - 기본값"""
        mock_ranking_api.get_foreign_period_trading_top()

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10034"

    def test_get_foreign_period_trading_top_custom(self, mock_ranking_api):
        """외인 기간별 매매 상위 조회 - 커스텀 파라미터"""
        mock_ranking_api.get_foreign_period_trading_top(
            market="KOSPI", period="5", count=30
        )

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10034"

    def test_get_foreign_continuous_trading_top(self, mock_ranking_api):
        """외인 연속 순매매 상위 조회"""
        mock_ranking_api.get_foreign_continuous_trading_top()

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10035"

    def test_get_foreign_limit_exhaustion_top(self, mock_ranking_api):
        """외인 한도소진율 상위 조회"""
        mock_ranking_api.get_foreign_limit_exhaustion_top()

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10036"

    def test_get_foreign_window_trading_top(self, mock_ranking_api):
        """외국계 창구 매매 상위 조회"""
        mock_ranking_api.get_foreign_window_trading_top()

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10037"

    # ========== 증권사 관련 테스트 ==========

    def test_get_stock_securities_ranking(self, mock_ranking_api):
        """종목별 증권사 순위 조회"""
        mock_ranking_api.get_stock_securities_ranking(stock_code="005930", data_count="20")

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10038"

    def test_get_securities_trading_top(self, mock_ranking_api):
        """증권사별 매매 상위 조회"""
        mock_ranking_api.get_securities_trading_top()

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10039"

    def test_get_daily_major_traders(self, mock_ranking_api):
        """당일 주요 거래원 조회"""
        mock_ranking_api.get_daily_major_traders(stock_code="005930")

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10040"

    def test_get_net_buy_trader_ranking(self, mock_ranking_api):
        """순매수 거래원 순위 조회"""
        mock_ranking_api.get_net_buy_trader_ranking()

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10042"

    # ========== 기타 순위 테스트 ==========

    def test_get_daily_top_departure(self, mock_ranking_api):
        """당일 상위 이탈 조회"""
        mock_ranking_api.get_daily_top_departure()

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10053"

    def test_get_same_net_trading_ranking(self, mock_ranking_api):
        """동일 순매매 순위 조회"""
        mock_ranking_api.get_same_net_trading_ranking()

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10062"

    def test_get_investor_trading_top(self, mock_ranking_api):
        """투자자별 매매 상위 조회"""
        mock_ranking_api.get_investor_trading_top()

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10065"

    def test_get_overtime_rate_ranking(self, mock_ranking_api):
        """시간외 단일가 등락률 순위 조회"""
        mock_ranking_api.get_overtime_rate_ranking()

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10098"

    def test_get_foreign_institution_trading_top(self, mock_ranking_api):
        """외국인 기관 매매 상위 조회"""
        mock_ranking_api.get_foreign_institution_trading_top()

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka90009"

    # ========== 프로그램 매매 테스트 ==========

    def test_get_hourly_program_trading(self, mock_ranking_api):
        """시간별 프로그램 매매 추이 조회"""
        mock_ranking_api.get_hourly_program_trading(
            stock_code="005930", date="20260113"
        )

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka90008"
        assert call_kwargs["data"]["stk_cd"] == "005930"
        assert call_kwargs["data"]["date"] == "20260113"

    def test_get_hourly_program_trading_with_amount(self, mock_ranking_api):
        """시간별 프로그램 매매 추이 조회 - 금액 기준"""
        mock_ranking_api.get_hourly_program_trading(
            stock_code="005930", date="20260113", amount_or_quantity="1"
        )

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["data"]["amt_qty_tp"] == "1"

    def test_get_hourly_program_trading_with_quantity(self, mock_ranking_api):
        """시간별 프로그램 매매 추이 조회 - 수량 기준"""
        mock_ranking_api.get_hourly_program_trading(
            stock_code="005930", date="20260113", amount_or_quantity="2"
        )

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["data"]["amt_qty_tp"] == "2"

    # ========== 전일 거래량 상위 테스트 ==========

    def test_get_previous_volume_top(self, mock_ranking_api):
        """전일 거래량 상위 조회"""
        mock_ranking_api.get_previous_volume_top()

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10031"

    def test_get_previous_volume_top_kosdaq(self, mock_ranking_api):
        """전일 거래량 상위 조회 - KOSDAQ"""
        mock_ranking_api.get_previous_volume_top(market="KOSDAQ")

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10031"


class TestRankingAPIMarketVariations:
    """시장별 변형 테스트"""

    @pytest.fixture
    def mock_ranking_api(self):
        """모의 RankingAPI 인스턴스"""
        with patch.object(RankingAPI, "_get_access_token", return_value="mock_token"), patch.object(
            RankingAPI, "make_tr_request"
        ) as mock_tr_request:
            mock_tr_request.return_value = {"rt_cd": "0", "output": []}
            api = RankingAPI(appkey="test_key", appsecret="test_secret", account_no="12345678")
            api.make_tr_request = mock_tr_request
            yield api

    @pytest.mark.parametrize(
        "market,expected_code",
        [
            ("ALL", "0000"),
            ("KOSPI", "0001"),
            ("KOSDAQ", "1001"),
        ],
    )
    def test_volume_top_market_variations(self, mock_ranking_api, market, expected_code):
        """호가잔량 상위 - 시장별 변형 테스트"""
        mock_ranking_api.get_volume_top(market=market)

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["data"]["FID_INPUT_ISCD"] == expected_code

    @pytest.mark.parametrize("count", [10, 30, 50, 100])
    def test_volume_top_count_variations(self, mock_ranking_api, count):
        """호가잔량 상위 - 개수 변형 테스트"""
        mock_ranking_api.get_volume_top(count=count)

        call_kwargs = mock_ranking_api.make_tr_request.call_args[1]
        assert call_kwargs["data"]["FID_INPUT_CNT_1"] == str(count)
