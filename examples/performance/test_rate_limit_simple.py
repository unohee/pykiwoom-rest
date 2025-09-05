#!/usr/bin/env python3
"""
Rate Limiting 최적화 간단 테스트
작성일: 2025-01-05
"""

import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from src.pykiwoom_rest import KiwoomRest


def test_basic_rate_limit():
    """기본 rate limiting 테스트"""
    print("\n" + "="*60)
    print("Rate Limiting 기본 테스트")
    print("="*60)
    
    # 기본 설정
    kiwoom = KiwoomRest(enable_rate_optimizer=False)
    
    print("\n5회 연속 요청 테스트 (rate limit 없음)...")
    for i in range(5):
        start = time.time()
        try:
            result = kiwoom.get_stock_price("005930")
            elapsed = time.time() - start
            # APIResponse 객체 확인
            if hasattr(result, 'success'):
                status = "✅ 성공" if result.success and result.data else "❌ 실패"
            else:
                status = "✅ 성공" if result and 'stk_cd' in result else "❌ 실패"
            print(f"  요청 {i+1}: {status} ({elapsed:.3f}초)")
        except Exception as e:
            elapsed = time.time() - start
            print(f"  요청 {i+1}: ❌ 에러 ({elapsed:.3f}초) - {str(e)[:50]}")
    
    print("\n✅ 기본 테스트 완료")


def test_with_rate_optimizer():
    """Rate optimizer 테스트"""
    print("\n" + "="*60)
    print("Rate Optimizer 테스트")
    print("="*60)
    
    # Rate optimizer 활성화
    kiwoom = KiwoomRest(enable_rate_optimizer=True)
    
    if hasattr(kiwoom.api_base, 'rate_optimizer'):
        optimizer = kiwoom.api_base.rate_optimizer
        stats = optimizer.get_stats()
        print(f"\nRate Optimizer 상태:")
        print(f"  - 크레덴셜 수: {stats['total_credentials']}")
        print(f"  - 로테이션 활성화: {stats['rotation_enabled']}")
    
    print("\n10회 연속 요청 테스트 (optimizer 적용)...")
    success_count = 0
    
    for i in range(10):
        start = time.time()
        try:
            result = kiwoom.get_stock_price("005930")
            elapsed = time.time() - start
            if (hasattr(result, 'success') and result.success and result.data) or (result and 'stk_cd' in result):
                success_count += 1
                print(f"  요청 {i+1}: ✅ 성공 ({elapsed:.3f}초)")
            else:
                print(f"  요청 {i+1}: ⚠️  데이터 없음 ({elapsed:.3f}초)")
        except Exception as e:
            elapsed = time.time() - start
            print(f"  요청 {i+1}: ❌ 에러 ({elapsed:.3f}초)")
            if '429' in str(e):
                print("    → 429 에러 감지 (rate limit)")
    
    print(f"\n결과: {success_count}/10 성공")
    
    if hasattr(kiwoom.api_base, 'rate_optimizer'):
        final_stats = optimizer.get_stats()
        print(f"\n최종 통계:")
        print(f"  - 총 요청: {final_stats['total_requests']}")
        print(f"  - 429 에러: {final_stats['total_429_errors']}")
        print(f"  - 로테이션: {final_stats['total_rotations']}")
    
    print("\n✅ Rate Optimizer 테스트 완료")


def test_burst_requests():
    """버스트 요청 테스트"""
    print("\n" + "="*60)
    print("버스트 요청 테스트")
    print("="*60)
    
    kiwoom = KiwoomRest(enable_rate_optimizer=True)
    
    print("\n20회 빠른 요청 테스트...")
    start_time = time.time()
    success_count = 0
    error_count = 0
    
    for i in range(20):
        try:
            result = kiwoom.get_stock_price("005930")
            if (hasattr(result, 'success') and result.success and result.data) or (result and 'stk_cd' in result):
                success_count += 1
                print(".", end="", flush=True)
            else:
                print("?", end="", flush=True)
        except Exception as e:
            error_count += 1
            if '429' in str(e):
                print("!", end="", flush=True)
            else:
                print("x", end="", flush=True)
    
    elapsed = time.time() - start_time
    print(f"\n\n결과:")
    print(f"  - 소요 시간: {elapsed:.2f}초")
    print(f"  - 성공: {success_count}")
    print(f"  - 실패: {error_count}")
    print(f"  - 처리량: {20/elapsed:.2f} req/s")
    
    print("\n✅ 버스트 테스트 완료")


def main():
    """메인 실행"""
    print("\n" + "="*60)
    print("Kiwoom REST API Rate Limiting 테스트")
    print("="*60)
    
    if not os.getenv('KIWOOM_APPKEY'):
        print("❌ 환경변수를 설정하세요: KIWOOM_APPKEY, KIWOOM_APPSECRET")
        return
    
    # 1. 기본 테스트
    test_basic_rate_limit()
    
    # 2. Rate optimizer 테스트
    test_with_rate_optimizer()
    
    # 3. 버스트 테스트
    test_burst_requests()
    
    print("\n" + "="*60)
    print("✅ 모든 테스트 완료")
    print("="*60)


if __name__ == "__main__":
    main()