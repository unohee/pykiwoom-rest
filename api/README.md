# Kiwoom REST API 문서

Kiwoom증권 REST API 명세서를 LLM이 쉽게 접근할 수 있도록 구조화한 문서입니다.

## 📚 API 문서 구조

총 180개의 API를 카테고리별로 분류하여 문서화했습니다.

### 🔐 [01. 인증 (OAuth)](./01_authentication.md)
- 접근토큰 발급 및 폐기
- OAuth2 인증 프로세스

### 📊 [02. 종목정보](./02_stock_info.md)
- 30개 API
- 종목 기본정보, 거래원, 신용매매, 공매도 등

### 💹 [03. 시세](./03_market_data.md)
- 20개 API
- 호가, 체결, 시분봉, 기관매매 동향

### 📈 [04. 차트](./04_chart.md)
- 14개 API
- 틱/분/일/주/월/년 차트 데이터

### 🏆 [05. 순위정보](./05_ranking.md)
- 23개 API
- 거래량, 거래대금, 등락률 순위

### 💼 [06. 계좌 및 주문](./06_account_order.md)
- 33개 API (계좌 25개, 주문 8개)
- 잔고조회, 주문실행, 정정/취소

### ⚡ [07. 실시간시세](./07_realtime.md)
- 18개 WebSocket API
- 실시간 체결, 호가, 주문 알림

### 🎯 [08. ETF/ELW](./08_etf_elw.md)
- 20개 API (ETF 9개, ELW 11개)
- ETF NAV, ELW 민감도 지표

### 🏢 [09. 업종/테마](./09_sector_theme.md)
- 8개 API
- 업종지수, 업종차트, 테마그룹

### 🔍 [10. 특수거래](./10_special.md)
- 12개 API
- 기관/외국인, 공매도, 대차거래, 조건검색

## 🗂️ API 엔드포인트 분류

| 엔드포인트 | API 수 | 주요 기능 |
|-----------|--------|----------|
| `/api/dostk/stkinfo` | 30 | 종목정보 |
| `/api/dostk/acnt` | 25 | 계좌관련 |
| `/api/dostk/rkinfo` | 23 | 순위정보 |
| `/api/dostk/websocket` | 22 | 실시간시세 |
| `/api/dostk/mrkcond` | 20 | 시세조회 |
| `/api/dostk/chart` | 14 | 차트데이터 |
| `/api/dostk/elw` | 11 | ELW |
| `/api/dostk/etf` | 9 | ETF |
| `/api/dostk/sect` | 6 | 업종 |
| `/api/dostk/ordr` | 4 | 일반주문 |
| `/api/dostk/crdordr` | 4 | 신용주문 |
| `/api/dostk/slb` | 4 | 대차거래 |
| `/api/dostk/frgnistt` | 3 | 외국인/기관 |
| `/api/dostk/thme` | 2 | 테마 |
| `/oauth2/*` | 2 | 인증 |
| `/api/dostk/shsa` | 1 | 공매도 |

## 🔧 사용 방법

1. **인증**: OAuth2 토큰 발급 (24시간 유효)
2. **API 호출**: Bearer Token을 헤더에 포함
3. **응답 처리**: JSON 형식의 응답 파싱

## 📋 공통 요구사항

- **인증**: 모든 API는 Bearer Token 필수 (인증 API 제외)
- **메서드**: 대부분 POST 메서드 사용
- **호출 제한**: 초당 20회 제한
- **Content-Type**: `application/json`

## 🚀 주요 API 예시

```python
# 1. 토큰 발급
POST /oauth2/token
Content-Type: application/x-www-form-urlencoded

# 2. 주식 기본정보 조회
POST /api/dostk/stkinfo
Authorization: Bearer {access_token}
{
  "tr_id": "ka10001",
  "stock_code": "005930"
}

# 3. 분봉 차트 조회
POST /api/dostk/chart
Authorization: Bearer {access_token}
{
  "tr_id": "ka10080",
  "stock_code": "005930",
  "interval": 5,
  "start_date": "20250101"
}
```

## 📝 참고사항

- 일부 API는 장시간(09:00~15:30)에만 정상 작동
- 대량 데이터 조회 시 페이지네이션 지원
- WebSocket은 실시간 데이터 스트리밍용
- 각 문서에서 상세 파라미터 및 응답 형식 확인 가능

## 🔗 관련 리소스

- [PyKiwoom-REST GitHub](https://github.com/your-repo/pykiwoom-rest)
- [Kiwoom Open API 공식 문서](https://apiportal.koreainvestment.com)