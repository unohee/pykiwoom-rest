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
        headers = {"api-id": "ka90013", "cont-yn": "N", "next-key": ""}
        data = {"stk_cd": stock_code}

        token = self._get_access_token()
        headers["authorization"] = f"Bearer {token}"
        headers["Content-Type"] = "application/json;charset=UTF-8"

        response = self.request(
            method="POST",
            endpoint="/api/dostk/mrkcond",
            json_data=data,
            headers=headers,
        )

        return response

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
                close_price = int(
                    candle.get("stck_clpr", candle.get("close_pric", 0))
                )
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
