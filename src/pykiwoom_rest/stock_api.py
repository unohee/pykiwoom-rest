"""
Stock Information API
주식 정보 관련 API 클래스
작성일: 2025-01-27
"""

from typing import Any, Dict

from .kiwoom_base import KiwoomAPIBase


class StockAPI(KiwoomAPIBase):
    """주식 정보 관련 API"""

    # TR 코드 매핑
    TR_CODES = {
        "stock_basic_info": "ka10001",
        "stock_member_info": "ka10002",
        "execution_info": "ka10003",
        "stock_quote": "ka10004",
        "stock_daily_weekly_monthly": "ka10005",  # 일주월시분 통합
        "stock_member_trading": "ka10006",
        "stock_elapsed_time": "ka10007",
        "foreign_investor_trading": "ka10008",  # 주식외국인종목별매매동향
        "institutional_request": "ka10009",  # 주식기관요청
        "stock_program_trading": "ka10009",  # 동일 TR 코드
        "stock_trade_volume_power": "ka10010",
        "credit_trend": "ka10013",
        "daily_trading_detail": "ka10015",
        "new_high_low": "ka10016",
        "upper_lower_limit": "ka10017",
        "high_low_approach": "ka10018",
        "price_fluctuation": "ka10019",
        "volume_update": "ka10024",
        "supply_concentration": "ka10025",
        "high_low_per": "ka10026",
        "open_price_rate": "ka10028",
        "member_supply_analysis": "ka10043",
        "institutional_daily_trading": "ka10044",  # 일별기관매매동향
        "institutional_trading_trend": "ka10045",
        "new_previous_execution": "ka10055",
        "investor_daily_trading": "ka10058",  # 투자자별일별매매종목요청
        "investor_intraday_trading": "ka10063",  # 장중투자자별매매요청
        "current_previous_execution": "ka10084",
        "watchlist_info": "ka10095",
        "stock_info_list": "ka10099",
        "stock_info_inquiry": "ka10100",
        "sector_code_list": "ka10101",  # 업종코드 리스트
        "member_company_list": "ka10102",  # 회원사 리스트
        "institutional_foreign_consecutive": "ka10131",  # 기관외국인연속매매현황
        "daily_trading_journal": "ka10170",
    }

    def get_stock_basic_info(self, stock_code: str) -> Dict[str, Any]:
        """
        주식 기본 정보 조회 (ka10001)

        Args:
            stock_code: 종목코드 (예: '005930')

        Returns:
            주식 기본 정보
        """
        params = self.convert_stock_code_param(stock_code)
        return self.make_tr_request(
            tr_code=self.TR_CODES["stock_basic_info"],
            endpoint="stock_info",
            data=params,
            method="POST",
        )

    def get_stock_quote(self, stock_code: str) -> Dict[str, Any]:
        """
        주식 현재가 호가 조회 (ka10004)

        Args:
            stock_code: 종목코드

        Returns:
            호가 정보
        """
        params = {"stk_cd": stock_code}
        return self.make_tr_request(
            tr_code=self.TR_CODES["stock_quote"],
            endpoint="market_condition",
            data=params,
            method="POST",
        )

    def get_execution_info(self, stock_code: str) -> Dict[str, Any]:
        """
        체결 정보 조회 (ka10003)

        Args:
            stock_code: 종목코드

        Returns:
            체결 정보
        """
        params = {"stk_cd": stock_code}
        return self.make_tr_request(
            tr_code=self.TR_CODES["execution_info"],
            endpoint="stock_info",
            data=params,
            method="POST",
        )

    def get_stock_member_info(self, stock_code: str) -> Dict[str, Any]:
        """
        종목별 투자자별 매매동향 (ka10002)

        Args:
            stock_code: 종목코드

        Returns:
            투자자별 매매동향
        """
        params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": stock_code}
        return self.make_tr_request(
            tr_code=self.TR_CODES["stock_member_info"],
            endpoint="stock_info",
            data=params,
            method="POST",
        )

    def get_credit_trend(
        self, date: str = None, query_type: str = "1"
    ) -> Dict[str, Any]:
        """
        신용매매동향 조회 (ka10013)

        Args:
            date: 조회일자 (YYYYMMDD, 기본값: 오늘)
            query_type: 조회구분 (1=융자, 2=대주, 기본값: 1)

        Returns:
            신용매매동향 정보
        """
        from datetime import datetime

        if not date:
            date = datetime.now().strftime("%Y%m%d")

        params = {"dt": date, "qry_tp": query_type}

        headers = {"api-id": "ka10013", "cont-yn": "N", "next-key": ""}
        token = self._get_access_token()
        headers["authorization"] = f"Bearer {token}"
        headers["Content-Type"] = "application/json;charset=UTF-8"

        response = self.request(
            method="POST",
            endpoint="/api/dostk/stkinfo",
            json_data=params,
            headers=headers,
        )

        return response

    def get_daily_trading_detail(self, start_date: str = None) -> Dict[str, Any]:
        """
        일별거래상세 조회 (ka10015)

        Args:
            start_date: 시작일자 (YYYYMMDD, 기본값: 오늘)

        Returns:
            일별거래상세 정보
        """
        from datetime import datetime

        if not start_date:
            start_date = datetime.now().strftime("%Y%m%d")

        params = {"strt_dt": start_date}

        headers = {"api-id": "ka10015", "cont-yn": "N", "next-key": ""}
        token = self._get_access_token()
        headers["authorization"] = f"Bearer {token}"
        headers["Content-Type"] = "application/json;charset=UTF-8"

        response = self.request(
            method="POST",
            endpoint="/api/dostk/stkinfo",
            json_data=params,
            headers=headers,
        )

        return response

    def get_new_high_low(
        self,
        new_high_low_type: str = "1",
        high_low_close_type: str = "1",
        stock_condition: str = "0",
        trade_volume_type: str = "00000",
        credit_condition: str = "0",
        updown_include: str = "0",
        period: str = "5",
        exchange_type: str = "3",
    ) -> Dict[str, Any]:
        """
        신고가/신저가 조회 (ka10016)

        Args:
            new_high_low_type: 신고저구분 (1=신고가, 2=신저가, 기본값: 1)
            high_low_close_type: 고저종구분 (1=고저기준, 2=종가기준, 기본값: 1)
            stock_condition: 종목조건 (0=전체조회, 1=관리종목제외, 3=우선주제외,
                           5=증100제외, 6=증100만보기, 7=증40만보기, 8=증30만보기, 기본값: 0)
            trade_volume_type: 거래량구분 (00000=전체조회, 00010=만주이상, 00050=5만주이상,
                             00100=10만주이상, 00150=15만주이상, 00200=20만주이상,
                             00300=30만주이상, 00500=50만주이상, 01000=백만주이상, 기본값: 00000)
            credit_condition: 신용조건 (0=전체조회, 1=신용융자A군, 2=신용융자B군,
                            3=신용융자C군, 4=신용융자D군, 7=신용융자E군, 9=신용융자전체, 기본값: 0)
            updown_include: 상하한포함 (0=미포함, 1=포함, 기본값: 0)
            period: 기간 (5=5일, 10=10일, 20=20일, 60=60일, 250=250일, 250일까지 입력가능, 기본값: 5)
            exchange_type: 거래소구분 (1=KRX, 2=NXT, 3=통합, 기본값: 3)

        Returns:
            신고가/신저가 목록
        """
        params = {
            "ntl_tp": new_high_low_type,
            "high_low_close_tp": high_low_close_type,
            "stk_cnd": stock_condition,
            "trde_qty_tp": trade_volume_type,
            "crd_cnd": credit_condition,
            "updown_incls": updown_include,
            "dt": period,
            "stex_tp": exchange_type,
        }

        headers = {"api-id": "ka10016", "cont-yn": "N", "next-key": ""}
        token = self._get_access_token()
        headers["authorization"] = f"Bearer {token}"
        headers["Content-Type"] = "application/json;charset=UTF-8"

        response = self.request(
            method="POST",
            endpoint="/api/dostk/stkinfo",
            json_data=params,
            headers=headers,
        )

        return response

    def get_upper_lower_limit(self, market: str = "ALL") -> Dict[str, Any]:
        """
        상한/하한가 조회 (ka10017)

        Args:
            market: 시장구분

        Returns:
            상한/하한가 목록
        """
        market_code = {"ALL": "0000", "KOSPI": "0001", "KOSDAQ": "1001"}.get(
            market, "0000"
        )

        params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": market_code}
        return self.make_tr_request(
            tr_code=self.TR_CODES["upper_lower_limit"],
            endpoint="stock_info",
            data=params,
            method="POST",
        )

    def get_price_fluctuation(self, market: str = "ALL") -> Dict[str, Any]:
        """
        등락률 상위 조회 (ka10019)

        Args:
            market: 시장구분

        Returns:
            등락률 상위 목록
        """
        market_code = {"ALL": "0000", "KOSPI": "0001", "KOSDAQ": "1001"}.get(
            market, "0000"
        )

        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": market_code,
            "FID_RANK_SORT_CLS_CODE": "0",
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES["price_fluctuation"],
            endpoint="stock_info",
            data=params,
            method="POST",
        )

    def get_high_low_approach(self, stock_code: str) -> Dict[str, Any]:
        """
        고가/저가 근접 조회 (ka10018)

        Args:
            stock_code: 종목코드

        Returns:
            고가/저가 근접 정보
        """
        params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": stock_code}
        return self.make_tr_request(
            tr_code=self.TR_CODES["high_low_approach"],
            endpoint="stock_info",
            data=params,
            method="POST",
        )

    def get_volume_concentration(self, stock_code: str) -> Dict[str, Any]:
        """
        거래량 집중도 조회 (ka10025)

        Args:
            stock_code: 종목코드

        Returns:
            거래량 집중도 정보
        """
        params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": stock_code}
        return self.make_tr_request(
            tr_code=self.TR_CODES["supply_concentration"],
            endpoint="stock_info",
            data=params,
            method="POST",
        )

    def get_high_low_per(self, market: str = "ALL") -> Dict[str, Any]:
        """
        고가/저가 PER 조회 (ka10026)

        Args:
            market: 시장구분

        Returns:
            고가/저가 PER 정보
        """
        market_code = {"ALL": "0000", "KOSPI": "0001", "KOSDAQ": "1001"}.get(
            market, "0000"
        )

        params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": market_code}
        return self.make_tr_request(
            tr_code=self.TR_CODES["high_low_per"],
            endpoint="stock_info",
            data=params,
            method="POST",
        )

    def get_current_previous_execution(self, stock_code: str) -> Dict[str, Any]:
        """
        당일/전일 체결 비교 (ka10084)

        Args:
            stock_code: 종목코드

        Returns:
            당일/전일 체결 비교 정보
        """
        params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": stock_code}
        return self.make_tr_request(
            tr_code=self.TR_CODES["current_previous_execution"],
            endpoint="stock_info",
            data=params,
            method="POST",
        )

    def get_watchlist_info(self, watchlist_code: str = "1") -> Dict[str, Any]:
        """
        관심종목 정보 조회 (ka10095)

        Args:
            watchlist_code: 관심종목 그룹코드

        Returns:
            관심종목 정보
        """
        params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": watchlist_code}
        return self.make_tr_request(
            tr_code=self.TR_CODES["watchlist_info"],
            endpoint="stock_info",
            data=params,
            method="POST",
        )

    def get_stock_list(self, market: str = "ALL") -> Dict[str, Any]:
        """
        종목 리스트 조회 (ka10099)

        Args:
            market: 시장구분

        Returns:
            종목 리스트
        """
        market_code = {"ALL": "0000", "KOSPI": "0001", "KOSDAQ": "1001"}.get(
            market, "0000"
        )

        params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": market_code}
        return self.make_tr_request(
            tr_code=self.TR_CODES["stock_info_list"],
            endpoint="stock_info",
            data=params,
            method="POST",
        )

    def get_stock_info_detail(self, stock_code: str) -> Dict[str, Any]:
        """
        종목 상세정보 조회 (ka10100)

        Args:
            stock_code: 종목코드

        Returns:
            종목 상세정보
        """
        params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": stock_code}
        return self.make_tr_request(
            tr_code=self.TR_CODES["stock_info_inquiry"],
            endpoint="stock_info",
            data=params,
            method="POST",
        )

    def get_foreign_trading(self, stock_code: str) -> Dict[str, Any]:
        """
        주식외국인종목별매매동향 조회 (ka10008)

        Args:
            stock_code: 종목코드 (6자리)

        Returns:
            외국인 매매동향 데이터
        """
        # 직접 API 호출 (TR 코드 방식이 아님)
        headers = {"api-id": "ka10008", "cont-yn": "N", "next-key": ""}

        data = {"stk_cd": stock_code}

        # 토큰 확보
        token = self._get_access_token()
        headers["authorization"] = f"Bearer {token}"
        headers["Content-Type"] = "application/json;charset=UTF-8"

        # 직접 요청
        response = self.request(
            method="POST",
            endpoint="/api/dostk/frgnistt",
            json_data=data,
            headers=headers,
        )

        return response

    def get_program_trading_daily(self, stock_code: str) -> Dict[str, Any]:
        """
        종목일별프로그램매매추이요청 (ka90013)

        Args:
            stock_code: 종목코드 (6자리)

        Returns:
            프로그램 매매 추이 데이터
        """
        # 직접 API 호출
        headers = {"api-id": "ka90013", "cont-yn": "N", "next-key": ""}

        data = {"stk_cd": stock_code}

        # 토큰 확보
        token = self._get_access_token()
        headers["authorization"] = f"Bearer {token}"
        headers["Content-Type"] = "application/json;charset=UTF-8"

        # 직접 요청
        response = self.request(
            method="POST",
            endpoint="/api/dostk/mrkcond",
            json_data=data,
            headers=headers,
        )

        return response

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

        Note:
            이전에 잘못된 TR 코드 ka10005가 사용되었습니다.
            ka10005는 '주식일주월시분요청'으로 차트 데이터 조회 API입니다.
            현재는 정확한 TR 코드 ka10058(투자자별일별매매종목요청)을 사용합니다.
        """
        from datetime import datetime, timedelta

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

        return response

    def get_stock_member_trading(self, stock_code: str) -> Dict[str, Any]:
        """
        기관별 매매동향 조회 (ka10006)

        Args:
            stock_code: 종목코드

        Returns:
            기관별 매매동향 정보
        """
        params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": stock_code}
        return self.make_tr_request(
            tr_code=self.TR_CODES["stock_member_trading"],
            endpoint="stock_info",
            data=params,
            method="POST",
        )

    def get_stock_elapsed_time(self, stock_code: str) -> Dict[str, Any]:
        """
        소요시간 조회 (ka10007)

        Args:
            stock_code: 종목코드

        Returns:
            소요시간 정보
        """
        params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": stock_code}
        return self.make_tr_request(
            tr_code=self.TR_CODES["stock_elapsed_time"],
            endpoint="stock_info",
            data=params,
            method="POST",
        )

    def get_stock_program_trading(self, stock_code: str) -> Dict[str, Any]:
        """
        프로그램매매동향 조회 (ka10009)

        Args:
            stock_code: 종목코드

        Returns:
            프로그램매매동향 정보
        """
        params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": stock_code}
        return self.make_tr_request(
            tr_code=self.TR_CODES["stock_program_trading"],
            endpoint="stock_info",
            data=params,
            method="POST",
        )

    def get_stock_trade_volume_power(self, stock_code: str) -> Dict[str, Any]:
        """
        거래량파동력 조회 (ka10010)

        Args:
            stock_code: 종목코드

        Returns:
            거래량파동력 정보
        """
        params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": stock_code}
        return self.make_tr_request(
            tr_code=self.TR_CODES["stock_trade_volume_power"],
            endpoint="stock_info",
            data=params,
            method="POST",
        )

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
        from datetime import datetime, timedelta

        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

        # API v2 형식의 매개변수 구조
        params = {
            "stk_cd": stock_code,
            "strt_dt": start_date,
            "end_dt": end_date,
            "orgn_prsm_unp_tp": "01",  # 기관법인단위유형 (01: 기본값)
            "for_prsm_unp_tp": "01",  # 외국인법인단위유형 (01: 기본값)
        }

        headers = {"api-id": "ka10045", "cont-yn": "N", "next-key": ""}

        # 토큰 확보
        token = self._get_access_token()
        headers["authorization"] = f"Bearer {token}"
        headers["Content-Type"] = "application/json;charset=UTF-8"

        # 직접 요청
        response = self.request(
            method="POST",
            endpoint="/api/dostk/mrkcond",
            json_data=params,
            headers=headers,
        )

        return response

        return response.data if response.success else {}

    def get_institutional_foreign_consecutive_trading(
        self,
        market: str = "ALL",
        start_date: str = None,
        end_date: str = None,
    ) -> Dict[str, Any]:
        """
        기관외국인연속매매현황 조회 (ka10131) ⭐ 핵심 API

        Args:
            market: 시장 구분 ("ALL", "KOSPI", "KOSDAQ")
            start_date: 시작일자 (YYYYMMDD)
            end_date: 종료일자 (YYYYMMDD)

        Returns:
            기관/외국인 연속 매매 현황 데이터
        """
        from datetime import datetime, timedelta

        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

        market_code = {"ALL": "J", "KOSPI": "J", "KOSDAQ": "Q"}.get(
            market.upper(), "J"
        )

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

        return response.data if response.success else {}

    def get_institutional_request(self, stock_code: str) -> Dict[str, Any]:
        """
        주식기관요청 조회 (ka10009)

        Args:
            stock_code: 종목코드 (6자리)
                       거래소별 종목코드 (KRX:039490, NXT:039490_NX, SOR:039490_AL)

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
            endpoint="/api/dostk/frgnistt",  # ✓ 수정: stkinfo → frgnistt
            json_data=params,
            headers=headers,
        )

        return response

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
        from datetime import datetime, timedelta

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

        return response.data if response.success else {}

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

        return response.data if response.success else {}

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

        return response.data if response.success else {}

    # ========== 별칭 메서드 (Alias Methods) ==========

    def get_stock_price(self, stock_code: str) -> Dict[str, Any]:
        """
        주식 현재가 조회 (ka10001의 별칭)

        Args:
            stock_code: 종목코드 (6자리)

        Returns:
            주식 기본 정보 (현재가 포함)
        """
        return self.get_stock_basic_info(stock_code)

    def get_stock_orderbook(self, stock_code: str) -> Dict[str, Any]:
        """
        주식 호가 조회 (ka10004의 별칭)

        Args:
            stock_code: 종목코드 (6자리)

        Returns:
            주식 호가 정보 (매수/매도 10호가)
        """
        return self.get_stock_quote(stock_code)

    # ========== PyKIS 호환 메서드 (PyKIS Compatibility) ==========

    def get_stock_financial(self, stock_code: str) -> Dict[str, Any]:
        """
        주식 재무 정보 조회 (PyKIS 호환)

        키움 REST API의 ka10001 (주식기본정보)에서 재무 데이터를 추출합니다.
        PyKIS의 get_stock_financial() 응답 형식과 호환됩니다.

        Args:
            stock_code: 종목코드 (6자리)

        Returns:
            Dict[str, Any]: 재무 정보 (PyKIS 형식 호환)
            {
                "rt_cd": "0",
                "output": [
                    {
                        "stac_yymm": "202509",  # 결산년월
                        "eps": "3701.00",       # 주당순이익
                        "bps": "50000.00",      # 주당순자산
                        "roe_val": "15.5",      # ROE
                        "sps": "120000.00",     # 주당매출
                        "per": "12.5",          # PER
                        "pbr": "1.2",           # PBR
                        ...
                    }
                ]
            }

        Note:
            키움 REST API는 분기별 상세 재무제표 데이터를 제공하지 않습니다.
            ka10001 응답에서 추출 가능한 필드만 반환합니다.
            더 상세한 재무 데이터가 필요하면 PyKIS 또는 외부 API를 사용하세요.
        """
        from datetime import datetime

        try:
            # 기본 정보 조회
            basic_info = self.get_stock_basic_info(stock_code)

            if not basic_info or basic_info.get("rt_cd") != "0":
                return {
                    "rt_cd": "1",
                    "msg1": "FINANCIAL_DATA_ERROR",
                    "output": [],
                }

            # 응답에서 재무 데이터 추출
            # ka10001 응답 필드 매핑:
            # - per: PER
            # - pbr: PBR
            # - eps: EPS
            # - bps: BPS
            # - stk_divi_rate: 배당수익률

            output1 = basic_info.get("output1", {})
            if not output1:
                # 다른 응답 형식 시도
                output1 = basic_info.get("stk_prpr_qry", {})
                if not output1:
                    output1 = basic_info

            # 재무 필드 추출
            eps = output1.get("eps", output1.get("stck_eps", "0"))
            bps = output1.get("bps", output1.get("stck_bps", "0"))
            per = output1.get("per", output1.get("stck_per", "0"))
            pbr = output1.get("pbr", output1.get("stck_pbr", "0"))
            dvd_rate = output1.get(
                "stk_divi_rate", output1.get("dvdn_rate", "0")
            )

            # PyKIS 형식으로 변환
            current_quarter = datetime.now().strftime("%Y%m")

            financial_data = {
                "stac_yymm": current_quarter,
                "eps": str(eps) if eps else "0",
                "bps": str(bps) if bps else "0",
                "roe_val": "",  # ka10001에서 제공하지 않음
                "sps": "",  # ka10001에서 제공하지 않음
                "per": str(per) if per else "0",
                "pbr": str(pbr) if pbr else "0",
                "dvdn_rate": str(dvd_rate) if dvd_rate else "0",
                # 추가 필드 (있으면 포함)
                "grs": "",  # 매출성장률
                "bsop_prfi_inrt": "",  # 영업이익성장률
                "ntin_inrt": "",  # 순이익성장률
                "rsrv_rate": "",  # 유보율
                "lblt_rate": "",  # 부채비율
            }

            return {
                "rt_cd": "0",
                "msg1": "FINANCIAL_FROM_BASIC_INFO",
                "output": [financial_data],
                "_source": "ka10001",
                "_note": "키움 REST API는 분기별 상세 재무데이터를 제공하지 않습니다.",
            }

        except Exception as e:
            self.logger.warning(f"[{stock_code}] get_stock_financial 실패: {e}")
            return {
                "rt_cd": "1",
                "msg1": str(e),
                "output": [],
            }

    def get_pbar_tratio(self, stock_code: str) -> Dict[str, Any]:
        """
        매물대 분석 (Volume Profile) 조회 (PyKIS 호환)

        가격대별 거래량 분포를 조회하여 지지/저항 분석에 활용합니다.

        Args:
            stock_code: 종목코드 (6자리)

        Returns:
            Dict[str, Any]: 매물대 데이터
            {
                "rt_cd": "0",
                "output1": {"stck_prpr": "71000", ...},  # 현재가 정보
                "output2": [  # 가격대별 거래량
                    {"stck_prpr": "71000", "cntg_vol": "123456", ...},
                    ...
                ]
            }

        Note:
            키움 REST API에서는 매물대(Volume Profile) 전용 TR이 제한적입니다.
            일봉 데이터를 활용하여 간접적으로 매물대를 분석할 수 있습니다.
            정확한 매물대 분석은 PyKIS의 get_pbar_tratio()를 권장합니다.
        """
        try:
            # 키움 REST API는 매물대 전용 TR을 제공하지 않음
            # 대안: 일봉 데이터로 가격대별 거래량 분포 추정
            daily_data = self.make_tr_request(
                tr_code="ka10081",  # 일봉 차트
                endpoint="chart",
                data={
                    "stk_cd": stock_code,
                    "base_dt": "",
                    "upd_stkpc_tp": "1",
                    "req_cnt": "100",  # 100일치
                },
            )

            if not daily_data or daily_data.get("rt_cd") != "0":
                return {
                    "rt_cd": "1",
                    "msg1": "PBAR_NOT_AVAILABLE",
                    "output1": {},
                    "output2": [],
                    "_note": "키움 REST API는 매물대 전용 API를 제공하지 않습니다.",
                }

            # 일봉 데이터에서 가격대별 거래량 집계
            candles = daily_data.get("stk_day_pole_chart_qry", [])
            if not candles:
                candles = daily_data.get("output2", [])

            if not candles:
                return {
                    "rt_cd": "0",
                    "msg1": "NO_CANDLE_DATA",
                    "output1": {},
                    "output2": [],
                }

            # 가격대별 거래량 집계 (간단한 Volume Profile)
            price_volume_map = {}
            current_price = 0
            for candle in candles:
                # 종가를 대표 가격으로 사용
                close_price = int(candle.get("stck_clpr", candle.get("close_pric", 0)))
                volume = int(candle.get("acml_vol", candle.get("volume", 0)))

                if close_price > 0:
                    # 가격대 그룹화 (1% 단위)
                    price_group = int(close_price / (close_price * 0.01)) * int(
                        close_price * 0.01
                    )
                    if price_group not in price_volume_map:
                        price_volume_map[price_group] = 0
                    price_volume_map[price_group] += volume

                    # 현재가 (가장 최근 종가)
                    if current_price == 0:
                        current_price = close_price

            # output2 형식으로 변환
            output2 = []
            for price, volume in sorted(price_volume_map.items(), reverse=True):
                output2.append(
                    {
                        "stck_prpr": str(price),
                        "cntg_vol": str(volume),
                    }
                )

            return {
                "rt_cd": "0",
                "msg1": "PBAR_FROM_DAILY_CHART",
                "output1": {"stck_prpr": str(current_price)},
                "output2": output2,
                "_source": "ka10081_aggregated",
                "_note": "일봉 데이터 기반 추정치. 정확한 분석은 PyKIS 권장.",
            }

        except Exception as e:
            self.logger.warning(f"[{stock_code}] get_pbar_tratio 실패: {e}")
            return {
                "rt_cd": "1",
                "msg1": str(e),
                "output1": {},
                "output2": [],
            }

    def get_pbar_concentration(
        self,
        market: str = "000",
        concentration_rate: str = "50",
        include_current_entry: str = "0",
        pbar_count: str = "10",
        cycle: str = "50",
        exchange: str = "3",
    ) -> Dict[str, Any]:
        """
        매물대집중요청 (ka10025)

        시장 전체에서 매물대가 집중된 종목을 스크리닝합니다.
        특정 종목의 매물대가 아닌, 매물대 집중 조건에 맞는 종목 목록을 반환합니다.

        Args:
            market: 시장구분
                - "000": 전체
                - "001": 코스피
                - "101": 코스닥
            concentration_rate: 매물집중비율 (0~100, 기본값 50)
            include_current_entry: 현재가 매물대 진입 포함 여부
                - "0": 포함 안 함
                - "1": 포함
            pbar_count: 매물대수 (숫자, 기본값 10)
            cycle: 주기구분
                - "50": 50일
                - "100": 100일
                - "150": 150일
                - "200": 200일
                - "250": 250일
                - "300": 300일
            exchange: 거래소구분
                - "1": KRX
                - "2": NXT
                - "3": 통합 (기본값)

        Returns:
            Dict[str, Any]: 매물대 집중 종목 목록
            {
                "rt_cd": "0",
                "prps_cnctr": [
                    {
                        "stk_cd": "005930",
                        "stk_nm": "삼성전자",
                        "cur_prc": "71000",
                        "pred_pre_sig": "3",  # 전일대비 부호
                        "pred_pre": "500",    # 전일대비
                        "flu_rt": "0.71",     # 등락률
                        "now_trde_qty": "123456",  # 현재거래량
                        "pric_strt": "70000",  # 매물대 시작가
                        "pric_end": "71500",   # 매물대 종료가
                        "prps_qty": "5",       # 매물대 수
                        "prps_rt": "+60.00"    # 매물집중비율
                    },
                    ...
                ]
            }

        Example:
            >>> # 코스피에서 매물집중비율 60% 이상, 100일 기준
            >>> result = api.get_pbar_concentration(
            ...     market="001",
            ...     concentration_rate="60",
            ...     cycle="100"
            ... )
        """
        params = {
            "mrkt_tp": market,
            "prps_cnctr_rt": concentration_rate,
            "cur_prc_entry": include_current_entry,
            "prpscnt": pbar_count,
            "cycle_tp": cycle,
            "stex_tp": exchange,
        }

        result = self.make_tr_request(
            tr_code=self.TR_CODES["supply_concentration"],
            endpoint="stkinfo",
            data=params,
        )

        # 응답 형식 표준화
        if result and "prps_cnctr" in result:
            return {
                "rt_cd": "0",
                "msg1": result.get("return_msg", "정상처리"),
                "prps_cnctr": result.get("prps_cnctr", []),
                "_source": "ka10025",
            }

        return result
