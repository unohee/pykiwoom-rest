# 🚀 PyKiwoom-REST Swagger UI 설정 및 사용 가이드

## 📋 개요

PyKiwoom-REST v2.1.0이 Swagger UI를 지원합니다. 웹 브라우저를 통해 모든 API 엔드포인트를 테스트할 수 있습니다.

---

## 🔧 설치 및 준비

### 1단계: 의존성 설치

```bash
# 프로젝트 디렉토리로 이동
cd pykiwoom-rest

# Flask 및 Flasgger 설치
pip install -r requirements.txt
```

### 2단계: 환경변수 설정

`.env` 파일을 프로젝트 루트에 생성하고 인증 정보를 입력합니다:

```bash
# .env 파일 예시
ACCOUNT_NO=63513804
KIWOOM_APPKEY=your_app_key_here
KIWOOM_APPSECRET=your_app_secret_here
```

또는 API 호출 시 직접 입력할 수 있습니다.

---

## 🚀 서버 실행

### 기본 실행 방법

```bash
python3 swagger_server.py
```

서버 시작 시 다음과 같은 메시지가 표시됩니다:

```
╔════════════════════════════════════════════════════════╗
║     PyKiwoom-REST Swagger UI Server v2.1.0             ║
╚════════════════════════════════════════════════════════╝

📍 서버 시작 중...

🌐 액세스 주소:
   • Swagger UI: http://localhost:5000/apidocs
   • REST API:  http://localhost:5000/api/*
   • 헬스 체크: http://localhost:5000/health
```

### 백그라운드 실행 (Linux/Mac)

```bash
nohup python3 swagger_server.py > swagger_server.log 2>&1 &
```

### Docker를 사용한 실행 (선택사항)

```bash
# Docker 이미지 빌드
docker build -t pykiwoom-swagger .

# 컨테이너 실행
docker run -p 5000:5000 \
  -e ACCOUNT_NO=63513804 \
  -e KIWOOM_APPKEY=your_key \
  -e KIWOOM_APPSECRET=your_secret \
  pykiwoom-swagger
```

---

## 🌐 Swagger UI 접근

1. 웹 브라우저에서 다음 주소로 이동:
   ```
   http://localhost:5000/apidocs
   ```

2. Swagger UI 대시보드가 로드됩니다

3. API 카테고리별로 엔드포인트가 정렬되어 있습니다:
   - **Authentication** - 인증 관련
   - **Stock** - 주식 시세 데이터
   - **Chart** - 차트 데이터
   - **Account** - 계좌 관리
   - **Ranking** - 순위 및 통계

---

## 📝 API 테스트 방법

### 방법 1: Swagger UI에서 테스트

#### 1. 토큰 발급 (선택사항)

1. "Authentication" 섹션 확장
2. `POST /api/auth/token` 클릭
3. **"Try it out"** 버튼 클릭
4. JSON 바디에 아래 입력:
   ```json
   {
     "appkey": "your_app_key",
     "appsecret": "your_app_secret"
   }
   ```
5. **"Execute"** 버튼 클릭
6. 응답에서 `access_token` 복사

#### 2. 주식 정보 조회

1. "Stock" 섹션 확장
2. `GET /api/stock/price` 클릭
3. **"Try it out"** 버튼 클릭
4. 파라미터 입력:
   - `stock_code`: `005930` (삼성전자)
5. **"Execute"** 버튼 클릭
6. 응답 확인

#### 3. 차트 데이터 조회

1. "Chart" 섹션 확장
2. `GET /api/chart/minute` 클릭
3. **"Try it out"** 버튼 클릭
4. 파라미터 입력:
   - `stock_code`: `005930`
   - `interval`: `5` (5분봉)
   - `count`: `100`
5. **"Execute"** 버튼 클릭

#### 4. 계좌 정보 조회

1. "Account" 섹션 확장
2. `GET /api/account/balance` 클릭
3. **"Try it out"** 버튼 클릭
4. **"Execute"** 버튼 클릭
5. 계좌 잔고 정보 확인

### 방법 2: cURL을 사용한 테스트

```bash
# 주식 현재가 조회
curl "http://localhost:5000/api/stock/price?stock_code=005930" \
  -H "Content-Type: application/json"

# 투자자별 매매동향
curl "http://localhost:5000/api/stock/investor-trading?stock_code=005930" \
  -H "Content-Type: application/json"

# 분봉 차트
curl "http://localhost:5000/api/chart/minute?stock_code=005930&interval=5&count=100" \
  -H "Content-Type: application/json"

# 계좌 잔고
curl "http://localhost:5000/api/account/balance" \
  -H "Content-Type: application/json"
```

### 방법 3: Python 스크립트

```python
import requests

# API 베이스 URL
BASE_URL = "http://localhost:5000"

# 주식 현재가 조회
response = requests.get(
    f"{BASE_URL}/api/stock/price",
    params={"stock_code": "005930"}
)
print("주식 정보:", response.json())

# 투자자별 매매동향
response = requests.get(
    f"{BASE_URL}/api/stock/investor-trading",
    params={"stock_code": "005930"}
)
print("투자자 동향:", response.json())

# 분봉 차트
response = requests.get(
    f"{BASE_URL}/api/chart/minute",
    params={
        "stock_code": "005930",
        "interval": 5,
        "count": 100
    }
)
print("차트 데이터:", response.json())

# 계좌 잔고
response = requests.get(f"{BASE_URL}/api/account/balance")
print("계좌 잔고:", response.json())
```

