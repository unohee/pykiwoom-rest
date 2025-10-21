# PyKiwoom-REST API 구현 로드맵

> **생성일**: 2025-10-21
> **현황**: 132개 메서드 구현 / 206개 API 중 (64.1%)
> **미구현**: 약 74개 API

## 📊 전체 현황

| 카테고리 | 구현 | 미구현 | 우선순위 |
|---------|------|--------|---------|
| Stock API | 19 | 7 | ⭐⭐⭐ |
| Chart API | 8 | 2 | ⭐⭐⭐ |
| Account API | 22 | 10 | ⭐⭐⭐ |
| Order API | 10 | 6 | ⭐⭐⭐ |
| Ranking API | 25 | 0 | ✅ |
| Sector API | 12 | 0 | ✅ |
| ELW API | 0 | 12 | ⭐ |
| ETF API | 0 | 9 | ⭐ |
| Commodity API | 0 | 19 | ⭐ |
| Auth API | 0 | 2 | ⭐⭐⭐ |
| Other APIs | 36 | 28 | ⭐ |

**합계**: 132개 / 206개 (64.1%)

---

## 🎯 Phase 1: 핵심 API 완성 (우선순위 ⭐⭐⭐)

### Task 1-1: 인증 API 구현
**중요도**: 🔴 CRITICAL

```markdown
- [ ] au10001: 접근토큰 발급 (OAuth Token Issuance)
  - 엔드포인트: POST /oauth2/token
  - 목적: OAuth2 인증
  - 예상 난이도: ⭐ (낮음)
  - 예상 시간: 1-2시간

- [ ] au10002: 접근토큰 폐기 (OAuth Token Revocation)
  - 엔드포인트: POST /oauth2/revoke
  - 목적: 토큰 무효화
  - 예상 난이도: ⭐ (낮음)
  - 예상 시간: 30분-1시간
```

**구현 위치**: `src/pykiwoom_rest/auth_api.py` (신규 생성)

---

### Task 1-2: Stock API 추가 메서드

```markdown
- [ ] ka10002: 주식거래원요청 (Stock Trading Member Info)
  - 메서드명: get_stock_traders()
  - 난이도: ⭐⭐ (중간)

- [ ] ka10003: 체결정보요청 (Execution Information)
  - 메서드명: get_execution_details()
  - 난이도: ⭐⭐ (중간)

- [ ] ka10005: 주식일주월시분요청 (Daily/Weekly/Monthly/Minute)
  - 메서드명: get_stock_time_data()
  - 난이도: ⭐ (낮음)

- [ ] ka10006: 주식시분요청 (Stock Minute Data)
  - 메서드명: get_minute_data() [중복확인 필요]
  - 난이도: ⭐ (낮음)

- [ ] ka10007: 시세표성정보요청 (Quote Trend Info)
  - 메서드명: get_quote_trend_info()
  - 난이도: ⭐⭐ (중간)

- [ ] ka10009: 주식기관요청 (Institutional Trading)
  - 메서드명: get_institutional_trading() [중복확인]
  - 난이도: ⭐⭐ (중간)

- [ ] ka10010: 업종프로그램요청 (Sector Program Trading)
  - 메서드명: get_sector_program_trading()
  - 난이도: ⭐⭐ (중간)
```

**구현 위치**: `src/pykiwoom_rest/stock_api.py` (확장)

---

### Task 1-3: Chart API 추가 메서드

```markdown
- [ ] ka10079: 주식틱차트조회요청 (Tick Chart)
  - 메서드명: get_tick_chart() [이미 구현되어 있는지 확인]
  - 난이도: ⭐ (낮음)

- [ ] ka10094: 주식년봉차트조회요청 (Yearly Chart)
  - 메서드명: get_yearly_chart() [이미 구현 확인됨]
  - 난이도: ⭐ (낮음)
```

**구현 위치**: `src/pykiwoom_rest/chart_api.py` (확장)

---

### Task 1-4: Account API 추가 메서드

