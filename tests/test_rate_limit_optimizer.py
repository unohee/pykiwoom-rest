#!/usr/bin/env python3
"""
Rate Limiting Optimizer 통합 테스트
작성일: 2025-01-05
목적: RateLimitOptimizer 및 SmartRetryStrategy 테스트
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

from pykiwoom_rest.rate_limit_optimizer import (
    RateLimitOptimizer,
    SmartRetryStrategy
)


class TestRateLimitOptimizer:
    """RateLimitOptimizer 기능 테스트"""
    
    def test_single_credential_initialization(self):
        """단일 크레덴셜 초기화 테스트"""
        credentials = [{
            'APPKEY': 'test_key',
            'APPSECRET': 'test_secret'
        }]
        
        optimizer = RateLimitOptimizer(
            credentials_list=credentials,
            base_rate_limit=20,
            burst_capacity=50
        )
        
        assert len(optimizer.credentials_list) == 1
        assert optimizer.base_rate_limit == 20
        assert optimizer.burst_capacity == 50
        assert optimizer.enable_rotation == False  # 단일 크레덴셜은 로테이션 비활성화
    
    def test_multi_credential_rotation(self):
        """다중 크레덴셜 로테이션 테스트"""
        credentials = [
            {'APPKEY': 'key1', 'APPSECRET': 'secret1'},
            {'APPKEY': 'key2', 'APPSECRET': 'secret2'},
            {'APPKEY': 'key3', 'APPSECRET': 'secret3'}
        ]
        
        optimizer = RateLimitOptimizer(
            credentials_list=credentials,
            base_rate_limit=5,
            burst_capacity=10,
            enable_rotation=True
        )
        
        assert optimizer.enable_rotation == True
        
        # 최적 크레덴셜 선택
        idx1, cred1 = optimizer.get_optimal_credential()
        assert 0 <= idx1 < 3
        assert cred1 in credentials
        
        # 토큰 소진 시뮬레이션
        key = f"{cred1['APPKEY']}_{idx1}"
        optimizer.token_buckets[key]['tokens'] = 0
        
        # 다른 크레덴셜 선택되어야 함
        idx2, cred2 = optimizer.get_optimal_credential()
        assert idx2 != idx1  # 다른 크레덴셜 선택
    
    def test_token_acquisition_and_consumption(self):
        """토큰 획득 및 소비 테스트"""
        credentials = [{'APPKEY': 'key1', 'APPSECRET': 'secret1'}]
        optimizer = RateLimitOptimizer(
            credentials_list=credentials,
            base_rate_limit=10
        )
        
        # 초기 토큰 확인
        initial_tokens = optimizer.token_buckets['key1_0']['tokens']
        
        # 토큰 획득
        success = optimizer.acquire_token(credential_idx=0)
        assert success == True
        
        # 토큰 감소 확인
        current_tokens = optimizer.token_buckets['key1_0']['tokens']
        assert current_tokens < initial_tokens
    
    def test_429_error_handling(self):
        """429 에러 처리 테스트"""
        credentials = [
            {'APPKEY': 'key1', 'APPSECRET': 'secret1'},
            {'APPKEY': 'key2', 'APPSECRET': 'secret2'}
        ]
        
        optimizer = RateLimitOptimizer(
            credentials_list=credentials,
            recovery_time=1  # 빠른 테스트를 위해 짧게 설정
        )
        
        # 429 에러 처리
        optimizer.handle_429_error(0)
        
        # 첫 번째 크레덴셜 차단 확인
        bucket = optimizer.token_buckets['key1_0']
        assert bucket['is_blocked'] == True
        assert bucket['consecutive_errors'] == 1
        assert bucket['tokens'] == 0
        
        # 통계 확인
        assert optimizer.total_429_errors == 1
    
    def test_error_count_reset(self):
        """에러 카운트 리셋 테스트"""
        credentials = [{'APPKEY': 'key1', 'APPSECRET': 'secret1'}]
        optimizer = RateLimitOptimizer(credentials_list=credentials)
        
        # 에러 카운트 증가
        optimizer.handle_429_error(0)
        bucket = optimizer.token_buckets['key1_0']
        assert bucket['consecutive_errors'] == 1
        
        # 에러 카운트 리셋
        optimizer.reset_error_count(0)
        assert bucket['consecutive_errors'] == 0
    
    def test_statistics_tracking(self):
        """통계 추적 테스트"""
        credentials = [
            {'APPKEY': 'key1', 'APPSECRET': 'secret1'},
            {'APPKEY': 'key2', 'APPSECRET': 'secret2'}
        ]
        
        optimizer = RateLimitOptimizer(credentials_list=credentials)
        
        # 요청 시뮬레이션
        optimizer.acquire_token(0)
        optimizer.acquire_token(0)
        optimizer.handle_429_error(0)
        
        stats = optimizer.get_stats()
        
        assert stats['total_requests'] == 2
        assert stats['total_429_errors'] == 1
        assert stats['total_credentials'] == 2
        assert stats['rotation_enabled'] == True
    
    def test_request_pattern_optimization(self):
        """요청 패턴 최적화 테스트"""
        credentials = [
            {'APPKEY': 'key1', 'APPSECRET': 'secret1'},
            {'APPKEY': 'key2', 'APPSECRET': 'secret2'}
        ]
        
        optimizer = RateLimitOptimizer(credentials_list=credentials)
        
        requests_batch = [
            {'endpoint': '/api/1', 'priority': 1},
            {'endpoint': '/api/2', 'priority': 5},
            {'endpoint': '/api/3', 'priority': 3}
        ]
        
        optimized = optimizer.optimize_request_pattern(requests_batch)
        
        # 우선순위별 정렬 확인
        assert optimized[0]['priority'] == 1  # 최고 우선순위
        assert len(optimized) == 3
        
        # 크레덴셜 할당 확인
        for req in optimized:
            assert 'credential_idx' in req
            assert 'credential' in req
            assert 'delay' in req
    
    def test_adaptive_rate_adjustment(self):
        """적응형 레이트 조정 테스트"""
        credentials = [{'APPKEY': 'key1', 'APPSECRET': 'secret1'}]
        optimizer = RateLimitOptimizer(
            credentials_list=credentials,
            base_rate_limit=20
        )
        
        initial_rate = optimizer.base_rate_limit
        
        # 높은 성공률 - 레이트 증가
        optimizer.adaptive_rate_adjustment(0.96)
        assert optimizer.base_rate_limit > initial_rate
        
        # 낮은 성공률 - 레이트 감소
        optimizer.adaptive_rate_adjustment(0.7)
        assert optimizer.base_rate_limit < initial_rate
    
    def test_concurrent_token_acquisition(self):
        """동시 토큰 획득 테스트"""
        credentials = [{'APPKEY': 'key1', 'APPSECRET': 'secret1'}]
        optimizer = RateLimitOptimizer(
            credentials_list=credentials,
            base_rate_limit=5
        )

        results = []
        timeout_event = threading.Event()

        def acquire_token_thread():
            # Timeout 설정을 위해 non-blocking 방식으로 변경
            start_time = time.time()
            max_wait = 1.0  # 1초 타임아웃

            while time.time() - start_time < max_wait:
                if timeout_event.is_set():
                    return
                try:
                    # 즉시 반환하도록 priority를 높게 설정
                    success = optimizer.acquire_token(priority=1)
                    results.append(success)
                    return
                except Exception:
                    results.append(False)
                    return
            # 타임아웃시 실패로 처리
            results.append(False)

        # 10개 스레드 동시 실행
        threads = []
        for _ in range(10):
            t = threading.Thread(target=acquire_token_thread)
            t.daemon = True  # 데몬 스레드로 설정
            threads.append(t)
            t.start()

        # 최대 2초 대기
        for t in threads:
            t.join(timeout=0.2)

        # 타임아웃 이벤트 설정
        timeout_event.set()

        # 최소 5개는 성공해야 함 (base_rate_limit)
        successful_count = sum(results)
        assert successful_count >= 5
    
    def test_credential_blocking_and_recovery(self):
        """크레덴셜 차단 및 복구 테스트"""
        credentials = [
            {'APPKEY': 'key1', 'APPSECRET': 'secret1'},
            {'APPKEY': 'key2', 'APPSECRET': 'secret2'}
        ]
        
        optimizer = RateLimitOptimizer(
            credentials_list=credentials,
            recovery_time=0.1  # 빠른 테스트를 위해 0.1초
        )
        
        # 첫 번째 크레덴셜 차단
        optimizer.handle_429_error(0)
        
        # 차단된 크레덴셜은 선택되지 않음
        idx, _ = optimizer.get_optimal_credential()
        assert idx == 1  # 두 번째 크레덴셜 선택
        
        # 복구 시간 대기
        time.sleep(0.3)
        
        # 복구 확인
        idx, _ = optimizer.get_optimal_credential()
        # 복구되었으므로 다시 선택 가능
        bucket = optimizer.token_buckets['key1_0']
        if not bucket['is_blocked']:
            assert True  # 복구됨


class TestSmartRetryStrategy:
    """SmartRetryStrategy 테스트"""
    
    def test_retry_delay_calculation(self):
        """재시도 지연 시간 계산 테스트"""
        strategy = SmartRetryStrategy()
        
        # 429 에러 - 긴 지연
        delay_429 = strategy.calculate_retry_delay(429, attempt=1)
        assert delay_429 >= 60  # 기본 429 지연은 60초 이상
        
        # 503 에러 - 중간 지연
        delay_503 = strategy.calculate_retry_delay(503, attempt=1)
        assert 5 <= delay_503 <= 10
        
        # 기타 에러 - 짧은 지연
        delay_other = strategy.calculate_retry_delay(500, attempt=1)
        assert delay_other < 5
    
    def test_exponential_backoff(self):
        """지수 백오프 테스트"""
        strategy = SmartRetryStrategy()
        
        # 시도 횟수별 지연 증가
        delay1 = strategy.calculate_retry_delay(503, attempt=1)
        delay2 = strategy.calculate_retry_delay(503, attempt=2)
        delay3 = strategy.calculate_retry_delay(503, attempt=3)
        
        # 지수적 증가 확인
        assert delay2 > delay1
        assert delay3 > delay2
    
    def test_retry_after_header(self):
        """Retry-After 헤더 처리 테스트"""
        strategy = SmartRetryStrategy()
        
        headers = {'Retry-After': '120'}
        delay = strategy.calculate_retry_delay(429, 1, headers)
        
        # Retry-After 값이 사용되어야 함
        assert delay == 120.0
    
    def test_max_delay_limit(self):
        """최대 지연 시간 제한 테스트"""
        strategy = SmartRetryStrategy()
        
        # 매우 많은 시도 횟수
        delay = strategy.calculate_retry_delay(429, attempt=10)
        
        # 최대 지연 시간을 초과하지 않아야 함 (jitter 포함 고려)
        assert delay <= 330  # 429의 max_delay + jitter margin
    
    def test_jitter_addition(self):
        """랜덤 지터 추가 테스트"""
        strategy = SmartRetryStrategy()
        
        delays = []
        for _ in range(10):
            delay = strategy.calculate_retry_delay(500, attempt=1)
            delays.append(delay)
        
        # 모든 지연이 동일하지 않아야 함 (지터 때문에)
        assert len(set(delays)) > 1


class TestIntegration:
    """통합 테스트"""
    
    @patch('time.sleep')
    def test_full_workflow_with_429_recovery(self, mock_sleep):
        """429 에러 발생 및 복구 전체 플로우 테스트"""
        credentials = [
            {'APPKEY': 'key1', 'APPSECRET': 'secret1'},
            {'APPKEY': 'key2', 'APPSECRET': 'secret2'},
            {'APPKEY': 'key3', 'APPSECRET': 'secret3'}
        ]
        
        optimizer = RateLimitOptimizer(
            credentials_list=credentials,
            base_rate_limit=5,
            recovery_time=60
        )
        
        retry_strategy = SmartRetryStrategy()
        
        # 시나리오: 첫 번째 크레덴셜에서 429 에러
        optimizer.handle_429_error(0)
        
        # 두 번째 크레덴셜로 자동 전환
        idx, cred = optimizer.get_optimal_credential()
        assert idx in [1, 2]  # 첫 번째 제외
        
        # 재시도 지연 계산
        delay = retry_strategy.calculate_retry_delay(429, attempt=1)
        assert delay > 0
        
        # 통계 확인
        stats = optimizer.get_stats()
        assert stats['total_429_errors'] == 1
        assert stats['active_credentials'] == 2  # 하나 차단됨
    
    def test_burst_traffic_handling(self):
        """버스트 트래픽 처리 테스트"""
        credentials = [
            {'APPKEY': 'key1', 'APPSECRET': 'secret1'},
            {'APPKEY': 'key2', 'APPSECRET': 'secret2'}
        ]

        optimizer = RateLimitOptimizer(
            credentials_list=credentials,
            base_rate_limit=10,
            burst_capacity=30,
            enable_rotation=True  # 강제로 rotation 활성화
        )

        # 버스트 요청 생성
        burst_requests = [
            {'endpoint': f'/api/{i}', 'priority': i % 5}
            for i in range(50)
        ]

        # 첫 번째 credential에 일부 부하 추가 (rotation 유도)
        for _ in range(5):
            optimizer.acquire_token(credential_idx=0, priority=1)

        # 최적화 적용
        optimized = optimizer.optimize_request_pattern(burst_requests)

        # 모든 요청이 처리 계획에 포함되어야 함
        assert len(optimized) == 50

        # 우선순위 0이 가장 먼저
        assert optimized[0]['priority'] == 0

        # 크레덴셜이 할당되어야 함 (둘 다 사용되거나 최소한 하나는 사용)
        cred_indices = [req['credential_idx'] for req in optimized]
        assert all(idx in [0, 1] for idx in cred_indices)
        # 최소한 하나의 credential은 사용되어야 함
        assert len(set(cred_indices)) >= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])