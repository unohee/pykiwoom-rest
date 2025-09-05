#!/usr/bin/env python3
"""
Rate Limiting Optimizer 실시간 테스트
작성일: 2025-01-05
목적: 실제 API 환경에서 rate limiting 최적화 검증
"""

import os
import time
import json
import threading
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

from src.pykiwoom_rest import KiwoomRest
from src.pykiwoom_rest.rate_limit_optimizer import RateLimitOptimizer


def test_single_credential_baseline():
    """단일 크레덴셜 기준선 테스트"""
    print("\n" + "="*60)
    print("단일 크레덴셜 기준선 테스트")
    print("="*60)
    
    # 기본 설정 (rate optimizer 비활성화)
    kiwoom = KiwoomRest(enable_rate_optimizer=False)
    
    start_time = time.time()
    successful_requests = 0
    failed_requests = 0
    errors_429 = 0
    
    # 30초간 연속 요청
    test_duration = 30
    request_count = 0
    
    while time.time() - start_time < test_duration:
        try:
            # 간단한 시세 조회
            result = kiwoom.get_stock_price("005930")
            if result and 'rt_cd' in result:
                successful_requests += 1
            else:
                failed_requests += 1
            request_count += 1
            
        except Exception as e:
            failed_requests += 1
            if '429' in str(e):
                errors_429 += 1
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 429 에러 발생")
                time.sleep(1)  # 간단한 대기
    
    elapsed = time.time() - start_time
    rps = successful_requests / elapsed
    
    print(f"\n테스트 결과:")
    print(f"  - 총 요청: {request_count}")
    print(f"  - 성공: {successful_requests}")
    print(f"  - 실패: {failed_requests}")
    print(f"  - 429 에러: {errors_429}")
    print(f"  - 처리량: {rps:.2f} req/s")
    print(f"  - 성공률: {(successful_requests/max(request_count, 1))*100:.1f}%")
    
    return {
        'total': request_count,
        'success': successful_requests,
        'failed': failed_requests,
        'errors_429': errors_429,
        'rps': rps
    }


def test_multi_credential_optimized():
    """다중 크레덴셜 최적화 테스트"""
    print("\n" + "="*60)
    print("다중 크레덴셜 최적화 테스트")
    print("="*60)
    
    # 다중 크레덴셜 설정 (환경변수에서 여러 개 로드)
    credentials = []
    
    # 기본 크레덴셜
    if os.getenv('KIWOOM_APPKEY') and os.getenv('KIWOOM_APPSECRET'):
        credentials.append({
            'APPKEY': os.getenv('KIWOOM_APPKEY'),
            'APPSECRET': os.getenv('KIWOOM_APPSECRET')
        })
    
    # 추가 크레덴셜 (있는 경우)
    for i in range(1, 4):
        appkey = os.getenv(f'KIWOOM_APPKEY_{i}')
        appsecret = os.getenv(f'KIWOOM_APPSECRET_{i}')
        if appkey and appsecret:
            credentials.append({
                'APPKEY': appkey,
                'APPSECRET': appsecret
            })
    
    print(f"사용 가능한 크레덴셜: {len(credentials)}개")
    
    if len(credentials) < 2:
        print("⚠️  다중 크레덴셜 테스트를 위해서는 최소 2개의 크레덴셜이 필요합니다.")
        print("   환경변수에 KIWOOM_APPKEY_1, KIWOOM_APPSECRET_1 등을 추가하세요.")
        return None
    
    # Rate optimizer 활성화
    kiwoom = KiwoomRest(
        enable_rate_optimizer=True,
        credentials_list=credentials
    )
    
    start_time = time.time()
    successful_requests = 0
    failed_requests = 0
    errors_429 = 0
    rotations = 0
    
    # 30초간 연속 요청
    test_duration = 30
    request_count = 0
    last_stats = {}
    
    while time.time() - start_time < test_duration:
        try:
            # 간단한 시세 조회
            result = kiwoom.get_stock_price("005930")
            if result and 'rt_cd' in result:
                successful_requests += 1
            else:
                failed_requests += 1
            request_count += 1
            
            # 통계 업데이트
            if hasattr(kiwoom.api_base, 'rate_optimizer'):
                stats = kiwoom.api_base.rate_optimizer.get_stats()
                if stats['total_rotations'] > rotations:
                    rotations = stats['total_rotations']
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 크레덴셜 로테이션 #{rotations}")
            
        except Exception as e:
            failed_requests += 1
            if '429' in str(e):
                errors_429 += 1
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 429 에러 (자동 처리)")
    
    elapsed = time.time() - start_time
    rps = successful_requests / elapsed
    
    # 최종 통계
    if hasattr(kiwoom.api_base, 'rate_optimizer'):
        final_stats = kiwoom.api_base.rate_optimizer.get_stats()
        print(f"\nRate Optimizer 통계:")
        print(f"  - 총 로테이션: {final_stats['total_rotations']}")
        print(f"  - 활성 크레덴셜: {final_stats['active_credentials']}/{final_stats['total_credentials']}")
        print(f"  - 429 에러 처리: {final_stats['total_429_errors']}")
    
    print(f"\n테스트 결과:")
    print(f"  - 총 요청: {request_count}")
    print(f"  - 성공: {successful_requests}")
    print(f"  - 실패: {failed_requests}")
    print(f"  - 429 에러: {errors_429}")
    print(f"  - 처리량: {rps:.2f} req/s")
    print(f"  - 성공률: {(successful_requests/max(request_count, 1))*100:.1f}%")
    
    return {
        'total': request_count,
        'success': successful_requests,
        'failed': failed_requests,
        'errors_429': errors_429,
        'rps': rps,
        'rotations': rotations
    }


