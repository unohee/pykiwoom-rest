# 차트 API (정확한 사양)

주식 차트 데이터를 조회하는 API - 실제 Excel 명세서 기반

## 공통 정보
- **Base URL**: `/api/dostk/chart`
- **Method**: `POST`
- **Content-Type**: `application/json;charset=UTF-8`

## 주식틱차트조회요청 (ka10079)

### 기본 정보
- **시간 단위**: 틱
- **URL**: `/api/dostk/chart`

### 요청 파라미터

| 파라미터 | 한글명 | 타입 | 필수 | 설명 |
|----------|--------|------|------|------|
| stk_cd | 종목코드 | String | Y | 거래소별 종목코드 (KRX:039490,NXT:039490_NX,SOR:039490_AL) |

### 응답 필드

| 필드 | 한글명 | 타입 | 설명 |
|------|--------|------|------|
| stk_cd | 종목코드 | String |  |
| last_tic_cnt | 마지막틱갯수 | String |  |
| cur_prc | 현재가 | String |  |
| trde_qty | 거래량 | String |  |
| cntr_tm | 체결시간 | String |  |
| open_pric | 시가 | String |  |
| high_pric | 고가 | String |  |
| low_pric | 저가 | String |  |
| upd_stkpc_tp | 수정주가구분 | String | 1:유상증자, 2:무상증자, 4:배당락, 8:액면분할, 16:액면병합, 32:기업합병, 64:감자, 256:권리락 |

---

## 주식분봉차트조회요청 (ka10080)

### 기본 정보
- **시간 단위**: 분 (1, 3, 5, 10, 15, 30, 45, 60분)
- **URL**: `/api/dostk/chart`

### 요청 파라미터

| 파라미터 | 한글명 | 타입 | 필수 | 설명 |
|----------|--------|------|------|------|
| stk_cd | 종목코드 | String | Y | 거래소별 종목코드 (KRX:039490,NXT:039490_NX,SOR:039490_AL) |
| tic_scope | 틱범위 | String | Y | 1:1분, 3:3분, 5:5분, 10:10분, 15:15분, 30:30분, 45:45분, 60:60분 |
| upd_stkpc_tp | 수정주가구분 | String | Y | 0:수정주가미반영, 1:수정주가반영 |

### 응답 필드

| 필드 | 한글명 | 타입 | 설명 |
|------|--------|------|------|
| stk_cd | 종목코드 | String |  |
| cur_prc | 현재가 | String |  |
| trde_qty | 거래량 | String |  |
| cntr_tm | 체결시간 | String |  |
| open_pric | 시가 | String |  |
| high_pric | 고가 | String |  |
| low_pric | 저가 | String |  |
| upd_stkpc_tp | 수정주가구분 | String | 1:유상증자, 2:무상증자, 4:배당락, 8:액면분할, 16:액면병합, 32:기업합병, 64:감자, 256:권리락 |
| upd_rt | 수정비율 | String |  |

---

## 주식일봉차트조회요청 (ka10081)

### 기본 정보
- **시간 단위**: 일
- **URL**: `/api/dostk/chart`

### 요청 파라미터

| 파라미터 | 한글명 | 타입 | 필수 | 설명 |
|----------|--------|------|------|------|
| stk_cd | 종목코드 | String | Y | 거래소별 종목코드 (KRX:039490,NXT:039490_NX,SOR:039490_AL) |

### 응답 필드

| 필드 | 한글명 | 타입 | 설명 |
|------|--------|------|------|
| stk_cd | 종목코드 | String |  |
| cur_prc | 현재가 | String |  |
| trde_qty | 거래량 | String |  |
| trde_prica | 거래대금 | String |  |
| dt | 일자 | String |  |
| open_pric | 시가 | String |  |
| high_pric | 고가 | String |  |
| low_pric | 저가 | String |  |
| upd_stkpc_tp | 수정주가구분 | String | 1:유상증자, 2:무상증자, 4:배당락, 8:액면분할, 16:액면병합, 32:기업합병, 64:감자, 256:권리락 |

---

## 주식주봉차트조회요청 (ka10082)

### 기본 정보
- **시간 단위**: 주
- **URL**: `/api/dostk/chart`

### 요청 파라미터

| 파라미터 | 한글명 | 타입 | 필수 | 설명 |
|----------|--------|------|------|------|
| stk_cd | 종목코드 | String | Y | 거래소별 종목코드 (KRX:039490,NXT:039490_NX,SOR:039490_AL) |

### 응답 필드

| 필드 | 한글명 | 타입 | 설명 |
|------|--------|------|------|
| stk_cd | 종목코드 | String |  |
| cur_prc | 현재가 | String |  |
| trde_qty | 거래량 | String |  |
| trde_prica | 거래대금 | String |  |
| dt | 일자 | String |  |
| open_pric | 시가 | String |  |
| high_pric | 고가 | String |  |
| low_pric | 저가 | String |  |
| upd_stkpc_tp | 수정주가구분 | String | 1:유상증자, 2:무상증자, 4:배당락, 8:액면분할, 16:액면병합, 32:기업합병, 64:감자, 256:권리락 |

---

## 주식월봉차트조회요청 (ka10083)

### 기본 정보
- **시간 단위**: 월
- **URL**: `/api/dostk/chart`

### 요청 파라미터

| 파라미터 | 한글명 | 타입 | 필수 | 설명 |
|----------|--------|------|------|------|
| stk_cd | 종목코드 | String | Y | 거래소별 종목코드 (KRX:039490,NXT:039490_NX,SOR:039490_AL) |

### 응답 필드

| 필드 | 한글명 | 타입 | 설명 |
|------|--------|------|------|
| stk_cd | 종목코드 | String |  |
| cur_prc | 현재가 | String |  |
| trde_qty | 거래량 | String |  |
| trde_prica | 거래대금 | String |  |
| dt | 일자 | String |  |
| open_pric | 시가 | String |  |
| high_pric | 고가 | String |  |
| low_pric | 저가 | String |  |
| upd_stkpc_tp | 수정주가구분 | String | 1:유상증자, 2:무상증자, 4:배당락, 8:액면분할, 16:액면병합, 32:기업합병, 64:감자, 256:권리락 |

---

## 주식년봉차트조회요청 (ka10094)

### 기본 정보
- **시간 단위**: 년
- **URL**: `/api/dostk/chart`

### 요청 파라미터

| 파라미터 | 한글명 | 타입 | 필수 | 설명 |
|----------|--------|------|------|------|
| stk_cd | 종목코드 | String | Y | 거래소별 종목코드 (KRX:039490,NXT:039490_NX,SOR:039490_AL) |

### 응답 필드

| 필드 | 한글명 | 타입 | 설명 |
|------|--------|------|------|
| stk_cd | 종목코드 | String |  |
| cur_prc | 현재가 | String |  |
| trde_qty | 거래량 | String |  |
| trde_prica | 거래대금 | String |  |
| dt | 일자 | String |  |
| open_pric | 시가 | String |  |
| high_pric | 고가 | String |  |
| low_pric | 저가 | String |  |
| upd_stkpc_tp | 수정주가구분 | String | 1:유상증자, 2:무상증자, 4:배당락, 8:액면분할, 16:액면병합, 32:기업합병, 64:감자, 256:권리락 |

---
