# PyKiwoom-REST 리팩토링 PRD

## 배경

코드 품질 분석 결과 LOC 제한(1000줄) 초과 파일 발견:
- `stock_api.py`: 1150줄 (초과)
- `kiwoom_rest.py`: 1138줄 (초과)
- `ranking_api.py`: 942줄 (경고)

## 목표

1. 모든 파일 1000줄 이하 유지
2. 단일 책임 원칙(SRP) 준수
3. 기존 API 호환성 100% 유지
4. 테스트 통과율 유지

---

## Task 1: stock_api.py 분할 (1150줄 → 3개 파일)

### 현재 구조
- 기본 시세: `get_stock_price`, `get_stock_orderbook`, `get_stock_quote` 등
- 투자자 매매: `get_foreign_trading`, `get_institutional_*`, `get_stock_investor_*`
- 프로그램 매매: `get_program_*`, `get_pbar_*`
- 기타: `get_credit_trend`, `get_member_company_list` 등

### 분할 계획
1. `stock_api.py` (400줄): 기본 시세, 호가, 재무
2. `investor_api.py` (400줄): 외국인/기관 매매동향
3. `program_api.py` (350줄): 프로그램 매매, 매물대 분석

### 검증
- 기존 import 경로 유지 (`from pykiwoom_rest import StockAPI`)
- `__init__.py`에서 통합 export
- 테스트 전체 통과

---

## Task 2: kiwoom_rest.py Facade 최적화 (1138줄 → 800줄)

### 현재 문제
- 각 메서드에 중복 docstring
- 단순 위임인데 코드량 과다

### 최적화 방안
1. docstring 간소화 (원본 API 참조 유도)
2. 그룹별 메서드 정리
3. 불필요한 줄바꿈/공백 제거
4. 동적 위임 패턴 고려 (선택사항)

### 검증
- 모든 public API 동작 확인
- 테스트 통과

---

## Task 3: ranking_api.py 정리 (942줄 → 800줄)

### 최적화 방안
1. 중복 패턴 추출 (공통 랭킹 요청 헬퍼)
2. docstring 간소화
3. 유사 메서드 그룹화

---

## Task 4: 테스트 및 CI/CD 검증

1. 전체 테스트 실행 (`pytest tests/ -v`)
2. 타입 체크 (`mypy src/pykiwoom_rest`)
3. 린트 검사 (`ruff check src/pykiwoom_rest`)
4. LOC 게이트 통과 확인
5. PR #10 머지 후 main 브랜치 검증

---

## 우선순위

| Task | 우선순위 | 예상 영향도 |
|------|---------|------------|
| Task 1 | High | stock_api 1000줄 초과 해결 |
| Task 2 | High | kiwoom_rest 1000줄 초과 해결 |
| Task 3 | Medium | 경고 수준이나 개선 권장 |
| Task 4 | High | 모든 변경 검증 |

## 제약사항

- 기존 API 시그니처 변경 금지
- `from pykiwoom_rest import *` 호환성 유지
- MCP 서버 연동 정상 동작 확인
