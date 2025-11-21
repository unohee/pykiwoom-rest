# PyKiwoom MCP Server - Project Structure

## Directory Structure

```
pykiwoom-mcp-server/
├── src/
│   └── pykiwoom_mcp_server/
│       ├── __init__.py              # 패키지 초기화
│       └── server.py                # MCP 서버 메인 코드
│
├── pyproject.toml                   # 프로젝트 설정 및 의존성
├── README.md                        # 사용자 문서
├── STRUCTURE.md                     # 이 파일 (프로젝트 구조)
│
├── .env.example                     # 환경 변수 템플릿
├── .gitignore                       # Git 제외 파일
├── claude_desktop_config.example.json  # Claude Desktop 설정 예제
│
└── test_server.py                   # 테스트 스크립트
```

## Key Files

### `src/pykiwoom_mcp_server/server.py`
- MCP 서버 핵심 구현
- 11개의 도구(tools) 정의:
  - 시세 조회: `get_stock_price`, `get_stock_orderbook`
  - 차트 데이터: `get_daily_chart`, `get_minute_chart`, `get_minute_chart_paginated`
  - 계좌: `get_account_balance`
  - 외국인 매매: `get_foreign_trading`
  - 순위: `get_top_gainers`, `get_top_volume`
  - 주문: `buy_order`, `sell_order`

### `pyproject.toml`
- 프로젝트 메타데이터 및 의존성
- MCP SDK (mcp>=0.9.0)
- pykiwoom-rest (>=2.2.0)
- Ruff, Pytest 설정

### `test_server.py`
- MCP 서버 기능 테스트
- 3가지 핵심 테스트:
  1. 주식 현재가 조회
  2. 호가 조회
  3. 상승률 상위 종목 조회

## Installation

```bash
# 개발 모드로 설치
pip install -e .

# 의존성만 설치
pip install -r pyproject.toml
```

## Usage

```bash
# 직접 실행
python src/pykiwoom_mcp_server/server.py

# 설치 후 커맨드 사용
pykiwoom-mcp-server

# 테스트 실행
python test_server.py
```

## Configuration

### Environment Variables (Required)
- `ACCOUNT_NO`: 계좌번호
- `KIWOOM_APPKEY`: API 키
- `KIWOOM_APPSECRET`: API 시크릿

### Optional Environment Variables
- `KIWOOM_APPKEY_1`, `KIWOOM_APPSECRET_1`: 추가 크레덴셜 (Rate Limit 최적화)

## Development

### Code Style
- Ruff: Line length 100, Python 3.10+
- Type hints 사용 권장

### Testing
```bash
# 테스트 실행
pytest tests/ -v

# 커버리지 포함
pytest tests/ --cov=pykiwoom_mcp_server
```

### Formatting
```bash
# 포맷팅
ruff format src/

# 린팅
ruff check src/ --fix
```

## Architecture

### MCP Server Flow
```
Claude Desktop (Client)
    ↓ stdio
PyKiwoom MCP Server (server.py)
    ↓ Python API
pykiwoom-rest Library
    ↓ HTTP REST
Kiwoom Securities API
```

### Component Interaction
1. **Client Request**: Claude Desktop이 도구 호출 요청
2. **MCP Protocol**: stdio를 통한 JSON-RPC 통신
3. **Server Handler**: `call_tool()` 핸들러가 요청 처리
4. **API Call**: `KiwoomRest` 인스턴스를 통해 API 호출
5. **Response**: JSON 형식으로 결과 반환

## Security

- stdio 통신만 사용 (네트워크 노출 없음)
- 환경 변수로 민감 정보 관리
- .env 파일은 .gitignore에 포함

## Troubleshooting

### "pykiwoom_rest 패키지를 찾을 수 없습니다"
```bash
cd .. && pip install -e .
```

### "MCP 서버 연결 실패"
- Python 버전 확인 (3.10+)
- mcp 패키지 설치 확인
- 환경 변수 설정 확인

### "토큰 발급 실패"
- API 키 유효성 확인
- 네트워크 연결 확인
- 키움증권 API 신청 상태 확인
