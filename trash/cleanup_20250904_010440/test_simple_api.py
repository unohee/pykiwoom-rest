#!/usr/bin/env python3
"""
간단한 키움 REST API 테스트
토큰 발급만 테스트
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pykiwoom_rest.kiwoom_rest import KiwoomRest


@patch.dict(os.environ, {
    'ACCOUNT_NO': 'test_account',
    'KIWOOM_APPKEY': 'test_appkey',
    'KIWOOM_APPSECRET': 'test_appsecret'
})
@patch('pykiwoom_rest.stock_api.StockAPI._get_access_token')
@patch('pykiwoom_rest.chart_api.ChartAPI._get_access_token')
@patch('pykiwoom_rest.ranking_api.RankingAPI._get_access_token')
def test_token_only(mock_ranking_token, mock_chart_token, mock_stock_token):
    """토큰 발급만 테스트 (모킹)"""
    
    # Mock 토큰 설정
    mock_token = 'mock_test_token_1234567890'
    mock_stock_token.return_value = mock_token
    mock_chart_token.return_value = mock_token
    mock_ranking_token.return_value = mock_token
    
    print("🔑 키움 REST API 토큰 발급 테스트")
    print("=" * 50)
    
    try:
        # 인스턴스 생성
        kiwoom = KiwoomRest()
        print(" KiwoomRest 인스턴스 생성 완료")
        
        # 토큰 메서드 호출 확인
        assert mock_stock_token.called
        print(f" 토큰 메서드 호출 확인 완료")
        
        assert True  # 테스트 통과
        
    except Exception as e:
        print(f" 오류: {e}")
        assert False, f"토큰 발급 실패: {e}"

if __name__ == "__main__":
    success = test_token_only()
    if success:
        print("\n API 키가 정상 작동합니다!")
    else:
        print("\n API 키에 문제가 있습니다.")
    
    sys.exit(0 if success else 1)