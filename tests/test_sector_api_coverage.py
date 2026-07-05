"""
sector_api.py 모듈 단위 테스트

자동 생성됨 - boost-coverage 스킬
생성일: 2026-01-13
목표: 커버리지 20% → 70%
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from pykiwoom_rest.sector_api import SectorAPI

OFFICIAL_DOC = Path(__file__).resolve().parents[1] / "docs" / "kiwoom_rest_api_full.md"


def assert_official_api_url(api_id: str, expected_url: str) -> None:
    doc = OFFICIAL_DOC.read_text(encoding="utf-8")
    section_start = doc.index(f"API ID {api_id}")
    section = doc[section_start : section_start + 700]
    assert f"URL {expected_url}" in section


class TestSectorAPI:
    """SectorAPI 클래스 테스트"""

    @pytest.fixture
    def mock_sector_api(self):
        """모의 SectorAPI 인스턴스"""
        with patch.object(SectorAPI, "_get_access_token", return_value="mock_token"), patch.object(
            SectorAPI, "make_tr_request"
        ) as mock_tr_request:
            mock_tr_request.return_value = {
                "rt_cd": "0",
                "output": {"sect_cd": "0001", "cur_prc": "2800"},
            }
            api = SectorAPI(appkey="test_key", appsecret="test_secret", account_no="12345678")
            api.make_tr_request = mock_tr_request
            yield api

    @pytest.mark.parametrize("api_id", ["ka20004", "ka20005", "ka20006"])
    def test_sector_chart_methods_match_official_chart_endpoint(self, mock_sector_api, api_id):
        """업종 차트 TR은 공식 문서의 chart endpoint와 구현 endpoint key가 일치"""
        assert_official_api_url(api_id, "/api/dostk/chart")
        assert mock_sector_api.ENDPOINTS["chart"] == "/api/dostk/chart"

    # ========== 업종 현재가 테스트 ==========

    def test_get_sector_current_price_default(self, mock_sector_api):
        """업종 현재가 조회 - 기본값"""
        mock_sector_api.get_sector_current_price()

        mock_sector_api.make_tr_request.assert_called_once()
        call_kwargs = mock_sector_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka20001"
        assert call_kwargs["endpoint"] == "sector"
        assert call_kwargs["data"]["sect_cd"] == "0001"

    def test_get_sector_current_price_kosdaq(self, mock_sector_api):
        """업종 현재가 조회 - KOSDAQ"""
        mock_sector_api.get_sector_current_price(sector_code="1001")

        call_kwargs = mock_sector_api.make_tr_request.call_args[1]
        assert call_kwargs["data"]["sect_cd"] == "1001"

    # ========== 업종별 주가 테스트 ==========

    def test_get_sector_stock_price_default(self, mock_sector_api):
        """업종별 주가 조회 - 기본값"""
        mock_sector_api.get_sector_stock_price()

        mock_sector_api.make_tr_request.assert_called_once()
        call_kwargs = mock_sector_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka20002"

    def test_get_sector_stock_price_custom(self, mock_sector_api):
        """업종별 주가 조회 - 커스텀 업종"""
        mock_sector_api.get_sector_stock_price(sector_code="0016")

        call_kwargs = mock_sector_api.make_tr_request.call_args[1]
        assert call_kwargs["data"]["sect_cd"] == "0016"

    # ========== 전업종지수 테스트 ==========

    def test_get_all_sector_index(self, mock_sector_api):
        """전업종지수 조회"""
        mock_sector_api.get_all_sector_index()

        mock_sector_api.make_tr_request.assert_called_once()
        call_kwargs = mock_sector_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka20003"

    # ========== 업종 틱차트 테스트 ==========

    def test_get_sector_tick_chart_default(self, mock_sector_api):
        """업종 틱차트 조회 - 기본값"""
        mock_sector_api.get_sector_tick_chart(sector_code="001")

        mock_sector_api.make_tr_request.assert_called_once()
        call_kwargs = mock_sector_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka20004"
        assert call_kwargs["endpoint"] == "chart"
        assert call_kwargs["data"]["inds_cd"] == "001"
        assert call_kwargs["data"]["tic_scope"] == "1"

    def test_get_sector_tick_chart_4digit_code(self, mock_sector_api):
        """업종 틱차트 조회 - 4자리 코드 자동 변환"""
        mock_sector_api.get_sector_tick_chart(sector_code="0001")

        call_kwargs = mock_sector_api.make_tr_request.call_args[1]
        assert call_kwargs["data"]["inds_cd"] == "001"

    @pytest.mark.parametrize("tick_scope", [1, 3, 5, 10, 30])
    def test_get_sector_tick_chart_scopes(self, mock_sector_api, tick_scope):
        """업종 틱차트 조회 - 다양한 틱 범위"""
        mock_sector_api.get_sector_tick_chart(sector_code="001", tick_scope=tick_scope)

        call_kwargs = mock_sector_api.make_tr_request.call_args[1]
        assert call_kwargs["data"]["tic_scope"] == str(tick_scope)

    # ========== 업종 분봉 테스트 ==========

    def test_get_sector_minute_chart_default(self, mock_sector_api):
        """업종 분봉 조회 - 기본값"""
        mock_sector_api.get_sector_minute_chart(sector_code="001")

        mock_sector_api.make_tr_request.assert_called_once()
        call_kwargs = mock_sector_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka20005"

    @pytest.mark.parametrize("interval", [1, 3, 5, 10, 30])
    def test_get_sector_minute_chart_intervals(self, mock_sector_api, interval):
        """업종 분봉 조회 - 공식 지원 분봉 간격"""
        mock_sector_api.get_sector_minute_chart(sector_code="001", interval=interval)

        call_kwargs = mock_sector_api.make_tr_request.call_args[1]
        assert call_kwargs["data"]["tic_scope"] == str(interval)

    @pytest.mark.parametrize("interval", [15, 45, 60, "bad"])
    def test_get_sector_minute_chart_rejects_invalid_interval(
        self, mock_sector_api, interval
    ):
        """업종 분봉은 공식 지원하지 않는 간격을 거부"""
        with pytest.raises(ValueError, match="interval must be one of"):
            mock_sector_api.get_sector_minute_chart(sector_code="001", interval=interval)

    # ========== 업종 일봉 테스트 ==========

    def test_get_sector_daily_chart_default(self, mock_sector_api):
        """업종 일봉 조회 - 기본값"""
        mock_sector_api.get_sector_daily_chart(sector_code="001")

        mock_sector_api.make_tr_request.assert_called_once()
        call_kwargs = mock_sector_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka20006"

    def test_get_sector_daily_chart_with_date(self, mock_sector_api):
        """업종 일봉 조회 - 날짜 지정"""
        mock_sector_api.get_sector_daily_chart(
            sector_code="001", base_date="20260101"
        )

        call_kwargs = mock_sector_api.make_tr_request.call_args[1]
        assert call_kwargs["data"]["base_dt"] == "20260101"

    # ========== 업종 주봉 테스트 ==========

    def test_get_sector_weekly_chart_default(self, mock_sector_api):
        """업종 주봉 조회 - 기본값"""
        mock_sector_api.get_sector_weekly_chart(sector_code="001")

        mock_sector_api.make_tr_request.assert_called_once()
        call_kwargs = mock_sector_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka20007"

    def test_get_sector_weekly_chart_with_date(self, mock_sector_api):
        """업종 주봉 조회 - 날짜 지정"""
        mock_sector_api.get_sector_weekly_chart(
            sector_code="001", base_date="20260101"
        )

        call_kwargs = mock_sector_api.make_tr_request.call_args[1]
        assert call_kwargs["data"]["base_dt"] == "20260101"

    # ========== 업종 월봉 테스트 ==========

    def test_get_sector_monthly_chart_default(self, mock_sector_api):
        """업종 월봉 조회 - 기본값"""
        mock_sector_api.get_sector_monthly_chart(sector_code="001")

        mock_sector_api.make_tr_request.assert_called_once()
        call_kwargs = mock_sector_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka20008"

    def test_get_sector_monthly_chart_with_date(self, mock_sector_api):
        """업종 월봉 조회 - 날짜 지정"""
        mock_sector_api.get_sector_monthly_chart(
            sector_code="001", base_date="20260101"
        )

        call_kwargs = mock_sector_api.make_tr_request.call_args[1]
        assert call_kwargs["data"]["base_dt"] == "20260101"

    # ========== 업종 년봉 테스트 ==========

    def test_get_sector_yearly_chart_default(self, mock_sector_api):
        """업종 년봉 조회 - 기본값"""
        mock_sector_api.get_sector_yearly_chart(sector_code="001")

        mock_sector_api.make_tr_request.assert_called_once()
        call_kwargs = mock_sector_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka20019"

    def test_get_sector_yearly_chart_with_date(self, mock_sector_api):
        """업종 년봉 조회 - 날짜 지정"""
        mock_sector_api.get_sector_yearly_chart(
            sector_code="001", base_date="20260101"
        )

        call_kwargs = mock_sector_api.make_tr_request.call_args[1]
        assert call_kwargs["data"]["base_dt"] == "20260101"

    # ========== 업종 현재가 일별 테스트 ==========

    def test_get_sector_daily_current_default(self, mock_sector_api):
        """업종 현재가 일별 조회 - 기본값"""
        mock_sector_api.get_sector_daily_current(sector_code="001")

        mock_sector_api.make_tr_request.assert_called_once()
        call_kwargs = mock_sector_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka20009"

    # ========== 업종별 투자자 매매 테스트 ==========

    def test_get_sector_investor_trading_default(self, mock_sector_api):
        """업종별 투자자 매매 조회 - 기본값"""
        mock_sector_api.get_sector_investor_trading(sector_code="001")

        mock_sector_api.make_tr_request.assert_called_once()
        call_kwargs = mock_sector_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10051"

    # ========== 업종 프로그램 매매 테스트 ==========

    def test_get_sector_program_trading_default(self, mock_sector_api):
        """업종 프로그램 매매 조회 - 기본값"""
        mock_sector_api.get_sector_program_trading(sector_code="001")

        mock_sector_api.make_tr_request.assert_called_once()
        call_kwargs = mock_sector_api.make_tr_request.call_args[1]
        assert call_kwargs["tr_code"] == "ka10010"


class TestSectorAPISectorCodes:
    """업종 코드 변형 테스트"""

    @pytest.fixture
    def mock_sector_api(self):
        """모의 SectorAPI 인스턴스"""
        with patch.object(SectorAPI, "_get_access_token", return_value="mock_token"), patch.object(
            SectorAPI, "make_tr_request"
        ) as mock_tr_request:
            mock_tr_request.return_value = {"rt_cd": "0", "output": {}}
            api = SectorAPI(appkey="test_key", appsecret="test_secret", account_no="12345678")
            api.make_tr_request = mock_tr_request
            yield api

    @pytest.mark.parametrize(
        "sector_code,description",
        [
            ("0001", "코스피"),
            ("1001", "코스닥"),
            ("0016", "반도체"),
            ("0025", "은행"),
            ("0028", "증권"),
        ],
    )
    def test_sector_current_price_various_sectors(
        self, mock_sector_api, sector_code, description
    ):
        """업종 현재가 - 다양한 업종"""
        mock_sector_api.get_sector_current_price(sector_code=sector_code)

        call_kwargs = mock_sector_api.make_tr_request.call_args[1]
        assert call_kwargs["data"]["sect_cd"] == sector_code

    @pytest.mark.parametrize(
        "input_code,expected_code",
        [
            ("0001", "001"),  # 4자리 → 3자리
            ("001", "001"),  # 3자리 유지
            ("0101", "101"),  # 4자리 → 3자리 (KOSDAQ)
            ("101", "101"),  # 3자리 유지
        ],
    )
    def test_sector_tick_chart_code_conversion(
        self, mock_sector_api, input_code, expected_code
    ):
        """업종 틱차트 - 코드 변환 테스트"""
        mock_sector_api.get_sector_tick_chart(sector_code=input_code)

        call_kwargs = mock_sector_api.make_tr_request.call_args[1]
        assert call_kwargs["data"]["inds_cd"] == expected_code
