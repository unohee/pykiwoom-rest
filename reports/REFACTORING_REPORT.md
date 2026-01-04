# PyKiwoom-REST Refactoring Report

**분석일**: 2026-01-04
**대상**: `src/pykiwoom_rest/`

---

## 1. 코드 품질 분석 요약

### 1.1 파일 크기 분석 (1000줄 초과 경고)

| 파일 | 줄 수 | 상태 | 권장 조치 |
|------|-------|------|----------|
| `kiwoom_rest_legacy.py` | 1,946 | **삭제 대상** | 사용되지 않음, 제거 권장 |
| `kiwoom_rest.py` | 793 | 정상 | - |
| `ranking_api.py` | 787 | 정상 | - |
| `kiwoom_base.py` | 603 | 정상 | 복잡도 개선 필요 |

### 1.2 순환 복잡도 분석 (Radon CC)

**높은 복잡도 (D등급 - 리팩토링 필요)**:
| 파일 | 메서드 | 복잡도 | 등급 |
|------|--------|--------|------|
| `chart_api.py` | `get_minute_chart_with_date` | 21 | D |
| `kiwoom_base.py` | `make_tr_request` | 17 | C |
| `ranking_api.py` | `get_hourly_program_trading_paginated` | 15 | C |
| `chart_api.py` | `get_minute_chart_paginated` | 14 | C |
| `auth_api.py` | `revoke_token` | 12 | C |
| `kiwoom_base.py` | `_setup_credentials` | 12 | C |
| `rate_limit_optimizer.py` | `get_optimal_credential` | 12 | C |

### 1.3 유지보수성 지수 (Radon MI)

| 파일 | MI 점수 | 등급 | 상태 |
|------|---------|------|------|
| `kiwoom_rest_legacy.py` | 0.00 | **C** | 심각 - 제거 필요 |
| `kiwoom_rest.py` | 38.50 | A | 개선 여지 있음 |
| `concurrent_api.py` | 40.76 | A | 정상 |
| `api_facade.py` | 43.75 | A | 정상 |
| 기타 | 45+ | A | 양호 |

---

## 2. 발견된 이슈

### 2.1 Dead Code (제거 대상)

#### `kiwoom_rest_legacy.py` - 완전히 사용되지 않음
- **줄 수**: 1,946줄
- **클래스**: `KiwoomRestBase`, `KiwoomRest`
- **메서드**: 123개
- **상태**: `__init__.py`에서 import되지 않음
- **권장**: 완전 삭제 또는 `deprecated/` 폴더로 이동

```python
# 현재 __init__.py는 새로운 아키텍처 사용:
from .kiwoom_rest_base import KiwoomRestBase  # 새 파일
from .kiwoom_rest import KiwoomRest           # 새 파일
```

#### `unified_kiwoom_rest.py` / `unified_kiwoom_base.py` - 사용 여부 불분명
- `__init__.py`에서 export되지 않음
- 내부적으로만 사용될 가능성
- 검토 후 제거 또는 통합 권장

#### `simple_api_facade.py` - 사용되지 않음
- 다른 파일에서 import하지 않음
- `api_facade.py`와 기능 중복
- 제거 권장

### 2.2 중복 코드 패턴

#### 차트 API 날짜 처리 로직 반복
```python
# 동일 패턴이 5개 메서드에서 반복됨
if not end_date:
    end_date = datetime.now().strftime("%Y%m%d")
if not start_date:
    start_date = (datetime.now() - timedelta(days=N)).strftime("%Y%m%d")
```

**권장**: 헬퍼 함수로 추출
```python
def _normalize_date_range(
    start_date: str = None,
    end_date: str = None,
    default_days: int = 365
) -> Tuple[str, str]:
    ...
```

### 2.3 높은 복잡도 메서드

#### `chart_api.py:get_minute_chart_with_date` (복잡도 21)
**문제점**:
- 중첩 루프와 조건문
- 여러 책임이 혼합됨 (데이터 수집, 필터링, 정렬)

**권장 리팩토링**:
```python
# Before: 단일 함수 80줄
def get_minute_chart_with_date(...):
    ...

# After: 책임 분리
def get_minute_chart_with_date(...):
    raw_data = self._collect_minute_data(stock_code, interval, max_pages)
    filtered = self._filter_by_date(raw_data, target_date)
    return self._format_chart_response(filtered, target_date)
```