def test_burst_traffic_simulation():
    """버스트 트래픽 시뮬레이션"""
    print("\n" + "="*60)
    print("버스트 트래픽 시뮬레이션")
    print("="*60)
    
    kiwoom = KiwoomRest(enable_rate_optimizer=True)
    
    results = []
    
    def burst_worker(worker_id: int, num_requests: int):
        """워커 스레드에서 버스트 요청 실행"""
        local_success = 0
        local_failed = 0
        
        for i in range(num_requests):
            try:
                result = kiwoom.get_stock_price("005930")
                if result and 'rt_cd' in result:
                    local_success += 1
                else:
                    local_failed += 1
            except Exception as e:
                local_failed += 1
                print(f"Worker {worker_id}: Error - {str(e)[:50]}")
        
        results.append({
            'worker_id': worker_id,
            'success': local_success,
            'failed': local_failed
        })
    
    # 5개 스레드에서 동시에 10개씩 요청
    threads = []
    start_time = time.time()
    
    for i in range(5):
        t = threading.Thread(target=burst_worker, args=(i, 10))
        threads.append(t)
        t.start()
    
    # 모든 스레드 완료 대기
    for t in threads:
        t.join()
    
    elapsed = time.time() - start_time
    
    # 결과 집계
    total_success = sum(r['success'] for r in results)
    total_failed = sum(r['failed'] for r in results)
    total_requests = total_success + total_failed
    
    print(f"\n버스트 테스트 결과:")
    print(f"  - 총 요청: {total_requests}")
    print(f"  - 성공: {total_success}")
    print(f"  - 실패: {total_failed}")
    print(f"  - 소요 시간: {elapsed:.2f}초")
    print(f"  - 처리량: {total_requests/elapsed:.2f} req/s")
    print(f"  - 성공률: {(total_success/max(total_requests, 1))*100:.1f}%")
    
    # 워커별 결과
    print(f"\n워커별 결과:")
    for r in results:
        print(f"  Worker {r['worker_id']}: 성공 {r['success']}, 실패 {r['failed']}")


