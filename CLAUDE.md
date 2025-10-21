# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🏗️ Project Architecture

**PyKiwoom-REST v2**는 고도로 최적화된 모듈화 아키텍처를 사용하는 Kiwoom증권 REST API Python Wrapper입니다.

### Core Architecture Layers
```
┌─────────────────────────────────────────────┐
│  KiwoomRest (Unified Facade)                │ ← Public API
├─────────────────────────────────────────────┤
│  Modular API Classes                        │
│  (StockAPI, ChartAPI, AccountAPI, etc.)     │ ← Domain-specific logic
├─────────────────────────────────────────────┤
│  KiwoomRestBase → KiwoomAPIBase             │ ← Core request handling
├─────────────────────────────────────────────┤
│  BaseAPIClient (Rate Limiting, Auth)        │ ← Infrastructure
├─────────────────────────────────────────────┤
│  GlobalRateLimiter, ResponseUtils           │ ← Cross-cutting concerns
└─────────────────────────────────────────────┘
```

### Key Components
- **`kiwoom_rest.py`**: 통합 Facade - 모든 API 메서드를 단일 진입점으로 제공 (Legacy 호환)
- **`*_api.py`** (auth, stock, chart, account, order, ranking, sector): 기능별 모듈러 API 클래스
  - **`auth_api.py`** ⭐ NEW: OAuth2 인증 관련 API (토큰 발급/폐기, au10001/au10002)
  - **`stock_api.py`**: 주식 시세 정보 API
  - **`chart_api.py`**: 차트 데이터 API (분봉, 일봉, 주봉, 월봉)
  - **`account_api.py`**: 계좌 정보 및 잔고 조회 API
  - **`order_api.py`**: 주문 실행 API
  - **`ranking_api.py`**: 순위 정보 API
  - **`sector_api.py`**: 업종 정보 API
- **`base_api.py`**: Rate limiting, 토큰 관리, 에러 처리 기본 클래스
- **`kiwoom_base.py`/`kiwoom_rest_base.py`**: Kiwoom API 공통 기능 및 요청 처리
- **`api_facade.py`**: 중앙집중식 Rate Limit 관리 (GlobalRateLimiter, APIRequest)
- **`rate_limit_optimizer.py`**: 다중 크레덴셜 로테이션, 지능형 최적화
- **`response_model.py`/`response_utils.py`**: 응답 파싱 및 타입 변환
- **`exception_utils.py`**: 통일된 예외 처리 및 재시도 로직

### Unified Facade Usage Pattern
```python
from pykiwoom_rest import KiwoomRest

# 단일 인스턴스로 모든 API 접근
kiwoom = KiwoomRest(enable_rate_optimizer=True)

# ===== 인증 관리 (AuthAPI) =====
# 토큰 발급 (자동 처리, 필요시 수동 호출)
token_info = kiwoom.get_access_token()
print(f"Token: {token_info['token']}, Expires: {token_info['expires_at']}")

# 토큰 상태 확인
status = kiwoom.get_token_status()
if status['needs_refresh']:
    kiwoom.refresh_token()

# 직접 API 접근
auth_result = kiwoom.auth.get_token_status()

# ===== 주식 시세 (StockAPI) =====
price = kiwoom.get_stock_price("005930")

# ===== 차트 데이터 (ChartAPI, 페이지네이션 자동) =====
chart = kiwoom.get_minute_chart_paginated(
    stock_code="005930",
    interval=5,
    start_date="20250101",
    end_date="20250131"
)

# ===== 계좌 관리 (AccountAPI) =====
balance = kiwoom.get_account_balance()

# ===== 주문 실행 (OrderAPI) =====
order = kiwoom.buy_order("005930", quantity=10, price=70000)

# ===== 순위 정보 (RankingAPI) =====
top_gainers = kiwoom.get_top_gainers()

# ===== 로그아웃 =====
kiwoom.logout()  # 토큰 폐기 및 세션 정리
```

### Authentication & Token Management Flow
1. `.env` 또는 환경변수에서 인증정보 로드
2. `BaseAPIClient._get_access_token()`: OAuth2 토큰 자동 발급
3. 토큰 만료 시 자동 갱신 (24시간 주기)
4. POST 요청은 `_get_hashkey()` 로 데이터 무결성 보장

## 🔧 Development Commands

### Environment Setup
```bash
# Python 버전 확인 (3.10+ 권장)
python3 --version

# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 개발 의존성 설치
pip install -e ".[dev]"

# 또는 직접 설치
pip install -r requirements.txt
```

### Environment Variables Setup
```bash
# .env 파일 생성 (프로젝트 루트)
cat > .env << EOF
ACCOUNT_NO=your-account-number
KIWOOM_APPKEY=your-app-key
KIWOOM_APPSECRET=your-app-secret
EOF

# 다중 크레덴셜 (선택사항)
KIWOOM_APPKEY_1=secondary-key
KIWOOM_APPSECRET_1=secondary-secret
```

