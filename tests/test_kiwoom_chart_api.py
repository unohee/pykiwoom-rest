#!/usr/bin/env python3
"""
키움증권 공식 예제 - 주식분봉차트조회 테스트
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
    
    return response.json()

# 주식분봉차트조회요청
def fn_ka10080(token, data, cont_yn='N', next_key=''):
    # 1. 요청할 API URL
    #host = 'https://mockapi.kiwoom.com' # 모의투자
    host = 'https://api.kiwoom.com' # 실전투자
    endpoint = '/api/dostk/chart'
    url =  host + endpoint

    # 2. header 데이터
    headers = {
        'Content-Type': 'application/json;charset=UTF-8', # 컨텐츠타입
        'authorization': f'Bearer {token}', # 접근토큰
        'cont-yn': cont_yn, # 연속조회여부
        'next-key': next_key, # 연속조회키
        'api-id': 'ka10080', # TR명
    }

    # 3. http POST 요청
    response = requests.post(url, headers=headers, json=data)

    # 4. 응답 상태 코드와 데이터 출력
    print('Code:', response.status_code)
    print('Header:', json.dumps({key: response.headers.get(key) for key in ['next-key', 'cont-yn', 'api-id']}, indent=4, ensure_ascii=False))
    try:
        response_json = response.json()
        print('Body:', json.dumps(response_json, indent=4, ensure_ascii=False))
        return response_json
    except:
        print('Body (text):', response.text)
        return None

# 실행 구간
if __name__ == '__main__':
    print("🔑 키움증권 공식 예제 - 분봉차트 조회 테스트")
    print("=" * 60)
    
    # 1. 토큰 발급
    print("\n1. 토큰 발급")
    token_params = {
        'grant_type': 'client_credentials',
        'appkey': 'Px3ffmslMwr3qWVkwzW9yFbuEkbIKkwwiwoo4UWICYg',
        'secretkey': 'bV4Dpr-5u9T3zWoRHbGOkU5O0uPxF3VPMJfyfrs08Uc',
    }
    
    token_result = fn_au10001(data=token_params)
    
    if token_result.get('return_code') != 0:
        print(" 토큰 발급 실패")
        exit(1)
    
    access_token = token_result.get('token')
    print(f" 토큰 발급 성공: {access_token[:30]}...")
    
    # 2. 분봉차트 조회
    print("\n2. 주식분봉차트조회 (삼성전자 5분봉)")
    chart_params = {
        'stk_cd': '005930', # 종목코드 거래소별 종목코드 (KRX:039490,NXT:039490_NX,SOR:039490_AL)
        'tic_scope': '5', # 틱범위 1:1분, 3:3분, 5:5분, 10:10분, 15:15분, 30:30분, 45:45분, 60:60분
        'upd_stkpc_tp': '1', # 수정주가구분 0 or 1
    }
    
    print("요청 파라미터:")
    print(json.dumps(chart_params, indent=2, ensure_ascii=False))
    print()
    
    # 3. API 실행
    chart_result = fn_ka10080(token=access_token, data=chart_params)
    
    # 4. 결과 분석
    print("\n3. 결과 분석")
    if chart_result:
        if 'output' in chart_result:
            output_data = chart_result['output']
            print(f" 차트 데이터 수신 성공!")
            print(f"데이터 개수: {len(output_data)}개")
            
            if len(output_data) > 0:
                print("\n 최근 5개 데이터:")
                for i, item in enumerate(output_data[:5]):
                    print(f"{i+1}. 시간: {item.get('dt', '')}, 종가: {item.get('close', '')}, 거래량: {item.get('vol', '')}")
        else:
            print(" 예상과 다른 응답 구조")
    else:
        print(" API 호출 실패")
    
    # 다른 종목도 테스트
    print("\n4. 추가 테스트 - SK하이닉스 1분봉")
    chart_params2 = {
        'stk_cd': '000660',  # SK하이닉스
        'tic_scope': '1',    # 1분봉
        'upd_stkpc_tp': '1',
    }
    
    chart_result2 = fn_ka10080(token=access_token, data=chart_params2)
    
    if chart_result2 and 'output' in chart_result2:
        print(f" SK하이닉스 1분봉 데이터: {len(chart_result2['output'])}개")
    else:
        print(" SK하이닉스 데이터 조회 실패")