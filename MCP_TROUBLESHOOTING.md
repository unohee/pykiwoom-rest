# MCP 서버가 도구 목록에 표시되지 않는 문제 해결

## ✅ 확인 완료 사항

### 1. MCP 서버 정상 작동
```bash
$ python3 test_mcp_simple.py
✓ 초기화 성공: pykiwoom-mcp-server
✓ 총 68개 도구 발견
```

### 2. .mcp.json 설정 정상
```json
{
  "mcpServers": {
    "pykiwoom-mcp-server": {
      "command": ".venv-mcp/bin/python3",
      "args": ["pykiwoom-mcp-server/src/pykiwoom_mcp_server/server.py"],
      "env": { ... }
    }
  }
}
```

### 3. 가상환경 및 패키지 정상
```bash
$ .venv-mcp/bin/python3 -c "from pykiwoom_rest import KiwoomRest; print('OK')"
✓ Import OK
```

## ❌ 문제 원인

**Claude Code는 시작할 때만 `.mcp.json`을 읽습니다.**

현재 상황:
1. Claude Code 세션 시작 (`.mcp.json` 없음)
2. `.mcp.json` 파일 생성
3. Claude Code가 인식하지 못함 ← **여기가 문제**

## 🔧 해결 방법

### 방법 1: Claude Code 재시작 (권장)

```bash
# 현재 세션 종료
exit

# 프로젝트 디렉토리에서 재시작
cd /home/unohee/dev/tools/pykiwoom-rest
claude
```

**재시작 후 자동으로 MCP 서버가 연결됩니다.**

### 방법 2: 새 터미널에서 Claude Code 시작

```bash
# 새 터미널 열기
cd /home/unohee/dev/tools/pykiwoom-rest
claude
```

### 방법 3: MCP 서버를 직접 Python으로 사용

`.mcp.json` 없이도 MCP 서버를 직접 사용할 수 있습니다:

```python
from pykiwoom_rest import KiwoomRest

# 직접 API 사용
kiwoom = KiwoomRest()
price = kiwoom.get_stock_price("005930")
print(price)
```

## 📊 MCP 서버 사용 가능한 도구 (68개)

재시작 후 사용 가능한 도구들:

1. **list_endpoints** - 모든 API 목록 조회
2. **get_stock_price** - 주식 시세 조회
3. **get_minute_chart** - 분봉 차트
4. **get_daily_chart** - 일봉 차트
5. **get_account_balance** - 계좌 잔고
6. **buy_order** / **sell_order** - 매수/매도
7. **get_top_gainers** - 상승률 상위 종목
... 총 68개

## 🔍 재시작 후 확인 방법

재시작하면 Claude Code가 다음과 같이 표시합니다:

```
Connected to MCP servers:
  - pykiwoom-mcp-server (68 tools)
```

그 후 다음 명령어로 테스트:

```
user: list_endpoints 도구를 사용해서 Stock 카테고리 API를 보여줘

assistant: [mcp__pykiwoom-mcp-server__list_endpoints 호출]
```

## ⚠️ 주의사항

- `.mcp.json` 파일은 Claude Code 시작 시점에만 읽힘
- 설정 변경 후에는 반드시 재시작 필요
- 현재 세션에서는 MCP 서버를 인식할 수 없음

---

**결론**: Claude Code를 재시작하면 모든 것이 정상 작동합니다! 🚀
