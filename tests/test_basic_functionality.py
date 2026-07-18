"""
PyKiwoom-Rest Basic Functionality Test
기본 기능 테스트 (Mock 없이)
작성일: 2025-01-27
"""

import unittest
import sys
import os

# 프로젝트 루트를 Python path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from pykiwoom_rest.base_api import TokenBucketRateLimiter, RateLimitExceededError
    from pykiwoom_rest import (
        KiwoomAPIBase,
        StockAPI,
        ChartAPI,
        RankingAPI,
        KiwoomAPIError
    )
    IMPORTS_OK = True
except ImportError as e:
    print(f"Import Error: {e}")
    IMPORTS_OK = False


class TestBasicImports(unittest.TestCase):
    """기본 임포트 테스트"""
    
    def test_imports_successful(self):
        """모든 모듈이 정상적으로 임포트되는지 확인"""
        self.assertTrue(IMPORTS_OK, "모든 모듈이 정상적으로 임포트되어야 합니다")
    
    @unittest.skipUnless(IMPORTS_OK, "Import failed")
    def test_class_inheritance(self):
        """클래스 상속 구조 확인"""
        # StockAPI는 KiwoomAPIBase를 상속
        self.assertTrue(issubclass(StockAPI, KiwoomAPIBase))
        self.assertTrue(issubclass(ChartAPI, KiwoomAPIBase))
        self.assertTrue(issubclass(RankingAPI, KiwoomAPIBase))
    
    @unittest.skipUnless(IMPORTS_OK, "Import failed")
    def test_tr_codes_existence(self):
        """TR 코드 매핑이 존재하는지 확인"""
        # StockAPI TR 코드
        self.assertIn('stock_basic_info', StockAPI.TR_CODES)
        self.assertEqual(StockAPI.TR_CODES['stock_basic_info'], 'ka10001')
        
        # ChartAPI TR 코드
        self.assertIn('minute_chart', ChartAPI.TR_CODES)
        self.assertEqual(ChartAPI.TR_CODES['minute_chart'], 'ka10080')
        
        # RankingAPI TR 코드
        self.assertIn('quote_volume_top', RankingAPI.TR_CODES)
        self.assertEqual(RankingAPI.TR_CODES['quote_volume_top'], 'ka10020')


class TestRateLimiterStandalone(unittest.TestCase):
    """Rate Limiter 독립 테스트"""
    
    def test_rate_limiter_creation(self):
        """Rate Limiter 생성 테스트"""
        limiter = TokenBucketRateLimiter(rate=10, per_seconds=1.0)
        
        self.assertEqual(limiter.rate, 10)
        self.assertEqual(limiter.per_seconds, 1.0)
        self.assertEqual(limiter.max_tokens, 10)
        self.assertEqual(limiter.tokens, 10)
    
    def test_token_acquisition_basic(self):
        """기본 토큰 획득 테스트"""
        limiter = TokenBucketRateLimiter(rate=5, per_seconds=1.0)
        
        # 5번까지는 즉시 성공
        for i in range(5):
            success = limiter.acquire(blocking=False)
            self.assertTrue(success, f"Token acquisition {i+1} should succeed")
        
        # 6번째는 실패
        success = limiter.acquire(blocking=False)
        self.assertFalse(success, "6th token acquisition should fail")
    
    def test_rate_limiter_reset(self):
        """Rate Limiter 리셋 테스트"""
        limiter = TokenBucketRateLimiter(rate=3, per_seconds=1.0)
        
        # 모든 토큰 소진
        limiter.acquire(tokens=3, blocking=False)
        self.assertFalse(limiter.acquire(blocking=False))
        
        # 리셋 후 다시 사용 가능
        limiter.reset()
        self.assertTrue(limiter.acquire(blocking=False))
    
    def test_invalid_token_request(self):
        """잘못된 토큰 요청 테스트"""
        limiter = TokenBucketRateLimiter(rate=5, per_seconds=1.0)
        
        # 최대값보다 많은 토큰 요청 시 ValueError 발생
        with self.assertRaises(ValueError):
            limiter.acquire(tokens=10)


