# PyKiwoom-REST API 구현 PRD (Product Requirements Document)

> **문서 ID**: PRD-2025-1021-API-IMPLEMENTATION
> **작성일**: 2025-10-21
> **상태**: Draft
> **목표**: 206개 API 중 미구현 74개 API 구현

---

## 📋 Executive Summary

PyKiwoom-REST는 현재 132개 API를 구현하여 64.1%의 완성도를 달성했습니다.
본 PRD는 남은 74개 미구현 API를 3개 Phase로 나누어 구현하기 위한 요구사항을 정의합니다.

**목표**:
- 206개 API 100% 구현
- 높은 품질의 코드 (타입 힌팅, 테스트, 문서)
- 프로덕션 레디 상태 달성

---

## 🎯 Phase 1: 핵심 API 완성 (CRITICAL)

### Phase 1 목표
- ✅ 기본 거래 기능 완성
- ✅ 인증 시스템 통합
- ✅ 모든 주요 사용자 시나리오 지원
- 예상 기간: 2-3주

### Phase 1-A: 인증 API (2개)

**목표**: OAuth2 토큰 관리 기능 완성

**API 목록**:
1. **au10001 - 접근토큰 발급**
   - 식별자: au10001
   - 타입: Authentication
   - HTTP 메서드: POST
 - 엔드포인트: /oauth2/token
   - 역할: OAuth2 토큰 발급
   - 입력: app_key, app_secret
   - 출력: access_token, token_type, expires_in
   - 구현파일: src/pykiwoom_rest/auth_api.py
   - 메서드: get_access_token()
   - 난이도: ⭐ (Low)
   - 예상시간: 1-2시간

2. **au10002 - 접근토큰폐기**
   - 식별자: au10002
   - 타입: Authentication
   - HTTP 메서드: POST
 - 엔드포인트: /oauth2/revoke
   - 역할: 토큰 무효화
   - 입력: access_token
   - 출력: success/failure
   - 구현파일: src/pykiwoom_rest/auth_api.py
   - 메서드: revoke_token()
   - 난이도: ⭐ (Low)
   - 예상시간: 30분-1시간

**구현 전략**:
- auth_api.py 신규 생성
- BaseAPIClient 상속
- 토큰 캐싱 메커니즘 고려
- Rate limiter 적용

**테스트 요구사항**:
- 단위 테스트: 토큰 발급, 만료, 갱신
- 통합 테스트: 토큰을 사용한 API 호출
- Mock 테스트: 성공/실패 시나리오

---

### Phase 1-B: Stock API 확장 (7개)

**목표**: 주식 시세 조회 기능 완성

**API 목록**:

1. **ka10002 - 주식거래원요청**
   - 식별자: ka10002
   - 역할: 거래원 정보 조회
   - 메서드: get_stock_traders()
   - 난이도: ⭐⭐ (Medium)
   - 예상시간: 1-2시간
   - 구현파일: stock_api.py 확장

2. **ka10003 - 체결정보요청**
   - 식별자: ka10003
   - 역할: 체결 정보 조회
   - 메서드: get_execution_info() [확인: 이미 구현?]
   - 난이도: ⭐⭐ (Medium)
   - 예상시간: 1-2시간

3. **ka10005 - 주식일주월시분요청**
   - 식별자: ka10005
   - 역할: 일/주/월/분 데이터 통합 조회
   - 메서드: get_stock_time_data()
   - 난이도: ⭐⭐ (Medium)
   - 예상시간: 1.5-2시간

4. **ka10006 - 주식시분요청**
   - 식별자: ka10006
   - 역할: 분봉 시세 데이터
   - 메서드: get_minute_quote() [확인: 차트API와 차이?]
   - 난이도: ⭐ (Low)
   - 예상시간: 1시간

5. **ka10007 - 시세표성정보요청**
   - 식별자: ka10007
   - 역할: 시세 추이 정보
   - 메서드: get_quote_trend_info()
   - 난이도: ⭐⭐ (Medium)
   - 예상시간: 1.5-2시간

6. **ka10009 - 주식기관요청**
   - 식별자: ka10009
   - 역할: 기관 거래 정보 [확인: get_institutional_trading_trend와 중복?]
   - 메서드: get_institutional_info()
   - 난이도: ⭐⭐ (Medium)
   - 예상시간: 1.5-2시간

