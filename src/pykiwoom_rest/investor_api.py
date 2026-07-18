"""
Investor Trading API
투자자 매매동향 관련 API 클래스
작성일: 2026-01-05
"""

from datetime import datetime, timedelta
from typing import Any, Dict

from .kiwoom_base import KiwoomAPIBase


class InvestorAPI(KiwoomAPIBase):
    """투자자 매매동향 관련 API (외국인, 기관, 프로그램 매매)"""

    # TR 코드 매핑
    TR_CODES = {
        "foreign_investor_trading": "ka10008",  # 주식외국인종목별매매동향
        "institutional_request": "ka10009",  # 주식기관요청
        "stock_member_trading": "ka10006",
        "institutional_daily_trading": "ka10044",  # 일별기관매매동향
        "institutional_trading_trend": "ka10045",
        "investor_daily_trading": "ka10058",  # 투자자별일별매매종목요청
        "investor_intraday_trading": "ka10063",  # 장중투자자별매매요청
        "institutional_foreign_consecutive": "ka10131",  # 기관외국인연속매매현황
        "sector_code_list": "ka10101",  # 업종코드 리스트
        "member_company_list": "ka10102",  # 회원사 리스트
    }

    @staticmethod
    def _data_or_error(response) -> Dict[str, Any]:
        """성공/실패 여부와 무관하게 동일한 응답 envelope 반환"""
        if isinstance(response, dict):
            if response.get("success") is False:
                return {
                    "success": False,
                    "data": response.get("data"),
                    "error": response.get("error"),
                    "metadata": response.get("metadata", response),
                }
            status_code = response.get("status_code")
            has_error_status = isinstance(status_code, int) and status_code >= 400
            if (response.get("error") or has_error_status) and response.get("rt_cd") not in (
                "0",
                0,
            ):
                return {
                    "success": False,
                    "data": response.get("data"),
                    "error": response.get("error") or response.get("msg1"),
                    "metadata": response,
                }
            if response.get("rt_cd") not in (None, "0", 0):
                return {
                    "success": False,
                    "data": None,
                    "error": response.get("msg1") or response.get("error"),
                    "metadata": response,
                }
            return {
                "success": True,
                "data": response.get("data", response),
                "error": None,
                "metadata": response.get("metadata", response),
            }

        success = getattr(response, "success", None)
        data = getattr(response, "data", None)
        error = getattr(response, "error", None)
        metadata = getattr(response, "metadata", None)

        if success is True:
            return {
                "success": True,
                "data": data,
                "error": None,
                "metadata": metadata,
            }
        if success is False:
            return {
                "success": False,
                "data": data,
                "error": error,
                "metadata": metadata,
            }
        return {
            "success": False,
            "data": None,
            "error": f"Unexpected response type: {type(response).__name__}",
            "metadata": {"raw_response": repr(response)},
        }

    def get_foreign_trading(self, stock_code: str) -> Dict[str, Any]:
        """
        주식외국인종목별매매동향 조회 (ka10008)

        Args:
            stock_code: 종목코드 (6자리)

        Returns:
            외국인 매매동향 데이터
        """
        headers = {"api-id": "ka10008", "cont-yn": "N", "next-key": ""}
        data = {"stk_cd": stock_code}

        token = self._get_access_token()
        headers["authorization"] = f"Bearer {token}"
        headers["Content-Type"] = "application/json;charset=UTF-8"

        response = self.request(
            method="POST",
            endpoint="/api/dostk/frgnistt",
            json_data=data,
            headers=headers,
        )

        return self._data_or_error(response)

    def get_stock_investor_trading(
        self,
        start_date: str = None,
        end_date: str = None,
        trade_type: str = "2",
        market_type: str = "101",
        investor_type: str = "8000",
        exchange_type: str = "3",
    ) -> Dict[str, Any]:
        """
        투자자별 일별 매매동향 조회 (ka10058)

        Args:
            start_date: 시작일자 (YYYYMMDD, 기본값: 30일 전)
            end_date: 종료일자 (YYYYMMDD, 기본값: 오늘)
            trade_type: 매매구분 (1=순매도, 2=순매수, 기본값: 2)
            market_type: 시장구분 (001=코스피, 101=코스닥, 기본값: 101)
            investor_type: 투자자구분 (8000=개인, 9000=외국인, 1000=금융투자,
                          3000=투신, 5000=기타금융, 4000=은행, 2000=보험,
                          6000=연기금, 7000=국가, 7100=기타법인, 9999=기관계, 기본값: 8000)
            exchange_type: 거래소구분 (1=KRX, 2=NXT, 3=통합, 기본값: 3)

        Returns:
            투자자별 일별 매매동향 정보 (개인, 기관, 외국인 등)
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

        params = {
            "strt_dt": start_date,
            "end_dt": end_date,
            "trde_tp": trade_type,
            "mrkt_tp": market_type,
            "invsr_tp": investor_type,
            "stex_tp": exchange_type,
        }

        headers = {"api-id": "ka10058", "cont-yn": "N", "next-key": ""}
        token = self._get_access_token()
        headers["authorization"] = f"Bearer {token}"
        headers["Content-Type"] = "application/json;charset=UTF-8"

        response = self.request(
            method="POST",
            endpoint="/api/dostk/stkinfo",
            json_data=params,
            headers=headers,
        )

        return self._data_or_error(response)

    def get_stock_member_trading(self, stock_code: str) -> Dict[str, Any]:
        """
        기관별 매매동향 조회 (ka10006)

        Args:
            stock_code: 종목코드

        Returns:
            기관별 매매동향 정보
        """
        headers = {"api-id": "ka10006", "cont-yn": "N", "next-key": ""}
        data = {"stk_cd": stock_code}

        token = self._get_access_token()
        headers["authorization"] = f"Bearer {token}"
        headers["Content-Type"] = "application/json;charset=UTF-8"

        response = self.request(
            method="POST",
            endpoint="/api/dostk/stkinfo",
            json_data=data,
            headers=headers,
        )

        return self._data_or_error(response)

    def get_institutional_trading_trend(
        self, stock_code: str, start_date: str = None, end_date: str = None
    ) -> Dict[str, Any]:
        """
        종목별기관매매추이요청 (ka10045)

        Args:
            stock_code: 종목코드 (6자리)
            start_date: 조회 시작일 (YYYYMMDD, 기본값: 30일 전)
            end_date: 조회 종료일 (YYYYMMDD, 기본값: 오늘)

        Returns:
            기관 매매 추이 데이터
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

        params = {
            "stk_cd": stock_code,
            "strt_dt": start_date,
            "end_dt": end_date,
            "orgn_prsm_unp_tp": "01",  # 기관법인단위유형
            "for_prsm_unp_tp": "01",  # 외국인법인단위유형
        }

        headers = {"api-id": "ka10045", "cont-yn": "N", "next-key": ""}
        token = self._get_access_token()
        headers["authorization"] = f"Bearer {token}"
        headers["Content-Type"] = "application/json;charset=UTF-8"

        response = self.request(
            method="POST",
            endpoint="/api/dostk/mrkcond",
            json_data=params,
            headers=headers,
        )

        return self._data_or_error(response)

    def get_institutional_foreign_consecutive_trading(
        self,
        market: str = "ALL",
        start_date: str = None,
        end_date: str = None,
    ) -> Dict[str, Any]:
        """
        기관외국인연속매매현황 조회 (ka10131)

        Args:
            market: 시장 구분 ("ALL", "KOSPI", "KOSDAQ")
            start_date: 시작일자 (YYYYMMDD)
            end_date: 종료일자 (YYYYMMDD)

        Returns:
            기관/외국인 연속 매매 현황 데이터
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

        market_codes = {"ALL": "J", "KOSPI": "J", "KOSDAQ": "Q"}
        market_key = market.upper()
        if market_key not in market_codes:
            raise ValueError(
                f"Invalid market: {market}. Expected one of: {', '.join(market_codes)}"
            )
        market_code = market_codes[market_key]

        params = {
            "FID_COND_MRKT_DIV_CODE": market_code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date,
        }

        headers = {"api-id": "ka10131", "cont-yn": "N", "next-key": ""}
        token = self._get_access_token()
        headers["authorization"] = f"Bearer {token}"
        headers["Content-Type"] = "application/json;charset=UTF-8"

        response = self.request(
            method="POST",
            endpoint="/api/dostk/frgnistt",
            json_data=params,
            headers=headers,
        )

        return self._data_or_error(response)

    def get_institutional_request(self, stock_code: str) -> Dict[str, Any]:
        """
        주식기관요청 조회 (ka10009)

        Args:
            stock_code: 종목코드 (6자리)

        Returns:
            기관 요청 정보
        """
        params = {"stk_cd": stock_code}

        headers = {"api-id": "ka10009", "cont-yn": "N", "next-key": ""}
        token = self._get_access_token()
        headers["authorization"] = f"Bearer {token}"
        headers["Content-Type"] = "application/json;charset=UTF-8"

        response = self.request(
            method="POST",
            endpoint="/api/dostk/frgnistt",
            json_data=params,
            headers=headers,
        )

        return self._data_or_error(response)

    def get_institutional_daily_trading(
        self,
        stock_code: str,
        start_date: str = None,
        end_date: str = None,
    ) -> Dict[str, Any]:
        """
        일별기관매매동향 조회 (ka10044)

        Args:
            stock_code: 종목코드 (6자리)
            start_date: 시작일자 (YYYYMMDD)
            end_date: 종료일자 (YYYYMMDD)

        Returns:
            일별 기관 매매 동향 데이터
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

        params = {
            "stk_cd": stock_code,
            "strt_dt": start_date,
            "end_dt": end_date,
        }

        headers = {"api-id": "ka10044", "cont-yn": "N", "next-key": ""}
        token = self._get_access_token()
        headers["authorization"] = f"Bearer {token}"
        headers["Content-Type"] = "application/json;charset=UTF-8"

        response = self.request(
            method="POST",
            endpoint="/api/dostk/mrkcond",
            json_data=params,
            headers=headers,
        )

        return self._data_or_error(response)

    def get_sector_code_list(self) -> Dict[str, Any]:
        """
        업종코드 리스트 조회 (ka10101)

        Returns:
            업종코드 리스트
        """
        headers = {"api-id": "ka10101", "cont-yn": "N", "next-key": ""}
        token = self._get_access_token()
        headers["authorization"] = f"Bearer {token}"
        headers["Content-Type"] = "application/json;charset=UTF-8"

        response = self.request(
            method="POST",
            endpoint="/api/dostk/stkinfo",
            json_data={},
            headers=headers,
        )

        return self._data_or_error(response)

    def get_member_company_list(self) -> Dict[str, Any]:
        """
        회원사 리스트 조회 (ka10102)

        Returns:
            회원사 리스트
        """
        headers = {"api-id": "ka10102", "cont-yn": "N", "next-key": ""}
        token = self._get_access_token()
        headers["authorization"] = f"Bearer {token}"
        headers["Content-Type"] = "application/json;charset=UTF-8"

        response = self.request(
            method="POST",
            endpoint="/api/dostk/stkinfo",
            json_data={},
            headers=headers,
        )

        return self._data_or_error(response)
