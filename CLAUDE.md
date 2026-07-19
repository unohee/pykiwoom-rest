# 저장소 작업 안내

이 문서는 PyKiwoom-REST 저장소를 수정하는 개발 도구와 기여자를 위한 프로젝트별 안내입니다.

## 프로젝트 개요

PyKiwoom-REST는 키움증권 REST API를 Python 라이브러리, CLI, MCP 서버로 제공하는 비공식
래퍼입니다. 공개 Python 진입점은 `KiwoomRest`, CLI는 `kiwoom`, MCP 서버는
`kiwoom-mcp`입니다.

## 구조

```text
src/pykiwoom_rest/
├── kiwoom_rest.py          # 공개 파사드
├── kiwoom_base.py          # 인증·HTTP 요청 공통 계층
├── auth_api.py             # OAuth2
├── stock_api.py            # 종목 시세
├── chart_api.py            # 차트와 페이지네이션
├── account_api.py          # 계좌 조회
├── order_api.py            # 주문
├── ranking_api.py          # 순위
├── sector_api.py           # 업종
├── response_utils.py       # 응답 정규화
├── rate_limit_optimizer.py # 요청 속도 제한
├── cli/                    # kiwoom CLI
└── mcp_server.py           # kiwoom-mcp 서버
```

`KiwoomRest`는 기능별 API 클래스를 조합한 단일 공개 파사드입니다. 메서드를 변경할 때는 파사드,
기능별 구현, CLI/MCP 호출 경계, 테스트를 함께 확인합니다.

## 개발 환경

프로젝트 전용 환경이 없으면 이 컴퓨터의 MLX 환경을 사용합니다.

```bash
source ~/dev/mlx_env/bin/activate
python --version
pip install -e '.[mcp]'
```

인증 정보는 `.env` 또는 환경 변수로 전달합니다.

```bash
ACCOUNT_NO=your-account-number
KIWOOM_APPKEY=your-app-key
KIWOOM_APPSECRET=your-app-secret
```

비밀값을 코드, 테스트 픽스처, 문서, 로그에 넣지 않습니다.

## 검사 명령

```bash
# 전체 단위 테스트
pytest -q

# CLI와 MCP 집중 테스트
pytest -q tests/test_cli_main.py tests/test_cli_schema.py tests/test_mcp_server.py

# 정적 검사
ruff check src tests pykiwoom-mcp-server/src
black --check src tests pykiwoom-mcp-server/src
mypy src/pykiwoom_rest --ignore-missing-imports

# 패치 무결성
git diff --check
```

실제 API를 호출하는 통합 테스트는 인증 정보, 네트워크, 거래 시간에 의존하므로 기본 테스트와
구분합니다. 단위 테스트가 통과했다는 이유만으로 실제 계좌 동작을 검증했다고 보고하지 않습니다.

## CLI 계약

- 기본 출력은 JSON입니다.
- `--pretty`, `--raw`, `--format` 전역 옵션을 유지합니다.
- `query`는 읽기 전용 메서드만 허용합니다.
- 수량과 조회 개수는 명령 실행 전에 검증합니다.
- 매수·매도·정정·취소는 기본적으로 대화형 확인을 요구합니다.
- 자동화의 `--yes`는 사용자 승인을 대신하지 않습니다.

CLI 명령 또는 출력 구조를 바꾸면 `schema` 출력과 관련 테스트·README를 함께 갱신합니다.

## MCP 계약

- MCP 로직의 기준 구현은 `src/pykiwoom_rest/mcp_server.py`입니다.
- `pykiwoom-mcp-server` 하위 패키지는 기존 실행 명령을 위한 호환 래퍼입니다.
- 목록 조회는 인증 정보와 API 클라이언트 생성 없이 동작해야 합니다.
- 동기 REST 호출은 작업 스레드에서 실행합니다.
- 읽기 도구와 변경성 도구의 MCP 힌트를 정확히 지정합니다.
- 주문·토큰 변경 도구는 `confirm=true`를 필수로 요구합니다.
- 콜백 기반 실시간 구독은 stdio 도구로 노출하지 않습니다.
- MCP 안정 1.x 범위를 사용하며 2.x 전환은 별도 호환성 작업으로 처리합니다.

MCP 변경 시 단위 테스트뿐 아니라 실제 `ClientSession`과 `stdio_client`를 사용한 왕복 검증도
실행합니다.

## API 구현 규칙

- 키움 공식 명세의 TR 코드, 엔드포인트, 요청 키, 응답 키를 확인합니다.
- 시장 데이터나 브로커 동작을 추측하지 않습니다.
- 연속 조회는 `cont-yn`과 `next-key`를 보존합니다.
- 공개 날짜 범위와 개수 제한을 메서드 내부에서 일관되게 적용합니다.
- 429, 인증 만료, 빈 응답을 서로 다른 경로로 처리합니다.
- 예외를 조용히 삼키거나 성공 형태의 빈 가짜 데이터를 반환하지 않습니다.

## 주문 안전

실제 주문, 정정, 취소, 토큰 폐기는 명시적 사용자 승인이 필요합니다. 개발 검증은 모의투자를
우선하고, 자동 테스트에서 실제 주문을 실행하지 않습니다. 주문 인자 변경 시 호출자와 CLI/MCP
안전 게이트를 모두 검사합니다.

## 문서

설명 문장은 한국어를 기본으로 사용하고 코드 식별자, 명령, API 이름, 오류 원문은 원형을
유지합니다. 동작을 변경하면 최소한 다음 문서를 확인합니다.

- `README.md`
- `docs/API.md`
- `CHANGELOG.md`
- CLI 또는 MCP 관련 문서

자동 추출 API 레퍼런스의 필드명은 번역하지 않습니다. 필드 설명과 문서 레이블만 한국어로
표기합니다.

## Git과 리뷰

- 사용자 변경이 있는 작업 트리를 되돌리지 않습니다.
- 의미 있는 변경은 기본 브랜치가 아닌 작업 브랜치에서 커밋합니다.
- 커밋에 AI 공동 작성자 표기를 넣지 않습니다.
- PR 전 관련 테스트와 `git diff --check`를 실행합니다.
- OpenSwarm을 사용할 수 있으면 `openswarm review --path .`를 리뷰 게이트로 사용하고 차단
  지적을 해결합니다.
