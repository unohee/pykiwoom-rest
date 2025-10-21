# 통합 API Facade 시스템

## 개요

모든 API 호출을 **단일 파사드**로 통합하여 Rate Limiting을 정확하게 관리하는 시스템입니다.

## 🎯 주요 특징

### 1. **싱글턴 패턴**
```python
# 어디서든 같은 인스턴스 사용
facade1 = SimpleKiwoomAPIFacade.get_instance()
facade2 = SimpleKiwoomAPIFacade()
# facade1 is facade2 → True
```

### 2. **중앙 집중 Rate Limiting**
```python
# 모든 API 호출이 동일한 Rate Limiter를 공유
facade = SimpleKiwoomAPIFacade.get_instance(max_requests_per_second=20)

# 자동으로 Rate Limiting 적용
response = facade.make_request('GET', '/api/endpoint')
```

### 3. **요청 우선순위 관리**
```python
from src.pykiwoom_rest.simple_api_facade import RequestPriority

# 중요한 요청은 높은 우선순위로
facade.make_request(
    'POST',
    '/api/important',
    priority=RequestPriority.HIGH
)
```

### 4. **실시간 모니터링**
```python
# 종합 통계
stats = facade.get_comprehensive_stats()
print(f"성공률: {stats['facade_stats']['success_rate']:.2%}")
print(f"Rate Limit 대기열: {stats['rate_limiter_stats']['current_queue_size']}")

# 헬스체크
health = facade.health_check()
print(f"상태: {health['status']}")
```

## 🏗️ 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                 Application Layer                           │
├─────────────────────────────────────────────────────────────┤
│  StockAPI │ ChartAPI │ RankingAPI │ AccountAPI │ OrderAPI   │
├─────────────────────────────────────────────────────────────┤
│               UnifiedKiwoomRest                             │
├─────────────────────────────────────────────────────────────┤
│             SimpleKiwoomAPIFacade (Singleton)               │
│  ┌─────────────────┐  ┌─────────────────┐                 │
│  │ GlobalRateLimiter│  │ Request History │                 │
│  └─────────────────┘  └─────────────────┘                 │
├─────────────────────────────────────────────────────────────┤
│                    HTTP Layer                               │
└─────────────────────────────────────────────────────────────┘
```

## 📊 장점

### ✅ **정확한 Rate Limiting**
- 모든 API 호출이 단일 지점을 통과
- 전역 토큰 버킷 알고리즘 사용
- 429 에러 최소화

### ✅ **중앙 집중 관리**
- 모든 요청 통계 추적
- 실시간 모니터링
- 성능 분석 용이

### ✅ **싱글턴으로 리소스 효율성**
- 단일 HTTP Session 공유
- 메모리 사용량 최적화
- 인스턴스 관리 간소화

### ✅ **완전한 호환성**
- 기존 API 인터페이스 유지
- 투명한 Rate Limiting
- 점진적 마이그레이션 가능

## 🔧 사용법

### 기본 사용
```python
from src.pykiwoom_rest.simple_api_facade import SimpleKiwoomAPIFacade

# 인스턴스 생성 (싱글턴)
facade = SimpleKiwoomAPIFacade.get_instance(
    max_requests_per_second=20
)

# API 호출
response = facade.make_request(
    method='GET',
    endpoint='/api/dostk/stkinfo',
    headers={'Authorization': 'Bearer token'}
)
```

### 통계 모니터링
```python
# 실시간 통계
stats = facade.get_comprehensive_stats()

print(f"총 요청 수: {stats['facade_stats']['total_facade_requests']}")
print(f"성공률: {stats['facade_stats']['success_rate']:.2%}")
print(f"초당 요청: {stats['facade_stats']['requests_per_second']:.1f}")

# Rate Limiter 상태
rate_stats = stats['rate_limiter_stats']
print(f"현재 대기열: {rate_stats['current_queue_size']}")
print(f"차단 비율: {rate_stats['block_rate']:.2%}")
```

## 🧪 검증 결과

```
🚀 간단한 API Facade 테스트 시작
======================================================================

🔧 싱글턴 패턴 테스트
  ✅ facade1 is facade2 is facade3: True

⏱️ Rate Limiting 테스트
  ✅ 초당 3개 제한으로 5개 요청 처리
  ✅ 대기열 관리 정상 작동

🏗️ 기본 기능 테스트
  ✅ 헬스체크: healthy
  ✅ 통계 수집: 정상
  ✅ 요청 히스토리: 정상

전체 결과: ✅ 전체 성공
```

## 🔄 기존 시스템과 비교

| 항목 | 기존 시스템 | 통합 Facade |
|------|-------------|-------------|
| Rate Limiting | 개별 관리 | 중앙 집중 |
| 429 에러 | 빈번 발생 | 최소화 |
| 모니터링 | 분산된 통계 | 통합 통계 |
| 리소스 사용 | 중복 Session | 단일 Session |
| 인스턴스 관리 | 개별 생성 | 싱글턴 |

## 🚀 다음 단계

1. **실제 API 통합**: 키움증권 인증 시스템 연동
2. **UnifiedKiwoomRest**: 기존 인터페이스와 완전 호환
3. **성능 최적화**: 연결 풀링 및 캐싱
4. **모니터링 대시보드**: 실시간 성능 시각화

---

**결론**: 모든 API 호출을 단일 파사드로 통합하여 Rate Limiting을 정확하게 관리하고, 싱글턴 패턴으로 리소스 효율성을 극대화한 시스템이 성공적으로 구현되었습니다.