7. **ka10010 - 업종프로그램요청**
   - 식별자: ka10010
   - 역할: 업종별 프로그램 매매
   - 메서드: get_sector_program_info()
   - 난이도: ⭐⭐ (Medium)
   - 예상시간: 1.5-2시간

**구현 전략**:
- stock_api.py 확장 (기존 19개 메서드 + 7개 추가)
- 기존 메서드와의 중복 확인 필수
- Response 모델 검토 및 확장
- Pagination 지원 검토

**예상 소계 시간**: 8-13시간

---

### Phase 1-C: Chart API 확장 (2개)

**목표**: 차트 데이터 조회 기능 완성

**API 목록**:

1. **ka10079 - 주식틱차트조회요청**
   - 식별자: ka10079
   - 역할: 틱 단위 차트 데이터
   - 메서드: get_tick_chart() [확인: 이미 구현?]
   - 난이도: ⭐ (Low)
   - 구현파일: chart_api.py

2. **ka10094 - 주식년봉차트조회요청**
   - 식별자: ka10094
   - 역할: 연간 차트 데이터
   - 메서드: get_yearly_chart() [확인: 이미 구현?]
   - 난이도: ⭐ (Low)
   - 구현파일: chart_api.py

**구현 전략**:
- 기존 get_*_chart 메서드 패턴 적용
- Pagination 지원 (필요시)
- DataFrame 변환 지원

**예상 소계 시간**: 2-3시간 (확인 필요)

---

### Phase 1-D: Account API 확장 (10개)

**목표**: 계좌 관리 기능 완성

**API 목록**:

1. **kt00001 - 예수금상세현황요청**
   - 메서드: get_deposit_detail() [이미 구현됨]
   - 난이도: ⭐

2. **kt00002 - 일별추정예탁자산현황요청**
   - 메서드: get_daily_asset_status()
   - 난이도: ⭐⭐

3. **kt00004 - 계좌평가현황요청**
   - 메서드: get_account_evaluation() [이미 구현됨]
   - 난이도: ⭐

4. **kt00005 - 체결잔고요청**
   - 메서드: get_execution_balance() [이미 구현됨]
   - 난이도: ⭐

5. **kt00007 - 계좌별익일결제예정내역요청**
   - 메서드: get_next_settlement()
   - 난이도: ⭐⭐

6. **kt00009 - 주문체결현황요청**
   - 메서드: get_order_execution_status() [이미 구현됨]
   - 난이도: ⭐

7. **kt00010 - 주문인출가능금액요청**
   - 메서드: get_withdrawable_amount() [이미 구현됨]
   - 난이도: ⭐

8. **kt00013 - 증거금세부내역조회요청**
   - 메서드: get_margin_detail() [이미 구현됨]
   - 난이도: ⭐⭐

9. **kt00015 - 위탁종합거래내역요청**
   - 메서드: get_comprehensive_trading_history()
   - 난이도: ⭐⭐

10. **kt00016 - 일별계좌수익률상세현황요청**
    - 메서드: get_daily_account_return_detail()
    - 난이도: ⭐⭐

**구현 전략**:
- 기존 22개 메서드 기반 확장
- 많은 메서드가 이미 구현되었을 가능성 높음
- 누락된 메서드만 우선 구현

**예상 소계 시간**: 8-10시간

---

### Phase 1-E: Order API 신용거래 확장 (6개)

**목표**: 신용거래 주문 기능 완성

**API 목록**:

1. **kt10006 - 신용 매수주문**
   - 메서드: buy_credit() [이미 구현됨]
   - 난이도: ⭐⭐

2. **kt10007 - 신용 매도주문**
   - 메서드: sell_credit() [이미 구현됨]
   - 난이도: ⭐⭐

3. **kt10008 - 신용 정정주문**
   - 메서드: modify_credit_order() [이미 구현됨]
   - 난이도: ⭐⭐

4. **kt10009 - 신용 취소주문**
   - 메서드: cancel_credit_order() [이미 구현됨]
   - 난이도: ⭐⭐

