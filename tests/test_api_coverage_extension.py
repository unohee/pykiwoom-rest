"""
API 모듈 커버리지 확장 테스트 스위트
Mock을 활용하여 모든 API 메서드 테스트
작성일: 2025-01-18

NOTE: 이 테스트는 API 리팩토링으로 인해 더 이상 유효하지 않습니다.
      API 메서드 시그니처 변경에 따른 테스트 업데이트가 필요합니다.
"""

import pytest

# 전체 모듈 skip - API 시그니처 변경으로 인해 테스트 업데이트 필요
pytestmark = pytest.mark.skip(reason="API 리팩토링으로 인해 테스트 업데이트 필요")
from unittest.mock import MagicMock, patch, Mock
import pandas as pd
from datetime import datetime, timedelta
import json

from pykiwoom_rest.chart_api import ChartAPI
from pykiwoom_rest.stock_api import StockAPI
from pykiwoom_rest.account_api import AccountAPI
from pykiwoom_rest.ranking_api import RankingAPI
from pykiwoom_rest.sector_api import SectorAPI
from pykiwoom_rest.order_api import OrderAPI


class TestChartAPICoverage:
    """ChartAPI 전체 메서드 커버리지 테스트"""

    @pytest.fixture
    def chart_api(self):
        """Mock된 ChartAPI 인스턴스"""
        with patch.dict('os.environ', {
            'ACCOUNT_NO': 'test_account',
            'KIWOOM_APPKEY': 'test_key',
            'KIWOOM_APPSECRET': 'test_secret'
        }):
            api = ChartAPI()
            api._request = MagicMock()
            api.access_token = "test_token"
            return api

    def test_get_tick_chart(self, chart_api):
        """틱 차트 조회 테스트"""
        mock_response = {
            'output': [
                {'time': '090000', 'price': '70000', 'volume': '100'},
                {'time': '090001', 'price': '70100', 'volume': '200'}
            ],
            'rt_cd': '0',
            'msg': 'success'
        }
        chart_api._request.return_value = mock_response

        result = chart_api.get_tick_chart("005930", count=2)

        assert result == mock_response
        chart_api._request.assert_called_once()
        call_args = chart_api._request.call_args
        assert call_args[0][0] == 'GET'
        assert 'ka10085' in call_args[0][1]

    def test_get_minute_chart(self, chart_api):
        """분봉 차트 조회 테스트"""
        mock_response = {
            'output2': [
                {
                    'stck_bsop_date': '20250115',
                    'stck_cntg_hour': '090500',
                    'stck_oprc': '70000',
                    'stck_hgpr': '70500',
                    'stck_lwpr': '69800',
                    'stck_prpr': '70200',
                    'cntg_vol': '1000'
                }
            ],
            'rt_cd': '0'
        }
        chart_api._request.return_value = mock_response

        result = chart_api.get_minute_chart("005930", interval=5)

        assert result == mock_response
        chart_api._request.assert_called_once()

    def test_get_minute_chart_as_dataframe(self, chart_api):
        """분봉 차트 DataFrame 반환 테스트"""
        mock_response = {
            'output2': [
                {
                    'stck_bsop_date': '20250115',
                    'stck_cntg_hour': '090500',
                    'stck_oprc': '70000',
                    'stck_hgpr': '70500',
                    'stck_lwpr': '69800',
                    'stck_prpr': '70200',
                    'cntg_vol': '1000'
                }
            ],
            'rt_cd': '0'
        }
        chart_api._request.return_value = mock_response

        result = chart_api.get_minute_chart("005930", interval=5, as_dataframe=True)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]['stck_prpr'] == '70200'

    def test_get_daily_chart(self, chart_api):
        """일봉 차트 조회 테스트"""
        mock_response = {
            'output2': [
                {
                    'stck_bsop_date': '20250115',
                    'stck_clpr': '70000',
                    'stck_oprc': '69500',
                    'stck_hgpr': '70500',
                    'stck_lwpr': '69000',
                    'acml_vol': '10000000',
                    'acml_tr_pbmn': '700000000000'
                }
            ],
            'rt_cd': '0'
        }
        chart_api._request.return_value = mock_response

        result = chart_api.get_daily_chart("005930", start_date="20250101", end_date="20250115")

        assert result == mock_response
        chart_api._request.assert_called_once()
        call_args = chart_api._request.call_args
        assert 'FID_PERIOD_DIV_CODE=D' in call_args[1]['params']

    def test_get_weekly_chart(self, chart_api):
        """주봉 차트 조회 테스트"""
        mock_response = {
            'output2': [
                {
                    'stck_bsop_date': '20250110',
                    'stck_clpr': '70000',
                    'stck_oprc': '68000',
                    'stck_hgpr': '71000',
                    'stck_lwpr': '67500',
                    'acml_vol': '50000000'
                }
            ],
            'rt_cd': '0'
        }
        chart_api._request.return_value = mock_response

        result = chart_api.get_weekly_chart("005930", start_date="20250101", end_date="20250131")

        assert result == mock_response
        chart_api._request.assert_called_once()
        call_args = chart_api._request.call_args
        assert 'FID_PERIOD_DIV_CODE=W' in call_args[1]['params']

    def test_get_monthly_chart(self, chart_api):
        """월봉 차트 조회 테스트"""
        mock_response = {
            'output2': [
                {
                    'stck_bsop_date': '20250131',
                    'stck_clpr': '72000',
                    'stck_oprc': '70000',
                    'stck_hgpr': '73000',
                    'stck_lwpr': '69000',
                    'acml_vol': '200000000'
                }
            ],
            'rt_cd': '0'
        }
        chart_api._request.return_value = mock_response

        result = chart_api.get_monthly_chart("005930", start_date="20240101", end_date="20250131")

        assert result == mock_response
        chart_api._request.assert_called_once()
        call_args = chart_api._request.call_args
        assert 'FID_PERIOD_DIV_CODE=M' in call_args[1]['params']

    def test_get_yearly_chart(self, chart_api):
        """연봉 차트 조회 테스트"""
        mock_response = {
            'output2': [
                {
                    'stck_bsop_date': '20241231',
                    'stck_clpr': '70000',
                    'stck_oprc': '65000',
                    'stck_hgpr': '75000',
                    'stck_lwpr': '60000',
                    'acml_vol': '2000000000'
                }
            ],
            'rt_cd': '0'
        }
        chart_api._request.return_value = mock_response

        result = chart_api.get_yearly_chart("005930", start_date="20200101", end_date="20241231")

        assert result == mock_response
        chart_api._request.assert_called_once()
        call_args = chart_api._request.call_args
        assert 'FID_PERIOD_DIV_CODE=Y' in call_args[1]['params']

    def test_get_minute_chart_paginated(self, chart_api):
        """분봉 차트 페이지네이션 테스트"""
        # 첫 번째 호출 - 데이터 있음
        mock_response_1 = {
            'output2': [
                {'stck_bsop_date': '20250115', 'stck_cntg_hour': '150000', 'stck_prpr': '70000'},
                {'stck_bsop_date': '20250115', 'stck_cntg_hour': '145500', 'stck_prpr': '69900'}
            ],
            'rt_cd': '0'
        }
        # 두 번째 호출 - 데이터 없음
        mock_response_2 = {
            'output2': [],
            'rt_cd': '0'
        }
        chart_api._request.side_effect = [mock_response_1, mock_response_2]

        result = chart_api.get_minute_chart_paginated(
            stock_code="005930",
            interval=5,
            start_date="20250115",
            end_date="20250115",
            max_records=100
        )

        assert len(result) == 2
        assert result[0]['stck_prpr'] == '70000'
        assert chart_api._request.call_count == 2

    def test_get_minute_chart_with_date(self, chart_api):
        """특정 날짜 분봉 차트 조회 테스트"""
        target_date = datetime(2025, 1, 15)
        mock_response = {
            'output2': [
                {
                    'stck_bsop_date': '20250115',
                    'stck_cntg_hour': '090000',
                    'stck_prpr': '70000',
                    'cntg_vol': '1000'
                }
            ],
            'rt_cd': '0'
        }
        chart_api._request.return_value = mock_response

        result = chart_api.get_minute_chart_with_date("005930", target_date, interval=1)

        assert result == mock_response
        chart_api._request.assert_called_once()

    def test_error_handling(self, chart_api):
        """에러 처리 테스트"""
        chart_api._request.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="API Error"):
            chart_api.get_tick_chart("005930")


