#!/usr/bin/env python3
"""
새로운 API 모듈 테스트
작성일: 2025-01-27
"""

import os
import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json
from typing import Dict, Any

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pykiwoom_rest.kiwoom_rest import KiwoomRest
import time

pytestmark = pytest.mark.integration


def test_account_apis(kiwoom: KiwoomRest):
    """계좌 관련 API 테스트"""
    print("\n" + "="*60)
    print("계좌 관련 API 테스트")
    print("="*60)
    
    tests = [
        ("예수금 상세 현황", lambda: kiwoom.get_deposit_detail()),
        ("계좌 평가 현황", lambda: kiwoom.get_account_evaluation()),
        ("계좌 평가잔고 내역", lambda: kiwoom.get_balance_detail()),
        ("미체결 주문", lambda: kiwoom.get_unfilled_orders()),
        ("체결된 주문", lambda: kiwoom.get_executed_orders()),
        ("계좌 수익률", lambda: kiwoom.get_account_return())
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"\n테스트: {test_name}")
            result = test_func()
            
            if isinstance(result, dict):
                if result.get('rt_cd') == '0':
                    print(f"  ✓ 성공")
                    if 'output' in result:
                        print(f"    데이터 수: {len(result.get('output', []))}")
                else:
                    print(f"  ✗ 실패: {result.get('msg1', 'Unknown error')}")
            else:
                print(f"  ✓ 응답 수신")
            
            time.sleep(0.1)  # Rate limiting
            
        except Exception as e:
            print(f"  ✗ 오류: {str(e)}")


def test_order_apis(kiwoom: KiwoomRest):
    """주문 관련 API 테스트 (읽기 전용)"""
    print("\n" + "="*60)
    print("주문 관련 API 테스트")
    print("="*60)
    
    # 신용 가능 종목 확인만 테스트 (실제 주문은 하지 않음)
    tests = [
        ("신용융자 가능종목", lambda: kiwoom.order_api.get_credit_available_stocks("KOSPI")),
        ("신용융자 가능 확인 (삼성전자)", lambda: kiwoom.order_api.check_credit_available("005930"))
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"\n테스트: {test_name}")
            result = test_func()
            
            if isinstance(result, dict):
                if result.get('rt_cd') == '0':
                    print(f"  ✓ 성공")
                    if 'output' in result:
                        print(f"    데이터 수: {len(result.get('output', []))}")
                else:
                    print(f"  ✗ 실패: {result.get('msg1', 'Unknown error')}")
            
            time.sleep(0.1)
            
        except Exception as e:
            print(f"  ✗ 오류: {str(e)}")
    
    print("\n※ 주문 실행 API (buy/sell/modify/cancel)는 실제 거래가 발생하므로 테스트 생략")


def test_sector_apis(kiwoom: KiwoomRest):
    """업종 관련 API 테스트"""
    print("\n" + "="*60)
    print("업종 관련 API 테스트")
    print("="*60)
    
    # 어제 날짜
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
    
    tests = [
        ("업종 현재가 (KOSPI)", lambda: kiwoom.get_sector_current_price("0001")),
        ("전업종 지수", lambda: kiwoom.get_all_sector_index()),
        ("업종 일봉차트", lambda: kiwoom.get_sector_daily_chart("0001", week_ago, yesterday)),
        ("업종 투자자 순매수", lambda: kiwoom.sector_api.get_sector_investor_trading("0001")),
        ("업종 프로그램 매매", lambda: kiwoom.sector_api.get_sector_program_trading("0001"))
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"\n테스트: {test_name}")
            result = test_func()
            
            if isinstance(result, dict):
                if result.get('rt_cd') == '0':
                    print(f"  ✓ 성공")
                    if 'output' in result:
                        print(f"    데이터 수: {len(result.get('output', []))}")
                    elif 'output1' in result:
                        print(f"    데이터 수: {len(result.get('output1', []))}")
                else:
                    print(f"  ✗ 실패: {result.get('msg1', 'Unknown error')}")
            
            time.sleep(0.1)
            
        except Exception as e:
            print(f"  ✗ 오류: {str(e)}")


