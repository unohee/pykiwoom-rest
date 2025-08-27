"""
Stock Information API
주식 정보 관련 API 클래스
작성일: 2025-01-27
"""

from typing import Dict, Any, Optional
from .kiwoom_base import KiwoomAPIBase


class StockAPI(KiwoomAPIBase):
    """주식 정보 관련 API"""
    
    # TR 코드 매핑
    TR_CODES = {
        'stock_basic_info': 'ka10001',
        'stock_member_info': 'ka10002',
        'execution_info': 'ka10003',
        'stock_quote': 'ka10004',
        'credit_trend': 'ka10013',
        'daily_trading_detail': 'ka10015',
        'new_high_low': 'ka10016',
        'upper_lower_limit': 'ka10017',
        'high_low_approach': 'ka10018',
        'price_fluctuation': 'ka10019',
        'volume_update': 'ka10024',
        'supply_concentration': 'ka10025',
        'high_low_per': 'ka10026',
        'open_price_rate': 'ka10028',
        'member_supply_analysis': 'ka10043',
        'new_previous_execution': 'ka10055',
        'current_previous_execution': 'ka10084',
        'watchlist_info': 'ka10095',
        'stock_info_list': 'ka10099',
        'stock_info_inquiry': 'ka10100',
        'daily_trading_journal': 'ka10170'
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
            tr_code=self.TR_CODES['stock_basic_info'],
            endpoint='stock_info',
            params=params,
            method='GET'
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
            tr_code=self.TR_CODES['stock_quote'],
            endpoint='market_condition',
            params=params,
            method='GET'
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
            tr_code=self.TR_CODES['execution_info'],
            endpoint='stock_info',
            params=params,
            method='GET'
        )
    
    def get_stock_member_info(self, stock_code: str) -> Dict[str, Any]:
        """
        종목별 투자자별 매매동향 (ka10002)
        
        Args:
            stock_code: 종목코드
            
        Returns:
            투자자별 매매동향
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['stock_member_info'],
            endpoint='stock_info',
            params=params,
            method='GET'
        )
    
    def get_credit_trend(self, stock_code: str) -> Dict[str, Any]:
        """
        신용추이 조회 (ka10013)
        
        Args:
            stock_code: 종목코드
            
        Returns:
            신용추이 정보
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['credit_trend'],
            endpoint='stock_info',
            params=params,
            method='GET'
        )
    
    def get_daily_trading_detail(self, stock_code: str) -> Dict[str, Any]:
        """
        일별매매상세 (ka10015)
        
        Args:
            stock_code: 종목코드
            
        Returns:
            일별매매상세 정보
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['daily_trading_detail'],
            endpoint='stock_info',
            params=params,
            method='GET'
        )
    
    def get_new_high_low(self, market: str = "ALL") -> Dict[str, Any]:
        """
        신고가/신저가 조회 (ka10016)
        
        Args:
            market: 시장구분 (ALL, KOSPI, KOSDAQ)
            
        Returns:
            신고가/신저가 목록
        """
        market_code = {
            "ALL": "0000",
            "KOSPI": "0001", 
            "KOSDAQ": "1001"
        }.get(market, "0000")
        
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": market_code
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['new_high_low'],
            endpoint='stock_info',
            params=params,
            method='GET'
        )
    
    def get_upper_lower_limit(self, market: str = "ALL") -> Dict[str, Any]:
        """
        상한/하한가 조회 (ka10017)
        
        Args:
            market: 시장구분
            
        Returns:
            상한/하한가 목록
        """
        market_code = {
            "ALL": "0000",
            "KOSPI": "0001",
            "KOSDAQ": "1001"
        }.get(market, "0000")
        
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": market_code
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['upper_lower_limit'],
            endpoint='stock_info',
            params=params,
            method='GET'
        )
    
    def get_price_fluctuation(self, market: str = "ALL") -> Dict[str, Any]:
        """
        등락률 상위 조회 (ka10019)
        
        Args:
            market: 시장구분
            
        Returns:
            등락률 상위 목록
        """
        market_code = {
            "ALL": "0000",
            "KOSPI": "0001",
            "KOSDAQ": "1001"
        }.get(market, "0000")
        
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": market_code,
            "FID_RANK_SORT_CLS_CODE": "0"
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['price_fluctuation'],
            endpoint='stock_info',
            params=params,
            method='GET'
        )
    
    def get_high_low_approach(self, stock_code: str) -> Dict[str, Any]:
        """
        고가/저가 근접 조회 (ka10018)
        
        Args:
            stock_code: 종목코드
            
        Returns:
            고가/저가 근접 정보
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['high_low_approach'],
            endpoint='stock_info',
            params=params,
            method='GET'
        )
    
    def get_volume_concentration(self, stock_code: str) -> Dict[str, Any]:
        """
        거래량 집중도 조회 (ka10025)
        
        Args:
            stock_code: 종목코드
            
        Returns:
            거래량 집중도 정보
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['supply_concentration'],
            endpoint='stock_info',
            params=params,
            method='GET'
        )
    
    def get_high_low_per(self, market: str = "ALL") -> Dict[str, Any]:
        """
        고가/저가 PER 조회 (ka10026)
        
        Args:
            market: 시장구분
            
        Returns:
            고가/저가 PER 정보
        """
        market_code = {
            "ALL": "0000",
            "KOSPI": "0001",
            "KOSDAQ": "1001"
        }.get(market, "0000")
        
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": market_code
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['high_low_per'],
            endpoint='stock_info',
            params=params,
            method='GET'
        )
    
    def get_current_previous_execution(self, stock_code: str) -> Dict[str, Any]:
        """
        당일/전일 체결 비교 (ka10084)
        
        Args:
            stock_code: 종목코드
            
        Returns:
            당일/전일 체결 비교 정보
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['current_previous_execution'],
            endpoint='stock_info',
            params=params,
            method='GET'
        )
    
    def get_watchlist_info(self, watchlist_code: str = "1") -> Dict[str, Any]:
        """
        관심종목 정보 조회 (ka10095)
        
        Args:
            watchlist_code: 관심종목 그룹코드
            
        Returns:
            관심종목 정보
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": watchlist_code
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['watchlist_info'],
            endpoint='stock_info',
            params=params,
            method='GET'
        )
    
    def get_stock_list(self, market: str = "ALL") -> Dict[str, Any]:
        """
        종목 리스트 조회 (ka10099)
        
        Args:
            market: 시장구분
            
        Returns:
            종목 리스트
        """
        market_code = {
            "ALL": "0000",
            "KOSPI": "0001",
            "KOSDAQ": "1001"
        }.get(market, "0000")
        
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": market_code
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['stock_info_list'],
            endpoint='stock_info',
            params=params,
            method='GET'
        )
    
    def get_stock_info_detail(self, stock_code: str) -> Dict[str, Any]:
        """
        종목 상세정보 조회 (ka10100)
        
        Args:
            stock_code: 종목코드
            
        Returns:
            종목 상세정보
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_tr_request(
            tr_code=self.TR_CODES['stock_info_inquiry'],
            endpoint='stock_info',
            params=params,
            method='GET'
        )