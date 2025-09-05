# PyKiwoom REST API Documentation

## 📚 Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Features](#core-features)
- [API Reference](#api-reference)
- [Advanced Features](#advanced-features)
- [Examples](#examples)

## 🎯 Overview

PyKiwoom-REST는 한국투자증권(키움증권) OpenAPI REST 서비스를 위한 고성능 Python 라이브러리입니다.

### Key Features
- ✅ **완전한 REST API 지원**: 모든 주요 엔드포인트 구현
- ⚡ **고성능 처리**: 비동기/병렬 처리 지원
- 🔄 **자동 Rate Limiting**: 다중 크레덴셜 로테이션
- 📊 **타입 안정성**: 완전한 타입 힌팅
- 🛡️ **에러 처리**: 자동 재시도 및 복구

## 📦 Installation

```bash
pip install -r requirements.txt
```

### Requirements
- Python 3.10+
- 키움증권 REST API 계정

## 🚀 Quick Start

### 1. 환경 설정
```bash
# .env 파일 생성
KIWOOM_APPKEY=your-app-key
KIWOOM_APPSECRET=your-app-secret  
ACCOUNT_NO=your-account-number
```

### 2. 기본 사용법
```python
from pykiwoom_rest import KiwoomRest

# API 초기화
kiwoom = KiwoomRest()

# 주식 시세 조회
result = kiwoom.get_stock_price("005930")  # 삼성전자
print(f"현재가: {result.data['cur_prc']}")

# 분봉 차트 조회
chart_data = kiwoom.get_minute_chart("005930", interval=5)
```

## 🔧 Core Features

### 1. 모듈화된 API 구조
```python
from pykiwoom_rest import KiwoomRest

kiwoom = KiwoomRest()

# 각 도메인별 API 접근
kiwoom.stock_api    # 주식 정보
kiwoom.chart_api    # 차트 데이터
kiwoom.account_api  # 계좌 관리
kiwoom.order_api    # 주문 실행
kiwoom.ranking_api  # 순위/통계
kiwoom.sector_api   # 업종 정보
```

### 2. APIResponse 객체
```python
result = kiwoom.get_stock_price("005930")

# APIResponse 속성
result.success      # 성공 여부
result.data        # 응답 데이터
result.error       # 에러 정보
result.metadata    # 메타데이터

# Dict처럼 사용 가능
if result['stk_cd']:
    print(result['stk_nm'])
```

### 3. Rate Limiting 최적화
```python
# 자동 rate limiting
kiwoom = KiwoomRest(
    rate_limit=20,      # 초당 최대 요청
    max_retries=3,      # 자동 재시도
    enable_rate_optimizer=True  # 고급 최적화
)
```

## 📖 API Reference

### Stock API (주식 정보)
```python
# 주식 기본 정보
kiwoom.get_stock_price("005930")

# 호가 정보
kiwoom.get_stock_orderbook("005930")

# 체결 정보
kiwoom.get_execution_info("005930")

# 외국인 매매 동향
kiwoom.get_foreign_trading("005930")

# 프로그램 매매
kiwoom.get_program_trading_daily("005930")
```

### Chart API (차트 데이터)
```python
# 분봉 차트
kiwoom.get_minute_chart(
    stock_code="005930",
    interval=5,  # 5분봉
    count=100
)

# 특정 날짜 분봉
kiwoom.get_minute_chart_with_date(
    stock_code="005930",
    target_date="20250103"
)

# 일봉/주봉/월봉
kiwoom.get_daily_chart("005930", period="D")  # D/W/M
kiwoom.get_weekly_chart("005930")
kiwoom.get_monthly_chart("005930")

# 페이지네이션 지원
kiwoom.get_minute_chart_paginated(
    stock_code="005930",
    start_date="20250101",
    end_date="20250131",
    max_records=1000
)
```

### Account API (계좌 관리)
```python
# 계좌 잔고 조회
balance = kiwoom.get_account_balance()

# 보유 종목 조회
positions = kiwoom.get_stock_positions()

# 매수 가능 금액
buying_power = kiwoom.get_buying_power()

# 일별 손익
daily_pnl = kiwoom.get_daily_pnl()
```

### Order API (주문 실행)
```python
# 매수 주문
result = kiwoom.buy_order(
    stock_code="005930",
    quantity=10,
    price=70000,
    order_type="00"  # 지정가
)

# 매도 주문
result = kiwoom.sell_order(
    stock_code="005930",
    quantity=10,
    price=75000
)

# 주문 취소
kiwoom.cancel_order(order_no="123456")

# 주문 내역 조회
orders = kiwoom.get_order_history()
```

### Ranking API (순위/통계)
```python
# 거래량 순위
kiwoom.get_volume_ranking(market="ALL")

# 시가총액 순위  
kiwoom.get_market_cap_ranking()

# 등락률 순위
kiwoom.get_price_change_ranking()

# 외국인 순매수 순위
kiwoom.get_foreign_net_buy_ranking()
```

### Sector API (업종 정보)
```python
# 업종 지수
kiwoom.get_sector_index("001")  # KOSPI

# 업종별 종목
kiwoom.get_sector_stocks("001")

# 업종 차트
kiwoom.get_sector_chart("001")
```

## 🚀 Advanced Features

### 1. 비동기 처리
```python
from pykiwoom_rest.async_api import AsyncKiwoomAPI
import asyncio

async def fetch_multiple():
    async with AsyncKiwoomAPI() as api:
        # 동시에 여러 종목 조회
        codes = ["005930", "000660", "035720"]
        results = await api.get_multiple_stock_prices(codes)
        
        for code, result in zip(codes, results):
            print(f"{code}: {result.data['stk_nm']}")

# 실행
asyncio.run(fetch_multiple())
```

### 2. 병렬 처리
```python
from pykiwoom_rest.concurrent_api import ParallelKiwoomAPI

# 스레드 풀 병렬 처리
client = ParallelKiwoomAPI(max_workers=5)

# 병렬로 여러 종목 조회
codes = ["005930", "000660", "035720", "005380", "051910"]
results = client.get_stock_prices_parallel(codes)

for code, result in results.items():
    if result:
        print(f"{code}: 조회 성공")

client.shutdown()
```

### 3. 자동 최적화 모드
```python
from pykiwoom_rest.concurrent_api import OptimizedBatchProcessor

processor = OptimizedBatchProcessor()

# 자동으로 최적 처리 모드 선택
codes = ["005930", "000660", "035720", "005380", "051910"]
result = processor.auto_process(codes)

print(f"처리 시간: {result.total_time:.2f}초")
print(f"처리량: {result.throughput:.2f} req/s")
```

### 4. Rate Limiting 고급 설정
```python
# 다중 크레덴셜 로테이션
credentials = [
    {'APPKEY': 'key1', 'APPSECRET': 'secret1'},
    {'APPKEY': 'key2', 'APPSECRET': 'secret2'},
]

kiwoom = KiwoomRest(
    enable_rate_optimizer=True,
    credentials_list=credentials
)

# 자동으로 크레덴셜 로테이션하여 Rate Limit 회피
```

### 5. 실시간 스트리밍 (Polling)
```python
async def stream_prices():
    async with AsyncKiwoomAPI() as api:
        async def callback(code, result):
            print(f"[{code}] {result.data['cur_prc']}")
        
        # 실시간 가격 스트리밍
        await api.stream_stock_prices(
            ["005930", "000660"],
            interval=1.0,
            callback=callback
        )
```

## 📊 Examples

### Example 1: 포트폴리오 분석
```python
def analyze_portfolio():
    kiwoom = KiwoomRest()
    
    # 보유 종목 조회
    positions = kiwoom.get_stock_positions()
    
    total_value = 0
    for position in positions['output']:
        code = position['pdno']
        qty = int(position['hldg_qty'])
        
        # 현재가 조회
        price_info = kiwoom.get_stock_price(code)
        current_price = int(price_info.data['cur_prc'])
        
        value = qty * current_price
        total_value += value
        
        print(f"{code}: {qty}주 × {current_price:,}원 = {value:,}원")
    
    print(f"총 평가액: {total_value:,}원")
```

### Example 2: 기술적 분석
```python
import pandas as pd

def technical_analysis(stock_code):
    kiwoom = KiwoomRest()
    
    # 일봉 데이터 조회
    chart = kiwoom.get_daily_chart(stock_code, count=60)
    
    # DataFrame 변환
    df = pd.DataFrame(chart['output2'])
    df['stck_clpr'] = df['stck_clpr'].astype(float)
    
    # 이동평균 계산
    df['MA20'] = df['stck_clpr'].rolling(window=20).mean()
    df['MA60'] = df['stck_clpr'].rolling(window=60).mean()
    
    # 골든크로스/데드크로스 체크
    latest = df.iloc[-1]
    if latest['MA20'] > latest['MA60']:
        print(f"{stock_code}: 골든크로스 신호")
    else:
        print(f"{stock_code}: 데드크로스 신호")
```

### Example 3: 자동 매매 시스템
```python
class AutoTrader:
    def __init__(self):
        self.kiwoom = KiwoomRest()
        self.target_stocks = ["005930", "000660", "035720"]
    
    def check_buy_signal(self, stock_code):
        # RSI, MACD 등 기술적 지표 체크
        chart = self.kiwoom.get_minute_chart(stock_code, interval=5)
        # ... 매수 신호 로직 ...
        return True  # 예시
    
    def execute_buy(self, stock_code, quantity):
        # 현재가 조회
        price_info = self.kiwoom.get_stock_price(stock_code)
        current_price = int(price_info.data['cur_prc'])
        
        # 매수 주문
        result = self.kiwoom.buy_order(
            stock_code=stock_code,
            quantity=quantity,
            price=current_price,
            order_type="01"  # 시장가
        )
        
        if result.success:
            print(f"매수 주문 성공: {stock_code} {quantity}주")
        return result
    
    def run(self):
        for code in self.target_stocks:
            if self.check_buy_signal(code):
                self.execute_buy(code, 10)
```

## 🔍 Error Handling

### 에러 타입
```python
from pykiwoom_rest.base_api import APIError, RateLimitExceeded

try:
    result = kiwoom.get_stock_price("005930")
except RateLimitExceeded:
    print("Rate limit 초과 - 잠시 대기")
except APIError as e:
    print(f"API 에러: {e.status_code} - {e.response}")
```

### 자동 재시도
```python
# 자동 재시도 설정
kiwoom = KiwoomRest(
    max_retries=3,
    backoff_factor=1.0  # 지수 백오프
)
```

## 🧪 Testing

```bash
# 단위 테스트
pytest tests/

# 통합 테스트
python tests/test_integration.py

# 성능 테스트
python test_concurrent_performance.py
```

## 📈 Performance

- **순차 처리**: ~50 req/s
- **병렬 처리 (5 workers)**: ~25 req/s
- **비동기 처리**: ~70 req/s
- **Rate Limit**: 20 req/s (키움 API 제한)

## 🔒 Security

- API 키는 환경변수에 저장
- 토큰 자동 갱신 (24시간)
- 민감정보 로깅 방지

## 📝 License

MIT License

## 🤝 Contributing

Issues 및 Pull Requests 환영합니다.

## 📞 Support

- GitHub Issues: [Report Issues](https://github.com/yourusername/pykiwoom-rest/issues)
- Documentation: [Full Docs](https://docs.example.com)

---
*Last Updated: 2025-01-05*