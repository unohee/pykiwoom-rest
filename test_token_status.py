#!/usr/bin/env python3
"""
토큰 상태 확인 테스트 스크립트
"""

from pathlib import Path
from pykiwoom_rest import KiwoomRest

# KiwoomRest 초기화
print("=" * 60)
print("KiwoomRest 초기화 중...")
print("=" * 60)

env_path = Path(__file__).parent / ".env"
kiwoom = KiwoomRest(env_path=str(env_path))

print("\n✅ KiwoomRest 초기화 완료")

# 주식 가격 조회 (토큰 자동 발급)
print("\n" + "=" * 60)
print("주식 가격 조회 (토큰 자동 발급 테스트)")
print("=" * 60)

try:
    price_info = kiwoom.get_stock_price("005930")
    print(f"✅ 삼성전자 현재가 조회 성공")
    print(f"   - 종목코드: {price_info.get('stk_cd', 'N/A')}")
    print(f"   - 종목명: {price_info.get('stk_nm', 'N/A')}")
    print(f"   - 현재가: {price_info.get('cur_prc', 'N/A')}")
except Exception as e:
    print(f"❌ 주식 가격 조회 실패: {e}")

# 토큰 상태 확인
print("\n" + "=" * 60)
print("토큰 상태 조회")
print("=" * 60)

token_status = kiwoom.get_token_status()

print(f"\n📋 토큰 상태:")
print(f"   - 토큰 보유: {token_status['has_token']}")
print(f"   - 유효: {token_status['is_valid']}")
print(f"   - 토큰 프리픽스: {token_status['token_prefix']}")
print(f"   - 만료 시간: {token_status['expires_at']}")
print(f"   - 남은 시간: {token_status['time_to_expiry']}초")
print(f"   - 갱신 필요: {token_status['needs_refresh']}")

# 결과 검증
print("\n" + "=" * 60)
print("검증 결과")
print("=" * 60)

if token_status['has_token']:
    print("✅ 토큰이 존재합니다")
else:
    print("❌ 토큰이 없습니다")

if token_status['is_valid']:
    print("✅ 토큰이 유효합니다")
else:
    print("❌ 토큰이 유효하지 않습니다")

if token_status['expires_at']:
    print(f"✅ 만료 시간이 설정되어 있습니다: {token_status['expires_at']}")
else:
    print("❌ 만료 시간이 없습니다")

print("\n" + "=" * 60)
print("테스트 완료")
print("=" * 60)
