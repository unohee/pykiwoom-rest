"""
KiwoomRest - Unified Facade using New Modular Architecture
기존 인터페이스를 유지하면서 새로운 아키텍처 사용
작성일: 2025-01-27
"""

from typing import Dict, Any, Optional
from .stock_api import StockAPI
from .chart_api import ChartAPI
from .ranking_api import RankingAPI


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
        max_retries: int = 3
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
        """
        # 공통 설정
        common_config = {
            'account_no': account_no,
            'appkey': appkey,
            'appsecret': appsecret,
            'env_path': env_path,
            'use_mock': use_mock,
            'rate_limit': rate_limit,
            'max_retries': max_retries
        }
        
        # 모듈러 API 클래스들 초기화
        self.stock_api = StockAPI(**common_config)
        self.chart_api = ChartAPI(**common_config)
        self.ranking_api = RankingAPI(**common_config)
        
        # 인증 정보 공유
        self._sync_authentication()
        
    def _sync_authentication(self):
        """인증 정보 동기화 (토큰 공유)"""
        # 첫 번째 API 객체의 토큰을 다른 객체들과 공유
        base_token = None
        if hasattr(self.stock_api, 'access_token') and self.stock_api.access_token:
            base_token = self.stock_api.access_token
            
        for api in [self.chart_api, self.ranking_api]:
            if base_token:
                api.access_token = base_token
                api.token_expires = self.stock_api.token_expires
    
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
    
    # ========== 차트 데이터 메서드 (Legacy Compatible) ==========
    
    def get_tick_chart(self, stock_code: str, count: int = 100) -> Dict[str, Any]:
        """틱 차트 조회"""
        return self.chart_api.get_tick_chart(stock_code, count)
    
    def get_minute_chart(
        self,
        stock_code: str,
        interval: int = 1,
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """분봉 차트 조회"""
        return self.chart_api.get_minute_chart(stock_code, interval, start_date, end_date)
    
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
    
    # ========== 순위 정보 메서드 (Legacy Compatible) ==========
    
    def get_volume_top(self, market: str = "ALL", count: int = 50) -> Dict[str, Any]:
        """호가잔량 상위 조회"""
        return self.ranking_api.get_volume_top(market, count)
    
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
    
    # ========== 새로운 고급 기능 ==========
    
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
    
    # ========== 유틸리티 메서드 ==========
    
    def to_dataframe(self, response: Dict[str, Any], output_key: str = None, numeric_fields: list = None):
        """API 응답을 DataFrame으로 변환"""
        # 첫 번째 API 객체의 메서드 사용
        return self.stock_api.to_dataframe(response, output_key, numeric_fields)
    
    def verify_connection(self) -> Dict[str, Any]:
        """API 연결 상태 확인"""
        return self.stock_api.health_check()
    
    def get_stats(self) -> Dict[str, Any]:
        """API 호출 통계 반환"""
        return {
            'stock_api_stats': self.stock_api.get_stats(),
            'chart_api_stats': self.chart_api.get_stats(),
            'ranking_api_stats': self.ranking_api.get_stats(),
            'total_requests': sum([
                self.stock_api.get_stats()['request_count'],
                self.chart_api.get_stats()['request_count'],
                self.ranking_api.get_stats()['request_count']
            ]),
            'total_errors': sum([
                self.stock_api.get_stats()['error_count'],
                self.chart_api.get_stats()['error_count'],
                self.ranking_api.get_stats()['error_count']
            ])
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