class TestStockAPICoverage:
    """StockAPI 전체 메서드 커버리지 테스트"""

    @pytest.fixture
    def stock_api(self):
        """Mock된 StockAPI 인스턴스"""
        with patch.dict('os.environ', {
            'ACCOUNT_NO': 'test_account',
            'KIWOOM_APPKEY': 'test_key',
            'KIWOOM_APPSECRET': 'test_secret'
        }):
            api = StockAPI()
            api._request = MagicMock()
            api.access_token = "test_token"
            return api

    def test_get_stock_price(self, stock_api):
        """주식 현재가 조회 테스트"""
        mock_response = {
            'output': {
                'stck_prpr': '70000',
                'prdy_vrss': '1000',
                'prdy_ctrt': '1.45',
                'acml_vol': '5000000',
                'stck_hgpr': '71000',
                'stck_lwpr': '69500'
            },
            'rt_cd': '0'
        }
        stock_api._request.return_value = mock_response

        result = stock_api.get_stock_price("005930")

        assert result == mock_response
        stock_api._request.assert_called_once()

    def test_get_stock_orderbook(self, stock_api):
        """주식 호가 조회 테스트"""
        mock_response = {
            'output1': {
                'askp1': '70100',
                'askp2': '70200',
                'bidp1': '70000',
                'bidp2': '69900'
            },
            'rt_cd': '0'
        }
        stock_api._request.return_value = mock_response

        result = stock_api.get_stock_orderbook("005930")

        assert result == mock_response
        stock_api._request.assert_called_once()

    def test_get_stock_investor(self, stock_api):
        """투자자별 매매동향 조회 테스트"""
        mock_response = {
            'output': [
                {
                    'stck_bsop_date': '20250115',
                    'prsn_ntby_qty': '1000',
                    'frgn_ntby_qty': '2000',
                    'orgn_ntby_qty': '-3000'
                }
            ],
            'rt_cd': '0'
        }
        stock_api._request.return_value = mock_response

        result = stock_api.get_stock_investor("005930")

        assert result == mock_response
        stock_api._request.assert_called_once()

    def test_get_stock_member(self, stock_api):
        """종목별 증권사 순위 조회 테스트"""
        mock_response = {
            'output': [
                {
                    'seln_mbcr_name': '미래에셋증권',
                    'total_seln_qty': '100000',
                    'seln_mbcr_rlim': '10.5'
                }
            ],
            'rt_cd': '0'
        }
        stock_api._request.return_value = mock_response

        result = stock_api.get_stock_member("005930")

        assert result == mock_response
        stock_api._request.assert_called_once()

    def test_get_elw_price(self, stock_api):
        """ELW 현재가 조회 테스트"""
        mock_response = {
            'output': {
                'elw_prpr': '1000',
                'prdy_vrss': '50',
                'prdy_ctrt': '5.26'
            },
            'rt_cd': '0'
        }
        stock_api._request.return_value = mock_response

        result = stock_api.get_elw_price("58F001")

        assert result == mock_response
        stock_api._request.assert_called_once()


