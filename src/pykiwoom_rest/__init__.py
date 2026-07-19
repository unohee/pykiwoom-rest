"""키움증권 REST API를 Python, CLI, MCP로 제공하는 비공식 라이브러리.

사용 예시:
    >>> from pykiwoom_rest import KiwoomRest
    >>> kiwoom = KiwoomRest(enable_rate_optimizer=True)
    >>> result = kiwoom.get_stock_price("005930")
"""

__version__ = "2.2.0"
__author__ = "PyKiwoom-REST contributors"
__email__ = "contact@pykiwoom-rest.org"

# Main API classes (Enhanced with new architecture)
from .account_api import AccountAPI
from .auth_api import AuthAPI
from .base_api import (
    APIError,
    BaseAPIClient,
    RateLimitExceededError,
    TokenBucketRateLimiter,
)
from .chart_api import ChartAPI
from .investor_api import InvestorAPI

# New modular API classes (for direct access)
from .kiwoom_base import KiwoomAPIBase, KiwoomAPIError
from .kiwoom_rest import KiwoomRest
from .kiwoom_rest_base import KiwoomRestBase
from .program_api import ProgramAPI
from .ranking_api import RankingAPI
from .response_model import APIResponse
from .stock_api import StockAPI

# WebSocket API (실시간 시세)
from .websocket_api import RealtimeOrderbook, RealtimeQuote, RealtimeTrade, WebSocketAPI
from .websocket_client import WebSocketClient

__all__ = [
    # Main API classes (Enhanced)
    "KiwoomRest",
    "KiwoomRestBase",
    # Modular classes (for direct access)
    "KiwoomAPIBase",
    "AuthAPI",
    "AccountAPI",
    "StockAPI",
    "InvestorAPI",
    "ProgramAPI",
    "ChartAPI",
    "RankingAPI",
    # WebSocket API (실시간 시세)
    "WebSocketAPI",
    "WebSocketClient",
    "RealtimeQuote",
    "RealtimeOrderbook",
    "RealtimeTrade",
    # Base classes
    "BaseAPIClient",
    "TokenBucketRateLimiter",
    "APIResponse",
    # Exceptions
    "KiwoomAPIError",
    "APIError",
    "RateLimitExceededError",
]
