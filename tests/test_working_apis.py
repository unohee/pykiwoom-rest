#!/usr/bin/env python3
"""
키움증권 REST API 작동하는 엔드포인트들 테스트
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pykiwoom_rest.kiwoom_rest import KiwoomRest
import requests


@pytest.mark.integration
def _setup_test_environment() -> KiwoomRest:
    """테스트 환경 설정 - 실제 API 키는 .env 파일 사용"""
    # 환경변수는 .env 파일에서 자동으로 로드됨
    return KiwoomRest()

def _test_stock_basic_info(kiwoom: KiwoomRest) -> None:
    """주식기본정보 테스트"""
    print("\n1. 주식기본정보 조회 - 삼성전자")
    print("-" * 40)
    
    try:
        result = kiwoom.stock_api.make_tr_request('ka10001', 'stock_info', params={'FID_INPUT_ISCD': '005930'}, method='GET')
        
        if result and 'stk_nm' in result:
            print(f"종목명: {result['stk_nm']}")
            print(f"   현재가: {result.get('cur_prc', 'N/A')}")
            print(f"   전일대비: {result.get('pred_pre', 'N/A')} ({result.get('flu_rt', 'N/A')}%)")
            print(f"   시가총액: {result.get('cap', 'N/A')}억원")
            print(f"   PER: {result.get('per', 'N/A')}")
            print(f"   PBR: {result.get('pbr', 'N/A')}")
        else:
            print("데이터 없음")
    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"오류: {e}")

def _test_stock_orderbook(kiwoom: KiwoomRest) -> None:
    """주식호가정보 테스트"""
    print("\n2. 주식호가정보 조회 - 삼성전자")
    print("-" * 40)
    
    try:
        result = kiwoom.stock_api.make_tr_request('ka10004', 'stock_info', params={'FID_INPUT_ISCD': '005930'}, method='GET')
        
        if result:
            print("호가정보 수신")
            print(f"   매도 1호가: {result.get('sel_fpr_bid', 'N/A')} (잔량: {result.get('sel_fpr_req', 'N/A')})")
            print(f"   매수 1호가: {result.get('buy_fpr_bid', 'N/A')} (잔량: {result.get('buy_fpr_req', 'N/A')})")
            print(f"   총 매도잔량: {result.get('tot_sel_req', 'N/A')}")
            print(f"   총 매수잔량: {result.get('tot_buy_req', 'N/A')}")
        else:
            print("데이터 없음")
    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"오류: {e}")

def _test_minute_chart(kiwoom: KiwoomRest) -> None:
    """분봉차트 테스트"""
    print("\n3. 주식분봉차트 조회 - 삼성전자 5분봉")
    print("-" * 40)
    
    try:
        params = {
            'stk_cd': '005930',
            'tic_scope': '5',
            'upd_stkpc_tp': '1'
        }
        
        result = kiwoom.chart_api.make_tr_request('ka10080', 'chart', data=params)
        
        if result and 'stk_min_pole_chart_qry' in result:
            chart_data = result['stk_min_pole_chart_qry']
            print(f"5분봉 데이터 {len(chart_data)}개 수신")
            
            print("   최근 5개 봉:")
            for i, item in enumerate(chart_data[:5]):
                time = item.get('cntr_tm', '')[:8]
                formatted_time = f"{time[:4]}-{time[4:6]}-{time[6:8]}"
                print(f"   {i+1}. {formatted_time} | 종가: {item.get('cur_prc', '')} | 거래량: {item.get('trde_qty', '')}")
        else:
            print("차트 데이터 없음")
    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"오류: {e}")

@pytest.mark.integration
def test_working_apis() -> None:
    """작동하는 키움 API들 테스트"""
    print("키움증권 REST API 엔드포인트 테스트")
    print("=" * 60)
    
    kiwoom = _setup_test_environment()
    
    _test_stock_basic_info(kiwoom)
    _test_stock_orderbook(kiwoom)
    _test_minute_chart(kiwoom)
    
    print(f"\n{'='*60}")
    pass
    print(f"{'='*60}")

if __name__ == "__main__":
    test_working_apis()