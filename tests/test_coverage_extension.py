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
from pykiwoom_rest.response_model import APIResponse


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
    """APIResponse 엣지 케이스 테스트"""

    def test_empty_data_handling(self):
        """빈 데이터 처리 테스트"""
        response = APIResponse.create_success(data={})
        
        assert response.success == True
        assert len(response) == 0
        assert list(response.keys()) == []
        assert list(response.values()) == []

    def test_complex_data_structures(self):
        """복잡한 데이터 구조 테스트"""
        complex_data = {
            'nested': {'level1': {'level2': 'value'}},
            'list_data': [1, 2, 3, {'inner': 'value'}],
            'mixed': {'numbers': 123, 'strings': 'abc'}
        }
        
        response = APIResponse.create_success(complex_data)
        
        assert response['nested']['level1']['level2'] == 'value'
        assert response['list_data'][3]['inner'] == 'value'
        assert len(response['list_data']) == 4

    def test_dict_interface_completeness(self):
        """dict 인터페이스 완전성 테스트"""
        data = {'key1': 'value1', 'key2': 'value2', 'key3': 123}
        response = APIResponse.create_success(data)
        
        # keys(), values(), items() 테스트
        assert set(response.keys()) == {'key1', 'key2', 'key3'}
        assert set(response.values()) == {'value1', 'value2', 123}
        assert ('key1', 'value1') in response.items()
        
        # update() 메서드 테스트
        response.update({'key4': 'value4'})
        assert response['key4'] == 'value4'
        
        # setitem 테스트
        response['key5'] = 'value5'
        assert response['key5'] == 'value5'

    def test_kiwoom_specific_methods(self):
        """키움 API 특화 메서드 테스트"""
        # 성공 응답
        success_data = {'rt_cd': '0', 'msg1': 'SUCCESS', 'output': [1, 2, 3]}
        success_response = APIResponse.create_success(success_data)
        
        assert success_response.is_kiwoom_success() == True
        assert success_response.get_kiwoom_message() == 'SUCCESS'
        assert success_response.has_output_data('output') == True
        assert success_response.get_output_data('output') == [1, 2, 3]
        
        # 실패 응답
        fail_data = {'rt_cd': '1', 'msg1': 'FAIL'}
        fail_response = APIResponse.create_success(fail_data)
        
        assert fail_response.is_kiwoom_success() == False
        assert fail_response.get_kiwoom_message() == 'FAIL'

    def test_string_representations(self):
        """문자열 표현 테스트"""
        response = APIResponse.create_success(
            {'test': 'data'}, 
            tr_code='ka10001',
            endpoint='test_endpoint'
        )
        
        str_repr = str(response)
        assert 'SUCCESS' in str_repr
        assert 'ka10001' in str_repr
        assert response.__repr__() == str_repr

    def test_boolean_evaluation(self):
        """Boolean 평가 테스트"""
        success_response = APIResponse.create_success({'test': 'data'})
        error_response = APIResponse.create_error('Test error')
        
        assert bool(success_response) == True
        assert bool(error_response) == False
        
        # if문에서 사용
        if success_response:
            result = "success"
        else:
            result = "fail"
        assert result == "success"

    def test_error_response_details(self):
        """에러 응답 상세 정보 테스트"""
        error_details = {'stack_trace': 'line 123', 'request_id': 'req_001'}
        error_response = APIResponse.create_error(
            error_message="상세 에러",
            error_code="E999",
            error_details=error_details,
            tr_code="ka99999",
            endpoint="error_test"
        )
        
        assert error_response.success == False
        assert error_response.error['message'] == "상세 에러"
        assert error_response.error['code'] == "E999"
        assert error_response.error['details']['stack_trace'] == 'line 123'
        assert error_response.metadata['tr_code'] == "ka99999"

    def test_legacy_compatibility(self):
        """하위 호환성 테스트"""
        response = APIResponse.create_success({'rt_cd': '0', 'data_field': 'value'})
        
        # 기존 코드 패턴 동작 확인
        if response.get('rt_cd') == '0':
            success = True
        else:
            success = False
            
        assert success == True
        
        # to_legacy_dict() 메서드
        legacy_dict = response.to_legacy_dict()
        assert isinstance(legacy_dict, dict)
        assert legacy_dict['rt_cd'] == '0'
        assert legacy_dict['data_field'] == 'value'


class TestEnvironmentHandling:
    """환경변수 처리 관련 테스트"""

    def test_dotenv_import_fallback(self, mock_env_vars):
        """dotenv 임포트 실패 시 수동 파싱 테스트"""
        from pykiwoom_rest.kiwoom_base import KiwoomAPIBase
        
        with patch('importlib.import_module') as mock_import:
            mock_import.side_effect = ImportError("No module named 'dotenv'")
            
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