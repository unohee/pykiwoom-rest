"""
Order API Module - 주문 관련 API 구현
작성일: 2025-01-27
"""

from typing import Dict, Any, Optional
from .base_api import BaseAPIClient


class OrderAPI(BaseAPIClient):
    """주문 관련 API 클래스"""
    
    def __init__(self, **kwargs):
        """
        초기화
        
        Args:
            kwargs: BaseAPI 초기화 파라미터
        """
        super().__init__(**kwargs)
        self.base_path = "/api/dostk/ordr"
        self.credit_path = "/api/dostk/crdordr"
    
    def buy_stock(
        self, 
        stock_code: str, 
        quantity: int, 
        price: int = 0,
        order_type: str = "00",
        price_type: str = "00"
    ) -> Dict[str, Any]:
        """
        주식 매수주문 (kt10000)
        
        Args:
            stock_code: 종목코드
            quantity: 주문수량
            price: 주문가격 (시장가는 0)
            order_type: 주문구분 (00: 지정가, 01: 시장가)
            price_type: 호가유형
            
        Returns:
            Dict[str, Any]: 주문 결과
        """
        return self.make_request(
            endpoint_key='order',
            tr_id_key='stock_buy',
            params={
                'account_no': self.account_no,
                'stk_cd': stock_code,
                'order_qty': str(quantity),
                'order_prc': str(price),
                'order_tp': order_type,
                'prc_tp': price_type
            }
        )
    
    def sell_stock(
        self,
        stock_code: str,
        quantity: int,
        price: int = 0,
        order_type: str = "00",
        price_type: str = "00"
    ) -> Dict[str, Any]:
        """
        주식 매도주문 (kt10001)
        
        Args:
            stock_code: 종목코드
            quantity: 주문수량
            price: 주문가격 (시장가는 0)
            order_type: 주문구분 (00: 지정가, 01: 시장가)
            price_type: 호가유형
            
        Returns:
            Dict[str, Any]: 주문 결과
        """
        return self.make_request(
            endpoint_key='order',
            tr_id_key='stock_sell',
            params={
                'account_no': self.account_no,
                'stk_cd': stock_code,
                'order_qty': str(quantity),
                'order_prc': str(price),
                'order_tp': order_type,
                'prc_tp': price_type
            }
        )
    
    def modify_order(
        self,
        original_order_no: str,
        stock_code: str,
        quantity: int,
        price: int = 0,
        order_type: str = "00"
    ) -> Dict[str, Any]:
        """
        주식 정정주문 (kt10002)
        
        Args:
            original_order_no: 원주문번호
            stock_code: 종목코드
            quantity: 정정수량
            price: 정정가격
            order_type: 주문구분
            
        Returns:
            Dict[str, Any]: 정정 결과
        """
        return self.make_request(
            endpoint_key='order',
            tr_id_key='stock_modify',
            params={
                'account_no': self.account_no,
                'original_order_no': original_order_no,
                'stk_cd': stock_code,
                'modify_qty': str(quantity),
                'modify_prc': str(price),
                'order_tp': order_type
            }
        )
    
    def cancel_order(
        self,
        original_order_no: str,
        stock_code: str,
        quantity: int
    ) -> Dict[str, Any]:
        """
        주식 취소주문 (kt10003)
        
        Args:
            original_order_no: 원주문번호
            stock_code: 종목코드
            quantity: 취소수량
            
        Returns:
            Dict[str, Any]: 취소 결과
        """
        return self.make_request(
            endpoint_key='order',
            tr_id_key='stock_cancel',
            params={
                'account_no': self.account_no,
                'original_order_no': original_order_no,
                'stk_cd': stock_code,
                'cancel_qty': str(quantity)
            }
        )
    
    def buy_credit(
        self,
        stock_code: str,
        quantity: int,
        price: int = 0,
        credit_type: str = "02",
        order_type: str = "00",
        price_type: str = "00"
    ) -> Dict[str, Any]:
        """
        신용 매수주문 (kt10006)
        
        Args:
            stock_code: 종목코드
            quantity: 주문수량
            price: 주문가격 (시장가는 0)
            credit_type: 신용구분 (02: 자기융자)
            order_type: 주문구분 (00: 지정가, 01: 시장가)
            price_type: 호가유형
            
        Returns:
            Dict[str, Any]: 주문 결과
        """
        return self.make_request(
            endpoint_key='credit_order',
            tr_id_key='credit_buy',
            params={
                'account_no': self.account_no,
                'stk_cd': stock_code,
                'order_qty': str(quantity),
                'order_prc': str(price),
                'credit_tp': credit_type,
                'order_tp': order_type,
                'prc_tp': price_type
            }
        )
    
    def sell_credit(
        self,
        stock_code: str,
        quantity: int,
        price: int = 0,
        credit_type: str = "02",
        order_type: str = "00",
        price_type: str = "00"
    ) -> Dict[str, Any]:
        """
        신용 매도주문 (kt10007)
        
        Args:
            stock_code: 종목코드
            quantity: 주문수량
            price: 주문가격 (시장가는 0)
            credit_type: 신용구분 (02: 자기융자)
            order_type: 주문구분 (00: 지정가, 01: 시장가)
            price_type: 호가유형
            
        Returns:
            Dict[str, Any]: 주문 결과
        """
        return self.make_request(
            endpoint_key='credit_order',
            tr_id_key='credit_sell',
            params={
                'account_no': self.account_no,
                'stk_cd': stock_code,
                'order_qty': str(quantity),
                'order_prc': str(price),
                'credit_tp': credit_type,
                'order_tp': order_type,
                'prc_tp': price_type
            }
        )
    
    def modify_credit_order(
        self,
        original_order_no: str,
        stock_code: str,
        quantity: int,
        price: int = 0,
        order_type: str = "00"
    ) -> Dict[str, Any]:
        """
        신용 정정주문 (kt10008)
        
        Args:
            original_order_no: 원주문번호
            stock_code: 종목코드
            quantity: 정정수량
            price: 정정가격
            order_type: 주문구분
            
        Returns:
            Dict[str, Any]: 정정 결과
        """
        return self.make_request(
            endpoint_key='credit_order',
            tr_id_key='credit_modify',
            params={
                'account_no': self.account_no,
                'original_order_no': original_order_no,
                'stk_cd': stock_code,
                'modify_qty': str(quantity),
                'modify_prc': str(price),
                'order_tp': order_type
            }
        )
    
    def cancel_credit_order(
        self,
        original_order_no: str,
        stock_code: str,
        quantity: int
    ) -> Dict[str, Any]:
        """
        신용 취소주문 (kt10009)
        
        Args:
            original_order_no: 원주문번호
            stock_code: 종목코드
            quantity: 취소수량
            
        Returns:
            Dict[str, Any]: 취소 결과
        """
        return self.make_request(
            endpoint_key='credit_order',
            tr_id_key='credit_cancel',
            params={
                'account_no': self.account_no,
                'original_order_no': original_order_no,
                'stk_cd': stock_code,
                'cancel_qty': str(quantity)
            }
        )
    
    def get_credit_available_stocks(self, market: str = "ALL") -> Dict[str, Any]:
        """
        신용융자 가능종목요청 (kt20016)
        
        Args:
            market: 시장구분 (ALL, KOSPI, KOSDAQ)
            
        Returns:
            Dict[str, Any]: 신용융자 가능 종목 목록
        """
        return self.make_request(
            endpoint_key='credit_order',
            tr_id_key='credit_available_stocks',
            params={'market': market}
        )
    
    def check_credit_available(self, stock_code: str) -> Dict[str, Any]:
        """
        신용융자 가능문의 (kt20017)
        
        Args:
            stock_code: 종목코드
            
        Returns:
            Dict[str, Any]: 신용융자 가능 여부
        """
        return self.make_request(
            endpoint_key='credit_order', 
            tr_id_key='credit_available_check',
            params={'stk_cd': stock_code}
        )