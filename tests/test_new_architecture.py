"""
PyKiwoom-Rest v2 New Architecture Test
새로운 모듈러 아키텍처 테스트
작성일: 2025-01-27
"""

import unittest
import os
import time
from unittest.mock import Mock, patch, MagicMock
from pykiwoom_rest.base_api import TokenBucketRateLimiter, RateLimitExceededError
from pykiwoom_rest.kiwoom_base import KiwoomAPIBase, KiwoomAPIError
from pykiwoom_rest.stock_api import StockAPI
from pykiwoom_rest.chart_api import ChartAPI
from pykiwoom_rest.ranking_api import RankingAPI
from pykiwoom_rest.kiwoom_rest import KiwoomRest


class TestTokenBucketRateLimiter(unittest.TestCase):
    """Token Bucket Rate Limiter 테스트"""
    
    def test_basic_token_acquisition(self):
        """기본 토큰 획득 테스트"""
        limiter = TokenBucketRateLimiter(rate=10, per_seconds=1.0)
        
        # 초기에는 모든 토큰 사용 가능
        for _ in range(10):
            self.assertTrue(limiter.acquire(blocking=False))
        
        # 토큰 소진 후에는 False 반환
        self.assertFalse(limiter.acquire(blocking=False))
    
    def test_token_refill(self):
        """토큰 보충 테스트"""
        limiter = TokenBucketRateLimiter(rate=2, per_seconds=0.1)  # 0.1초마다 2개씩
        
        # 모든 토큰 소진
        limiter.acquire(tokens=2, blocking=False)
        self.assertFalse(limiter.acquire(blocking=False))
        
        # 시간 경과 후 토큰 보충 확인
        time.sleep(0.15)  # 0.1초보다 조금 더 대기
        self.assertTrue(limiter.acquire(blocking=False))
    
    def test_blocking_acquisition(self):
        """블로킹 토큰 획득 테스트"""
        limiter = TokenBucketRateLimiter(rate=1, per_seconds=0.1)
        
        # 토큰 소진
        limiter.acquire()
        
        # 블로킹 모드에서 토큰 획득 (시간이 좀 걸릴 것)
        start_time = time.time()
        success = limiter.acquire(timeout=0.2)
        elapsed = time.time() - start_time
        
        self.assertTrue(success)
        self.assertGreater(elapsed, 0.08)  # 최소한의 대기 시간


