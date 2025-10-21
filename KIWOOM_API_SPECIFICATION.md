# 키움증권 REST API 완전 명세서

> **최종 업데이트**: 2025-10-21  
> **생성방식**: pykiwoom.xlsx 파일 자동 파싱  
> **총 API 수**: 206개

## 📊 문서 개요

이 문서는 키움증권 REST API의 모든 엔드포인트를 정리한 완전한 명세입니다.

### 기본 정보

- **운영 서버**: https://api.kiwoom.com
- **모의 서버**: https://mockapi.kiwoom.com (KRX 상품만 지원)
- **인증**: OAuth2 Bearer Token
- **Rate Limit**: 초당 20회 요청 제한

### 공통 Header

```
Content-Type: application/json;charset=UTF-8
Authorization: Bearer {access_token}
```

## 🎯 주요 API 가이드

### 📈 Stock API (주식 시세)

| API명 | ID | URL |
|-------|-----|-----|
| 주식기본정보요청 | ka10001 | /api/dostk/stkinfo |
| 주식호가요청 | ka10004 | /api/dostk/orderbook |
| 주식외국인종목별매매동향 | ka10008 | /api/dostk/foreign |

### 📊 Chart API (차트 데이터)

| API명 | ID | URL |
|-------|-----|-----|
| 주식분봉차트조회 | ka10080 | /api/dostk/minutechart |
| 주식일봉차트조회 | ka10081 | /api/dostk/dailychart |
| 주식주봉차트조회 | ka10082 | /api/dostk/weeklychart |
| 주식월봉차트조회 | ka10083 | /api/dostk/monthlychart |

### 🏆 Ranking API (순위)

| API명 | ID | URL |
|-------|-----|-----|
| 당일거래량상위 | ka10030 | /api/dostk/volume-ranking |
| 전일거래량상위 | ka10031 | /api/dostk/prev-volume |
| 거래대금상위 | ka10032 | /api/dostk/amount-ranking |

### 💼 Account API (계좌)

| API명 | ID | URL |
|-------|-----|-----|
| 예수금상세현황 | kt00001 | /api/tradeAccount/balance |
| 계좌평가현황 | kt00004 | /api/tradeAccount/evaluation |
| 체결잔고 | kt00005 | /api/tradeAccount/settlement |
| 주문체결현황 | kt00009 | /api/tradeAccount/orderStatus |

### 📋 Order API (주문)

| API명 | ID | URL |
|-------|-----|-----|
| 주식 매수주문 | kt10000 | /api/tradeOrder/buy |
| 주식 매도주문 | kt10001 | /api/tradeOrder/sell |
| 주식 정정주문 | kt10002 | /api/tradeOrder/modify |
| 주식 취소주문 | kt10003 | /api/tradeOrder/cancel |

---

## 📚 전체 API 목록


### 1. ELW 이론가

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 실시간시세 | /api/dostk/websocket |

### 2. ELW 지표

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 실시간시세 | /api/dostk/websocket |

### 3. ELWLP보유일별추이요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | ELW | /api/dostk/elw |

### 4. ELW가격급등락요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | ELW | /api/dostk/elw |

### 5. ELW괴리율요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | ELW | /api/dostk/elw |

### 6. ELW근접율요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | ELW | /api/dostk/elw |

### 7. ELW등락율순위요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | ELW | /api/dostk/elw |

### 8. ELW민감도지표요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | ELW | /api/dostk/elw |

### 9. ELW일별민감도지표요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | ELW | /api/dostk/elw |

### 10. ELW잔량순위요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | ELW | /api/dostk/elw |

### 11. ELW조건검색요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | ELW | /api/dostk/elw |

### 12. ELW종목상세정보요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | ELW | /api/dostk/elw |

### 13. ETF NAV

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 실시간시세 | /api/dostk/websocket |

### 14. ETF수익율요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | ETF | /api/dostk/etf |

### 15. ETF시간대별체결요청

**API 수: 2개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | ETF | /api/dostk/etf |
| 국내주식 | ETF | /api/dostk/etf |

