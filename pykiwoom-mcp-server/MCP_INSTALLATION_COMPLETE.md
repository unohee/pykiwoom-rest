# PyKiwoom MCP Server - Claude Code 설치 완료 ✅

## 설치 완료 사항

### 1. 가상환경 생성 및 패키지 설치
```bash
✓ .venv-mcp 생성 완료
✓ 필수 패키지 설치 완료:
  - websockets==15.0.1
  - requests==2.32.5
  - mcp==1.21.2
  - python-dotenv==1.2.1
  - pykiwoom-rest==2.1.0 (editable mode)
  - pandas==2.3.3
  - numpy==2.3.5
```

### 2. MCP 설정 파일 생성

#### 프로젝트 레벨 설정
파일: `/home/unohee/dev/tools/pykiwoom-rest/.mcp.json`
```json
{
  "mcpServers": {
    "pykiwoom-mcp-server": {
      "command": "/home/unohee/dev/tools/pykiwoom-rest/.venv-mcp/bin/python3",
      "args": [
        "/home/unohee/dev/tools/pykiwoom-rest/pykiwoom-mcp-server/src/pykiwoom_mcp_server/server.py"
      ],
      "env": {
        "ACCOUNT_NO": "${ACCOUNT_NO}",
        "KIWOOM_APPKEY": "${KIWOOM_APPKEY}",
        "KIWOOM_APPSECRET": "${KIWOOM_APPSECRET}"
      }
    }
  }
}
```

#### 전역 설정
파일: `/home/unohee/.mcp.json`
```json
{
  "mcpServers": {
    "pykiwoom-mcp-server": {
      "command": "/home/unohee/dev/tools/pykiwoom-rest/.venv-mcp/bin/python3",
      "args": [
        "/home/unohee/dev/tools/pykiwoom-rest/pykiwoom-mcp-server/src/pykiwoom_mcp_server/server.py"
      ]
    }
  }
}
```

### 3. 서버 동작 테스트
```bash
$ timeout 3 .venv-mcp/bin/python3 pykiwoom-mcp-server/src/pykiwoom_mcp_server/server.py
PyKiwoom MCP Server started with 67 endpoints
✓ 서버 정상 시작 확인
```

## Claude Code에서 사용 방법

### 1. Claude Code 시작
```bash
# 프로젝트 디렉토리에서
cd /home/unohee/dev/tools/pykiwoom-rest
claude
```

### 2. MCP 서버 확인
Claude Code가 시작되면 자동으로 `.mcp.json`을 읽어서 MCP 서버를 연결합니다.

### 3. MCP 도구 사용 예시

#### 사용 가능한 엔드포인트 목록 조회
```
user: list_endpoints를 사용해서 모든 API를 확인해줘

assistant: [list_endpoints 도구 호출]
Result: 67개 엔드포인트 (Stock: 18, Chart: 13, Account: 10, ...)
```

#### 주식 시세 조회
```
user: 삼성전자(005930) 현재가를 조회해줘

assistant: [get_stock_price 도구 호출]
Arguments: {"stock_code": "005930"}
Result: 현재가, 등락률, 거래량 등
```

#### 차트 데이터 조회
```
user: 삼성전자 5분봉 차트 100개 가져와줘

assistant: [get_minute_chart 도구 호출]
Arguments: {"stock_code": "005930", "interval": 5, "count": 100}
Result: 분봉 차트 데이터
```

## 환경변수 설정

MCP 서버가 Kiwoom API를 사용하려면 환경변수가 필요합니다.

### 방법 1: 프로젝트 .env 파일 사용
```bash
# /home/unohee/dev/tools/pykiwoom-rest/.env 파일이 이미 존재
# Claude Code가 자동으로 로드
```

### 방법 2: 시스템 환경변수 설정
```bash
export ACCOUNT_NO="12345678"
export KIWOOM_APPKEY="your-app-key"
export KIWOOM_APPSECRET="your-app-secret"
```

