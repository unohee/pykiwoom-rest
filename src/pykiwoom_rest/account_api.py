"""
Account API Module - 계좌 관련 API 구현
작성일: 2025-01-27
"""

from typing import Any, Dict, Optional

from .kiwoom_base import KiwoomAPIBase


class AccountAPI(KiwoomAPIBase):
    """계좌 관련 API 클래스"""

    # TR 코드 매핑
    TR_CODES = {
        "deposit_detail": "kt00001",
        "daily_estimated_asset": "kt00002",
        "estimated_asset": "kt00003",
        "account_evaluation": "kt00004",
        "execution_balance": "kt00005",
        "order_execution_detail": "kt00007",
        "next_day_settlement": "kt00008",
        "order_execution_status": "kt00009",
        "withdrawable_amount": "kt00010",
        "orderable_quantity_margin": "kt00011",
        "orderable_quantity_credit": "kt00012",
        "margin_detail": "kt00013",
        "trading_history": "kt00015",
        "daily_return_detail": "kt00016",
        "current_day_status": "kt00017",
        "balance_detail": "kt00018",
        "unfilled_orders": "ka10075",
        "executed_orders": "ka10076",
        "realized_profit_detail": "ka10077",
        "account_return": "ka10085",
        "unfilled_split_order": "ka10088",
        "daily_trading_diary": "ka10170",
    }

    def get_deposit_detail(self) -> Dict[str, Any]:
        """예수금상세현황요청 (kt00001)"""
        params = {"acnt_no": self.account_no}
        return self.make_tr_request(tr_code=self.TR_CODES["deposit_detail"], endpoint="account", data=params)

    def get_daily_estimated_asset(self, base_date: Optional[str] = None) -> Dict[str, Any]:
        """일별추정예탁자산현황요청 (kt00002)"""
        params = {"acnt_no": self.account_no}
        if base_date:
            params["base_dt"] = base_date
        return self.make_tr_request(tr_code=self.TR_CODES["daily_estimated_asset"], endpoint="account", data=params)

    def get_estimated_asset(self) -> Dict[str, Any]:
        """추정자산조회요청 (kt00003)"""
        params = {"acnt_no": self.account_no}
        return self.make_tr_request(tr_code=self.TR_CODES["estimated_asset"], endpoint="account", data=params)

    def get_account_evaluation(self) -> Dict[str, Any]:
        """계좌평가현황요청 (kt00004)"""
        params = {"acnt_no": self.account_no}
        return self.make_tr_request(tr_code=self.TR_CODES["account_evaluation"], endpoint="account", data=params)

    def get_execution_balance(self) -> Dict[str, Any]:
        """체결잔고요청 (kt00005)"""
        params = {"acnt_no": self.account_no}
        return self.make_tr_request(tr_code=self.TR_CODES["execution_balance"], endpoint="account", data=params)

    def get_order_execution_detail(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """계좌별주문체결내역상세요청 (kt00007)"""
        params = {"acnt_no": self.account_no}
        if start_date:
            params["start_dt"] = start_date
        if end_date:
            params["end_dt"] = end_date
        return self.make_tr_request(tr_code=self.TR_CODES["order_execution_detail"], endpoint="account", data=params)

    def get_next_day_settlement(self) -> Dict[str, Any]:
        """계좌별익일결제예정내역요청 (kt00008)"""
        params = {"acnt_no": self.account_no}
        return self.make_tr_request(tr_code=self.TR_CODES["next_day_settlement"], endpoint="account", data=params)

    def get_order_execution_status(self) -> Dict[str, Any]:
        """계좌별주문체결현황요청 (kt00009)"""
        params = {"acnt_no": self.account_no}
        return self.make_tr_request(tr_code=self.TR_CODES["order_execution_status"], endpoint="account", data=params)

    def get_withdrawable_amount(self) -> Dict[str, Any]:
        """주문인출가능금액요청 (kt00010)"""
        params = {"acnt_no": self.account_no}
        return self.make_tr_request(tr_code=self.TR_CODES["withdrawable_amount"], endpoint="account", data=params)

    def get_orderable_quantity_by_margin(self, stock_code: str, order_price: int) -> Dict[str, Any]:
        """증거금율별주문가능수량조회요청 (kt00011)"""
        params = {
            "acnt_no": self.account_no,
            "stk_cd": self.convert_stock_code_param(stock_code)["stk_cd"],
            "ord_prc": str(order_price),
        }
        return self.make_tr_request(tr_code=self.TR_CODES["orderable_quantity_margin"], endpoint="account", data=params)

    def get_orderable_quantity_by_credit(self, stock_code: str, order_price: int) -> Dict[str, Any]:
        """신용보증금율별주문가능수량조회요청 (kt00012)"""
        params = {
            "acnt_no": self.account_no,
            "stk_cd": self.convert_stock_code_param(stock_code)["stk_cd"],
            "ord_prc": str(order_price),
        }
        return self.make_tr_request(tr_code=self.TR_CODES["orderable_quantity_credit"], endpoint="account", data=params)

    def get_margin_detail(self) -> Dict[str, Any]:
        """증거금세부내역조회요청 (kt00013)"""
        params = {"acnt_no": self.account_no}
        return self.make_tr_request(tr_code=self.TR_CODES["margin_detail"], endpoint="account", data=params)

    def get_trading_history(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """위탁종합거래내역요청 (kt00015)"""
        params = {"acnt_no": self.account_no}
        if start_date:
            params["start_dt"] = start_date
        if end_date:
            params["end_dt"] = end_date
        return self.make_tr_request(tr_code=self.TR_CODES["trading_history"], endpoint="account", data=params)

    def get_daily_return_detail(self, base_date: Optional[str] = None) -> Dict[str, Any]:
        """일별계좌수익률상세현황요청 (kt00016)"""
        params = {"acnt_no": self.account_no}
        if base_date:
            params["base_dt"] = base_date
        return self.make_tr_request(tr_code=self.TR_CODES["daily_return_detail"], endpoint="account", data=params)

    def get_current_day_status(self) -> Dict[str, Any]:
        """계좌별당일현황요청 (kt00017)"""
        params = {"acnt_no": self.account_no}
        return self.make_tr_request(tr_code=self.TR_CODES["current_day_status"], endpoint="account", data=params)

    def get_balance_detail(self) -> Dict[str, Any]:
        """계좌평가잔고내역요청 (kt00018)"""
        params = {"acnt_no": self.account_no}
        return self.make_tr_request(tr_code=self.TR_CODES["balance_detail"], endpoint="account", data=params)

    def get_unfilled_orders(self) -> Dict[str, Any]:
        """미체결요청 (ka10075)"""
        params = {"acnt_no": self.account_no}
        return self.make_tr_request(tr_code=self.TR_CODES["unfilled_orders"], endpoint="account", data=params)

    def get_executed_orders(self) -> Dict[str, Any]:
        """체결요청 (ka10076)"""
        params = {"acnt_no": self.account_no}
        return self.make_tr_request(tr_code=self.TR_CODES["executed_orders"], endpoint="account", data=params)

    def get_realized_profit_detail(self) -> Dict[str, Any]:
        """당일실현손익상세요청 (ka10077)"""
        params = {"acnt_no": self.account_no}
        return self.make_tr_request(tr_code=self.TR_CODES["realized_profit_detail"], endpoint="account", data=params)

    def get_account_return(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """계좌수익률요청 (ka10085)"""
        params = {"acnt_no": self.account_no}
        if start_date:
            params["start_dt"] = start_date
        if end_date:
            params["end_dt"] = end_date
        return self.make_tr_request(tr_code=self.TR_CODES["account_return"], endpoint="account", data=params)

    def get_unfilled_split_order_detail(self, order_no: str) -> Dict[str, Any]:
        """미체결 분할주문 상세 (ka10088)"""
        params = {"acnt_no": self.account_no, "ord_no": order_no}
        return self.make_tr_request(tr_code=self.TR_CODES["unfilled_split_order"], endpoint="account", data=params)

    def get_daily_trading_diary(self, base_date: Optional[str] = None) -> Dict[str, Any]:
        """당일매매일지요청 (ka10170)"""
        params = {"acnt_no": self.account_no}
        if base_date:
            params["base_dt"] = base_date
        return self.make_tr_request(tr_code=self.TR_CODES["daily_trading_diary"], endpoint="account", data=params)
