# Sector Chart API 사용 가이드

업종(지수) 차트 데이터 조회 API 사용 방법을 설명합니다.

## 목차
- [개요](#개요)
- [업종코드 안내](#업종코드-안내)
- [API 메서드](#api-메서드)
  - [업종 분봉 조회](#1-업종-분봉-조회-ka20005)
  - [업종 틱차트 조회](#2-업종-틱차트-조회-ka20004)
  - [업종 일봉 조회](#3-업종-일봉-조회-ka20006)
  - [업종 주봉 조회](#4-업종-주봉-조회-ka20007)
  - [업종 월봉 조회](#5-업종-월봉-조회-ka20008)
  - [업종 년봉 조회](#6-업종-년봉-조회-ka20019)
- [응답 데이터 구조](#응답-데이터-구조)
- [사용 예제](#사용-예제)

---

## 개요

Sector Chart API는 KOSPI, KOSDAQ 등 주요 지수의 차트 데이터를 조회하는 기능을 제공합니다.

```python
from pykiwoom_rest import KiwoomRest

kiwoom = KiwoomRest()

# KOSPI 5분봉 조회
result = kiwoom.get_sector_minute_chart("001", interval=5)
```

---

## 업종코드 안내

| 코드 | 업종명 | 설명 |
|------|--------|------|
| 001 | KOSPI | 코스피 종합지수 |
| 002 | 대형주 | KOSPI 대형주 |
| 003 | 중형주 | KOSPI 중형주 |
| 004 | 소형주 | KOSPI 소형주 |
| 101 | KOSDAQ | 코스닥 종합지수 |
| 201 | KOSPI200 | 코스피 200 |
| 302 | KOSTAR | 코스타 |
| 701 | KRX100 | KRX 100 |

> **참고**: 4자리 코드(예: "0001")를 입력해도 자동으로 3자리(예: "001")로 변환됩니다.

---

## API 메서드

### 1. 업종 분봉 조회 (ka20005)

분 단위 OHLCV 데이터를 조회합니다.

```python
def get_sector_minute_chart(
    sector_code: str,      # 업종코드 (3자리)
    interval: int = 1      # 분봉 간격 (1, 3, 5, 10, 30)
) -> Dict[str, Any]
```

**사용 예제:**
```python
# KOSPI 5분봉 조회
result = kiwoom.get_sector_minute_chart("001", interval=5)

# KOSDAQ 1분봉 조회
result = kiwoom.get_sector_minute_chart("101", interval=1)

# 4자리 코드도 사용 가능 (자동 변환)
result = kiwoom.get_sector_minute_chart("0001", interval=5)
```

**응답 예시:**
```python
{
    "inds_cd": "001",
    "inds_min_pole_qry": [
        {
            "cur_prc": "402055",      # 현재가 (x100)
            "open_pric": "403068",    # 시가
            "high_pric": "403420",    # 고가
            "low_pric": "402055",     # 저가
            "trde_qty": "47296",      # 거래량
            "acc_trde_qty": "442664", # 누적거래량
            "cntr_tm": "20251219153000",  # 체결시간
            "pred_pre": "2604",       # 전일대비
            "pred_pre_sig": "43"      # 전일대비 기호
        },
        ...
    ]
}
```

---

### 2. 업종 틱차트 조회 (ka20004)

틱 단위 시세 데이터를 조회합니다.

```python
def get_sector_tick_chart(
    sector_code: str,      # 업종코드 (3자리)
    tick_scope: int = 1    # 틱 범위 (1, 3, 5, 10, 30)
) -> Dict[str, Any]
```

**사용 예제:**
```python
# KOSPI 5틱 차트
result = kiwoom.get_sector_tick_chart("001", tick_scope=5)
```

**응답 키:** `inds_tic_chart_qry`

---

### 3. 업종 일봉 조회 (ka20006)

일별 OHLCV 데이터를 조회합니다.

```python
def get_sector_daily_chart(
    sector_code: str,              # 업종코드 (3자리)
    base_date: Optional[str] = None  # 기준일자 (YYYYMMDD, 미입력시 오늘)
) -> Dict[str, Any]
```

**사용 예제:**
```python
# KOSPI 일봉 (오늘 기준)
result = kiwoom.get_sector_daily_chart("001")

# KOSPI 일봉 (특정일 기준)
result = kiwoom.get_sector_daily_chart("001", base_date="20251220")
```

**응답 키:** `inds_dt_pole_qry`

**응답 예시:**
```python
{
    "inds_cd": "001",
    "inds_dt_pole_qry": [
        {
            "cur_prc": "402055",      # 종가
            "open_pric": "405578",    # 시가
            "high_pric": "405578",    # 고가
            "low_pric": "399705",     # 저가
            "trde_qty": "442664",     # 거래량
            "trde_prica": "16470368", # 거래대금
            "dt": "20251219"          # 일자
        },
        ...
    ]
}
```

---

### 4. 업종 주봉 조회 (ka20007)

주별 OHLCV 데이터를 조회합니다.

```python
def get_sector_weekly_chart(
    sector_code: str,              # 업종코드 (3자리)
    base_date: Optional[str] = None  # 기준일자 (YYYYMMDD, 미입력시 오늘)
) -> Dict[str, Any]
```

**사용 예제:**
```python
# KOSPI 주봉
result = kiwoom.get_sector_weekly_chart("001")
```

**응답 키:** `inds_stk_pole_qry`

---

### 5. 업종 월봉 조회 (ka20008)

월별 OHLCV 데이터를 조회합니다.

```python
def get_sector_monthly_chart(
    sector_code: str,              # 업종코드 (3자리)
    base_date: Optional[str] = None  # 기준일자 (YYYYMMDD, 미입력시 오늘)
) -> Dict[str, Any]
```

**사용 예제:**
```python
# KOSPI 월봉
result = kiwoom.get_sector_monthly_chart("001")
```

**응답 키:** `inds_mth_pole_qry`

---

### 6. 업종 년봉 조회 (ka20019)

연별 OHLCV 데이터를 조회합니다.

```python
def get_sector_yearly_chart(
    sector_code: str,              # 업종코드 (3자리)
    base_date: Optional[str] = None  # 기준일자 (YYYYMMDD, 미입력시 오늘)
) -> Dict[str, Any]
```

**사용 예제:**
```python
# KOSPI 년봉
result = kiwoom.get_sector_yearly_chart("001")
```

**응답 키:** `inds_yr_pole_qry`

---

## 응답 데이터 구조

### 공통 필드

| 필드명 | 한글명 | 설명 |
|--------|--------|------|
| `cur_prc` | 현재가/종가 | 지수값 x 100 (예: 402055 = 4020.55) |
| `open_pric` | 시가 | 지수값 x 100 |
| `high_pric` | 고가 | 지수값 x 100 |
| `low_pric` | 저가 | 지수값 x 100 |
| `trde_qty` | 거래량 | |
| `trde_prica` | 거래대금 | 백만원 단위 |
| `dt` | 일자 | YYYYMMDD |
| `cntr_tm` | 체결시간 | YYYYMMDDHHMMSS |
| `pred_pre` | 전일대비 | |
| `pred_pre_sig` | 전일대비기호 | 1:상한, 2:상승, 3:보합, 4:하한, 5:하락 |

### 가격 변환

지수값은 100을 곱한 정수로 반환됩니다.

```python
# 실제 지수값 계산
raw_price = int(data["cur_prc"])
actual_price = raw_price / 100  # 402055 -> 4020.55
```

---

## 사용 예제

### 기본 사용법

```python
from pykiwoom_rest import KiwoomRest

# 인스턴스 생성
kiwoom = KiwoomRest()

# KOSPI 5분봉 조회
result = kiwoom.get_sector_minute_chart("001", interval=5)

if "inds_min_pole_qry" in result:
    data = result["inds_min_pole_qry"]
    print(f"조회된 레코드 수: {len(data)}")

    for item in data[:5]:  # 최근 5개만 출력
        price = int(item["cur_prc"]) / 100
        time = item["cntr_tm"]
        print(f"{time}: {price:.2f}")
```

### DataFrame 변환

```python
import pandas as pd
from pykiwoom_rest import KiwoomRest

kiwoom = KiwoomRest()

# 일봉 데이터 조회
result = kiwoom.get_sector_daily_chart("001")

if "inds_dt_pole_qry" in result:
    df = pd.DataFrame(result["inds_dt_pole_qry"])

    # 가격 컬럼 변환
    price_cols = ["cur_prc", "open_pric", "high_pric", "low_pric"]
    for col in price_cols:
        df[col] = df[col].astype(float) / 100

    # 날짜 컬럼 변환
    df["dt"] = pd.to_datetime(df["dt"], format="%Y%m%d")
    df.set_index("dt", inplace=True)

    print(df.head())
```

### 여러 지수 비교

```python
from pykiwoom_rest import KiwoomRest

kiwoom = KiwoomRest()

indices = {
    "001": "KOSPI",
    "101": "KOSDAQ",
    "201": "KOSPI200"
}

for code, name in indices.items():
    result = kiwoom.get_sector_daily_chart(code)

    if "inds_dt_pole_qry" in result:
        latest = result["inds_dt_pole_qry"][0]
        price = int(latest["cur_prc"]) / 100
        change = int(latest.get("pred_pre", 0)) / 100
        print(f"{name}: {price:.2f} ({change:+.2f})")
```

### 기술적 분석 (이동평균)

```python
import pandas as pd
from pykiwoom_rest import KiwoomRest

kiwoom = KiwoomRest()

# KOSPI 일봉 조회
result = kiwoom.get_sector_daily_chart("001")
df = pd.DataFrame(result["inds_dt_pole_qry"])

# 종가 변환
df["close"] = df["cur_prc"].astype(float) / 100

# 이동평균 계산
df["MA5"] = df["close"].rolling(5).mean()
df["MA20"] = df["close"].rolling(20).mean()
df["MA60"] = df["close"].rolling(60).mean()

# 최근 데이터 출력
print(df[["close", "MA5", "MA20", "MA60"]].head(10))
```

---

## 데이터 제한

| 차트 종류 | 최대 레코드 수 | 데이터 보유 기간 |
|-----------|---------------|-----------------|
| 틱차트 | ~900건 | 당일 |
| 분봉 | ~900건 | 약 160일 |
| 일봉 | ~600건 | 약 2.5년 |
| 주봉 | ~300건 | 약 6년 |
| 월봉 | ~240건 | 약 20년 |
| 년봉 | ~41건 | 약 40년 |

---

## 버전 정보

- **v2.1.1** (2025-12-21): 업종 차트 API 파라미터 수정
  - `sect_cd` → `inds_cd` 변경
  - 엔드포인트 `/api/dostk/sect` → `/api/dostk/chart` 변경
  - 4자리→3자리 코드 자동 변환 지원
