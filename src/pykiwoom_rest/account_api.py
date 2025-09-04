"""
Account API Module - 계좌 관련 API 구현
작성일: 2025-01-27
"""

from typing import Dict, Any, Optional
from .base_api import BaseAPIClient


class AccountAPI(BaseAPIClient):
    """계좌 관련 API 클래스"""
    
    def __init__(self, **kwargs):
        """
        초기화
        
        Args:
            kwargs: BaseAPI 초기화 파라미터
        """
        super().__init__(**kwargs)
        self.base_path = "/api/dostk/acnt"
    
    def get_deposit_detail(self) -> Dict[str, Any]:
        """
        예수금상세현황요청 (kt00001)
        
        Returns:
            Dict[str, Any]: 예수금 상세 정보
        """
        return self.make_request(
            endpoint_key='account',
            tr_id_key='deposit_detail',
            params={'account_no': self.account_no}
        )
    
    def get_daily_estimated_asset(self, base_date: Optional[str] = None) -> Dict[str, Any]:
        """
        일별추정예탁자산현황요청 (kt00002)
        
        Args:
            base_date: 기준일자 (YYYYMMDD)
            
        Returns:
            Dict[str, Any]: 일별 추정 예탁자산 현황
        """
        params = {'account_no': self.account_no}
        if base_date:
            params['base_dt'] = base_date
            
        return self.make_request(
            endpoint_key='account',
            tr_id_key='daily_estimated_asset',
            params=params
        )
    
    def get_estimated_asset(self) -> Dict[str, Any]:
        """
        추정자산조회요청 (kt00003)
        
        Returns:
            Dict[str, Any]: 추정 자산 정보
        """
        return self.make_request(
            endpoint_key='account',
            tr_id_key='estimated_asset',
            params={'account_no': self.account_no}
        )
    
    def get_account_evaluation(self) -> Dict[str, Any]:
        """
        계좌평가현황요청 (kt00004)
        
        Returns:
            Dict[str, Any]: 계좌 평가 현황
        """
        return self.make_request(
            endpoint_key='account',
            tr_id_key='account_evaluation',
            params={'account_no': self.account_no}
        )
    
    def get_execution_balance(self) -> Dict[str, Any]:
        """
        체결잔고요청 (kt00005)
        
        Returns:
            Dict[str, Any]: 체결 잔고 정보
        """
        return self.make_request(
            endpoint_key='account',
            tr_id_key='execution_balance',
            params={'account_no': self.account_no}
        )
    
    def get_order_execution_detail(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        계좌별주문체결내역상세요청 (kt00007)
        
        Args:
            start_date: 시작일자 (YYYYMMDD)
            end_date: 종료일자 (YYYYMMDD)
            
        Returns:
            Dict[str, Any]: 주문체결 내역 상세
        """
        params = {'account_no': self.account_no}
        if start_date:
            params['start_dt'] = start_date
        if end_date:
            params['end_dt'] = end_date
            
        return self.make_request(
            endpoint_key='account',
            tr_id_key='order_execution_detail',
            params=params
        )
    
    def get_next_day_settlement(self) -> Dict[str, Any]:
        """
        계좌별익일결제예정내역요청 (kt00008)
        
        Returns:
            Dict[str, Any]: 익일 결제 예정 내역
        """
        return self.make_request(
            endpoint_key='account',
            tr_id_key='next_day_settlement',
            params={'account_no': self.account_no}
        )
    
    def get_order_execution_status(self) -> Dict[str, Any]:
        """
        계좌별주문체결현황요청 (kt00009)
        
        Returns:
            Dict[str, Any]: 주문체결 현황
        """
        return self.make_request(
            endpoint_key='account',
            tr_id_key='order_execution_status',
            params={'account_no': self.account_no}
        )
    
    def get_withdrawable_amount(self) -> Dict[str, Any]:
        """
        주문인출가능금액요청 (kt00010)
        
        Returns:
            Dict[str, Any]: 인출 가능 금액
        """
        return self.make_request(
            endpoint_key='account',
            tr_id_key='withdrawable_amount',
            params={'account_no': self.account_no}
        )
    
    def get_orderable_quantity_by_margin(self, stock_code: str, order_price: int) -> Dict[str, Any]:
        """
        증거금율별주문가능수량조회요청 (kt00011)
        
        Args:
            stock_code: 종목코드
            order_price: 주문가격
            
        Returns:
            Dict[str, Any]: 주문 가능 수량
        """
        return self.make_request(
            endpoint_key='account',
            tr_id_key='orderable_quantity_margin',
            params={
                'account_no': self.account_no,
                'stk_cd': stock_code,
                'order_prc': str(order_price)
            }
        )
    
    def get_orderable_quantity_by_credit(self, stock_code: str, order_price: int) -> Dict[str, Any]:
        """
        신용보증금율별주문가능수량조회요청 (kt00012)
        
        Args:
            stock_code: 종목코드
            order_price: 주문가격
            
        Returns:
            Dict[str, Any]: 신용 주문 가능 수량
        """
        return self.make_request(
            endpoint_key='account',
            tr_id_key='orderable_quantity_credit',
            params={
                'account_no': self.account_no,
                'stk_cd': stock_code,
                'order_prc': str(order_price)
            }
        )
    
    def get_margin_detail(self) -> Dict[str, Any]:
        """
        증거금세부내역조회요청 (kt00013)
        
        Returns:
            Dict[str, Any]: 증거금 세부 내역
        """
        return self.make_request(
            endpoint_key='account',
            tr_id_key='margin_detail',
            params={'account_no': self.account_no}
        )
    
    def get_trading_history(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        위탁종합거래내역요청 (kt00015)
        
        Args:
            start_date: 시작일자 (YYYYMMDD)
            end_date: 종료일자 (YYYYMMDD)
            
        Returns:
            Dict[str, Any]: 종합 거래 내역
        """
        params = {'account_no': self.account_no}
        if start_date:
            params['start_dt'] = start_date
        if end_date:
            params['end_dt'] = end_date
            
        return self.make_request(
            endpoint_key='account',
            tr_id_key='trading_history',
            params=params
        )
    
    def get_daily_return_detail(self, base_date: Optional[str] = None) -> Dict[str, Any]:
        """
        일별계좌수익률상세현황요청 (kt00016)
        
        Args:
            base_date: 기준일자 (YYYYMMDD)
            
        Returns:
            Dict[str, Any]: 일별 수익률 상세
        """
        params = {'account_no': self.account_no}
        if base_date:
            params['base_dt'] = base_date
            
        return self.make_request(
            endpoint_key='account',
            tr_id_key='daily_return_detail',
            params=params
        )
    
    def get_current_day_status(self) -> Dict[str, Any]:
        """
        계좌별당일현황요청 (kt00017)
        
        Returns:
            Dict[str, Any]: 당일 현황
        """
        return self.make_request(
            endpoint_key='account',
            tr_id_key='current_day_status',
            params={'account_no': self.account_no}
        )
    
    def get_balance_detail(self) -> Dict[str, Any]:
        """
        계좌평가잔고내역요청 (kt00018)
        
        Returns:
            Dict[str, Any]: 평가잔고 내역
        """
        return self.make_request(
            endpoint_key='account',
            tr_id_key='balance_detail',
            params={'account_no': self.account_no}
        )
    
    def get_unfilled_orders(self) -> Dict[str, Any]:
        """
        미체결요청 (ka10075)
        
        Returns:
            Dict[str, Any]: 미체결 주문 목록
        """
        return self.make_request(
            endpoint_key='account',
            tr_id_key='unfilled_orders',
            params={'account_no': self.account_no}
        )
    
    def get_executed_orders(self) -> Dict[str, Any]:
        """
        체결요청 (ka10076)
        
        Returns:
            Dict[str, Any]: 체결된 주문 목록
        """
        return self.make_request(
            endpoint_key='account',
            tr_id_key='executed_orders',
            params={'account_no': self.account_no}
        )
    
    def get_realized_profit_detail(self) -> Dict[str, Any]:
        """
        당일실현손익상세요청 (ka10077)
        
        Returns:
            Dict[str, Any]: 당일 실현손익 상세
        """
        return self.make_request(
            endpoint_key='account',
            tr_id_key='realized_profit_detail',
            params={'account_no': self.account_no}
        )
    
    def get_account_return(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        계좌수익률요청 (ka10085)
        
        Args:
            start_date: 시작일자 (YYYYMMDD)
            end_date: 종료일자 (YYYYMMDD)
            
        Returns:
            Dict[str, Any]: 계좌 수익률
        """
        params = {'account_no': self.account_no}
        if start_date:
            params['start_dt'] = start_date
        if end_date:
            params['end_dt'] = end_date
            
        return self.make_request(
            endpoint_key='account',
            tr_id_key='account_return',
            params=params
        )
    
    def get_unfilled_split_order_detail(self, order_no: str) -> Dict[str, Any]:
        """
        미체결 분할주문 상세 (ka10088)
        
        Args:
            order_no: 주문번호
            
        Returns:
            Dict[str, Any]: 분할주문 상세
        """
        return self.make_request(
            endpoint_key='account',
            tr_id_key='unfilled_split_order',
            params={
                'account_no': self.account_no,
                'order_no': order_no
            }
        )
    
    def get_daily_trading_diary(self, base_date: Optional[str] = None) -> Dict[str, Any]:
        """
        당일매매일지요청 (ka10170)
        
        Args:
            base_date: 기준일자 (YYYYMMDD)
            
        Returns:
            Dict[str, Any]: 당일 매매일지
        """
        params = {'account_no': self.account_no}
        if base_date:
            params['base_dt'] = base_date
            
        return self.make_request(
            endpoint_key='account',
            tr_id_key='daily_trading_diary',
            params=params
        )