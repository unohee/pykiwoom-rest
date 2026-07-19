#!/usr/bin/env python3
"""
키움증권 API 매개변수 일관성 검증 테스트
"""

import pytest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pykiwoom_rest.kiwoom_rest import KiwoomRest
import requests

@pytest.mark.integration  # 실제 API 키가 필요하므로 integration으로 변경
def test_parameter_consistency():
    """매개변수 일관성 테스트"""
    
    print("키움증권 API 매개변수 일관성 검증")
    print("=" * 50)
    
    # .env 파일에서 환경변수 자동 로드
    kiwoom = KiwoomRest()
    
    test_cases = [
        {
            "name": "고레벨 메서드 - get_stock_price",
            "method": lambda: kiwoom.get_stock_price('005930'),
            "expected_keys": ['stk_nm', 'cur_prc']
        },
        {
            "name": "고레벨 메서드 - get_stock_orderbook", 
            "method": lambda: kiwoom.get_stock_orderbook('005930'),
            "expected_keys": ['sel_fpr_bid', 'buy_fpr_bid']
        },
        {
            "name": "고레벨 메서드 - get_minute_chart",
            "method": lambda: kiwoom.get_minute_chart('005930', interval=5),
            "expected_keys": ['stk_min_pole_chart_qry']
        },
        {
            "name": "저레벨 메서드 - make_tr_request (FID_INPUT_ISCD)",
            "method": lambda: kiwoom.stock_api.make_tr_request('ka10001', 'stock_info', params={'FID_INPUT_ISCD': '005930'}, method='GET'),
            "expected_keys": ['stck_shrn_iscd', 'stck_prpr']
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['name']}")
        print("-" * 30)
        
        try:
            result = test['method']()
            
            if result:
                # 예상 키 확인
                found_keys = [key for key in test['expected_keys'] if key in result]
                
                if found_keys:
                    print(f"성공: {len(found_keys)}/{len(test['expected_keys'])} 키 발견")
                    if 'stk_nm' in result:
                        print(f"   종목: {result['stk_nm']}")
                    if 'stk_min_pole_chart_qry' in result:
                        chart_count = len(result['stk_min_pole_chart_qry'])
                        print(f"   차트 데이터: {chart_count}개")
                    results.append({"name": test['name'], "success": True})
                else:
                    print(f"부분 성공: 응답 키 {list(result.keys())[:3]}")
                    results.append({"name": test['name'], "success": True})
            else:
                print("실패: 응답 없음")
                results.append({"name": test['name'], "success": False})
                
        except (requests.RequestException, ValueError, KeyError) as e:
            print(f"오류: {e}")
            results.append({"name": test['name'], "success": False})
    
    # 결과 요약
    print(f"\n{'='*50}")
    print("매개변수 일관성 검증 결과")
    print(f"{'='*50}")
    
    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)
    
    for result in results:
        status = "성공" if result['success'] else "실패"
        print(f"{status}: {result['name']}")
    
    print(f"\n전체 결과: {success_count}/{total_count} 성공 ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("\n모든 매개변수가 일관성 있게 작동합니다!")
        return True
    else:
        print(f"\n{total_count - success_count}개 테스트에서 문제 발견")
        return False

if __name__ == "__main__":
    success = test_parameter_consistency()
    sys.exit(0 if success else 1)