5. **kt20016 - 신용융자 가능종목요청**
   - 메서드: get_credit_available_stocks() [이미 구현됨]
   - 난이도: ⭐⭐

6. **kt20017 - 신용융자 가능문의**
   - 메서드: check_credit_available() [이미 구현됨]
   - 난이도: ⭐

**구현 전략**:
- 대부분 이미 구현되었을 가능성
- 누락/버그 확인 및 수정
- 테스트 커버리지 확인

**예상 소계 시간**: 4-6시간 (확인/수정만)

---

## 🌟 Phase 2: 추가 상품 API (MEDIUM 우선순위)

### Phase 2 목표
- ELW, ETF, 금현물 API 구현
- 각 상품별 전문화된 기능 제공
- 예상 기간: 3-4주

### Phase 2-A: ELW API (12개)

**파일**: src/pykiwoom_rest/elw_api.py (신규)

**API 목록**:
- ka30001: ELW가격급등락요청 → get_elw_price_fluctuation()
- ka30002: 거래원별ELW순매매상위요청 → get_elw_network_trading_top()
- ka30003: ELWLP보유일별추이요청 → get_elw_lp_possession_trend()
- ka30004: ELW괴리율요청 → get_elw_divergence_rate()
- ka30005: ELW조건검색요청 → get_elw_condition_search()
- ka30009: ELW등락율순위요청 → get_elw_rate_ranking()
- ka30010: ELW잔량순위요청 → get_elw_volume_ranking()
- ka30011: ELW근접율요청 → get_elw_proximity_rate()
- ka30012: ELW종목상세정보요청 → get_elw_product_info()
- 추가 3개 (분석 필요)

**예상 시간**: 8-10시간

---

### Phase 2-B: ETF API (9개)

**파일**: src/pykiwoom_rest/etf_api.py (신규)

**API 목록**:
- ka40001: ETF수익율요청 → get_etf_return_rate()
- ka40002: ETF종목정보요청 → get_etf_stock_info()
- ka40003: ETF일별추이요청 → get_etf_daily_trend()
- ka40004: ETF전체시세요청 → get_etf_all_quote()
- ka40006: ETF시간대별추이요청 → get_etf_hourly_trend()
- ka40007: ETF시간대별체결요청 → get_etf_hourly_execution()
- ka40008: ETF일자별체결요청 → get_etf_daily_execution()
- ka40009: ETF시간대별체결요청 (추가) → get_etf_intraday_execution()
- ka40010: ETF시간대별추이요청 (추가) → get_etf_intraday_trend()

**예상 시간**: 6-8시간

---

### Phase 2-C: 금현물 API (19개)

**파일**: src/pykiwoom_rest/commodity_api.py (신규)

**API 목록** (주요):
- ka50010: 금현물체결추이 → get_commodity_execution_trend()
- ka50012: 금현물일별추이 → get_commodity_daily_trend()
- ka50079: 금현물틱차트조회 → get_commodity_tick_chart()
- ka50080: 금현물분봉차트조회 → get_commodity_minute_chart()
- ka50081: 금현물일봉차트조회 → get_commodity_daily_chart()
- ka50082: 금현물주봉차트조회 → get_commodity_weekly_chart()
- ka50083: 금현물월봉차트조회 → get_commodity_monthly_chart()
- kt50000: 금현물 매수주문 → buy_commodity()
- kt50001: 금현물 매도주문 → sell_commodity()
- kt50002: 금현물 정정주문 → modify_commodity_order()
- kt50003: 금현물 취소주문 → cancel_commodity_order()
- 추가 8개 (조회 기능)

**예상 시간**: 12-15시간

---

## 🔧 Phase 3: 고급 기능 API (LOW 우선순위)

### Phase 3 목표
- 조건검색, 프로그램 매매, 테마 등 고급 기능
- 예상 기간: 2-3주

### Phase 3-A: 조건검색 API (4개)

**파일**: src/pykiwoom_rest/screener_api.py (신규)

- ka10171: 조건검색 목록조회 → get_screener_list()
- ka10172: 조건검색 요청 일반 → search_by_condition()
- ka10173: 조건검색 요청 실시간 → search_by_condition_realtime()
- ka10174: 조건검색 실시간 해제 → stop_realtime_search()

