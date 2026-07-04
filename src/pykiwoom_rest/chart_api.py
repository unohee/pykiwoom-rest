"""
Chart Data API
차트 데이터 관련 API 클래스
작성일: 2025-01-27
"""

from datetime import datetime
from typing import Any, Dict

from .kiwoom_base import KiwoomAPIBase


class ChartAPI(KiwoomAPIBase):
    """차트 데이터 관련 API"""

    # TR 코드 매핑
    TR_CODES = {
        "daily_weekly_monthly_minute": "ka10005",  # 주식일주월시분요청 (통합 차트)
        "tick_chart": "ka10079",
        "minute_chart": "ka10080",
        "daily_chart": "ka10081",
        "weekly_chart": "ka10082",
        "monthly_chart": "ka10083",
        "yearly_chart": "ka10094",
    }

    @staticmethod
    def _record_date(record: Dict[str, Any], key: str) -> str:
        value = str(record.get(key, ""))
        return value[:8] if len(value) >= 8 else ""

    @classmethod
    def _date_in_range(
        cls,
        record: Dict[str, Any],
        date_key: str,
        start_date: str = None,
        end_date: str = None,
    ) -> bool:
        record_date = cls._record_date(record, date_key)
        if not record_date:
            return not (start_date or end_date)
        if start_date and record_date < start_date:
            return False
        return not (end_date and record_date > end_date)

    @classmethod
    def _filter_chart_response(
        cls,
        result: Dict[str, Any],
        date_key: str,
        start_date: str = None,
        end_date: str = None,
    ) -> Dict[str, Any]:
        if not (start_date or end_date) or not isinstance(result, dict):
            return result

        filtered = dict(result)
        for key, value in result.items():
            if isinstance(value, list):
                filtered[key] = [
                    record
                    for record in value
                    if isinstance(record, dict)
                    and cls._date_in_range(record, date_key, start_date, end_date)
                ]
        return filtered

    def get_tick_chart(self, stock_code: str, count: int = 100) -> Dict[str, Any]:
        """
        주식 틱 차트 조회 (ka10079)

        Args:
            stock_code: 종목코드
            count: 호환성 인자. Kiwoom ka10079 요청 body에는 포함하지 않음.

        Returns:
            틱 차트 데이터
        """
        params = {
            "stk_cd": stock_code,
            "tic_scope": "1",
            "upd_stkpc_tp": "1",
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES["tick_chart"],
            endpoint="chart",
            data=params,
            method="POST",
        )

    def get_minute_chart(
        self,
        stock_code: str,
        interval: int = 1,
        start_date: str = None,
        end_date: str = None,
        count: int = 100,
    ) -> Dict[str, Any]:
        """
        주식 분봉 차트 조회 (ka10080)

        Args:
            stock_code: 종목코드
            interval: 분봉 간격 (1, 3, 5, 10, 15, 30, 60)
            start_date: 호환성 인자. Kiwoom ka10080 요청 body에는 포함하지 않음.
            end_date: 호환성 인자. Kiwoom ka10080 요청 body에는 포함하지 않음.
            count: 호환성 인자. Kiwoom ka10080 요청 body에는 포함하지 않음.

        Returns:
            분봉 차트 데이터
        """
        if start_date or end_date:
            return self.get_minute_chart_paginated(
                stock_code=stock_code,
                interval=interval,
                start_date=start_date,
                end_date=end_date,
                max_records=count,
            )

        data = {
            "stk_cd": stock_code,
            "tic_scope": str(interval),
            "upd_stkpc_tp": "1",
        }

        return self.make_tr_request(
            tr_code=self.TR_CODES["minute_chart"],
            endpoint="chart",
            data=data,
            method="POST",
        )

    def get_daily_chart(
        self,
        stock_code: str,
        start_date: str = None,
        end_date: str = None,
        count: int = 100,
    ) -> Dict[str, Any]:
        """
        주식 일봉 차트 조회 (ka10081)

        Args:
            stock_code: 종목코드
            start_date: 호환성 인자. Kiwoom ka10081 요청 body에는 포함하지 않음.
            end_date: 종료일 (YYYYMMDD)
            count: 호환성 인자. Kiwoom ka10081 요청 body에는 포함하지 않음.

        Returns:
            일봉 차트 데이터
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")

        data = {
            "stk_cd": stock_code,
            "base_dt": end_date,
            "upd_stkpc_tp": "1",
        }

        result = self.make_tr_request(
            tr_code=self.TR_CODES["daily_chart"],
            endpoint="chart",
            data=data,
            method="POST",
        )
        return self._filter_chart_response(result, "dt", start_date, end_date)

    def get_weekly_chart(
        self,
        stock_code: str,
        start_date: str = None,
        end_date: str = None,
        count: int = 100,
    ) -> Dict[str, Any]:
        """
        주식 주봉 차트 조회 (ka10082)

        Args:
            stock_code: 종목코드
            start_date: 시작일 (YYYYMMDD)
            end_date: 종료일 (YYYYMMDD)
            count: 조회 개수

        Returns:
            주봉 차트 데이터
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")

        params = {
            "stk_cd": stock_code,
            "base_dt": end_date,
            "upd_stkpc_tp": "1",
        }
        result = self.make_tr_request(
            tr_code=self.TR_CODES["weekly_chart"],
            endpoint="chart",
            data=params,
            method="POST",
        )
        return self._filter_chart_response(result, "dt", start_date, end_date)

    def get_monthly_chart(
        self,
        stock_code: str,
        start_date: str = None,
        end_date: str = None,
        count: int = 100,
    ) -> Dict[str, Any]:
        """
        주식 월봉 차트 조회 (ka10083)

        Args:
            stock_code: 종목코드
            start_date: 호환성 인자. Kiwoom ka10083 요청 body에는 포함하지 않음.
            end_date: 종료일 (YYYYMMDD)
            count: 호환성 인자. 서버 요청 body에는 포함하지 않음.

        Returns:
            월봉 차트 데이터
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")

        params = {
            "stk_cd": stock_code,
            "base_dt": end_date,
            "upd_stkpc_tp": "1",
        }
        result = self.make_tr_request(
            tr_code=self.TR_CODES["monthly_chart"],
            endpoint="chart",
            data=params,
            method="POST",
        )
        return self._filter_chart_response(result, "dt", start_date, end_date)

    def get_yearly_chart(
        self,
        stock_code: str,
        start_date: str = None,
        end_date: str = None,
        count: int = 100,
    ) -> Dict[str, Any]:
        """
        주식 년봉 차트 조회 (ka10094)

        Args:
            stock_code: 종목코드
            start_date: 호환성 인자. Kiwoom ka10094 요청 body에는 포함하지 않음.
            end_date: 종료일 (YYYYMMDD)
            count: 호환성 인자. 서버 요청 body에는 포함하지 않음.

        Returns:
            년봉 차트 데이터
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")

        params = {
            "stk_cd": stock_code,
            "base_dt": end_date,
            "upd_stkpc_tp": "1",
        }
        result = self.make_tr_request(
            tr_code=self.TR_CODES["yearly_chart"],
            endpoint="chart",
            data=params,
            method="POST",
        )
        return self._filter_chart_response(result, "dt", start_date, end_date)

    def get_minute_chart_paginated(
        self,
        stock_code: str,
        interval: int = 1,
        start_date: str = None,
        end_date: str = None,
        max_records: int = 1000,
    ) -> Dict[str, Any]:
        """
        분봉 차트 대량 조회 (페이지네이션)

        Args:
            stock_code: 종목코드
            interval: 분봉 간격
            start_date: 시작일
            end_date: 종료일
            max_records: 최대 조회 개수

        Returns:
            통합된 분봉 차트 데이터
        """
        all_data = []
        cont_yn = "N"
        next_key = ""
        last_result: Dict[str, Any] = {}

        while len(all_data) < max_records:
            response = self.make_tr_request_continuous(
                tr_code=self.TR_CODES["minute_chart"],
                endpoint="chart",
                data={
                    "stk_cd": stock_code,
                    "tic_scope": str(interval),
                    "upd_stkpc_tp": "1",
                },
                cont_yn=cont_yn,
                next_key=next_key,
            )

            if not response or "data" not in response:
                break

            last_result = response.get("data") or {}
            cont_yn = response.get("cont_yn", "N")
            next_key = response.get("next_key", "")

            # 데이터 추출 - 실제 응답 필드명 사용
            chart_data = last_result.get("stk_min_pole_chart_qry", [])
            if not chart_data:
                # output2 필드 체크 (호환성)
                chart_data = last_result.get("output2", [])
                if not chart_data:
                    break

            for record in chart_data:
                record_date = self._record_date(record, "cntr_tm")
                if end_date and record_date and record_date > end_date:
                    continue
                if start_date and record_date and record_date < start_date:
                    cont_yn = "N"
                    break
                all_data.append(record)
                if len(all_data) >= max_records:
                    break

            if cont_yn != "Y" or not next_key:
                break

        # 결과 구성 - output2로 통일하여 반환 (하위 호환성)
        result = dict(last_result)
        if all_data:
            trimmed = all_data[:max_records]
            result["stk_min_pole_chart_qry"] = trimmed
            result["output2"] = trimmed
            result["total_records"] = len(all_data)

        return result

    def get_minute_chart_with_date(
        self,
        stock_code: str,
        interval: int = 5,
        target_date: str = None,
        max_pages: int = 20,
    ) -> Dict[str, Any]:
        """특정 날짜의 분봉 데이터 조회 (연속조회 사용)

        Args:
            stock_code: 종목코드
            interval: 분봉 간격 (1, 3, 5, 10, 15, 30, 60)
            target_date: 대상 날짜 (YYYYMMDD)
            max_pages: 최대 연속조회 페이지 수

        Returns:
            대상 날짜의 분봉 데이터
        """
        all_data = []
        target_data = []
        cont_yn = "N"
        next_key = ""

        for page in range(max_pages):  # noqa: B007 (used after loop)
            # 연속조회 실행
            response = self.make_tr_request_continuous(
                tr_code=self.TR_CODES["minute_chart"],
                endpoint="chart",
                data={
                    "stk_cd": stock_code,
                    "tic_scope": str(interval),
                    "upd_stkpc_tp": "1",
                },
                cont_yn=cont_yn,
                next_key=next_key,
            )

            if not response or "data" not in response:
                break

            result_data = response["data"]
            cont_yn = response.get("cont_yn", "N")
            next_key = response.get("next_key", "")

            # 분봉 데이터 추출
            chart_data = result_data.get("stk_min_pole_chart_qry", [])
            if not chart_data:
                break

            # 대상 날짜 데이터 필터링
            if target_date:
                found_target = False
                for record in chart_data:
                    time_str = record.get("cntr_tm", "")
                    if len(time_str) >= 8:
                        record_date = time_str[:8]
                        if record_date == target_date:
                            target_data.append(record)
                            found_target = True
                        elif record_date < target_date:
                            # 대상 날짜를 지나쳤음
                            cont_yn = "N"
                            break

                # 대상 날짜 발견 시 계속 수집
                if found_target and cont_yn == "Y":
                    continue

                # 대상 날짜를 완전히 지나친 경우 중단
                last_time = chart_data[-1].get("cntr_tm", "") if chart_data else ""
                if len(last_time) >= 8 and last_time[:8] < target_date:
                    break
            else:
                all_data.extend(chart_data)

            # 연속조회 불가능 시 중단
            if cont_yn != "Y" or not next_key:
                break

        # 최종 데이터 정리
        final_data = target_data if target_date else all_data
        final_data.sort(key=lambda x: x.get("cntr_tm", ""))

        # 날짜 범위 계산
        date_range = None
        if final_data:
            first_time = final_data[0].get("cntr_tm", "")
            last_time = final_data[-1].get("cntr_tm", "")
            if len(first_time) >= 8 and len(last_time) >= 8:
                date_range = {
                    "start": first_time[:8],
                    "end": last_time[:8],
                    "start_time": first_time,
                    "end_time": last_time,
                }

        return {
            "success": len(final_data) > 0,
            "data": final_data,
            "output2": final_data,  # 하위 호환성
            "total": len(final_data),
            "target_date": target_date,
            "date_range": date_range,
            "pages": page + 1,
        }

    def get_daily_weekly_monthly_minute_chart(
        self,
        stock_code: str,
        period: str = "D",
        start_date: str = None,
        end_date: str = None,
        interval: int = 1,
    ) -> Dict[str, Any]:
        """
        주식 일/주/월/시분 통합 차트 조회 (ka10005)

        Args:
            stock_code: 종목코드
            period: 기간 구분
                - "D": 일봉 (기본값)
                - "W": 주봉
                - "M": 월봉
                - "T": 분봉
            start_date: 시작일 (YYYYMMDD, 선택사항)
            end_date: 종료일 (YYYYMMDD, 선택사항)
            interval: 분봉 간격 (period="T"일 때만 사용, 1/3/5/10/15/30/45/60)

        Returns:
            Dict[str, Any]: 차트 데이터
            - Response Body: stk_ddwkmm (LIST)
                - date: 날짜
                - open_pric: 시가
                - high_pric: 고가
                - low_pric: 저가
                - close_pric: 종가
                - volume: 거래량

        Note:
            **페이지네이션 지원**: 이 API는 연속조회를 지원합니다.

            - Response Header의 `cont-yn`이 "Y"인 경우 다음 데이터가 존재
            - 다음 페이지 조회 시 Request Header에 다음 값을 설정:
                - `cont-yn`: Response Header의 `cont-yn` 값
                - `next-key`: Response Header의 `next-key` 값

            대량 데이터 조회 시 페이지네이션을 활용하여 여러 번 호출해야 합니다.

            **참고**: 이 TR 코드는 이전에 stock_api.py에서 잘못 사용되었습니다.
            ka10005는 차트 데이터 조회 API이며, 투자자 매매동향 조회가 아닙니다.
        """
        # ka10005 Request parameters (from PDF docs)
        params = {
            "stk_cd": stock_code,  # 종목코드 (KRX:039490, NXT:039490_NX, SOR:039490_AL)
        }

        # Optional parameters
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if period:
            params["period"] = period  # D=일, W=주, M=월, T=분
        if period == "T" and interval:
            params["interval"] = str(interval)

        return self.make_tr_request(
            tr_code=self.TR_CODES["daily_weekly_monthly_minute"],
            endpoint="mrkcond",  # ka10005 uses /api/dostk/mrkcond endpoint
            data=params,
            method="POST",
        )
