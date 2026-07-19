"""
Program Trading & Volume Profile API
프로그램 매매 및 매물대 분석 관련 API 클래스
작성일: 2026-01-05
"""

from typing import Any, Dict

from .kiwoom_base import KiwoomAPIBase


class ProgramAPI(KiwoomAPIBase):
    """프로그램 매매 및 매물대 분석 관련 API"""

    # TR 코드 매핑
    TR_CODES = {
        "program_trading_daily": "ka90013",  # 종목일별프로그램매매추이요청
        "stock_program_trading": "ka10009",
        "stock_trade_volume_power": "ka10010",
        "supply_concentration": "ka10025",  # 매물대집중요청
    }

    def get_program_trading_daily(self, stock_code: str) -> Dict[str, Any]:
        """
        종목일별프로그램매매추이요청 (ka90013)

        Args:
            stock_code: 종목코드 (6자리)

        Returns:
            프로그램 매매 추이 데이터
        """
        data = {"stk_cd": self.convert_stock_code_param(stock_code)["stk_cd"]}
        return self.make_tr_request(
            tr_code=self.TR_CODES["program_trading_daily"],
            endpoint="mrkcond",
            data=data,
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
        params = {"stk_cd": self.convert_stock_code_param(stock_code)["stk_cd"]}
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
        params = {"stk_cd": self.convert_stock_code_param(stock_code)["stk_cd"]}
        return self.make_tr_request(
            tr_code=self.TR_CODES["stock_trade_volume_power"],
            endpoint="stock_info",
            data=params,
            method="POST",
        )

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

        Args:
            market: 시장구분 ("000"=전체, "001"=코스피, "101"=코스닥)
            concentration_rate: 매물집중비율 (0~100, 기본값 50)
            include_current_entry: 현재가 매물대 진입 포함 여부 ("0"=불포함, "1"=포함)
            pbar_count: 매물대수 (숫자, 기본값 10)
            cycle: 주기구분 ("50"~"300", 기본값 50일)
            exchange: 거래소구분 ("1"=KRX, "2"=NXT, "3"=통합)

        Returns:
            Dict[str, Any]: 매물대 집중 종목 목록
        """
        allowed_markets = {"000", "001", "101"}
        allowed_current_entry = {"0", "1"}
        allowed_cycles = {"50", "100", "150", "200", "250", "300"}
        allowed_exchanges = {"1", "2", "3"}

        if market not in allowed_markets:
            raise ValueError("market must be one of 000, 001, 101")
        if include_current_entry not in allowed_current_entry:
            raise ValueError("include_current_entry must be one of 0, 1")
        if cycle not in allowed_cycles:
            raise ValueError("cycle must be one of 50, 100, 150, 200, 250, 300")
        if exchange not in allowed_exchanges:
            raise ValueError("exchange must be one of 1, 2, 3")
        if not isinstance(concentration_rate, str) or not concentration_rate.isdigit():
            raise ValueError("concentration_rate must be a numeric string between 0 and 100")
        concentration_rate_value = int(concentration_rate)
        if concentration_rate_value < 0 or concentration_rate_value > 100:
            raise ValueError("concentration_rate must be a numeric string between 0 and 100")
        if not isinstance(pbar_count, str) or not pbar_count.isdigit() or int(pbar_count) <= 0:
            raise ValueError("pbar_count must be a positive numeric string")

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
            endpoint="stock_info",
            data=params,
            method="POST",
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