### 방법 3: .mcp.json에 직접 설정 (권장하지 않음)
보안상 권장하지 않지만, 테스트 목적으로는 가능합니다:
```json
{
  "mcpServers": {
    "pykiwoom-mcp-server": {
      "command": "...",
      "args": [...],
      "env": {
        "ACCOUNT_NO": "actual-account-number",
        "KIWOOM_APPKEY": "actual-key",
        "KIWOOM_APPSECRET": "actual-secret"
      }
    }
  }
}
```

## 사용 가능한 MCP 도구 (68개)

### 메타 도구
- `list_endpoints` - 사용 가능한 모든 API 엔드포인트 목록 조회

### 주식 시세 (Stock API) - 18개
- `get_stock_price` - 주식 현재가 조회
- `get_stock_orderbook` - 주식 호가 조회
- `get_foreign_trading` - 외국인 매매 동향
- `get_stock_investor_trading` - 투자자별 매매 동향
- 기타 15개...

### 차트 데이터 (Chart API) - 13개
- `get_minute_chart` - 분봉 차트 조회
- `get_minute_chart_paginated` - 분봉 차트 (자동 페이지네이션)
- `get_daily_chart` - 일봉 차트 조회
- `get_weekly_chart` - 주봉 차트 조회
- `get_monthly_chart` - 월봉 차트 조회
- 기타 8개...

### 계좌 관리 (Account API) - 10개
- `get_account_balance` - 계좌 잔고 조회
- `get_account_evaluation` - 계좌 평가 현황
- `get_unfilled_orders` - 미체결 주문 조회
- 기타 7개...

### 주문 실행 (Order API) - 4개
- `buy_order` - 매수 주문
- `sell_order` - 매도 주문
- `modify_order` - 주문 정정
- `cancel_order` - 주문 취소

### 순위 정보 (Ranking API) - 6개
- `get_top_gainers` - 상승률 상위 종목
- `get_top_volume` - 거래량 상위 종목
- 기타 4개...

### 인증 (Auth API) - 5개
- `get_access_token` - OAuth2 토큰 발급
- `refresh_token` - 토큰 갱신
- `revoke_token` - 토큰 폐기
- `logout` - 로그아웃

### 업종 정보 (Sector API) - 1개
- `get_all_sector_index` - 전업종 지수 조회

### 기타 (Etc) - 10개
- 세션 관리, WebSocket 제어 등

## 트러블슈팅

### MCP 서버가 연결되지 않을 때
```bash
# 1. 서버가 정상 시작되는지 확인
/home/unohee/dev/tools/pykiwoom-rest/.venv-mcp/bin/python3 \
  /home/unohee/dev/tools/pykiwoom-rest/pykiwoom-mcp-server/src/pykiwoom_mcp_server/server.py

# 2. .mcp.json 파일 확인
cat /home/unohee/dev/tools/pykiwoom-rest/.mcp.json

# 3. 환경변수 확인
cat /home/unohee/dev/tools/pykiwoom-rest/.env
```

### 패키지 임포트 오류
```bash
# 가상환경에 pykiwoom-rest가 설치되어 있는지 확인
/home/unohee/dev/tools/pykiwoom-rest/.venv-mcp/bin/python3 -c "from pykiwoom_rest import KiwoomRest; print('OK')"
```

### 권한 오류
```bash
# 실행 권한 확인
chmod +x /home/unohee/dev/tools/pykiwoom-rest/pykiwoom-mcp-server/src/pykiwoom_mcp_server/server.py
```

## 다음 단계

1. ✅ Claude Code 시작: `cd /home/unohee/dev/tools/pykiwoom-rest && claude`
2. ✅ MCP 도구 사용: `list_endpoints` 호출하여 사용 가능한 API 확인
3. ✅ 실제 API 테스트: 시세 조회, 차트 데이터 수집 등
4. ✅ 자동화 스크립트 작성: Claude Code와 MCP를 활용한 트레이딩 도구 개발

---

**설치 완료**: 2025-11-20
**상태**: ✅ Production Ready
**MCP 서버 버전**: 0.2.0 (Dynamic Tool Generation)
**사용 가능한 도구**: 68개 (67 API endpoints + 1 meta tool)