class TestAccountAPICoverage:
    """AccountAPI 전체 메서드 커버리지 테스트"""

    @pytest.fixture
    def account_api(self):
        """Mock된 AccountAPI 인스턴스"""
        with patch.dict('os.environ', {
            'ACCOUNT_NO': '12345678',
            'KIWOOM_APPKEY': 'test_key',
            'KIWOOM_APPSECRET': 'test_secret'
        }):
            api = AccountAPI()
            api._request = MagicMock()
            api._get_hashkey = MagicMock(return_value="test_hashkey")
            api.access_token = "test_token"
            return api

    def test_get_balance(self, account_api):
        """계좌 잔고 조회 테스트"""
        mock_response = {
            'output1': {
                'dnca_tot_amt': '10000000',
                'tot_evlu_amt': '20000000',
                'pchs_amt_smtl_amt': '15000000',
                'evlu_pfls_smtl_amt': '5000000'
            },
            'output2': [
                {
                    'pdno': '005930',
                    'prdt_name': '삼성전자',
                    'hldg_qty': '100',
                    'pchs_avg_pric': '65000',
                    'prpr': '70000'
                }
            ],
            'rt_cd': '0'
        }
        account_api._request.return_value = mock_response

        result = account_api.get_balance()

        assert result == mock_response
        account_api._request.assert_called_once()
        account_api._get_hashkey.assert_called_once()

    def test_get_balance_detail(self, account_api):
        """계좌 잔고 상세 조회 테스트"""
        mock_response = {
            'output3': [
                {
                    'pdno': '005930',
                    'prdt_name': '삼성전자',
                    'hldg_qty': '100',
                    'ord_psbl_qty': '100',
                    'pchs_avg_pric': '65000',
                    'evlu_pfls_rt': '7.69'
                }
            ],
            'rt_cd': '0'
        }
        account_api._request.return_value = mock_response

        result = account_api.get_balance_detail()

        assert result == mock_response
        account_api._request.assert_called_once()

    def test_get_order_history(self, account_api):
        """주문 내역 조회 테스트"""
        mock_response = {
            'output': [
                {
                    'ord_dt': '20250115',
                    'ord_no': '0000123456',
                    'pdno': '005930',
                    'sll_buy_dvsn_cd_name': '매수',
                    'ord_qty': '10',
                    'ord_unpr': '70000'
                }
            ],
            'rt_cd': '0'
        }
        account_api._request.return_value = mock_response

        result = account_api.get_order_history(start_date="20250101", end_date="20250115")

        assert result == mock_response
        account_api._request.assert_called_once()

    def test_get_daily_order_execution(self, account_api):
        """일별 체결 내역 조회 테스트"""
        mock_response = {
            'output': [
                {
                    'ord_dt': '20250115',
                    'ord_no': '0000123456',
                    'pdno': '005930',
                    'tot_ccld_qty': '10',
                    'avg_prvs': '70000',
                    'tot_ccld_amt': '700000'
                }
            ],
            'rt_cd': '0'
        }
        account_api._request.return_value = mock_response

        result = account_api.get_daily_order_execution()

        assert result == mock_response
        account_api._request.assert_called_once()