#### `kiwoom_base.py:make_tr_request` (복잡도 17)
**문제점**:
- Rate optimizer 로직과 요청 로직이 혼합
- 에러 처리가 복잡

**권장 리팩토링**:
```python
# Extract Method 패턴 적용
def make_tr_request(...):
    token = self._acquire_token_with_optimizer()
    headers = self._build_tr_headers(tr_code, token, cont_yn, next_key)
    return self._execute_tr_request(method, endpoint, headers, data, params)
```

---

## 3. 리팩토링 권장사항

### 3.1 즉시 조치 (Quick Wins)

| 우선순위 | 조치 | 영향도 | 작업량 |
|----------|------|--------|--------|
| 1 | `kiwoom_rest_legacy.py` 삭제 | 높음 | 낮음 |
| 2 | `simple_api_facade.py` 삭제 | 중간 | 낮음 |
| 3 | 날짜 처리 헬퍼 함수 추출 | 낮음 | 낮음 |

### 3.2 중기 리팩토링 (1-2주)

| 우선순위 | 대상 | 패턴 | 예상 효과 |
|----------|------|------|----------|
| 1 | `get_minute_chart_with_date` | Extract Method | 복잡도 21→8 |
| 2 | `make_tr_request` | Extract Method | 복잡도 17→10 |
| 3 | `get_minute_chart_paginated` | Strategy | 복잡도 14→8 |

### 3.3 장기 아키텍처 개선

#### 3.3.1 Unified API 정리
현재 여러 "통합" 클래스가 존재:
- `KiwoomRest` (메인)
- `UnifiedKiwoomRest`
- `KiwoomRestBase`

**권장**: 단일 진입점으로 통합
```
KiwoomRest (Facade)
├── AuthAPI
├── StockAPI
├── ChartAPI
├── AccountAPI
├── OrderAPI
├── RankingAPI
└── SectorAPI
```

#### 3.3.2 Rate Limiting 추상화
현재 rate limiting이 여러 곳에 분산:
- `base_api.py`
- `api_facade.py`
- `rate_limit_optimizer.py`

**권장**: Strategy 패턴으로 통합
```python
class RateLimitStrategy(Protocol):
    def acquire(self) -> bool: ...
    def release(self) -> None: ...

class TokenBucketStrategy(RateLimitStrategy): ...
class MultiCredentialStrategy(RateLimitStrategy): ...
```

---

## 4. 테스트 영향 분석

### 삭제 시 테스트 확인 필요

```bash
# 삭제 전 테스트 실행
pytest tests/ -v --tb=short

# 특정 파일 의존성 확인
grep -r "kiwoom_rest_legacy" tests/
grep -r "simple_api_facade" tests/
```

---

## 5. 실행 계획

### Phase 1: Dead Code 제거 (즉시)
```bash
# 1. 안전 백업
git checkout -b refactor/cleanup-$(date +%Y%m%d)

# 2. Legacy 파일 삭제
rm src/pykiwoom_rest/kiwoom_rest_legacy.py
rm src/pykiwoom_rest/simple_api_facade.py

# 3. 테스트 확인
pytest tests/ -v

# 4. 커밋
git commit -m "♻️ refactor: remove unused legacy files"
```

### Phase 2: 복잡도 개선 (1주)
1. `chart_api.py` 메서드 분리
2. `kiwoom_base.py` 메서드 분리
3. 날짜 처리 유틸리티 추출

### Phase 3: 아키텍처 정리 (2주)
1. Unified 클래스 통합
2. Rate Limiting 추상화
3. 문서 업데이트

---

## 6. 메트릭 목표

| 메트릭 | 현재 | 목표 |
|--------|------|------|
| 최대 파일 줄 수 | 1,946 | < 800 |
| 최대 순환 복잡도 | 21 (D) | < 10 (B) |
| 최저 MI 점수 | 0.00 (C) | > 40 (A) |
| Dead Code | 2,300줄+ | 0줄 |

---

*Generated by Claude Code Refactoring Analysis*
