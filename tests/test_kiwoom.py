"""
PyKiwoom-Rest 테스트 코드
작성일: 2025-01-15
"""

import pytest
from pykiwoom_rest import KiwoomRest
from datetime import datetime, timedelta
import json
pytestmark = pytest.mark.integration

def test_basic_connection():
    """기본 연결 테스트"""
    print("=" * 50)
    print("1. 기본 연결 테스트")
    print("=" * 50)
    
    try:
        kiwoom = KiwoomRest(".env")
        print(f"✓ 계좌번호: {kiwoom.account_no}")
        print(f"✓ APPKEY: {kiwoom.appkey[:10]}...")
        print(f"✓ 연결 성공\n")
        return kiwoom
    except Exception as e:
        print(f"✗ 연결 실패: {e}\n")
        return None


def test_stock_price(kiwoom, stock_code="005930"):
    """주식 기본정보 조회 테스트"""
    print("=" * 50)
    print(f"2. 주식 기본정보 조회 (종목: {stock_code})")
    print("=" * 50)
    
    try:
        result = kiwoom.get_stock_price(stock_code)
        if 'output' in result:
            output = result['output']
            print(f"종목명: {output.get('prdt_abrv_name', 'N/A')}")
            print(f"현재가: {output.get('stck_prpr', 'N/A')}")
            print(f"전일대비: {output.get('prdy_vrss', 'N/A')}")
            print(f"등락률: {output.get('prdy_ctrt', 'N/A')}%")
            print("✓ 조회 성공\n")
        else:
            print(f"✗ 데이터 없음: {result}\n")
    except Exception as e:
        print(f"✗ 조회 실패: {e}\n")


def test_stock_orderbook(kiwoom, stock_code="005930"):
    """주식 호가 조회 테스트"""
    print("=" * 50)
    print(f"3. 주식 호가 조회 (종목: {stock_code})")
    print("=" * 50)
    
    try:
        result = kiwoom.get_stock_orderbook(stock_code)
        if 'output1' in result:
            output = result['output1']
            print("매도호가:")
            for i in range(1, 6):
                price = output.get(f'askp{i}', 'N/A')
                volume = output.get(f'askp_rsqn{i}', 'N/A')
                print(f"  {i}차: {price}원 / {volume}주")
            
            print("\n매수호가:")
            for i in range(1, 6):
                price = output.get(f'bidp{i}', 'N/A')
                volume = output.get(f'bidp_rsqn{i}', 'N/A')
                print(f"  {i}차: {price}원 / {volume}주")
            print("✓ 조회 성공\n")
        else:
            print(f"✗ 데이터 없음: {result}\n")
    except Exception as e:
        print(f"✗ 조회 실패: {e}\n")


def test_minute_chart(kiwoom, stock_code="005930"):
    """분봉차트 조회 테스트"""
    print("=" * 50)
    print(f"4. 분봉차트 조회 (종목: {stock_code})")
    print("=" * 50)
    
    try:
        # 최근 7일간 5분봉 조회
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
        
        result = kiwoom.get_minute_chart(
            stock_code=stock_code,
            interval=5,
            start_date=start_date,
            end_date=end_date
        )
        
        if 'output2' in result and result['output2']:
            data = result['output2']
            print(f"조회된 데이터 수: {len(data)}개")
            print("\n최근 5개 5분봉:")
            for item in data[:5]:
                print(f"  {item.get('stck_bsop_date')} {item.get('stck_cntg_hour')}")
                print(f"    시가: {item.get('stck_oprc')}, 고가: {item.get('stck_hgpr')}")
                print(f"    저가: {item.get('stck_lwpr')}, 종가: {item.get('stck_prpr')}")
                print(f"    거래량: {item.get('acml_vol')}")
            print("✓ 조회 성공\n")
        else:
            print(f"✗ 데이터 없음: {result}\n")
    except Exception as e:
        print(f"✗ 조회 실패: {e}\n")


