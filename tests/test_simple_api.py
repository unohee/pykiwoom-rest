#!/usr/bin/env python3
"""
간단한 키움 REST API 테스트
토큰 발급만 테스트
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.pykiwoom_rest.kiwoom_rest import KiwoomRest

def test_token_only():
    """토큰 발급만 테스트"""
    
    print("🔑 키움 REST API 토큰 발급 테스트")
    print("=" * 50)
    
    try:
        # 인스턴스 생성
        kiwoom = KiwoomRest()
        print("✅ KiwoomRest 인스턴스 생성 완료")
        
        # 토큰 발급
        token = kiwoom._get_access_token()
        print(f"✅ 토큰 발급 성공!")
        print(f"   토큰: {token[:20]}...")
        print(f"   만료시간: {kiwoom.token_expires}")
        
        return True
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

if __name__ == "__main__":
    success = test_token_only()
    if success:
        print("\n🎉 API 키가 정상 작동합니다!")
    else:
        print("\n❌ API 키에 문제가 있습니다.")
    
    sys.exit(0 if success else 1)