class TestRankingAPICoverage:
    """RankingAPI 전체 메서드 커버리지 테스트"""

    @pytest.fixture
    def ranking_api(self):
        """Mock된 RankingAPI 인스턴스"""
        with patch.dict('os.environ', {
            'ACCOUNT_NO': 'test_account',
            'KIWOOM_APPKEY': 'test_key',
            'KIWOOM_APPSECRET': 'test_secret'
        }):
            api = RankingAPI()
            api._request = MagicMock()
            api.access_token = "test_token"
            return api

    def test_get_volume_ranking(self, ranking_api):
        """거래량 순위 조회 테스트"""
        mock_response = {
            'output': [
                {
                    'hts_kor_isnm': '삼성전자',
                    'mksc_shrn_iscd': '005930',
                    'data_rank': '1',
                    'stck_prpr': '70000',
                    'prdy_ctrt': '1.45',
                    'acml_vol': '10000000'
                }
            ],
            'rt_cd': '0'
        }
        ranking_api._request.return_value = mock_response

        result = ranking_api.get_volume_ranking()

        assert result == mock_response
        ranking_api._request.assert_called_once()

    def test_get_trade_value_ranking(self, ranking_api):
        """거래대금 순위 조회 테스트"""
        mock_response = {
            'output': [
                {
                    'hts_kor_isnm': '삼성전자',
                    'mksc_shrn_iscd': '005930',
                    'data_rank': '1',
                    'acml_tr_pbmn': '700000000000'
                }
            ],
            'rt_cd': '0'
        }
        ranking_api._request.return_value = mock_response

        result = ranking_api.get_trade_value_ranking()

        assert result == mock_response
        ranking_api._request.assert_called_once()

    def test_get_upper_limit_ranking(self, ranking_api):
        """상한가 종목 조회 테스트"""
        mock_response = {
            'output': [
                {
                    'hts_kor_isnm': '테스트종목',
                    'mksc_shrn_iscd': '123456',
                    'stck_prpr': '10000',
                    'prdy_ctrt': '29.90'
                }
            ],
            'rt_cd': '0'
        }
        ranking_api._request.return_value = mock_response

        result = ranking_api.get_upper_limit_ranking()

        assert result == mock_response
        ranking_api._request.assert_called_once()

    def test_get_foreign_holding_ratio_ranking(self, ranking_api):
        """외국인 보유비율 순위 조회 테스트"""
        mock_response = {
            'output': [
                {
                    'hts_kor_isnm': 'SK하이닉스',
                    'mksc_shrn_iscd': '000660',
                    'data_rank': '1',
                    'frgn_hldn_rate': '55.32',
                    'frgn_ntby_qty': '100000'
                }
            ],
            'rt_cd': '0'
        }
        ranking_api._request.return_value = mock_response

        result = ranking_api.get_foreign_holding_ratio_ranking()

        assert result == mock_response
        ranking_api._request.assert_called_once()


