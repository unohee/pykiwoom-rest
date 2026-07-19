# MCP 서버 요약

PyKiwoom MCP 서버는 키움 REST API를 에이전트가 호출할 수 있는 구조화된 도구로 제공합니다.

## 핵심 계약

1. 도구 목록 조회는 인증 정보 없이 동작합니다.
2. 실제 API 클라이언트는 첫 API 도구 호출까지 생성하지 않습니다.
3. 읽기 도구는 `readOnlyHint=true`로 표시합니다.
4. 계좌·인증 상태 변경 도구는 `destructiveHint=true`와 `confirm=true`를 요구합니다.
5. 실시간 콜백처럼 stdio 요청/응답에 맞지 않는 메서드는 노출하지 않습니다.
6. 모든 결과는 `ok`, `tool`, `data` 또는 오류 정보를 담은 JSON으로 반환합니다.

## 빠른 시작

```bash
pip install 'pykiwoom-rest[mcp]'
kiwoom-mcp
```

설정 예시와 도구 분류는 [MCP 서버 안내](pykiwoom-mcp-server/README.md), 연결 문제는
[MCP 문제 해결](MCP_TROUBLESHOOTING.md)을 참고하세요.