### 16. ETF시간대별추이요청

**API 수: 2개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | ETF | /api/dostk/etf |
| 국내주식 | ETF | /api/dostk/etf |

### 17. ETF일별추이요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | ETF | /api/dostk/etf |

### 18. ETF일자별체결요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | ETF | /api/dostk/etf |

### 19. ETF전체시세요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | ETF | /api/dostk/etf |

### 20. ETF종목정보요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | ETF | /api/dostk/etf |

### 21. VI발동/해제

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 실시간시세 | /api/dostk/websocket |

### 22. 가격급등락요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 23. 거래대금상위요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 순위정보 | /api/dostk/rkinfo |

### 24. 거래량갱신요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 25. 거래량급증요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 순위정보 | /api/dostk/rkinfo |

### 26. 거래원매물대분석요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 27. 거래원별ELW순매매상위요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | ELW | /api/dostk/elw |

### 28. 거래원순간거래량요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 29. 계좌별당일현황요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 30. 계좌별익일결제예정내역요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 31. 계좌별주문체결내역상세요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 32. 계좌별주문체결현황요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 33. 계좌수익률요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 34. 계좌평가잔고내역요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 35. 계좌평가현황요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 36. 고저PER요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 37. 고저가근접요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 38. 공매도추이요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 공매도 | /api/dostk/shsa |

### 39. 관심종목정보요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 40. 국제금환산가격

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 실시간시세 | /api/dostk/websocket |

### 41. 금현물 거래내역조회

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 42. 금현물 매도주문

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 주문 | /api/dostk/ordr |

### 43. 금현물 매수주문

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 주문 | /api/dostk/ordr |

### 44. 금현물 미체결조회

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 45. 금현물 시세정보

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 46. 금현물 예수금

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 47. 금현물 잔고확인

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 48. 금현물 정정주문

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 주문 | /api/dostk/ordr |

### 49. 금현물 주문체결전체조회

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 50. 금현물 주문체결조회

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 51. 금현물 취소주문

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 주문 | /api/dostk/ordr |

### 52. 금현물 호가

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 53. 금현물당일분봉차트조회요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 차트 | /api/dostk/chart |

### 54. 금현물당일틱차트조회요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 차트 | /api/dostk/chart |

### 55. 금현물분봉차트조회요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 차트 | /api/dostk/chart |

### 56. 금현물예상체결

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 57. 금현물월봉차트조회요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 차트 | /api/dostk/chart |

### 58. 금현물일별추이

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 59. 금현물일봉차트조회요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 차트 | /api/dostk/chart |

### 60. 금현물주봉차트조회요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 차트 | /api/dostk/chart |

### 61. 금현물체결추이

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 62. 금현물투자자현황

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 기관/외국인 | /api/dostk/frgnistt |

### 63. 금현물틱차트조회요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 차트 | /api/dostk/chart |

### 64. 기관외국인연속매매현황요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 기관/외국인 | /api/dostk/frgnistt |

### 65. 당일거래량상위요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 순위정보 | /api/dostk/rkinfo |

### 66. 당일매매일지요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 67. 당일상위이탈원요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 순위정보 | /api/dostk/rkinfo |

### 68. 당일실현손익상세요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 69. 당일전일체결량요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 70. 당일전일체결요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 71. 당일주요거래원요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 순위정보 | /api/dostk/rkinfo |

### 72. 대차거래내역요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 대차거래 | /api/dostk/slb |

### 73. 대차거래상위10종목요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 대차거래 | /api/dostk/slb |

### 74. 대차거래추이요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 대차거래 | /api/dostk/slb |

### 75. 대차거래추이요청(종목별)

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 대차거래 | /api/dostk/slb |

### 76. 동일순매매순위요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 순위정보 | /api/dostk/rkinfo |

### 77. 매물대집중요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 78. 미체결 분할주문 상세

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 79. 미체결요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 80. 변동성완화장치발동종목요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 81. 상하한가요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 82. 순매수거래원순위요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 순위정보 | /api/dostk/rkinfo |