### Code Quality & Linting
```bash
# 자동 포맷팅 (Ruff)
ruff format src/pykiwoom_rest/ tests/

# 린팅 검사 및 자동 수정
ruff check src/pykiwoom_rest/ tests/ --fix

# 타입 체킹 (MyPy)
mypy src/pykiwoom_rest --ignore-missing-imports

# 한 번에 모두 (스크립트 사용)
./scripts/format.sh
./scripts/lint.sh
```

### Testing Strategy
```bash
# 전체 테스트 실행
./scripts/test.sh
# or
python -m pytest tests/ -v

# 커버리지 리포트 포함
pytest tests/ --cov=src/pykiwoom_rest --cov-report=html

# 특정 테스트 파일만 실행
pytest tests/test_stock_api.py -v
pytest tests/test_chart_api.py -v

# 특정 테스트 함수 실행
pytest tests/ -k "test_rate_limiter" -v

# 슬로우 테스트 제외
pytest tests/ -m "not slow" -v

# 마커별 테스트 실행
pytest tests/ -m "integration" -v     # 통합 테스트만
pytest tests/ -m "unit" -v             # 단위 테스트만
```

### Quick Validation
```bash
# 패키지 임포트 검증
python3 -c "from pykiwoom_rest import KiwoomRest; print('✓ Import OK')"

# 메인 실행 파일 테스트
python main.py

# 성능 벤치마크 (선택사항)
python examples/performance/test_concurrent_performance.py
```

## 📊 Key Implementation Details

### Rate Limiting Strategy
- **기본 제한**: 초당 20회 (Kiwoom API 정책)
- **다중 크레덴셜 로테이션**: 여러 계정으로 요청을 분산하여 실제 처리량 증가
- **지능형 최적화** (`rate_limit_optimizer.py`):
  - 요청 패턴 분석
  - 429 에러 자동 감지 및 재시도
  - 토큰 효율적 관리
- **Token Bucket Algorithm**: 공정한 요청 분배 (`TokenBucketRateLimiter`)

### API Constraints & Behavior
- **토큰 유효기간**: 24시간 (자동 갱신)
- **장 시간 의존성**: 일부 API (시세, 차트)는 장 시간에만 정상 작동
- **POST 요청**: 해시키 생성 필수 (`_get_hashkey()`)
- **Response Format**: 대부분 `output`/`output2` 키로 데이터 반환

### Pagination Implementation
분봉 등 대량 데이터 자동 수집:
```python
# ChartAPI에서 구현
chart = kiwoom.get_minute_chart_paginated(
    stock_code="005930",
    interval=5,
    start_date="20250101",
    end_date="20250131",
    max_records=5000  # 최대 5000개까지 자동 수집
)
```

### Error Handling Hierarchy
```python
# exception_utils.py 에서 정의된 통일된 예외 처리
from pykiwoom_rest import APIError, RateLimitExceededError

try:
    result = kiwoom.get_stock_price("005930")
except RateLimitExceededError:
    # 요청 제한 초과 - 재시도 로직
    pass
except APIError as e:
    # API 에러 - 오류 코드 확인 후 처리
    if e.error_code == "조회가능한 거래량이 부족합니다":
        # 데이터 없음 처리
        pass
```

### Response Parsing Pattern
```python
# response_utils.py 활용
from pykiwoom_rest.response_utils import parse_response, to_dataframe

# API 응답 파싱
result = kiwoom.get_minute_chart("005930", interval=5, count=100)

# DataFrame 변환
if result.data and 'output2' in result.data:
    df = to_dataframe(result.data['output2'])
    print(df.head())
```

## 🔍 Core TR Codes & Endpoints

### Authentication API (OAuth2 인증) ⭐ NEW
- `au10001`: 접근토큰발급 (POST /oauth2/token)
  - `kiwoom.get_access_token()`: 토큰 발급 (자동 처리)
  - 입력: appkey, appsecret
  - 출력: access_token, token_type, expires_in
  - 만료: 24시간 (자동 갱신)
- `au10002`: 접근토큰폐기 (POST /oauth2/revoke)
  - `kiwoom.revoke_token()`: 토큰 폐기
  - `kiwoom.logout()`: 토큰 폐기 + 세션 정리

**AuthAPI 사용 예시**:
```python
from pykiwoom_rest import KiwoomRest

kiwoom = KiwoomRest()

# 토큰 상태 확인
status = kiwoom.get_token_status()
print(f"Token valid: {status['is_valid']}, 만료: {status['expires_at']}")

# 필요시 갱신
if status['needs_refresh']:
    token = kiwoom.refresh_token()

# 직접 API 접근
auth = kiwoom.auth
token_info = auth.get_access_token(force_refresh=True)

# 로그아웃
kiwoom.logout()
```

