# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🏗️ Project Architecture

**PyKiwoom-Rest v2**는 모듈화된 아키텍처를 사용하는 Kiwoom증권 REST API Python Wrapper입니다.

### Core Components
- `src/pykiwoom_rest/`: 메인 패키지 디렉토리
  - `kiwoom_rest.py`: 통합 API wrapper 클래스
  - `base_api.py`: Rate limiting 및 에러 처리 기본 클래스
  - `kiwoom_base.py`: Kiwoom API 공통 기능
  - `*_api.py`: 기능별 API 모듈 (stock, chart, account, order, ranking, sector)
  - `response_model.py`: API 응답 모델
- `tests/`: 테스트 코드
- `main.py`: 메인 실행 파일
- **Postman Integration**: API 테스트용 Postman Collection 제공

### Modular API Architecture Pattern
```python
# 모듈화된 아키텍처 - 각 API 영역별 별도 클래스:
from pykiwoom_rest import KiwoomRest

kiwoom = KiwoomRest()

# 시세 조회
stock_info = kiwoom.get_stock_price("005930")

# 차트 데이터 (페이지네이션 지원)
minute_data = kiwoom.get_minute_chart_paginated(
    stock_code="005930", 
    interval=5,
    start_date="20250101",
    end_date="20250131"
)

# 계좌 조회
balance = kiwoom.get_account_balance()

# 주문 실행  
result = kiwoom.buy_order("005930", quantity=1, price=70000)
```

### Authentication Flow
1. 환경변수에서 인증정보 로드 (`.env` 파일)
2. OAuth2 토큰 자동 발급/갱신 (`_get_access_token()`)
3. 해시키 생성이 필요한 POST 요청 처리 (`_get_hashkey()`)

## 🔧 Development Commands

### Environment Setup
```bash
# Python 사용 (시스템 기본)
python3 --version  # Python 3.10.12

# 의존성 설치
pip3 install -r requirements.txt

# 환경변수 설정 (.env 파일 생성 필요)
# ACCOUNT_NO=계좌번호
# KIWOOM_APPKEY=앱키  
# KIWOOM_APPSECRET=앱시크릿
```

### Testing & Validation
```bash
# 패키지 테스트 실행
python -m pytest tests/

# 특정 API 테스트
python -m pytest tests/test_stock_api.py
python -m pytest tests/test_chart_api.py

# 메인 실행 파일 테스트
python main.py

# 개별 모듈 테스트 (Python REPL)
python3 -c "from src.pykiwoom_rest import KiwoomRest; print('Import OK')"
```

### Postman API Testing
```bash
# Postman Collection 파일들:
# - Kiwoom_REST_API_Collection.postman_collection.json
# - Kiwoom_Environment.postman_environment.json
# - POSTMAN_SETUP_GUIDE.md (상세 설정 가이드)

# 환경변수를 설정한 후 Postman에서 Collection Import하여 테스트
```

## 📊 Key Implementation Details

### Rate Limiting & API Constraints
- API 호출 제한: 초당 20회
- 토큰 유효기간: 24시간 (자동 갱신)
- 일부 API는 장 시간에만 정상 작동

### Pagination Support
분봉 데이터 등 대량 조회를 위한 페이지네이션 구현:
```python
# 대량 데이터 자동 수집
get_minute_chart_paginated(stock_code, interval, start_date, end_date, max_records)
```

### Error Handling Pattern
```python
try:
    result = kiwoom.api_method(params)
    if 'output' in result:
        # 정상 처리
    else:
        # 데이터 없음 처리
except Exception as e:
    # 연결/인증 오류 처리
```

## 🔍 Core TR Codes & Endpoints

### 필수 시세 조회 TR
- `ka10001`: 주식기본정보요청 (`get_stock_price`)
- `ka10004`: 주식호가요청 (`get_stock_orderbook`)
- `ka10080`: **주식분봉차트조회요청** (`get_minute_chart`) - 핵심 기능

### 차트 데이터 TR
- `ka10081`: 일봉차트 (`get_daily_chart`)
- `ka10082`: 주봉차트 (`get_weekly_chart`)
- `ka10083`: 월봉차트 (`get_monthly_chart`)

### 기관/외국인 매매 TR
- `ka10008`: 외국인종목별매매동향 (`get_foreign_trading`)
- `ka10044`: 일별기관매매종목 (`get_institutional_daily_trading`)

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
├── src/pykiwoom_rest/                          # 메인 패키지
│   ├── __init__.py                            # 패키지 초기화
│   ├── kiwoom_rest.py                         # 통합 API wrapper
│   ├── base_api.py                            # Rate limiter 및 기본 API 클래스
│   ├── kiwoom_base.py                         # Kiwoom API 공통 기능
│   ├── stock_api.py                           # 주식 시세 API
│   ├── chart_api.py                           # 차트 데이터 API
│   ├── account_api.py                         # 계좌 관련 API
│   ├── order_api.py                           # 주문 관련 API
│   ├── ranking_api.py                         # 순위 및 통계 API
│   ├── sector_api.py                          # 업종 관련 API
│   ├── response_model.py                      # API 응답 모델
│   └── kiwoom.xlsx                           # API 엔드포인트 참조
├── tests/                                     # 테스트 코드
├── main.py                                    # 메인 실행 파일
├── requirements.txt                           # 의존성 패키지
├── .env                                      # 환경설정 (local only)
├── KIWOOM_API_SPECIFICATION.md               # API 명세서
├── Kiwoom_REST_API_Collection.postman_collection.json  # Postman Collection
├── Kiwoom_Environment.postman_environment.json        # Postman 환경변수
└── POSTMAN_SETUP_GUIDE.md                   # Postman 설정 가이드
```

## 💡 Development Patterns

### 새로운 API 추가 시
1. `KIWOOM_API_SPECIFICATION.md`에서 TR 코드 및 엔드포인트 확인
2. 해당 기능에 맞는 `*_api.py` 모듈에 메서드 추가
3. `src/pykiwoom_rest/kiwoom_rest.py`에서 통합 메서드 노출
4. `tests/` 디렉토리에 테스트 함수 추가
5. Postman Collection에 새 API 엔드포인트 추가

### 데이터 처리 패턴
```python
# API 응답 → DataFrame 변환이 일반적
import pandas as pd
df = pd.DataFrame(result['output2'])  # output2가 리스트 데이터
```

### 날짜 형식 표준
- API 입력: "YYYYMMDD" (예: "20250115")
- Python datetime: `strftime("%Y%m%d")`

## 🔄 Testing Strategy

### Python 테스트
테스트는 실제 API 연결이 필요하므로:
1. 환경변수 설정 확인 (`.env` 파일)
2. 네트워크 연결 상태 확인  
3. 장 시간 여부 확인 (일부 API)
4. Rate Limit 준수 (초당 20회)

### Postman 테스트
1. `Kiwoom_Environment.postman_environment.json` 환경변수 설정
2. `Get Access Token` API로 인증 토큰 발급
3. 각 API 카테고리별 순차적 테스트
4. Rate Limiting 자동 처리 확인

### 개발 워크플로우
- 새 기능 구현 → Python 단위 테스트 → Postman 통합 테스트
- 실험적 코드는 별도 브랜치에서 작성 후 검증
- 모든 변경사항은 기존 테스트 통과 확인 필수