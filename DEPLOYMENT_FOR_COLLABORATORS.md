# 🚀 협업자를 위한 PyKiwoom-REST Swagger UI 배포 가이드

## 📦 배포 패키지 내용

이 패키지에는 PyKiwoom-REST v2.1.0의 모든 API를 **Swagger UI**를 통해 테스트할 수 있는 완전한 개발 환경이 포함되어 있습니다.

```
pykiwoom-rest/
├── swagger_server.py                 # 🔴 메인 서버 파일
├── openapi.yaml                      # OpenAPI 명세서
├── SWAGGER_UI_GUIDE.md              # 상세 사용 가이드
├── DEPLOYMENT_FOR_COLLABORATORS.md  # 이 파일
├── requirements.txt                 # Python 의존성
├── .env.example                     # 환경변수 템플릿
├── README.md                        # 프로젝트 소개
└── src/pykiwoom_rest/              # PyKiwoom-REST 메인 라이브러리
    ├── __init__.py
    ├── kiwoom_rest.py              # 통합 API 클래스
    ├── stock_api.py                # 주식 API
    ├── chart_api.py                # 차트 API
    ├── account_api.py              # 계좌 API
    └── ...                          # 기타 모듈
```

---

## ⚡ 빠른 시작 (5분)

### 1단계: Python 및 pip 확인

```bash
python3 --version  # Python 3.8 이상 필요
pip3 --version
```

### 2단계: 의존성 설치

```bash
cd pykiwoom-rest
pip3 install -r requirements.txt
```

### 3단계: 환경변수 설정

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일 편집 (텍스트 에디터로 열기)
# ACCOUNT_NO, KIWOOM_APPKEY, KIWOOM_APPSECRET 값 입력
```

**Windows:**
```
메모장에서 .env 파일 열기 → 값 입력 → 저장
```

**Mac/Linux:**
```bash
nano .env
# 또는
vim .env
```

### 4단계: 서버 실행

```bash
python3 swagger_server.py
```

**성공 메시지:**
```
╔════════════════════════════════════════════════════════╗
║     PyKiwoom-REST Swagger UI Server v2.1.0             ║
╚════════════════════════════════════════════════════════╝

🌐 액세스 주소:
   • Swagger UI: http://localhost:5000/apidocs
   • REST API:  http://localhost:5000/api/*
```

### 5단계: Swagger UI 열기

웹 브라우저에서 다음 주소로 이동:
```
http://localhost:5000/apidocs
```

---

## 🎯 주요 기능

### ✅ 사용 가능한 API

1. **Stock API** - 주식 시세 및 매매동향
   - 현재가 조회
   - 투자자별 매매동향
   - 기관별 매매동향
   - 프로그램매매동향

2. **Chart API** - 차트 데이터
   - 분봉 (1, 5, 10, 15, 30, 60분)
   - 일봉
   - 주봉
   - 월봉

3. **Account API** - 계좌 관리
   - 계좌 잔고 조회
   - 추정자산 조회
   - 예수금 상세 조회
   - 실현손익 조회

4. **Authentication** - 인증
   - OAuth2 토큰 발급
   - 토큰 상태 확인

5. **Ranking API** - 순위
   - 거래량 상위 종목
   - 등락률 상위 종목

---

## 🧪 테스트 예시

### 예제 1: 삼성전자(005930) 현재가 조회

1. Swagger UI 접속: http://localhost:5000/apidocs
2. "Stock" 섹션 클릭
3. `GET /api/stock/price` 클릭
4. "Try it out" 버튼 클릭
5. `stock_code` 필드에 `005930` 입력
6. "Execute" 버튼 클릭
7. 응답 확인:
   ```json
   {
     "output": {
       "hts_kor_isnm": "삼성전자",
       "stck_prpr": "73000",
       ...
     }
   }
   ```

### 예제 2: 5분봉 차트 데이터

1. "Chart" 섹션 클릭
2. `GET /api/chart/minute` 클릭
3. "Try it out" 버튼 클릭
4. 파라미터 입력:
   - `stock_code`: `005930`
   - `interval`: `5`
   - `count`: `100`
5. "Execute" 버튼 클릭

### 예제 3: 계좌 잔고 조회

1. "Account" 섹션 클릭
2. `GET /api/account/balance` 클릭
3. "Try it out" 버튼 클릭
4. "Execute" 버튼 클릭

---

## 🔧 문제 해결

### Q1: "Connection refused" 오류가 뜹니다

**A:** 서버가 실행 중이 아닙니다. 다시 시작하세요:
```bash
python3 swagger_server.py
```

### Q2: "ModuleNotFoundError: No module named 'flask'" 오류

**A:** 의존성이 설치되지 않았습니다:
```bash
pip3 install -r requirements.txt
```

### Q3: 포트 5000이 이미 사용 중입니다

**A:** 다른 포트에서 실행하려면 `swagger_server.py` 수정:
```python
# 마지막 줄 근처에서 포트 변경
app.run(port=8000)  # 5000을 8000으로 변경
```

그 후 새 주소로 접속:
```
http://localhost:8000/apidocs
```

### Q4: "계좌 조회"가 동작하지 않습니다

**A:** 두 가지 경우가 있습니다:

1. **야시간입니다**: 일부 API는 장 시간(09:00~15:30)에만 동작합니다
2. **인증정보 오류**: `.env` 파일의 값이 정확한지 확인하세요

### Q5: 외부 컴퓨터에서 API에 접근하려고 합니다

**A:** `swagger_server.py`를 다음과 같이 수정:

```python
# 마지막 줄 근처
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',  # 모든 인터페이스 허용
        port=5000,
        debug=True
    )
