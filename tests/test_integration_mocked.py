#!/usr/bin/env python3
"""
Mock을 사용한 통합 테스트
실제 API 연결 없이 전체 플로우를 테스트
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
# 원시 JSON(dict) 응답 기반 테스트


class TestIntegrationWithMocks:
    """Mock을 사용한 통합 테스트"""

    def test_stock_price_full_flow(self, kiwoom):
        """주가 조회 전체 플로우 테스트"""
        # Mock 응답 설정
        mock_response = {
            'rt_cd': '0',
            'msg1': 'SUCCESS',
            'output': {
                'stck_prpr': '75000',
                'prdy_vrss': '1000',
                'prdy_vrss_sign': '2',
                'stck_oprc': '74500',
                'stck_hgpr': '75500',
                'stck_lwpr': '74000',
                'acml_vol': '1234567',
                'prdt_abrv_name': '삼성전자'
            }
        }
        
        with patch.object(kiwoom.stock_api, 'make_tr_request') as mock_request:
            mock_request.return_value = mock_response
            
            # 실제 API 호출
            result = kiwoom.get_stock_price('005930')
            
            # 검증
            assert result.get('rt_cd') == '0'
            assert result['output']['stck_prpr'] == '75000'
            assert result['output']['prdt_abrv_name'] == '삼성전자'
            
            # 호출 파라미터 검증 (POST + data에 stk_cd 사용)
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]['data']['stk_cd'] == '005930'
            assert call_args[1]['method'] == 'POST'

    def test_minute_chart_with_dataframe(self, kiwoom):
        """분봉 차트 조회 및 DataFrame 변환 테스트"""
        chart_data = {
            'rt_cd': '0',
            'msg1': 'SUCCESS',
            'output2': [
                {
                    'stck_bsop_date': '20250127',
                    'stck_cntg_hour': '1530',
                    'stck_prpr': '75000',
                    'stck_oprc': '74800',
                    'stck_hgpr': '75200',
                    'stck_lwpr': '74700',
                    'acml_vol': '1000000'
                },
                {
                    'stck_bsop_date': '20250127',
                    'stck_cntg_hour': '1525',
                    'stck_prpr': '74800',
                    'stck_oprc': '74900',
                    'stck_hgpr': '75000',
                    'stck_lwpr': '74600',
                    'acml_vol': '800000'
                }
            ]
        }
        
        with patch.object(kiwoom.chart_api, 'make_tr_request') as mock_request:
            mock_request.return_value = chart_data
            
            # 차트 데이터 조회
            result = kiwoom.get_minute_chart('005930', interval=5)
            # 검증: 원시 JSON과 데이터 길이
            assert result.get('rt_cd') == '0'
            assert len(result.get('output2', [])) == 2

    def test_orderbook_detailed(self, kiwoom):
        """호가 정보 상세 테스트"""
        orderbook_data = {
            'rt_cd': '0',
            'msg1': 'SUCCESS',
            'output1': {
                # 매도 호가 1~5
                'askp1': '75100', 'askp_rsqn1': '1500',
                'askp2': '75200', 'askp_rsqn2': '2000',
                'askp3': '75300', 'askp_rsqn3': '1000',
                'askp4': '75400', 'askp_rsqn4': '800',
                'askp5': '75500', 'askp_rsqn5': '1200',
                # 매수 호가 1~5
                'bidp1': '75000', 'bidp_rsqn1': '2500',
                'bidp2': '74900', 'bidp_rsqn2': '1800',
                'bidp3': '74800', 'bidp_rsqn3': '2200',
                'bidp4': '74700', 'bidp_rsqn4': '1100',
                'bidp5': '74600', 'bidp_rsqn5': '900'
            }
        }
        
        with patch.object(kiwoom.stock_api, 'make_tr_request') as mock_request:
            mock_request.return_value = orderbook_data
            
            result = kiwoom.get_stock_orderbook('005930')
            
            # 검증
            assert result.get('rt_cd') == '0'
            output = result['output1']
            
            # 매도호가 검증
            assert output['askp1'] == '75100'
            assert output['askp_rsqn1'] == '1500'
            
            # 매수호가 검증  
            assert output['bidp1'] == '75000'
            assert output['bidp_rsqn1'] == '2500'
            
            # 호가 스프레드 계산 (매도1호가 - 매수1호가)
            spread = int(output['askp1']) - int(output['bidp1'])
            assert spread == 100

    def test_ranking_apis_comprehensive(self, kiwoom):
        """순위 API들 종합 테스트"""
        ranking_data = {
            'rt_cd': '0',
            'msg1': 'SUCCESS', 
            'output': [
                {
                    'hts_kor_isnm': '삼성전자',
                    'mksc_shrn_iscd': '005930',
                    'stck_prpr': '75000',
                    'prdy_vrss': '1000',
                    'acml_vol': '15000000',
                    'vol_tnrt': '2.5'
                },
                {
                    'hts_kor_isnm': 'SK하이닉스', 
                    'mksc_shrn_iscd': '000660',
                    'stck_prpr': '135000',
                    'prdy_vrss': '3000',
                    'acml_vol': '8000000',
                    'vol_tnrt': '3.2'
                }
            ]
        }
        
        with patch.object(kiwoom.ranking_api, 'make_tr_request') as mock_request:
            mock_request.return_value = ranking_data
            
            # 거래량 순위
            volume_result = kiwoom.get_volume_top()
            assert volume_result.get('rt_cd') == '0'
            assert len(volume_result['output']) == 2
            
            # 첫 번째 종목 검증
            first_stock = volume_result['output'][0]
            assert first_stock['hts_kor_isnm'] == '삼성전자'
            assert first_stock['mksc_shrn_iscd'] == '005930'
            assert int(first_stock['acml_vol']) > int(volume_result['output'][1]['acml_vol'])

    def test_error_scenarios(self, kiwoom):
        """다양한 에러 시나리오 테스트"""
        # 키움 API 에러 응답
        kiwoom_error_data = {
            'rt_cd': '1',
            'msg1': 'APBK0013 : 주식 단축코드 오류',
            'output': {}
        }
        
        with patch.object(kiwoom.stock_api, 'make_tr_request') as mock_request:
            mock_request.return_value = kiwoom_error_data
            
            result = kiwoom.get_stock_price('INVALID')
            # 원시 JSON 기준: rt_cd로 성공/실패 판정
            assert result.get('rt_cd') != '0'
            assert result.get('msg1') == 'APBK0013 : 주식 단축코드 오류'

    def test_health_check_mocked(self, kiwoom_api_base):
        """헬스 체크 Mock 테스트"""
        health_response = {
            'rt_cd': '0',
            'msg1': 'SUCCESS',
            'output': {
                'prdt_abrv_name': '삼성전자',
                'stck_prpr': '75000'
            }
        }
        
        with patch.object(kiwoom_api_base, 'make_tr_request') as mock_request:
            mock_request.return_value = health_response
            
            health_status = kiwoom_api_base.health_check()
            
            assert health_status['status'] == 'healthy'
            assert health_status['connected'] == True
            assert health_status['api_responsive'] == True
            assert 'stats' in health_status

    def test_context_manager_flow(self, mock_env_vars, mock_session):
        """Context Manager 전체 플로우 테스트"""
        with patch('requests.Session', return_value=mock_session):
            from pykiwoom_rest import KiwoomRest, StockAPI
            
            with patch.object(StockAPI, '_get_access_token', return_value='test_token'):
                with KiwoomRest() as kiwoom:
                    # Context 내에서 API 사용
                    with patch.object(kiwoom.stock_api, 'make_tr_request') as mock_request:
                        mock_request.return_value = {
                            'rt_cd': '0',
                            'msg1': 'SUCCESS',
                            'output': {'test': 'data'}
                        }
                        
                        result = kiwoom.get_stock_price('005930')
                        assert result.get('rt_cd') == '0'
                        
                        # 통계 확인
                        stats = kiwoom.get_stats()
                        assert 'total_requests' in stats

    # to_dataframe 관련 테스트는 원시 JSON 전환에 따라 제거됨

    def test_stock_code_conversion(self, ranking_api):
        """종목코드 변환 헬퍼 테스트"""
        legacy_format = ranking_api.convert_stock_code_param('005930', legacy_format=True)
        assert legacy_format == {'FID_INPUT_ISCD': '005930'}
        
        new_format = ranking_api.convert_stock_code_param('005930', legacy_format=False)
        assert new_format == {'stk_cd': '005930'}
