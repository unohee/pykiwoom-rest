# PyKiwoom MCP 서버

키움증권 REST API를 MCP 도구로 제공하는 stdio 서버입니다. 실제 구현은 메인 패키지의
`pykiwoom_rest.mcp_server`에 있으며, 이 디렉터리는 기존 `pykiwoom-mcp-server` 설치 방식과
실행 명령을 유지하는 호환 패키지입니다.

## 동작 방식

- `KiwoomRest`의 호출 가능한 공개 메서드를 시작 시 분석합니다.
- 타입 힌트와 기본값으로 각 도구의 JSON Schema를 만듭니다.
- `list_endpoints`로 전체 도구 또는 카테고리별 도구를 조회할 수 있습니다.
- API 클라이언트는 실제 API 도구를 처음 호출할 때 생성됩니다.
- 동기 REST 호출은 작업 스레드에서 실행되어 MCP 이벤트 루프를 막지 않습니다.
- 날짜, 모델, DataFrame 계열 결과도 JSON으로 직렬화합니다.

실시간 콜백 구독, 연결 종료, 내부 속도 제한 초기화처럼 stdio 요청/응답 모델에 맞지 않는
메서드는 자동 도구에서 제외됩니다.

## 요구 사항

- Python 3.10 이상
- `pykiwoom-rest` 2.2.0 이상
- 안정 MCP Python SDK 1.x (`mcp>=1.27,<2`)

MCP Python SDK 2.x가 정식 출시되기 전까지 예기치 않은 호환성 변경을 막기 위해 상한을 둡니다.

## 설치

메인 패키지의 추가 의존성으로 설치하는 방법을 권장합니다.

```bash
pip install 'pykiwoom-rest[mcp]'
```

저장소 개발 버전은 다음과 같이 설치합니다.

```bash
git clone https://github.com/unohee/pykiwoom-rest.git
cd pykiwoom-rest
pip install -e '.[mcp]'
```

기존 호환 패키지만 별도로 설치할 수도 있습니다.

```bash
cd pykiwoom-mcp-server
pip install -e .
```

## 인증 정보

MCP 클라이언트의 서버 환경 변수에 다음 값을 전달합니다.

```bash
ACCOUNT_NO=your-account-number
KIWOOM_APPKEY=your-app-key
KIWOOM_APPSECRET=your-app-secret
```

실제 API 호출 전까지 클라이언트를 만들지 않으므로, 인증 정보 없이도 서버 초기화와
`list_tools`, `list_endpoints`를 검사할 수 있습니다.

## 실행

```bash
# 메인 패키지 명령
kiwoom-mcp

# 기존 호환 명령
pykiwoom-mcp-server
```

두 명령은 같은 서버 구현을 실행합니다. 로그는 `stderr`, MCP 프로토콜 메시지는 `stdio`로
분리되므로 서버 실행 중 `stdout`에 임의 메시지를 출력하면 안 됩니다.

## MCP 클라이언트 설정

```json
{
  "mcpServers": {
    "pykiwoom": {
      "command": "kiwoom-mcp",
      "env": {
        "ACCOUNT_NO": "your-account-number",
        "KIWOOM_APPKEY": "your-app-key",
        "KIWOOM_APPSECRET": "your-app-secret"
      }
    }
  }
}
```

가상환경에 설치했다면 `command`에 해당 가상환경의 `kiwoom-mcp` 절대 경로를 지정하세요.

## 도구 카테고리

- `stock`: 종목 시세, 호가, 투자자·프로그램 동향
- `chart`: 틱·분·일·주·월·년 차트
- `account`: 잔고, 평가, 예수금, 체결·미체결
- `order`: 매수, 매도, 정정, 취소
- `ranking`: 거래량, 거래대금, 등락률 등 순위
- `sector`: 업종 시세와 차트
- `auth`: 토큰 상태, 갱신, 폐기
- `etc`: 연결 확인과 기타 읽기 API

`list_endpoints`의 `category`에 위 값을 전달하거나 `all`로 전체를 조회합니다.

## 주문과 인증 안전장치

다음 도구는 계좌 또는 인증 상태를 변경하므로 `destructiveHint=true`로 표시됩니다.

- `buy_stock`
- `sell_stock`
- `modify_order`
- `cancel_order`
- `refresh_token`
- `revoke_token`
- `logout`

호출자가 사용자 승인을 받은 뒤 `confirm: true`를 명시해야 실행됩니다. 누락하거나 `false`를
전달하면 API 클라이언트 생성 전에 요청을 거부합니다. 이 플래그는 보조 안전장치이며,
MCP 호스트도 변경성 도구 실행 전에 사용자 확인을 받아야 합니다.

## 응답 형식

성공 응답:

```json
{
  "ok": true,
  "tool": "get_stock_price",
  "data": {}
}
```

실패 응답:

```json
{
  "ok": false,
  "tool": "get_stock_price",
  "error": "오류 메시지",
  "errorType": "예외 클래스"
}
```

## 검증

```bash
pytest -q tests/test_mcp_server.py
pytest -q pykiwoom-mcp-server/tests
ruff check src/pykiwoom_rest/mcp_server.py pykiwoom-mcp-server/src
```

실제 API 통합 테스트는 인증 정보가 있을 때만 실행합니다. stdio 연결, 도구 목록, 스키마,
`list_endpoints`는 네트워크와 계좌 없이 검증할 수 있습니다.

## 문제 해결

연결이 되지 않으면 다음 순서로 확인하세요.

1. `kiwoom-mcp`가 터미널에서 실행되는지 확인합니다.
2. MCP 호스트가 사용하는 Python과 설치한 가상환경이 같은지 확인합니다.
3. 설정 파일의 `command`를 절대 경로로 바꿉니다.
4. 서버의 `stderr` 로그를 확인합니다.
5. 실제 API 호출만 실패하면 인증 환경 변수와 키움 API 권한을 확인합니다.

추가 사례는 [MCP 문제 해결](../MCP_TROUBLESHOOTING.md)을 참고하세요.