class TestExceptionHierarchy(unittest.TestCase):
    """예외 클래스 계층 테스트"""
    
    @unittest.skipUnless(IMPORTS_OK, "Import failed")
    def test_exception_inheritance(self):
        """예외 클래스 상속 구조 확인"""
        # KiwoomAPIError는 APIError를 상속해야 함
        from pykiwoom_rest.base_api import APIError
        self.assertTrue(issubclass(KiwoomAPIError, APIError))
        
        # 모든 예외는 Exception을 상속해야 함
        self.assertTrue(issubclass(KiwoomAPIError, Exception))
        self.assertTrue(issubclass(RateLimitExceededError, Exception))
    
    @unittest.skipUnless(IMPORTS_OK, "Import failed")
    def test_kiwoom_api_error_attributes(self):
        """KiwoomAPIError 속성 테스트"""
        error = KiwoomAPIError(
            message="테스트 에러",
            error_code="E001",
            error_msg="상세 에러 메시지"
        )
        
        self.assertEqual(str(error), "테스트 에러")
        self.assertEqual(error.error_code, "E001")
        self.assertEqual(error.error_msg, "상세 에러 메시지")


class TestBasicConfiguration(unittest.TestCase):
    """기본 설정 테스트"""
    
    @unittest.skipUnless(IMPORTS_OK, "Import failed")
    def test_endpoint_mapping(self):
        """엔드포인트 매핑 확인"""
        # KiwoomAPIBase 엔드포인트
        expected_endpoints = [
            'auth_token',
            'stock_info', 
            'chart',
            'ranking',
            'market_condition'
        ]
        
        for endpoint in expected_endpoints:
            self.assertIn(endpoint, KiwoomAPIBase.ENDPOINTS)
            self.assertTrue(KiwoomAPIBase.ENDPOINTS[endpoint].startswith('/'))
    
    @unittest.skipUnless(IMPORTS_OK, "Import failed")
    def test_base_url_configuration(self):
        """기본 URL 설정 확인"""
        self.assertEqual(KiwoomAPIBase.BASE_URL, "https://api.kiwoom.com")


class TestMethodSignatures(unittest.TestCase):
    """메서드 시그니처 테스트"""
    
    @unittest.skipUnless(IMPORTS_OK, "Import failed")
    def test_stock_api_methods(self):
        """StockAPI 메서드 존재 확인"""
        stock_methods = [
            'get_stock_basic_info',
            'get_stock_quote',
            'get_execution_info',
            'get_credit_trend'
        ]
        
        for method_name in stock_methods:
            self.assertTrue(hasattr(StockAPI, method_name))
            method = getattr(StockAPI, method_name)
            self.assertTrue(callable(method))
    
    @unittest.skipUnless(IMPORTS_OK, "Import failed")
    def test_chart_api_methods(self):
        """ChartAPI 메서드 존재 확인"""
        chart_methods = [
            'get_tick_chart',
            'get_minute_chart', 
            'get_daily_chart',
            'get_weekly_chart',
            'get_monthly_chart',
            'get_yearly_chart'
        ]
        
        for method_name in chart_methods:
            self.assertTrue(hasattr(ChartAPI, method_name))
            method = getattr(ChartAPI, method_name)
            self.assertTrue(callable(method))
    
    @unittest.skipUnless(IMPORTS_OK, "Import failed") 
    def test_ranking_api_methods(self):
        """RankingAPI 메서드 존재 확인"""
        ranking_methods = [
            'get_volume_top',
            'get_volume_surge',
            'get_trading_volume_surge',
            'get_previous_day_rate_top'
        ]
        
        for method_name in ranking_methods:
            self.assertTrue(hasattr(RankingAPI, method_name))
            method = getattr(RankingAPI, method_name)
            self.assertTrue(callable(method))


class TestHelperMethods(unittest.TestCase):
    """헬퍼 메서드 테스트"""
    
    @unittest.skipUnless(IMPORTS_OK, "Import failed")
    def test_market_code_conversion(self):
        """시장 코드 변환 테스트"""
        ranking = RankingAPI.__new__(RankingAPI)  # 인스턴스 생성 (초기화 없이)
        
        self.assertEqual(ranking._get_market_code("ALL"), "0000")
        self.assertEqual(ranking._get_market_code("KOSPI"), "0001")
        self.assertEqual(ranking._get_market_code("KOSDAQ"), "1001")
        with self.assertRaises(ValueError):
            ranking._get_market_code("UNKNOWN")


if __name__ == '__main__':
    # 자세한 출력으로 테스트 실행
    unittest.main(verbosity=2)