def test_integration(kiwoom: KiwoomRest):
    """통합 테스트 - 여러 API 연동"""
    print("\n" + "="*60)
    print("통합 테스트")
    print("="*60)
    
    try:
        # 1. 거래량 상위 종목 가져오기
        print("\n1. 거래량 상위 종목 조회...")
        volume_top = kiwoom.get_volume_top("KOSPI", 5)
        
        if volume_top.get('rt_cd') == '0' and 'output' in volume_top:
            stocks = volume_top['output'][:3]  # 상위 3종목
            print(f"  상위 3종목 선택")
            
            for stock in stocks:
                stock_code = stock.get('stk_cd', '')
                stock_name = stock.get('stk_nm', '')
                
                if stock_code:
                    print(f"\n2. {stock_name}({stock_code}) 상세 정보 조회...")
                    
                    # 기본 정보
                    basic_info = kiwoom.get_stock_price(stock_code)
                    if basic_info.get('rt_cd') == '0':
                        print(f"  ✓ 기본정보 조회 성공")
                    
                    time.sleep(0.1)
                    
                    # 분봉 차트
                    minute_chart = kiwoom.get_minute_chart(stock_code, 5)
                    if minute_chart.get('rt_cd') == '0':
                        print(f"  ✓ 5분봉 차트 조회 성공")
                    
                    time.sleep(0.1)
                    
                    # 외국인 매매
                    foreign_trading = kiwoom.get_foreign_trading(stock_code)
                    if foreign_trading.get('rt_cd') == '0':
                        print(f"  ✓ 외국인 매매 동향 조회 성공")
                    
                    time.sleep(0.1)
                    break  # 첫 종목만 테스트
        
    except Exception as e:
        print(f"통합 테스트 오류: {str(e)}")


def main():
    """메인 테스트 함수"""
    print("\n" + "="*60)
    print("PyKiwoom REST API 새 모듈 테스트")
    print("="*60)
    
    # API 초기화
    print("\nAPI 초기화 중...")
    try:
        kiwoom = KiwoomRest()
        print("✓ API 초기화 성공")
    except Exception as e:
        print(f"✗ API 초기화 실패: {str(e)}")
        return
    
    # 연결 확인
    print("\n연결 상태 확인...")
    try:
        result = kiwoom.verify_connection()
        if result.get('status') == 'healthy':
            print("✓ API 연결 정상")
        else:
            print(f"✗ API 연결 문제: {result}")
    except Exception as e:
        print(f"✗ 연결 확인 실패: {str(e)}")
    
    # 각 모듈 테스트
    test_functions = [
        test_account_apis,
        test_order_apis,
        test_sector_apis,
        test_integration
    ]
    
    for test_func in test_functions:
        try:
            test_func(kiwoom)
        except Exception as e:
            print(f"\n테스트 실행 중 오류: {str(e)}")
    
    # 통계 출력
    print("\n" + "="*60)
    print("API 호출 통계")
    print("="*60)
    
    stats = kiwoom.get_stats()
    total_requests = stats.get('total_requests', 0)
    
    print(f"\n총 요청 수: {total_requests}")
    print(f"Stock API: {stats.get('stock_api_stats', {}).get('request_count', 0)}")
    print(f"Chart API: {stats.get('chart_api_stats', {}).get('request_count', 0)}")
    print(f"Ranking API: {stats.get('ranking_api_stats', {}).get('request_count', 0)}")
    
    if hasattr(kiwoom, 'account_api'):
        account_stats = kiwoom.account_api.get_stats()
        print(f"Account API: {account_stats.get('request_count', 0)}")
    
    if hasattr(kiwoom, 'order_api'):
        order_stats = kiwoom.order_api.get_stats()
        print(f"Order API: {order_stats.get('request_count', 0)}")
    
    if hasattr(kiwoom, 'sector_api'):
        sector_stats = kiwoom.sector_api.get_stats()
        print(f"Sector API: {sector_stats.get('request_count', 0)}")
    
    print("\n테스트 완료!")


if __name__ == "__main__":
    main()
