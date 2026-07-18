"""
Order API Module - 주문 관련 API 구현
작성일: 2025-01-27
"""

from typing import Any, Dict

from .kiwoom_base import KiwoomAPIBase


class OrderAPI(KiwoomAPIBase):
    """주문 관련 API 클래스"""

    ORDER_ENDPOINT = "order"
    CREDIT_ORDER_ENDPOINT = "credit_order"
    CREDIT_INFO_ENDPOINT = "credit_info"

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
    TR_ENDPOINTS = {
        "stock_buy": ORDER_ENDPOINT,
        "stock_sell": ORDER_ENDPOINT,
        "stock_modify": ORDER_ENDPOINT,
        "stock_cancel": ORDER_ENDPOINT,
        "credit_buy": CREDIT_ORDER_ENDPOINT,
        "credit_sell": CREDIT_ORDER_ENDPOINT,
        "credit_modify": CREDIT_ORDER_ENDPOINT,
        "credit_cancel": CREDIT_ORDER_ENDPOINT,
        "credit_available_stocks": CREDIT_INFO_ENDPOINT,
        "credit_available_check": CREDIT_INFO_ENDPOINT,
    }
    PRICE_REQUIRED_ORDER_TYPES = {"00", "05", "10", "20", "62"}
    PRICELESS_ORDER_TYPES = {"03", "06", "07", "13", "16", "23", "26", "61", "81"}

    def _validate_account_no(self) -> str:
        """주문 요청용 계좌번호 검증"""
        account_no = getattr(self, "account_no", None)
        if not account_no or not str(account_no).strip():
            raise ValueError("account_no is required for order requests")
        return str(account_no).strip()

    @staticmethod
    def _validate_positive_int(value: int, field_name: str) -> None:
        """수량 필드 검증"""
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{field_name} must be a positive integer")

    @staticmethod
    def _validate_non_negative_int(value: int, field_name: str) -> None:
        """가격 필드 검증"""
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{field_name} must be a non-negative integer")

    @staticmethod
    def _validate_order_price(price: int, order_type: str) -> None:
        """호가유형별 주문가격 검증"""
        OrderAPI._validate_non_negative_int(price, "price")
        if order_type in OrderAPI.PRICE_REQUIRED_ORDER_TYPES and price <= 0:
            raise ValueError("price must be positive for limit order types")
        if order_type in OrderAPI.PRICELESS_ORDER_TYPES and price != 0:
            raise ValueError("price must be zero for market and price-less order types")

    @staticmethod
    def _convert_credit_market_code(market: str) -> str:
        """신용융자 가능종목 시장구분 변환"""
        market_codes = {
            "ALL": "0",
            "KOSPI": "1",
            "KOSDAQ": "2",
            "0": "0",
            "1": "1",
            "2": "2",
        }
        market_key = str(market).strip().upper()
        if market_key not in market_codes:
            raise ValueError("market must be one of: ALL, KOSPI, KOSDAQ, 0, 1, 2")
        return market_codes[market_key]

    @staticmethod
    def _validate_code(value: str, field_name: str) -> None:
        """주문 구분 등 코드 필드 검증"""
        allowed_codes = {
            "order_type": {
                "00",  # 지정가
                "03",  # 시장가
                "05",  # 조건부지정가
                "06",  # 최유리지정가
                "07",  # 최우선지정가
                "10",  # 지정가IOC
                "13",  # 시장가IOC
                "16",  # 최유리IOC
                "20",  # 지정가FOK
                "23",  # 시장가FOK
                "26",  # 최유리FOK
                "61",  # 장전시간외종가
                "62",  # 시간외단일가
                "81",  # 장후시간외종가
            },
            "price_type": {"00", "03", "05", "06", "07", "10", "13", "16", "20", "23", "26", "61", "62", "81"},
            "credit_type": {"02", "33"},
        }
        allowed = allowed_codes.get(field_name)
        if not isinstance(value, str) or allowed is None or value not in allowed:
            allowed_text = ", ".join(sorted(allowed)) if allowed else "documented allowed codes"
            raise ValueError(f"{field_name} must be one of {allowed_text}")

    @staticmethod
    def _validate_original_order_no(original_order_no: str) -> str:
        """원주문번호 검증"""
        if not isinstance(original_order_no, str) or not original_order_no.strip():
            raise ValueError("original_order_no is required")
        return original_order_no.strip()

    def _make_order_request(self, tr_code_key: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """현재 KiwoomAPIBase.make_tr_request 시그니처에 맞춘 주문 요청"""
        return self.make_tr_request(
            tr_code=self.TR_CODES[tr_code_key],
            endpoint=self.TR_ENDPOINTS[tr_code_key],
            data=params,
        )

    def buy_stock(
        self,
        stock_code: str,
        quantity: int,
        price: int = 0,
        order_type: str = "03",
        price_type: str = "00",
    ) -> Dict[str, Any]:
        """주식 매수주문 (kt10000)"""
        account_no = self._validate_account_no()
        self._validate_positive_int(quantity, "quantity")
        self._validate_code(order_type, "order_type")
        self._validate_code(price_type, "price_type")
        self._validate_order_price(price, order_type)
        params = {
            "acnt_no": account_no,
            "stk_cd": self.convert_stock_code_param(stock_code)["stk_cd"],
            "ord_qty": str(quantity),
            "ord_prc": str(price),
            "ord_tp": order_type,
            "prc_tp": price_type,
        }
        return self._make_order_request("stock_buy", params)

    def sell_stock(
        self,
        stock_code: str,
        quantity: int,
        price: int = 0,
        order_type: str = "03",
        price_type: str = "00",
    ) -> Dict[str, Any]:
        """주식 매도주문 (kt10001)"""
        account_no = self._validate_account_no()
        self._validate_positive_int(quantity, "quantity")
        self._validate_code(order_type, "order_type")
        self._validate_code(price_type, "price_type")
        self._validate_order_price(price, order_type)
        params = {
            "acnt_no": account_no,
            "stk_cd": self.convert_stock_code_param(stock_code)["stk_cd"],
            "ord_qty": str(quantity),
            "ord_prc": str(price),
            "ord_tp": order_type,
            "prc_tp": price_type,
        }
        return self._make_order_request("stock_sell", params)

    def modify_order(
        self,
        original_order_no: str,
        stock_code: str,
        quantity: int,
        price: int = 0,
        order_type: str = "03",
    ) -> Dict[str, Any]:
        """주식 정정주문 (kt10002)"""
        account_no = self._validate_account_no()
        original_order_no = self._validate_original_order_no(original_order_no)
        self._validate_positive_int(quantity, "quantity")
        self._validate_code(order_type, "order_type")
        self._validate_order_price(price, order_type)
        params = {
            "acnt_no": account_no,
            "orgn_ord_no": original_order_no,
            "stk_cd": self.convert_stock_code_param(stock_code)["stk_cd"],
            "mdf_qty": str(quantity),
            "mdf_prc": str(price),
            "ord_tp": order_type,
        }
        return self._make_order_request("stock_modify", params)

    def cancel_order(
        self, original_order_no: str, stock_code: str, quantity: int
    ) -> Dict[str, Any]:
        """주식 취소주문 (kt10003)"""
        account_no = self._validate_account_no()
        original_order_no = self._validate_original_order_no(original_order_no)
        self._validate_positive_int(quantity, "quantity")
        params = {
            "acnt_no": account_no,
            "orgn_ord_no": original_order_no,
            "stk_cd": self.convert_stock_code_param(stock_code)["stk_cd"],
            "cncl_qty": str(quantity),
        }
        return self._make_order_request("stock_cancel", params)

    def buy_credit(
        self,
        stock_code: str,
        quantity: int,
        price: int = 0,
        credit_type: str = "02",
        order_type: str = "03",
        price_type: str = "00",
    ) -> Dict[str, Any]:
        """신용 매수주문 (kt10006)"""
        account_no = self._validate_account_no()
        self._validate_positive_int(quantity, "quantity")
        self._validate_code(credit_type, "credit_type")
        self._validate_code(order_type, "order_type")
        self._validate_code(price_type, "price_type")
        self._validate_order_price(price, order_type)
        params = {
            "acnt_no": account_no,
            "stk_cd": self.convert_stock_code_param(stock_code)["stk_cd"],
            "ord_qty": str(quantity),
            "ord_prc": str(price),
            "crdt_tp": credit_type,
            "ord_tp": order_type,
            "prc_tp": price_type,
        }
        return self._make_order_request("credit_buy", params)

    def sell_credit(
        self,
        stock_code: str,
        quantity: int,
        price: int = 0,
        credit_type: str = "02",
        order_type: str = "03",
        price_type: str = "00",
    ) -> Dict[str, Any]:
        """신용 매도주문 (kt10007)"""
        account_no = self._validate_account_no()
        self._validate_positive_int(quantity, "quantity")
        self._validate_code(credit_type, "credit_type")
        self._validate_code(order_type, "order_type")
        self._validate_code(price_type, "price_type")
        self._validate_order_price(price, order_type)
        params = {
            "acnt_no": account_no,
            "stk_cd": self.convert_stock_code_param(stock_code)["stk_cd"],
            "ord_qty": str(quantity),
            "ord_prc": str(price),
            "crdt_tp": credit_type,
            "ord_tp": order_type,
            "prc_tp": price_type,
        }
        return self._make_order_request("credit_sell", params)

    def modify_credit_order(
        self,
        original_order_no: str,
        stock_code: str,
        quantity: int,
        price: int = 0,
        order_type: str = "03",
    ) -> Dict[str, Any]:
        """신용 정정주문 (kt10008)"""
        account_no = self._validate_account_no()
        original_order_no = self._validate_original_order_no(original_order_no)
        self._validate_positive_int(quantity, "quantity")
        self._validate_code(order_type, "order_type")
        self._validate_order_price(price, order_type)
        params = {
            "acnt_no": account_no,
            "orgn_ord_no": original_order_no,
            "stk_cd": self.convert_stock_code_param(stock_code)["stk_cd"],
            "mdf_qty": str(quantity),
            "mdf_prc": str(price),
            "ord_tp": order_type,
        }
        return self._make_order_request("credit_modify", params)

    def cancel_credit_order(
        self, original_order_no: str, stock_code: str, quantity: int
    ) -> Dict[str, Any]:
        """신용 취소주문 (kt10009)"""
        account_no = self._validate_account_no()
        original_order_no = self._validate_original_order_no(original_order_no)
        self._validate_positive_int(quantity, "quantity")
        params = {
            "acnt_no": account_no,
            "orgn_ord_no": original_order_no,
            "stk_cd": self.convert_stock_code_param(stock_code)["stk_cd"],
            "cncl_qty": str(quantity),
        }
        return self._make_order_request("credit_cancel", params)

    def get_credit_available_stocks(self, market: str = "ALL") -> Dict[str, Any]:
        """신용융자 가능종목요청 (kt20016)"""
        params = {"mrkt_tp": self._convert_credit_market_code(market)}
        return self._make_order_request("credit_available_stocks", params)

    def check_credit_available(self, stock_code: str) -> Dict[str, Any]:
        """신용융자 가능문의 (kt20017)"""
        params = {"stk_cd": self.convert_stock_code_param(stock_code)["stk_cd"]}
        return self._make_order_request("credit_available_check", params)
