# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🏗️ Project Architecture

**PyKiwoom-Rest v2**는 통합 아키텍처를 사용하는 Kiwoom증권 REST API Python Wrapper입니다.

### Core Components
- `kiwoom_rest.py`: 통합 API wrapper 클래스 (`KiwoomRestBase` + `KiwoomRest`)
- `test_kiwoom.py`: 기존 테스트 스위트 (호환성 유지)
- `example.py`: 사용 예제 및 데모 코드
- `testing/`: 새로운 아키텍처 테스트 및 실험 코드
- `kiwoom_rest_extended.py`: 추가 API 엔드포인트 구현 예제

### Unified API Architecture Pattern
```python
# pykis 스타일의 통합 아키텍처:
def api_method(self, params) -> dict:
    return self.make_request(
        endpoint_key='stock_info',      # ENDPOINTS 매핑에서 선택
        tr_id_key='stock_basic_info',   # TR_CODES 매핑에서 선택
        params=params
    )

# 저수준 API 직접 호출:
result = kiwoom.make_request('chart', 'minute_chart', params=params)

# DataFrame 자동 변환:
df = kiwoom.to_dataframe(result, numeric_fields=['stck_prpr', 'acml_vol'])
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
# 기존 테스트 실행 (호환성 확인)
python3 test_kiwoom.py

# 새로운 아키텍처 테스트
python3 testing/test_new_architecture.py

# 기본 사용 예제 실행
python3 example.py

# 개별 모듈 테스트 (Python REPL)
python3 -c "from kiwoom_rest import KiwoomRest; print('Import OK')"
```

### Data Analysis & Development
```bash
# testing/ 디렉토리의 분석 스크립트
python3 testing/analyze_excel_250115.py

# API 엔드포인트 추출 및 분석
python3 testing/extract_api_endpoints.py
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
├── kiwoom_rest.py          # 메인 래퍼 클래스
├── test_kiwoom.py          # 통합 테스트
├── example.py              # 사용 예제
├── requirements.txt        # 의존성 (requests, dotenv, pandas, openpyxl)
├── .env                   # 환경설정 (local only)
├── kiwoom.xlsx            # API 엔드포인트 참조
├── API.md                 # 전체 TR 코드 문서
└── testing/               # 실험/분석 코드
    ├── analyze_excel_250115.py
    └── market_apis.csv
```

## 💡 Development Patterns

### 새로운 API 추가 시
1. `API.md`에서 TR 코드 및 엔드포인트 확인
2. `kiwoom_rest.py`에 메서드 추가 (기존 패턴 따름)
3. `test_kiwoom.py`에 테스트 함수 추가
4. `example.py`에 사용 예제 추가

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

테스트는 실제 API 연결이 필요하므로:
1. 환경변수 설정 확인
2. 네트워크 연결 상태 확인  
3. 장 시간 여부 확인 (일부 API)
4. Rate Limit 준수

실험적 코드는 `testing/` 디렉토리에서만 작성하고, 검증 후 메인 모듈로 이동.