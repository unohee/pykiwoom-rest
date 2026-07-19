# MCP 서버 검증 기준과 결과 기록

과거 환경의 성공 로그를 현재 상태처럼 보이지 않게 하기 위해, 이 문서는 재현 가능한 검증 명령과
판정 기준을 기록합니다. 최신 실행 결과는 PR 검사와 해당 커밋의 로컬 테스트 로그를 기준으로 합니다.

## 단위 테스트

```bash
pytest -q tests/test_mcp_server.py
```

다음을 검증합니다.

- 읽기 도구와 변경성 도구의 MCP 힌트
- 주문 도구의 명시적 확인 게이트
- `list_endpoints`의 무인증 동작
- 제외 메서드가 도구 목록에 나타나지 않음
- 공통 성공·실패 JSON 구조

## stdio 프로토콜 테스트

```bash
pytest -q pykiwoom-mcp-server/tests/test_mcp_protocol.py
```

MCP 클라이언트 세션을 실제로 열어 초기화, 도구 목록, 스키마, 메타 도구 호출을 확인합니다.
이 경로는 계좌 인증 정보 없이 실행할 수 있어야 합니다.

## 실제 API 테스트

```bash
ACCOUNT_NO=... \
KIWOOM_APPKEY=... \
KIWOOM_APPSECRET=... \
pytest -q pykiwoom-mcp-server/tests/test_mcp_protocol.py -k real
```

이 테스트는 유효한 키움 API 권한과 네트워크, 거래 시간 정책의 영향을 받습니다. 기본 CI에서는
실행하지 않으며, 실패를 단위 테스트 실패와 혼동하지 않습니다.

## 정적 검사

```bash
ruff check src/pykiwoom_rest/mcp_server.py tests/test_mcp_server.py \
  pykiwoom-mcp-server/src/pykiwoom_mcp_server/server.py
git diff --check
```

모든 명령이 종료 코드 0을 반환하고 stdio 왕복 테스트가 도구 목록을 읽어야 배포 가능한 상태로
판정합니다.
