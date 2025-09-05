# PyKiwoom REST API Examples

이 디렉토리는 PyKiwoom REST API 사용 예제와 성능 테스트를 포함합니다.

## 📁 Directory Structure

```
examples/
├── performance/           # 성능 테스트 및 벤치마크
│   ├── test_rate_limit_simple.py      # Rate limiting 기본 테스트
│   ├── test_rate_limit_live.py        # 실시간 rate limiting 테스트
│   ├── test_concurrent_performance.py # 병렬 처리 성능 테스트
│   └── test_async_parallel.py         # 비동기 처리 테스트
├── demos/                 # 실제 사용 데모
└── README.md             # 이 파일
```

## 🚀 Performance Tests

### 1. Rate Limiting Tests
```bash
# 기본 Rate Limiting 테스트
python examples/performance/test_rate_limit_simple.py

# 실시간 Rate Limiting 최적화 테스트
python examples/performance/test_rate_limit_live.py
```

**결과 예시:**
```
기준선 (단일 크레덴셜): 41.64 req/s
최적화 (다중 크레덴셜): 16.46 req/s (안정적)
429 에러: 0회
```

### 2. Concurrent Processing Tests
```bash
# 병렬 처리 성능 비교
python examples/performance/test_concurrent_performance.py

# 비동기 처리 테스트
python examples/performance/test_async_parallel.py
```

**성능 비교:**
- **순차 처리**: ~48 req/s (단일 종목)
- **스레드 풀**: ~25 req/s (최적 워커 3-5개)
- **비동기**: ~70 req/s (토큰 제한 없을 때)

## 📊 Test Results Summary

### Rate Limiting 최적화
| 테스트 | 처리량 | 에러율 | 특징 |
|--------|---------|--------|------|
| 단일 크레덴셜 | 48.92 req/s | 0% | 빠르지만 제한적 |
| 다중 크레덴셜 | 16.46 req/s | 0% | 안정적이고 확장 가능 |
| 버스트 모드 | 15.73 req/s | 0% | 대량 처리에 적합 |

### 병렬 처리
| 방식 | 10종목 처리시간 | 처리량 | 권장 사용 |
|------|----------------|--------|-----------|
| 순차 처리 | 0.24초 | 41.64 req/s | 10개 이하 |
| 스레드 풀(5) | 1.22초 | 8.19 req/s | 10-50개 |
| 자동 최적화 | 동적 | 최적화됨 | 50개 이상 |

## 🎯 Usage Recommendations

### 소량 데이터 (1-10종목)
```python
# 단순한 순차 처리가 가장 빠름
kiwoom = KiwoomRest()
for code in stock_codes:
    result = kiwoom.get_stock_price(code)
```

### 중간 규모 (10-50종목)
```python
# 스레드 풀 사용
from pykiwoom_rest.concurrent_api import fetch_stocks_parallel
results = fetch_stocks_parallel(stock_codes, max_workers=5)
```

### 대량 데이터 (50종목 이상)
```python
# 자동 최적화 모드
from pykiwoom_rest.concurrent_api import OptimizedBatchProcessor
processor = OptimizedBatchProcessor()
result = processor.auto_process(stock_codes)
```

### Rate Limit 회피
```python
# 다중 크레덴셜 로테이션
credentials = [
    {'APPKEY': 'key1', 'APPSECRET': 'secret1'},
    {'APPKEY': 'key2', 'APPSECRET': 'secret2'},
]
kiwoom = KiwoomRest(
    enable_rate_optimizer=True,
    credentials_list=credentials
)
```

## 📝 Running Tests

### Prerequisites
1. `.env` 파일에 키움 API 인증 정보 설정
2. 필요 패키지 설치: `pip install -r requirements.txt`

### 전체 성능 테스트 실행
```bash
# 모든 성능 테스트 순차 실행
for test in examples/performance/test_*.py; do
    echo "Running $test..."
    python "$test"
    echo "---"
done
```

### 개별 테스트 실행
```bash
# Rate limiting 기본 테스트
python examples/performance/test_rate_limit_simple.py

# 고급 성능 테스트
python examples/performance/test_concurrent_performance.py
```

## 🔧 Customization

테스트 파라미터를 수정하여 다양한 시나리오를 테스트할 수 있습니다:

### 종목 코드 변경
```python
# test_*.py 파일에서 수정
TEST_STOCKS = [
    "005930",  # 삼성전자
    "000660",  # SK하이닉스
    # ... 추가 종목
]
```

### 성능 파라미터 조정
```python
# Worker 수 조정
max_workers = 10

# Rate limit 조정
rate_limit = 20

# 테스트 지속 시간 조정
test_duration = 30  # seconds
```

## 📈 Performance Monitoring

테스트 실행 시 다음 메트릭들이 측정됩니다:

- **처리량 (req/s)**: 초당 처리 가능한 요청 수
- **성공률 (%)**: 전체 요청 대비 성공한 요청 비율
- **평균 응답 시간**: 요청당 평균 소요 시간
- **429 에러 발생률**: Rate limit 에러 발생 비율

## 🚨 Important Notes

1. **API Rate Limit**: 키움 API는 초당 20회 제한이 있습니다
2. **장 시간 제한**: 일부 API는 장 시간에만 정상 작동합니다
3. **네트워크 의존**: 실제 성능은 네트워크 상황에 따라 달라집니다
4. **크레덴셜 보안**: 여러 계정 사용 시 보안에 주의하세요

---
*Performance tests last updated: 2025-01-05*