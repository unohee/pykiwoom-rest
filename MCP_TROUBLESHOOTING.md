# MCP 서버 문제 해결

## 서버 명령을 찾을 수 없음

```bash
command -v kiwoom-mcp
python -m pip show pykiwoom-rest
```

MCP 호스트가 실행되는 환경과 패키지를 설치한 가상환경이 다르면 명령을 찾지 못합니다. 호스트
설정의 `command`에 가상환경 안의 실행 파일 절대 경로를 지정하세요.

## `mcp` 모듈을 찾을 수 없음

MCP 추가 의존성을 설치합니다. Python 3.10 이상이 필요합니다.

```bash
python --version
python -m pip install -e '.[mcp]'
```

## 서버가 실행 직후 종료됨

터미널에서 실행해 `stderr` 오류를 확인합니다.

```bash
kiwoom-mcp
```

일반적인 원인은 잘못된 Python 경로, 누락된 `mcp` 패키지, 저장소 개발 설치 경로 오류입니다.
`stdout`은 MCP 프로토콜 전용이므로 진단 출력은 반드시 `stderr`로 보내야 합니다.

## 도구 목록은 보이지만 API 호출이 실패함

`list_tools`와 `list_endpoints`는 인증 없이 동작합니다. 실제 조회에서만 실패한다면 다음 환경
변수와 키움 API 권한을 확인하세요.

```bash
ACCOUNT_NO=your-account-number
KIWOOM_APPKEY=your-app-key
KIWOOM_APPSECRET=your-app-secret
```

키움 API 운영·모의투자 도메인, 호출 가능 시간, 계좌 권한도 함께 확인해야 합니다. 비밀값은
로그나 이슈에 붙여 넣지 마세요.

## 주문 도구가 거부됨

주문·취소·정정과 토큰 변경 도구는 사용자 승인을 받은 호출만 실행합니다. MCP 호출 인자에
`confirm: true`를 명시해야 합니다.

```json
{
  "stock_code": "005930",
  "quantity": 1,
  "price": 70000,
  "confirm": true
}
```

승인 없이 이 값을 자동 추가하지 마세요. 먼저 모의투자에서 주문 인자와 결과를 검증하세요.

## stdio 연결을 재현하고 싶음

```bash
pytest -q pykiwoom-mcp-server/tests/test_mcp_protocol.py
```

이 테스트는 MCP 클라이언트로 서버를 시작해 초기화, 도구 목록, `list_endpoints` 호출을 왕복
검증합니다. 인증 정보가 없어도 기본 프로토콜 테스트는 통과해야 합니다.

## SDK 호환성 오류

현재 서버는 안정 MCP Python SDK 1.x를 대상으로 합니다.

```bash
python -m pip install 'mcp>=1.27,<2'
```

2.x 사전 공개 버전은 API가 달라질 수 있으므로 같은 환경에 섞지 않습니다.
