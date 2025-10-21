"""
통합 KiwoomRest 클래스 - API Facade 기반
기존 KiwoomRest의 통합 파사드 버전

작성일: 2025-01-28
목적:
- 모든 API 호출을 단일 파사드로 통합
- Rate Limiting 중앙 집중 관리
- 기존 인터페이스 완전 호환
- 싱글턴 패턴으로 인스턴스 관리
"""

from typing import Dict, Any, Optional
from .unified_kiwoom_base import UnifiedKiwoomAPIBase
from .api_facade import RequestPriority
from .stock_api import StockAPI
from .chart_api import ChartAPI
from .ranking_api import RankingAPI
from .account_api import AccountAPI
from .order_api import OrderAPI
from .sector_api import SectorAPI


class UnifiedKiwoomRest:
    """
    키움증권 REST API 통합 클래스 (Facade 기반)
    모든 API 호출이 단일 파사드를 통해 Rate Limiting 관리됨
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
        credentials_list: list = None
    ):
        """
        초기화

        Args:
            account_no: 계좌번호
            appkey: 앱키
            appsecret: 앱시크릿
            env_path: .env 파일 경로
            use_mock: 모의투자 API 사용 여부
            rate_limit: 초당 최대 요청 수
            max_retries: 최대 재시도 횟수
            enable_rate_optimizer: Rate limiting 최적화 활성화
            credentials_list: 다중 크레덴셜 리스트
        """

        # 통합 base 클래스 초기화
        self.api_base = UnifiedKiwoomAPIBase(
            account_no=account_no,
            appkey=appkey,
            appsecret=appsecret,
            env_path=env_path,
            use_mock=use_mock,
            rate_limit=rate_limit,
            max_retries=max_retries,
            enable_rate_optimizer=enable_rate_optimizer,
            credentials_list=credentials_list
        )

        # 공통 설정 준비
        common_config = {
            'account_no': account_no,
            'appkey': appkey,
            'appsecret': appsecret,
            'env_path': env_path,
            'use_mock': use_mock,
            'rate_limit': rate_limit,
            'max_retries': max_retries,
            'enable_rate_optimizer': enable_rate_optimizer,
            'credentials_list': credentials_list
        }

        # 기존 API 클래스들 초기화 (Facade 공유)
        self.stock_api = StockAPI(**common_config)
        self.chart_api = ChartAPI(**common_config)
        self.ranking_api = RankingAPI(**common_config)
        self.account_api = AccountAPI(**common_config)
        self.order_api = OrderAPI(**common_config)
        self.sector_api = SectorAPI(**common_config)

        # 인증 정보 동기화
        self._sync_authentication()

    def _sync_authentication(self):
        """인증 정보 동기화 (모든 API 클래스가 같은 Facade 사용)"""
        # Facade가 싱글턴이므로 자동으로 인증 정보가 공유됨
        pass

    # ========== 기존 메서드들 - 완전 호환성 유지 ==========

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
        """주식외국인종목별매매동향 조회"""
        return self.stock_api.get_foreign_trading(stock_code)

    def get_program_trading_daily(self, stock_code: str) -> Dict[str, Any]:
        """종목일별프로그램매매추이요청"""
        return self.stock_api.get_program_trading_daily(stock_code)

    def get_institutional_trading_trend(self, stock_code: str, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """종목별기관매매추이요청"""
        return self.stock_api.get_institutional_trading_trend(stock_code, start_date, end_date)

    # ========== 차트 데이터 메서드 ==========

    def get_tick_chart(self, stock_code: str, count: int = 100) -> Dict[str, Any]:
        """틱 차트 조회"""
        return self.chart_api.get_tick_chart(stock_code, count)

    def get_minute_chart(
        self,
        stock_code: str,
        interval: int = 1,
        start_date: str = None,
        end_date: str = None,
        count: int = 100
    ) -> Dict[str, Any]:
        """분봉 차트 조회"""
        return self.chart_api.get_minute_chart(stock_code, interval, start_date, end_date, count)

    def get_daily_chart(
        self,
        stock_code: str,
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """일봉 차트 조회"""
        return self.chart_api.get_daily_chart(stock_code, start_date, end_date)

    def get_weekly_chart(
        self,
        stock_code: str,
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """주봉 차트 조회"""
        return self.chart_api.get_weekly_chart(stock_code, start_date, end_date)

    def get_monthly_chart(
        self,
        stock_code: str,
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """월봉 차트 조회"""
        return self.chart_api.get_monthly_chart(stock_code, start_date, end_date)

    def get_yearly_chart(
        self,
        stock_code: str,
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """년봉 차트 조회"""
        return self.chart_api.get_yearly_chart(stock_code, start_date, end_date)

    # ========== 순위 정보 메서드 ==========

    def get_volume_top(self, market: str = "ALL", count: int = 50) -> Dict[str, Any]:
        """호가잔량 상위 조회"""
        return self.ranking_api.get_volume_top(market, count)

    def get_hourly_program_trading(self, stock_code: str, date: str, amount_or_quantity: str = "1") -> Dict[str, Any]:
        """종목시간별 프로그램매매 추이요청"""
        return self.ranking_api.get_hourly_program_trading(stock_code, date, amount_or_quantity)

    def get_hourly_program_trading_paginated(
        self,
        stock_code: str,
        date: str,
        amount_or_quantity: str = "1",
        max_records: int = None
    ) -> Dict[str, Any]:
        """종목시간별 프로그램매매 추이요청 (페이지네이션)"""
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

    # ========== 계좌 관련 메서드 ==========

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

    def get_account_return(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """계좌수익률요청"""
        return self.account_api.get_account_return(start_date, end_date)

    # ========== 주문 관련 메서드 ==========

    def buy_stock(self, stock_code: str, quantity: int, price: int = 0,
                  order_type: str = "00", price_type: str = "00") -> Dict[str, Any]:
        """주식 매수주문"""
        return self.order_api.buy_stock(stock_code, quantity, price, order_type, price_type)

    def sell_stock(self, stock_code: str, quantity: int, price: int = 0,
                   order_type: str = "00", price_type: str = "00") -> Dict[str, Any]:
        """주식 매도주문"""
        return self.order_api.sell_stock(stock_code, quantity, price, order_type, price_type)

    def modify_order(self, original_order_no: str, stock_code: str,
                     quantity: int, price: int = 0, order_type: str = "00") -> Dict[str, Any]:
        """주식 정정주문"""
        return self.order_api.modify_order(original_order_no, stock_code, quantity, price, order_type)

    def cancel_order(self, original_order_no: str, stock_code: str, quantity: int) -> Dict[str, Any]:
        """주식 취소주문"""
        return self.order_api.cancel_order(original_order_no, stock_code, quantity)

    # ========== 업종 관련 메서드 ==========

    def get_sector_current_price(self, sector_code: str = "0001") -> Dict[str, Any]:
        """업종현재가요청"""
        return self.sector_api.get_sector_current_price(sector_code)

    def get_all_sector_index(self) -> Dict[str, Any]:
        """전업종지수요청"""
        return self.sector_api.get_all_sector_index()

    def get_sector_daily_chart(self, sector_code: str, start_date: Optional[str] = None,
                               end_date: Optional[str] = None) -> Dict[str, Any]:
        """업종일봉조회요청"""
        return self.sector_api.get_sector_daily_chart(sector_code, start_date, end_date)

    # ========== 페이지네이션 메서드 ==========

    def get_minute_chart_paginated(
        self,
        stock_code: str,
        interval: int = 1,
        start_date: str = None,
        end_date: str = None,
        max_records: int = 1000
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
        max_pages: int = 20
    ) -> Dict[str, Any]:
        """특정 날짜의 분봉 데이터 조회"""
        return self.chart_api.get_minute_chart_with_date(
            stock_code, interval, target_date, max_pages
        )

    # ========== 유틸리티 메서드 ==========

    def verify_connection(self) -> Dict[str, Any]:
        """API 연결 상태 확인"""
        return self.api_base.health_check()

    def get_stats(self) -> Dict[str, Any]:
        """통합 통계 반환 (Facade 통계 포함)"""
        base_stats = self.api_base.get_stats()

        return {
            'unified_kiwoom_rest': {
                'version': '2.0-facade',
                'total_api_modules': 6,
                'facade_enabled': True
            },
            **base_stats,
            'individual_api_stats': {
                'stock_api_stats': self.stock_api.get_stats(),
                'chart_api_stats': self.chart_api.get_stats(),
                'ranking_api_stats': self.ranking_api.get_stats(),
                'account_api_stats': self.account_api.get_stats(),
                'order_api_stats': self.order_api.get_stats(),
                'sector_api_stats': self.sector_api.get_stats()
            }
        }

    def get_facade_stats(self) -> Dict[str, Any]:
        """Facade 통계 전용 메서드"""
        return self.api_base.facade.get_comprehensive_stats()

    def reset_rate_limiter(self):
        """Rate limiter 초기화"""
        # Facade의 rate limiter 리셋 기능이 있다면 사용
        if hasattr(self.api_base.facade, 'global_rate_limiter'):
            self.api_base.facade.global_rate_limiter.request_times.clear()

    def close(self):
        """모든 세션 종료"""
        self.api_base.close()

    def __enter__(self):
        """Context manager 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료"""
        self.close()

    # ========== 직접 API 접근 프로퍼티 ==========

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
    def facade(self):
        """API Facade 직접 접근"""
        return self.api_base.facade