#!/usr/bin/env python3
"""
수정된 노트북 셀 테스트 (Cell 10, 16, 17)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta

# 환경 설정
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

ACCOUNT_NO = os.getenv("ACCOUNT_NO")
KIWOOM_APPKEY = os.getenv("KIWOOM_APPKEY")
KIWOOM_APPSECRET = os.getenv("KIWOOM_APPSECRET")

from pykiwoom_rest import KiwoomRest

print("=" * 60)
print("수정된 노트북 셀 테스트")
print("=" * 60)

# KiwoomRest 초기화
kiwoom = KiwoomRest(
    account_no=ACCOUNT_NO,
    appkey=KIWOOM_APPKEY,
    appsecret=KIWOOM_APPSECRET,
    env_path=env_path,
    use_mock=False,
)

print("✅ KiwoomRest 초기화 완료\n")

# 토큰 발급
print("🔑 토큰 발급 중...")
token_info = kiwoom.get_access_token()
print(f"✅ 토큰 발급 완료\n")

stock_code = "005930"
stock_name = "삼성전자"

# ========================================
# Cell 10: ka10005 일봉 차트 테스트
# ========================================
print("=" * 60)
print("Cell 10: ka10005 일봉 차트 조회 테스트")
print("=" * 60)

try:
    daily_chart = kiwoom.chart_api.get_daily_weekly_monthly_minute_chart(
        stock_code=stock_code,
        period="D",  # D=일봉
        start_date=(datetime.now() - timedelta(days=30)).strftime("%Y%m%d"),
        end_date=datetime.now().strftime("%Y%m%d")
    )

    print("\n📈 일봉 데이터 (최근 5일):")
    if daily_chart and 'stk_ddwkmm' in daily_chart:
        import pandas as pd
        df = pd.DataFrame(daily_chart['stk_ddwkmm'][:5])
        print(df[['date', 'open_pric', 'high_pric', 'low_pric', 'close_pric', 'trde_qty']].to_string(index=False))
        print("\n✅ Cell 10 테스트 성공")
    else:
        print("❌ 일봉 데이터 조회 실패")
        print(f"   응답: {daily_chart}")
        print("\n❌ Cell 10 테스트 실패")
except Exception as e:
    print(f"\n❌ Cell 10 테스트 실패: {e}")
    import traceback
    traceback.print_exc()

# ========================================
# Cell 16: 투자자별 매매동향 API 이슈 안내
# ========================================
print("\n" + "=" * 60)
print("Cell 16: 투자자별 매매동향 API 이슈 안내")
print("=" * 60)

print("⚠️  투자자별 매매동향 API 안내")
print("=" * 60)
print("❌ 현재 get_stock_investor_trading() 메서드는 TR 코드 매핑이 잘못되어 있습니다.")
print()
print("📋 문제점:")
print("   - 현재 ka10058(투자자별일별매매종목요청)로 매핑되어 있음")
print("   - ka10058은 특정 종목이 아니라 투자자별 매매 종목 리스트를 조회하는 API")
print("   - stock_code 파라미터 대신 strt_dt, end_dt, trde_tp, mrkt_tp, invsr_tp, stex_tp 필요")
print()
print("✅ 대안:")
print("   1. 외국인 매매동향: get_foreign_trading(stock_code) - ka10008")
print("   2. 기관별 매매동향: get_stock_member_trading(stock_code) - ka10006")
print("   3. 장중 투자자별 매매: 전체 시장 순위 조회 - ka10063")
print()
print("   → Cell 17에서 외국인 매매동향(ka10008)을 확인하세요.")
print("=" * 60)
print("✅ Cell 16 테스트 성공 (경고 메시지 표시)")

# ========================================
# Cell 17: 외국인 매매동향 테스트
# ========================================
print("\n" + "=" * 60)
print("Cell 17: 외국인 매매동향 조회 테스트")
print("=" * 60)

try:
    print(f"\n🌏 {stock_name} 외국인 매매동향 (ka10008)")
    print("=" * 60)

    foreign_trading = kiwoom.get_foreign_trading(stock_code)

    if foreign_trading and 'stk_frgnr' in foreign_trading:
        import pandas as pd
        df = pd.DataFrame(foreign_trading['stk_frgnr'][:10])
        print("최근 10일 외국인 매매 동향:")
        print(df[['dt', 'wght', 'trde_qty', 'chg_qty']].to_string(index=False))

        print("\n📋 필드 설명:")
        print("   dt: 일자")
        print("   wght: 비중 (%)")
        print("   trde_qty: 거래량")
        print("   chg_qty: 변동수량 (순매수량)")
        print("\n✅ Cell 17 테스트 성공")
    else:
        print("❌ 외국인 매매동향 조회 실패")
        print(f"   응답: {foreign_trading}")
        print("\n❌ Cell 17 테스트 실패")
except Exception as e:
    print(f"\n❌ Cell 17 테스트 실패: {e}")
    import traceback
    traceback.print_exc()

# ========================================
# 결과 요약
# ========================================
print("\n" + "=" * 60)
print("테스트 완료")
print("=" * 60)
print("\n수정 사항:")
print("  ✅ Cell 10: 'output' → 'stk_ddwkmm', 'volume' → 'trde_qty'")
print("  ✅ Cell 16: API 이슈 안내 메시지로 대체")
print("  ✅ Cell 17: 'netprps_qty' → 'chg_qty'")
