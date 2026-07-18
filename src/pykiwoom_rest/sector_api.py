"""
Sector API Module - 업종 관련 API 구현
작성일: 2025-01-27
"""

from datetime import datetime
from typing import Any, Dict, Optional

from .kiwoom_base import KiwoomAPIBase
from .response_utils import clean_index_price


class SectorAPI(KiwoomAPIBase):
    """업종 관련 API 클래스"""

    # TR 코드 매핑
    TR_CODES = {
        "sector_current_price": "ka20001",
        "sector_stock_price": "ka20002",
        "all_sector_index": "ka20003",
        "sector_tick_chart": "ka20004",
        "sector_minute_chart": "ka20005",
        "sector_daily_chart": "ka20006",
        "sector_weekly_chart": "ka20007",
        "sector_monthly_chart": "ka20008",
        "sector_daily_current": "ka20009",
        "sector_yearly_chart": "ka20019",
        "sector_investor_trading": "ka10051",
        "sector_program_trading": "ka10010",
    }

    @staticmethod
    def _normalize_sector_value(name: str, value: Any) -> str:
        """Validate and normalize sector request parameters before TR submission."""
        if value is None:
            raise ValueError(f"{name} is required")

        normalized = str(value).strip()
        if not normalized:
            raise ValueError(f"{name} must not be empty")

        key = name.lower()
        if "date" in key or key.endswith("dt"):
            if not (len(normalized) == 8 and normalized.isdigit()):
                raise ValueError(f"{name} must be YYYYMMDD")
            try:
                datetime.strptime(normalized, "%Y%m%d")
            except ValueError as exc:
                raise ValueError(f"{name} must be a valid YYYYMMDD date") from exc
        elif key in {"sect_cd", "sector_code"}:
            if not (normalized.isdigit() and 3 <= len(normalized) <= 4):
                raise ValueError(f"{name} must be a 3-4 digit sector code")
        elif any(token in key for token in ("mrkt", "market", "tp", "type", "unit", "gb")):
            if not (normalized.isdigit() and len(normalized) <= 2):
                raise ValueError(f"{name} must be a numeric code")

        return normalized

    def _normalize_sector_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {key: self._normalize_sector_value(key, value) for key, value in params.items()}

    def make_tr_request(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Validate sector request parameters before delegating to the base client."""
        if "data" in kwargs and isinstance(kwargs["data"], dict):
            kwargs["data"] = self._normalize_sector_params(kwargs["data"])
        elif len(args) >= 3 and isinstance(args[2], dict):
            args = (*args[:2], self._normalize_sector_params(args[2]), *args[3:])
        return super().make_tr_request(*args, **kwargs)

    def get_sector_current_price(self, sector_code: str = "0001") -> Dict[str, Any]:
        """
        업종현재가요청 (ka20001)

        Args:
            sector_code: 업종코드 (기본값: 0001)

        Returns:
            Dict[str, Any]: 업종 현재가 정보
        """
        params = {"sect_cd": sector_code}
        return self.make_tr_request(
            tr_code=self.TR_CODES["sector_current_price"],
            endpoint="sector",
            data=params,
        )

    def get_sector_stock_price(self, sector_code: str = "0001") -> Dict[str, Any]:
        """
        업종별주가요청 (ka20002)

        Args:
            sector_code: 업종코드

        Returns:
            Dict[str, Any]: 업종별 주가 정보
        """
        params = {"sect_cd": sector_code}
        return self.make_tr_request(
            tr_code=self.TR_CODES["sector_stock_price"],
            endpoint="sector",
            data=params,
        )

    def get_all_sector_index(self) -> Dict[str, Any]:
        """
        전업종지수요청 (ka20003)

        Returns:
            Dict[str, Any]: 전체 업종 지수
        """
        params = {}
        return self.make_tr_request(
            tr_code=self.TR_CODES["all_sector_index"],
            endpoint="sector",
            data=params,
        )

    def get_sector_tick_chart(self, sector_code: str, tick_scope: int = 1) -> Dict[str, Any]:
        """
        업종틱차트조회요청 (ka20004)

        Args:
            sector_code: 업종코드 (3자리, 예: "001"=KOSPI, "101"=KOSDAQ)
                        4자리 입력 시 자동 변환 ("0001" -> "001")
            tick_scope: 틱 범위 (1, 3, 5, 10, 30)

        Returns:
            Dict[str, Any]: 업종 틱차트 데이터
        """
        # 4자리 코드를 3자리로 변환 (0001 -> 001)
        if len(sector_code) == 4 and sector_code.startswith("0"):
            sector_code = sector_code[1:]

        params = {"inds_cd": sector_code, "tic_scope": str(tick_scope)}
        return self.make_tr_request(
            tr_code=self.TR_CODES["sector_tick_chart"],
            endpoint="chart",
            data=params,
        )

    def get_sector_minute_chart(
        self,
        sector_code: str,
        interval: int = 1,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        업종분봉조회요청 (ka20005)

        Args:
            sector_code: 업종코드 (3자리, 예: "001"=KOSPI, "101"=KOSDAQ)
                        4자리 입력 시 자동 변환 ("0001" -> "001")
            interval: 분봉 간격 (1, 3, 5, 10, 30)
            start_date: 시작일자 (YYYYMMDD) - 미사용
            end_date: 종료일자 (YYYYMMDD) - 미사용

        Returns:
            Dict[str, Any]: 업종 분봉 차트
        """
        # 4자리 코드를 3자리로 변환 (0001 -> 001)
        if len(sector_code) == 4 and sector_code.startswith("0"):
            sector_code = sector_code[1:]

        allowed_intervals = {1, 3, 5, 10, 30}
        try:
            interval_value = int(interval)
        except (TypeError, ValueError) as exc:
            raise ValueError("interval must be one of 1, 3, 5, 10, 30") from exc
        if interval_value not in allowed_intervals:
            raise ValueError("interval must be one of 1, 3, 5, 10, 30")

        params = {"inds_cd": sector_code, "tic_scope": str(interval_value)}

        return self.make_tr_request(
            tr_code=self.TR_CODES["sector_minute_chart"],
            endpoint="chart",  # 업종 차트는 chart 엔드포인트 사용
            data=params,
        )

    def get_sector_daily_chart(
        self,
        sector_code: str,
        base_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        업종일봉조회요청 (ka20006)

        Args:
            sector_code: 업종코드 (3자리, 예: "001"=KOSPI, "101"=KOSDAQ)
                        4자리 입력 시 자동 변환 ("0001" -> "001")
            base_date: 기준일자 (YYYYMMDD, 미입력시 오늘)

        Returns:
            Dict[str, Any]: 업종 일봉 차트
        """
        # 4자리 코드를 3자리로 변환 (0001 -> 001)
        if len(sector_code) == 4 and sector_code.startswith("0"):
            sector_code = sector_code[1:]

        from datetime import datetime

        if not base_date:
            base_date = datetime.now().strftime("%Y%m%d")

        params = {"inds_cd": sector_code, "base_dt": base_date}

        return self.make_tr_request(
            tr_code=self.TR_CODES["sector_daily_chart"],
            endpoint="chart",
            data=params,
        )

    def get_index_daily_price(
        self,
        index_code: str,
        base_date: Optional[str] = None,
        count: int = 100,
    ) -> Dict[str, Any]:
        """
        지수/업종 일별 시세 조회 (PyKIS 호환)

        PyKIS의 get_index_daily_price()와 호환되는 인터페이스를 제공합니다.
        내부적으로 ka20006 (업종일봉조회)을 사용합니다.

        Args:
            index_code: 업종/지수 코드
                - "0001" 또는 "001": 코스피
                - "1001" 또는 "101": 코스닥
                - "2001" 또는 "201": 코스피200
            base_date: 기준일자 (YYYYMMDD, 미입력시 오늘)
            count: 조회 개수 (기본 100)

        Returns:
            Dict[str, Any]: PyKIS 호환 응답 형식
            {
                "rt_cd": "0",
                "output2": [
                    {
                        "stck_bsop_date": "20251226",
                        "bstp_nmix_oprc": "2500.00",  # 시가
                        "bstp_nmix_hgpr": "2520.00",  # 고가
                        "bstp_nmix_lwpr": "2480.00",  # 저가
                        "bstp_nmix_prpr": "2510.00",  # 종가
                        "acml_vol": "123456789",      # 거래량
                        "acml_tr_pbmn": "1234567890000",  # 거래대금
                    },
                    ...
                ],
                "_source": "ka20006"
            }
        """
        try:
            # 기존 get_sector_daily_chart 호출
            raw_data = self.get_sector_daily_chart(index_code, base_date)

            if not raw_data:
                return {
                    "rt_cd": "1",
                    "msg1": "INDEX_DAILY_DATA_ERROR",
                    "output2": [],
                }

            # 에러 응답 처리
            rt_cd = raw_data.get("rt_cd", "1")
            if rt_cd != "0":
                return {
                    "rt_cd": rt_cd,
                    "msg1": raw_data.get("msg1", "API_ERROR"),
                    "output2": [],
                }

            # 차트 데이터 추출 (output2 또는 output)
            chart_data = raw_data.get(
                "output2",
                raw_data.get("output", raw_data.get("inds_dt_pole_qry", [])),
            )
            if not isinstance(chart_data, list):
                chart_data = [chart_data] if chart_data else []

            # PyKIS 호환 형식으로 변환
            output2 = []
            for item in chart_data[:count]:
                if not item:
                    continue

                # Kiwoom 필드명 -> PyKIS 필드명 매핑
                # Kiwoom: dt, open, high, low, close, vol
                # PyKIS: stck_bsop_date, bstp_nmix_oprc, bstp_nmix_hgpr, etc.
                open_value = item.get("open", item.get("open_pric", item.get("bstp_nmix_oprc", item.get("oprc", "0"))))
                high_value = item.get("high", item.get("high_pric", item.get("bstp_nmix_hgpr", item.get("hgpr", "0"))))
                low_value = item.get("low", item.get("low_pric", item.get("bstp_nmix_lwpr", item.get("lwpr", "0"))))
                close_value = item.get("close", item.get("cur_prc", item.get("bstp_nmix_prpr", item.get("prpr", "0"))))

                should_normalize_index = getattr(self, "normalize_data", False) or "inds_dt_pole_qry" in raw_data
                if should_normalize_index:
                    open_value = clean_index_price(open_value)
                    high_value = clean_index_price(high_value)
                    low_value = clean_index_price(low_value)
                    close_value = clean_index_price(close_value)

                converted = {
                    # 날짜
                    "stck_bsop_date": str(
                        item.get("dt", item.get("stck_bsop_date", item.get("date", "")))
                    ),
                    # 시가
                    "bstp_nmix_oprc": str(open_value),
                    # 고가
                    "bstp_nmix_hgpr": str(high_value),
                    # 저가
                    "bstp_nmix_lwpr": str(low_value),
                    # 종가
                    "bstp_nmix_prpr": str(close_value),
                    # 거래량
                    "acml_vol": str(item.get("vol", item.get("trde_qty", item.get("acml_vol", item.get("volume", "0"))))),
                    # 거래대금
                    "acml_tr_pbmn": str(
                        item.get("amt", item.get("trde_prica", item.get("acml_tr_pbmn", item.get("tr_pbmn", "0"))))
                    ),
                }
                output2.append(converted)

            return {
                "rt_cd": "0",
                "msg1": "정상처리",
                "output2": output2,
                "_source": "ka20006",
                "_note": "Kiwoom REST 업종일봉 데이터",
            }

        except Exception as e:
            return {
                "rt_cd": "1",
                "msg1": str(e),
                "output2": [],
            }

    def get_sector_weekly_chart(
        self,
        sector_code: str,
        base_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        업종주봉조회요청 (ka20007)

        Args:
            sector_code: 업종코드 (3자리, 예: "001"=KOSPI, "101"=KOSDAQ)
                        4자리 입력 시 자동 변환 ("0001" -> "001")
            base_date: 기준일자 (YYYYMMDD, 미입력시 오늘)

        Returns:
            Dict[str, Any]: 업종 주봉 차트
        """
        # 4자리 코드를 3자리로 변환 (0001 -> 001)
        if len(sector_code) == 4 and sector_code.startswith("0"):
            sector_code = sector_code[1:]

        from datetime import datetime

        if not base_date:
            base_date = datetime.now().strftime("%Y%m%d")

        params = {"inds_cd": sector_code, "base_dt": base_date}

        return self.make_tr_request(
            tr_code=self.TR_CODES["sector_weekly_chart"],
            endpoint="chart",
            data=params,
        )

    def get_sector_monthly_chart(
        self,
        sector_code: str,
        base_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        업종월봉조회요청 (ka20008)

        Args:
            sector_code: 업종코드 (3자리, 예: "001"=KOSPI, "101"=KOSDAQ)
                        4자리 입력 시 자동 변환 ("0001" -> "001")
            base_date: 기준일자 (YYYYMMDD, 미입력시 오늘)

        Returns:
            Dict[str, Any]: 업종 월봉 차트
        """
        # 4자리 코드를 3자리로 변환 (0001 -> 001)
        if len(sector_code) == 4 and sector_code.startswith("0"):
            sector_code = sector_code[1:]

        from datetime import datetime

        if not base_date:
            base_date = datetime.now().strftime("%Y%m%d")

        params = {"inds_cd": sector_code, "base_dt": base_date}

        return self.make_tr_request(
            tr_code=self.TR_CODES["sector_monthly_chart"],
            endpoint="chart",
            data=params,
        )

    def get_sector_daily_current(self, sector_code: str) -> Dict[str, Any]:
        """
        업종현재가일별요청 (ka20009)

        Args:
            sector_code: 업종코드

        Returns:
            Dict[str, Any]: 업종 현재가 일별 데이터
        """
        params = {"sect_cd": sector_code}
        return self.make_tr_request(
            tr_code=self.TR_CODES["sector_daily_current"],
            endpoint="sector",
            data=params,
        )

    def get_sector_yearly_chart(
        self,
        sector_code: str,
        base_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        업종년봉조회요청 (ka20019)

        Args:
            sector_code: 업종코드 (3자리, 예: "001"=KOSPI, "101"=KOSDAQ)
                        4자리 입력 시 자동 변환 ("0001" -> "001")
            base_date: 기준일자 (YYYYMMDD, 미입력시 오늘)

        Returns:
            Dict[str, Any]: 업종 년봉 차트
        """
        # 4자리 코드를 3자리로 변환 (0001 -> 001)
        if len(sector_code) == 4 and sector_code.startswith("0"):
            sector_code = sector_code[1:]

        from datetime import datetime

        if not base_date:
            base_date = datetime.now().strftime("%Y%m%d")

        params = {"inds_cd": sector_code, "base_dt": base_date}

        return self.make_tr_request(
            tr_code=self.TR_CODES["sector_yearly_chart"],
            endpoint="chart",
            data=params,
        )

    def get_sector_investor_trading(self, sector_code: str) -> Dict[str, Any]:
        """
        업종별투자자순매수요청 (ka10051)

        Args:
            sector_code: 업종코드

        Returns:
            Dict[str, Any]: 업종별 투자자 순매수 정보
        """
        params = {"sect_cd": self._normalize_sector_value("sect_cd", sector_code)}
        return self.make_tr_request(
            tr_code=self.TR_CODES["sector_investor_trading"],
            endpoint="sector",
            data=params,
        )

    def get_sector_program_trading(self, sector_code: str) -> Dict[str, Any]:
        """
        업종프로그램요청 (ka10010)

        Args:
            sector_code: 업종코드

        Returns:
            Dict[str, Any]: 업종 프로그램 매매 정보
        """
        params = {"sect_cd": self._normalize_sector_value("sect_cd", sector_code)}
        return self.make_tr_request(
            tr_code=self.TR_CODES["sector_program_trading"],
            endpoint="sector",
            data=params,
        )
