#!/usr/bin/env python3
"""
Kiwoom REST API 연결 테스트
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pykiwoom_rest import KiwoomRest
from datetime import datetime
import json

def test_api_connection():
    """API 키 작동 여부 테스트"""
    
    print("=" * 60)
    print("🔍 Kiwoom REST API 연결 테스트 시작")
    print("=" * 60)
    
    # 1. 환경변수 확인
    print("\n1️⃣ 환경변수 확인")
    print("-" * 40)
    
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        print(f"✅ .env 파일 발견: {env_path}")
        
        # 환경변수 로드 확인
        from dotenv import load_dotenv
        load_dotenv(env_path)
        
        account_no = os.getenv('ACCOUNT_NO')
        appkey = os.getenv('KIWOOM_APPKEY')
        appsecret = os.getenv('KIWOOM_APPSECRET')
        
        print(f"✅ 계좌번호: {account_no[:4]}****" if account_no else "❌ 계좌번호 없음")
        print(f"✅ APP KEY: {appkey[:10]}..." if appkey else "❌ APP KEY 없음")
        print(f"✅ APP SECRET: {appsecret[:10]}..." if appsecret else "❌ APP SECRET 없음")
    else:
        print("❌ .env 파일이 없습니다")
        return False
    
    # 2. KiwoomRest 인스턴스 생성
    print("\n2️⃣ KiwoomRest 인스턴스 생성")
    print("-" * 40)
    
    try:
        kiwoom = KiwoomRest()
        print("✅ KiwoomRest 인스턴스 생성 성공")
    except Exception as e:
        print(f"❌ 인스턴스 생성 실패: {e}")
        return False
    
    # 3. 연결 상태 확인
    print("\n3️⃣ API 연결 상태 확인")
    print("-" * 40)
    
    try:
        connection_status = kiwoom.verify_connection()
        
        if connection_status.get('connected'):
            print("✅ API 연결 성공!")
            print(f"   - 토큰 유효: {connection_status.get('token_valid')}")
            print(f"   - API 응답: {connection_status.get('api_responsive')}")
            print(f"   - 테스트 응답: {connection_status.get('test_response')}")
        else:
            print(f"❌ API 연결 실패")
            print(f"   - 오류: {connection_status.get('error')}")
            if 'response_code' in connection_status:
                print(f"   - 응답 코드: {connection_status.get('response_code')}")
            return False
            
    except Exception as e:
        print(f"❌ 연결 테스트 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. 실제 API 호출 테스트
    print("\n4️⃣ 실제 API 호출 테스트")
    print("-" * 40)
    
    test_stocks = [
        ("005930", "삼성전자"),
        ("000660", "SK하이닉스"),
        ("035720", "카카오")
    ]
    
    for stock_code, stock_name in test_stocks:
        print(f"\n📊 {stock_name}({stock_code}) 정보 조회")
        
        try:
            # 현재가 조회
            result = kiwoom.get_stock_price(stock_code)
            
            if result and result.get('rt_cd') == '0':
                output = result.get('output', {})
                print(f"   ✅ 조회 성공")
                print(f"   - 현재가: {output.get('stck_prpr', 'N/A')}원")
                print(f"   - 전일대비: {output.get('prdy_vrss', 'N/A')}원 ({output.get('prdy_ctrt', 'N/A')}%)")
                print(f"   - 거래량: {output.get('acml_vol', 'N/A')}")
                print(f"   - 시가: {output.get('stck_oprc', 'N/A')}원")
                print(f"   - 고가: {output.get('stck_hgpr', 'N/A')}원")
                print(f"   - 저가: {output.get('stck_lwpr', 'N/A')}원")
            else:
                error_msg = result.get('msg1', '알 수 없는 오류') if result else '응답 없음'
                print(f"   ⚠️ 조회 실패: {error_msg}")
                
        except Exception as e:
            print(f"   ❌ API 호출 오류: {e}")
    
    # 5. 호가 정보 테스트
    print("\n5️⃣ 호가 정보 조회 테스트")
    print("-" * 40)
    
    try:
        orderbook = kiwoom.get_stock_orderbook("005930")
        
        if orderbook and orderbook.get('rt_cd') == '0':
            output1 = orderbook.get('output1', {})
            print("✅ 호가 조회 성공")
            print(f"   매도호가1: {output1.get('askp1', 'N/A')}원 (잔량: {output1.get('askp_rsqn1', 'N/A')})")
            print(f"   매수호가1: {output1.get('bidp1', 'N/A')}원 (잔량: {output1.get('bidp_rsqn1', 'N/A')})")
        else:
            print(f"⚠️ 호가 조회 실패: {orderbook.get('msg1', '알 수 없는 오류') if orderbook else '응답 없음'}")
            
    except Exception as e:
        print(f"❌ 호가 조회 오류: {e}")
    
    # 6. 차트 데이터 테스트
    print("\n6️⃣ 차트 데이터 조회 테스트")
    print("-" * 40)
    
    try:
        today = datetime.now().strftime("%Y%m%d")
        minute_chart = kiwoom.get_minute_chart("005930", interval=5, end_date=today)
        
        if minute_chart and minute_chart.get('rt_cd') == '0':
            output2 = minute_chart.get('output2', [])
            print(f"✅ 5분봉 차트 조회 성공")
            print(f"   - 데이터 개수: {len(output2)}개")
            
            if output2 and len(output2) > 0:
                latest = output2[0]
                print(f"   - 최근 데이터: {latest.get('stck_bsop_date', '')} {latest.get('stck_cntg_hour', '')}")
                print(f"     종가: {latest.get('stck_prpr', 'N/A')}원, 거래량: {latest.get('acml_vol', 'N/A')}")
        else:
            print(f"⚠️ 차트 조회 실패: {minute_chart.get('msg1', '알 수 없는 오류') if minute_chart else '응답 없음'}")
            
    except Exception as e:
        print(f"❌ 차트 조회 오류: {e}")
    
    print("\n" + "=" * 60)
    print("✅ API 테스트 완료!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_api_connection()
    sys.exit(0 if success else 1)