```markdown
- [ ] kt00002: 일별추정예탁자산현황요청 (Daily Asset Status)
  - 메서드명: get_daily_asset_status()
  - 난이도: ⭐⭐ (중간)

- [ ] kt00003: 추정자산조회요청 (Estimated Asset)
  - 메서드명: get_estimated_asset() [이미 구현 확인]
  - 난이도: ⭐ (낮음)

- [ ] kt00007: 계좌별익일결제예정내역요청 (Next Day Settlement)
  - 메서드명: get_next_settlement() [중복 확인]
  - 난이도: ⭐⭐ (중간)

- [ ] kt00010: 주문인출가능금액요청 (Withdrawable Amount)
  - 메서드명: get_withdrawable_amount() [이미 구현됨]
  - 난이도: ⭐ (낮음)

- [ ] kt00011: 증거금율별주문가능수량조회요청 (Margin Rate Order Quantity)
  - 메서드명: get_orderable_quantity_by_margin() [이미 구현됨]
  - 난이도: ⭐⭐ (중간)

- [ ] kt00012: 신용보증금율별주문가능수량조회요청 (Credit Margin Rate)
  - 메서드명: get_orderable_quantity_by_credit() [이미 구현됨]
  - 난이도: ⭐⭐ (중간)

- [ ] kt00013: 증거금세부내역조회요청 (Margin Detail)
  - 메서드명: get_margin_detail() [이미 구현됨]
  - 난이도: ⭐⭐ (중간)

- [ ] kt00015: 위탁종합거래내역요청 (Comprehensive Trading History)
  - 메서드명: get_comprehensive_trading_history()
  - 난이도: ⭐⭐ (중간)

- [ ] kt00016: 일별계좌수익률상세현황요청 (Daily Account Return Detail)
  - 메서드명: get_daily_account_return_detail() [중복 확인]
  - 난이도: ⭐⭐ (중간)

- [ ] kt00017: 계좌별당일현황요청 (Today's Account Status)
  - 메서드명: get_today_account_status()
  - 난이도: ⭐ (낮음)
```

**구현 위치**: `src/pykiwoom_rest/account_api.py` (확장)

---

### Task 1-5: Order API 추가 메서드 (신용거래)

```markdown
- [ ] kt10006: 신용 매수주문 (Credit Buy Order)
  - 메서드명: buy_credit() [이미 구현됨]
  - 난이도: ⭐⭐ (중간)

- [ ] kt10007: 신용 매도주문 (Credit Sell Order)
  - 메서드명: sell_credit() [이미 구현됨]
  - 난이도: ⭐⭐ (중간)

- [ ] kt10008: 신용 정정주문 (Credit Modify Order)
  - 메서드명: modify_credit_order() [이미 구현됨]
  - 난이도: ⭐⭐ (중간)

- [ ] kt10009: 신용 취소주문 (Credit Cancel Order)
  - 메서드명: cancel_credit_order() [이미 구현됨]
  - 난이도: ⭐⭐ (중간)

- [ ] kt20016: 신용융자 가능종목요청 (Credit Loan Available Stocks)
  - 메서드명: get_credit_available_stocks() [이미 구현됨]
  - 난이도: ⭐⭐ (중간)

- [ ] kt20017: 신용융자 가능문의 (Credit Loan Available Check)
  - 메서드명: check_credit_available() [이미 구현됨]
  - 난이도: ⭐ (낮음)
```

**구현 위치**: `src/pykiwoom_rest/order_api.py` (확장)

---

## ⭐ Phase 2: 추가 API 구현 (우선순위 ⭐⭐)

### Task 2-1: ELW API (12개)

```markdown
- [ ] ka30001: ELW가격급등락요청
  - 파일: `src/pykiwoom_rest/elw_api.py` (신규)
  - 메서드 수: 12개
  - 예상 시간: 8-10시간
```

**구현할 메서드**:
- get_elw_price_fluctuation
- get_elw_network_trading_top
- get_elw_lp_possession_trend
- get_elw_divergence_rate
- get_elw_condition_search
- get_elw_sensitivity_indicator
- get_elw_daily_sensitivity
- get_elw_range_approximation
- get_elw_remaining_volume_ranking
- get_elw_product_info
- get_elw_leverage_volatility
- get_elw_index_gap_rate

---

### Task 2-2: ETF API (9개)

```markdown
- [ ] ka40001: ETF수익율요청
  - 파일: `src/pykiwoom_rest/etf_api.py` (신규)
  - 메서드 수: 9개
  - 예상 시간: 6-8시간
```

**구현할 메서드**:
- get_etf_return_rate
- get_etf_stock_info
- get_etf_daily_trend
- get_etf_all_quote
- get_etf_hourly_trend
- get_etf_hourly_execution
- get_etf_daily_execution
- get_etf_nav
- get_etf_composition

---

### Task 2-3: 금현물 API (19개)

```markdown
- [ ] ka50010: 금현물체결추이
  - 파일: `src/pykiwoom_rest/commodity_api.py` (신규)
  - 메서드 수: 19개
  - 예상 시간: 12-15시간
```

**구현할 메서드**:
- get_commodity_execution_trend
- get_commodity_daily_trend
- get_commodity_tick_chart
- get_commodity_minute_chart
- get_commodity_daily_chart
- get_commodity_weekly_chart
- get_commodity_monthly_chart
- get_commodity_expected_execution
- get_commodity_today_tick_chart
- get_commodity_today_minute_chart
- get_commodity_current_price
- get_commodity_orderbook
- get_commodity_investor_status
- buy_commodity
- sell_commodity
- modify_commodity_order
- cancel_commodity_order
- get_commodity_execution_status
- get_commodity_trading_history

---

## 🔧 Phase 3: 기타 API (우선순위 ⭐)

### Task 3-1: 조건검색 API (4개)

