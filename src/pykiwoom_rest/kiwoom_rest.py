"""
KiwoomRest - Unified Facade using New Modular Architecture
기존 인터페이스를 유지하면서 새로운 아키텍처 사용
작성일: 2025-01-27
"""

from typing import Any, Dict, Optional

from .account_api import AccountAPI
from .auth_api import AuthAPI
from .chart_api import ChartAPI
from .investor_api import InvestorAPI
from .order_api import OrderAPI
from .program_api import ProgramAPI
from .ranking_api import RankingAPI
from .sector_api import SectorAPI
from .stock_api import StockAPI
from .websocket_api import WebSocketAPI


class KiwoomRest:
    """
    키움증권 REST API 통합 클래스
    새로운 모듈러 아키텍처 기반, Rate Limiting 및 에러 처리 자동화
    """

    def __init__(
        self,
        account_no: str = None,
        appkey: str = None,
        appsecret: str = None,
        env_path: str = None,
        use_mock: bool = False,
        rate_limit: int = 20,
        max_retries: int = 3,
        enable_rate_optimizer: bool = False,
        credentials_list: list = None,
    ):
        """
        키움증권 REST API 클라이언트 초기화

        인증 정보는 다음 우선순위로 로드됩니다:
        1. 직접 전달된 파라미터 (account_no, appkey, appsecret)
        2. 환경변수 (.env 파일 또는 시스템 환경변수)
           - ACC_NO 또는 ACCOUNT_NO
           - APPKEY 또는 KIWOOM_APPKEY
           - APPSECRET, KIWOOM_SECRETKEY 또는 KIWOOM_APPSECRET

        Args:
            account_no: 계좌번호 (직접 주입 가능, 선택)
            appkey: 앱키 (직접 주입 가능, 선택)
            appsecret: 앱시크릿 (직접 주입 가능, 선택)
            env_path: .env 파일 경로 (기본: 프로젝트 루트)
            use_mock: 모의투자 API 사용 여부
            rate_limit: 초당 최대 요청 수 (기본: 20)
            max_retries: 최대 재시도 횟수 (기본: 3)
            enable_rate_optimizer: Rate limiting 최적화 활성화
            credentials_list: 다중 크레덴셜 리스트 (로테이션용)

        Examples:
            # 방법 1: 환경변수 사용 (.env 파일)
            >>> kiwoom = KiwoomRest()

            # 방법 2: 직접 주입
            >>> kiwoom = KiwoomRest(
            ...     account_no="12345678",
            ...     appkey="your-app-key",
            ...     appsecret="your-app-secret"
            ... )

            # 방법 3: 혼합 (일부만 직접 주입)
            >>> kiwoom = KiwoomRest(
            ...     appkey="your-app-key",
            ...     appsecret="your-app-secret"
            ...     # account_no는 환경변수에서 로드
            ... )

        Raises:
            ValueError: 필수 인증 정보가 누락된 경우
        """
        # 공통 설정
        common_config = {
            "account_no": account_no,
            "appkey": appkey,
            "appsecret": appsecret,
            "env_path": env_path,
            "use_mock": use_mock,
            "rate_limit": rate_limit,
            "max_retries": max_retries,
            "enable_rate_optimizer": enable_rate_optimizer,
            "credentials_list": credentials_list,
        }

        # 모듈러 API 클래스들 초기화
        self.auth_api = AuthAPI(**common_config)
        self.stock_api = StockAPI(**common_config)
        self.investor_api = InvestorAPI(**common_config)
        self.program_api = ProgramAPI(**common_config)
        self.chart_api = ChartAPI(**common_config)
        self.ranking_api = RankingAPI(**common_config)
        self.account_api = AccountAPI(**common_config)
        self.order_api = OrderAPI(**common_config)
        self.sector_api = SectorAPI(**common_config)

        # 인증 정보 공유
        self._sync_authentication()

        # Rate optimizer 접근을 위한 참조
        self.api_base = self.stock_api.api_base

        # WebSocket API (lazy initialization)
        self._websocket_api: Optional[WebSocketAPI] = None
        self._websocket_enabled = False

    def _sync_authentication(self):
        """
        인증 정보 동기화 (토큰 공유)

        모든 API 클래스 중 가장 최신 토큰을 찾아서 전체 동기화
        """
        # 모든 API 객체에서 토큰 수집
        all_apis = [
            self.auth_api,
            self.stock_api,
            self.chart_api,
            self.ranking_api,
            self.account_api,
            self.order_api,
            self.sector_api,
        ]

        # 가장 최신 토큰 찾기
        latest_token = None
        latest_expires = None

        for api in all_apis:
            if hasattr(api, "access_token") and api.access_token:
                if hasattr(api, "token_expires") and api.token_expires:
                    # 기존 토큰보다 만료 시간이 더 늦으면 업데이트
                    if latest_expires is None or api.token_expires > latest_expires:
                        latest_token = api.access_token
                        latest_expires = api.token_expires
                elif latest_token is None:
                    # 만료 시간이 없어도 토큰이 있으면 사용
                    latest_token = api.access_token
                    latest_expires = api.token_expires

        # 모든 API 객체에 최신 토큰 동기화
        if latest_token:
            for api in all_apis:
                api.access_token = latest_token
                api.token_expires = latest_expires

    # ========== 주식 정보 관련 메서드 (Legacy Compatible) ==========

    def get_stock_price(self, stock_code: str) -> Dict[str, Any]:
        """주식 기본 정보 조회"""
        return self.stock_api.get_stock_basic_info(stock_code)

    def get_stock_orderbook(self, stock_code: str) -> Dict[str, Any]:
        """주식 호가 조회"""
        return self.stock_api.get_stock_quote(stock_code)

    def get_execution_info(self, stock_code: str) -> Dict[str, Any]:
        """체결 정보 조회"""
        return self.stock_api.get_execution_info(stock_code)

    def get_foreign_trading(self, stock_code: str) -> Dict[str, Any]:
        """주식외국인종목별매매동향 조회 (ka10008)"""
        return self.investor_api.get_foreign_trading(stock_code)

    def get_program_trading_daily(self, stock_code: str) -> Dict[str, Any]:
        """종목일별프로그램매매추이요청 (ka90013)"""
        return self.program_api.get_program_trading_daily(stock_code)

    def get_institutional_trading_trend(
        self, stock_code: str, start_date: str = None, end_date: str = None
    ) -> Dict[str, Any]:
        """종목별기관매매추이요청 (ka10045)"""
        return self.investor_api.get_institutional_trading_trend(stock_code, start_date, end_date)

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
            investor_type: 투자자구분 (8000=개인, 9000=외국인, 1000=금융투자 등)
            exchange_type: 거래소구분 (1=KRX, 2=NXT, 3=통합, 기본값: 3)

        Returns:
            투자자별 일별 매매동향 정보
        """
        return self.investor_api.get_stock_investor_trading(
            start_date=start_date,
            end_date=end_date,
            trade_type=trade_type,
            market_type=market_type,
            investor_type=investor_type,
            exchange_type=exchange_type,
        )

    def get_credit_trend(self, date: str = None, query_type: str = "1") -> Dict[str, Any]:
        """신용매매동향 조회 (ka10013)"""
        return self.stock_api.get_credit_trend(date=date, query_type=query_type)

    def get_daily_trading_detail(self, start_date: str = None) -> Dict[str, Any]:
        """일별거래상세 조회 (ka10015)"""
        return self.stock_api.get_daily_trading_detail(start_date=start_date)

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
        """신고가/신저가 조회 (ka10016)"""
        return self.stock_api.get_new_high_low(
            new_high_low_type=new_high_low_type,
            high_low_close_type=high_low_close_type,
            stock_condition=stock_condition,
            trade_volume_type=trade_volume_type,
            credit_condition=credit_condition,
            updown_include=updown_include,
            period=period,
            exchange_type=exchange_type,
        )

    def get_stock_member_trading(self, stock_code: str) -> Dict[str, Any]:
        """기관별 매매동향 조회 (ka10006)"""
        return self.investor_api.get_stock_member_trading(stock_code)

    def get_stock_elapsed_time(self, stock_code: str) -> Dict[str, Any]:
        """소요시간 조회 (ka10007)"""
        return self.stock_api.get_stock_elapsed_time(stock_code)

    def get_stock_program_trading(self, stock_code: str) -> Dict[str, Any]:
        """프로그램매매동향 조회 (ka10009)"""
        return self.stock_api.get_stock_program_trading(stock_code)

    def get_stock_trade_volume_power(self, stock_code: str) -> Dict[str, Any]:
        """거래량파동력 조회 (ka10010)"""
        return self.program_api.get_stock_trade_volume_power(stock_code)

    # ========== 차트 데이터 메서드 (Legacy Compatible) ==========

    def get_tick_chart(self, stock_code: str, count: int = 100) -> Dict[str, Any]:
        """틱 차트 조회"""
        return self.chart_api.get_tick_chart(stock_code, count)

    def get_minute_chart(
        self,
        stock_code: str,
        interval: int = 1,
        start_date: str = None,
        end_date: str = None,
        count: int = 100,
    ) -> Dict[str, Any]:
        """분봉 차트 조회"""
        return self.chart_api.get_minute_chart(stock_code, interval, start_date, end_date, count)

    def get_daily_chart(
        self, stock_code: str, start_date: str = None, end_date: str = None
    ) -> Dict[str, Any]:
        """일봉 차트 조회"""
        return self.chart_api.get_daily_chart(stock_code, start_date, end_date)

    def get_weekly_chart(
        self, stock_code: str, start_date: str = None, end_date: str = None
    ) -> Dict[str, Any]:
        """주봉 차트 조회"""
        return self.chart_api.get_weekly_chart(stock_code, start_date, end_date)

    def get_monthly_chart(
        self, stock_code: str, start_date: str = None, end_date: str = None
    ) -> Dict[str, Any]:
        """월봉 차트 조회"""
        return self.chart_api.get_monthly_chart(stock_code, start_date, end_date)

    def get_yearly_chart(
        self, stock_code: str, start_date: str = None, end_date: str = None
    ) -> Dict[str, Any]:
        """년봉 차트 조회"""
        return self.chart_api.get_yearly_chart(stock_code, start_date, end_date)

    # ========== 순위 정보 메서드 (Legacy Compatible) ==========

    def get_volume_top(self, market: str = "ALL", count: int = 50) -> Dict[str, Any]:
        """호가잔량 상위 조회"""
        return self.ranking_api.get_volume_top(market, count)

    def get_hourly_program_trading(
        self, stock_code: str, date: str, amount_or_quantity: str = "1"
    ) -> Dict[str, Any]:
        """종목시간별 프로그램매매 추이요청 (ka90008)"""
        return self.ranking_api.get_hourly_program_trading(stock_code, date, amount_or_quantity)

    def get_hourly_program_trading_paginated(
        self,
        stock_code: str,
        date: str,
        amount_or_quantity: str = "1",
        max_records: int = None,
    ) -> Dict[str, Any]:
        """종목시간별 프로그램매매 추이요청 (페이지네이션 지원)"""
        return self.ranking_api.get_hourly_program_trading_paginated(
            stock_code, date, amount_or_quantity, max_records
        )

    def get_foreign_top_buy(self, period: str = "1") -> Dict[str, Any]:
        """외인 기간별 매매 상위 조회"""
        return self.ranking_api.get_foreign_period_trading_top("ALL", period, 50)

    def get_trading_volume_surge(self, market: str = "ALL") -> Dict[str, Any]:
        """거래대금 급증 조회"""
        return self.ranking_api.get_trading_volume_surge(market)

    def get_previous_day_rate_top(self, market: str = "ALL") -> Dict[str, Any]:
        """전일 대비 등락률 상위 조회"""
        return self.ranking_api.get_previous_day_rate_top(market)

    def get_daily_volume_top(self, market: str = "ALL") -> Dict[str, Any]:
        """당일 거래량 상위 조회"""
        return self.ranking_api.get_daily_volume_top(market)

    def get_trading_amount_top(self, market: str = "ALL") -> Dict[str, Any]:
        """거래대금 상위 조회"""
        return self.ranking_api.get_trading_amount_top(market)

    def get_previous_volume_top(
        self, market: str = "ALL", data_count: str = "50"
    ) -> Dict[str, Any]:
        """전일거래량상위요청 (ka10031)"""
        return self.ranking_api.get_previous_volume_top(market, data_count)

    def get_foreign_window_trading_top(
        self, market: str = "ALL", data_count: str = "50"
    ) -> Dict[str, Any]:
        """외국계창구매매상위요청 (ka10037)"""
        return self.ranking_api.get_foreign_window_trading_top(market, data_count)

    def get_stock_securities_ranking(
        self, stock_code: str, data_count: str = "20"
    ) -> Dict[str, Any]:
        """종목별증권사순위요청 (ka10038)"""
        return self.ranking_api.get_stock_securities_ranking(stock_code, data_count)

    def get_daily_top_departure(
        self, market: str = "ALL", data_count: str = "50"
    ) -> Dict[str, Any]:
        """당일상위이탈원요청 (ka10053)"""
        return self.ranking_api.get_daily_top_departure(market, data_count)

    def get_same_net_trading_ranking(
        self, market: str = "ALL", data_count: str = "50"
    ) -> Dict[str, Any]:
        """동일순매매순위요청 (ka10062)"""
        return self.ranking_api.get_same_net_trading_ranking(market, data_count)

    def get_foreign_institution_trading_top(
        self, market: str = "ALL", data_count: str = "50", sort_type: str = "1"
    ) -> Dict[str, Any]:
        """외국인기관매매상위요청 (ka90009)"""
        return self.ranking_api.get_foreign_institution_trading_top(market, data_count, sort_type)

    # ========== 계좌 관련 메서드 (Account API) ==========

    def get_deposit_detail(self) -> Dict[str, Any]:
        """예수금상세현황요청"""
        return self.account_api.get_deposit_detail()

    def get_account_evaluation(self) -> Dict[str, Any]:
        """계좌평가현황요청"""
        return self.account_api.get_account_evaluation()

    def get_balance_detail(self) -> Dict[str, Any]:
        """계좌평가잔고내역요청"""
        return self.account_api.get_balance_detail()

    def get_unfilled_orders(self) -> Dict[str, Any]:
        """미체결요청"""
        return self.account_api.get_unfilled_orders()

    def get_executed_orders(self) -> Dict[str, Any]:
        """체결요청"""
        return self.account_api.get_executed_orders()

    def get_account_return(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """계좌수익률요청"""
        return self.account_api.get_account_return(start_date, end_date)

    def get_estimated_asset(self) -> Dict[str, Any]:
        """추정자산조회요청"""
        return self.account_api.get_estimated_asset()

    def get_execution_balance(self) -> Dict[str, Any]:
        """체결잔고요청"""
        return self.account_api.get_execution_balance()

    def get_daily_estimated_asset(self, base_date: Optional[str] = None) -> Dict[str, Any]:
        """일별추정예탁자산현황요청"""
        return self.account_api.get_daily_estimated_asset(base_date)

    def get_realized_profit_detail(self) -> Dict[str, Any]:
        """당일실현손익상세요청"""
        return self.account_api.get_realized_profit_detail()

    def get_daily_trading_diary(self, base_date: Optional[str] = None) -> Dict[str, Any]:
        """당일매매일지요청"""
        return self.account_api.get_daily_trading_diary(base_date)

    def get_trading_history(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """위탁종합거래내역요청"""
        return self.account_api.get_trading_history(start_date, end_date)

    # ========== 주문 관련 메서드 (Order API) ==========

    def buy_stock(
        self,
        stock_code: str,
        quantity: int,
        price: int = 0,
        order_type: str = "00",
        price_type: str = "00",
    ) -> Dict[str, Any]:
        """주식 매수주문"""
        return self.order_api.buy_stock(stock_code, quantity, price, order_type, price_type)

    def sell_stock(
        self,
        stock_code: str,
        quantity: int,
        price: int = 0,
        order_type: str = "00",
        price_type: str = "00",
    ) -> Dict[str, Any]:
        """주식 매도주문"""
        return self.order_api.sell_stock(stock_code, quantity, price, order_type, price_type)

    def modify_order(
        self,
        original_order_no: str,
        stock_code: str,
        quantity: int,
        price: int = 0,
        order_type: str = "00",
    ) -> Dict[str, Any]:
        """주식 정정주문"""
        return self.order_api.modify_order(
            original_order_no, stock_code, quantity, price, order_type
        )

    def cancel_order(
        self, original_order_no: str, stock_code: str, quantity: int
    ) -> Dict[str, Any]:
        """주식 취소주문"""
        return self.order_api.cancel_order(original_order_no, stock_code, quantity)

    # ========== 업종 관련 메서드 (Sector API) ==========

    def get_sector_current_price(self, sector_code: str = "0001") -> Dict[str, Any]:
        """업종현재가요청"""
        return self.sector_api.get_sector_current_price(sector_code)

    def get_all_sector_index(self) -> Dict[str, Any]:
        """전업종지수요청"""
        return self.sector_api.get_all_sector_index()

    def get_sector_daily_chart(
        self,
        sector_code: str,
        base_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        업종일봉조회요청 (ka20006)

        Args:
            sector_code: 업종코드 (예: "0001"=코스피, "1001"=코스닥)
            base_date: 기준일자 (YYYYMMDD, 미입력시 오늘)
        """
        return self.sector_api.get_sector_daily_chart(sector_code, base_date)

    def get_sector_minute_chart(
        self,
        sector_code: str,
        interval: int = 1,
    ) -> Dict[str, Any]:
        """
        업종분봉조회요청 (ka20005)

        Args:
            sector_code: 업종코드 (예: "0001"=코스피, "1001"=코스닥)
            interval: 분봉 간격 (1, 3, 5, 10, 30)

        Returns:
            Dict[str, Any]: 업종 분봉 차트 데이터
        """
        return self.sector_api.get_sector_minute_chart(sector_code, interval)

    def get_sector_weekly_chart(
        self,
        sector_code: str,
        base_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        업종주봉조회요청 (ka20007)

        Args:
            sector_code: 업종코드 (예: "0001"=코스피, "1001"=코스닥)
            base_date: 기준일자 (YYYYMMDD, 미입력시 오늘)
        """
        return self.sector_api.get_sector_weekly_chart(sector_code, base_date)

    def get_sector_monthly_chart(
        self,
        sector_code: str,
        base_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        업종월봉조회요청 (ka20008)

        Args:
            sector_code: 업종코드 (예: "0001"=코스피, "1001"=코스닥)
            base_date: 기준일자 (YYYYMMDD, 미입력시 오늘)
        """
        return self.sector_api.get_sector_monthly_chart(sector_code, base_date)

    def get_sector_yearly_chart(
        self,
        sector_code: str,
        base_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        업종년봉조회요청 (ka20019)

        Args:
            sector_code: 업종코드 (예: "0001"=코스피, "1001"=코스닥)
            base_date: 기준일자 (YYYYMMDD, 미입력시 오늘)
        """
        return self.sector_api.get_sector_yearly_chart(sector_code, base_date)

    def get_sector_tick_chart(self, sector_code: str, tick_scope: int = 1) -> Dict[str, Any]:
        """
        업종틱차트조회요청 (ka20004)

        Args:
            sector_code: 업종코드 (예: "0001"=코스피, "1001"=코스닥)
            tick_scope: 틱 범위 (1, 3, 5, 10, 30)
        """
        return self.sector_api.get_sector_tick_chart(sector_code, tick_scope)

    # ========== 인증 관련 메서드 (Auth API) ==========

    def get_access_token(self, force_refresh: bool = False) -> Dict[str, Any]:
        """OAuth2 액세스 토큰 발급"""
        token_info = self.auth_api.get_access_token(force_refresh=force_refresh)
        # 토큰 동기화
        self._sync_authentication()
        return token_info

    def revoke_token(self, token: Optional[str] = None) -> Dict[str, Any]:
        """OAuth2 액세스 토큰 폐기"""
        return self.auth_api.revoke_token(token)

    def get_token_status(self) -> Dict[str, Any]:
        """
        현재 토큰 상태 조회

        모든 API 클래스를 확인하여 실제 사용 중인 토큰의 상태 반환

        Returns:
            토큰 상태 정보
            {
                'has_token': bool,
                'is_valid': bool,
                'token_prefix': str,
                'expires_at': str (ISO format),
                'time_to_expiry': int (초),
                'needs_refresh': bool
            }
        """
        # 먼저 토큰 동기화
        self._sync_authentication()

        # 모든 API 중 유효한 토큰 찾기
        all_apis = [
            self.stock_api,
            self.chart_api,
            self.auth_api,
            self.ranking_api,
            self.account_api,
            self.order_api,
            self.sector_api,
        ]

        # 가장 최신 토큰 정보 찾기
        best_token = None
        best_expires = None

        for api in all_apis:
            if hasattr(api, "access_token") and api.access_token:
                if hasattr(api, "token_expires") and api.token_expires:
                    if best_expires is None or api.token_expires > best_expires:
                        best_token = api.access_token
                        best_expires = api.token_expires
                elif best_token is None:
                    best_token = api.access_token
                    best_expires = api.token_expires

        # 토큰 상태 계산
        from datetime import datetime

        has_token = bool(best_token)
        is_valid = False
        time_to_expiry = 0
        needs_refresh = False

        if has_token and best_expires:
            now = datetime.now()
            is_valid = now < best_expires
            time_to_expiry = int((best_expires - now).total_seconds())
            # 5분 미만 남으면 갱신 필요
            needs_refresh = 0 < time_to_expiry < 300

        token_prefix = (
            f"{best_token[:20]}..." if best_token and len(best_token) > 20 else best_token
        )

        return {
            "has_token": has_token,
            "is_valid": is_valid,
            "token_prefix": token_prefix or "None",
            "expires_at": best_expires.isoformat() if best_expires else None,
            "time_to_expiry": time_to_expiry,
            "needs_refresh": needs_refresh,
        }

    def refresh_token(self) -> Dict[str, Any]:
        """토큰 갱신"""
        token_info = self.auth_api.refresh_token()
        # 토큰 동기화
        self._sync_authentication()
        return token_info

    def logout(self) -> Dict[str, Any]:
        """로그아웃 (토큰 폐기 + 세션 정리)"""
        return self.auth_api.logout()

    # ========== 새로운 고급 기능 ==========

    def get_minute_chart_paginated(
        self,
        stock_code: str,
        interval: int = 1,
        start_date: str = None,
        end_date: str = None,
        max_records: int = 1000,
    ) -> Dict[str, Any]:
        """분봉 차트 대량 조회 (페이지네이션)"""
        return self.chart_api.get_minute_chart_paginated(
            stock_code, interval, start_date, end_date, max_records
        )

    def get_minute_chart_with_date(
        self,
        stock_code: str,
        interval: int = 5,
        target_date: str = None,
        max_pages: int = 20,
    ) -> Dict[str, Any]:
        """특정 날짜의 분봉 데이터 조회 (연속조회 사용)"""
        return self.chart_api.get_minute_chart_with_date(
            stock_code, interval, target_date, max_pages
        )

    # ========== 유틸리티 메서드 ==========

    # to_dataframe 폐기: 원시 JSON만 제공 (DataFrame 변환은 사용자 책임)

    def verify_connection(self) -> Dict[str, Any]:
        """API 연결 상태 확인"""
        return self.stock_api.health_check()

    def get_stats(self) -> Dict[str, Any]:
        """API 호출 통계 반환"""
        return {
            "stock_api_stats": self.stock_api.get_stats(),
            "chart_api_stats": self.chart_api.get_stats(),
            "ranking_api_stats": self.ranking_api.get_stats(),
            "total_requests": sum(
                [
                    self.stock_api.get_stats()["request_count"],
                    self.chart_api.get_stats()["request_count"],
                    self.ranking_api.get_stats()["request_count"],
                ]
            ),
            "total_errors": sum(
                [
                    self.stock_api.get_stats()["error_count"],
                    self.chart_api.get_stats()["error_count"],
                    self.ranking_api.get_stats()["error_count"],
                ]
            ),
        }

    def reset_rate_limiter(self):
        """Rate limiter 초기화"""
        self.stock_api.rate_limiter.reset()
        self.chart_api.rate_limiter.reset()
        self.ranking_api.rate_limiter.reset()

    def close(self):
        """모든 세션 종료"""
        self.stock_api.close()
        self.chart_api.close()
        self.ranking_api.close()

    def __enter__(self):
        """Context manager 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        self.close()

    # ========== 직접 API 접근 프로퍼티 ==========

    @property
    def auth(self) -> AuthAPI:
        """인증 API 직접 접근"""
        return self.auth_api

    @property
    def stock(self) -> StockAPI:
        """주식 정보 API 직접 접근"""
        return self.stock_api

    @property
    def chart(self) -> ChartAPI:
        """차트 데이터 API 직접 접근"""
        return self.chart_api

    @property
    def ranking(self) -> RankingAPI:
        """순위 정보 API 직접 접근"""
        return self.ranking_api

    @property
    def websocket(self) -> WebSocketAPI:
        """WebSocket API 직접 접근 (실시간 시세)"""
        if not self._websocket_api:
            # Lazy initialization - api_base에서 인증 정보 가져옴
            api_base = self.stock_api.api_base
            self._websocket_api = WebSocketAPI(
                access_token=self.auth_api.access_token or "",
                appkey=api_base.appkey,
                appsecret=api_base.appsecret,
            )
        return self._websocket_api

    # ========== 실시간 시세 (WebSocket) 메서드 ==========

    def enable_websocket(self) -> bool:
        """
        WebSocket 실시간 시세 활성화

        Returns:
            활성화 성공 여부

        Examples:
            >>> kiwoom = KiwoomRest(...)
            >>> kiwoom.enable_websocket()
            >>> # 이제 실시간 시세 구독 가능
        """
        try:
            import asyncio

            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        self._websocket_enabled = loop.run_until_complete(self.websocket.connect())
        return self._websocket_enabled

    def disable_websocket(self):
        """WebSocket 실시간 시세 비활성화"""
        if self._websocket_api:
            try:
                import asyncio

                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            loop.run_until_complete(self._websocket_api.disconnect())
            self._websocket_enabled = False

    def subscribe_realtime_quote(self, stock_code: str, callback=None) -> bool:
        """
        실시간 시세 구독

        Args:
            stock_code: 종목코드 (예: "005930")
            callback: 데이터 수신 콜백 함수

        Returns:
            구독 성공 여부

        Examples:
            >>> def on_quote(quote):
            ...     print(f"현재가: {quote.current_price}")
            >>> kiwoom.subscribe_realtime_quote("005930", on_quote)
        """
        if not self._websocket_enabled:
            raise RuntimeError(
                "WebSocket이 활성화되지 않았습니다. enable_websocket()을 먼저 호출하세요."
            )

        import asyncio

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.websocket.subscribe_quote(stock_code, callback))

    def subscribe_realtime_orderbook(self, stock_code: str, callback=None) -> bool:
        """
        실시간 호가 구독

        Args:
            stock_code: 종목코드
            callback: 데이터 수신 콜백 함수

        Returns:
            구독 성공 여부

        Examples:
            >>> def on_orderbook(orderbook):
            ...     print(f"매수 1호가: {orderbook.bid_prices[0]}")
            >>> kiwoom.subscribe_realtime_orderbook("005930", on_orderbook)
        """
        if not self._websocket_enabled:
            raise RuntimeError(
                "WebSocket이 활성화되지 않았습니다. enable_websocket()을 먼저 호출하세요."
            )

        import asyncio

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.websocket.subscribe_orderbook(stock_code, callback))

    def subscribe_realtime_trade(self, stock_code: str, callback=None) -> bool:
        """
        실시간 체결 구독

        Args:
            stock_code: 종목코드
            callback: 데이터 수신 콜백 함수

        Returns:
            구독 성공 여부

        Examples:
            >>> def on_trade(trade):
            ...     print(f"체결가: {trade.trade_price}, 체결량: {trade.trade_volume}")
            >>> kiwoom.subscribe_realtime_trade("005930", on_trade)
        """
        if not self._websocket_enabled:
            raise RuntimeError(
                "WebSocket이 활성화되지 않았습니다. enable_websocket()을 먼저 호출하세요."
            )

        import asyncio

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.websocket.subscribe_trade(stock_code, callback))

    def unsubscribe_realtime_all(self):
        """모든 실시간 구독 해제"""
        if not self._websocket_enabled:
            return

        import asyncio

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.websocket.unsubscribe_all())

    # ========== 기관/외국인 관련 API (NEW) ==========

    def get_institutional_foreign_consecutive_trading(
        self,
        market: str = "ALL",
        start_date: str = None,
        end_date: str = None,
    ) -> Dict[str, Any]:
        """기관외국인연속매매현황 조회 (ka10131)"""
        return self.investor_api.get_institutional_foreign_consecutive_trading(
            market, start_date, end_date
        )

    def get_institutional_request(self, stock_code: str) -> Dict[str, Any]:
        """주식기관요청 조회 (ka10009)"""
        return self.investor_api.get_institutional_request(stock_code)

    def get_institutional_daily_trading(
        self,
        stock_code: str,
        start_date: str = None,
        end_date: str = None,
    ) -> Dict[str, Any]:
        """일별기관매매동향 조회 (ka10044)"""
        return self.investor_api.get_institutional_daily_trading(stock_code, start_date, end_date)

    def get_sector_code_list(self) -> Dict[str, Any]:
        """업종코드 리스트 조회 (ka10101)"""
        return self.investor_api.get_sector_code_list()

    def get_member_company_list(self) -> Dict[str, Any]:
        """회원사 리스트 조회 (ka10102)"""
        return self.investor_api.get_member_company_list()

    # ==================== Ranking API 메서드 (추가) ====================

    def get_bid_ask_volume_top(self, market: str = "ALL") -> Dict[str, Any]:
        """호가잔량 상위 조회 (ka10020)"""
        return self.ranking_api.get_bid_ask_volume_top(market)

    def get_bid_ask_volume_surge(self, market: str = "ALL") -> Dict[str, Any]:
        """호가잔량 급증 조회 (ka10021)"""
        return self.ranking_api.get_bid_ask_volume_surge(market)

    def get_remaining_volume_surge(self, market: str = "ALL") -> Dict[str, Any]:
        """잔량 급증 조회 (ka10022)"""
        return self.ranking_api.get_remaining_volume_surge(market)

    def get_expected_execution_rate_top(self, market: str = "ALL") -> Dict[str, Any]:
        """예상체결률 상위 조회 (ka10029)"""
        return self.ranking_api.get_expected_execution_rate_top(market)

    def get_intraday_investor_trading_top(self, market: str = "ALL") -> Dict[str, Any]:
        """장중 투자자별 매매 상위 조회 (ka10065)"""
        return self.ranking_api.get_intraday_investor_trading_top(market)

    def get_overtime_single_price_rate_ranking(self, market: str = "ALL") -> Dict[str, Any]:
        """시간외 단일가 등락률 순위 조회 (ka10098)"""
        return self.ranking_api.get_overtime_single_price_rate_ranking(market)

    # ==================== Sector API 메서드 (추가) ====================

    def get_sector_program_trading(self, sector_code: str) -> Dict[str, Any]:
        """업종프로그램매매 조회 (ka10010)"""
        return self.sector_api.get_sector_program_trading(sector_code)

    def get_sector_investor_trading(self, sector_code: str) -> Dict[str, Any]:
        """업종별투자자순매수 조회 (ka10051)"""
        return self.sector_api.get_sector_investor_trading(sector_code)

    def get_sector_stock_price(self, sector_code: str = "0001") -> Dict[str, Any]:
        """업종별주가 조회 (ka20002)"""
        return self.sector_api.get_sector_stock_price(sector_code)

    def get_sector_daily_current(self, sector_code: str) -> Dict[str, Any]:
        """업종현재가일별 조회 (ka20009)"""
        return self.sector_api.get_sector_daily_current(sector_code)

    # ==================== PyKIS 호환 API 메서드 ====================

    def get_stock_financial(self, stock_code: str) -> Dict[str, Any]:
        """
        주식 재무 정보 조회 (PyKIS 호환)

        PyKIS의 get_stock_financial()과 호환되는 인터페이스를 제공합니다.
        키움 REST API의 ka10001 (주식기본정보)에서 재무 데이터를 추출합니다.

        Args:
            stock_code: 종목코드 (예: "005930")

        Returns:
            Dict[str, Any]: PyKIS 호환 응답 형식
            {
                "rt_cd": "0",
                "output": [
                    {
                        "stac_yymm": "202512",
                        "eps": "3000",
                        "bps": "45000",
                        "per": "12.50",
                        "pbr": "1.20",
                        ...
                    }
                ]
            }

        Note:
            키움 REST API는 별도의 재무 데이터 TR을 제공하지 않아
            주식기본정보(ka10001)에서 추출 가능한 항목만 반환합니다.
        """
        return self.stock_api.get_stock_financial(stock_code)

    def get_pbar_tratio(self, stock_code: str) -> Dict[str, Any]:
        """
        매물대 분석 (Volume Profile) 조회 (PyKIS 호환)

        PyKIS의 get_pbar_tratio()와 호환되는 인터페이스를 제공합니다.
        일봉 데이터를 활용하여 가격대별 거래량 분포를 추정합니다.

        Args:
            stock_code: 종목코드 (예: "005930")

        Returns:
            Dict[str, Any]: PyKIS 호환 응답 형식
            {
                "rt_cd": "0",
                "output1": {
                    "stck_prpr": "71000",
                    "stck_oprc": "70500",
                    ...
                },
                "output2": [
                    {"vol": "1000000", "prc_rng": "70000-71000", ...},
                    ...
                ]
            }

        Note:
            키움 REST API는 정확한 매물대 API를 제공하지 않아
            일봉 데이터를 가격대별로 집계하여 추정값을 반환합니다.
        """
        return self.program_api.get_pbar_tratio(stock_code)

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
                        "bstp_nmix_oprc": "2500.00",
                        "bstp_nmix_hgpr": "2520.00",
                        "bstp_nmix_lwpr": "2480.00",
                        "bstp_nmix_prpr": "2510.00",
                        "acml_vol": "123456789",
                        "acml_tr_pbmn": "1234567890000",
                    },
                    ...
                ]
            }
        """
        return self.sector_api.get_index_daily_price(index_code, base_date, count)

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
            include_current_entry: 현재가 매물대 진입 포함 ("0"=미포함, "1"=포함)
            pbar_count: 매물대수 (기본값 10)
            cycle: 주기구분 ("50", "100", "150", "200", "250", "300"일)
            exchange: 거래소구분 ("1"=KRX, "2"=NXT, "3"=통합)

        Returns:
            Dict[str, Any]: 매물대 집중 종목 목록
            {
                "rt_cd": "0",
                "prps_cnctr": [
                    {
                        "stk_cd": "005930",
                        "stk_nm": "삼성전자",
                        "cur_prc": "71000",
                        "pric_strt": "70000",  # 매물대 시작가
                        "pric_end": "71500",   # 매물대 종료가
                        "prps_qty": "5",       # 매물대 수
                        "prps_rt": "+60.00"    # 매물집중비율
                    },
                    ...
                ]
            }

        Note:
            이 API는 특정 종목의 매물대가 아닌,
            시장 전체에서 매물대 집중 조건에 부합하는 종목 목록을 반환합니다.
        """
        return self.program_api.get_pbar_concentration(
            market=market,
            concentration_rate=concentration_rate,
            include_current_entry=include_current_entry,
            pbar_count=pbar_count,
            cycle=cycle,
            exchange=exchange,
        )
