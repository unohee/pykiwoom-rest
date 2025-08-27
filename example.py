"""
PyKiwoom-Rest 사용 예제
작성일: 2025-01-15
"""

from kiwoom_rest import KiwoomRest
from datetime import datetime, timedelta
import pandas as pd


def example_basic_usage():
    """기본 사용 예제"""
    print("\n### 기본 사용 예제 ###\n")
    
    # KiwoomRest 인스턴스 생성
    kiwoom = KiwoomRest(".env")
    
    # 1. 주식 현재가 조회
    stock_code = "005930"  # 삼성전자
    price_info = kiwoom.get_stock_price(stock_code)
    
    if 'output' in price_info:
        output = price_info['output']
        print(f"종목코드: {stock_code}")
        print(f"종목명: {output.get('prdt_abrv_name')}")
        print(f"현재가: {output.get('stck_prpr')}원")
        print(f"전일대비: {output.get('prdy_vrss')}원")
        print(f"등락률: {output.get('prdy_ctrt')}%")
        print(f"거래량: {output.get('acml_vol')}")


def example_minute_chart():
    """분봉 데이터 조회 예제"""
    print("\n### 분봉 데이터 조회 예제 ###\n")
    
    kiwoom = KiwoomRest()
    
    # 최근 7일간 5분봉 데이터 조회
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    result = kiwoom.get_minute_chart(
        stock_code="005930",
        interval=5,  # 5분봉
        start_date=start_date.strftime("%Y%m%d"),
        end_date=end_date.strftime("%Y%m%d")
    )
    
    if 'output2' in result and result['output2']:
        # 데이터프레임으로 변환
        df = pd.DataFrame(result['output2'])
        df['datetime'] = pd.to_datetime(df['stck_bsop_date'] + df['stck_cntg_hour'])
        df[['open', 'high', 'low', 'close', 'volume']] = df[['stck_oprc', 'stck_hgpr', 'stck_lwpr', 'stck_prpr', 'acml_vol']].astype(float)
        
        print(f"조회된 5분봉 개수: {len(df)}")
        print("\n최근 5개 5분봉:")
        print(df[['datetime', 'open', 'high', 'low', 'close', 'volume']].head())


def example_paginated_minute_chart():
    """페이지네이션을 사용한 대량 분봉 데이터 조회"""
    print("\n### 페이지네이션 분봉 조회 예제 ###\n")
    
    kiwoom = KiwoomRest()
    
    # 최근 30일간 1분봉 데이터 모두 조회
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    print(f"조회 기간: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
    print("1분봉 데이터 수집 중...")
    
    data = kiwoom.get_minute_chart_paginated(
        stock_code="005930",
        interval=1,  # 1분봉
        start_date=start_date.strftime("%Y%m%d"),
        end_date=end_date.strftime("%Y%m%d"),
        max_records=500  # 최대 500개만 조회
    )
    
    if data:
        # 데이터프레임으로 변환
        df = pd.DataFrame(data)
        df['datetime'] = pd.to_datetime(df['date'] + df['time'])
        df = df.set_index('datetime')
        
        print(f"\n총 {len(df)}개의 1분봉 데이터 수집 완료")
        print(f"기간: {df.index.min()} ~ {df.index.max()}")
        print(f"\n통계:")
        print(f"  평균가: {df['close'].mean():.0f}원")
        print(f"  최고가: {df['high'].max():.0f}원")
        print(f"  최저가: {df['low'].min():.0f}원")
        print(f"  평균 거래량: {df['volume'].mean():.0f}주")


def example_institutional_trading():
    """기관/외국인 매매 동향 조회"""
    print("\n### 기관/외국인 매매 동향 예제 ###\n")
    
    kiwoom = KiwoomRest()
    
    # 최근 30일간 기관매매 동향
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    result = kiwoom.get_institutional_daily_trading(
        stock_code="005930",
        start_date=start_date.strftime("%Y%m%d"),
        end_date=end_date.strftime("%Y%m%d")
    )
    
    if 'output' in result and result['output']:
        df = pd.DataFrame(result['output'])
        
        # 컬럼 타입 변환 (실제 컬럼명은 API 응답에 따라 조정 필요)
        numeric_cols = ['inst_ntby_qty', 'frgn_ntby_qty', 'indv_ntby_qty']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        print("최근 10일 기관/외국인 순매수 동향:")
        print(df[['stck_bsop_date'] + [col for col in numeric_cols if col in df.columns]].head(10))


def example_realtime_monitoring():
    """실시간 모니터링 예제 (폴링 방식)"""
    print("\n### 실시간 모니터링 예제 ###\n")
    
    import time
    
    kiwoom = KiwoomRest()
    stock_codes = ["005930", "000660", "035720"]  # 삼성전자, SK하이닉스, 카카오
    
    print("실시간 모니터링 시작 (3초 간격, 5회)")
    print("-" * 50)
    
    for i in range(5):
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 업데이트 #{i+1}")
        
        for code in stock_codes:
            try:
                result = kiwoom.get_stock_price(code)
                if 'output' in result:
                    output = result['output']
                    print(f"  {code} - {output.get('prdt_abrv_name', 'N/A'):10s}: "
                          f"{output.get('stck_prpr', 'N/A'):>8s}원 "
                          f"({output.get('prdy_vrss', 'N/A'):>6s}) "
                          f"{output.get('prdy_ctrt', 'N/A'):>6s}%")
            except Exception as e:
                print(f"  {code} - 조회 실패: {e}")
        
        if i < 4:  # 마지막 반복에서는 대기하지 않음
            time.sleep(3)
    
    print("\n모니터링 종료")


def example_top_rankings():
    """상위 종목 조회 예제"""
    print("\n### 상위 종목 조회 예제 ###\n")
    
    kiwoom = KiwoomRest()
    
    # 1. 거래량 상위
    print("거래량 상위 종목:")
    try:
        result = kiwoom.get_volume_top()
        if 'output' in result and result['output']:
            for i, item in enumerate(result['output'][:5], 1):
                print(f"  {i}. {item.get('hts_kor_isnm', 'N/A')} ({item.get('mksc_shrn_iscd', 'N/A')})")
                print(f"     현재가: {item.get('stck_prpr', 'N/A')}원, "
                      f"거래량: {item.get('acml_vol', 'N/A')}")
    except Exception as e:
        print(f"  조회 실패: {e}")
    
    print("\n외국인 순매수 상위:")
    try:
        result = kiwoom.get_foreign_top_buy()
        if 'output' in result and result['output']:
            for i, item in enumerate(result['output'][:5], 1):
                print(f"  {i}. {item.get('hts_kor_isnm', 'N/A')} ({item.get('mksc_shrn_iscd', 'N/A')})")
                print(f"     순매수: {item.get('frgn_ntby_qty', 'N/A')}주")
    except Exception as e:
        print(f"  조회 실패: {e}")


def main():
    """모든 예제 실행"""
    print("=" * 60)
    print("PyKiwoom-Rest 사용 예제")
    print("=" * 60)
    
    # 각 예제 실행
    example_basic_usage()
    example_minute_chart()
    example_paginated_minute_chart()
    example_institutional_trading()
    example_top_rankings()
    # example_realtime_monitoring()  # 시간이 걸리므로 주석 처리
    
    print("\n" + "=" * 60)
    pass
    print("=" * 60)


if __name__ == "__main__":
    main()