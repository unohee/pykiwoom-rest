#!/usr/bin/env python3
"""
키움증권 공식 예제 코드 테스트
"""

import requests
import json

# 접근토큰 발급
def fn_au10001(data):
    # 1. 요청할 API URL
    #host = 'https://mockapi.kiwoom.com' # 모의투자
    host = 'https://api.kiwoom.com' # 실전투자
    endpoint = '/oauth2/token'
    url =  host + endpoint

    # 2. header 데이터
    headers = {
        'Content-Type': 'application/json;charset=UTF-8', # 컨텐츠타입
    }

    # 3. http POST 요청
    response = requests.post(url, headers=headers, json=data)

    # 4. 응답 상태 코드와 데이터 출력
    print('Code:', response.status_code)
    print('Header:', json.dumps({key: response.headers.get(key) for key in ['next-key', 'cont-yn', 'api-id']}, indent=4, ensure_ascii=False))
    print('Body:', json.dumps(response.json(), indent=4, ensure_ascii=False))  # JSON 응답을 파싱하여 출력
    
    return response.json()

# 실행 구간
if __name__ == '__main__':
    print("🔑 키움증권 공식 예제 코드 테스트")
    print("=" * 50)
    
    # 1. 요청 데이터 (실제 API 키 사용)
    params = {
        'grant_type': 'client_credentials',  # grant_type
        'appkey': 'Px3ffmslMwr3qWVkwzW9yFbuEkbIKkwwiwoo4UWICYg',  # 앱키
        'secretkey': 'bV4Dpr-5u9T3zWoRHbGOkU5O0uPxF3VPMJfyfrs08Uc',  # 시크릿키
    }

    print("요청 데이터:")
    print(json.dumps(params, indent=2, ensure_ascii=False))
    print()
    
    # 2. API 실행
    result = fn_au10001(data=params)
    
    print("\n분석:")
    if result.get('return_code') == 0:
        print(" 토큰 발급 성공!")
        print(f"토큰: {result.get('token', '')[:30]}...")
        print(f"만료일시: {result.get('expires_dt', '')}")
    else:
        print(" 토큰 발급 실패")
        print(f"오류: {result.get('return_msg', '')}")