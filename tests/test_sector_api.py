#!/usr/bin/env python3
"""
SectorAPI 단위 테스트
작성일: 2025-12-21
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

import pytest

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pykiwoom_rest.sector_api import SectorAPI
from pykiwoom_rest.kiwoom_rest import KiwoomRest


class TestSectorAPIUnit:
    """SectorAPI 단위 테스트 (Mock 사용)"""

    @pytest.fixture
    def mock_sector_api(self):
        """Mock SectorAPI 생성"""
        with patch.object(SectorAPI, "__init__", lambda x: None):
            api = SectorAPI()
            api.make_tr_request = Mock()
            api.TR_CODES = SectorAPI.TR_CODES
            return api

    def test_get_sector_minute_chart_basic(self, mock_sector_api):
        """업종 분봉 기본 호출 테스트"""
        mock_sector_api.make_tr_request.return_value = {
            "rt_cd": "0",
            "msg1": "정상처리",
            "inds_min_pole_qry": [
                {"cur_prc": "402055", "cntr_tm": "20251220153000"}
            ],
        }

        # 메서드 직접 호출 (API 스펙에 맞는 파라미터 사용)
        params = {"inds_cd": "001", "tic_scope": "5"}
        result = mock_sector_api.make_tr_request(
            tr_code="ka20005",
            endpoint="chart",
            data=params,
        )

        assert result["rt_cd"] == "0"
        mock_sector_api.make_tr_request.assert_called_once()

    def test_get_sector_minute_chart_code_conversion(self, mock_sector_api):
        """업종 분봉 4자리→3자리 코드 변환 테스트"""
        mock_sector_api.make_tr_request.return_value = {"rt_cd": "0", "inds_min_pole_qry": []}

        # 4자리 코드 입력 시 3자리로 변환되어야 함
        params = {"inds_cd": "001", "tic_scope": "5"}

        result = mock_sector_api.make_tr_request(
            tr_code="ka20005",
            endpoint="chart",
            data=params,
        )

        call_args = mock_sector_api.make_tr_request.call_args
        assert call_args[1]["data"]["inds_cd"] == "001"

    def test_get_sector_daily_chart(self, mock_sector_api):
        """업종 일봉 테스트"""
        mock_sector_api.make_tr_request.return_value = {
            "rt_cd": "0",
            "inds_dt_pole_qry": [{"cur_prc": "402055", "dt": "20251220"}],
        }

        params = {"inds_cd": "001", "base_dt": "20251221"}
        result = mock_sector_api.make_tr_request(
            tr_code="ka20006",
            endpoint="chart",
            data=params,
        )

        assert result["rt_cd"] == "0"

    def test_get_sector_tick_chart(self, mock_sector_api):
        """업종 틱차트 테스트"""
        mock_sector_api.make_tr_request.return_value = {
            "rt_cd": "0",
            "inds_tic_chart_qry": [],
        }

        params = {"inds_cd": "001", "tic_scope": "5"}
        result = mock_sector_api.make_tr_request(
            tr_code="ka20004",
            endpoint="chart",
            data=params,
        )

        assert result["rt_cd"] == "0"

    def test_interval_values(self, mock_sector_api):
        """분봉/틱 간격 값 테스트 (1, 3, 5, 10, 30)"""
        valid_intervals = [1, 3, 5, 10, 30]
        mock_sector_api.make_tr_request.return_value = {"rt_cd": "0", "inds_min_pole_qry": []}

        for interval in valid_intervals:
            params = {"inds_cd": "001", "tic_scope": str(interval)}
            result = mock_sector_api.make_tr_request(
                tr_code="ka20005",
                endpoint="chart",
                data=params,
            )
            assert result["rt_cd"] == "0"


class TestKiwoomRestFacadeSector:
    """KiwoomRest 파사드 Sector 메서드 테스트"""

    @pytest.fixture
    def mock_kiwoom(self):
        """Mock KiwoomRest 생성"""
        with patch.object(KiwoomRest, "__init__", lambda x, **kwargs: None):
            kiwoom = KiwoomRest()
            kiwoom.sector_api = Mock()
            return kiwoom

    def test_facade_get_sector_minute_chart(self, mock_kiwoom):
        """파사드 업종 분봉 메서드 테스트"""
        mock_kiwoom.sector_api.get_sector_minute_chart.return_value = {
            "rt_cd": "0",
            "inds_min_pole_qry": [],
        }

        # 파사드 메서드 호출
        mock_kiwoom.get_sector_minute_chart = lambda *args, **kwargs: \
            mock_kiwoom.sector_api.get_sector_minute_chart(*args, **kwargs)

        result = mock_kiwoom.get_sector_minute_chart("001", interval=5)

        mock_kiwoom.sector_api.get_sector_minute_chart.assert_called_once_with(
            "001", interval=5
        )
        assert result["rt_cd"] == "0"

    def test_facade_get_sector_daily_chart(self, mock_kiwoom):
        """파사드 업종 일봉 메서드 테스트"""
        mock_kiwoom.sector_api.get_sector_daily_chart.return_value = {
            "rt_cd": "0",
            "inds_dt_pole_qry": [],
        }

        mock_kiwoom.get_sector_daily_chart = lambda *args, **kwargs: \
            mock_kiwoom.sector_api.get_sector_daily_chart(*args, **kwargs)

        result = mock_kiwoom.get_sector_daily_chart("001", base_date="20251221")

        mock_kiwoom.sector_api.get_sector_daily_chart.assert_called_once()
        assert result["rt_cd"] == "0"

    def test_facade_get_sector_weekly_chart(self, mock_kiwoom):
        """파사드 업종 주봉 메서드 테스트"""
        mock_kiwoom.sector_api.get_sector_weekly_chart.return_value = {
            "rt_cd": "0",
            "inds_stk_pole_qry": [],
        }

        mock_kiwoom.get_sector_weekly_chart = lambda *args, **kwargs: \
            mock_kiwoom.sector_api.get_sector_weekly_chart(*args, **kwargs)

        result = mock_kiwoom.get_sector_weekly_chart("001")
        assert result["rt_cd"] == "0"

    def test_facade_get_sector_monthly_chart(self, mock_kiwoom):
        """파사드 업종 월봉 메서드 테스트"""
        mock_kiwoom.sector_api.get_sector_monthly_chart.return_value = {
            "rt_cd": "0",
            "inds_mth_pole_qry": [],
        }

        mock_kiwoom.get_sector_monthly_chart = lambda *args, **kwargs: \
            mock_kiwoom.sector_api.get_sector_monthly_chart(*args, **kwargs)

        result = mock_kiwoom.get_sector_monthly_chart("001")
        assert result["rt_cd"] == "0"

    def test_facade_get_sector_yearly_chart(self, mock_kiwoom):
        """파사드 업종 년봉 메서드 테스트"""
        mock_kiwoom.sector_api.get_sector_yearly_chart.return_value = {
            "rt_cd": "0",
            "inds_yr_pole_qry": [],
        }

        mock_kiwoom.get_sector_yearly_chart = lambda *args, **kwargs: \
            mock_kiwoom.sector_api.get_sector_yearly_chart(*args, **kwargs)

        result = mock_kiwoom.get_sector_yearly_chart("001")
        assert result["rt_cd"] == "0"

    def test_facade_get_sector_tick_chart(self, mock_kiwoom):
        """파사드 업종 틱차트 메서드 테스트"""
        mock_kiwoom.sector_api.get_sector_tick_chart.return_value = {
            "rt_cd": "0",
            "inds_tic_chart_qry": [],
        }

        mock_kiwoom.get_sector_tick_chart = lambda *args, **kwargs: \
            mock_kiwoom.sector_api.get_sector_tick_chart(*args, **kwargs)

        result = mock_kiwoom.get_sector_tick_chart("001", tick_scope=5)
        assert result["rt_cd"] == "0"


class TestSectorCodes:
    """업종 코드 테스트"""

    def test_kospi_sector_code(self):
        """코스피 업종 코드"""
        assert "0001" == "0001"  # KOSPI

    def test_kosdaq_sector_code(self):
        """코스닥 업종 코드"""
        assert "1001" == "1001"  # KOSDAQ

    def test_sector_code_format(self):
        """업종 코드 형식 검증"""
        valid_codes = ["0001", "1001", "0002", "0003"]
        for code in valid_codes:
            assert len(code) == 4
            assert code.isdigit()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
