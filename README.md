# PyKiwoom-Rest

Kiwoom증권 REST API를 위한 Python Wrapper 라이브러리

## 📌 주요 기능

- 🔐 **자동 인증**: 환경변수에서 자동으로 인증 정보 로드
- 📊 **시세 조회**: 실시간 시세, 호가, 체결 정보 조회
- 📈 **차트 데이터**: 분/일/주/월/년봉 차트 데이터 조회
- 🔄 **페이지네이션**: 대량 데이터 조회를 위한 자동 페이지네이션
- 🏢 **기관/외국인**: 기관 및 외국인 매매 동향 분석
- 💹 **프로그램매매**: 프로그램매매 추이 및 상위 종목

## 🚀 빠른 시작

### 설치

```bash
# 의존성 설치
pip install -r requirements.txt
```

### 환경 설정

`.env` 파일에 Kiwoom API 인증 정보를 설정하세요:

```env
ACCOUNT_NO=계좌번호
KIWOOM_APPKEY=앱키
KIWOOM_APPSECRET=앱시크릿
```

### 기본 사용법

```python
from kiwoom_rest import KiwoomRest

# 인스턴스 생성 (환경변수에서 자동 로드)
kiwoom = KiwoomRest()

# 주식 현재가 조회
stock_info = kiwoom.get_stock_price("005930")  # 삼성전자
print(f"현재가: {stock_info['output']['stck_prpr']}원")

# 분봉 데이터 조회
minute_data = kiwoom.get_minute_chart(
    stock_code="005930",
    interval=5,  # 5분봉
    start_date="20250101",
    end_date="20250115"
)
```

## 💡 주요 사용 예제

### 1. 분봉 데이터 페이지네이션

원하는 기간의 모든 분봉 데이터를 자동으로 수집합니다:

```python
# 최근 30일간 1분봉 데이터 모두 수집
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=30)

# 페이지네이션으로 전체 데이터 수집
all_minute_data = kiwoom.get_minute_chart_paginated(
    stock_code="005930",
    interval=1,  # 1분봉
    start_date=start_date.strftime("%Y%m%d"),
    end_date=end_date.strftime("%Y%m%d"),
    max_records=1000  # 최대 1000개 수집
)

print(f"수집된 분봉 개수: {len(all_minute_data)}")
```

### 2. 호가 정보 조회

```python
# 실시간 호가 조회
orderbook = kiwoom.get_stock_orderbook("005930")

# 매도호가 상위 5개
for i in range(1, 6):
    price = orderbook['output1'][f'askp{i}']
    volume = orderbook['output1'][f'askp_rsqn{i}']
    print(f"매도 {i}차: {price}원 / {volume}주")
```

### 3. 기관/외국인 매매 동향

```python
# 최근 30일 기관매매 동향
institutional = kiwoom.get_institutional_daily_trading(
    stock_code="005930",
    start_date="20241215",
    end_date="20250115"
)

for day in institutional['output'][:5]:
    print(f"{day['stck_bsop_date']}: 기관 {day['inst_ntby_qty']}주")
```

### 4. 차트 데이터 조회

```python
# 일봉 차트
daily_chart = kiwoom.get_daily_chart(
    stock_code="005930",
    start_date="20250101",
    end_date="20250115"
)

# 주봉 차트
weekly_chart = kiwoom.get_weekly_chart(
    stock_code="005930",
    start_date="20240101",
    end_date="20250115"
)

# 월봉 차트
monthly_chart = kiwoom.get_monthly_chart(
    stock_code="005930",
    start_date="20240101",
    end_date="20250115"
)
```

### 5. 순위 정보 조회

```python
# 거래량 상위 종목
volume_top = kiwoom.get_volume_top(market="ALL")

# 외국인 순매수 상위
foreign_top = kiwoom.get_foreign_top_buy(period="1")

# 프로그램 순매수 상위
program_top = kiwoom.get_program_top_buy()
```

## 📚 API 메서드 목록

### 시세 조회
- `get_stock_price()` - 주식 기본정보 및 현재가
- `get_stock_orderbook()` - 호가 정보
- `get_execution_info()` - 체결 정보
- `get_daily_price()` - 일별 주가
- `get_daily_trading_detail()` - 일별 거래 상세

### 차트 데이터
- `get_tick_chart()` - 틱 차트
- `get_minute_chart()` - 분봉 차트 (1, 3, 5, 10, 15, 30, 60분)
- `get_minute_chart_paginated()` - 분봉 차트 페이지네이션
- `get_daily_chart()` - 일봉 차트
- `get_weekly_chart()` - 주봉 차트
- `get_monthly_chart()` - 월봉 차트
- `get_yearly_chart()` - 년봉 차트

### 기관/외국인
- `get_foreign_trading()` - 외국인 종목별 매매동향
- `get_institutional_daily_trading()` - 일별 기관매매
- `get_institutional_trading_trend()` - 종목별 기관매매 추이

### 프로그램매매
- `get_program_top_buy()` - 프로그램 순매수 상위 50
- `get_program_trading_daily()` - 종목일별 프로그램매매 추이

### 순위 정보
- `get_volume_top()` - 호가잔량 상위
- `get_foreign_top_buy()` - 외인 기간별 매매 상위

전체 API 목록은 [API.md](API.md) 파일을 참조하세요.

## 🧪 테스트

```bash
# 기본 테스트 실행
python test_kiwoom.py

# 사용 예제 실행
python example.py
```

## 📂 프로젝트 구조

```
pykiwoom-rest/
├── kiwoom_rest.py      # 메인 API wrapper 클래스
├── test_kiwoom.py      # 테스트 코드
├── example.py          # 사용 예제
├── requirements.txt    # 의존성 패키지
├── .env               # 환경 설정 (API 키)
├── kiwoom.xlsx        # API 엔드포인트 정보
├── API.md             # API 엔드포인트 문서
└── README.md          # 이 파일
```

## ⚠️ 주의사항

1. **API 키 보안**: `.env` 파일을 절대 공개 저장소에 업로드하지 마세요
2. **Rate Limit**: API 호출 제한을 준수하세요 (초당 20회)
3. **거래 시간**: 일부 API는 장 시간에만 정상 작동합니다
4. **인증 토큰**: 토큰은 자동 갱신되지만, 24시간마다 재발급됩니다

## 📋 요구사항

- Python 3.7+
- Kiwoom증권 REST API 계정
- 필수 패키지:
  - requests
  - python-dotenv
  - pandas
  - openpyxl

## 🔧 환경 변수

| 변수명 | 설명 | 예시 |
|--------|------|------|
| `ACCOUNT_NO` | Kiwoom 계좌번호 | 12345678 |
| `KIWOOM_APPKEY` | API 앱키 | your-app-key |
| `KIWOOM_APPSECRET` | API 앱시크릿 | your-app-secret |

## 📝 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 🤝 기여

버그 리포트, 기능 제안, Pull Request 모두 환영합니다!

## 📞 문의

문제가 발생하거나 질문이 있으시면 이슈를 등록해주세요.

---

**작성일**: 2025-01-15  
**버전**: 1.0.0