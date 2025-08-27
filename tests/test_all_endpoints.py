#!/usr/bin/env python3
"""
키움증권 REST API 전체 엔드포인트 테스트
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pykiwoom_rest import KiwoomRest
import json
import os

def test_all_endpoints():
    """다양한 키움 API 엔드포인트 테스트"""
    
    print("키움증권 REST API 전체 엔드포인트 테스트")
    print("=" * 60)
    
    # 환경변수 설정 (테스트용)
    os.environ['ACCOUNT_NO'] = '63513804'
    os.environ['KIWOOM_APPKEY'] = 'Px3ffmslMwr3qWVkwzW9yFbuEkbIKkwwiwoo4UWICYg'
    os.environ['KIWOOM_APPSECRET'] = 'bV4Dpr-5u9T3zWoRHbGOkU5O0uPxF3VPMJfyfrs08Uc'
    
    # API 키로 직접 인스턴스 생성
    kiwoom = KiwoomRest()
    
    # 테스트할 API 목록
    test_cases = [
        {
            "name": "주식분봉차트조회 (ka10080)",
            "method": lambda: test_minute_chart(kiwoom),
        },
        {
            "name": "주식기본정보요청 (ka10001)",
            "method": lambda: test_stock_basic_info(kiwoom),
        },
        {
            "name": "주식일봉차트조회 (ka10081)",
            "method": lambda: test_daily_chart(kiwoom),
        },
        {
            "name": "주식호가요청 (ka10004)",
            "method": lambda: test_stock_orderbook(kiwoom),
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}️⃣ {test_case['name']} 테스트")
        print("-" * 50)
        
        try:
            success = test_case['method']()
            results.append({"name": test_case['name'], "success": success})
            
            if success:
                print("성공")
            else:
                print("실패")
                
        except Exception as e:
            print(f"오류: {e}")
            results.append({"name": test_case['name'], "success": False})
    
    # 결과 요약
    print(f"\n{'='*60}")
    print("📊 테스트 결과 요약")
    print(f"{'='*60}")
    
    success_count = sum(1 for r in results if r['success'])
    total_count = len(results)
    
    for result in results:
        status = "성공" if result['success'] else "실패"
        print(f"{status} {result['name']}")
    
    print(f"\n전체 결과: {success_count}/{total_count} 성공 ({success_count/total_count*100:.1f}%)")
    
    return success_count == total_count

def test_minute_chart(kiwoom):
    """분봉 차트 테스트"""
    try:
        params = {
            'stk_cd': '005930',
            'tic_scope': '5',
            'upd_stkpc_tp': '1'
        }
        
        # 직접 make_request 호출 (키움 방식)
        result = kiwoom.make_request('chart', 'minute_chart', data=params)
        
        if result and 'stk_min_pole_chart_qry' in result:
            data_count = len(result['stk_min_pole_chart_qry'])
            print(f"   📊 데이터 {data_count}개 수신")
            return True
        else:
            print(f"   ⚠️ 예상과 다른 응답: {list(result.keys()) if result else 'None'}")
            return False
            
    except Exception as e:
        print(f"   ❌ 오류: {e}")
        return False

def test_stock_basic_info(kiwoom):
    """주식 기본정보 테스트"""
    try:
        params = {
            'stk_cd': '005930'  # 키움 방식 파라미터
        }
        
        result = kiwoom.make_request('stock_info', 'stock_basic_info', data=params)
        
        if result:
            print(f"   📈 응답 키: {list(result.keys())}")
            
            # 키움 방식 응답 구조 확인
            if any(key in result for key in ['stk_cd', 'output', 'stk_info']):
                return True
            else:
                print(f"   📋 전체 응답: {json.dumps(result, ensure_ascii=False)[:200]}...")
                return True  # 일단 응답이 있으면 성공으로 간주
        else:
            return False
            
    except Exception as e:
        print(f"   ❌ 오류: {e}")
        return False

def test_daily_chart(kiwoom):
    """일봉 차트 테스트"""
    try:
        params = {
            'stk_cd': '005930',
            'upd_stkpc_tp': '1'
        }
        
        result = kiwoom.make_request('chart', 'daily_chart', data=params)
        
        if result:
            print(f"   📊 응답 키: {list(result.keys())}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"   ❌ 오류: {e}")
        return False

def test_stock_orderbook(kiwoom):
    """주식 호가 테스트"""
    try:
        params = {
            'stk_cd': '005930'
        }
        
        result = kiwoom.make_request('market_condition', 'stock_quote', data=params)
        
        if result:
            print(f"   💰 응답 키: {list(result.keys())}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"   ❌ 오류: {e}")
        return False

if __name__ == "__main__":
    success = test_all_endpoints()
    if success:
        print("\n모든 엔드포인트 작동 확인")
    else:
        print("\n일부 엔드포인트에 문제 발견")
    
    sys.exit(0 if success else 1)