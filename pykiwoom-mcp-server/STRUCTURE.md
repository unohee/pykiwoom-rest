# MCP 서버 구조

## 단일 구현 원칙

MCP 로직의 기준 구현은 `src/pykiwoom_rest/mcp_server.py` 하나입니다. 별도 패키지는 과거 설치
경로와 `pykiwoom-mcp-server` 명령을 유지하는 얇은 래퍼만 제공합니다. 두 구현이 서로 달라지는
문제를 막기 위한 구조입니다.

```text
pykiwoom-rest/
├── src/pykiwoom_rest/
│   ├── mcp_cli.py                    # 선택 의존성 확인 진입점
│   ├── mcp_server.py                 # MCP 기준 구현
│   ├── cli/                          # kiwoom CLI
│   └── kiwoom_rest.py                # 통합 REST 클라이언트
├── tests/test_mcp_server.py          # 레지스트리·안전 게이트 단위 테스트
└── pykiwoom-mcp-server/
    ├── pyproject.toml                # 기존 독립 패키지 메타데이터
    ├── src/pykiwoom_mcp_server/
    │   └── server.py                 # 기준 구현을 호출하는 호환 래퍼
    └── tests/                        # stdio 프로토콜 회귀 테스트
```

## 요청 흐름

```text
MCP 호스트
  → stdio 초기화
  → list_tools
  → 도구 호출
  → 변경성 도구 확인 게이트
  → KiwoomRest 지연 생성
  → 작업 스레드에서 REST 호출
  → 공통 JSON 응답
```

`list_tools`와 `list_endpoints`는 인증 정보나 네트워크 연결이 없어도 동작합니다. 실제 REST 도구를
처음 호출할 때만 `KiwoomRest`를 생성합니다.

## 레지스트리

서버 시작 시 다음 정보를 수집합니다.

- 메서드 이름과 설명 첫 줄
- Python 타입 힌트와 기본값
- 필수 인자
- 문서 문자열의 TR 코드
- 카테고리
- 읽기 전용 또는 변경성 여부

콜백 인자를 요구하거나 서버 수명 주기를 직접 변경하는 메서드는 제외 목록으로 관리합니다.
주문과 인증 상태 변경 메서드는 변경성 목록으로 관리하고 `confirm` 필수 인자를 추가합니다.

## 의존성 정책

메인 라이브러리는 Python 3.8 이상을 유지합니다. MCP 추가 기능은 Python 3.10 이상에서만 설치되며,
현재 안정 계열인 MCP Python SDK 1.x에 고정합니다.
