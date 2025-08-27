"""
PyKiwoom-Rest New Architecture Example
새로운 모듈러 아키텍처 사용 예제
작성일: 2025-01-27
"""

import os
import sys
from datetime import datetime

# 프로젝트 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pykiwoom_rest import (
    StockAPI,
    ChartAPI, 
    RankingAPI,
    KiwoomRest,
    TokenBucketRateLimiter,
    KiwoomAPIError
)


def example_rate_limiter():
    """Rate Limiter 사용 예제"""
    print("🔧 Rate Limiter 예제")
    print("=" * 50)
    
    # 초당 5회 제한 Rate Limiter
    limiter = TokenBucketRateLimiter(rate=5, per_seconds=1.0)
    
    print("초당 5회 제한으로 10번 요청 시도:")
    successful = 0
    failed = 0
    
    for i in range(10):
        if limiter.acquire(blocking=False):
            print(f"  ✅ 요청 {i+1}: 성공")
            successful += 1
        else:
            print(f"  ❌ 요청 {i+1}: Rate limit 초과")
            failed += 1
    
    print(f"\n결과: 성공 {successful}건, 실패 {failed}건")
    print(f"현재 남은 토큰: {limiter.tokens:.2f}/{limiter.max_tokens}")
    print()


def example_modular_apis():
    """모듈러 API 사용 예제 (Mock)"""
    print("🏗️ 모듈러 API 구조 예제")
    print("=" * 50)
    
    # 각 API를 독립적으로 사용
    try:
        print("1. StockAPI 메서드 목록:")
        stock_methods = [method for method in dir(StockAPI) 
                        if method.startswith('get_') and not method.startswith('get__')]
        for i, method in enumerate(stock_methods[:5], 1):
            print(f"   {i}. {method}")
        print(f"   ... 총 {len(stock_methods)}개 메서드")
        
        print("\n2. ChartAPI 메서드 목록:")
        chart_methods = [method for method in dir(ChartAPI)
                        if method.startswith('get_') and not method.startswith('get__')]
        for i, method in enumerate(chart_methods, 1):
            print(f"   {i}. {method}")
        
        print("\n3. RankingAPI 메서드 목록:")
        ranking_methods = [method for method in dir(RankingAPI)
                          if method.startswith('get_') and not method.startswith('get__')]
        for i, method in enumerate(ranking_methods[:5], 1):
            print(f"   {i}. {method}")
        print(f"   ... 총 {len(ranking_methods)}개 메서드")
        
    except Exception as e:
        print(f"❌ 에러: {e}")
    
    print()


def example_unified_facade():
    """통합 Facade 사용 예제"""
    print("🏢 통합 Facade 패턴 예제")
    print("=" * 50)
    
    print("KiwoomRest Facade의 주요 특징:")
    print("✅ 기존 인터페이스 호환성 유지")
    print("✅ 새로운 모듈러 아키텍처 내부 사용")  
    print("✅ Rate Limiting 자동 적용")
    print("✅ 통합 에러 처리")
    print("✅ Connection Pooling")
    print("✅ 자동 토큰 관리")
    
    print("\n사용 방법:")
    print("```python")
    print("# 기존 방식과 동일")
    print("kiwoom = KiwoomRest()")
    print("result = kiwoom.get_stock_price('005930')")
    print("")
    print("# 새로운 직접 접근")
    print("stock_info = kiwoom.stock.get_stock_basic_info('005930')")
    print("chart_data = kiwoom.chart.get_minute_chart('005930', interval=5)")
    print("rankings = kiwoom.ranking.get_volume_top()")
    print("```")
    print()


def example_error_handling():
    """에러 처리 예제"""
    print("⚠️ 에러 처리 및 예외 계층 예제")
    print("=" * 50)
    
    # 커스텀 예외 생성 및 처리
    try:
        # KiwoomAPIError 예제
        error = KiwoomAPIError(
            message="API 호출 실패",
            error_code="RT_CD_01",
            error_msg="토큰이 만료되었습니다"
        )
        raise error
        
    except KiwoomAPIError as e:
        print("✅ KiwoomAPIError 처리:")
        print(f"   메시지: {str(e)}")
        print(f"   에러코드: {e.error_code}")
        print(f"   상세메시지: {e.error_msg}")
    
    print("\n에러 처리 계층:")
    print("  BaseException")
    print("  └── Exception") 
    print("      ├── APIError")
    print("      │   └── KiwoomAPIError")
    print("      └── RateLimitExceeded")
    print()


def example_best_practices():
    """모범 사례 예제"""
    print("💡 모범 사례 및 권장 패턴")
    print("=" * 50)
    
    print("1. Context Manager 사용:")
    print("```python")
    print("with KiwoomRest() as kiwoom:")
    print("    result = kiwoom.get_stock_price('005930')")
    print("    # 자동으로 세션 정리")
    print("```")
    
    print("\n2. 에러 처리와 재시도:")
    print("```python")
    print("try:")
    print("    result = kiwoom.get_minute_chart('005930')")
    print("except RateLimitExceeded:")
    print("    print('Rate limit 초과, 잠시 대기 필요')")
    print("except KiwoomAPIError as e:")
    print("    print(f'키움 API 에러: {e.error_code}')")
    print("```")
    
    print("\n3. 대량 데이터 조회:")
    print("```python")
    print("# 자동 페이지네이션 사용")
    print("data = kiwoom.get_minute_chart_paginated(")
    print("    '005930', interval=1, max_records=5000")
    print(")")
    print("```")
    
    print("\n4. 통계 모니터링:")
    print("```python")
    print("stats = kiwoom.get_stats()")
    print("print(f'총 요청: {stats[\"total_requests\"]}건')")
    print("print(f'에러율: {stats[\"total_errors\"]}건')")
    print("```")
    print()


def main():
    """메인 실행 함수"""
    print("🚀 PyKiwoom-Rest v2 새로운 아키텍처 데모")
    print("=" * 60)
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # 각 예제 실행
    example_rate_limiter()
    example_modular_apis()  
    example_unified_facade()
    example_error_handling()
    example_best_practices()
    
    print("🎉 새로운 아키텍처의 주요 개선 사항:")
    print("=" * 50)
    print("✅ 모듈화된 구조로 유지보수성 향상")
    print("✅ Token Bucket 알고리즘 기반 Rate Limiting")
    print("✅ Exponential Backoff 재시도 로직") 
    print("✅ Connection Pooling으로 성능 최적화")
    print("✅ 체계적인 에러 처리 및 로깅")
    print("✅ 기존 코드와 완벽한 하위 호환성")
    print("✅ 테스트 용이성 (Mock 지원)")
    print("✅ Context Manager 지원")
    print("✅ 실시간 성능 모니터링")
    print()


if __name__ == "__main__":
    main()