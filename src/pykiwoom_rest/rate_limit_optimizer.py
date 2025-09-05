"""
Rate Limiting 회피 최적화 모듈
작성일: 2025-01-13

키움 API의 유량 제한을 효율적으로 회피하기 위한 최적화 전략:
1. 다중 앱키/시크릿 로테이션
2. 지능형 백오프 알고리즘
3. 요청 분산 및 큐잉
4. 429 에러 자동 감지 및 대응
"""

import time
import threading
import queue
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque, defaultdict
import logging

logger = logging.getLogger(__name__)


class RateLimitOptimizer:
    """고급 Rate Limiting 회피 최적화 클래스"""
    
    def __init__(
        self,
        credentials_list: List[Dict[str, str]] = None,
        base_rate_limit: int = 20,  # 초당 기본 제한
        burst_capacity: int = 50,   # 버스트 허용량
        recovery_time: int = 60,    # 회복 시간(초)
        enable_rotation: bool = True
    ):
        """
        Args:
            credentials_list: 여러 앱키/시크릿 리스트
            base_rate_limit: 기본 초당 요청 제한
            burst_capacity: 버스트 모드 최대 허용량
            recovery_time: 제한 도달 후 회복 시간
            enable_rotation: 크레덴셜 로테이션 활성화
        """
        self.credentials_list = credentials_list or []
        self.base_rate_limit = base_rate_limit
        self.burst_capacity = burst_capacity
        self.recovery_time = recovery_time
        self.enable_rotation = enable_rotation and len(self.credentials_list) > 1
        
        # 현재 활성 크레덴셜 인덱스
        self.current_credential_idx = 0
        self.credential_locks = [threading.Lock() for _ in self.credentials_list]
        
        # 각 크레덴셜별 토큰 버킷
        self.token_buckets = {}
        self.request_history = defaultdict(deque)  # 요청 이력
        self.error_counts = defaultdict(int)  # 에러 카운트
        self.last_429_time = {}  # 마지막 429 에러 시간
        
        # 글로벌 통계
        self.total_requests = 0
        self.total_429_errors = 0
        self.total_rotations = 0
        
        # 요청 큐 (우선순위 큐)
        self.request_queue = queue.PriorityQueue()
        self.queue_processor_thread = None
        self.stop_queue_processor = threading.Event()
        
        # 초기화
        self._initialize_token_buckets()
        
    def _initialize_token_buckets(self):
        """각 크레덴셜별 토큰 버킷 초기화"""
        for i, cred in enumerate(self.credentials_list):
            key = f"{cred.get('APPKEY', '')}_{i}"
            self.token_buckets[key] = {
                'tokens': self.base_rate_limit,
                'max_tokens': self.burst_capacity,
                'last_refill': time.time(),
                'is_blocked': False,
                'block_until': None,
                'consecutive_errors': 0
            }
    
    def get_optimal_credential(self) -> Tuple[int, Dict[str, str]]:
        """
        최적의 크레덴셜 선택 (로드 밸런싱)
        
        Returns:
            (인덱스, 크레덴셜 딕셔너리)
        """
        if not self.enable_rotation:
            return 0, self.credentials_list[0] if self.credentials_list else None
        
        best_idx = -1
        best_score = -1
        
        for i, cred in enumerate(self.credentials_list):
            key = f"{cred.get('APPKEY', '')}_{i}"
            bucket = self.token_buckets.get(key, {})
            
            # 차단된 크레덴셜 스킵
            if bucket.get('is_blocked'):
                if bucket.get('block_until') and time.time() > bucket['block_until']:
                    # 차단 해제
                    bucket['is_blocked'] = False
                    bucket['block_until'] = None
                    bucket['consecutive_errors'] = 0
                else:
                    continue
            
            # 점수 계산 (토큰 수 + 에러 페널티)
            score = bucket.get('tokens', 0) - (bucket.get('consecutive_errors', 0) * 10)
            
            if score > best_score:
                best_score = score
                best_idx = i
        
        if best_idx >= 0:
            self.total_rotations += 1
            return best_idx, self.credentials_list[best_idx]
        
        # 모든 크레덴셜이 차단된 경우, 가장 빨리 해제되는 것 선택
        earliest_unblock = float('inf')
        fallback_idx = 0
        
        for i, cred in enumerate(self.credentials_list):
            key = f"{cred.get('APPKEY', '')}_{i}"
            bucket = self.token_buckets.get(key, {})
            unblock_time = bucket.get('block_until', float('inf'))
            
            if unblock_time < earliest_unblock:
                earliest_unblock = unblock_time
                fallback_idx = i
        
        # 대기
        wait_time = max(0, earliest_unblock - time.time())
        if wait_time > 0:
            logger.warning(f"모든 크레덴셜 차단. {wait_time:.1f}초 대기...")
            time.sleep(wait_time)
        
        return fallback_idx, self.credentials_list[fallback_idx]
    
    def acquire_token(self, credential_idx: int = None, priority: int = 5) -> bool:
        """
        토큰 획득 (우선순위 기반)
        
        Args:
            credential_idx: 특정 크레덴셜 지정
            priority: 요청 우선순위 (1=최고, 10=최저)
            
        Returns:
            토큰 획득 성공 여부
        """
        if credential_idx is None:
            credential_idx, _ = self.get_optimal_credential()
        
        if credential_idx < 0 or credential_idx >= len(self.credentials_list):
            return False
        
        cred = self.credentials_list[credential_idx]
        key = f"{cred.get('APPKEY', '')}_{credential_idx}"
        bucket = self.token_buckets[key]
        
        with self.credential_locks[credential_idx]:
            # 토큰 리필
            self._refill_tokens(bucket)
            
            # 토큰 확인
            if bucket['tokens'] >= 1:
                bucket['tokens'] -= 1
                self.total_requests += 1
                
                # 요청 이력 기록
                self.request_history[key].append(time.time())
                if len(self.request_history[key]) > 100:
                    self.request_history[key].popleft()
                
                return True
            
            # 토큰 부족 - 대기 또는 다른 크레덴셜 시도
            if self.enable_rotation:
                # 다른 크레덴셜 시도
                for _ in range(len(self.credentials_list) - 1):
                    alt_idx, _ = self.get_optimal_credential()
                    if alt_idx != credential_idx:
                        return self.acquire_token(alt_idx, priority)
            
            # 대기
            wait_time = self._calculate_wait_time(bucket)
            if wait_time > 0:
                logger.debug(f"토큰 대기: {wait_time:.3f}초")
                time.sleep(wait_time)
                return self.acquire_token(credential_idx, priority)
            
            return False
    
    def _refill_tokens(self, bucket: Dict[str, Any]):
        """토큰 버킷 리필"""
        now = time.time()
        time_passed = now - bucket['last_refill']
        
        # 토큰 리필 계산
        tokens_to_add = time_passed * self.base_rate_limit
        bucket['tokens'] = min(
            bucket['max_tokens'],
            bucket['tokens'] + tokens_to_add
        )
        bucket['last_refill'] = now
    
    def _calculate_wait_time(self, bucket: Dict[str, Any]) -> float:
        """필요한 대기 시간 계산"""
        tokens_needed = 1 - bucket['tokens']
        if tokens_needed <= 0:
            return 0
        
        # 지능형 백오프
        base_wait = tokens_needed / self.base_rate_limit
        
        # 연속 에러에 따른 추가 대기
        error_penalty = bucket.get('consecutive_errors', 0) * 0.5
        
        # 랜덤 지터 추가 (충돌 방지)
        jitter = random.uniform(0, 0.1)
        
        return base_wait + error_penalty + jitter
    
    def handle_429_error(self, credential_idx: int):
        """429 (Too Many Requests) 에러 처리"""
        self.total_429_errors += 1
        
        cred = self.credentials_list[credential_idx]
        key = f"{cred.get('APPKEY', '')}_{credential_idx}"
        bucket = self.token_buckets[key]
        
        with self.credential_locks[credential_idx]:
            bucket['consecutive_errors'] += 1
            bucket['tokens'] = 0  # 토큰 고갈
            
            # 지수 백오프
            backoff_time = min(300, self.recovery_time * (2 ** bucket['consecutive_errors']))
            bucket['is_blocked'] = True
            bucket['block_until'] = time.time() + backoff_time
            
            logger.warning(f"429 에러 - 크레덴셜 {credential_idx} 차단 ({backoff_time:.1f}초)")
            
            # 다른 크레덴셜로 자동 전환
            if self.enable_rotation:
                self.current_credential_idx = (credential_idx + 1) % len(self.credentials_list)
    
    def reset_error_count(self, credential_idx: int):
        """에러 카운트 리셋 (성공 시 호출)"""
        cred = self.credentials_list[credential_idx]
        key = f"{cred.get('APPKEY', '')}_{credential_idx}"
        bucket = self.token_buckets[key]
        
        with self.credential_locks[credential_idx]:
            bucket['consecutive_errors'] = 0
            if bucket.get('is_blocked') and not bucket.get('block_until'):
                bucket['is_blocked'] = False
    
    def get_stats(self) -> Dict[str, Any]:
        """통계 정보 반환"""
        active_credentials = sum(
            1 for bucket in self.token_buckets.values()
            if not bucket.get('is_blocked')
        )
        
        total_tokens = sum(
            bucket.get('tokens', 0)
            for bucket in self.token_buckets.values()
        )
        
        avg_error_rate = (
            self.total_429_errors / self.total_requests * 100
            if self.total_requests > 0 else 0
        )
        
        return {
            'total_requests': self.total_requests,
            'total_429_errors': self.total_429_errors,
            'total_rotations': self.total_rotations,
            'active_credentials': active_credentials,
            'total_credentials': len(self.credentials_list),
            'total_available_tokens': total_tokens,
            'avg_error_rate': f"{avg_error_rate:.2f}%",
            'rotation_enabled': self.enable_rotation
        }
    
    def optimize_request_pattern(self, requests_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        요청 패턴 최적화 (배치 처리)
        
        Args:
            requests_batch: 요청 배치 리스트
            
        Returns:
            최적화된 요청 순서
        """
        # 우선순위별 정렬
        sorted_requests = sorted(
            requests_batch,
            key=lambda x: (x.get('priority', 5), random.random())
        )
        
        # 시간 분산
        optimized = []
        for i, req in enumerate(sorted_requests):
            # 크레덴셜 할당
            cred_idx, cred = self.get_optimal_credential()
            req['credential_idx'] = cred_idx
            req['credential'] = cred
            
            # 지연 시간 계산
            if i > 0:
                # 요청 간 최소 간격
                min_interval = 1.0 / self.base_rate_limit
                req['delay'] = min_interval * (1 + random.uniform(0, 0.2))
            else:
                req['delay'] = 0
            
            optimized.append(req)
        
        return optimized
    
    def adaptive_rate_adjustment(self, success_rate: float):
        """
        성공률 기반 적응형 레이트 조정
        
        Args:
            success_rate: 최근 성공률 (0-1)
        """
        if success_rate > 0.95:
            # 성공률 높음 - 레이트 증가
            self.base_rate_limit = min(30, int(self.base_rate_limit * 1.1))
            self.burst_capacity = min(100, int(self.burst_capacity * 1.1))
            logger.info(f"레이트 증가: {self.base_rate_limit}/초")
            
        elif success_rate < 0.8:
            # 성공률 낮음 - 레이트 감소
            self.base_rate_limit = max(5, int(self.base_rate_limit * 0.9))
            self.burst_capacity = max(20, int(self.burst_capacity * 0.9))
            logger.info(f"레이트 감소: {self.base_rate_limit}/초")
    
    def start_queue_processor(self):
        """백그라운드 큐 프로세서 시작"""
        if self.queue_processor_thread and self.queue_processor_thread.is_alive():
            return
        
        self.stop_queue_processor.clear()
        self.queue_processor_thread = threading.Thread(
            target=self._process_request_queue,
            daemon=True
        )
        self.queue_processor_thread.start()
    
    def _process_request_queue(self):
        """요청 큐 처리 (백그라운드)"""
        while not self.stop_queue_processor.is_set():
            try:
                # 우선순위 큐에서 요청 가져오기
                priority, timestamp, request = self.request_queue.get(timeout=1)
                
                # 토큰 획득 대기
                if self.acquire_token(priority=priority):
                    # 요청 처리 콜백 실행
                    if 'callback' in request:
                        request['callback'](request)
                    
                    # 성공 카운트
                    if 'credential_idx' in request:
                        self.reset_error_count(request['credential_idx'])
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"큐 처리 오류: {e}")
    
    def stop_queue_processor(self):
        """백그라운드 큐 프로세서 중지"""
        self.stop_queue_processor.set()
        if self.queue_processor_thread:
            self.queue_processor_thread.join(timeout=5)
    
    def add_request_to_queue(self, request: Dict[str, Any], priority: int = 5):
        """요청을 큐에 추가"""
        timestamp = time.time()
        self.request_queue.put((priority, timestamp, request))


class SmartRetryStrategy:
    """지능형 재시도 전략"""
    
    def __init__(self):
        self.retry_patterns = {
            429: {'base_delay': 60, 'multiplier': 2, 'max_delay': 300},
            503: {'base_delay': 5, 'multiplier': 1.5, 'max_delay': 60},
            'default': {'base_delay': 1, 'multiplier': 1.5, 'max_delay': 30}
        }
        
    def calculate_retry_delay(
        self, 
        error_code: int, 
        attempt: int,
        response_headers: Dict[str, str] = None
    ) -> float:
        """
        재시도 지연 시간 계산
        
        Args:
            error_code: HTTP 에러 코드
            attempt: 재시도 횟수
            response_headers: 응답 헤더 (Retry-After 등)
            
        Returns:
            대기 시간 (초)
        """
        # Retry-After 헤더 확인
        if response_headers and 'Retry-After' in response_headers:
            try:
                return float(response_headers['Retry-After'])
            except (ValueError, TypeError):
                pass
        
        # 에러 코드별 패턴
        pattern = self.retry_patterns.get(
            error_code,
            self.retry_patterns['default']
        )
        
        # 지수 백오프 계산
        delay = pattern['base_delay'] * (pattern['multiplier'] ** attempt)
        delay = min(delay, pattern['max_delay'])
        
        # 랜덤 지터 추가
        jitter = random.uniform(0, delay * 0.1)
        
        return delay + jitter