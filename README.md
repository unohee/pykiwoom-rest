# PyKiwoom-REST

키움증권 REST API를 Python, CLI, MCP에서 일관되게 사용할 수 있는 비공식 래퍼입니다.

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://img.shields.io/pypi/v/pykiwoom-rest.svg)](https://pypi.org/project/pykiwoom-rest/)

## 주요 기능

- 국내주식 시세, 차트, 투자자, 순위, 업종, 계좌, 주문 API
- OAuth2 토큰 발급·갱신과 자동 재인증
- 연속 조회와 대량 차트 페이지네이션
- 비동기·병렬 조회와 요청 속도 제한 최적화
- 사람이 사용하기 쉬운 `kiwoom` CLI와 에이전트용 JSON 출력
- MCP 호환 클라이언트에서 사용할 수 있는 `kiwoom-mcp` stdio 서버

## 설치

Python 라이브러리와 CLI는 Python 3.8 이상에서 동작합니다.

```bash
pip install pykiwoom-rest
```

MCP 서버까지 설치하려면 Python 3.10 이상에서 추가 의존성을 설치합니다.

```bash
pip install 'pykiwoom-rest[mcp]'
```

기본 설치에서 `kiwoom-mcp`를 실행하면 필요한 MCP 추가 기능의 설치 명령을 안내합니다.

저장소에서 개발 버전을 설치하는 방법은 다음과 같습니다.

```bash
git clone https://github.com/unohee/pykiwoom-rest.git
cd pykiwoom-rest
pip install -e '.[mcp]'
```

## 인증 설정

프로젝트 디렉터리에 `.env`를 만들거나 같은 이름의 환경 변수를 설정합니다.

```bash
KIWOOM_APPKEY=your-app-key
KIWOOM_APPSECRET=your-app-secret
ACCOUNT_NO=your-account-number
```

라이브러리를 다른 서비스에 포함할 때는 생성자에 인증 정보를 직접 전달할 수도 있습니다.

```python
from pykiwoom_rest import KiwoomRest

kiwoom = KiwoomRest(
    account_no="your-account-number",
    appkey="your-app-key",
    appsecret="your-app-secret",
)
```

환경 변수와 직접 전달을 함께 사용하면 직접 전달한 값이 우선합니다.

## Python 사용법

```python
from pykiwoom_rest import KiwoomRest

kiwoom = KiwoomRest()

# 삼성전자 현재가
price = kiwoom.get_stock_price("005930")

# 5분봉 100개
chart = kiwoom.get_minute_chart(
    stock_code="005930",
    interval=5,
    count=100,
)

# 계좌 평가 잔고
balance = kiwoom.get_account_evaluation()
```

여러 종목을 병렬로 조회할 때는 `ConcurrentKiwoomRest`, 비동기 코드에서는
`AsyncKiwoomRest`를 사용할 수 있습니다. 세부 메서드와 응답 형식은
[API 안내](docs/API.md)와 [키움 API 레퍼런스](docs/KIWOOM_API_REFERENCE.md)를 참고하세요.

## CLI 사용법

설치 후 `kiwoom` 명령을 사용할 수 있습니다. 기본 출력은 에이전트가 처리하기 쉬운 JSON이며,
`--pretty`, `--format table`, `--raw` 옵션을 지원합니다.

```bash
# 사용 가능한 명령과 스키마
kiwoom --help
kiwoom schema
kiwoom schema price

# 현재가와 호가
kiwoom price 005930 --orderbook --pretty

# 일봉과 5분봉
kiwoom chart 005930 --count 30
kiwoom chart 005930 --minute --interval 5 --count 100

# 순위, 업종, 투자자 동향
kiwoom rank volume --market ALL
kiwoom sector --all
kiwoom investor 005930 --institution

# 계좌 조회
kiwoom account balance --pretty
kiwoom account orders

# 연결 및 토큰 상태
kiwoom status
kiwoom token
```

