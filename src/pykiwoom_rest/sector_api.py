"""
Sector API Module - 업종 관련 API 구현
작성일: 2025-01-27
"""

from typing import Any, Dict, Optional

from .kiwoom_base import KiwoomAPIBase


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
            tr_id=self.TR_CODES["sector_current_price"], data=params
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
            tr_id=self.TR_CODES["sector_stock_price"], data=params
        )

    def get_all_sector_index(self) -> Dict[str, Any]:
        """
        전업종지수요청 (ka20003)

        Returns:
            Dict[str, Any]: 전체 업종 지수
        """
        params = {}
        return self.make_tr_request(
            tr_id=self.TR_CODES["all_sector_index"], data=params
        )

    def get_sector_tick_chart(
        self, sector_code: str, count: int = 100
    ) -> Dict[str, Any]:
        """
        업종틱차트조회요청 (ka20004)

        Args:
            sector_code: 업종코드
            count: 조회 건수

        Returns:
            Dict[str, Any]: 업종 틱차트 데이터
        """
        params = {"sect_cd": sector_code, "count": str(count)}
        return self.make_tr_request(
            tr_id=self.TR_CODES["sector_tick_chart"], data=params
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
            sector_code: 업종코드
            interval: 분봉 간격 (1, 3, 5, 10, 15, 30, 45, 60)
            start_date: 시작일자 (YYYYMMDD)
            end_date: 종료일자 (YYYYMMDD)

        Returns:
            Dict[str, Any]: 업종 분봉 차트
        """
        params = {"sect_cd": sector_code, "tic_scope": str(interval)}

        if start_date:
            params["start_dt"] = start_date
        if end_date:
            params["end_dt"] = end_date

        return self.make_tr_request(
            tr_id=self.TR_CODES["sector_minute_chart"], data=params
        )

    def get_sector_daily_chart(
        self,
        sector_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        업종일봉조회요청 (ka20006)

        Args:
            sector_code: 업종코드
            start_date: 시작일자 (YYYYMMDD)
            end_date: 종료일자 (YYYYMMDD)

        Returns:
            Dict[str, Any]: 업종 일봉 차트
        """
        params = {"sect_cd": sector_code}

        if start_date:
            params["start_dt"] = start_date
        if end_date:
            params["end_dt"] = end_date

        return self.make_tr_request(
            tr_id=self.TR_CODES["sector_daily_chart"], data=params
        )

    def get_sector_weekly_chart(
        self,
        sector_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        업종주봉조회요청 (ka20007)

        Args:
            sector_code: 업종코드
            start_date: 시작일자 (YYYYMMDD)
            end_date: 종료일자 (YYYYMMDD)

        Returns:
            Dict[str, Any]: 업종 주봉 차트
        """
        params = {"sect_cd": sector_code}

        if start_date:
            params["start_dt"] = start_date
        if end_date:
            params["end_dt"] = end_date

        return self.make_tr_request(
            tr_id=self.TR_CODES["sector_weekly_chart"], data=params
        )

    def get_sector_monthly_chart(
        self,
        sector_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        업종월봉조회요청 (ka20008)

        Args:
            sector_code: 업종코드
            start_date: 시작일자 (YYYYMMDD)
            end_date: 종료일자 (YYYYMMDD)

        Returns:
            Dict[str, Any]: 업종 월봉 차트
        """
        params = {"sect_cd": sector_code}

        if start_date:
            params["start_dt"] = start_date
        if end_date:
            params["end_dt"] = end_date

        return self.make_tr_request(
            tr_id=self.TR_CODES["sector_monthly_chart"], data=params
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
            tr_id=self.TR_CODES["sector_daily_current"], data=params
        )

    def get_sector_yearly_chart(
        self,
        sector_code: str,
        start_year: Optional[str] = None,
        end_year: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        업종년봉조회요청 (ka20019)

        Args:
            sector_code: 업종코드
            start_year: 시작년도 (YYYY)
            end_year: 종료년도 (YYYY)

        Returns:
            Dict[str, Any]: 업종 년봉 차트
        """
        params = {"sect_cd": sector_code}

        if start_year:
            params["start_year"] = start_year
        if end_year:
            params["end_year"] = end_year

        return self.make_tr_request(
            tr_id=self.TR_CODES["sector_yearly_chart"], data=params
        )

    def get_sector_investor_trading(self, sector_code: str) -> Dict[str, Any]:
        """
        업종별투자자순매수요청 (ka10051)

        Args:
            sector_code: 업종코드

        Returns:
            Dict[str, Any]: 업종별 투자자 순매수 정보
        """
        params = {"sect_cd": sector_code}
        return self.make_tr_request(
            tr_id=self.TR_CODES["sector_investor_trading"], data=params
        )

    def get_sector_program_trading(self, sector_code: str) -> Dict[str, Any]:
        """
        업종프로그램요청 (ka10010)

        Args:
            sector_code: 업종코드

        Returns:
            Dict[str, Any]: 업종 프로그램 매매 정보
        """
        params = {"sect_cd": sector_code}
        return self.make_tr_request(
            tr_id=self.TR_CODES["sector_program_trading"], data=params
        )
