# PyKiwoom-REST

High-performance Python wrapper for Kiwoom Securities REST API

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://img.shields.io/pypi/v/pykiwoom-rest.svg)](https://pypi.org/project/pykiwoom-rest/)

A complete Python solution for Kiwoom Securities OpenAPI REST service.
Supports rate limiting optimization, asynchronous processing, parallel execution, and automatic error recovery.

## Key Features

### Comprehensive API Support
- All major endpoints (stock quotes, charts, accounts, orders, rankings, sectors)
- Real-time market data
- Automatic pagination for large datasets
- Full type hints and validation

### High-Performance Processing
- Asynchronous I/O (AsyncIO) for concurrent requests
- Thread-pool based parallel processing
- Automatic optimization based on request patterns
- Real-time performance monitoring

### Reliability & Stability
- Multi-credential rotation to bypass rate limits
- Intelligent retry with exponential backoff
- Complete error handling for all edge cases
- Real-time API status and performance tracking

## Quick Start

### Installation

```bash
pip install pykiwoom-rest
```

### Configuration

You can configure credentials in **two ways**: environment variables or direct injection.

#### Option 1: Environment Variables (Recommended for Local Development)

Create a `.env` file in your project directory:

```bash
KIWOOM_APPKEY=your-app-key
KIWOOM_APPSECRET=your-app-secret
ACCOUNT_NO=your-account-number
```

```python
from pykiwoom_rest import KiwoomRest

# Automatically loads from .env or system environment
kiwoom = KiwoomRest()
```

#### Option 2: Direct Injection (Recommended for Production/Libraries)

Pass credentials directly when initializing:

```python
from pykiwoom_rest import KiwoomRest

# Direct credential injection
kiwoom = KiwoomRest(
    account_no="your-account-number",
    appkey="your-app-key",
    appsecret="your-app-secret"
)
```

#### Mixed Approach

You can also mix both methods:

```python
# Use environment for account, but override API keys
kiwoom = KiwoomRest(
    appkey="your-app-key",
    appsecret="your-app-secret"
    # account_no will be loaded from environment
)
```

### Basic Usage

```python
from pykiwoom_rest import KiwoomRest

# Initialize with direct credentials
kiwoom = KiwoomRest(
    account_no="your-account-number",
    appkey="your-app-key",
    appsecret="your-app-secret"
)

# Get stock price
stock_info = kiwoom.get_stock_price("005930")  # Samsung Electronics
print(stock_info['output']['stck_prpr'])  # Current price

# Get minute chart
chart_data = kiwoom.get_minute_chart(
    stock_code="005930",
    interval=5,
    count=100
)

# Get account balance
balance = kiwoom.get_account_balance()
print(balance)
```

## Supported Operations

### Authentication
- OAuth2 token issuance and management
- Automatic token refresh
- Token status monitoring

### Stock Data
- Current price and basic information
- Investor/institution trading trends
- Program trading trends
- Trade volume analysis

### Charts
- Minute-level OHLCV data
- Daily, weekly, monthly charts
- Automatic pagination for large datasets

### Account Management
- Portfolio balance inquiry
- Estimated asset value
- Cash position details
- Realized profit/loss
- Trading history

### Rankings
- Volume leaders
- Price gainers/losers
- Trading activity trends

## API Methods (61 Total)

The library provides 61 public methods across 7 API modules:

- AuthAPI (5 methods)
- StockAPI (14+ methods)
- ChartAPI (7 methods)
- AccountAPI (18 methods)
- RankingAPI (12+ methods)
- OrderAPI (4 methods)
- SectorAPI (3 methods)

See [CHANGELOG.md](CHANGELOG.md) for detailed API documentation.

## Advanced Features

### Asynchronous Processing

```python
import asyncio
from pykiwoom_rest import KiwoomRest

async def fetch_multiple():
    kiwoom = KiwoomRest(...)
    
    # Fetch multiple stocks concurrently
    tasks = [
        kiwoom.get_stock_price(code)
        for code in ["005930", "000660", "035420"]
    ]
    
    results = await asyncio.gather(*tasks)
    return results

# Execute
results = asyncio.run(fetch_multiple())
```

### Parallel Processing

```python
from pykiwoom_rest import KiwoomRest

kiwoom = KiwoomRest(...)

# Get daily charts for multiple stocks in parallel
charts = kiwoom.get_daily_chart_parallel(
    stock_codes=["005930", "000660", "035420"],
    max_workers=3
)
```

### Error Recovery

The library automatically handles common errors:
- Rate limit (429) - automatic retry with exponential backoff
- Connection errors - automatic reconnection
- Invalid data - validation and fallback

## Configuration Options

```python
kiwoom = KiwoomRest(
    account_no="your-account",
    appkey="your-key",
    appsecret="your-secret",
    use_mock=False,              # Use mock API for testing
    rate_limit=20,               # Requests per second
    max_retries=3,               # Max retry attempts
    enable_rate_optimizer=True,  # Auto rate limit optimization
)
```

## Requirements

- Python 3.8 or higher
- Internet connection for API calls
- Valid Kiwoom Securities OpenAPI credentials

## Dependencies

- requests >= 2.31.0
- python-dotenv >= 1.0.0
- pandas >= 2.0.0
- openpyxl >= 3.1.0
- numpy >= 1.24.0

## Limitations

- API rate limit: 20 requests per second
- Token validity: 24 hours (automatic refresh)
- Some real-time data only available during market hours (9:00-15:30 KST)

## License

MIT License - see [LICENSE](LICENSE) for details

## Support

- GitHub Issues: https://github.com/unohee/pykiwoom-rest/issues
- Documentation: https://github.com/unohee/pykiwoom-rest
- Requirements: Kiwoom Securities OpenAPI account

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This library is not affiliated with Kiwoom Securities.
Use at your own risk for trading and financial decisions.

---

**Version:** 2.1.0
**Status:** Production Ready
**Last Updated:** October 21, 2025