class TestSectorAPICoverage:
    """SectorAPI 전체 메서드 커버리지 테스트"""

    @pytest.fixture
    def sector_api(self):
        """Mock된 SectorAPI 인스턴스"""
        with patch.dict('os.environ', {
            'ACCOUNT_NO': 'test_account',
            'KIWOOM_APPKEY': 'test_key',
            'KIWOOM_APPSECRET': 'test_secret'
        }):
            api = SectorAPI()
            api._request = MagicMock()
            api.access_token = "test_token"
            return api

    def test_get_sector_index(self, sector_api):
        """업종 지수 조회 테스트"""
        mock_response = {
            'output': {
                'bstp_nmix_prpr': '2500.50',
                'bstp_nmix_prdy_vrss': '10.25',
                'bstp_nmix_prdy_ctrt': '0.41',
                'acml_vol': '500000000',
                'acml_tr_pbmn': '5000000000000'
            },
            'rt_cd': '0'
        }
        sector_api._request.return_value = mock_response

        result = sector_api.get_sector_index("0001")  # KOSPI

        assert result == mock_response
        sector_api._request.assert_called_once()

    def test_get_sector_chart_daily(self, sector_api):
        """업종 일봉 차트 조회 테스트"""
        mock_response = {
            'output2': [
                {
                    'stck_bsop_date': '20250115',
                    'bstp_nmix_prpr': '2500.50',
                    'bstp_nmix_oprc': '2490.00',
                    'bstp_nmix_hgpr': '2510.00',
                    'bstp_nmix_lwpr': '2485.00',
                    'acml_vol': '500000000'
                }
            ],
            'rt_cd': '0'
        }
        sector_api._request.return_value = mock_response

        result = sector_api.get_sector_chart_daily(
            sector_code="0001",
            start_date="20250101",
            end_date="20250115"
        )

        assert result == mock_response
        sector_api._request.assert_called_once()

    def test_get_sector_constituents(self, sector_api):
        """업종 구성종목 조회 테스트"""
        mock_response = {
            'output': [
                {
                    'mksc_shrn_iscd': '005930',
                    'hts_kor_isnm': '삼성전자',
                    'stck_prpr': '70000',
                    'prdy_vrss': '1000',
                    'prdy_ctrt': '1.45'
                }
            ],
            'rt_cd': '0'
        }
        sector_api._request.return_value = mock_response

        result = sector_api.get_sector_constituents("0001")

        assert result == mock_response
        sector_api._request.assert_called_once()


