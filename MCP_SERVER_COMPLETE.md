# MCP 서버 구현 현황

파일 이름은 기존 외부 링크를 보존하기 위해 유지합니다. 현재 MCP 서버의 기준 구현과 완료 조건은
다음과 같습니다.

## 제공 항목

- 메인 패키지 실행 명령: `kiwoom-mcp`
- 기존 호환 실행 명령: `pykiwoom-mcp-server`
- stdio 전송과 MCP Python SDK 1.x
- `KiwoomRest` 공개 메서드 기반 동적 도구 스키마
- `list_endpoints` 카테고리 검색
- 읽기 전용·변경성 도구 힌트
- 주문과 인증 변경 도구의 `confirm=true` 안전 게이트
- 무인증 초기화·목록 조회
- stdio 프로토콜 및 단위 테스트

## 기준 파일

- 선택 의존성 진입점: `src/pykiwoom_rest/mcp_cli.py`
- 구현: `src/pykiwoom_rest/mcp_server.py`
- 호환 래퍼: `pykiwoom-mcp-server/src/pykiwoom_mcp_server/server.py`
- 단위 테스트: `tests/test_mcp_server.py`
- 프로토콜 테스트: `pykiwoom-mcp-server/tests/test_mcp_protocol.py`
- 사용법: `pykiwoom-mcp-server/README.md`

## 완료 판정

문서의 “완료” 표현만으로 상태를 판단하지 않습니다. 다음 명령의 현재 실행 결과와 PR 검사를
근거로 판정합니다.

```bash
pytest -q tests/test_mcp_server.py
pytest -q pykiwoom-mcp-server/tests/test_mcp_protocol.py
ruff check src tests pykiwoom-mcp-server/src
git diff --check
```

실제 계좌 조회는 유효한 인증 정보가 있는 별도 통합 환경에서 확인합니다. 주문 실행은 자동
검증에 포함하지 않습니다.
