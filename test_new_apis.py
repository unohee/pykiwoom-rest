#!/usr/bin/env python3
"""
종목시간별 프로그램매매 추이요청 (ka90008) 테스트
생성일: 2025-01-29
"""

import sys
import os
import time
from datetime import datetime, timedelta

# 절대 경로로 src 디렉토리를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)

from pykiwoom_rest.kiwoom_rest import KiwoomRest
from dotenv import load_dotenv

def test_hourly_program_trading():
    """종목시간별 프로그램매매 추이요청 테스트"""
    
    # 환경변수 로드
    load_dotenv()
    
    # KiwoomRest 인스턴스 생성
    print("KiwoomRest 인스턴스 생성 중...")
    kiwoom = KiwoomRest()
    
    # 테스트용 날짜 설정 - 2025년 1월 9일로 고정
    test_date = "20250109"
    
    print(f"\n{'='*60}")
    print("종목시간별 프로그램매매 추이요청 테스트")
    print(f"{'='*60}")
    
    # 1. 단일 요청 테스트
    print(f"\n1. 단일 요청 테스트 (삼성전자, {test_date})")
    print("-" * 40)
    
    try:
        result = kiwoom.get_hourly_program_trading(
            stock_code="005930",
            date=test_date,
            amount_or_quantity="1"  # 금액 기준
        )
        
        # APIResponse 객체 처리
        if hasattr(result, 'data'):
            # APIResponse 객체인 경우
            print(f"APIResponse 성공 여부: {result.success}")
            data = result.data
            print(f"실제 데이터 타입: {type(data)}")
            print(f"데이터 키: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            if isinstance(data, dict) and 'output' in data:
                output = data['output']
                print(f"✅ 조회 성공: {len(output) if isinstance(output, list) else 1}건")
                
                if isinstance(output, list) and output:
                    sample = output[0]
                    print(f"\n첫 번째 데이터 샘플:")
                    for key, value in list(sample.items())[:5]:
                        print(f"  {key}: {value}")
            else:
                print(f"전체 응답 데이터: {data}")
        elif result and 'output' in result:
            # 일반 dict 응답인 경우
            data = result['output']
            print(f"✅ 조회 성공: {len(data) if isinstance(data, list) else 1}건")
            
            # 첫 번째 데이터 샘플 출력
            if isinstance(data, list) and data:
                sample = data[0]
                print(f"\n첫 번째 데이터 샘플:")
                for key, value in list(sample.items())[:5]:
                    print(f"  {key}: {value}")
            
            # 헤더 정보 확인
            header = result.get('header', {})
            cont_yn = header.get('cont-yn', 'N')
            next_key = header.get('next-key', '')
            
            print(f"\n연속조회 가능 여부: {cont_yn}")
            print(f"다음 키 존재: {'있음' if next_key else '없음'}")
            
        else:
            print("❌ 데이터 조회 실패 또는 데이터 없음")
            print(f"응답 타입: {type(result)}")
            print(f"응답: {result}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    
    time.sleep(0.5)
    
    # 2. 페이지네이션 테스트
    print(f"\n2. 페이지네이션 테스트 (SK하이닉스, {test_date})")
    print("-" * 40)
    
    try:
        result = kiwoom.get_hourly_program_trading_paginated(
            stock_code="000660",
            date=test_date,
            amount_or_quantity="2",  # 수량 기준
            max_records=100
        )
        
        if result and 'output' in result:
            data = result['output']
            total_records = result.get('total_records', 0)
            
            print(f"✅ 페이지네이션 조회 성공")
            print(f"  전체 레코드 수: {total_records}건")
            print(f"  실제 조회된 수: {len(data)}건")
            
            # 데이터 요약 정보
            if data:
                print(f"\n데이터 요약:")
                print(f"  첫 번째 시간: {data[0].get('time', 'N/A') if isinstance(data[0], dict) else 'N/A'}")
                print(f"  마지막 시간: {data[-1].get('time', 'N/A') if isinstance(data[-1], dict) else 'N/A'}")
                
                # 프로그램 매매 정보 샘플
                if len(data) > 5:
                    print(f"\n중간 데이터 샘플 (5번째):")
                    sample = data[4]
                    if isinstance(sample, dict):
                        for key, value in list(sample.items())[:7]:
                            print(f"    {key}: {value}")
        else:
            print("❌ 페이지네이션 조회 실패 또는 데이터 없음")
            print(f"응답: {result}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    
    time.sleep(0.5)
    
    # 3. 여러 종목 비교 테스트
    print(f"\n3. 여러 종목 비교 테스트 ({test_date})")
    print("-" * 40)
    
    test_stocks = [
        ("005930", "삼성전자"),
        ("000660", "SK하이닉스"),
        ("035420", "NAVER")
    ]
    
    for stock_code, stock_name in test_stocks:
        try:
            result = kiwoom.get_hourly_program_trading(
                stock_code=stock_code,
                date=test_date,
                amount_or_quantity="1"
            )
            
            if result and 'output' in result:
                data = result['output']
                record_count = len(data) if isinstance(data, list) else 1
                print(f"  {stock_name}({stock_code}): {record_count}건 조회")
                
                # 프로그램 매매 요약
                if isinstance(data, list) and data:
                    # 매수/매도 합계 계산 (필드명은 실제 API 응답에 따라 조정 필요)
                    total_buy = 0
                    total_sell = 0
                    
                    for item in data[:10]:  # 상위 10개만 샘플링
                        if isinstance(item, dict):
                            # 실제 필드명에 따라 조정 필요
                            buy_amt = item.get('pgmm_buy_amt', 0)
                            sell_amt = item.get('pgmm_sell_amt', 0)
                            
                            try:
                                total_buy += float(buy_amt) if buy_amt else 0
                                total_sell += float(sell_amt) if sell_amt else 0
                            except (ValueError, TypeError):
                                pass
                    
                    if total_buy or total_sell:
                        print(f"    프로그램 매수 합계: {total_buy:,.0f}")
                        print(f"    프로그램 매도 합계: {total_sell:,.0f}")
                        
            else:
                print(f"  {stock_name}({stock_code}): 데이터 없음")
                
            time.sleep(0.1)  # Rate limiting
            
        except Exception as e:
            print(f"  {stock_name}({stock_code}): 오류 - {e}")
    
    # 4. Rate Limiting 및 통계 정보
    print(f"\n4. API 사용 통계")
    print("-" * 40)
    
    stats = kiwoom.get_stats()
    print(f"총 요청 수: {stats.get('total_requests', 0)}")
    print(f"총 오류 수: {stats.get('total_errors', 0)}")
    
    print(f"\n{'='*60}")
    print("테스트 완료")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    test_hourly_program_trading()