# OAuth 인증 API (정확한 사양)

Kiwoom REST API OAuth2 인증 - 실제 명세서 기반

## 접근토큰 발급 (au10001)

### 기본 정보
- **URL**: `/oauth2/token`
- **Method**: `POST`
- **Content-Type**: `application/x-www-form-urlencoded`

### 요청 파라미터
```
grant_type=client_credentials
appkey={APP_KEY}
appsecret={APP_SECRET}
```

### 응답 (실제 형식)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "scope": "READ",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

## 접근토큰폐기 (au10002)

### 기본 정보
- **URL**: `/oauth2/revoke`
- **Method**: `POST`
- **Authorization**: `Bearer {access_token}`
- **Content-Type**: `application/x-www-form-urlencoded`

### 요청 파라미터
```
appkey={APP_KEY}
appsecret={APP_SECRET}
token={access_token}
```
