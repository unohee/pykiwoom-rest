# PyKiwoom MCP Server

**키움증권 REST API를 위한 MCP 서버 - 동적 Tool 생성 방식**

이 프로젝트는 [pykiwoom-rest](../README.md) 라이브러리의 **모든 메서드를 자동으로** MCP 도구로 노출합니다. Claude Desktop 등의 MCP 클라이언트에서 키움증권 API 전체를 자연어로 쉽게 사용할 수 있습니다.

## 주요 특징

### 🚀 동적 Tool 생성
- **pykiwoom-rest의 모든 공개 메서드를 자동 감지**
- **70+ 개의 API 엔드포인트를 MCP tools로 노출**
- 수동 매핑 불필요 - 라이브러리 업데이트 시 자동 반영

### 📋 제공되는 Tool 카테고리

1. **Stock (시세)** - 20+ 개
   - 현재가, 호가, 외국인 매매, 프로그램 매매, 투자자별 동향 등

2. **Chart (차트)** - 10+ 개
   - 일/주/월/년봉, 분봉, 틱 차트, 페이지네이션 지원

3. **Account (계좌)** - 15+ 개
   - 잔고, 평가, 미체결, 체결내역, 손익, 거래일지 등

4. **Order (주문)** - 4개
   - 매수, 매도, 정정, 취소

5. **Ranking (순위)** - 15+ 개
   - 상승률/거래량/거래대금 상위, 외국인 순매수 등

6. **Sector (업종)** - 3개
   - 업종 시세, 지수, 차트

7. **Auth (인증)** - 5개
   - 토큰 발급/폐기, 상태 확인, 로그아웃

8. **list_endpoints** 🔍
   - 모든 API 엔드포인트 목록 조회 (카테고리별 필터 지원)

## 설치 방법

### 1. 사전 요구사항
```bash
# Python 3.10 이상 필요
python --version

# pykiwoom-rest 패키지 설치 (부모 디렉토리)
cd ..
pip install -e .
```

### 2. MCP 서버 설치
```bash
cd pykiwoom-mcp-server
pip install -e .

# 또는 의존성만 설치
pip install mcp>=0.9.0
```

### 3. 환경 변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 수정
ACCOUNT_NO=your-account-number
KIWOOM_APPKEY=your-app-key
KIWOOM_APPSECRET=your-app-secret
```

## 사용 방법

### Claude Desktop 설정

`~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) 또는 `%APPDATA%\Claude\claude_desktop_config.json` (Windows)에 다음 내용 추가:

```json
{
  "mcpServers": {
    "pykiwoom": {
      "command": "python",
      "args": [
        "/absolute/path/to/pykiwoom-rest/pykiwoom-mcp-server/src/pykiwoom_mcp_server/server.py"
      ],
      "env": {
        "ACCOUNT_NO": "your-account-number",
        "KIWOOM_APPKEY": "your-app-key",
        "KIWOOM_APPSECRET": "your-app-secret"
      }
    }
  }
}
```

### 직접 실행 (테스트)
```bash
# MCP 서버 실행
python src/pykiwoom_mcp_server/server.py

# 설치 후 커맨드 사용
pykiwoom-mcp-server

# 테스트 실행
python test_server.py
```

## 사용 예시

### 1. 엔드포인트 목록 조회
```
User: 사용 가능한 모든 API 엔드포인트를 보여줘

Claude: [list_endpoints 도구 호출 - category: "all"]
총 72개의 엔드포인트가 있습니다:

Stock (시세): 23개
- get_stock_price (ka10001)
- get_stock_orderbook (ka10004)
- get_foreign_trading (ka10008)
...

Chart (차트): 12개
- get_daily_chart (ka10081)
- get_minute_chart (ka10080)
...
```

### 2. 카테고리별 조회
```
User: 차트 관련 API만 보여줘

Claude: [list_endpoints 도구 호출 - category: "chart"]
차트 관련 API 12개:
- get_tick_chart: 틱 차트 조회
- get_minute_chart: 분봉 차트 조회 (ka10080)
- get_minute_chart_paginated: 대량 분봉 페이지네이션
- get_daily_chart: 일봉 차트 (ka10081)
- get_weekly_chart: 주봉 차트 (ka10082)
- get_monthly_chart: 월봉 차트 (ka10083)
- get_yearly_chart: 년봉 차트 (ka10094)
...
```

### 3. 일반 API 호출
```
User: 삼성전자(005930) 현재가를 알려줘

Claude: [get_stock_price 도구 호출]
삼성전자의 현재가는 70,500원입니다.
전일 대비 +1,000원(+1.44%) 상승했습니다.
```

```
User: 오늘 상승률 상위 10개 종목은?

Claude: [get_previous_day_rate_top 도구 호출]
상승률 상위 10개 종목:
1. OO전자 +15.2%
2. XX바이오 +12.8%
...
```

### 4. 계좌 관리
```
User: 내 계좌 잔고를 보여줘

Claude: [get_account_evaluation 도구 호출]
계좌 평가 정보:
- 총 평가금액: 10,250,000원
- 총 수익률: +2.5%
- 보유 종목: 3개
```

## API 도구 상세

### list_endpoints (메타 도구)
모든 API 엔드포인트 목록 조회

