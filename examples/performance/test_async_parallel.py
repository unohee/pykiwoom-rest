#!/usr/bin/env python3
"""
비동기 및 병렬 처리 성능 테스트
작성일: 2025-01-05
"""

import asyncio
import time
from datetime import datetime
import statistics
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

from src.pykiwoom_rest import KiwoomRest
from src.pykiwoom_rest.async_api import AsyncKiwoomAPI, ParallelKiwoomAPI


# 테스트할 종목 코드들
TEST_STOCKS = [
    "005930",  # 삼성전자
    "000660",  # SK하이닉스
    "035720",  # 카카오
    "005380",  # 현대차
    "051910",  # LG화학
    "006400",  # 삼성SDI
    "035420",  # NAVER
    "003550",  # LG
    "012330",  # 현대모비스
    "066570",  # LG전자
]


def test_sequential_baseline():
    """순차 처리 기준선 테스트"""
    print("\n" + "="*60)
    print("1. 순차 처리 (기준선)")
    print("="*60)
    
    kiwoom = KiwoomRest()
    
    start_time = time.time()
    results = []
    errors = 0
    
    for code in TEST_STOCKS:
        try:
            result = kiwoom.get_stock_price(code)
            if result and hasattr(result, 'data'):
                results.append(result)
                print(f"  {code}: ✅")
            else:
                print(f"  {code}: ❌")
                errors += 1
        except Exception as e:
            print(f"  {code}: ❌ ({str(e)[:30]})")
            errors += 1
    
    elapsed = time.time() - start_time
    
    print(f"\n📊 결과:")
    print(f"  - 종목 수: {len(TEST_STOCKS)}")
    print(f"  - 성공: {len(results)}")
    print(f"  - 실패: {errors}")
    print(f"  - 소요 시간: {elapsed:.2f}초")
    print(f"  - 처리량: {len(TEST_STOCKS)/elapsed:.2f} req/s")
    
    return {
        'method': 'sequential',
        'elapsed': elapsed,
        'success': len(results),
        'errors': errors,
        'throughput': len(TEST_STOCKS)/elapsed
    }


async def test_async_concurrent():
    """비동기 동시 처리 테스트"""
    print("\n" + "="*60)
    print("2. 비동기 동시 처리 (AsyncIO)")
    print("="*60)
    
    start_time = time.time()
    
    async with AsyncKiwoomAPI(max_concurrent=5) as api:
        # 모든 종목 동시 조회
        results = await api.get_multiple_stock_prices(TEST_STOCKS)
        
        success_count = 0
        error_count = 0
        
        for code, result in zip(TEST_STOCKS, results):
            if result:
                print(f"  {code}: ✅")
                success_count += 1
            else:
                print(f"  {code}: ❌")
                error_count += 1
    
    elapsed = time.time() - start_time
    
    print(f"\n📊 결과:")
    print(f"  - 종목 수: {len(TEST_STOCKS)}")
    print(f"  - 성공: {success_count}")
    print(f"  - 실패: {error_count}")
    print(f"  - 소요 시간: {elapsed:.2f}초")
    print(f"  - 처리량: {len(TEST_STOCKS)/elapsed:.2f} req/s")
    
    return {
        'method': 'async',
        'elapsed': elapsed,
        'success': success_count,
        'errors': error_count,
        'throughput': len(TEST_STOCKS)/elapsed
    }


def test_parallel_threads():
    """스레드 병렬 처리 테스트"""
    print("\n" + "="*60)
    print("3. 스레드 병렬 처리 (ThreadPoolExecutor)")
    print("="*60)
    
    client = ParallelKiwoomAPI(max_workers=5)
    
    start_time = time.time()
    
    try:
        # 병렬 조회
        results = client.get_stock_prices_parallel(TEST_STOCKS)
        
        success_count = 0
        error_count = 0
        
        for code, result in results.items():
            if result:
                print(f"  {code}: ✅")
                success_count += 1
            else:
                print(f"  {code}: ❌")
                error_count += 1
        
        elapsed = time.time() - start_time
        
        # 통계
        stats = client.get_stats()
        
        print(f"\n📊 결과:")
        print(f"  - 종목 수: {len(TEST_STOCKS)}")
        print(f"  - 성공: {success_count}")
        print(f"  - 실패: {error_count}")
        print(f"  - 소요 시간: {elapsed:.2f}초")
        print(f"  - 처리량: {stats['requests_per_second']:.2f} req/s")
        
        return {
            'method': 'parallel',
            'elapsed': elapsed,
            'success': success_count,
            'errors': error_count,
            'throughput': stats['requests_per_second']
        }
        
    finally:
        client.shutdown()