---

## 📊 주요 API 엔드포인트 요약

### 인증 (Authentication)

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| POST | `/api/auth/token` | OAuth2 토큰 발급 |

### 주식 (Stock)

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | `/api/stock/price` | 현재가 조회 |
| GET | `/api/stock/investor-trading` | 투자자별 매매동향 |
| GET | `/api/stock/member-trading` | 기관별 매매동향 |
| GET | `/api/stock/program-trading` | 프로그램매매동향 |

### 차트 (Chart)

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | `/api/chart/minute` | 분봉 차트 데이터 |
| GET | `/api/chart/daily` | 일봉 차트 데이터 |

### 계좌 (Account)

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | `/api/account/balance` | 계좌 잔고 |
| GET | `/api/account/estimated-asset` | 추정자산 |
| GET | `/api/account/deposit-detail` | 예수금 상세 |
| GET | `/api/account/realized-profit` | 실현손익 |

### 순위 (Ranking)

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | `/api/ranking/volume` | 거래량 상위 종목 |

---

## 🔍 응답 예시

### 주식 현재가 응답

```json
{
  "output": {
    "hts_kor_isnm": "삼성전자",
    "stck_prpr": "73000",
    "prdy_vrss": "+1500",
    "prdy_ctrt": "+2.10",
    "trade_qty": "22742094"
  },
  "metadata": {
    "timestamp": "2025-10-21T16:16:07.867591",
    "tr_code": "ka10001",
    "processing_time": 0.136
  }
}
```

### 토큰 발급 응답

```json
{
  "access_token": "IutdHpcKPO99r-3q2f98jubsm0Y7sQWf...",
  "token_type": "Bearer",
  "expires_in": 86400,
  "issued_at": "2025-10-21T16:15:44.114514",
  "expires_at": "2025-10-22T16:10:44.114508",
  "status": "valid"
}
```

---

## ⚙️ 고급 설정

### 포트 변경

`swagger_server.py`의 마지막 줄을 수정:

```python
app.run(
    host='0.0.0.0',
    port=8000,  # 포트 변경
    debug=True
)
```

### 외부 접근 허용

```python
app.run(
    host='0.0.0.0',  # 모든 인터페이스에서 접근 가능
    port=5000,
    debug=False  # 프로덕션에서는 False
)
```

### CORS 설정

```bash
# flask-cors 설치
pip install flask-cors
```

`swagger_server.py`에 추가:

```python
from flask_cors import CORS
CORS(app)
```

---

## 🐛 문제 해결

### 1. "Connection refused" 오류

```
Error: Could not connect to http://localhost:5000
```

**해결:**
- 서버가 실행 중인지 확인: `ps aux | grep swagger_server.py`
- 포트 충돌 확인: `lsof -i :5000`
- 서버 재시작: `python3 swagger_server.py`

### 2. "Module not found" 오류

```
ModuleNotFoundError: No module named 'flask'
```

**해결:**
```bash
pip install flask flasgger
```

### 3. 인증 오류

```
"error": "Missing appkey or appsecret"
```

**해결:**
- `.env` 파일 확인
- 또는 토큰 발급 API에서 직접 인증정보 제공

### 4. 계좌 조회 실패

```
"error": "KiwoomRest object has no attribute 'account_api'"
```

**해결:**
- `.env` 파일에 올바른 인증정보 입력
- 또는 `/api/auth/token` 먼저 호출

---

## 📤 협업자와 공유하기

### 준비 사항

협업자에게 다음 파일들을 공유합니다:

```
pykiwoom-rest/
├── swagger_server.py          # Swagger 서버 (메인)
├── openapi.yaml              # OpenAPI 명세서
├── requirements.txt           # 의존성
├── .env.example              # 환경변수 템플릿
├── SWAGGER_UI_GUIDE.md       # 이 파일
└── src/pykiwoom_rest/        # 메인 패키지
```

### 협업자 설정 방법

1. 파일 받기
2. 의존성 설치:
   ```bash
   pip install -r requirements.txt
   ```
3. `.env` 파일 생성:
   ```bash
   cp .env.example .env
   # .env 파일 편집하여 인증정보 입력
   ```
4. 서버 시작:
   ```bash
   python3 swagger_server.py
   ```
5. Swagger UI 접속:
   ```
   http://localhost:5000/apidocs
   ```

---

## 🔐 보안 주의사항

- ⚠️ **프로덕션 환경에서는 `debug=False`로 설정하세요**
- ⚠️ **API 키를 `.env` 파일에 저장하고 `.gitignore`에 추가하세요**
- ⚠️ **외부 접근이 필요한 경우 HTTPS를 사용하세요**
- ⚠️ **Rate limit을 고려하여 테스트하세요 (초당 20회)**

---

## 📞 지원 및 피드백

문제가 발생하거나 기능 요청이 있으면 GitHub Issues에 등록하세요:
- GitHub: https://github.com/unohee/pykiwoom-rest/issues

---

**마지막 업데이트**: 2025-10-21
**버전**: 2.1.0
**상태**: ✅ Ready for Testing