def test_minute_chart_paginated(kiwoom, stock_code="005930"):
    """분봉차트 페이지네이션 테스트"""
    print("=" * 50)
    print(f"5. 분봉차트 페이지네이션 (종목: {stock_code})")
    print("=" * 50)
    
    try:
        # 최근 30일간 1분봉 조회 (최대 100개)
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        
        print(f"기간: {start_date} ~ {end_date}")
        print("1분봉 데이터 수집 중...")
        
        data = kiwoom.get_minute_chart_paginated(
            stock_code=stock_code,
            interval=1,
            start_date=start_date,
            end_date=end_date,
            max_records=100
        )
        
        print(f"조회된 데이터 수: {len(data)}개")
        
        if data:
            print("\n최초 데이터:")
            print(f"  날짜/시간: {data[0]['date']} {data[0]['time']}")
            print(f"  OHLC: {data[0]['open']}, {data[0]['high']}, {data[0]['low']}, {data[0]['close']}")
            print(f"  거래량: {data[0]['volume']}")
            
            print("\n최종 데이터:")
            print(f"  날짜/시간: {data[-1]['date']} {data[-1]['time']}")
            print(f"  OHLC: {data[-1]['open']}, {data[-1]['high']}, {data[-1]['low']}, {data[-1]['close']}")
            print(f"  거래량: {data[-1]['volume']}")
            
            print("✓ 페이지네이션 성공\n")
        else:
            print("✗ 데이터 없음\n")
    except Exception as e:
        print(f"✗ 조회 실패: {e}\n")


def test_daily_institutional_trading(kiwoom, stock_code="005930"):
    """일별 기관매매 조회 테스트"""
    print("=" * 50)
    print(f"6. 일별 기관매매 조회 (종목: {stock_code})")
    print("=" * 50)
    
    try:
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        
        result = kiwoom.get_institutional_daily_trading(
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date
        )
        
        if 'output' in result:
            data = result['output']
            if isinstance(data, list) and data:
                print(f"조회 기간: {start_date} ~ {end_date}")
                print(f"조회된 데이터 수: {len(data)}개")
                print("\n최근 3일 기관매매:")
                for item in data[:3]:
                    print(f"  날짜: {item.get('stck_bsop_date', 'N/A')}")
                    print(f"    기관 순매수: {item.get('inst_ntby_qty', 'N/A')}")
                    print(f"    외국인 순매수: {item.get('frgn_ntby_qty', 'N/A')}")
                print("✓ 조회 성공\n")
            else:
                print("✗ 데이터 없음\n")
        else:
            print(f"✗ 응답 형식 오류: {result}\n")
    except Exception as e:
        print(f"✗ 조회 실패: {e}\n")


def test_program_trading(kiwoom, stock_code="005930"):
    """프로그램매매 추이 조회 테스트"""
    print("=" * 50)
    print(f"7. 프로그램매매 추이 조회 (종목: {stock_code})")
    print("=" * 50)
    
    try:
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        
        result = kiwoom.get_program_trading_daily(
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date
        )
        
        if 'output' in result:
            data = result['output']
            if isinstance(data, list) and data:
                print(f"조회 기간: {start_date} ~ {end_date}")
                print(f"조회된 데이터 수: {len(data)}개")
                print("\n최근 3일 프로그램매매:")
                for item in data[:3]:
                    print(f"  날짜: {item.get('stck_bsop_date', 'N/A')}")
                    print(f"    순매수: {item.get('seln_pbmn_val', 'N/A')}")
                    print(f"    매수: {item.get('shnu_pbmn_val', 'N/A')}")
                    print(f"    매도: {item.get('seln_pbmn_val', 'N/A')}")
                print("✓ 조회 성공\n")
            else:
                print("✗ 데이터 없음\n")
        else:
            print(f"✗ 응답 형식 오류: {result}\n")
    except Exception as e:
        print(f"✗ 조회 실패: {e}\n")


def main():
    """메인 테스트 실행"""
    print("\n" + "=" * 50)
    print("PyKiwoom-Rest 테스트 시작")
    print("=" * 50 + "\n")
    
    # 연결 테스트
    kiwoom = test_basic_connection()
    if not kiwoom:
        print("연결 실패로 테스트 종료")
        return
    
    # 삼성전자(005930)로 테스트
    test_stock_code = "005930"
    
    # 각 기능 테스트
    test_stock_price(kiwoom, test_stock_code)
    test_stock_orderbook(kiwoom, test_stock_code)
    test_minute_chart(kiwoom, test_stock_code)
    test_minute_chart_paginated(kiwoom, test_stock_code)
    test_daily_institutional_trading(kiwoom, test_stock_code)
    test_program_trading(kiwoom, test_stock_code)
    
    print("=" * 50)
    pass
    print("=" * 50)


if __name__ == "__main__":
    main()
