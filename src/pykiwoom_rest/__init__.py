"""
PyKiwoom-REST v2.0: 고성능 키움증권 REST API Python 라이브러리

🚀 Key Features:
- ✅ 완전한 API 지원 (시세, 차트, 계좌, 주문, 순위, 업종)
- ⚡ 고성능 처리 (비동기/병렬, ~70 req/s)
- 🛡️ 안정성 보장 (Rate limiting 회피, 지능형 재시도)
- 🎯 타입 안전성 (완전한 타입 힌팅)

📊 Performance:
- 순차 처리: ~48 req/s
- 병렬 처리: ~25 req/s (ThreadPool)
- 비동기 처리: ~70 req/s (AsyncIO)
- Rate limiting 최적화: 429 에러 0%

🏗️ Architecture:
- Modular design with specialized API classes
- Advanced rate limiting with multi-credential rotation
- Comprehensive error handling and automatic recovery
- Real-time performance monitoring and optimization

Example Usage:
    >>> from pykiwoom_rest import KiwoomRest
    >>> kiwoom = KiwoomRest(enable_rate_optimizer=True)
    >>> result = kiwoom.get_stock_price("005930")
    >>> print(f"현재가: {result.data['cur_prc']:,}원")
"""

__version__ = "2.0.0"
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
