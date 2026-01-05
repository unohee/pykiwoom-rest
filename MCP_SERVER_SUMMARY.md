# PyKiwoom MCP Server 설치 완료 ✅

## 설치 완료 사항

### 1. 가상환경 및 패키지
- ✅ 가상환경: `/home/unohee/dev/tools/pykiwoom-rest/.venv-mcp`
- ✅ 패키지: mcp, websockets, requests, pykiwoom-rest (editable)

### 2. MCP 설정 파일
- ✅ 프로젝트: `.mcp.json` (환경변수 포함)
- ✅ 전역: `~/.mcp.json` (환경변수 포함)

### 3. 서버 동작 확인
- ✅ 67개 엔드포인트 정상 시작
- ✅ MCP JSON-RPC 프로토콜 응답 정상

## 🚀 Claude Code에서 사용하기

### 현재 세션에서는 MCP 서버가 표시되지 않는 이유:
Claude Code는 **시작할 때** `.mcp.json` 파일을 읽습니다.
현재 세션은 `.mcp.json` 생성 **이전에** 시작되었기 때문에 MCP 서버를 인식하지 못합니다.

### 해결 방법: Claude Code 재시작

```bash
# 1. 현재 Claude Code 세션 종료
exit (또는 Ctrl+D)

# 2. Claude Code 재시작
cd /home/unohee/dev/tools/pykiwoom-rest
claude
```

### 재시작 후 확인:
Claude Code가 시작되면 자동으로 MCP 서버가 연결됩니다.

## 📊 사용 가능한 MCP 도구 (68개)

### 메타 도구
- `list_endpoints` - 모든 API 엔드포인트 목록 조회

### 주요 API 카테고리
- **Stock (18개)**: get_stock_price, get_stock_orderbook, get_foreign_trading...
- **Chart (13개)**: get_minute_chart, get_daily_chart, get_weekly_chart...
- **Account (10개)**: get_account_balance, get_account_evaluation...
- **Order (4개)**: buy_order, sell_order, modify_order, cancel_order
- **Ranking (6개)**: get_top_gainers, get_top_volume...
- **Auth (5개)**: get_access_token, refresh_token, logout...
- **Sector (1개)**: get_all_sector_index
- **Etc (10개)**: 세션 관리, WebSocket 제어 등

## 🔧 MCP 서버 설정 내용

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

## 💡 사용 예시 (재시작 후)

### 1. 엔드포인트 목록 확인
```
user: list_endpoints로 사용 가능한 API 확인해줘

assistant: [list_endpoints 도구 호출]
Result: 67개 엔드포인트 (Stock: 18, Chart: 13, ...)
```

### 2. 주식 시세 조회
```
user: 삼성전자(005930) 현재가 조회해줘

assistant: [get_stock_price 도구 호출]
Arguments: {"stock_code": "005930"}
Result: 현재가, 등락률, 거래량 등
```

### 3. 차트 데이터 조회
```
user: 삼성전자 5분봉 차트 100개 가져와줘

assistant: [get_minute_chart 도구 호출]
Arguments: {"stock_code": "005930", "interval": 5, "count": 100}
Result: 분봉 차트 데이터
```

## 🔍 트러블슈팅

### MCP 서버가 목록에 없을 때
```bash
# 1. .mcp.json 파일 확인
cat /home/unohee/dev/tools/pykiwoom-rest/.mcp.json

# 2. 서버 수동 실행 테스트
/home/unohee/dev/tools/pykiwoom-rest/.venv-mcp/bin/python3 \
  /home/unohee/dev/tools/pykiwoom-rest/pykiwoom-mcp-server/src/pykiwoom_mcp_server/server.py

# 3. Claude Code 재시작 (필수!)
exit && claude
```

### 패키지 임포트 오류
```bash
# 가상환경에서 테스트
/home/unohee/dev/tools/pykiwoom-rest/.venv-mcp/bin/python3 -c \
  "from pykiwoom_rest import KiwoomRest; print('OK')"
```

## 📝 다음 단계

1. **Claude Code 재시작** ← 가장 중요!
2. MCP 도구 목록에서 `pykiwoom-mcp-server` 확인
3. `list_endpoints` 도구로 사용 가능한 API 확인
4. 실제 API 테스트 (시세 조회, 차트 데이터 등)

---

**설치 완료 시간**: 2025-11-20
**MCP 서버 버전**: 0.2.0 (Dynamic Tool Generation)
**총 도구 개수**: 68개 (67 API + 1 meta)
**상태**: ✅ Production Ready

**재시작 필수!** Claude Code를 재시작해야 MCP 서버가 인식됩니다.
