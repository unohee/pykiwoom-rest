"""
Ranking Information API
순위 정보 관련 API 클래스
작성일: 2025-01-27
"""

from typing import Dict, Any
from .kiwoom_base import KiwoomAPIBase


class RankingAPI(KiwoomAPIBase):
    """순위 정보 관련 API"""
    
    # TR 코드 매핑
    TR_CODES = {
        'quote_volume_top': 'ka10020',
        'quote_volume_surge': 'ka10021',
        'volume_rate_surge': 'ka10022',
        'trading_volume_surge': 'ka10023',
        'previous_day_rate_top': 'ka10027',
        'expected_rate_top': 'ka10029',
        'daily_volume_top': 'ka10030',
        'previous_volume_top': 'ka10031',
        'trading_amount_top': 'ka10032',
        'credit_ratio_top': 'ka10033',
        'foreign_period_trading_top': 'ka10034',
        'foreign_continuous_trading_top': 'ka10035',
        'foreign_limit_exhaustion_top': 'ka10036',
        'foreign_window_trading_top': 'ka10037',
        'stock_securities_ranking': 'ka10038',
        'securities_trading_top': 'ka10039',
        'daily_major_trader': 'ka10040',
        'net_buy_trader_ranking': 'ka10042',
        'daily_top_departure': 'ka10053',
        'same_net_trading_ranking': 'ka10062',
        'investor_trading_top': 'ka10065',
        'overtime_rate_ranking': 'ka10098'
    }
    
    def _get_market_code(self, market: str) -> str:
        """시장 코드 변환 헬퍼"""
        return {
            "ALL": "0000",
            "KOSPI": "0001",
            "KOSDAQ": "1001"
        }.get(market, "0000")
    
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
            "FID_PRC_CLS_CODE": "1"
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['quote_volume_top'],
            endpoint='ranking',
            params=params,
            method='GET'
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
            "FID_INPUT_CNT_1": str(count)
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['quote_volume_surge'],
            endpoint='ranking',
            params=params,
            method='GET'
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
            "FID_INPUT_CNT_1": str(count)
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['volume_rate_surge'],
            endpoint='ranking',
            params=params,
            method='GET'
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
            "FID_INPUT_CNT_1": str(count)
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['trading_volume_surge'],
            endpoint='ranking',
            params=params,
            method='GET'
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
            "FID_INPUT_CNT_1": str(count)
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['previous_day_rate_top'],
            endpoint='ranking',
            params=params,
            method='GET'
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
            "FID_INPUT_CNT_1": str(count)
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['expected_rate_top'],
            endpoint='ranking',
            params=params,
            method='GET'
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
            "FID_INPUT_CNT_1": str(count)
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['daily_volume_top'],
            endpoint='ranking',
            params=params,
            method='GET'
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
            "FID_INPUT_CNT_1": str(count)
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['trading_amount_top'],
            endpoint='ranking',
            params=params,
            method='GET'
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
            "FID_INPUT_CNT_1": str(count)
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['credit_ratio_top'],
            endpoint='ranking',
            params=params,
            method='GET'
        )
    
    def get_foreign_period_trading_top(self, market: str = "ALL", period: str = "1", count: int = 50) -> Dict[str, Any]:
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
            "FID_INPUT_OPTION_1": period
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['foreign_period_trading_top'],
            endpoint='ranking',
            params=params,
            method='GET'
        )
    
    def get_foreign_continuous_trading_top(self, market: str = "ALL", count: int = 50) -> Dict[str, Any]:
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
            "FID_INPUT_CNT_1": str(count)
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['foreign_continuous_trading_top'],
            endpoint='ranking',
            params=params,
            method='GET'
        )
    
    def get_foreign_limit_exhaustion_top(self, market: str = "ALL", count: int = 50) -> Dict[str, Any]:
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
            "FID_INPUT_CNT_1": str(count)
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['foreign_limit_exhaustion_top'],
            endpoint='ranking',
            params=params,
            method='GET'
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
            "FID_INPUT_CNT_1": str(count)
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['securities_trading_top'],
            endpoint='ranking',
            params=params,
            method='GET'
        )
    
    def get_daily_major_traders(self, stock_code: str) -> Dict[str, Any]:
        """
        당일 주요 거래원 조회 (ka10040)
        
        Args:
            stock_code: 종목코드
            
        Returns:
            당일 주요 거래원 정보
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['daily_major_trader'],
            endpoint='ranking',
            params=params,
            method='GET'
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
            "FID_INPUT_CNT_1": str(count)
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['net_buy_trader_ranking'],
            endpoint='ranking',
            params=params,
            method='GET'
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
            "FID_INPUT_CNT_1": str(count)
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['investor_trading_top'],
            endpoint='ranking',
            params=params,
            method='GET'
        )
    
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
            "FID_INPUT_CNT_1": str(count)
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['overtime_rate_ranking'],
            endpoint='ranking',
            params=params,
            method='GET'
        )