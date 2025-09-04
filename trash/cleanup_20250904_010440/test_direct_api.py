#!/usr/bin/env python3
"""
직접 API 키로 키움 REST API 테스트
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pykiwoom_rest.kiwoom_rest import KiwoomRest

@pytest.mark.integration
def test_direct_keys():
    """직접 API 키로 테스트"""
    
    print("🔑 키움 REST API 직접 키 테스트")
    print("=" * 50)
    
    try:
        # 직접 API 키 전달
        kiwoom = KiwoomRest(
            account_no="63513804",
            appkey="Px3ffmslMwr3qWVkwzW9yFbuEkbIKkwwiwoo4UWICYg",
            appsecret="bV4Dpr-5u9T3zWoRHbGOkU5O0uPxF3VPMJfyfrs08Uc"
        )
        print(" KiwoomRest 인스턴스 생성 완료")
        
        # 토큰 발급
        token = kiwoom._get_access_token()
        print(f" 토큰 발급 성공!")
        print(f"   토큰: {token[:30]}...")
        print(f"   만료시간: {kiwoom.token_expires}")
        
        assert True  # 테스트 통과
        
    except Exception as e:
        print(f" 오류: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"API 키 테스트 실패: {e}"

if __name__ == "__main__":
    success = test_direct_keys()
    if success:
        print("\n API 키가 정상 작동합니다!")
        print("키움증권 REST API 토큰 발급 성공 ")
    else:
        print("\n API 키에 문제가 있습니다.")
    
    sys.exit(0 if success else 1)