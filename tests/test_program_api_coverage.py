"""
program_api.py 모듈 단위 테스트

자동 생성됨 - boost-coverage 스킬
생성일: 2026-01-05
목표: 커버리지 17% → 70%
"""

from unittest.mock import patch

import pytest

from pykiwoom_rest.program_api import ProgramAPI
from pykiwoom_rest.response_model import APIResponse


class TestProgramAPI:
    """ProgramAPI 클래스 테스트"""

    @pytest.fixture
    def mock_program_api(self):
        """모의 ProgramAPI 인스턴스"""
        token_patch = patch.object(ProgramAPI, "_get_access_token", return_value="mock_token")
        request_patch = patch.object(ProgramAPI, "make_tr_request")
        with token_patch, request_patch as mock_tr_request:
            mock_tr_request.return_value = APIResponse(
                success=True, data={"rt_cd": "0", "output": {"test": "data"}}
            )
            api = ProgramAPI(appkey="test_key", appsecret="test_secret", account_no="12345678")
            api.make_tr_request = mock_tr_request
            yield api

    def test_get_program_trading_daily_success(self, mock_program_api):
        """프로그램 매매 일별 조회 성공"""
        result = mock_program_api.get_program_trading_daily("005930")

        assert result is not None
        mock_program_api.make_tr_request.assert_called_once()

    def test_get_stock_program_trading(self, mock_program_api):
        """프로그램 매매동향 조회"""
        # Act
        result = mock_program_api.get_stock_program_trading("005930")

        # Assert
        assert result is not None
        mock_program_api.make_tr_request.assert_called_once()

    def test_get_stock_trade_volume_power(self, mock_program_api):
        """거래량 파동력 조회"""
        # Act
        result = mock_program_api.get_stock_trade_volume_power("005930")

        # Assert
        assert result is not None
        mock_program_api.make_tr_request.assert_called_once()

    def test_get_pbar_concentration_default_params(self, mock_program_api):
        """매물대 집중 조회 - 기본 파라미터"""
        # Act
        result = mock_program_api.get_pbar_concentration()

        # Assert
        assert result is not None
        mock_program_api.make_tr_request.assert_called_once()
        call_kwargs = mock_program_api.make_tr_request.call_args.kwargs
        assert call_kwargs["tr_code"] == "ka10025"
        assert call_kwargs["endpoint"] == "stock_info"
        assert call_kwargs["endpoint"] in ProgramAPI.ENDPOINTS

    def test_get_pbar_concentration_custom_params(self, mock_program_api):
        """매물대 집중 조회 - 커스텀 파라미터"""
        # Act
        result = mock_program_api.get_pbar_concentration(
            market="101",
            exchange="3",
            pbar_count="100",
            cycle="50",
            concentration_rate="5",
            include_current_entry="1",
        )

        # Assert
        assert result is not None
        mock_program_api.make_tr_request.assert_called_once()

    def test_get_pbar_concentration_all_market(self, mock_program_api):
        """매물대 집중 조회 - 전체 시장"""
        # Act
        result = mock_program_api.get_pbar_concentration(market="000")

        # Assert
        assert result is not None
        mock_program_api.make_tr_request.assert_called_once()

    def test_get_pbar_concentration_kospi_market(self, mock_program_api):
        """매물대 집중 조회 - KOSPI 시장"""
        # Act
        result = mock_program_api.get_pbar_concentration(market="001")

        # Assert
        assert result is not None
        mock_program_api.make_tr_request.assert_called_once()

    # NOTE: get_hourly_program_trading_paginated does not exist in ProgramAPI
    # These tests are removed as the method is not implemented


class TestProgramAPIErrorCases:
    """ProgramAPI 에러 케이스 테스트"""

    @pytest.fixture
    def failing_program_api(self):
        """에러 발생 API"""
        token_patch = patch.object(ProgramAPI, "_get_access_token", return_value="mock_token")
        request_patch = patch.object(ProgramAPI, "make_tr_request")
        with token_patch, request_patch as mock_tr_request:
            mock_tr_request.return_value = APIResponse(
                success=False, data={}, error={"message": "API Error", "code": "500"}
            )
            api = ProgramAPI(appkey="test_key", appsecret="test_secret", account_no="12345678")
            api.make_tr_request = mock_tr_request
            yield api

    def test_get_program_trading_daily_failure(self, failing_program_api):
        """프로그램 매매 일별 조회 실패"""
        result = failing_program_api.get_program_trading_daily("005930")

        # Assert
        assert result is not None  # Returns APIResponse even on failure
        assert not result.success
        failing_program_api.make_tr_request.assert_called_once()

    def test_get_pbar_concentration_failure(self, failing_program_api):
        """매물대 집중 조회 실패"""
        # Act
        result = failing_program_api.get_pbar_concentration()

        # Assert
        assert not result.success
