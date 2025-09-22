#!/usr/bin/env python3
"""
프로그램매매 추세 분석기 (고도화 버전)
날짜: 2025-01-28
목적: 장 시작부터 현재까지 프로그램매매 추세를 스마트하게 분석
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import sys
from datetime import datetime
from typing import Dict, List, Tuple
import numpy as np
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# .env 파일 로드
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

from pykiwoom_rest import KiwoomRest

# 환경변수 설정
ACCOUNT_NO = os.getenv("ACCOUNT_NO")
KIWOOM_APPKEY = os.getenv("KIWOOM_APPKEY")
KIWOOM_APPSECRET = os.getenv("KIWOOM_APPSECRET")

if not all([ACCOUNT_NO, KIWOOM_APPKEY, KIWOOM_APPSECRET]):
    print("ERROR: 환경변수가 설정되지 않았습니다.")
    sys.exit(1)


class ProgramTradingTrendAnalyzer:
    """프로그램매매 추세 분석 클래스"""

    def __init__(self):
        self.agent = KiwoomRest(
            account_no=ACCOUNT_NO,
            appkey=KIWOOM_APPKEY,
            appsecret=KIWOOM_APPSECRET,
            env_path=env_path,
            use_mock=False,
        )

    def parse_amount(self, val) -> int:
        """금액 문자열을 정수로 변환 (음수 처리 포함)"""
        if isinstance(val, str):
            # -- 기호는 음수를 의미
            is_negative = val.startswith('--') or (val.startswith('-') and not val.startswith('--'))

            # 모든 기호 제거
            val_clean = val.replace("+", "").replace(",", "").replace("-", "")

            try:
                amt = int(val_clean)
                return -amt if is_negative else amt
            except:
                return 0
        return 0

    def fetch_all_day_data(self, stock_code: str, date: str = None) -> List[Dict]:
        """장 시작부터 현재까지 모든 데이터 수집"""
        if date is None:
            date = datetime.now().strftime("%Y%m%d")

        print(f"전체 데이터 조회 중... [{stock_code}] {date}")
        print("  (Rate limiting으로 인해 시간이 걸릴 수 있습니다)")

        try:
            result = self.agent.get_hourly_program_trading_paginated(
                stock_code, date, "1"  # 1: 금액 기준
            )

            if 'output' in result and result['output']:
                # 시간순 정렬
                data = sorted(result['output'], key=lambda x: x.get('tm', '000000'))

                # 장 시작(09:00) 이후 데이터만 필터링
                filtered_data = [d for d in data if d.get('tm', '000000') >= '090000']

                print(f"  → {len(filtered_data)}개 시점 데이터 수집 완료")
                return filtered_data
            else:
                print("  → 데이터 없음")
                return []

        except Exception as e:
            # 일반적이지 않은 오류만 출력
            if "429" not in str(e) and "rate" not in str(e).lower():
                print(f"  → 오류: {e}")
            else:
                print("  → Rate limiting으로 인한 일시적 지연 발생")
            return []

    def analyze_trend_smart(self, data: List[Dict]) -> Dict:
        """스마트한 추세 분석"""
        if not data:
            return {"trend": "데이터 없음", "details": {}}

        # 순매수금액 추출
        net_amounts = [self.parse_amount(d.get('prm_netprps_amt', '0')) for d in data]
        net_quantities = [self.parse_amount(d.get('prm_netprps_qty', '0')) for d in data]

        if len(net_amounts) < 2:
            return {"trend": "데이터 부족", "details": {}}

        # 1. 전반부/후반부 평균 비교
        mid_point = len(net_amounts) // 2
        first_half_avg = np.mean(net_amounts[:mid_point]) if mid_point > 0 else 0
        second_half_avg = np.mean(net_amounts[mid_point:]) if mid_point < len(net_amounts) else 0

        # 2. 선형 회귀를 통한 기울기 계산
        x = np.arange(len(net_amounts))
        coefficients = np.polyfit(x, net_amounts, 1)
        slope = coefficients[0]  # 기울기

        # 3. 이동평균 계산 (10개 구간)
        window = max(1, len(net_amounts) // 10)
        if window > 1 and len(net_amounts) >= window:
            ma = np.convolve(net_amounts, np.ones(window)/window, mode='valid')
            ma_trend_up = sum(ma[i] < ma[i+1] for i in range(len(ma)-1)) > len(ma) // 2
        else:
            ma_trend_up = None

        # 4. 변동성 계산
        volatility = np.std(net_amounts) if len(net_amounts) > 1 else 0
        avg_amount = np.mean(net_amounts)
        cv = (volatility / avg_amount * 100) if avg_amount != 0 else 0  # 변동계수

        # 5. 구간별 증감 패턴 분석
        changes = [net_amounts[i+1] - net_amounts[i] for i in range(len(net_amounts)-1)]
        positive_changes = sum(1 for c in changes if c > 0)
        negative_changes = sum(1 for c in changes if c < 0)

        # 6. 추세 판단 (종합)
        trend_indicators = {
            'half_comparison': second_half_avg - first_half_avg,
            'slope': slope,
            'ma_trend': ma_trend_up,
            'positive_ratio': positive_changes / len(changes) if changes else 0
        }

        # 추세 결정 로직
        if abs(cv) < 5:  # 변동성이 매우 낮음
            trend = "횡보"
            confidence = "높음"
        elif slope > 0 and second_half_avg > first_half_avg * 1.05:
            trend = "강한 상승"
            confidence = "높음" if trend_indicators['positive_ratio'] > 0.6 else "중간"
        elif slope > 0 and second_half_avg > first_half_avg:
            trend = "상승"
            confidence = "중간"
        elif slope < 0 and second_half_avg < first_half_avg * 0.95:
            trend = "강한 하락"
            confidence = "높음" if trend_indicators['positive_ratio'] < 0.4 else "중간"
        elif slope < 0 and second_half_avg < first_half_avg:
            trend = "하락"
            confidence = "중간"
        else:
            trend = "횡보"
            confidence = "낮음"

        # 결과 반환
        return {
            "trend": trend,
            "confidence": confidence,
            "details": {
                "first_half_avg": first_half_avg,
                "second_half_avg": second_half_avg,
                "change_ratio": ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg != 0 else 0,
                "slope": slope,
                "volatility_cv": cv,
                "positive_change_ratio": trend_indicators['positive_ratio'] * 100,
                "total_change": net_amounts[-1] - net_amounts[0],
                "start_value": net_amounts[0],
                "end_value": net_amounts[-1],
                "max_value": max(net_amounts),
                "min_value": min(net_amounts),
                "data_points": len(net_amounts)
            },
            "quantities": {
                "start": net_quantities[0] if net_quantities else 0,
                "end": net_quantities[-1] if net_quantities else 0,
                "change": (net_quantities[-1] - net_quantities[0]) if net_quantities and len(net_quantities) > 1 else 0
            },
            "time_range": {
                "start": data[0].get('tm', 'N/A') if data else 'N/A',
                "end": data[-1].get('tm', 'N/A') if data else 'N/A'
            }
        }

    def analyze_stock(self, stock_code: str, stock_name: str, date: str = None) -> Dict:
        """특정 종목의 프로그램매매 추세 분석"""
        print(f"\n{'='*70}")
        print(f"📊 {stock_name}({stock_code}) 프로그램매매 추세 분석")
        print(f"{'='*70}")

        # 데이터 수집
        data = self.fetch_all_day_data(stock_code, date)

        if not data:
            return {"stock_code": stock_code, "stock_name": stock_name, "trend": "데이터 없음"}

        # 추세 분석
        analysis = self.analyze_trend_smart(data)

        # 결과 출력
        print(f"\n⏰ 시간 범위: {analysis['time_range']['start']} ~ {analysis['time_range']['end']}")
        print(f"📈 데이터 포인트: {analysis['details']['data_points']}개")

        print(f"\n💰 순매수금액 분석:")
        print(f"  • 시작: {analysis['details']['start_value']:,}백만원")
        print(f"  • 현재: {analysis['details']['end_value']:,}백만원")
        print(f"  • 변화: {analysis['details']['total_change']:+,}백만원")
        print(f"  • 최대: {analysis['details']['max_value']:,}백만원")
        print(f"  • 최소: {analysis['details']['min_value']:,}백만원")

        print(f"\n📊 구간 분석:")
        print(f"  • 전반부 평균: {analysis['details']['first_half_avg']:,.0f}백만원")
        print(f"  • 후반부 평균: {analysis['details']['second_half_avg']:,.0f}백만원")
        print(f"  • 변화율: {analysis['details']['change_ratio']:+.2f}%")

        print(f"\n📉 추세 지표:")
        print(f"  • 선형 기울기: {analysis['details']['slope']:+.2f}")
        print(f"  • 변동성(CV): {analysis['details']['volatility_cv']:.2f}%")
        print(f"  • 상승 비율: {analysis['details']['positive_change_ratio']:.1f}%")

        print(f"\n🎯 추세 판단: **{analysis['trend']}** (신뢰도: {analysis['confidence']})")

        print(f"\n📦 순매수수량:")
        print(f"  • 시작: {analysis['quantities']['start']:,}주")
        print(f"  • 현재: {analysis['quantities']['end']:,}주")
        print(f"  • 변화: {analysis['quantities']['change']:+,}주")

        return {
            "stock_code": stock_code,
            "stock_name": stock_name,
            **analysis
        }


def main():
    """메인 실행 함수"""
    analyzer = ProgramTradingTrendAnalyzer()

    print(f"\n현재 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 분석할 종목들
    stocks = [
        ("005930", "삼성전자"),
        ("000660", "SK하이닉스")
    ]

    results = []
    for stock_code, stock_name in stocks:
        result = analyzer.analyze_stock(stock_code, stock_name)
        results.append(result)

    # 종합 비교
    print(f"\n{'='*70}")
    print(f"📊 종합 비교")
    print(f"{'='*70}")

    for r in results:
        if 'trend' in r:
            print(f"\n{r['stock_name']}({r['stock_code']}):")
            print(f"  추세: {r.get('trend', 'N/A')}")
            if 'confidence' in r:
                print(f"  신뢰도: {r.get('confidence', 'N/A')}")
            if 'details' in r:
                print(f"  순매수금액 변화: {r['details'].get('total_change', 0):+,}백만원")
                print(f"  전/후반부 변화율: {r['details'].get('change_ratio', 0):+.2f}%")


if __name__ == "__main__":
    main()