### 83. 시가대비등락률요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 84. 시간외단일가등락율순위요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 순위정보 | /api/dostk/rkinfo |

### 85. 시간외단일가요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 86. 시세표성정보요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 87. 신고저가요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 88. 신용 매도주문

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 신용주문 | /api/dostk/crdordr |

### 89. 신용 매수주문

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 신용주문 | /api/dostk/crdordr |

### 90. 신용 정정주문

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 신용주문 | /api/dostk/crdordr |

### 91. 신용 취소주문

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 신용주문 | /api/dostk/crdordr |

### 92. 신용매매동향요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 93. 신용보증금율별주문가능수량조회요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 94. 신용비율상위요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 순위정보 | /api/dostk/rkinfo |

### 95. 신용융자 가능문의

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 96. 신용융자 가능종목요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 97. 신주인수권전체시세요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 98. 실시간종목조회순위

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 99. 업종년봉조회요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 차트 | /api/dostk/chart |

### 100. 업종등락

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 실시간시세 | /api/dostk/websocket |

### 101. 업종별주가요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 업종 | /api/dostk/sect |

### 102. 업종별투자자순매수요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 업종 | /api/dostk/sect |

### 103. 업종분봉조회요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 차트 | /api/dostk/chart |

### 104. 업종월봉조회요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 차트 | /api/dostk/chart |

### 105. 업종일봉조회요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 차트 | /api/dostk/chart |

### 106. 업종주봉조회요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 차트 | /api/dostk/chart |

### 107. 업종지수

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 실시간시세 | /api/dostk/websocket |

### 108. 업종코드 리스트

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 109. 업종틱차트조회요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 차트 | /api/dostk/chart |

### 110. 업종프로그램요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 업종 | /api/dostk/sect |

### 111. 업종현재가요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 업종 | /api/dostk/sect |

### 112. 업종현재가일별요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 업종 | /api/dostk/sect |

### 113. 예상체결등락률상위요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 순위정보 | /api/dostk/rkinfo |

### 114. 예수금상세현황요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 115. 외국계창구매매상위요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 순위정보 | /api/dostk/rkinfo |

### 116. 외국인기관매매상위요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 순위정보 | /api/dostk/rkinfo |

### 117. 외인기간별매매상위요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 순위정보 | /api/dostk/rkinfo |

### 118. 외인연속순매매상위요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 순위정보 | /api/dostk/rkinfo |

### 119. 외인한도소진율증가상위

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 순위정보 | /api/dostk/rkinfo |

### 120. 위탁종합거래내역요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 121. 일별거래상세요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 122. 일별계좌수익률상세현황요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 123. 일별기관매매종목요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 124. 일별잔고수익률

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 125. 일별주가요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 126. 일별추정예탁자산현황요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 127. 일자별실현손익요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 128. 일자별종목별실현손익요청_기간

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 129. 일자별종목별실현손익요청_일자

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 130. 잔고

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 실시간시세 | /api/dostk/websocket |

### 131. 잔량율급증요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 순위정보 | /api/dostk/rkinfo |

### 132. 장마감후투자자별매매요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 133. 장시작시간

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 실시간시세 | /api/dostk/websocket |

### 134. 장중투자자별매매상위요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 순위정보 | /api/dostk/rkinfo |

### 135. 장중투자자별매매요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 136. 장중투자자별매매차트요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 차트 | /api/dostk/chart |

### 137. 전업종지수요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 업종 | /api/dostk/sect |

### 138. 전일거래량상위요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 순위정보 | /api/dostk/rkinfo |

### 139. 전일대비등락률상위요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 순위정보 | /api/dostk/rkinfo |

### 140. 접근토큰 발급

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| OAuth 인증 | 접근토큰발급 | /oauth2/token |

### 141. 접근토큰폐기

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| OAuth 인증 | 접근토큰폐기 | /oauth2/revoke |

### 142. 조건검색 목록조회

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 조건검색 | /api/dostk/websocket |

