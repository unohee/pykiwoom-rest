#!/usr/bin/env python3
"""
키움증권 API 디버그 테스트 - 응답 구조 분석
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pykiwoom_rest.kiwoom_rest import KiwoomRest
import json
import os

def debug_api_responses():
    """API 응답 구조 디버그"""
    
    print("키움증권 API 응답 구조 디버그")
    print("=" * 60)
    
    # 환경변수 확인 (테스트 전 .env 파일 또는 환경변수 설정 필요)
    if not os.environ.get('ACCOUNT_NO') or not os.environ.get('KIWOOM_APPKEY'):
        print("Error: ACCOUNT_NO, KIWOOM_APPKEY, KIWOOM_APPSECRET 환경변수를 설정해주세요.")
        return
    
    kiwoom = KiwoomRest()
    
    # 1. 분봉차트 (성공한 것)
    print("\n1. 분봉차트 API (성공 사례)")
    print("-" * 40)
    
    try:
        params = {
            'stk_cd': '005930',
            'tic_scope': '5',
            'upd_stkpc_tp': '1'
        }
        
        result = kiwoom.make_request('chart', 'minute_chart', data=params)
        
        if result:
            print(" 응답 수신")
            print(f"응답 키: {list(result.keys())}")
            print(f"응답 타입: {type(result)}")
            
            if 'stk_min_pole_chart_qry' in result:
                print(f"차트 데이터: {len(result['stk_min_pole_chart_qry'])}개")
        else:
            print(" 응답 없음")
            
    except Exception as e:
        print(f" 오류: {e}")
        import traceback
        traceback.print_exc()
    
    # 2. 주식기본정보 (다른 엔드포인트)
    print("\n2. 주식기본정보 API 테스트")
    print("-" * 40)
    
    try:
        # 키움증권 방식으로 직접 호출
        import requests
        
        token = kiwoom._get_access_token()
        url = "https://api.kiwoom.com/api/dostk/stkinfo"
        
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'authorization': f'Bearer {token}',
            'api-id': 'ka10001'
        }
        
        data = {
            'stk_cd': '005930'
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        print(f"HTTP Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            json_response = response.json()
            print(f"Response Keys: {list(json_response.keys())}")
            print(f"Response Sample: {json.dumps(json_response, indent=2, ensure_ascii=False)[:500]}...")
        except:
            print(f"Response Text: {response.text[:500]}...")
            
    except Exception as e:
        print(f" 오류: {e}")
    
    # 3. 다른 API도 테스트
    print("\n3. 다른 API 엔드포인트 확인")
    print("-" * 40)
    
    other_apis = [
        {
            'name': '호가정보',
            'endpoint': '/api/dostk/mrkcond', 
            'api_id': 'ka10004',
            'data': {'stk_cd': '005930'}
        },
        {
            'name': '일봉차트',
            'endpoint': '/api/dostk/chart',
            'api_id': 'ka10081', 
            'data': {'stk_cd': '005930', 'upd_stkpc_tp': '1'}
        }
    ]
    
    token = kiwoom._get_access_token()
    
    for api in other_apis:
        print(f"\n{api['name']} ({api['api_id']}) 테스트:")
        
        try:
            url = f"https://api.kiwoom.com{api['endpoint']}"
            headers = {
                'Content-Type': 'application/json;charset=UTF-8',
                'authorization': f'Bearer {token}',
                'api-id': api['api_id']
            }
            
            response = requests.post(url, headers=headers, json=api['data'])
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    json_response = response.json()
                    print(f"  Keys: {list(json_response.keys())}")
                    
                    # 응답 크기에 따라 출력 조절
                    response_str = json.dumps(json_response, ensure_ascii=False)
                    if len(response_str) > 300:
                        print(f"  Sample: {response_str[:300]}...")
                    else:
                        print(f"  Data: {response_str}")
                        
                except Exception as parse_error:
                    print(f"  Text: {response.text[:200]}...")
            else:
                print(f"  Error: {response.text}")
                
        except Exception as e:
            print(f"  Exception: {e}")

if __name__ == "__main__":
    debug_api_responses()