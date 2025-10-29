# API 응답 키 매핑 요약

## ka10001 (주식기본정보요청)
- 현재가: `cur_prc`
- 전일대비: `pred_pre`
- 등락률: `flu_rt`
- 거래량: `trde_qty`
- 대비기호: `pre_sig` (2=상승, 5=하락, 3=보합)

## ka10004 (주식호가요청)
### 매도 호가
- 1호가: `sel_fpr_bid` (가격), `sel_fpr_req` (수량)
- 2-10호가: `sel_2th_pre_bid` ~ `sel_10th_pre_bid`

### 매수 호가
- 1호가: `buy_fpr_bid` (가격), `buy_fpr_req` (수량)
- 2-10호가: `buy_2th_pre_bid` ~ `buy_10th_pre_bid`

## ka10005 (주식일주월시분요청)
- 응답 키: `stk_ddwkmm` (리스트)
- 필드:
  - `date`: 날짜
  - `open_pric`: 시가
  - `high_pric`: 고가
  - `low_pric`: 저가
  - `close_pric`: 종가
  - `trde_qty`: 거래량
  - `for_poss`: 외인보유
  - `for_wght`: 외인비중

## ka10080 (주식분봉차트조회요청)
- `cntr_tm`: 체결시간 (YYYYMMDDHHMMSS)
- `cur_prc`: 현재가
- `pred_pre`: 전일대비
- `pred_pre_sig`: 대비기호 (2=상승, 5=하락)
- `trde_qty`: 거래량
- `open_pric`: 시가
- `high_pric`: 고가
- `low_pric`: 저가

## ka10081 (주식일봉차트조회요청)
- `dt`: 날짜 (YYYYMMDD)
- `cur_prc`: 종가
- `open_pric`: 시가
- `high_pric`: 고가
- `low_pric`: 저가
- `trde_qty`: 거래량
- `pred_pre`: 전일대비
- `pred_pre_sig`: 대비기호

## 공통 패턴
1. **대비기호 (pre_sig / pred_pre_sig)**:
   - `2`: 상승 (빨강)
   - `5`: 하락 (파랑)
   - `3`: 보합 (검정)

2. **가격/수량 필드**:
   - 문자열로 반환되며 `+`, `-`, `,` 기호 포함
   - 사용 전 `.replace('+', '').replace('-', '').replace(',', '')` 처리 필요

3. **날짜/시간 형식**:
   - 날짜: `YYYYMMDD`
   - 시간: `HHMMSS` 또는 `YYYYMMDDHHMMSS`