### 143. 조건검색 실시간 해제

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 조건검색 | /api/dostk/websocket |

### 144. 조건검색 요청 실시간

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 조건검색 | /api/dostk/websocket |

### 145. 조건검색 요청 일반

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 조건검색 | /api/dostk/websocket |

### 146. 종목별기관매매추이요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 147. 종목별증권사순위요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 순위정보 | /api/dostk/rkinfo |

### 148. 종목별투자자기관별요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 149. 종목별투자자기관별차트요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 차트 | /api/dostk/chart |

### 150. 종목별투자자기관별합계요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 151. 종목별프로그램매매현황요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 152. 종목시간별프로그램매매추이요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 153. 종목일별프로그램매매추이요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 154. 종목정보 리스트

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 155. 종목정보 조회

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 156. 종목프로그램매매

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 실시간시세 | /api/dostk/websocket |

### 157. 주문인출가능금액요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 158. 주문체결

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 실시간시세 | /api/dostk/websocket |

### 159. 주식 매도주문

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 주문 | /api/dostk/ordr |

### 160. 주식 매수주문

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 주문 | /api/dostk/ordr |

### 161. 주식 정정주문

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 주문 | /api/dostk/ordr |

### 162. 주식 취소주문

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 주문 | /api/dostk/ordr |

### 163. 주식거래원요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 164. 주식기관요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 기관/외국인 | /api/dostk/frgnistt |

### 165. 주식기본정보요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 166. 주식기세

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 실시간시세 | /api/dostk/websocket |

### 167. 주식년봉차트조회요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 차트 | /api/dostk/chart |

### 168. 주식당일거래원

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 실시간시세 | /api/dostk/websocket |

### 169. 주식분봉차트조회요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 차트 | /api/dostk/chart |

### 170. 주식시간외호가

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 실시간시세 | /api/dostk/websocket |

### 171. 주식시분요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 172. 주식예상체결

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 실시간시세 | /api/dostk/websocket |

### 173. 주식외국인종목별매매동향

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 기관/외국인 | /api/dostk/frgnistt |

### 174. 주식우선호가

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 실시간시세 | /api/dostk/websocket |

### 175. 주식월봉차트조회요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 차트 | /api/dostk/chart |

### 176. 주식일봉차트조회요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 차트 | /api/dostk/chart |

### 177. 주식일주월시분요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 178. 주식종목정보

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 실시간시세 | /api/dostk/websocket |

### 179. 주식주봉차트조회요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 차트 | /api/dostk/chart |

### 180. 주식체결

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 실시간시세 | /api/dostk/websocket |

### 181. 주식틱차트조회요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 차트 | /api/dostk/chart |

### 182. 주식호가요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 183. 주식호가잔량

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 실시간시세 | /api/dostk/websocket |

### 184. 증거금세부내역조회요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 185. 증거금율별주문가능수량조회요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 186. 증권사별매매상위요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 순위정보 | /api/dostk/rkinfo |

### 187. 증권사별종목매매동향요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 188. 체결강도추이시간별요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 189. 체결강도추이일별요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 190. 체결요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 191. 체결잔고요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 192. 체결정보요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 193. 추정자산조회요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 계좌 | /api/dostk/acnt |

### 194. 테마구성종목요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 테마 | /api/dostk/thme |

### 195. 테마그룹별요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 테마 | /api/dostk/thme |

### 196. 투자자별일별매매종목요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 197. 프로그램매매누적추이요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 198. 프로그램매매차익잔고추이요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 199. 프로그램매매추이요청 시간대별

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 200. 프로그램매매추이요청 일자별

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 시세 | /api/dostk/mrkcond |

### 201. 프로그램순매수상위50요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |

### 202. 호가잔량급증요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 순위정보 | /api/dostk/rkinfo |

### 203. 호가잔량상위요청

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 순위정보 | /api/dostk/rkinfo |

### 204. 회원사 리스트

**API 수: 1개**

| API명 | ID | URL |
|-------|-----|-----|
| 국내주식 | 종목정보 | /api/dostk/stkinfo |
