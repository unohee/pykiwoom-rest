# Kiwoom REST API Postman 설정 가이드

## 🚀 설치 및 설정

### 1. Postman Collection 가져오기
1. Postman 실행
2. Import 클릭
3. `Kiwoom_REST_API_Collection.postman_collection.json` 파일 선택
4. Import 완료

### 2. 환경변수 설정
1. Postman에서 Environment 섹션으로 이동
2. `Kiwoom_Environment.postman_environment.json` 파일 Import
3. 다음 환경변수 값들을 입력:

```
ACCOUNT_NO=12345678           # 계좌번호
KIWOOM_APPKEY=your_app_key    # 앱키
KIWOOM_APPSECRET=your_secret  # 앱시크릿
```

## 🔐 인증 프로세스

### 1. 토큰 발급
1. **Authentication** 폴더의 **Get Access Token** 요청 실행
2. 자동으로 `access_token` 환경변수에 저장됨
3. 토큰 유효기간: 24시간

### 2. Hashkey 생성 (주문 시 필요)
- 주문 API 호출 시 Pre-request Script에서 자동 생성
- 별도 설정 불필요

## 📊 주요 API 카테고리

### 1. **Stock Quotation (주식 시세)**
- 주식기본정보, 호가, 체결정보 조회
- 예시: 삼성전자(005930) 기본정보

### 2. **Chart Data (차트 데이터)**
- 분봉, 일봉, 주봉, 월봉 차트 조회
- 페이지네이션 지원

### 3. **Account (계좌)**
- 예수금, 잔고, 포트폴리오 조회
- 계좌번호 환경변수 사용

### 4. **Trading (주문)**
- 매수/매도 주문 실행
- Hashkey 자동 생성 기능 내장

### 5. **Ranking & Statistics (순위/통계)**
- 거래량순위, 등락률순위 등
- 시장 분석용 데이터

### 6. **Sector & Market (업종/시장)**
- 업종지수, 시장지수 조회

### 7. **WebSocket Real-time (실시간)**
- 실시간 데이터 연결 정보
- TR 코드 및 연결 예시 제공

## ⚡ Rate Limiting

**제한**: 초당 20회
- Collection 레벨에서 자동 Rate Limiting 구현
- 50ms 간격 자동 조절

## 🛠️ 사용 팁

### 1. 환경변수 활용
```javascript
// 종목코드 동적 설정
pm.environment.set("stock_code", "005930");

// 날짜 자동 생성
const today = new Date().toISOString().slice(0,10).replace(/-/g,'');
pm.environment.set("today", today);
```

### 2. 응답 데이터 처리
```javascript
// 응답 데이터를 환경변수에 저장
const response = pm.response.json();
if (response.output1) {
    pm.environment.set("current_price", response.output1.stck_prpr);
}
```

### 3. 에러 처리
```javascript
// 에러 응답 체크
pm.test("API 호출 성공", function () {
    const response = pm.response.json();
    pm.expect(response.rt_cd).to.equal("0");
});
```

## 🔧 고급 기능

### 1. 배치 테스트
- Collection Runner 사용
- 여러 종목 일괄 조회

### 2. 모니터링 설정
- Postman Monitor로 주기적 API 상태 확인
- 알림 설정

### 3. CI/CD 통합
- Newman CLI 도구 활용
- 자동화된 API 테스트

## 📝 주의사항

1. **장시간 제한**: 일부 API는 장시간(09:00-15:30)에만 작동
2. **토큰 만료**: 24시간마다 토큰 재발급 필요
3. **Rate Limiting**: 초당 20회 제한 준수
4. **데이터 형식**: 모든 날짜는 YYYYMMDD 형식

## 🚨 문제해결

### 토큰 만료 시
```
401 Unauthorized 응답
→ Get Access Token 재실행
```

### Rate Limit 초과 시
```
429 Too Many Requests 응답
→ 잠시 대기 후 재시도
```

### 잘못된 파라미터
```
400 Bad Request 응답  
→ 요청 파라미터 확인
```

## 📞 지원

- **API 문서**: 키움증권 OpenAPI 가이드
- **문의**: 키움증권 고객센터
- **개발자 포럼**: 키움 OpenAPI 커뮤니티

---

**Version**: 1.0.0  
**Last Updated**: 2025-09-05  
**Compatible**: Postman v10+