### Stock API (시세 정보)
- `ka10001`: 주식기본정보요청 → `get_stock_price()`
- `ka10004`: 주식호가요청 → `get_stock_orderbook()`
- `ka10008`: 외국인종목별매매동향 → `get_foreign_trading()`

### Chart API (차트 데이터) - 핵심 기능
- `ka10080`: **주식분봉차트조회요청** → `get_minute_chart()/get_minute_chart_paginated()`
- `ka10081`: 일봉차트 → `get_daily_chart()`
- `ka10082`: 주봉차트 → `get_weekly_chart()`
- `ka10083`: 월봉차트 → `get_monthly_chart()`

### Ranking API (순위 정보)
- `ka10031`: 거래대금 상위 종목
- `ka10037`: 등락률 상위 종목
- `ka10038`: 거래량 상위 종목
- `ka10053`: 외국인 순매수 상위 종목
- `ka10062`: 시가총액 상위 종목

### Account API (계좌 관리)
- `tb6012`: 잔고 조회 → `get_account_balance()`
- `tb6000`: 주문 체결 확인
- `tb6030`: 매매 손익 조회

### Order API (주문 실행)
- `bo6001`: 매매 주문 → `buy_order()/sell_order()`
- `bo5001`: 주문 취소 → `cancel_order()`

**모든 API 명세는 `pykiwoom.xlsx` 참조 (별도 동기화 필요)**

## 🚨 Security & Environment

### Required Environment Variables
```bash
ACCOUNT_NO=12345678
KIWOOM_APPKEY=your-app-key
KIWOOM_APPSECRET=your-app-secret
```

### Security Best Practices
- `.env` 파일은 절대 버전 관리에 포함 금지
- API 키는 환경변수에서만 로드
- 토큰은 메모리에서만 관리, 파일 저장 금지

## 📂 Directory Structure Context

```
pykiwoom-rest/
├── src/pykiwoom_rest/                          # 📦 메인 패키지
│   ├── __init__.py                            # 패키지 초기화 및 export
│   │
│   ├── kiwoom_rest.py                         # ⭐ Unified Facade (공개 API)
│   ├── kiwoom_rest_base.py                    # 파사드 기본 클래스
│   ├── kiwoom_base.py                         # Kiwoom API 공통 기능
│   ├── unified_kiwoom_rest.py                 # 통합 기능 (레거시)
│   ├── unified_kiwoom_base.py                 # 통합 기본 클래스
│   │
│   ├── api_facade.py                          # 🔄 중앙 Rate Limiter (GlobalRateLimiter)
│   ├── base_api.py                            # 🛡️ 기본 API 클래스 (토큰, 에러 처리)
│   ├── rate_limit_optimizer.py                # ⚙️ 지능형 Rate Limit 최적화
│   ├── simple_api_facade.py                   # 간단한 파사드
│   │
│   ├── stock_api.py                           # 📈 주식 시세 API
│   ├── chart_api.py                           # 📊 차트 데이터 API
│   ├── account_api.py                         # 💼 계좌 관련 API
│   ├── order_api.py                           # 📋 주문 실행 API
│   ├── ranking_api.py                         # 🏆 순위 정보 API
│   ├── sector_api.py                          # 🏭 업종 정보 API
│   │
│   ├── response_model.py                      # 📋 응답 모델 (APIResponse)
│   ├── response_utils.py                      # 🔧 응답 파싱 유틸리티
│   ├── exception_utils.py                     # ⚠️ 통일된 예외 처리
│   ├── async_api.py                           # ⚡ 비동기 처리
│   ├── concurrent_api.py                      # 🧵 병렬 처리
│   └── kiwoom_rest_legacy.py                  # 레거시 호환성
│
├── tests/                                     # 🧪 테스트 코드 (127개 케이스)
├── scripts/                                   # 🛠️ 개발 스크립트
│   ├── format.sh                             # Ruff 포맷팅
│   ├── lint.sh                               # Ruff 린팅
│   └── test.sh                               # 테스트 실행
├── examples/                                  # 📖 사용 예제
│   ├── performance/                          # 성능 벤치마크
│   └── pykiwoom.ipynb                        # Jupyter 예제
├── pykiwoom-adapter/                          # 어댑터 (별도 모듈)
├── .github/workflows/                         # CI/CD 설정
├── pyproject.toml                             # 프로젝트 설정 (Ruff, Pytest, MyPy)
├── requirements.txt                           # 의존성
├── pykiwoom.xlsx                              # API 명세 (TR 코드 및 필드)
├── DEVELOPMENT.md                             # 개발 가이드
├── CLAUDE.md                                  # 이 문서
└── README.md                                  # 프로젝트 문서
```

