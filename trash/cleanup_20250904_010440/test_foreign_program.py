#!/usr/bin/env python3
"""
키움증권 REST API 테스트
- 주식외국인종목별매매동향 (ka10008)
- 종목일별프로그램매매추이요청 (ka90013)
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class KiwoomAPI:
    def __init__(self):
        self.base_url = "https://api.kiwoom.com"
        self.account_no = os.getenv("ACCOUNT_NO")
        self.appkey = os.getenv("KIWOOM_APPKEY")
        self.secretkey = os.getenv("KIWOOM_SECRET")  # 환경변수명 수정
        self.access_token = None
        
        # 토큰 발급
        self.get_access_token()
    
    def get_access_token(self):
        """OAuth2 토큰 발급"""
        url = f"{self.base_url}/oauth2/token"
        headers = {
            "Content-Type": "application/json;charset=UTF-8"
        }
        data = {
            "grant_type": "client_credentials",
            "appkey": self.appkey,
            "secretkey": self.secretkey
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            self.access_token = result.get("token")
            print(f"✅ 토큰 발급 성공: {self.access_token[:30]}...")
            return self.access_token
        else:
            print(f"❌ 토큰 발급 실패: {response.text}")
            return None
    
    def get_foreign_trading(self, stock_code):
        """주식외국인종목별매매동향 조회 (ka10008)"""
        url = f"{self.base_url}/api/dostk/frgnistt"
        
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "authorization": f"Bearer {self.access_token}",
            "api-id": "ka10008",
            "cont-yn": "N",
            "next-key": ""
        }
        
        data = {
            "stk_cd": stock_code
        }
        
        print(f"\n📊 외국인 매매동향 조회: {stock_code}")
        print(f"URL: {url}")
        print(f"Headers: {json.dumps(headers, indent=2, ensure_ascii=False)}")
        print(f"Body: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            print(f"응답 코드: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("return_code") == 0:
                    print("✅ 조회 성공")
                    # 최근 5일 데이터만 출력
                    if "stk_frgnr" in result and result["stk_frgnr"]:
                        print("\n최근 5일 외국인 매매 현황:")
                        for i, item in enumerate(result["stk_frgnr"][:5]):
                            print(f"  {item['dt']}: 종가 {item['close_pric']}, 변동수량 {item['chg_qty']}, 한도소진률 {item['limit_exh_rt']}%")
                    return result
                else:
                    print(f"❌ API 오류: {result.get('return_msg')}")
            else:
                print(f"❌ HTTP 오류: {response.text}")
                
        except Exception as e:
            print(f"❌ 예외 발생: {e}")
            
        return None
    
    def get_program_trading(self, stock_code):
        """종목일별프로그램매매추이요청 (ka90013)"""
        url = f"{self.base_url}/api/dostk/mrkcond"
        
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "authorization": f"Bearer {self.access_token}",
            "api-id": "ka90013",
            "cont-yn": "N",
            "next-key": ""
        }
        
        data = {
            "stk_cd": stock_code
        }
        
        print(f"\n📊 프로그램 매매추이 조회: {stock_code}")
        print(f"URL: {url}")
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            print(f"응답 코드: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("return_code") == 0:
                    print("✅ 조회 성공")
                    # 데이터 출력
                    return result
                else:
                    print(f"❌ API 오류: {result.get('return_msg')}")
            else:
                print(f"❌ HTTP 오류: {response.text}")
                
        except Exception as e:
            print(f"❌ 예외 발생: {e}")
            
        return None


if __name__ == "__main__":
    print("🚀 키움증권 REST API 테스트")
    print("="*50)
    
    # API 인스턴스 생성
    api = KiwoomAPI()
    
    if api.access_token:
        # 삼성전자 테스트
        stock_code = "005930"
        
        # 1. 외국인 매매동향 조회
        foreign_result = api.get_foreign_trading(stock_code)
        
        # 2. 프로그램 매매추이 조회  
        program_result = api.get_program_trading(stock_code)
        
        print("\n" + "="*50)
        print("테스트 완료")
    else:
        print("토큰 발급 실패로 테스트 중단")