#!/usr/bin/env python3
"""
키움증권 REST API 엔드포인트 테스트 (보안 버전)
Mock을 사용하여 실제 API 키 없이 테스트
"""

import pytest
from unittest.mock import patch, MagicMock
# 원시 JSON(dict) 응답 기준으로 테스트


class TestEndpointsSecure:
    """보안 API 엔드포인트 테스트"""

    def test_stock_basic_info(self, kiwoom, mock_response):
        """주식 기본정보 조회 테스트"""
        with patch.object(kiwoom.stock_api, 'make_tr_request') as mock_request:
            mock_request.return_value = mock_response
            
            result = kiwoom.get_stock_price('005930')
            
            assert result is not None
            assert result.get('rt_cd') == '0'
            mock_request.assert_called_once()

    def test_minute_chart(self, kiwoom, mock_response):
        """분봉 차트 조회 테스트"""
        chart_response = {
            'rt_cd': '0',
            'msg1': 'SUCCESS',
            'output2': [
                {
                    'stck_bsop_date': '20250127',
                    'stck_cntg_hour': '1530',
                    'stck_prpr': '75000'
                }
            ]
        }
        
        with patch.object(kiwoom.chart_api, 'make_tr_request') as mock_request:
            mock_request.return_value = chart_response
            
            result = kiwoom.get_minute_chart('005930', interval=5)
            
            assert result is not None
            assert result.get('rt_cd') == '0'
            assert 'output2' in result
            mock_request.assert_called_once()

    def test_daily_chart(self, kiwoom, mock_response):
        """일봉 차트 조회 테스트"""
        with patch.object(kiwoom.chart_api, 'make_tr_request') as mock_request:
            mock_request.return_value = mock_response
            
            result = kiwoom.get_daily_chart('005930')
            
            assert result is not None
            assert result.get('rt_cd') == '0'
            mock_request.assert_called_once()

    def test_stock_orderbook(self, kiwoom, mock_response):
        """호가 정보 조회 테스트"""
        orderbook_response = {
            'rt_cd': '0',
            'msg1': 'SUCCESS',
            'output1': {
                'askp1': '75100',
                'bidp1': '74900',
                'askp_rsqn1': '1000',
                'bidp_rsqn1': '1500'
            }
        }
        
        with patch.object(kiwoom.stock_api, 'make_tr_request') as mock_request:
            mock_request.return_value = orderbook_response
            
            result = kiwoom.get_stock_orderbook('005930')
            
            assert result is not None
            assert result.get('rt_cd') == '0'
            assert 'output1' in result
            mock_request.assert_called_once()

    def test_volume_ranking(self, kiwoom, mock_response):
        """거래량 순위 조회 테스트"""
        ranking_response = {
            'rt_cd': '0', 
            'msg1': 'SUCCESS',
            'output': [
                {
                    'hts_kor_isnm': '삼성전자',
                    'mksc_shrn_iscd': '005930',
                    'stck_prpr': '75000',
                    'acml_vol': '10000000'
                }
            ]
        }
        
        with patch.object(kiwoom.ranking_api, 'make_tr_request') as mock_request:
            mock_request.return_value = ranking_response
            
            result = kiwoom.get_volume_top()
            
            assert result is not None
            assert result.get('rt_cd') == '0'
            assert 'output' in result
            mock_request.assert_called_once()

    def test_error_handling(self, kiwoom):
        """에러 처리 테스트"""
        error_response = {'rt_cd': '1', 'msg1': 'API 에러 테스트', 'error': {'code': 'E001'}}
        
        with patch.object(kiwoom.stock_api, 'make_tr_request') as mock_request:
            mock_request.return_value = error_response
            
            result = kiwoom.get_stock_price('INVALID')
            
            assert result is not None
            assert result.get('rt_cd') != '0'
            assert 'error' in result
            mock_request.assert_called_once()

    # APIResponse 호환성 테스트는 원시 JSON 전환으로 제거됨
