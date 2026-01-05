"""
investor_api.py 모듈 단위 테스트

자동 생성됨 - boost-coverage 스킬
생성일: 2026-01-05
목표: 커버리지 16% → 70%
"""

from unittest.mock import patch

import pytest

from pykiwoom_rest.investor_api import InvestorAPI
from pykiwoom_rest.response_model import APIResponse


class TestInvestorAPI:
    """InvestorAPI 클래스 테스트"""

    @pytest.fixture
    def mock_investor_api(self):
        """모의 InvestorAPI 인스턴스"""
        with (
            patch.object(InvestorAPI, "_get_access_token", return_value="mock_token"),
            patch.object(InvestorAPI, "request") as mock_request,
        ):
            mock_request.return_value = APIResponse(
                success=True, data={"rt_cd": "0", "output": {"test": "data"}}
            )
            api = InvestorAPI(appkey="test_key", appsecret="test_secret", account_no="12345678")
            api.request = mock_request
            yield api

    def test_get_foreign_trading_success(self, mock_investor_api):
        """외국인 매매동향 조회 성공 케이스"""
        # Act
        result = mock_investor_api.get_foreign_trading("005930")

        # Assert
        assert result.success
        assert result.data["rt_cd"] == "0"
        mock_investor_api.request.assert_called_once()
        call_args = mock_investor_api.request.call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["endpoint"] == "/api/dostk/frgnistt"
        assert call_args[1]["json_data"]["stk_cd"] == "005930"

    def test_get_stock_investor_trading_default_dates(self, mock_investor_api):
        """투자자별 매매동향 - 기본 날짜 사용"""
        # Act
        result = mock_investor_api.get_stock_investor_trading()

        # Assert
        assert result.success
        call_args = mock_investor_api.request.call_args
        json_data = call_args[1]["json_data"]

        # 날짜 자동 생성 확인
        assert "strt_dt" in json_data
        assert "end_dt" in json_data
        assert len(json_data["strt_dt"]) == 8  # YYYYMMDD
        assert len(json_data["end_dt"]) == 8

    def test_get_stock_investor_trading_custom_params(self, mock_investor_api):
        """투자자별 매매동향 - 커스텀 파라미터"""
        # Arrange
        start_date = "20250101"
        end_date = "20250131"

        # Act
        result = mock_investor_api.get_stock_investor_trading(
            start_date=start_date,
            end_date=end_date,
            trade_type="1",
            market_type="001",
            investor_type="9000",
        )

        # Assert
        assert result.success
        call_args = mock_investor_api.request.call_args
        json_data = call_args[1]["json_data"]

        assert json_data["strt_dt"] == start_date
        assert json_data["end_dt"] == end_date
        assert json_data["trde_tp"] == "1"
        assert json_data["mrkt_tp"] == "001"
        assert json_data["invsr_tp"] == "9000"

    def test_get_stock_member_trading(self, mock_investor_api):
        """기관별 매매동향 조회"""
        # Act
        result = mock_investor_api.get_stock_member_trading("005930")

        # Assert
        assert result.success
        mock_investor_api.request.assert_called_once()

    def test_get_institutional_trading_trend(self, mock_investor_api):
        """기관 매매 추이 조회"""
        # Act
        result = mock_investor_api.get_institutional_trading_trend("005930")

        # Assert
        assert result.success
        call_args = mock_investor_api.request.call_args
        json_data = call_args[1]["json_data"]

        assert json_data["stk_cd"] == "005930"
        assert "strt_dt" in json_data
        assert "end_dt" in json_data

    def test_get_institutional_foreign_consecutive_trading_all_market(self, mock_investor_api):
        """기관외국인 연속매매 - 전체 시장"""
        # Act
        result = mock_investor_api.get_institutional_foreign_consecutive_trading(market="ALL")

        # Assert
        assert result is not None  # Returns response.data which is dict
        call_args = mock_investor_api.request.call_args
        json_data = call_args[1]["json_data"]

        assert json_data["FID_COND_MRKT_DIV_CODE"] == "J"

    def test_get_institutional_foreign_consecutive_trading_kosdaq(self, mock_investor_api):
        """기관외국인 연속매매 - 코스닥"""
        # Act
        mock_investor_api.get_institutional_foreign_consecutive_trading(market="KOSDAQ")

        # Assert
        call_args = mock_investor_api.request.call_args
        json_data = call_args[1]["json_data"]

        assert json_data["FID_COND_MRKT_DIV_CODE"] == "Q"

    def test_get_institutional_request(self, mock_investor_api):
        """기관 요청 정보 조회"""
        # Act
        result = mock_investor_api.get_institutional_request("005930")

        # Assert
        assert result.success
        call_args = mock_investor_api.request.call_args

        assert call_args[1]["endpoint"] == "/api/dostk/frgnistt"
        assert call_args[1]["json_data"]["stk_cd"] == "005930"

    def test_get_institutional_daily_trading(self, mock_investor_api):
        """일별 기관 매매동향 조회"""
        # Act
        result = mock_investor_api.get_institutional_daily_trading("005930")

        # Assert
        assert result is not None
        call_args = mock_investor_api.request.call_args

        assert call_args[1]["endpoint"] == "/api/dostk/mrkcond"

    def test_get_sector_code_list(self, mock_investor_api):
        """업종 코드 리스트 조회"""
        # Act
        result = mock_investor_api.get_sector_code_list()

        # Assert
        assert result is not None
        call_args = mock_investor_api.request.call_args

        assert call_args[1]["endpoint"] == "/api/dostk/stkinfo"
        assert call_args[1]["json_data"] == {}

    def test_get_member_company_list(self, mock_investor_api):
        """회원사 리스트 조회"""
        # Act
        result = mock_investor_api.get_member_company_list()

        # Assert
        assert result is not None
        call_args = mock_investor_api.request.call_args

        assert call_args[1]["endpoint"] == "/api/dostk/stkinfo"


class TestInvestorAPIErrorCases:
    """InvestorAPI 에러 케이스 테스트"""

    @pytest.fixture
    def failing_investor_api(self):
        """에러 발생 API"""
        with (
            patch.object(InvestorAPI, "_get_access_token", return_value="mock_token"),
            patch.object(InvestorAPI, "request") as mock_request,
        ):
            mock_request.return_value = APIResponse(
                success=False, data={}, error={"message": "API Error", "code": "500"}
            )
            api = InvestorAPI(appkey="test_key", appsecret="test_secret", account_no="12345678")
            api.request = mock_request
            yield api

    def test_get_foreign_trading_failure(self, failing_investor_api):
        """외국인 매매동향 조회 실패"""
        # Act
        result = failing_investor_api.get_foreign_trading("005930")

        # Assert
        assert not result.success
        assert result.error["code"] == "500"

    def test_get_stock_investor_trading_failure(self, failing_investor_api):
        """투자자별 매매동향 조회 실패"""
        # Act
        result = failing_investor_api.get_stock_investor_trading()

        # Assert
        assert not result.success
