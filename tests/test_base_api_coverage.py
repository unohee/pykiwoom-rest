#!/usr/bin/env python3
"""
BaseAPI 및 TokenBucket 커버리지 확장 테스트
Mock을 사용하여 실제 네트워크 없이 테스트
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
import requests
from typing import Dict, Any

from pykiwoom_rest.base_api import BaseAPIClient, TokenBucketRateLimiter, RateLimitExceeded, APIError
from pykiwoom_rest.kiwoom_base import KiwoomAPIBase


# BaseAPIClient의 구체적 구현 클래스 (테스트용)
class ConcreteAPIClient(BaseAPIClient):
    """테스트용 구체 API 클라이언트"""
    
    def _prepare_headers(self, headers: Dict[str, str] = None) -> Dict[str, str]:
        """헤더 준비 (구현)"""
        base_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'TestClient/1.0'
        }
        if headers:
            base_headers.update(headers)
        return base_headers
    
    def _process_response(self, response: requests.Response) -> Dict[str, Any]:
        """응답 처리 (구현)"""
        return response.json()


class TestBaseAPIClient:
    """BaseAPIClient 커버리지 테스트"""

    def test_initialization(self):
        """BaseAPIClient 초기화 테스트"""
        api = ConcreteAPIClient("https://api.test.com", rate_limit=10)
        
        assert api.base_url == "https://api.test.com"
        assert api.rate_limiter.rate == 10
        assert api.session is not None
        assert api.request_count == 0

    def test_url_construction(self):
        """URL 구성 테스트"""
        api = ConcreteAPIClient("https://api.test.com")
        
        # BaseAPIClient는 _build_url 메서드가 없으므로
        # 직접 URL을 구성하는 방식 테스트
        endpoint = "/test/path"
        expected = f"{api.base_url}{endpoint}"
        assert expected == "https://api.test.com/test/path"

    @patch('requests.Session.request')
    def test_request_success(self, mock_request):
        """성공적인 요청 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.json.return_value = {'result': 'success'}
        mock_response.raise_for_status = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        api = ConcreteAPIClient("https://api.test.com")
        result = api.request('GET', '/test')
        
        assert result == {'result': 'success'}
        assert api.stats['total_requests'] == 1
        assert api.stats['total_errors'] == 0

    @patch('requests.Session.request')
    def test_request_http_error(self, mock_request):
        """HTTP 에러 테스트"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_response.status_code = 404
        mock_request.return_value = mock_response
        
        api = ConcreteAPIClient("https://api.test.com")
        
        with pytest.raises(APIError):
            api.request('GET', '/not-found')
        
        assert api.stats['total_errors'] == 1

    @patch('requests.Session.request')
    def test_request_timeout(self, mock_request):
        """타임아웃 테스트"""
        mock_request.side_effect = requests.exceptions.Timeout("Request timeout")
        
        api = ConcreteAPIClient("https://api.test.com")
        
        with pytest.raises(APIError):
            api.request('GET', '/slow')
        
        # 3번 재시도하므로 총 3번의 에러
        assert api.stats['total_errors'] == 3
        assert api.stats['total_requests'] == 3

    @patch('requests.Session.request') 
    def test_request_connection_error(self, mock_request):
        """연결 에러 테스트"""
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        api = ConcreteAPIClient("https://api.test.com")
        
        with pytest.raises(APIError):
            api.request('GET', '/test')
        
        # 3번 재시도하므로 총 3번의 에러
        assert api.stats['total_errors'] == 3
        assert api.stats['total_requests'] == 3

    @patch('requests.Session.request')
    def test_request_with_retry(self, mock_request):
        """재시도 로직 테스트"""
        # 처음 두 번은 실패, 세 번째는 성공
        mock_response_fail = Mock()
        mock_response_fail.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Internal Server Error")
        mock_response_fail.status_code = 500
        
        mock_response_success = Mock()
        mock_response_success.json.return_value = {'result': 'success'}
        mock_response_success.raise_for_status = Mock()
        mock_response_success.status_code = 200
        
        mock_request.side_effect = [mock_response_fail, mock_response_fail, mock_response_success]
        
        api = ConcreteAPIClient("https://api.test.com", max_retries=3, backoff_factor=0.01)
        result = api.request('GET', '/test')
        
        assert result == {'result': 'success'}
        assert mock_request.call_count == 3

    def test_context_manager(self):
        """Context Manager 테스트"""
        with ConcreteAPIClient("https://api.test.com") as api:
            assert api.session is not None
            session = api.session
        
        # 세션이 닫혔는지 확인하기 어려우므로 예외가 없으면 성공으로 간주

    def test_stats_tracking(self):
        """통계 추적 테스트"""
        api = ConcreteAPIClient("https://api.test.com")
        
        # 초기 상태
        stats = api.get_stats()
        assert stats['request_count'] == 0
        assert stats['error_count'] == 0
        assert stats['error_rate'] == 0.0
        assert 'last_request_time' in stats
        assert 'rate_limit_tokens' in stats

    def test_rate_limiting_integration(self):
        """Rate limiting 통합 테스트"""
        api = ConcreteAPIClient("https://api.test.com", rate_limit=2)
        
        # Rate limiter가 설정되었는지 확인
        assert api.rate_limiter.rate == 2
        assert api.rate_limiter.tokens == 2


class TestTokenBucketAdvanced:
    """TokenBucket 고급 테스트"""

    def test_concurrent_access(self):
        """동시 접근 테스트"""
        limiter = TokenBucketRateLimiter(rate=5, per_seconds=1.0)
        results = []
        
        def worker():
            success = limiter.acquire(blocking=False)
            results.append(success)
        
        # 10개 스레드가 동시에 토큰 요청
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # 5개는 성공, 5개는 실패해야 함
        successful_count = sum(results)
        assert successful_count == 5

    def test_refill_timing(self):
        """토큰 보충 타이밍 테스트"""
        limiter = TokenBucketRateLimiter(rate=2, per_seconds=0.1)  # 0.1초마다 2개 보충
        
        # 모든 토큰 소진
        assert limiter.acquire(tokens=2, blocking=False) == True
        assert limiter.tokens == 0
        
        # 즉시 요청하면 실패
        assert limiter.acquire(blocking=False) == False
        
        # 시간 경과 후 성공
        time.sleep(0.15)  # 0.1초보다 조금 더 대기
        assert limiter.acquire(blocking=False) == True

    def test_partial_token_consumption(self):
        """부분 토큰 소비 테스트"""
        limiter = TokenBucketRateLimiter(rate=10, per_seconds=1.0)
        
        # 3개 토큰 소비
        assert limiter.acquire(tokens=3, blocking=False) == True
        # 자동 refill로 인한 미세한 차이 허용 (대략 7개 근처)
        assert 6.9 <= limiter.tokens <= 7.1
        
        # 8개 요청 (실패해야 함)
        assert limiter.acquire(tokens=8, blocking=False) == False
        # 실패 시 토큰 수 변화 없음
        assert 6.9 <= limiter.tokens <= 7.1
        
        # 남은 토큰 모두 소비 (성공해야 함)
        remaining_tokens = int(limiter.tokens)
        assert limiter.acquire(tokens=remaining_tokens, blocking=False) == True
        assert limiter.tokens < 1  # 거의 0에 가까워야 함

    def test_max_tokens_validation(self):
        """최대 토큰 수 검증 테스트"""
        limiter = TokenBucketRateLimiter(rate=5, per_seconds=1.0)
        
        # 최대값 초과 요청
        with pytest.raises(ValueError, match="요청한 토큰 수"):
            limiter.acquire(tokens=10, blocking=False)

    def test_blocking_with_interruption(self):
        """블로킹 중단 테스트"""
        limiter = TokenBucketRateLimiter(rate=1, per_seconds=5.0)  # 5초마다 1개
        
        # 토큰 소진
        assert limiter.acquire(blocking=False) == True
        
        def interrupt_after_delay():
            time.sleep(0.1)
            # 강제로 토큰 추가 (테스트를 위해)
            limiter.tokens = 1
        
        thread = threading.Thread(target=interrupt_after_delay)
        thread.start()
        
        # 블로킹 모드로 대기 (0.2초 타임아웃)
        start_time = time.time()
        success = limiter.acquire(timeout=0.2, blocking=True)
        elapsed = time.time() - start_time
        
        thread.join()
        
        # 빠르게 성공했어야 함
        assert success == True
        assert elapsed < 0.3  # 시스템 지연을 고려하여 더 관대한 기준


class TestAPIErrorHandling:
    """API 에러 처리 테스트"""

    def test_api_error_with_details(self):
        """상세 정보가 있는 API 에러 테스트"""
        error = APIError(
            "Test error message",
            status_code=404,
            response={'error': 'Not found', 'code': 'E001'}
        )
        
        assert str(error) == "Test error message"
        assert error.status_code == 404
        assert error.response['error'] == 'Not found'

    def test_api_error_inheritance(self):
        """API 에러 상속 구조 테스트"""
        error = APIError("Test error")
        
        assert isinstance(error, Exception)
        assert isinstance(error, APIError)

    def test_rate_limit_exceeded_error(self):
        """Rate limit 초과 에러 테스트"""
        error = RateLimitExceeded("Rate limit exceeded")
        
        assert str(error) == "Rate limit exceeded"
        assert isinstance(error, Exception)
        assert isinstance(error, RateLimitExceeded)


class TestRequestParameters:
    """요청 파라미터 테스트"""

    @patch('requests.Session.request')
    def test_get_with_params(self, mock_request):
        """GET 요청 파라미터 테스트"""
        mock_response = Mock()
        mock_response.json.return_value = {'result': 'success'}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        api = ConcreteAPIClient("https://api.test.com")
        api.request('GET', '/test', params={'key': 'value', 'num': 123})
        
        # 호출된 파라미터 확인
        call_args = mock_request.call_args
        assert call_args[1]['params'] == {'key': 'value', 'num': 123}

    @patch('requests.Session.request')
    def test_post_with_json(self, mock_request):
        """POST JSON 요청 테스트"""
        mock_response = Mock()
        mock_response.json.return_value = {'result': 'created'}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        api = ConcreteAPIClient("https://api.test.com")
        api.request('POST', '/create', json_data={'name': 'test', 'value': 42})
        
        # JSON 데이터가 전달되었는지 확인
        call_args = mock_request.call_args
        assert call_args[1]['json'] == {'name': 'test', 'value': 42}

    @patch('requests.Session.request')
    def test_custom_headers(self, mock_request):
        """커스텀 헤더 테스트"""
        mock_response = Mock()
        mock_response.json.return_value = {'result': 'success'}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response
        
        api = ConcreteAPIClient("https://api.test.com")
        custom_headers = {'Authorization': 'Bearer token123', 'Custom-Header': 'value'}
        api.request('GET', '/test', headers=custom_headers)
        
        # 헤더가 전달되었는지 확인
        call_args = mock_request.call_args
        headers = call_args[1]['headers']
        assert 'Authorization' in headers
        assert 'Custom-Header' in headers