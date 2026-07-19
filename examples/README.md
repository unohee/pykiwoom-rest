# PyKiwoom-REST 예제

이 디렉터리는 라이브러리 연결 예제와 성능 측정 스크립트를 포함합니다. 실제 API를 호출하는
파일은 유효한 인증 정보와 네트워크가 필요합니다.

## 파일 구성

```text
examples/
├── direct_credential_injection.py       # 생성자에 인증 정보 직접 전달
├── test_new_apis_script.py              # 주요 API 호출 예제
├── test_websocket_connection.py         # WebSocket 연결 예제
├── pykiwoom.ipynb                       # 기본 노트북
├── pykiwoom_comprehensive_test.ipynb    # 종합 노트북
└── performance/
    ├── perf_concurrent_performance.py   # 병렬 처리 측정
    ├── perf_rate_limit_live.py          # 실제 속도 제한 측정
    ├── perf_rate_limit_simple.py        # 단순 속도 제한 측정
    └── test_async_parallel.py           # 비동기 처리 비교
```

## 실행 전 준비

```bash
source ~/dev/mlx_env/bin/activate
pip install -e .

export ACCOUNT_NO=your-account-number
export KIWOOM_APPKEY=your-app-key
export KIWOOM_APPSECRET=your-app-secret
```

`.env`를 사용할 수도 있지만 비밀값을 저장소에 커밋하지 마세요.

## 기본 예제

```bash
python examples/direct_credential_injection.py
python examples/test_new_apis_script.py
```

## 성능 측정

```bash
python examples/performance/perf_rate_limit_simple.py
python examples/performance/perf_rate_limit_live.py
python examples/performance/perf_concurrent_performance.py
python examples/performance/test_async_parallel.py
```

성능 숫자는 컴퓨터, 네트워크, 거래 시간, 키움 API 정책, 인증 정보 수에 따라 달라집니다.
과거 실행값을 현재 보장 처리량으로 해석하지 말고 같은 커밋과 환경에서 다시 측정하세요.

## 주의 사항

- 키움 API의 최신 호출 제한을 직접 확인하세요.
- 실제 계좌 주문은 예제나 성능 측정에서 실행하지 마세요.
- 일부 시세 API는 장 운영 시간에만 유효한 데이터를 반환합니다.
- 429 응답을 성능 향상을 위해 무시하거나 재시도 상한 없이 반복하지 마세요.
- 노트북 출력에 계좌번호와 토큰이 남지 않았는지 커밋 전에 확인하세요.
