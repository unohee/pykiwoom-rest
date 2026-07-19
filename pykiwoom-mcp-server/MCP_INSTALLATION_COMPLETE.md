# MCP 설치 확인표

파일 이름은 기존 링크 호환성을 위해 유지합니다. 특정 컴퓨터에서 설치가 끝났다는 기록이 아니라,
새 환경에서 설치 상태를 재현하고 확인하는 절차입니다.

## 설치

```bash
python --version
pip install -e '.[mcp]'
command -v kiwoom-mcp
```

Python 3.10 이상이어야 하며 `kiwoom-mcp`가 현재 가상환경 안에서 발견되어야 합니다.

## 서버 초기화 확인

```bash
kiwoom-mcp
```

서버는 stdio 입력을 기다리므로 일반 터미널에서는 멈춘 것처럼 보이는 것이 정상입니다.
시작 메시지는 `stderr`에만 기록됩니다. 종료는 `Ctrl-C`를 사용합니다.

## 자동 검증

```bash
pytest -q tests/test_mcp_server.py
pytest -q pykiwoom-mcp-server/tests/test_mcp_protocol.py
```

검증 항목:

- MCP 초기화 성공
- 도구 목록과 `list_endpoints` 조회 성공
- 읽기/변경성 힌트 생성
- 콜백 기반 메서드 제외
- 주문 도구의 `confirm=true` 강제
- 목록 조회 중 API 클라이언트를 생성하지 않음

## 호스트 설정 확인

```json
{
  "mcpServers": {
    "pykiwoom": {
      "command": "/absolute/path/to/venv/bin/kiwoom-mcp",
      "env": {
        "ACCOUNT_NO": "your-account-number",
        "KIWOOM_APPKEY": "your-app-key",
        "KIWOOM_APPSECRET": "your-app-secret"
      }
    }
  }
}
```

설정을 바꾼 뒤 MCP 호스트를 완전히 재시작하고 도구 목록에서 `list_endpoints`를 확인합니다.
