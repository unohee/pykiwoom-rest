#!/usr/bin/env python3
"""
동시 처리 성능 비교 테스트
작성일: 2025-01-05
"""

import time
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

from src.pykiwoom_rest.concurrent_api import (
    ConcurrentKiwoomAPI,
    ProcessingMode,
    OptimizedBatchProcessor,
    fetch_stocks_parallel,
    benchmark_all_modes
)

# 테스트 종목들
KOSPI_TOP_20 = [
    "005930",  # 삼성전자
    "000660",  # SK하이닉스
    "005490",  # POSCO
    "005380",  # 현대차
    "000270",  # 기아
    "068270",  # 셀트리온
    "035420",  # NAVER
    "051910",  # LG화학
    "006400",  # 삼성SDI
    "035720",  # 카카오
    "003550",  # LG
    "105560",  # KB금융
    "055550",  # 신한지주
    "066570",  # LG전자
    "096770",  # SK이노베이션
    "032830",  # 삼성생명
    "012330",  # 현대모비스
    "003490",  # 대한항공
    "015760",  # 한국전력
    "017670",  # SK텔레콤
]


def test_sequential_vs_parallel():
    """순차 vs 병렬 처리 비교"""
    print("\n" + "="*60)
    print("순차 처리 vs 병렬 처리 비교")
    print("="*60)
    
    test_stocks = KOSPI_TOP_20[:10]
    
    # 1. 순차 처리
    print("\n1. 순차 처리 (Sequential)")
    print("-" * 40)
    
    with ConcurrentKiwoomAPI(mode=ProcessingMode.SEQUENTIAL) as api:
        start = time.time()
        result = api.fetch_stock_prices(test_stocks)
        seq_time = time.time() - start
        
        print(f"  ✅ 성공: {result.success_count}")
        print(f"  ❌ 실패: {result.error_count}") 
        print(f"  ⏱️  시간: {seq_time:.2f}초")
        print(f"  📊 처리량: {result.throughput:.2f} req/s")
        print(f"  📈 성공률: {result.success_rate*100:.1f}%")
    
    # 2. 스레드 병렬 처리
    print("\n2. 스레드 병렬 처리 (ThreadPool)")
    print("-" * 40)
    
    with ConcurrentKiwoomAPI(mode=ProcessingMode.THREAD_POOL, max_workers=5) as api:
        start = time.time()
        result = api.fetch_stock_prices(test_stocks)
        thread_time = time.time() - start
        
        print(f"  ✅ 성공: {result.success_count}")
        print(f"  ❌ 실패: {result.error_count}")
        print(f"  ⏱️  시간: {thread_time:.2f}초")
        print(f"  📊 처리량: {result.throughput:.2f} req/s")
        print(f"  📈 성공률: {result.success_rate*100:.1f}%")
    
    # 성능 비교
    if seq_time > 0:
        speedup = seq_time / thread_time
        print(f"\n🚀 속도 향상: {speedup:.2f}배")
        print(f"   시간 절약: {(seq_time - thread_time):.2f}초 ({(1-thread_time/seq_time)*100:.1f}%)")


def test_scalability():
    """확장성 테스트 - 종목 수 증가에 따른 성능"""
    print("\n" + "="*60)
    print("확장성 테스트")
    print("="*60)
    
    test_sizes = [5, 10, 20]
    
    for size in test_sizes:
        test_stocks = KOSPI_TOP_20[:size]
        
        print(f"\n종목 {size}개 처리")
        print("-" * 40)
        
        # 스레드 풀 테스트
        with ConcurrentKiwoomAPI(
            mode=ProcessingMode.THREAD_POOL,
            max_workers=min(size, 10)
        ) as api:
            start = time.time()
            result = api.fetch_stock_prices(test_stocks)
            elapsed = time.time() - start
            
            print(f"  시간: {elapsed:.2f}초")
            print(f"  처리량: {result.throughput:.2f} req/s")
            print(f"  종목당 평균: {elapsed/size:.3f}초")