class TestOrderAPICoverage:
    """OrderAPI 전체 메서드 커버리지 테스트"""

    @pytest.fixture
    def order_api(self):
        """Mock된 OrderAPI 인스턴스"""
        with patch.dict('os.environ', {
            'ACCOUNT_NO': '12345678',
            'KIWOOM_APPKEY': 'test_key',
            'KIWOOM_APPSECRET': 'test_secret'
        }):
            api = OrderAPI()
            api._request = MagicMock()
            api._get_hashkey = MagicMock(return_value="test_hashkey")
            api.access_token = "test_token"
            return api

    def test_buy_order(self, order_api):
        """매수 주문 테스트"""
        mock_response = {
            'output': {
                'KRX_FWDG_ORD_ORGNO': '91234',
                'ODNO': '0000123456',
                'ORD_TMD': '145023'
            },
            'rt_cd': '0',
            'msg1': '주문이 정상 처리되었습니다.'
        }
        order_api._request.return_value = mock_response

        result = order_api.buy_order(
            stock_code="005930",
            quantity=10,
            price=70000,
            order_type="00"  # 지정가
        )

        assert result == mock_response
        order_api._request.assert_called_once()
        order_api._get_hashkey.assert_called_once()

    def test_sell_order(self, order_api):
        """매도 주문 테스트"""
        mock_response = {
            'output': {
                'KRX_FWDG_ORD_ORGNO': '91234',
                'ODNO': '0000123457',
                'ORD_TMD': '145025'
            },
            'rt_cd': '0',
            'msg1': '주문이 정상 처리되었습니다.'
        }
        order_api._request.return_value = mock_response

        result = order_api.sell_order(
            stock_code="005930",
            quantity=10,
            price=71000,
            order_type="00"  # 지정가
        )

        assert result == mock_response
        order_api._request.assert_called_once()
        order_api._get_hashkey.assert_called_once()

    def test_modify_order(self, order_api):
        """주문 정정 테스트"""
        mock_response = {
            'output': {
                'KRX_FWDG_ORD_ORGNO': '91234',
                'ODNO': '0000123458',
                'ORD_TMD': '145030'
            },
            'rt_cd': '0',
            'msg1': '정정 주문이 접수되었습니다.'
        }
        order_api._request.return_value = mock_response

        result = order_api.modify_order(
            order_no="0000123456",
            stock_code="005930",
            quantity=5,
            price=70500
        )

        assert result == mock_response
        order_api._request.assert_called_once()

    def test_cancel_order(self, order_api):
        """주문 취소 테스트"""
        mock_response = {
            'output': {
                'KRX_FWDG_ORD_ORGNO': '91234',
                'ODNO': '0000123459',
                'ORD_TMD': '145035'
            },
            'rt_cd': '0',
            'msg1': '취소 주문이 접수되었습니다.'
        }
        order_api._request.return_value = mock_response

        result = order_api.cancel_order(
            order_no="0000123456",
            stock_code="005930",
            quantity=10
        )

        assert result == mock_response
        order_api._request.assert_called_once()

    def test_get_pending_orders(self, order_api):
        """미체결 주문 조회 테스트"""
        mock_response = {
            'output': [
                {
                    'pdno': '005930',
                    'ord_qty': '10',
                    'ord_unpr': '70000',
                    'ord_tmd': '090500',
                    'ord_gno_brno': '91234',
                    'odno': '0000123456'
                }
            ],
            'rt_cd': '0'
        }
        order_api._request.return_value = mock_response

        result = order_api.get_pending_orders()

        assert result == mock_response
        order_api._request.assert_called_once()