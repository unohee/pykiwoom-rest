"""
PyKiwoom-REST: Python wrapper for Kiwoom Securities REST API
Enhanced version with modular architecture, rate limiting, and error handling
"""

__version__ = "2.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Main API classes (Enhanced with new architecture)
from .kiwoom_rest import KiwoomRest
from .kiwoom_rest_base import KiwoomRestBase

# New modular API classes (for direct access)
from .kiwoom_base import KiwoomAPIBase, KiwoomAPIError
from .stock_api import StockAPI
from .chart_api import ChartAPI
from .ranking_api import RankingAPI
from .base_api import BaseAPIClient, RateLimitExceeded, APIError, TokenBucketRateLimiter

__all__ = [
    # Main API classes (Enhanced)
    "KiwoomRest",
    "KiwoomRestBase",
    
    # Modular classes (for direct access)
    "KiwoomAPIBase",
    "StockAPI",
    "ChartAPI", 
    "RankingAPI",
    
    # Base classes
    "BaseAPIClient",
    "TokenBucketRateLimiter",
    
    # Exceptions
    "KiwoomAPIError",
    "APIError",
    "RateLimitExceeded"
]