**파라미터:**
- `category` (string, 선택): 카테고리 필터
  - `"all"`: 전체 (기본값)
  - `"stock"`: 시세 관련
  - `"chart"`: 차트 관련
  - `"account"`: 계좌 관련
  - `"order"`: 주문 관련
  - `"ranking"`: 순위 관련
  - `"sector"`: 업종 관련
  - `"auth"`: 인증 관련

**반환 형식:**
```json
{
  "total_endpoints": 72,
  "by_category": {
    "stock": 23,
    "chart": 12,
    "account": 15,
    "order": 4,
    "ranking": 15,
    "sector": 3,
    "auth": 5
  },
  "endpoints": {
    "stock": [
      {
        "name": "get_stock_price",
        "tr_code": "ka10001",
        "description": "주식 현재가 조회",
        "param_count": 1,
        "required_count": 1,
        "params": ["stock_code"]
      },
      ...
    ]
  }
}
```

### 동적 Tool 자동 생성

모든 pykiwoom-rest 메서드가 자동으로 MCP tools로 변환됩니다:

- **메서드 이름**: Tool 이름으로 사용
- **파라미터**: 타입 힌트 기반 자동 추출
- **필수 파라미터**: 기본값 없는 파라미터 자동 감지
- **TR 코드**: Docstring에서 자동 추출
- **설명**: Docstring 첫 줄 사용

## 동적 Tool 생성 장점

### 1. 유지보수 불필요
- pykiwoom-rest 업데이트 시 자동 반영
- 새로운 API 추가 시 수동 매핑 불필요

### 2. 완전성 보장
- 모든 공개 메서드를 100% 노출
- 누락된 API 없음

### 3. 타입 안전성
- Python 타입 힌트 기반 자동 스키마 생성
- 필수/선택 파라미터 자동 구분

### 4. 개발 속도 향상
- 새로운 API 추가 시 즉시 사용 가능
- MCP 서버 코드 수정 불필요

## Rate Limiting

이 MCP 서버는 pykiwoom-rest의 Rate Limit 최적화 기능을 활용합니다:

- 기본 Rate Limit: 초당 20회 (키움 API 정책)
- 다중 크레덴셜 지원: 여러 API 키를 로테이션하여 처리량 증가
- 자동 재시도: 429 에러 시 exponential backoff

## 보안 주의사항

1. **API 키 보안**
   - `.env` 파일을 절대 버전 관리에 포함하지 마세요
   - 프로덕션 환경에서는 환경 변수 또는 시크릿 관리 시스템 사용

2. **주문 실행**
   - `buy_stock`, `sell_stock`는 실제 거래를 발생시킵니다
   - 테스트 시에는 모의투자 계좌 사용 권장

3. **접근 제어**
   - MCP 서버는 로컬 stdio 통신만 지원 (네트워크 노출 없음)
   - Claude Desktop 등 신뢰할 수 있는 클라이언트에서만 사용

## 트러블슈팅

### 1. "pykiwoom_rest 패키지를 찾을 수 없습니다"
```bash
# 부모 디렉토리에서 pykiwoom-rest 설치
cd ..
pip install -e .

# 또는 PYTHONPATH 설정
export PYTHONPATH=/path/to/pykiwoom-rest/src:$PYTHONPATH
```

### 2. "PyKiwoom MCP Server started with 0 endpoints"
- Python 버전 확인 (3.10+)
- pykiwoom-rest 설치 확인
- 임포트 에러 확인 (stderr 로그)

### 3. "토큰 발급 실패"
- `.env` 파일의 API 키 확인
- 키움증권 API 신청 상태 확인
- 네트워크 연결 확인

### 4. "Rate Limit 초과"
- 다중 크레덴셜 설정 (`.env`에 `KIWOOM_APPKEY_1`, `KIWOOM_APPSECRET_1` 추가)
- 요청 간격 조정

## 개발

### 코드 구조
```python
class PyKiwoomMCPServer:
    def _build_method_registry(self):
        """KiwoomRest의 모든 메서드를 분석하여 레지스트리 구축"""
        # inspect 모듈로 동적 분석
        # 파라미터, 타입, TR 코드 자동 추출

    def _setup_handlers(self):
        @self.server.list_tools()
        async def list_tools():
            """레지스트리 기반 동적 Tool 생성"""

        @self.server.call_tool()
        async def call_tool(name, arguments):
            """동적 메서드 호출"""
```

### 테스트 실행
```bash
pytest tests/ -v
```

### 코드 포맷팅
```bash
ruff format src/
ruff check src/ --fix
```

## 라이선스

MIT License - [LICENSE](../LICENSE) 참조

## 관련 프로젝트

- [pykiwoom-rest](../README.md): 기반이 되는 Python 라이브러리 (70+ API 엔드포인트)
- [MCP Protocol](https://modelcontextprotocol.io/): Model Context Protocol 명세

## 통계

- **총 엔드포인트**: 72개 (동적 감지)
- **카테고리**: 7개 (Stock, Chart, Account, Order, Ranking, Sector, Auth)
- **코드 라인**: ~280줄 (자동 생성으로 간결함)
- **유지보수**: 거의 불필요 (자동 동기화)

## 기여

이슈 및 PR은 언제나 환영합니다!

## 지원

- 이슈 트래커: https://github.com/yourusername/pykiwoom-rest/issues
- 문서: https://github.com/yourusername/pykiwoom-rest/blob/main/README.md
- MCP Server Structure: [STRUCTURE.md](STRUCTURE.md)