**주요 특징**:
- `kiwoom_rest.py`는 모든 API 메서드를 단일 클래스로 제공 (사용자 편의)
- 내부는 `*_api.py` 모듈로 분리되어 유지보수성 우수
- `api_facade.py`의 `GlobalRateLimiter`로 중앙집중식 Rate Limit 관리

## 💡 Development Patterns

### 새로운 API 추가 시
1. **API 명세 확인**: `pykiwoom.xlsx`에서 TR 코드, URL, 필드 명세 파악
2. **모듈 선택**: 기능에 맞는 `*_api.py` 모듈 선택 또는 생성
3. **메서드 구현** (예: `stock_api.py`):
   ```python
   def get_new_data(self, stock_code: str) -> APIResponse:
       """새로운 API 데이터 조회"""
       # KiwoomRestBase 상속으로 자동으로 Rate Limit 관리
       result = self.request(
           method="GET",
           endpoint="/path/to/api",
           params={"stk_code": stock_code}
       )
       return self._parse_response(result)
   ```
4. **Facade 메서드 노출** (`kiwoom_rest.py`):
   ```python
   def get_new_data(self, stock_code: str) -> Dict[str, Any]:
       """새로운 API 데이터 조회 (통합 API)"""
       return self.stock_api.get_new_data(stock_code).data
   ```
5. **테스트 작성**: `tests/test_stock_api.py`에 테스트 케이스 추가
6. **CI/CD 검증**: GitHub Actions에서 자동 테스트 실행

### API Response 처리 패턴
```python
# BaseAPIClient에서 자동으로 처리됨
from pykiwoom_rest import APIResponse

result = kiwoom.get_stock_price("005930")  # APIResponse 반환

# 데이터 접근
if result.success:
    price = result.data['cur_prc']
    volume = result.data['acc_vol']
else:
    # 에러 처리
    print(f"Error: {result.error}")
```

### 대량 데이터 처리 (DataFrame)
```python
# response_utils 활용
from pykiwoom_rest.response_utils import to_dataframe

chart = kiwoom.get_minute_chart("005930", interval=5, count=100)
if 'output2' in chart.data:
    df = to_dataframe(chart.data['output2'])
    # 기술적 지표 계산
    df['MA20'] = df['stck_clpr'].rolling(20).mean()
```

### 날짜 형식 표준
- **API 입력 형식**: "YYYYMMDD" (예: "20250115")
- **Python 변환**: `datetime.strftime("%Y%m%d")`
- **권장 방식**: `from datetime import datetime; date_str = datetime.now().strftime("%Y%m%d")`

### 에러 처리 Best Practice
```python
from pykiwoom_rest import RateLimitExceededError, APIError

def safe_api_call():
    try:
        result = kiwoom.get_stock_price("005930")
    except RateLimitExceededError:
        # 자동 재시도 (exponential backoff)
        time.sleep(2)
        return safe_api_call()
    except APIError as e:
        if "조회가능한" in str(e):
            return None  # 데이터 없음
        raise  # 다른 에러는 전파
```

## 🔄 Testing Strategy

### 테스트 전 필수 조건
1. `.env` 파일 설정 (환경변수)
2. 네트워크 연결 확인
3. 장 시간 여부 확인 (시세 API)
4. Kiwoom 계정 유효성 확인

### 테스트 타입별 실행
```bash
# 단위 테스트 (모의 객체 사용)
pytest tests/ -m "unit" -v

# 통합 테스트 (실제 API)
pytest tests/ -m "integration" -v

# 성능 테스트 (Rate Limit)
pytest tests/ -m "performance" -v

# 특정 기능 테스트
pytest tests/test_rate_limit_optimizer.py::test_multi_credential_rotation -v
```

### CI/CD 파이프라인 (`.github/workflows/ci.yml`)
1. **Linting** (Python 3.12): Ruff 포맷 및 코드 스타일 검사
2. **Testing** (Python 3.8, 3.10, 3.12): 모든 버전에서 테스트
3. **Type Checking** (Python 3.12): MyPy로 타입 검증
4. **Coverage**: Codecov 자동 업로드

### 개발 워크플로우
```bash
# 1. 기능 개발
git checkout -b feature/new-api

# 2. 로컬 테스트
./scripts/lint.sh
./scripts/test.sh
pytest tests/test_*.py -v

# 3. 커밋 및 푸시
git add .
git commit -m "feat: add new API method"
git push origin feature/new-api

# 4. PR 생성 → GitHub Actions 자동 검증 → Merge
```

## Task Master AI Instructions
**Import Task Master's development workflow commands and guidelines, treat as if import is in the main CLAUDE.md file.**
@./.taskmaster/CLAUDE.md
