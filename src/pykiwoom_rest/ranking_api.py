"""
Ranking Information API
순위 정보 관련 API 클래스
작성일: 2025-01-27
"""

from typing import Any, Dict, List

from .kiwoom_base import KiwoomAPIBase


class RankingAPI(KiwoomAPIBase):
    """순위 정보 관련 API"""

    # TR 코드 매핑
    TR_CODES = {
        "quote_volume_top": "ka10020",
        "quote_volume_surge": "ka10021",
        "volume_rate_surge": "ka10022",
        "trading_volume_surge": "ka10023",
        "previous_day_rate_top": "ka10027",
        "expected_rate_top": "ka10029",
        "daily_volume_top": "ka10030",
        "previous_volume_top": "ka10031",
        "trading_amount_top": "ka10032",
        "credit_ratio_top": "ka10033",
        "foreign_period_trading_top": "ka10034",
        "foreign_continuous_trading_top": "ka10035",
        "foreign_limit_exhaustion_top": "ka10036",
        "foreign_window_trading_top": "ka10037",
        "stock_securities_ranking": "ka10038",
        "securities_trading_top": "ka10039",
        "daily_major_trader": "ka10040",
        "net_buy_trader_ranking": "ka10042",
        "daily_top_departure": "ka10053",
        "same_net_trading_ranking": "ka10062",
        "investor_trading_top": "ka10065",
        "hourly_program_trading": "ka90008",
        "overtime_rate_ranking": "ka10098",
        "foreign_institution_trading_top": "ka90009",
    }

    def _get_market_code(self, market: str) -> str:
        """시장 코드 변환 헬퍼"""
        return {"ALL": "0000", "KOSPI": "0001", "KOSDAQ": "1001"}.get(market, "0000")

    def get_volume_top(self, market: str = "ALL", count: int = 50) -> Dict[str, Any]:
        """
        호가잔량 상위 조회 (ka10020)

        Args:
            market: 시장구분 (ALL, KOSPI, KOSDAQ)
            count: 조회 개수

        Returns:
            호가잔량 상위 목록
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_COND_SCR_DIV_CODE": "20",
            "FID_INPUT_ISCD": self._get_market_code(market),
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_INPUT_CNT_1": str(count),
            "FID_PRC_CLS_CODE": "1",
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES["quote_volume_top"],
            endpoint="ranking",
            data=params,
            method="POST",
        )

    def get_volume_surge(self, market: str = "ALL", count: int = 50) -> Dict[str, Any]:
        """
        호가잔량 급증 조회 (ka10021)

        Args:
            market: 시장구분
            count: 조회 개수

        Returns:
            호가잔량 급증 목록
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_COND_SCR_DIV_CODE": "20",
            "FID_INPUT_ISCD": self._get_market_code(market),
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_INPUT_CNT_1": str(count),
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES["quote_volume_surge"],
            endpoint="ranking",
            data=params,
            method="POST",
        )

    def get_volume_rate_surge(self, market: str = "ALL", count: int = 50) -> Dict[str, Any]:
        """
        거래량 증가율 상위 조회 (ka10022)

        Args:
            market: 시장구분
            count: 조회 개수

        Returns:
            거래량 증가율 상위 목록
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": self._get_market_code(market),
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_INPUT_CNT_1": str(count),
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES["volume_rate_surge"],
            endpoint="ranking",
            data=params,
            method="POST",
        )

    def get_trading_volume_surge(self, market: str = "ALL", count: int = 50) -> Dict[str, Any]:
        """
        거래대금 급증 조회 (ka10023)

        Args:
            market: 시장구분
            count: 조회 개수

        Returns:
            거래대금 급증 목록
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": self._get_market_code(market),
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_INPUT_CNT_1": str(count),
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES["trading_volume_surge"],
            endpoint="ranking",
            data=params,
            method="POST",
        )

    def get_previous_day_rate_top(self, market: str = "ALL", count: int = 50) -> Dict[str, Any]:
        """
        전일 대비 등락률 상위 조회 (ka10027)

        Args:
            market: 시장구분
            count: 조회 개수

        Returns:
            전일 대비 등락률 상위 목록
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": self._get_market_code(market),
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_INPUT_CNT_1": str(count),
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES["previous_day_rate_top"],
            endpoint="ranking",
            data=params,
            method="POST",
        )

    def get_expected_rate_top(self, market: str = "ALL", count: int = 50) -> Dict[str, Any]:
        """
        예상체결 등락률 상위 조회 (ka10029)

        Args:
            market: 시장구분
            count: 조회 개수

        Returns:
            예상체결 등락률 상위 목록
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": self._get_market_code(market),
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_INPUT_CNT_1": str(count),
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES["expected_rate_top"],
            endpoint="ranking",
            data=params,
            method="POST",
        )

    def get_daily_volume_top(self, market: str = "ALL", count: int = 50) -> Dict[str, Any]:
        """
        당일 거래량 상위 조회 (ka10030)

        Args:
            market: 시장구분
            count: 조회 개수

        Returns:
            당일 거래량 상위 목록
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": self._get_market_code(market),
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_INPUT_CNT_1": str(count),
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES["daily_volume_top"],
            endpoint="ranking",
            data=params,
            method="POST",
        )

    def get_trading_amount_top(self, market: str = "ALL", count: int = 50) -> Dict[str, Any]:
        """
        거래대금 상위 조회 (ka10032)

        Args:
            market: 시장구분
            count: 조회 개수

        Returns:
            거래대금 상위 목록
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": self._get_market_code(market),
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_INPUT_CNT_1": str(count),
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES["trading_amount_top"],
            endpoint="ranking",
            data=params,
            method="POST",
        )

    def get_credit_ratio_top(self, market: str = "ALL", count: int = 50) -> Dict[str, Any]:
        """
        신용비율 상위 조회 (ka10033)

        Args:
            market: 시장구분
            count: 조회 개수

        Returns:
            신용비율 상위 목록
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": self._get_market_code(market),
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_INPUT_CNT_1": str(count),
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES["credit_ratio_top"],
            endpoint="ranking",
            data=params,
            method="POST",
        )

    def get_foreign_period_trading_top(
        self, market: str = "ALL", period: str = "1", count: int = 50
    ) -> Dict[str, Any]:
        """
        외인 기간별 매매 상위 조회 (ka10034)

        Args:
            market: 시장구분
            period: 기간 (1:1일, 5:5일, 10:10일)
            count: 조회 개수

        Returns:
            외인 기간별 매매 상위 목록
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": self._get_market_code(market),
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_INPUT_CNT_1": str(count),
            "FID_INPUT_OPTION_1": period,
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES["foreign_period_trading_top"],
            endpoint="ranking",
            data=params,
            method="POST",
        )

    def get_foreign_continuous_trading_top(
        self, market: str = "ALL", count: int = 50
    ) -> Dict[str, Any]:
        """
        외인 연속매매 상위 조회 (ka10035)

        Args:
            market: 시장구분
            count: 조회 개수

        Returns:
            외인 연속매매 상위 목록
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": self._get_market_code(market),
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_INPUT_CNT_1": str(count),
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES["foreign_continuous_trading_top"],
            endpoint="ranking",
            data=params,
            method="POST",
        )

    def get_foreign_limit_exhaustion_top(
        self, market: str = "ALL", count: int = 50
    ) -> Dict[str, Any]:
        """
        외인 한도소진 상위 조회 (ka10036)

        Args:
            market: 시장구분
            count: 조회 개수

        Returns:
            외인 한도소진 상위 목록
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": self._get_market_code(market),
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_INPUT_CNT_1": str(count),
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES["foreign_limit_exhaustion_top"],
            endpoint="ranking",
            data=params,
            method="POST",
        )

    def get_securities_trading_top(self, market: str = "ALL", count: int = 50) -> Dict[str, Any]:
        """
        증권사별 매매 상위 조회 (ka10039)

        Args:
            market: 시장구분
            count: 조회 개수

        Returns:
            증권사별 매매 상위 목록
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": self._get_market_code(market),
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_INPUT_CNT_1": str(count),
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES["securities_trading_top"],
            endpoint="ranking",
            data=params,
            method="POST",
        )

    def get_daily_major_traders(self, stock_code: str) -> Dict[str, Any]:
        """
        당일 주요 거래원 조회 (ka10040)

        Args:
            stock_code: 종목코드

        Returns:
            당일 주요 거래원 정보
        """
        params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": stock_code}
        return self.make_tr_request(
            tr_code=self.TR_CODES["daily_major_trader"],
            endpoint="ranking",
            data=params,
            method="POST",
        )

    def get_net_buy_trader_ranking(self, market: str = "ALL", count: int = 50) -> Dict[str, Any]:
        """
        순매수 거래원 순위 조회 (ka10042)

        Args:
            market: 시장구분
            count: 조회 개수

        Returns:
            순매수 거래원 순위
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": self._get_market_code(market),
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_INPUT_CNT_1": str(count),
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES["net_buy_trader_ranking"],
            endpoint="ranking",
            data=params,
            method="POST",
        )

    def get_investor_trading_top(self, market: str = "ALL", count: int = 50) -> Dict[str, Any]:
        """
        투자자별 거래 상위 조회 (ka10065)

        Args:
            market: 시장구분
            count: 조회 개수

        Returns:
            투자자별 거래 상위 목록
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": self._get_market_code(market),
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_INPUT_CNT_1": str(count),
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES["investor_trading_top"],
            endpoint="ranking",
            data=params,
            method="POST",
        )

    def get_hourly_program_trading(
        self, stock_code: str, date: str, amount_or_quantity: str = "1"
    ) -> Dict[str, Any]:
        """
        종목시간별 프로그램매매 추이요청 (ka90008)

        Args:
            stock_code: 종목코드
            date: 날짜 (YYYYMMDD)
            amount_or_quantity: 금액수량구분 (1:금액, 2:수량)

        Returns:
            종목시간별 프로그램매매 추이 데이터
        """
        params = {"amt_qty_tp": amount_or_quantity, "stk_cd": stock_code, "date": date}
        return self.make_tr_request(
            tr_code=self.TR_CODES["hourly_program_trading"],
            endpoint="mrkcond",
            data=params,
            method="POST",
        )

    def get_hourly_program_trading_paginated(
        self, stock_code: str, date: str, amount_or_quantity: str = "1", max_records: int = None
    ) -> Dict[str, Any]:
        """
        종목시간별 프로그램매매 추이요청 (페이지네이션 지원) (ka90008)

        Args:
            stock_code: 종목코드
            date: 날짜 (YYYYMMDD)
            amount_or_quantity: 금액수량구분 (1:금액, 2:수량)
            max_records: 최대 조회 레코드 수 (None이면 모든 데이터 조회)

        Returns:
            종목시간별 프로그램매매 추이 전체 데이터
        """
        import time

        def _extract_records(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
            """페이지 payload에서 레코드 리스트를 추출 (키 다양성 대응).
            - 우선 'output' 키를 사용
            - 없으면 최상위 dict의 첫 번째 리스트 값을 사용
            - 리스트가 없으면 빈 리스트
            """
            if not isinstance(payload, dict):
                return []
            if "output" in payload:
                value = payload["output"]
                if isinstance(value, list):
                    return value
                if isinstance(value, dict):
                    return [value]
            for _, value in payload.items():
                if isinstance(value, list):
                    return value
            return []

        all_data: List[Dict[str, Any]] = []
        params = {
            "amt_qty_tp": amount_or_quantity,
            "stk_cd": stock_code,
            "date": date,
        }

        # 연속조회는 최초 호출 시 cont_yn='N', next_key=''로 시작
        cont_yn = "N"
        next_key = ""
        records_collected = 0

        # 백오프 파라미터 개선
        sleep_sec = 0.1  # 기본 대기 시간 증가
        retry_count = 0
        max_retries = 3

        while True:
            try:
                res = self.make_tr_request_continuous(
                    tr_code=self.TR_CODES["hourly_program_trading"],
                    endpoint="mrkcond",
                    data=params,
                    cont_yn=cont_yn,
                    next_key=next_key,
                    method="POST",
                )
                retry_count = 0  # 성공 시 재시도 카운트 리셋

            except Exception as e:
                retry_count += 1

                # 429 에러인지 확인
                is_rate_limit = "429" in str(e) or "rate" in str(e).lower()

                if retry_count <= max_retries:
                    # 429 에러면 더 긴 대기, 아니면 기본 대기
                    wait_time = (2.0 if is_rate_limit else 0.5) * retry_count

                    # 조용히 재시도 (429 에러는 로그 레벨 낮춤)
                    if not is_rate_limit:
                        print(f"API 요청 재시도 중... ({retry_count}/{max_retries})")

                    time.sleep(wait_time)
                    continue
                else:
                    # 최대 재시도 초과 시 현재까지 수집된 데이터 반환
                    print(f"최대 재시도 초과. 현재까지 수집된 {len(all_data)}개 데이터 반환")
                    break

            if not res or "data" not in res:
                break

            page_payload = res["data"]
            page_records = _extract_records(page_payload)

            if page_records:
                all_data.extend(page_records)
                records_collected += len(page_records)

            # 응답 헤더에서 연속조회 정보
            cont_yn = res.get("cont_yn", "N")
            next_key = res.get("next_key", "")

            if max_records and records_collected >= max_records:
                all_data = all_data[:max_records]
                break

            if cont_yn != "Y" or not next_key:
                break

            # 429 에러 발생 빈도를 줄이기 위해 대기 시간 증가
            time.sleep(sleep_sec)

        return {
            "msg1": "SUCCESS" if all_data else "NO_DATA",
            "output": all_data,
            "total_records": len(all_data),
        }

    def get_overtime_rate_ranking(self, market: str = "ALL", count: int = 50) -> Dict[str, Any]:
        """
        시간외 단일가 등락률 순위 조회 (ka10098)

        Args:
            market: 시장구분
            count: 조회 개수

        Returns:
            시간외 단일가 등락률 순위
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": self._get_market_code(market),
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_INPUT_CNT_1": str(count),
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES["overtime_rate_ranking"],
            endpoint="ranking",
            data=params,
            method="POST",
        )

    def get_previous_volume_top(
        self, market: str = "ALL", data_count: str = "50"
    ) -> Dict[str, Any]:
        """
        전일거래량상위요청 (ka10031)
        전일 대비 거래량이 큰 종목들을 조회합니다.

        Args:
            market: 시장구분 (ALL=전체, KOSPI=코스피, KOSDAQ=코스닥)
            data_count: 조회건수 (기본: 50)

        Returns:
            전일 거래량 상위 종목 데이터
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": self._get_market_code(market),
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_INPUT_CNT_1": data_count,
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES["previous_volume_top"],
            endpoint="ranking",
            data=params,
            method="POST",
        )

    def get_foreign_window_trading_top(
        self, market: str = "ALL", data_count: str = "50"
    ) -> Dict[str, Any]:
        """
        외국계창구매매상위요청 (ka10037)
        외국계 창구 매매 활동이 활발한 종목을 조회합니다.

        Args:
            market: 시장구분 (ALL=전체, KOSPI=코스피, KOSDAQ=코스닥)
            data_count: 조회건수 (기본: 50)

        Returns:
            외국계 창구 매매 상위 종목 데이터
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": self._get_market_code(market),
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_INPUT_CNT_1": data_count,
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES["foreign_window_trading_top"],
            endpoint="ranking",
            data=params,
            method="POST",
        )

    def get_stock_securities_ranking(
        self, stock_code: str, data_count: str = "20"
    ) -> Dict[str, Any]:
        """
        종목별증권사순위요청 (ka10038)
        특정 종목의 증권사별 매매 순위를 조회합니다.

        Args:
            stock_code: 종목코드 (6자리)
            data_count: 조회건수 (기본: 20)

        Returns:
            종목별 증권사 순위 데이터
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_INPUT_CNT_1": data_count,
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES["stock_securities_ranking"],
            endpoint="ranking",
            data=params,
            method="POST",
        )

    def get_daily_top_departure(
        self, market: str = "ALL", data_count: str = "50"
    ) -> Dict[str, Any]:
        """
        당일상위이탈원요청 (ka10053)
        당일 상위권에서 이탈한 종목들을 조회합니다.

        Args:
            market: 시장구분 (ALL=전체, KOSPI=코스피, KOSDAQ=코스닥)
            data_count: 조회건수 (기본: 50)

        Returns:
            당일 상위 이탈 종목 데이터
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": self._get_market_code(market),
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_INPUT_CNT_1": data_count,
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES["daily_top_departure"],
            endpoint="ranking",
            data=params,
            method="POST",
        )

    def get_same_net_trading_ranking(
        self, market: str = "ALL", data_count: str = "50"
    ) -> Dict[str, Any]:
        """
        동일순매매순위요청 (ka10062)
        동일인의 순매매 거래 순위를 조회합니다.

        Args:
            market: 시장구분 (ALL=전체, KOSPI=코스피, KOSDAQ=코스닥)
            data_count: 조회건수 (기본: 50)

        Returns:
            동일인 순매매 순위 데이터
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": self._get_market_code(market),
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_INPUT_CNT_1": data_count,
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES["same_net_trading_ranking"],
            endpoint="ranking",
            data=params,
            method="POST",
        )

    def get_foreign_institution_trading_top(
        self, market: str = "ALL", data_count: str = "50", sort_type: str = "1"
    ) -> Dict[str, Any]:
        """
        외국인기관매매상위요청 (ka90009)
        외국인과 기관의 매매 상위 종목을 조회합니다.

        Args:
            market: 시장구분 (ALL=전체, KOSPI=코스피, KOSDAQ=코스닥)
            data_count: 조회건수 (기본: 50)
            sort_type: 정렬구분 (1=순매수금액, 2=순매수수량)

        Returns:
            외국인/기관 매매 상위 종목 데이터
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": self._get_market_code(market),
            "FID_RANK_SORT_CLS_CODE": sort_type,
            "FID_INPUT_CNT_1": data_count,
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES["foreign_institution_trading_top"],
            endpoint="ranking",
            data=params,
            method="POST",
        )