**예상 시간**: 4-6시간

---

### Phase 3-B: 기타 고급 API (10개+)

**파일**: src/pykiwoom_rest/advanced_api.py (신규)

포함 내용:
- 대차거래 관련 (4개)
- 테마 관련 (2개)
- 프로그램 매매 추가 (5개)
- 실시간 시세 관련 (3개)

**예상 시간**: 10-15시간

---

## 📊 구현 요구사항

### 코딩 표준
- ✅ 타입 힌팅 100% (Python 3.10+)
- ✅ 메서드 docstring 필수 (Args, Returns, Raises)
- ✅ Rate Limit 고려
- ✅ 에러 처리 (exception_utils 활용)
- ✅ Response 모델 (response_model.py)
- ✅ Pagination 지원 (필요시)

### 테스트 요구사항
- ✅ 각 메서드당 unit test
- ✅ 통합 테스트 (pytest)
- ✅ Mock 데이터 테스트
- ✅ 에러 시나리오 테스트
- ✅ 최소 80% 커버리지

### 문서 요구사항
- ✅ API 명세서 업데이트 (KIWOOM_API_SPECIFICATION.md)
- ✅ 메서드 예제 코드
- ✅ CLAUDE.md 업데이트
- ✅ 변경 로그 (CHANGELOG.md)

### 성능 요구사항
- ✅ Rate Limit 준수 (초당 20회)
- ✅ 응답 시간 < 1초 (네트워크 제외)
- ✅ 메모리 누수 없음
- ✅ 병렬 처리 지원 (concurrent_api 활용)

---

## 🎯 성공 기준

### Phase 1 완료
- [ ] 모든 인증 API 구현 및 테스트 통과
- [ ] Stock/Chart/Account/Order API 완성도 95% 이상
- [ ] 기본 거래 시나리오 모두 지원
- [ ] 커버리지 85% 이상

### Phase 2 완료
- [ ] ELW, ETF, 금현물 API 모두 구현
- [ ] 각 상품별 거래 기능 정상 작동
- [ ] 커버리지 80% 이상

### Phase 3 완료
- [ ] 모든 206개 API 구현
- [ ] 전체 커버리지 80% 이상
- [ ] CI/CD 모두 통과
- [ ] 프로덕션 레디

---

## 📈 예상 일정

| Phase | 기간 | 개발 | 테스트 | 리뷰 | 합계 |
|-------|------|------|--------|------|------|
| 1 | 2-3주 | 17-25h | 5-8h | 2-3h | 24-36h |
| 2 | 3-4주 | 26-33h | 6-10h | 2-3h | 34-46h |
| 3 | 2-3주 | 14-21h | 4-6h | 1-2h | 19-29h |
| **Total** | **7-10주** | **57-79h** | **15-24h** | **5-8h** | **77-111h** |

---

## 🚀 실행 계획

### Week 1-2: Phase 1-A/B (인증, 주식 API)
- [ ] auth_api.py 구현
- [ ] Stock API 7개 메서드 추가
- [ ] Unit tests 작성
- [ ] 코드 리뷰

### Week 2-3: Phase 1-C/D/E (차트, 계좌, 주문)
- [ ] Chart API 확장
- [ ] Account API 10개 메서드 추가
- [ ] Order API 신용거래 확인/수정
- [ ] 통합 테스트

### Week 4-6: Phase 2 (ELW, ETF, 금현물)
- [ ] ELW API 12개
- [ ] ETF API 9개
- [ ] 금현물 API 19개
- [ ] 테스트 및 문서화

### Week 7-10: Phase 3 (고급 API) + 마무리
- [ ] 조건검색 API
- [ ] 기타 고급 API
- [ ] 전체 통합 테스트
- [ ] 프로덕션 배포

---

## 📋 Acceptance Criteria

```
GIVEN: 206개 모든 API가 정의됨
WHEN: 구현 완료
THEN:
  - 모든 API 메서드가 구현되어야 함
  - 타입 힌팅 100%
  - 테스트 커버리지 80% 이상
  - CI/CD 모두 통과
  - 프로덕션 배포 가능
```

---

**문서 버전**: 1.0
**최종 검토**: 2025-10-21