```

그 후 다른 컴퓨터에서 접속:
```
http://your_ip_address:5000/apidocs
```

---

## 📊 API 응답 형식

모든 API는 JSON으로 응답합니다:

```json
{
  "output": {
    "field1": "value1",
    "field2": "value2"
  },
  "metadata": {
    "timestamp": "2025-10-21T16:16:07",
    "tr_code": "ka10001",
    "processing_time": 0.13
  },
  "return_code": 0,
  "return_msg": "SUCCESS"
}
```

---

## 🔐 보안 주의사항

⚠️ **중요**: 다음 사항을 주의하세요:

1. **API 키 보호**
   - `.env` 파일은 절대 버전 관리에 포함하지 마세요
   - `.gitignore`에 `.env`가 이미 추가되어 있습니다

2. **프로덕션 환경**
   - `debug=False`로 설정하세요
   - HTTPS를 사용하세요
   - 적절한 인증/인가 메커니즘을 추가하세요

3. **Rate Limiting**
   - Kiwoom API는 초당 20회 제한입니다
   - 많은 요청은 일정 시간 후에 실패할 수 있습니다

---

## 📚 추가 자료

- **상세 가이드**: `SWAGGER_UI_GUIDE.md` 참조
- **프로젝트 README**: `README.md` 참조
- **API 명세서**: `openapi.yaml` 참조

---

## 🚀 다음 단계

### API를 자신의 애플리케이션에 통합하기

```python
import requests

BASE_URL = "http://localhost:5000"

# 주식 현재가 조회
response = requests.get(
    f"{BASE_URL}/api/stock/price",
    params={"stock_code": "005930"}
)
data = response.json()
print(f"삼성전자 현재가: {data['output']['stck_prpr']}원")
```

### 배포 옵션

1. **로컬 개발**: `python3 swagger_server.py`
2. **백그라운드 실행**:
   ```bash
   nohup python3 swagger_server.py > swagger.log 2>&1 &
   ```
3. **Docker 배포**: (선택사항)
   ```bash
   docker build -t pykiwoom-api .
   docker run -p 5000:5000 -e KIWOOM_APPKEY=... pykiwoom-api
   ```
4. **클라우드 배포**: AWS, Azure, GCP 등

---

## 💬 피드백 및 지원

문제가 발생하거나 기능 요청이 있으면 GitHub Issues에 등록하세요:
- **GitHub**: https://github.com/unohee/pykiwoom-rest/issues

---

## 📝 버전 정보

- **PyKiwoom-REST**: 2.1.0
- **Swagger UI**: 최신 버전
- **Python 요구사항**: 3.8+

---

**최종 업데이트**: 2025-10-21
**작성자**: PyKiwoom-REST Team
**상태**: ✅ Ready for Production