```markdown
- [ ] ka10171: 조건검색 목록조회
- [ ] ka10172: 조건검색 요청 일반
- [ ] ka10173: 조건검색 요청 실시간
- [ ] ka10174: 조건검색 실시간 해제

파일: `src/pykiwoom_rest/screener_api.py` (신규)
예상 시간: 4-6시간
```

---

### Task 3-2: 기타 거래 API (10개+)

```markdown
다양한 카테고리의 API들:
- 대차거래 관련 (4개)
- 테마 관련 (2개)
- 프로그램 매매 추가 (5개)
- 실시간 시세 관련 (3개)

파일: `src/pykiwoom_rest/advanced_api.py` (신규)
예상 시간: 10-15시간
```

---

## 📋 구현 체크리스트

### Phase 1 (Core APIs)

#### 인증 API
- [ ] auth_api.py 파일 생성
- [ ] au10001 구현 (토큰 발급)
- [ ] au10002 구현 (토큰 폐기)
- [ ] 테스트 작성
- [ ] CI/CD 통과

#### Stock API 확장
- [ ] ka10002 구현
- [ ] ka10003 구현
- [ ] ka10005 구현
- [ ] ka10006 구현
- [ ] ka10007 구현
- [ ] ka10009 구현
- [ ] ka10010 구현
- [ ] 통합 테스트
- [ ] 문서 업데이트

#### Chart API 확장
- [ ] ka10079 확인/구현
- [ ] ka10094 확인/구현
- [ ] 페이지네이션 테스트

#### Account API 확장
- [ ] 나머지 메서드 10개 구현
- [ ] 테스트 커버리지 확인
- [ ] Rate Limit 테스트

#### Order API 확장
- [ ] 신용거래 메서드 6개 구현
- [ ] 거래 검증 로직
- [ ] 에러 처리 강화

---

### Phase 2 (Additional APIs)

- [ ] ELW API 구현 (12개)
- [ ] ETF API 구현 (9개)
- [ ] Commodity API 구현 (19개)

---

### Phase 3 (Others)

- [ ] 조건검색 API (4개)
- [ ] 기타 거래 API (10개+)

---

## 📊 예상 일정

| Phase | 항목 | 예상 시간 | 우선순위 |
|-------|------|---------|---------|
| 1 | 인증 API | 2-3시간 | 🔴 CRITICAL |
| 1 | Stock API 확장 | 4-6시간 | 🔴 CRITICAL |
| 1 | Chart API 확장 | 1-2시간 | 🔴 CRITICAL |
| 1 | Account API 확장 | 6-8시간 | 🟠 HIGH |
| 1 | Order API 확장 | 4-6시간 | 🟠 HIGH |
| **Phase 1 소계** | | **17-25시간** | |
| 2 | ELW API | 8-10시간 | 🟡 MEDIUM |
| 2 | ETF API | 6-8시간 | 🟡 MEDIUM |
| 2 | Commodity API | 12-15시간 | 🟡 MEDIUM |
| **Phase 2 소계** | | **26-33시간** | |
| 3 | 조건검색 & 기타 | 14-21시간 | 🔵 LOW |
| **Total** | | **57-79시간** | |

---

## 🛠️ 구현 전략

### 1. 코드 구조
```
src/pykiwoom_rest/
├── auth_api.py (신규)          # 인증 API
├── commodity_api.py (신규)     # 금현물 API
├── elw_api.py (신규)           # ELW API
├── etf_api.py (신규)           # ETF API
├── screener_api.py (신규)      # 조건검색 API
└── advanced_api.py (신규)      # 기타 고급 API
```

### 2. 테스트 방식
- 각 API마다 unit test 작성
- 통합 테스트 (pytest)
- Rate limit 검증
- Mock 환경에서 테스트

### 3. 문서화
- API 메서드 docstring 작성
- README.md 업데이트
- KIWOOM_API_SPECIFICATION.md 반영
- 사용 예제 작성

---

## ✅ 완료 기준

1. **코드**
   - [ ] 모든 메서드 구현
   - [ ] 타입 힌팅 100%
   - [ ] 에러 처리 완벽
   - [ ] Rate Limit 고려

2. **테스트**
   - [ ] 단위 테스트 작성
   - [ ] 통합 테스트 통과
   - [ ] 커버리지 80% 이상
   - [ ] CI/CD 통과

3. **문서**
   - [ ] API 명세 작성
   - [ ] 사용 예제 포함
   - [ ] 주의사항 명시

4. **리뷰**
   - [ ] 코드 리뷰 완료
   - [ ] 성능 검증
   - [ ] 보안 검사

---

## 📞 연락처 & 문의

- GitHub Issues: 기능 요청, 버그 리포트
- Pull Request: 구현 기여
- Discussions: 일반 질문

---

**마지막 업데이트**: 2025-10-21
**다음 검토 예정**: 2025-11-01
