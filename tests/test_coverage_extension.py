#!/usr/bin/env python3
"""
커버리지 확장을 위한 추가 테스트
현재 커버리지가 낮은 모듈들의 누락된 부분들을 테스트
"""

import pytest
import os
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from pykiwoom_rest.base_api import TokenBucketRateLimiter, RateLimitExceeded, APIError
from pykiwoom_rest.kiwoom_base import KiwoomAPIError


class TestTokenBucketRateLimiter:
    """TokenBucketRateLimiter 전체 기능 테스트"""

    def test_initialization_edge_cases(self):
        """초기화 엣지 케이스 테스트"""
        # 정상적인 초기화 (현재 validation이 없으므로)
        limiter = TokenBucketRateLimiter(rate=0, per_seconds=1.0)
        assert limiter.rate == 0
        
        # 음수 rate도 현재는 허용됨
        limiter2 = TokenBucketRateLimiter(rate=-5, per_seconds=1.0)
        assert limiter2.rate == -5

    def test_blocking_acquisition_timeout(self):
        """블로킹 토큰 획득 타임아웃 테스트"""
        limiter = TokenBucketRateLimiter(rate=1, per_seconds=10.0)  # 매우 느린 충전
        
        # 모든 토큰 소진
        assert limiter.acquire(blocking=False) == True
        assert limiter.acquire(blocking=False) == False
        
        # 짧은 타임아웃으로 실패 확인
        start_time = time.time()
        success = limiter.acquire(timeout=0.1, blocking=True)
        elapsed = time.time() - start_time
        
        assert success == False
        assert elapsed >= 0.1

    def test_multiple_tokens_acquisition(self):
        """복수 토큰 획득 테스트"""
        limiter = TokenBucketRateLimiter(rate=10, per_seconds=1.0)
        
        # 5개 토큰 한번에 획득
        assert limiter.acquire(tokens=5, blocking=False) == True
        assert limiter.tokens == 5
        
        # 남은 토큰보다 많이 요청 시 실패
        assert limiter.acquire(tokens=10, blocking=False) == False

    def test_rate_limit_exceeded_exception(self):
        """RateLimitExceeded 예외 테스트"""
        exception = RateLimitExceeded("Rate limit exceeded")
        assert str(exception) == "Rate limit exceeded"
        assert isinstance(exception, Exception)

    def test_reset_functionality(self):
        """리셋 기능 테스트"""
        limiter = TokenBucketRateLimiter(rate=5, per_seconds=1.0)
        
        # 토큰 소진
        limiter.acquire(tokens=5, blocking=False)
        assert limiter.tokens == 0
        
        # 리셋
        limiter.reset()
        assert limiter.tokens == limiter.max_tokens


class TestKiwoomAPIError:
    """KiwoomAPIError 예외 클래스 테스트"""

    def test_error_initialization(self):
        """에러 초기화 테스트"""
        error = KiwoomAPIError(
            message="테스트 에러",
            error_code="E001", 
            error_msg="상세 에러 메시지"
        )
        
        assert str(error) == "테스트 에러"
        assert error.error_code == "E001"
        assert error.error_msg == "상세 에러 메시지"
        assert isinstance(error, APIError)

    def test_error_without_details(self):
        """상세 정보 없는 에러 테스트"""
        error = KiwoomAPIError("기본 에러 메시지")
        
        assert str(error) == "기본 에러 메시지"
        assert error.error_code is None
        assert error.error_msg is None


class TestAPIResponseEdgeCases:
    """원시 JSON 전환에 따라 APIResponse 관련 테스트 제거됨"""
    def test_placeholder(self):
        assert True


class TestEnvironmentHandling:
    """환경변수 처리 관련 테스트"""

    def test_dotenv_import_fallback(self, mock_env_vars):
        """dotenv 임포트 실패 시 수동 파싱 테스트"""
        from pykiwoom_rest.kiwoom_base import KiwoomAPIBase
        
        # dotenv 모듈에 대해서만 ImportError를 유도
        import importlib as _orig_importlib
        _real_import = _orig_importlib.import_module

        def _import_side_effect(name, *args, **kwargs):
            if name == 'dotenv':
                raise ImportError("No module named 'dotenv'")
            return _real_import(name)

        with patch('importlib.import_module', side_effect=_import_side_effect):
            
            # .env 파일 생성
            env_content = "TEST_KEY=test_value\nACCOUNT_NO=12345\n# 주석\nEMPTY_LINE=\n"
            with patch('builtins.open', mock_open(env_content)):
                with patch('os.path.exists', return_value=True):
                    api = KiwoomAPIBase.__new__(KiwoomAPIBase)
                    api._load_env_file('/fake/path/.env')

    def test_manual_env_parsing(self):
        """수동 환경변수 파싱 테스트"""
        from pykiwoom_rest.kiwoom_base import KiwoomAPIBase
        
        api = KiwoomAPIBase.__new__(KiwoomAPIBase)
        
        # 테스트용 .env 내용
        env_lines = [
            "VALID_KEY=valid_value",
            "# 이것은 주석",
            "",  # 빈 줄
            "KEY_WITH_EQUALS=value=with=equals",
            "NO_VALUE_KEY="
        ]
        
        with patch('builtins.open', mock_open('\n'.join(env_lines))):
            with patch('os.path.exists', return_value=True):
                original_env = os.environ.copy()
                try:
                    api._manual_load_env('/fake/.env')
                    # 환경변수가 설정되었는지 확인
                    assert os.environ.get('VALID_KEY') == 'valid_value'
                    assert os.environ.get('KEY_WITH_EQUALS') == 'value=with=equals'
                finally:
                    # 환경변수 복원
                    os.environ.clear()
                    os.environ.update(original_env)


def mock_open(content):
    """파일 모킹 헬퍼"""
    from unittest.mock import mock_open as orig_mock_open
    return orig_mock_open(read_data=content)
