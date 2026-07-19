# 업종 차트 API 안내

키움 업종 코드는 요청에 따라 3자리 형식이 필요합니다. 이 라이브러리는 `0001`처럼 4자리로
전달된 코드를 `001`로 정규화합니다. 기준일은 `YYYYMMDD` 형식이며 생략하면 현재 날짜를
사용합니다.

## 제공 메서드

| 메서드 | TR 코드 | 주요 인자 | 설명 |
|---|---|---|---|
| `get_sector_tick_chart` | `ka20004` | `sector_code`, `tick_scope` | 업종 틱 차트 |
| `get_sector_minute_chart` | `ka20005` | `sector_code`, `interval` | 업종 분봉 차트 |
| `get_sector_daily_chart` | `ka20006` | `sector_code`, `base_date` | 업종 일봉 차트 |
| `get_sector_weekly_chart` | `ka20007` | `sector_code`, `base_date` | 업종 주봉 차트 |
| `get_sector_monthly_chart` | `ka20008` | `sector_code`, `base_date` | 업종 월봉 차트 |
| `get_sector_yearly_chart` | `ka20019` | `sector_code`, `base_date` | 업종 년봉 차트 |

분봉 간격은 키움 명세가 허용하는 `1`, `3`, `5`, `10`, `30`만 사용할 수 있습니다.

## 사용 예시

```python
from pykiwoom_rest import KiwoomRest

kiwoom = KiwoomRest()

# KOSPI 업종 5분봉
minute = kiwoom.get_sector_minute_chart("0001", interval=5)

# 기준일 일봉
daily = kiwoom.get_sector_daily_chart("001", base_date="20260717")

# 주봉, 월봉, 년봉
weekly = kiwoom.get_sector_weekly_chart("001")
monthly = kiwoom.get_sector_monthly_chart("001")
yearly = kiwoom.get_sector_yearly_chart("001")
```

## 응답 처리

키움 응답은 메타 필드와 데이터 목록을 함께 포함할 수 있습니다. 정확한 응답 키는 TR별 상세
문서와 실제 응답을 확인하세요. 빈 목록을 성공 데이터로 가정하지 말고 `return_code`,
`return_msg`, 연속 조회 헤더도 확인해야 합니다.

## 오류

- 지원하지 않는 분봉 간격은 API 호출 전에 `ValueError`가 발생합니다.
- 잘못된 업종 코드, 휴장일, 장 운영 시간에는 빈 데이터나 키움 오류가 반환될 수 있습니다.
- 429 응답은 공통 요청 계층의 재시도 정책을 따릅니다.

세부 원문 명세는 [전체 키움 REST API 문서](kiwoom_rest_api_full.md)와
[API 분야별 안내](../api/README.md)를 참고하세요.