async def test_async_streaming():
    """비동기 스트리밍 테스트"""
    print("\n" + "="*60)
    print("4. 비동기 스트리밍 (실시간 갱신)")
    print("="*60)
    
    updates = []
    
    async def update_callback(code: str, result: Dict[str, Any]):
        """업데이트 콜백"""
        updates.append((code, time.time()))
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] {code} 업데이트")
    
    async with AsyncKiwoomAPI() as api:
        print("5초간 실시간 스트리밍...")
        
        # 5초간 스트리밍
        streaming_task = asyncio.create_task(
            api.stream_stock_prices(
                TEST_STOCKS[:3],  # 3종목만
                interval=1.0,
                callback=update_callback
            )
        )
        
        await asyncio.sleep(5)
        streaming_task.cancel()
        
        try:
            await streaming_task
        except asyncio.CancelledError:
            pass
    
    print(f"\n📊 결과:")
    print(f"  - 총 업데이트: {len(updates)}회")
    print(f"  - 평균 간격: {5/max(len(updates), 1):.2f}초")


def test_batch_processing():
    """배치 처리 테스트"""
    print("\n" + "="*60)
    print("5. 배치 처리 (Mixed Operations)")
    print("="*60)
    
    client = ParallelKiwoomAPI(max_workers=5)
    
    try:
        # 다양한 작업 배치
        tasks = []
        
        # 주식 시세 조회
        for code in TEST_STOCKS[:5]:
            tasks.append({
                'method': 'get_stock_price',
                'args': [code]
            })
        
        # 추가 작업들 (예시)
        # tasks.append({
        #     'method': 'get_stock_orderbook',
        #     'args': ['005930']
        # })
        
        print(f"배치 작업 {len(tasks)}개 실행...")
        
        start_time = time.time()
        
        # 배치 실행
        completed = 0
        def progress_callback(result):
            nonlocal completed
            completed += 1
            print(f"  진행: {completed}/{len(tasks)} ({completed/len(tasks)*100:.1f}%)")
        
        results = client.batch_process(tasks, callback=progress_callback)
        
        elapsed = time.time() - start_time
        
        print(f"\n📊 결과:")
        print(f"  - 작업 수: {len(tasks)}")
        print(f"  - 완료: {len(results)}")
        print(f"  - 소요 시간: {elapsed:.2f}초")
        print(f"  - 처리량: {len(tasks)/elapsed:.2f} tasks/s")
        
    finally:
        client.shutdown()


def compare_performance(results: List[Dict[str, Any]]):
    """성능 비교 분석"""
    print("\n" + "="*60)
    print("성능 비교 분석")
    print("="*60)
    
    # 기준선 (순차 처리)
    baseline = next((r for r in results if r['method'] == 'sequential'), None)
    
    if not baseline:
        print("기준선 데이터 없음")
        return
    
    print(f"\n기준: 순차 처리 - {baseline['elapsed']:.2f}초")
    print("-" * 40)
    
    for result in results:
        if result['method'] != 'sequential':
            speedup = baseline['elapsed'] / result['elapsed']
            improvement = (speedup - 1) * 100
            
            print(f"\n{result['method'].upper()}:")
            print(f"  - 소요 시간: {result['elapsed']:.2f}초")
            print(f"  - 속도 향상: {speedup:.2f}배")
            print(f"  - 개선율: {improvement:+.1f}%")
            print(f"  - 처리량: {result['throughput']:.2f} req/s")
    
    # 최적 방법
    best = min(results, key=lambda r: r['elapsed'])
    print(f"\n🏆 최적 방법: {best['method'].upper()}")
    print(f"   {best['elapsed']:.2f}초 ({best['throughput']:.2f} req/s)")


async def main():
    """메인 실행 함수"""
    print("\n" + "="*60)
    print("Kiwoom REST API 비동기/병렬 처리 성능 테스트")
    print("="*60)
    
    results = []
    
    # 1. 순차 처리 (기준선)
    seq_result = test_sequential_baseline()
    results.append(seq_result)
    
    # 2. 비동기 처리
    async_result = await test_async_concurrent()
    results.append(async_result)
    
    # 3. 병렬 처리
    parallel_result = test_parallel_threads()
    results.append(parallel_result)
    
    # 4. 스트리밍 (선택적)
    # await test_async_streaming()
    
    # 5. 배치 처리
    test_batch_processing()
    
    # 성능 비교
    compare_performance(results)
    
    print("\n" + "="*60)
    print("✅ 모든 테스트 완료")
    print("="*60)


if __name__ == "__main__":
    # 이벤트 루프 실행
    asyncio.run(main())