def test_auto_optimization():
    """자동 최적화 테스트"""
    print("\n" + "="*60)
    print("자동 최적화 모드 선택")
    print("="*60)
    
    processor = OptimizedBatchProcessor()
    
    # 샘플로 벤치마크
    print("\n벤치마크 실행 중...")
    best_mode = processor.benchmark_modes(KOSPI_TOP_20[:5], sample_size=5)
    
    print(f"\n🏆 최적 모드: {best_mode.value}")
    
    # 벤치마크 결과 출력
    print("\n벤치마크 결과:")
    for mode, throughput in processor.benchmarks.items():
        print(f"  {mode.value:15s}: {throughput:.2f} req/s")
    
    # 최적 모드로 전체 처리
    print(f"\n최적 모드로 전체 {len(KOSPI_TOP_20)}개 종목 처리...")
    result = processor.auto_process(KOSPI_TOP_20)
    
    print(f"  ✅ 성공: {result.success_count}")
    print(f"  ⏱️  시간: {result.total_time:.2f}초")
    print(f"  📊 처리량: {result.throughput:.2f} req/s")


def test_convenience_functions():
    """편의 함수 테스트"""
    print("\n" + "="*60)
    print("편의 함수 테스트")
    print("="*60)
    
    test_stocks = ["005930", "000660", "035720", "005380", "051910"]
    
    print("\n병렬 조회 함수 테스트...")
    start = time.time()
    results = fetch_stocks_parallel(test_stocks, max_workers=5)
    elapsed = time.time() - start
    
    print(f"  조회 완료: {len(results)}개")
    print(f"  소요 시간: {elapsed:.2f}초")
    
    # 결과 샘플 출력
    for code in test_stocks[:3]:
        if code in results and results[code]:
            if hasattr(results[code], 'data'):
                stock_name = results[code].data.get('stk_nm', 'Unknown')
                print(f"  {code}: {stock_name}")


def test_worker_comparison():
    """워커 수에 따른 성능 비교"""
    print("\n" + "="*60)
    print("워커 수 최적화")
    print("="*60)
    
    test_stocks = KOSPI_TOP_20[:15]
    worker_counts = [1, 3, 5, 10]
    
    best_workers = 1
    best_time = float('inf')
    
    for workers in worker_counts:
        with ConcurrentKiwoomAPI(
            mode=ProcessingMode.THREAD_POOL,
            max_workers=workers
        ) as api:
            start = time.time()
            result = api.fetch_stock_prices(test_stocks)
            elapsed = time.time() - start
            
            print(f"\n워커 {workers:2d}개: {elapsed:.2f}초 ({result.throughput:.2f} req/s)")
            
            if elapsed < best_time:
                best_time = elapsed
                best_workers = workers
    
    print(f"\n🏆 최적 워커 수: {best_workers}개")


def main():
    """메인 실행"""
    print("\n" + "="*60)
    print("Kiwoom API 동시 처리 성능 테스트")
    print("="*60)
    
    # 1. 기본 비교
    test_sequential_vs_parallel()
    
    # 2. 확장성
    test_scalability()
    
    # 3. 자동 최적화
    test_auto_optimization()
    
    # 4. 편의 함수
    test_convenience_functions()
    
    # 5. 워커 수 최적화
    test_worker_comparison()
    
    print("\n" + "="*60)
    print("✅ 모든 테스트 완료")
    print("="*60)
    
    # 최종 권장사항
    print("\n📌 권장사항:")
    print("  - 10개 이하: 순차 처리도 충분")
    print("  - 10-50개: ThreadPool (워커 5-10개)")
    print("  - 50개 이상: 자동 최적화 모드 사용")
    print("  - Rate Limit 주의: 초당 20회 제한")


if __name__ == "__main__":
    main()