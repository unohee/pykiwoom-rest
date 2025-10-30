"""
Order API Module - 주문 관련 API 구현
작성일: 2025-01-27
"""

from typing import Any, Dict

from .kiwoom_base import KiwoomAPIBase


class OrderAPI(KiwoomAPIBase):
    """주문 관련 API 클래스"""

    # TR 코드 매핑
    TR_CODES = {
        "stock_buy": "kt10000",
        "stock_sell": "kt10001",
        "stock_modify": "kt10002",
        "stock_cancel": "kt10003",
        "credit_buy": "kt10006",
        "credit_sell": "kt10007",
        "credit_modify": "kt10008",
        "credit_cancel": "kt10009",
        "credit_available_stocks": "kt20016",
        "credit_available_check": "kt20017",
    }

    def buy_stock(
        self,
        stock_code: str,
        quantity: int,
        price: int = 0,
        order_type: str = "00",
        price_type: str = "00",
    ) -> Dict[str, Any]:
        """주식 매수주문 (kt10000)"""
        params = {
            "acnt_no": self.account_no,
            "stk_cd": self.convert_stock_code_param(stock_code)["stk_cd"],
            "ord_qty": str(quantity),
            "ord_prc": str(price),
            "ord_tp": order_type,
            "prc_tp": price_type,
        }
        return self.make_tr_request(tr_id=self.TR_CODES["stock_buy"], data=params)

    def sell_stock(
        self,
        stock_code: str,
        quantity: int,
        price: int = 0,
        order_type: str = "00",
        price_type: str = "00",
    ) -> Dict[str, Any]:
        """주식 매도주문 (kt10001)"""
        params = {
            "acnt_no": self.account_no,
            "stk_cd": self.convert_stock_code_param(stock_code)["stk_cd"],
            "ord_qty": str(quantity),
            "ord_prc": str(price),
            "ord_tp": order_type,
            "prc_tp": price_type,
        }
        return self.make_tr_request(tr_id=self.TR_CODES["stock_sell"], data=params)

    def modify_order(
        self,
        original_order_no: str,
        stock_code: str,
        quantity: int,
        price: int = 0,
        order_type: str = "00",
    ) -> Dict[str, Any]:
        """주식 정정주문 (kt10002)"""
        params = {
            "acnt_no": self.account_no,
            "orgn_ord_no": original_order_no,
            "stk_cd": self.convert_stock_code_param(stock_code)["stk_cd"],
            "mdf_qty": str(quantity),
            "mdf_prc": str(price),
            "ord_tp": order_type,
        }
        return self.make_tr_request(tr_id=self.TR_CODES["stock_modify"], data=params)

    def cancel_order(
        self, original_order_no: str, stock_code: str, quantity: int
    ) -> Dict[str, Any]:
        """주식 취소주문 (kt10003)"""
        params = {
            "acnt_no": self.account_no,
            "orgn_ord_no": original_order_no,
            "stk_cd": self.convert_stock_code_param(stock_code)["stk_cd"],
            "cncl_qty": str(quantity),
        }
        return self.make_tr_request(tr_id=self.TR_CODES["stock_cancel"], data=params)

    def buy_credit(
        self,
        stock_code: str,
        quantity: int,
        price: int = 0,
        credit_type: str = "02",
        order_type: str = "00",
        price_type: str = "00",
    ) -> Dict[str, Any]:
        """신용 매수주문 (kt10006)"""
        params = {
            "acnt_no": self.account_no,
            "stk_cd": self.convert_stock_code_param(stock_code)["stk_cd"],
            "ord_qty": str(quantity),
            "ord_prc": str(price),
            "crdt_tp": credit_type,
            "ord_tp": order_type,
            "prc_tp": price_type,
        }
        return self.make_tr_request(tr_id=self.TR_CODES["credit_buy"], data=params)

    def sell_credit(
        self,
        stock_code: str,
        quantity: int,
        price: int = 0,
        credit_type: str = "02",
        order_type: str = "00",
        price_type: str = "00",
    ) -> Dict[str, Any]:
        """신용 매도주문 (kt10007)"""
        params = {
            "acnt_no": self.account_no,
            "stk_cd": self.convert_stock_code_param(stock_code)["stk_cd"],
            "ord_qty": str(quantity),
            "ord_prc": str(price),
            "crdt_tp": credit_type,
            "ord_tp": order_type,
            "prc_tp": price_type,
        }
        return self.make_tr_request(tr_id=self.TR_CODES["credit_sell"], data=params)

    def modify_credit_order(
        self,
        original_order_no: str,
        stock_code: str,
        quantity: int,
        price: int = 0,
        order_type: str = "00",
    ) -> Dict[str, Any]:
        """신용 정정주문 (kt10008)"""
        params = {
            "acnt_no": self.account_no,
            "orgn_ord_no": original_order_no,
            "stk_cd": self.convert_stock_code_param(stock_code)["stk_cd"],
            "mdf_qty": str(quantity),
            "mdf_prc": str(price),
            "ord_tp": order_type,
        }
        return self.make_tr_request(tr_id=self.TR_CODES["credit_modify"], data=params)

    def cancel_credit_order(
        self, original_order_no: str, stock_code: str, quantity: int
    ) -> Dict[str, Any]:
        """신용 취소주문 (kt10009)"""
        params = {
            "acnt_no": self.account_no,
            "orgn_ord_no": original_order_no,
            "stk_cd": self.convert_stock_code_param(stock_code)["stk_cd"],
            "cncl_qty": str(quantity),
        }
        return self.make_tr_request(tr_id=self.TR_CODES["credit_cancel"], data=params)

    def get_credit_available_stocks(self, market: str = "ALL") -> Dict[str, Any]:
        """신용융자 가능종목요청 (kt20016)"""
        params = {"mrkt_tp": self.convert_market_code(market)}
        return self.make_tr_request(
            tr_id=self.TR_CODES["credit_available_stocks"], data=params
        )

    def check_credit_available(self, stock_code: str) -> Dict[str, Any]:
        """신용융자 가능문의 (kt20017)"""
        params = {"stk_cd": self.convert_stock_code_param(stock_code)["stk_cd"]}
        return self.make_tr_request(
            tr_id=self.TR_CODES["credit_available_check"], data=params
        )