class TestKiwoomAPIBase(unittest.TestCase):
    """KiwoomAPIBase 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        # 환경변수 모킹
        self.env_patcher = patch.dict(os.environ, {
            'ACCOUNT_NO': '12345678',
            'KIWOOM_APPKEY': 'test_app_key',
            'KIWOOM_APPSECRET': 'test_app_secret'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        """테스트 정리"""
        self.env_patcher.stop()
    
    @patch('requests.Session')
    def test_initialization(self, mock_session_class):
        """초기화 테스트"""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        api = KiwoomAPIBase()
        
        self.assertEqual(api.account_no, '12345678')
        self.assertEqual(api.appkey, 'test_app_key')
        self.assertEqual(api.appsecret, 'test_app_secret')
        self.assertIsNone(api.access_token)
    
    @patch('requests.Session')
    def test_token_acquisition(self, mock_session_class):
        """토큰 발급 테스트"""
        # Mock 응답 설정
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'token': 'test_access_token',
            'return_code': 0,
            'expires_dt': '20990101T000000'
        }
        mock_response.raise_for_status = MagicMock()
        
        mock_session = MagicMock()
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        api = KiwoomAPIBase()
        token = api._get_access_token()
        
        self.assertEqual(token, 'test_access_token')
        self.assertEqual(api.access_token, 'test_access_token')
        self.assertIsNotNone(api.token_expires)
    
    def test_error_handling(self):
        """에러 처리 테스트"""
        # 잘못된 인증 정보로 초기화 시도
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                KiwoomAPIBase()


class TestStockAPI(unittest.TestCase):
    """StockAPI 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.env_patcher = patch.dict(os.environ, {
            'ACCOUNT_NO': '12345678',
            'KIWOOM_APPKEY': 'test_app_key',
            'KIWOOM_APPSECRET': 'test_app_secret'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        """테스트 정리"""
        self.env_patcher.stop()
    
    @patch('requests.Session')
    def test_get_stock_basic_info(self, mock_session_class):
        """주식 기본 정보 조회 테스트"""
        # Mock 응답
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'rt_cd': '0',
            'msg1': 'Success',
            'output': {
                'stck_prpr': '70000',
                'stck_prdy_vrss': '1000',
                'prdy_vrss_sign': '2'
            }
        }
        mock_response.raise_for_status = MagicMock()
        
        mock_session = MagicMock()
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        # 토큰 발급도 모킹
        with patch.object(StockAPI, '_get_access_token', return_value='test_token'):
            api = StockAPI()
            result = api.get_stock_basic_info('005930')
            
            self.assertEqual(result['rt_cd'], '0')
            self.assertIn('output', result)


class TestChartAPI(unittest.TestCase):
    """ChartAPI 테스트"""
    
    def setUp(self):
        self.env_patcher = patch.dict(os.environ, {
            'ACCOUNT_NO': '12345678',
            'KIWOOM_APPKEY': 'test_app_key',
            'KIWOOM_APPSECRET': 'test_app_secret'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        self.env_patcher.stop()
    
    @patch('requests.Session')
    def test_get_minute_chart(self, mock_session_class):
        """분봉 차트 조회 테스트"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'rt_cd': '0',
            'msg1': 'Success',
            'output2': [
                {
                    'stck_bsop_date': '20250127',
                    'stck_cntg_hour': '1530',
                    'stck_prpr': '70000',
                    'stck_oprc': '69900',
                    'stck_hgpr': '70100',
                    'stck_lwpr': '69800',
                    'acml_vol': '1000000'
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        
        mock_session = MagicMock()
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session
        
        with patch.object(ChartAPI, '_get_access_token', return_value='test_token'):
            with patch.object(ChartAPI, '_get_hashkey', return_value='test_hash'):
                api = ChartAPI()
                result = api.get_minute_chart('005930', interval=1)
                
                self.assertEqual(result['rt_cd'], '0')
                self.assertIn('output2', result)
                self.assertEqual(len(result['output2']), 1)


class TestKiwoomRestIntegration(unittest.TestCase):
    """KiwoomRest 통합 테스트"""
    
    def setUp(self):
        self.env_patcher = patch.dict(os.environ, {
            'ACCOUNT_NO': '12345678',
            'KIWOOM_APPKEY': 'test_app_key',
            'KIWOOM_APPSECRET': 'test_app_secret'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        self.env_patcher.stop()
    
    @patch('requests.Session')
    def test_facade_pattern(self, mock_session_class):
        """Facade 패턴 테스트"""
        # Mock 세션
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Mock 응답
        mock_response = MagicMock()
        mock_response.json.return_value = {'rt_cd': '0', 'msg1': 'Success'}
        mock_response.raise_for_status = MagicMock()
        mock_session.request.return_value = mock_response
        
        with patch.object(StockAPI, '_get_access_token', return_value='test_token'):
            facade = KiwoomRest()
            
            # Facade를 통한 메서드 호출
            result = facade.get_stock_price('005930')
            self.assertEqual(result['rt_cd'], '0')
            
            # 직접 API 접근
            result2 = facade.stock.get_stock_basic_info('005930')
            self.assertEqual(result2['rt_cd'], '0')
    
    def test_context_manager(self):
        """Context Manager 테스트"""
        with patch('requests.Session'):
            with patch.object(StockAPI, '_get_access_token', return_value='test_token'):
                with KiwoomRest() as facade:
                    # Context 내에서 사용
                    stats = facade.get_stats()
                    self.assertIn('total_requests', stats)
                    self.assertIn('total_errors', stats)
    
    def test_rate_limiting_integration(self):
        """Rate limiting 통합 테스트"""
        with patch('requests.Session'):
            with patch.object(StockAPI, '_get_access_token', return_value='test_token'):
                # 낮은 rate limit 설정
                facade = KiwoomRest(rate_limit=2)
                
                # Rate limiter가 적용되었는지 확인
                self.assertEqual(facade.stock_api.rate_limiter.rate, 2)
                self.assertEqual(facade.chart_api.rate_limiter.rate, 2)
                self.assertEqual(facade.ranking_api.rate_limiter.rate, 2)


class TestRateLimitingBehavior(unittest.TestCase):
    """Rate Limiting 동작 테스트"""
    
    def test_rate_limit_enforcement(self):
        """Rate limit 강제 적용 테스트"""
        limiter = TokenBucketRateLimiter(rate=3, per_seconds=1.0)
        
        # 허용량만큼 즉시 처리
        start_time = time.time()
        for _ in range(3):
            self.assertTrue(limiter.acquire(blocking=False))
        
        # 초과 요청은 차단
        self.assertFalse(limiter.acquire(blocking=False))
        
        # 전체 처리 시간이 매우 짧아야 함
        elapsed = time.time() - start_time
        self.assertLess(elapsed, 0.1)
    
    def test_concurrent_rate_limiting(self):
        """동시 요청에서의 rate limiting 테스트"""
        import threading
        
        limiter = TokenBucketRateLimiter(rate=5, per_seconds=1.0)
        results = []
        
        def worker():
            result = limiter.acquire(blocking=False)
            results.append(result)
        
        # 10개의 동시 요청 (5개만 성공해야 함)
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # 모든 스레드 완료 대기
        for thread in threads:
            thread.join()
        
        # 정확히 5개만 성공
        successful_requests = sum(results)
        self.assertEqual(successful_requests, 5)


if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2)
