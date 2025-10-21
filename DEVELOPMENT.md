# Development Guide

PyKiwoom-Rest v2.0 개발 가이드입니다.

## 🛠️ 개발 환경 설정

### 1. 저장소 클론
```bash
git clone <repository-url>
cd pykiwoom-rest
```

### 2. 가상환경 생성 및 활성화
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### 3. 개발 의존성 설치
```bash
pip install -e ".[dev]"
```

## 📋 개발 워크플로우

### 코드 품질 관리

#### Ruff를 사용한 린팅 및 포맷팅

**자동 포맷팅 적용:**
```bash
./scripts/format.sh
# or
ruff format src/pykiwoom_rest/ tests/
ruff check src/pykiwoom_rest/ tests/ --fix
```

**린팅 검사:**
```bash
./scripts/lint.sh
# or
ruff check src/pykiwoom_rest/ tests/
```

### 테스트 실행

**기본 테스트:**
```bash
./scripts/test.sh
# or
pytest tests/ -v
```

**커버리지 포함 테스트:**
```bash
pytest tests/ --cov=src/pykiwoom_rest --cov-report=html
open htmlcov/index.html  # 커버리지 리포트 확인
```

**특정 테스트만 실행:**
```bash
pytest tests/test_basic_functionality.py -v
pytest tests/ -k "test_rate_limiter" -v
```

### 타입 체킹

```bash
mypy src/pykiwoom_rest --ignore-missing-imports
```

## 🏗️ 프로젝트 구조

```
pykiwoom-rest/
├── src/pykiwoom_rest/          # 메인 패키지
│   ├── __init__.py            # 패키지 초기화
│   ├── base_api.py            # Rate limiter 및 기본 API
│   ├── kiwoom_rest.py         # 통합 API wrapper
│   ├── stock_api.py           # 주식 시세 API
│   ├── chart_api.py           # 차트 데이터 API
│   └── ...                    # 기타 API 모듈
├── tests/                     # 테스트 코드
├── scripts/                   # 개발 스크립트
│   ├── lint.sh               # 린팅 검사
│   ├── format.sh             # 코드 포맷팅
│   └── test.sh               # 테스트 실행
├── .github/workflows/         # CI/CD 설정
│   └── ci.yml                # GitHub Actions CI
├── pyproject.toml            # 프로젝트 설정
└── README.md                 # 프로젝트 문서
```

## 🔧 코드 스타일 가이드

### Ruff 설정 (pyproject.toml)

```toml
[tool.ruff]
line-length = 100
target-version = "py38"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "N", "UP", "B", "C4", "SIM"]
ignore = ["E501", "E722", "B007", "B008", "B904", "SIM102", "SIM105"]
```

### 주요 규칙:
- 최대 줄 길이: 100자
- Import 정렬: isort 호환 (알파벳순)
- Type hints 사용 권장
- Docstring 필수 (공개 함수/클래스)

## 🚀 CI/CD 파이프라인

### GitHub Actions 워크플로우

`.github/workflows/ci.yml` 파일에 정의된 CI 파이프라인:

1. **Linting** (Python 3.12)
   - Ruff linter 검사
   - Ruff formatter 검사

2. **Testing** (Python 3.8, 3.10, 3.12)
   - Unit tests 실행
   - Coverage 리포트 생성
   - Codecov 업로드

3. **Type Checking** (Python 3.12)
   - mypy 타입 체크

### 로컬에서 CI 시뮬레이션

```bash
# 1. 린팅
./scripts/lint.sh

# 2. 테스트
./scripts/test.sh

# 3. 타입 체크
mypy src/pykiwoom_rest --ignore-missing-imports
```

## 📝 커밋 메시지 규칙

```
<type>: <subject>

<body>
```

**Type:**
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `style`: 코드 포맷팅
- `refactor`: 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드/설정 변경

**Example:**
```
feat: Add rate limiting optimization

- Implement token bucket algorithm
- Add comprehensive rate limit tests
- Update documentation
```

## 🐛 디버깅 팁

### 환경변수 설정 확인
```bash
# .env 파일이 올바르게 설정되었는지 확인
cat .env

# 필수 환경변수
ACCOUNT_NO=...
KIWOOM_APPKEY=...
KIWOOM_APPSECRET=...
```

### 로깅 활성화
```python
import logging
logging.basicConfig(level=logging.DEBUG)

from pykiwoom_rest import KiwoomRest
kiwoom = KiwoomRest()
```

### Rate Limiting 디버깅
```python
# Rate limiter 통계 확인
stats = kiwoom.base_api.rate_limiter.get_stats()
print(stats)
```

## 📦 배포 프로세스

### 1. 버전 업데이트
```bash
# pyproject.toml에서 버전 변경
version = "2.1.0"
```

### 2. CHANGELOG 업데이트
```bash
# CHANGELOG.md에 변경사항 기록
## [2.1.0] - 2025-01-XX
### Added
- New feature...
```

### 3. 빌드 및 배포
```bash
# 빌드
python -m build

# PyPI 업로드 (테스트)
twine upload --repository testpypi dist/*

# PyPI 업로드 (프로덕션)
twine upload dist/*
```

## 🤝 기여 가이드

1. Fork 저장소
2. Feature 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'feat: Add amazing feature'`)
4. 브랜치 푸시 (`git push origin feature/amazing-feature`)
5. Pull Request 생성

### PR 체크리스트:
- [ ] 코드가 Ruff 린팅을 통과함
- [ ] 새로운 기능에 대한 테스트 추가
- [ ] 문서 업데이트 (필요시)
- [ ] CHANGELOG 업데이트
- [ ] CI/CD 파이프라인 통과

## 📚 추가 리소스

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [pytest Documentation](https://docs.pytest.org/)
- [Kiwoom API Specification](./KIWOOM_API_SPECIFICATION.md)
- [Project README](./README.md)
