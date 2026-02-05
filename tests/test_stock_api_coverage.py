"""
stock_api.py 모듈 단위 테스트

자동 생성됨 - boost-coverage 스킬
생성일: 2026-01-13
목표: 커버리지 26% → 70%
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from pykiwoom_rest.stock_api import StockAPI
from pykiwoom_rest.response_model import APIResponse


class TestStockAPI:
    """StockAPI 클래스 테스트"""

    @pytest.fixture
    def mock_stock_api(self):
        """모의 StockAPI 인스턴스"""
        with (
            patch.object(StockAPI, "_get_access_token", return_value="mock_token"),
            patch.object(StockAPI, "request") as mock_request,
            patch.object(StockAPI, "make_tr_request") as mock_tr_request,
        ):
            mock_request.return_value = APIResponse(
                success=True, data={"rt_cd": "0", "output": {"stk_cd": "005930"}}
            )
            mock_tr_request.return_value = {"rt_cd": "0", "output": {"stk_cd": "005930"}}
            api = StockAPI(appkey="test_key", appsecret="test_secret", account_no="12345678")
            api.request = mock_request
            api.make_tr_request = mock_tr_request
            yield api

    # ========== 신용매매동향 테스트 ==========

    def test_get_credit_trend_default(self, mock_stock_api):
        """신용매매동향 조회 - 기본값"""
        today = datetime.now().strftime("%Y%m%d")
        result = mock_stock_api.get_credit_trend(stock_code="005930")

        mock_stock_api.request.assert_called_once()
        call_args = mock_stock_api.request.call_args
        assert call_args[1]["endpoint"] == "/api/dostk/stkinfo"
        assert call_args[1]["json_data"]["dt"] == today

    def test_get_credit_trend_custom_date(self, mock_stock_api):
        """신용매매동향 조회 - 날짜 지정"""
        result = mock_stock_api.get_credit_trend(stock_code="005930", date="20260101", query_type="2")

        call_args = mock_stock_api.request.call_args
        assert call_args[1]["json_data"]["dt"] == "20260101"
        assert call_args[1]["json_data"]["qry_tp"] == "2"

    # ========== 일별거래상세 테스트 ==========

    def test_get_daily_trading_detail_default(self, mock_stock_api):
        """일별거래상세 조회 - 기본값"""
        today = datetime.now().strftime("%Y%m%d")
        result = mock_stock_api.get_daily_trading_detail()

        mock_stock_api.request.assert_called_once()
        call_args = mock_stock_api.request.call_args
        assert call_args[1]["json_data"]["strt_dt"] == today

    def test_get_daily_trading_detail_custom_date(self, mock_stock_api):
        """일별거래상세 조회 - 날짜 지정"""
        result = mock_stock_api.get_daily_trading_detail(start_date="20260101")

        call_args = mock_stock_api.request.call_args
        assert call_args[1]["json_data"]["strt_dt"] == "20260101"

    # ========== 신고저가 테스트 ==========

    def test_get_new_high_low_default(self, mock_stock_api):
        """신고저가 조회 - 기본값"""
        result = mock_stock_api.get_new_high_low()

        mock_stock_api.request.assert_called_once()
        call_args = mock_stock_api.request.call_args
        assert call_args[1]["endpoint"] == "/api/dostk/stkinfo"

    def test_get_new_high_low_custom_params(self, mock_stock_api):
        """신고저가 조회 - 커스텀 파라미터"""
        result = mock_stock_api.get_new_high_low(
            period="60",
            new_high_low_type="1",
            exchange_type="01",
            stock_condition="1",
        )

        call_args = mock_stock_api.request.call_args
        json_data = call_args[1]["json_data"]
        # 실제 API는 dt 필드에 period 값을 저장
        assert json_data.get("dt") == "60" or json_data.get("ntl_tp") == "1"

    # ========== 기본 정보 테스트 ==========

    def test_get_stock_basic_info(self, mock_stock_api):
        """주식 기본정보 조회"""
        result = mock_stock_api.get_stock_basic_info("005930")

        mock_stock_api.make_tr_request.assert_called_once()
        call_kwargs = mock_stock_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10001"

    def test_get_stock_quote(self, mock_stock_api):
        """주식 호가 조회"""
        result = mock_stock_api.get_stock_quote("005930")

        mock_stock_api.make_tr_request.assert_called_once()
        call_kwargs = mock_stock_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10004"

    def test_get_execution_info(self, mock_stock_api):
        """체결정보 조회"""
        result = mock_stock_api.get_execution_info("005930")

        mock_stock_api.make_tr_request.assert_called_once()
        call_kwargs = mock_stock_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10003"

    def test_get_stock_member_info(self, mock_stock_api):
        """종목별 투자자별 매매동향 조회"""
        result = mock_stock_api.get_stock_member_info("005930")

        mock_stock_api.make_tr_request.assert_called_once()
        call_kwargs = mock_stock_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10002"
        assert call_kwargs["data"]["FID_INPUT_ISCD"] == "005930"

    # ========== 소요시간 테스트 ==========

    def test_get_stock_elapsed_time(self, mock_stock_api):
        """소요시간 조회"""
        result = mock_stock_api.get_stock_elapsed_time("005930")

        mock_stock_api.make_tr_request.assert_called_once()
        call_kwargs = mock_stock_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10007"

    # ========== 상하한가 테스트 ==========

    def test_get_upper_lower_limit_default(self, mock_stock_api):
        """상하한가 조회 - 기본값"""
        result = mock_stock_api.get_upper_lower_limit()

        mock_stock_api.make_tr_request.assert_called_once()
        call_kwargs = mock_stock_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10017"

    def test_get_upper_lower_limit_kospi(self, mock_stock_api):
        """상하한가 조회 - KOSPI"""
        result = mock_stock_api.get_upper_lower_limit(market="KOSPI")

        call_kwargs = mock_stock_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10017"

    # ========== 가격급등락 테스트 ==========

    def test_get_price_fluctuation_default(self, mock_stock_api):
        """가격급등락 조회 - 기본값"""
        result = mock_stock_api.get_price_fluctuation()

        mock_stock_api.make_tr_request.assert_called_once()
        call_kwargs = mock_stock_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10019"

    # ========== 고저가근접 테스트 ==========

    def test_get_high_low_approach(self, mock_stock_api):
        """고저가근접 조회"""
        result = mock_stock_api.get_high_low_approach("005930")

        mock_stock_api.make_tr_request.assert_called_once()
        call_kwargs = mock_stock_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10018"

    # ========== 거래량집중 테스트 ==========

    def test_get_volume_concentration(self, mock_stock_api):
        """거래량집중 조회"""
        result = mock_stock_api.get_volume_concentration("005930")

        mock_stock_api.make_tr_request.assert_called_once()
        call_kwargs = mock_stock_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10025"

    # ========== 고저PER 테스트 ==========

    def test_get_high_low_per_default(self, mock_stock_api):
        """고저PER 조회 - 기본값"""
        result = mock_stock_api.get_high_low_per()

        mock_stock_api.make_tr_request.assert_called_once()
        call_kwargs = mock_stock_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10026"

    # ========== 당일전일체결 테스트 ==========

    def test_get_current_previous_execution(self, mock_stock_api):
        """당일전일체결 조회"""
        result = mock_stock_api.get_current_previous_execution("005930")

        mock_stock_api.make_tr_request.assert_called_once()
        call_kwargs = mock_stock_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10084"

    # ========== 관심종목정보 테스트 ==========

    def test_get_watchlist_info_default(self, mock_stock_api):
        """관심종목정보 조회 - 기본값"""
        result = mock_stock_api.get_watchlist_info()

        mock_stock_api.make_tr_request.assert_called_once()
        call_kwargs = mock_stock_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10095"

    # ========== 종목리스트 테스트 ==========

    def test_get_stock_list_default(self, mock_stock_api):
        """종목리스트 조회 - 기본값"""
        result = mock_stock_api.get_stock_list()

        mock_stock_api.make_tr_request.assert_called_once()
        call_kwargs = mock_stock_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10099"

    # ========== 종목상세정보 테스트 ==========

    def test_get_stock_info_detail(self, mock_stock_api):
        """종목상세정보 조회"""
        result = mock_stock_api.get_stock_info_detail("005930")

        mock_stock_api.make_tr_request.assert_called_once()
        call_kwargs = mock_stock_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10100"


class TestStockAPIVariousStocks:
    """다양한 종목 테스트"""

    @pytest.fixture
    def mock_stock_api(self):
        """모의 StockAPI 인스턴스"""
        with (
            patch.object(StockAPI, "_get_access_token", return_value="mock_token"),
            patch.object(StockAPI, "make_tr_request") as mock_tr_request,
        ):
            mock_tr_request.return_value = {"rt_cd": "0", "output": {}}
            api = StockAPI(appkey="test_key", appsecret="test_secret", account_no="12345678")
            api.make_tr_request = mock_tr_request
            yield api

    @pytest.mark.parametrize(
        "stock_code",
        [
            "005930",  # 삼성전자
            "000660",  # SK하이닉스
            "035420",  # NAVER
            "373220",  # LG에너지솔루션
            "207940",  # 삼성바이오로직스
        ],
    )
    def test_stock_member_info_various_stocks(self, mock_stock_api, stock_code):
        """종목별 투자자별 매매동향 - 다양한 종목"""
        mock_stock_api.get_stock_member_info(stock_code=stock_code)

        call_kwargs = mock_stock_api.make_tr_request.call_args[1]
        assert call_kwargs["data"]["FID_INPUT_ISCD"] == stock_code

    @pytest.mark.parametrize(
        "stock_code",
        [
            "005930",
            "000660",
            "035420",
        ],
    )
    def test_stock_basic_info_various_stocks(self, mock_stock_api, stock_code):
        """주식기본정보 - 다양한 종목"""
        mock_stock_api.get_stock_basic_info(stock_code=stock_code)

        call_kwargs = mock_stock_api.make_tr_request.call_args[1]
        # 실제 API는 stk_cd 또는 FID_INPUT_ISCD 사용
        assert call_kwargs["data"].get("stk_cd") == stock_code or call_kwargs["data"].get("FID_INPUT_ISCD") == stock_code

    @pytest.mark.parametrize(
        "stock_code",
        [
            "005930",
            "000660",
            "035420",
        ],
    )
    def test_stock_quote_various_stocks(self, mock_stock_api, stock_code):
        """주식호가 - 다양한 종목"""
        mock_stock_api.get_stock_quote(stock_code=stock_code)

        call_kwargs = mock_stock_api.make_tr_request.call_args[1]
        # 실제 API는 stk_cd 키 사용
        assert call_kwargs["data"]["stk_cd"] == stock_code


class TestStockAPIDateParams:
    """날짜 파라미터 테스트"""

    @pytest.fixture
    def mock_stock_api(self):
        """모의 StockAPI 인스턴스"""
        with (
            patch.object(StockAPI, "_get_access_token", return_value="mock_token"),
            patch.object(StockAPI, "request") as mock_request,
        ):
            mock_request.return_value = APIResponse(
                success=True, data={"rt_cd": "0", "output": {}}
            )
            api = StockAPI(appkey="test_key", appsecret="test_secret", account_no="12345678")
            api.request = mock_request
            yield api

    @pytest.mark.parametrize(
        "date",
        [
            "20260101",
            "20251231",
            "20250601",
        ],
    )
    def test_credit_trend_various_dates(self, mock_stock_api, date):
        """신용매매동향 - 다양한 날짜"""
        mock_stock_api.get_credit_trend(stock_code="005930", date=date)

        call_args = mock_stock_api.request.call_args
        assert call_args[1]["json_data"]["dt"] == date

    @pytest.mark.parametrize(
        "query_type",
        ["1", "2"],
    )
    def test_credit_trend_query_types(self, mock_stock_api, query_type):
        """신용매매동향 - 다양한 조회 유형"""
        mock_stock_api.get_credit_trend(stock_code="005930", query_type=query_type)

        call_args = mock_stock_api.request.call_args
        assert call_args[1]["json_data"]["qry_tp"] == query_type
