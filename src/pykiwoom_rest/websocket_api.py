# Task: TM-20251029-001 | 생성: 2025-10-29 | PRD: FR-002, FR-003, FR-004
# 목적: 실시간 시세/호가/체결 WebSocket API | 의존성: websocket_client
# CI상태: [pending]

"""
WebSocket API 모듈

실시간 시세, 호가, 체결 데이터를 제공하는 고수준 API입니다.
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .websocket_client import WebSocketClient


logger = logging.getLogger(__name__)


@dataclass
class RealtimeQuote:
    """실시간 시세 데이터"""

    stock_code: str
    current_price: int
    change_price: int
    change_rate: float
    volume: int
    timestamp: datetime
    open_price: int = 0
    high_price: int = 0
    low_price: int = 0
    market_cap: int = 0


@dataclass
class RealtimeOrderbook:
    """실시간 호가 데이터"""

    stock_code: str
    timestamp: datetime
    ask_prices: List[int] = field(default_factory=list)  # 매도 호가 (10단계)
    ask_volumes: List[int] = field(default_factory=list)  # 매도 잔량
    bid_prices: List[int] = field(default_factory=list)  # 매수 호가 (10단계)
    bid_volumes: List[int] = field(default_factory=list)  # 매수 잔량
    total_ask_volume: int = 0  # 총 매도 잔량
    total_bid_volume: int = 0  # 총 매수 잔량


@dataclass
class RealtimeTrade:
    """실시간 체결 데이터"""

    stock_code: str
    trade_price: int
    trade_volume: int
    trade_time: str
    timestamp: datetime
    change_price: int = 0
    change_rate: float = 0.0
    cumulative_volume: int = 0


class WebSocketAPI:
    """
    실시간 시세 WebSocket API

    Kiwoom증권 WebSocket API를 래핑하여 실시간 데이터를 제공합니다.

    Examples:
        >>> from pykiwoom_rest import WebSocketAPI
        >>> ws_api = WebSocketAPI(access_token="...", appkey="...", appsecret="...")
        >>> await ws_api.connect()
        >>> await ws_api.subscribe_quote("005930", callback=lambda data: print(data))
    """

    # TR 코드 정의
    TR_ORDER_EXECUTION = "00"  # 주문체결
    TR_BALANCE = "04"  # 잔고
    TR_STOCK_QUOTE = "0A"  # 주식기세 (현재가)
    TR_STOCK_TRADE = "0B"  # 주식체결
    TR_STOCK_PRIORITY_QUOTE = "0C"  # 주식우선호가
    TR_STOCK_ORDERBOOK = "0D"  # 주식호가잔량
    TR_STOCK_AFTER_HOURS = "0E"  # 주식시간외호가
    TR_STOCK_BROKER = "0F"  # 주식당일거래원
    TR_ETF_NAV = "0G"  # ETF NAV
    TR_STOCK_EXPECTED_TRADE = "0H"  # 주식예상체결
    TR_SECTOR_INDEX = "0J"  # 업종지수
    TR_SECTOR_CHANGE = "0U"  # 업종등락

    def __init__(
        self,
        access_token: str,
        appkey: str,
        appsecret: str,
        base_url: str = "wss://openapi.koreainvestment.com:9443",
        auto_reconnect: bool = True,
    ):
        """
        WebSocket API 초기화

        Args:
            access_token: OAuth2 액세스 토큰
            appkey: 앱키
            appsecret: 앱시크릿
            base_url: WebSocket 베이스 URL
            auto_reconnect: 자동 재연결 활성화
        """
        self._client = WebSocketClient(
            base_url=base_url,
            access_token=access_token,
            appkey=appkey,
            appsecret=appsecret,
            auto_reconnect=auto_reconnect,
        )

        self._quote_callbacks: Dict[str, Callable] = {}
        self._orderbook_callbacks: Dict[str, Callable] = {}
        self._trade_callbacks: Dict[str, Callable] = {}

    @property
    def is_connected(self) -> bool:
        """WebSocket 연결 상태"""
        return self._client.is_connected

    async def connect(self) -> bool:
        """
        WebSocket 서버에 연결

        Returns:
            연결 성공 여부
        """
        return await self._client.connect()

    async def disconnect(self):
        """WebSocket 연결 종료"""
        await self._client.disconnect()

    async def subscribe_quote(
        self, stock_code: str, callback: Optional[Callable] = None
    ) -> bool:
        """
        실시간 시세 구독

        Args:
            stock_code: 종목코드 (예: "005930" - 삼성전자)
            callback: 데이터 수신 콜백 (선택)

        Returns:
            구독 성공 여부

        Examples:
            >>> async def on_quote(quote: RealtimeQuote):
            ...     print(f"현재가: {quote.current_price}")
            >>> await ws_api.subscribe_quote("005930", on_quote)
        """
        if callback:
            self._quote_callbacks[stock_code] = callback

        async def internal_callback(data: Dict[str, Any]):
            quote = self._parse_quote(stock_code, data)
            if stock_code in self._quote_callbacks:
                cb = self._quote_callbacks[stock_code]
                if asyncio.iscoroutinefunction(cb):
                    await cb(quote)
                else:
                    cb(quote)

        self._client.register_callback(self.TR_STOCK_QUOTE, internal_callback)
        return await self._client.subscribe(self.TR_STOCK_QUOTE, stock_code)

    async def subscribe_orderbook(
        self, stock_code: str, callback: Optional[Callable] = None
    ) -> bool:
        """
        실시간 호가 구독

        Args:
            stock_code: 종목코드
            callback: 데이터 수신 콜백 (선택)

        Returns:
            구독 성공 여부

        Examples:
            >>> async def on_orderbook(orderbook: RealtimeOrderbook):
            ...     print(f"매수 1호가: {orderbook.bid_prices[0]}")
            >>> await ws_api.subscribe_orderbook("005930", on_orderbook)
        """
        if callback:
            self._orderbook_callbacks[stock_code] = callback

        async def internal_callback(data: Dict[str, Any]):
            orderbook = self._parse_orderbook(stock_code, data)
            if stock_code in self._orderbook_callbacks:
                cb = self._orderbook_callbacks[stock_code]
                if asyncio.iscoroutinefunction(cb):
                    await cb(orderbook)
                else:
                    cb(orderbook)

        self._client.register_callback(self.TR_STOCK_ORDERBOOK, internal_callback)
        return await self._client.subscribe(self.TR_STOCK_ORDERBOOK, stock_code)

    async def subscribe_trade(
        self, stock_code: str, callback: Optional[Callable] = None
    ) -> bool:
        """
        실시간 체결 구독

        Args:
            stock_code: 종목코드
            callback: 데이터 수신 콜백 (선택)

        Returns:
            구독 성공 여부

        Examples:
            >>> async def on_trade(trade: RealtimeTrade):
            ...     print(f"체결가: {trade.trade_price}, 체결량: {trade.trade_volume}")
            >>> await ws_api.subscribe_trade("005930", on_trade)
        """
        if callback:
            self._trade_callbacks[stock_code] = callback

        async def internal_callback(data: Dict[str, Any]):
            trade = self._parse_trade(stock_code, data)
            if stock_code in self._trade_callbacks:
                cb = self._trade_callbacks[stock_code]
                if asyncio.iscoroutinefunction(cb):
                    await cb(trade)
                else:
                    cb(trade)

        self._client.register_callback(self.TR_STOCK_TRADE, internal_callback)
        return await self._client.subscribe(self.TR_STOCK_TRADE, stock_code)

    async def unsubscribe_quote(self, stock_code: str) -> bool:
        """실시간 시세 구독 해제"""
        if stock_code in self._quote_callbacks:
            del self._quote_callbacks[stock_code]
        return await self._client.unsubscribe(self.TR_STOCK_QUOTE, stock_code)

    async def unsubscribe_orderbook(self, stock_code: str) -> bool:
        """실시간 호가 구독 해제"""
        if stock_code in self._orderbook_callbacks:
            del self._orderbook_callbacks[stock_code]
        return await self._client.unsubscribe(self.TR_STOCK_ORDERBOOK, stock_code)

    async def unsubscribe_trade(self, stock_code: str) -> bool:
        """실시간 체결 구독 해제"""
        if stock_code in self._trade_callbacks:
            del self._trade_callbacks[stock_code]
        return await self._client.unsubscribe(self.TR_STOCK_TRADE, stock_code)

    async def unsubscribe_all(self):
        """모든 구독 해제"""
        for stock_code in list(self._quote_callbacks.keys()):
            await self.unsubscribe_quote(stock_code)
        for stock_code in list(self._orderbook_callbacks.keys()):
            await self.unsubscribe_orderbook(stock_code)
        for stock_code in list(self._trade_callbacks.keys()):
            await self.unsubscribe_trade(stock_code)

    def _parse_quote(self, stock_code: str, data: Dict[str, Any]) -> RealtimeQuote:
        """실시간 시세 데이터 파싱"""
        output = data.get("body", {}).get("output", {})
        return RealtimeQuote(
            stock_code=stock_code,
            current_price=int(output.get("stck_prpr", 0)),
            change_price=int(output.get("prdy_vrss", 0)),
            change_rate=float(output.get("prdy_ctrt", 0.0)),
            volume=int(output.get("acml_vol", 0)),
            open_price=int(output.get("stck_oprc", 0)),
            high_price=int(output.get("stck_hgpr", 0)),
            low_price=int(output.get("stck_lwpr", 0)),
            timestamp=datetime.now(),
        )

    def _parse_orderbook(
        self, stock_code: str, data: Dict[str, Any]
    ) -> RealtimeOrderbook:
        """실시간 호가 데이터 파싱"""
        output = data.get("body", {}).get("output", {})

        ask_prices = [int(output.get(f"askp{i}", 0)) for i in range(1, 11)]
        ask_volumes = [int(output.get(f"askp_rsqn{i}", 0)) for i in range(1, 11)]
        bid_prices = [int(output.get(f"bidp{i}", 0)) for i in range(1, 11)]
        bid_volumes = [int(output.get(f"bidp_rsqn{i}", 0)) for i in range(1, 11)]

        return RealtimeOrderbook(
            stock_code=stock_code,
            timestamp=datetime.now(),
            ask_prices=ask_prices,
            ask_volumes=ask_volumes,
            bid_prices=bid_prices,
            bid_volumes=bid_volumes,
            total_ask_volume=sum(ask_volumes),
            total_bid_volume=sum(bid_volumes),
        )

    def _parse_trade(self, stock_code: str, data: Dict[str, Any]) -> RealtimeTrade:
        """실시간 체결 데이터 파싱"""
        output = data.get("body", {}).get("output", {})
        return RealtimeTrade(
            stock_code=stock_code,
            trade_price=int(output.get("stck_cntg_hour", 0)),
            trade_volume=int(output.get("cntg_vol", 0)),
            trade_time=output.get("stck_cntg_hour", ""),
            change_price=int(output.get("prdy_vrss", 0)),
            change_rate=float(output.get("prdy_ctrt", 0.0)),
            cumulative_volume=int(output.get("acml_vol", 0)),
            timestamp=datetime.now(),
        )


# 헬퍼 함수: 동기 컨텍스트에서 WebSocket 사용
class WebSocketContextManager:
    """
    WebSocket API를 동기 컨텍스트에서 사용하기 위한 헬퍼

    Examples:
        >>> with WebSocketContextManager(ws_api) as ws:
        ...     ws.run(ws_api.subscribe_quote("005930"))
        ...     # ... 다른 작업
    """

    def __init__(self, ws_api: WebSocketAPI):
        self.ws_api = ws_api
        self.loop: Optional[asyncio.AbstractEventLoop] = None

    def __enter__(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.ws_api.connect())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.loop.run_until_complete(self.ws_api.disconnect())
        self.loop.close()

    def run(self, coro):
        """코루틴 실행"""
        return self.loop.run_until_complete(coro)
