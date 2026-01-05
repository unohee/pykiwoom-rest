# Changelog

All notable changes to PyKiwoom-REST will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.1] - 2025-12-21

### 🔧 Sector Chart API 수정 및 개선

#### Fixed
- **업종 차트 API 파라미터 수정**: 모든 업종 차트 메서드에서 잘못된 파라미터명 수정
  - `sect_cd` → `inds_cd` (3자리 업종코드)
  - 엔드포인트 `sector` → `chart` 변경
  - 날짜 파라미터 `start_date/end_date` → `base_dt` 통일

#### Changed
- **get_sector_tick_chart()**: `count` 파라미터를 `tick_scope`로 변경 (1, 3, 5, 10, 30)
- **get_sector_daily_chart()**: `base_date` 파라미터로 단순화
- **get_sector_weekly_chart()**: `base_date` 파라미터로 단순화
- **get_sector_monthly_chart()**: `base_date` 파라미터로 단순화
- **get_sector_yearly_chart()**: `base_date` 파라미터로 단순화

#### Added
- **4자리→3자리 코드 자동 변환**: 모든 업종 차트 메서드에서 "0001" → "001" 자동 변환 지원
- **기본값 설정**: `base_date` 미입력 시 오늘 날짜 자동 적용

#### API Coverage Update
- **Sector API**: 12 methods (차트 6개 + 현재가/지수 조회 6개)
  - ka20004: 업종틱차트조회 ✅
  - ka20005: 업종분봉조회 ✅
  - ka20006: 업종일봉조회 ✅
  - ka20007: 업종주봉조회 ✅
  - ka20008: 업종월봉조회 ✅
  - ka20019: 업종년봉조회 ✅

#### Testing
- 14개 단위 테스트 통과
- 실제 API 테스트 완료 (KOSPI 지수 데이터 조회 성공)

---

## [2.1.0] - 2025-10-21

### 🚀 API Expansion & Modernization

#### New Features
- **OAuth2 Authentication API** (au10001, au10002)
  - Token issuance and revocation
  - Automatic token refresh
  - Token status monitoring
  - Complete access control management

- **Stock API Extensions** (5 new methods)
  - ka10005: Investor trading trends (투자자별 매매동향)
  - ka10006: Member trading trends (기관별 매매동향)
  - ka10007: Elapsed time analysis (소요시간)
  - ka10009: Program trading trends (프로그램매매동향)
  - ka10010: Trade volume power (거래량파동력)

- **Expanded Account API** (7 new wrapper methods)
  - Estimated asset tracking
  - Daily asset estimation
  - Trading history retrieval
  - Realized profit/loss details

#### Architecture Improvements
- Unified Facade Pattern: Single `KiwoomRest` entry point
- Mixin-based extensions for cleaner code organization
- Dependency synchronization across API modules
- Enhanced rate limiting with token rotation

#### API Coverage
- **Total Methods**: 50+ public methods
- **Auth API**: 5 methods (OAuth2 management)
- **Stock API**: 35+ methods (market data)
- **Chart API**: 7 methods (time series data)
- **Account API**: 18 methods (portfolio management)
- **Order API**: 4 methods (execution)
- **Ranking API**: 12+ methods (market trends)
- **Sector API**: 3 methods (industry data)

#### Testing & Quality
- Comprehensive OAuth2 authentication tests
- Integration test suite for new methods
- Type safety verification
- Rate limiting compliance validation

#### Documentation
- OAuth2 integration guide
- API expansion roadmap
- Method usage examples
- Architecture documentation

### 🔄 Module Organization
```
New Import Pattern:
from pykiwoom_rest import KiwoomRest

kiwoom = KiwoomRest(enable_rate_optimizer=True)

# OAuth2 Token Management
token_info = kiwoom.get_access_token()
status = kiwoom.get_token_status()

# Extended Stock Analysis
investor_trend = kiwoom.get_stock_investor_trading("005930")
member_trend = kiwoom.get_stock_member_trading("005930")

# Enhanced Account Info
asset = kiwoom.get_estimated_asset()
history = kiwoom.get_trading_history()
```

---

## [2.0.0] - 2025-01-05

### 🎯 Major Features Added
- **Complete Architecture Overhaul**: New modular design with specialized API classes
- **Advanced Rate Limiting**: Multi-credential rotation and intelligent backoff algorithms
- **Async/Concurrent Processing**: High-performance parallel and asynchronous request handling
- **Enhanced Error Handling**: Comprehensive error recovery with exponential backoff
- **Type Safety**: Full type hints and validation throughout the codebase

### ⚡ Performance Improvements
- **Rate Limiting Optimizer**: Automatic credential rotation to avoid 429 errors
- **Async API Client**: ~70 req/s throughput with AsyncIO
- **Parallel Processing**: ThreadPool-based concurrent requests (~25 req/s)
- **Smart Retry Strategy**: Intelligent retry with exponential backoff

### 📚 API Enhancements
- **Modular API Structure**: Separate classes for Stock, Chart, Account, Order, Ranking, Sector
- **APIResponse Model**: Standardized response handling with dict compatibility
- **Pagination Support**: Automatic handling of large datasets
- **Health Monitoring**: Real-time API status and performance tracking

### 🧪 Testing & Quality
- **127 Test Cases**: Comprehensive test coverage for all components
- **Performance Benchmarks**: Automated performance testing and optimization
- **Code Quality**: BS Index 2.1/10 (Excellent grade)
- **Zero Technical Debt**: No TODO/FIXME items remaining

### 📖 Documentation
- **Complete API Documentation**: Comprehensive usage guide with examples
- **Performance Examples**: Real-world usage scenarios and benchmarks  
- **Developer Guide**: Setup, configuration, and contribution guidelines
- **Postman Integration**: API testing collection and environment

### 🔧 Technical Changes
- **Python 3.10+ Required**: Full type hints support
- **Dependency Updates**: Latest versions of all dependencies
- **Environment Variables**: Enhanced configuration management
- **Logging System**: Structured logging with performance metrics

### 🛡️ Security & Reliability
- **Credential Security**: Environment-only API key storage
- **Token Management**: Automatic token refresh and expiration handling
- **Error Recovery**: Graceful handling of all API failure scenarios
- **Rate Limit Compliance**: Automatic adherence to API limitations

### 📁 Project Structure Changes
```
src/pykiwoom_rest/
├── async_api.py              # NEW: Async processing
├── concurrent_api.py         # NEW: Parallel processing  
├── rate_limit_optimizer.py   # NEW: Advanced rate limiting
├── response_model.py         # NEW: Standardized responses
├── base_api.py              # Enhanced error handling
├── kiwoom_base.py           # Core functionality
└── [api_modules].py         # Modularized APIs
```

## [1.0.0] - 2024-08-20

### Initial Release
- Basic REST API wrapper for Kiwoom Securities
- Essential stock data retrieval functions
- Simple authentication and token management
- Basic error handling and retry logic

### Features
- Stock price and orderbook data
- Chart data (minute, daily, weekly, monthly)
- Account balance and position information
- Basic order execution capabilities

---

## Upcoming Releases

### [2.1.0] - Planned
- **WebSocket Integration**: Real-time streaming data
- **Technical Indicators**: Built-in TA-Lib integration
- **GUI Dashboard**: Real-time monitoring interface
- **Docker Support**: Containerized deployment

### [2.2.0] - Future
- **Backtesting Engine**: Historical strategy testing
- **ML Integration**: Machine learning signal generation
- **Cloud Templates**: AWS/GCP deployment guides
- **REST Server Mode**: API server for multi-client access

---

*For detailed API changes, see [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)*