라이브러리의 읽기 전용 메서드는 `query`로 호출할 수 있습니다. 변경성 메서드는 차단됩니다.

```bash
kiwoom query get_stock_financial --params '{"stock_code":"005930"}'
```

### 주문 안전장치

매수·매도·정정·취소는 실제 계좌를 변경합니다. CLI는 기본적으로 대화형 확인을 요구하며,
자동화에서 `--yes`를 사용할 때도 호출자가 사용자 승인을 먼저 받아야 합니다.

```bash
# 확인 프롬프트를 거쳐 1주 매수
kiwoom order buy 005930 --qty 1 --price 70000

# 주문 취소
kiwoom order cancel 005930 --order-no 123456 --qty 1
```

## MCP 서버 사용법

`kiwoom-mcp`는 stdio 전송을 사용하는 MCP 서버입니다. 공개 API 메서드에서 도구 스키마를
자동 생성하며 `list_endpoints` 도구로 카테고리별 목록을 조회할 수 있습니다.

```bash
kiwoom-mcp
```

MCP 클라이언트 설정 예시는 다음과 같습니다.

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

읽기 도구는 `readOnlyHint=true`로 표시됩니다. 주문과 토큰 폐기처럼 상태를 변경하는 도구는
`destructiveHint=true`로 표시되며, 사용자의 명시적 승인을 받은 호출만 `confirm=true`를
전달해 실행할 수 있습니다. 실시간 콜백 구독처럼 stdio 요청/응답에 맞지 않는 메서드는
도구에서 제외됩니다.

MCP 응답은 다음 공통 구조를 사용합니다.

```json
{
  "ok": true,
  "tool": "get_stock_price",
  "data": {}
}
```

별도 호환 패키지와 상세 설정은 [MCP 서버 안내](pykiwoom-mcp-server/README.md)를 참고하세요.

## 오류 처리와 속도 제한

- HTTP 429 응답은 지수 백오프로 재시도합니다.
- 인증 토큰은 만료 전에 갱신합니다.
- 연속 조회가 필요한 API는 다음 키를 보존해 페이지를 이어 받습니다.
- 운영 환경에서는 키움증권의 최신 호출 제한과 거래 시간 정책을 직접 확인해야 합니다.

## 테스트와 품질 검사

```bash
pytest
ruff check src tests
black --check src tests
mypy src
```

실제 계좌를 사용하는 통합 테스트는 기본 테스트에서 제외됩니다. 인증 정보가 없는 환경에서도
CLI 스키마와 MCP 프로토콜 목록 조회는 검증할 수 있습니다.

## 문서

- [API 개요](docs/API.md)
- [키움 API 레퍼런스](docs/KIWOOM_API_REFERENCE.md)
- [업종·차트 API](docs/SECTOR_CHART_API.md)
- [응답 키 매핑](docs/api_response_key_mapping.md)
- [API 분야별 안내](api/README.md)
- [예제](examples/README.md)
- [변경 기록](CHANGELOG.md)
- [MCP 문제 해결](MCP_TROUBLESHOOTING.md)

## 보안

- `.env`, API 키, 계좌번호, 접근 토큰을 버전 관리에 포함하지 마세요.
- 운영 환경에서는 시크릿 관리 시스템을 사용하세요.
- MCP 클라이언트가 주문 도구를 호출하기 전에 반드시 사용자 승인을 받도록 구성하세요.
- 모의투자에서 검증하지 않은 주문 코드를 실제 계좌에 사용하지 마세요.

## 라이선스와 면책

MIT 라이선스로 배포됩니다. 이 프로젝트는 키움증권과 제휴하거나 키움증권이 보증하는 공식
SDK가 아닙니다. 시장 데이터와 주문 결과를 직접 검증해야 하며, 사용에 따른 투자·운영 책임은
사용자에게 있습니다.

문제 제보와 기여는 [GitHub Issues](https://github.com/unohee/pykiwoom-rest/issues)와 Pull Request로 받습니다.