def test_adaptive_rate_adjustment():
    """적응형 레이트 조정 테스트"""
    print("\n" + "="*60)
    print("적응형 레이트 조정 테스트")
    print("="*60)
    
    kiwoom = KiwoomRest(enable_rate_optimizer=True)
    
    if not hasattr(kiwoom.api_base, 'rate_optimizer'):
        print("Rate optimizer가 활성화되지 않았습니다.")
        return
    
    optimizer = kiwoom.api_base.rate_optimizer
    
    print(f"초기 레이트: {optimizer.base_rate_limit} req/s")
    
    # 성공률 높은 구간 시뮬레이션
    print("\n높은 성공률 시뮬레이션...")
    success_count = 0
    total_count = 0
    
    for i in range(20):
        try:
            result = kiwoom.get_stock_price("005930")
            if result:
                success_count += 1
            total_count += 1
        except:
            total_count += 1
        time.sleep(0.1)  # 안정적인 속도
    
    success_rate = success_count / max(total_count, 1)
    print(f"성공률: {success_rate*100:.1f}%")
    
    # 적응형 조정
    optimizer.adaptive_rate_adjustment(success_rate)
    print(f"조정 후 레이트: {optimizer.base_rate_limit} req/s")
    
    # 성공률 낮은 구간 시뮬레이션
    print("\n낮은 성공률 시뮬레이션 (빠른 요청)...")
    success_count = 0
    total_count = 0
    
    for i in range(50):
        try:
            result = kiwoom.get_stock_price("005930")
            if result:
                success_count += 1
            total_count += 1
        except:
            total_count += 1
        # 의도적으로 빠른 요청
    
    success_rate = success_count / max(total_count, 1)
    print(f"성공률: {success_rate*100:.1f}%")
    
    # 적응형 조정
    optimizer.adaptive_rate_adjustment(success_rate)
    print(f"조정 후 레이트: {optimizer.base_rate_limit} req/s")


def main():
    """메인 실행 함수"""
    print("\n" + "="*60)
    print("Kiwoom REST API Rate Limiting 최적화 테스트")
    print("="*60)
    
    # 환경 확인
    if not os.getenv('KIWOOM_APPKEY'):
        print("❌ 환경변수를 설정하세요: KIWOOM_APPKEY, KIWOOM_APPSECRET")
        return
    
    results = {}
    
    # 1. 단일 크레덴셜 기준선
    print("\n1️⃣ 단일 크레덴셜 기준선 측정")
    baseline = test_single_credential_baseline()
    results['baseline'] = baseline
    
    # 2. 다중 크레덴셜 최적화 (가능한 경우)
    print("\n2️⃣ 다중 크레덴셜 최적화 측정")
    optimized = test_multi_credential_optimized()
    if optimized:
        results['optimized'] = optimized
        
        # 개선율 계산
        improvement = (optimized['rps'] / baseline['rps'] - 1) * 100
        print(f"\n📊 성능 개선: {improvement:+.1f}%")
    
    # 3. 버스트 트래픽 테스트
    print("\n3️⃣ 버스트 트래픽 처리")
    test_burst_traffic_simulation()
    
    # 4. 적응형 레이트 조정
    print("\n4️⃣ 적응형 레이트 조정")
    test_adaptive_rate_adjustment()
    
    # 최종 요약
    print("\n" + "="*60)
    print("테스트 완료 - 최종 요약")
    print("="*60)
    
    if 'baseline' in results:
        print(f"\n기준선 (단일 크레덴셜):")
        print(f"  - 처리량: {results['baseline']['rps']:.2f} req/s")
        print(f"  - 429 에러: {results['baseline']['errors_429']}회")
    
    if 'optimized' in results:
        print(f"\n최적화 (다중 크레덴셜):")
        print(f"  - 처리량: {results['optimized']['rps']:.2f} req/s")
        print(f"  - 429 에러: {results['optimized']['errors_429']}회")
        print(f"  - 로테이션: {results['optimized']['rotations']}회")
    
    print("\n✅ Rate limiting 최적화 테스트 완료")


if __name__ == "__main__":
    main()