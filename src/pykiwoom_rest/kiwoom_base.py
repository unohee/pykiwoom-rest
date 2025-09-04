"""
Kiwoom Securities REST API Base Client
키움증권 REST API 특화 기능 제공
작성일: 2025-01-27
"""

import os
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from .base_api import BaseAPIClient, APIError
from .response_model import APIResponse


class KiwoomAPIError(APIError):
    """키움증권 API 전용 예외 클래스"""
    
    def __init__(self, message: str, error_code: str = None, error_msg: str = None):
        super().__init__(message)
        self.error_code = error_code
        self.error_msg = error_msg


class KiwoomAPIBase(BaseAPIClient):
    """
    키움증권 REST API 기본 클래스
    OAuth 인증, 해시키 생성, TR 코드 매핑 등 키움 특화 기능 제공
    """
    
    # 키움증권 REST API URL
    BASE_URL = "https://api.kiwoom.com"  # 실전투자
    MOCK_BASE_URL = "https://mockapi.kiwoom.com"  # 모의투자
    
    # API 엔드포인트 매핑
    ENDPOINTS = {
        'auth_token': '/oauth2/token',
        'auth_revoke': '/oauth2/revoke',
        'hashkey': '/uapi/hashkey',
        'stock_info': '/api/dostk/stkinfo',
        'market_condition': '/api/dostk/mrkcond',
        'chart': '/api/dostk/chart',
        'foreign_institution': '/api/dostk/frgnistt',
        'ranking': '/api/dostk/rkinfo',
        'account': '/api/dostk/acnt',
        'order': '/api/dostk/ordr',
        'sector': '/api/dostk/sect',
        'etf': '/api/dostk/etf',
        'elw': '/api/dostk/elw',
        'short_sale': '/api/dostk/shsa',
        'securities_lending': '/api/dostk/slb',
        'theme': '/api/dostk/thme',
        'credit_order': '/api/dostk/crdordr',
        'websocket': '/api/dostk/websocket'
    }
    
    def __init__(
        self,
        account_no: str = None,
        appkey: str = None,
        appsecret: str = None,
        env_path: str = None,
        use_mock: bool = False,
        **kwargs
    ):
        """
        초기화
        
        Args:
            account_no: 계좌번호
            appkey: 앱키
            appsecret: 앱시크릿
            env_path: .env 파일 경로
            use_mock: 모의투자 API 사용 여부
            **kwargs: BaseAPIClient 추가 인자
        """
        base_url = self.BASE_URL
        if use_mock:
            base_url = self.MOCK_BASE_URL
            
        # 키움 API는 초당 20회 제한
        kwargs.setdefault('rate_limit', 20)
        
        super().__init__(base_url=base_url, **kwargs)
        
        # 환경변수 로드
        self._load_env_file(env_path)
        
        # 인증 정보 설정
        self._setup_credentials(account_no, appkey, appsecret)
        
        # 토큰 상태 초기화
        self.access_token = None
        self.token_expires = None
        
    def _load_env_file(self, env_path: str = None) -> None:
        """환경 파일 로드"""
        if env_path is None:
            # 프로젝트 루트에서 .env 파일 찾기
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            env_path = os.path.join(project_root, '.env')
            
        if os.path.exists(env_path):
            try:
                import dotenv
                dotenv.load_dotenv(env_path)
            except ImportError:
                # dotenv 없으면 수동 파싱
                self._manual_load_env(env_path)
                
    def _manual_load_env(self, env_path: str) -> None:
        """dotenv 라이브러리 없이 수동으로 환경변수 로드"""
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        except (FileNotFoundError, PermissionError):
            # .env 파일 없음 - 환경변수에서 직접 로드 진행
            # 의도적으로 예외 무시 (선택적 기능)
            pass
            
    def _setup_credentials(self, account_no: str = None, appkey: str = None, appsecret: str = None) -> None:
        """인증 정보 설정"""
        self.account_no = account_no or os.getenv('ACC_NO') or os.getenv('ACCOUNT_NO')
        self.appkey = appkey or os.getenv('APPKEY') or os.getenv('KIWOOM_APPKEY')
        self.appsecret = appsecret or os.getenv('APPSECRET') or os.getenv('KIWOOM_SECRETKEY') or os.getenv('KIWOOM_APPSECRET')
        
        if not all([self.account_no, self.appkey, self.appsecret]):
            raise ValueError("계좌번호, APPKEY, SECRETKEY가 필요합니다. .env 파일을 확인하세요.")
            
    def _prepare_headers(self, headers: Dict[str, str] = None) -> Dict[str, str]:
        """키움 API 요청 헤더 준비"""
        base_headers = {
            'Content-Type': 'application/json; charset=UTF-8',
            'Accept': 'application/json'
        }
        
        # 토큰이 있으면 Authorization 헤더 추가
        if self.access_token:
            base_headers['Authorization'] = f'Bearer {self.access_token}'
            
        # 커스텀 헤더 병합
        if headers:
            base_headers.update(headers)
            
        return base_headers
        
    def _process_response(self, response) -> APIResponse:
        """키움 API 응답 처리 - APIResponse 객체로 래핑"""
        start_time = getattr(self, '_request_start_time', time.time())
        processing_time = time.time() - start_time
        
        # 요청 정보 추출
        tr_code = getattr(self, '_current_tr_code', None)
        endpoint = getattr(self, '_current_endpoint', None)
        
        try:
            data = response.json()
            
            # 키움 API 에러 체크
            if isinstance(data, dict):
                error_code = data.get('rt_cd')
                if error_code and error_code != '0':
                    error_msg = data.get('msg1', '알 수 없는 오류')
                    return APIResponse.create_error(
                        error_message=f"키움 API 오류: {error_msg}",
                        error_code=error_code,
                        error_details={'raw_response': data},
                        tr_code=tr_code,
                        endpoint=endpoint,
                        processing_time=processing_time
                    )
            
            # 성공 응답
            return APIResponse.create_success(
                data=data,
                tr_code=tr_code,
                endpoint=endpoint,
                processing_time=processing_time
            )
            
        except json.JSONDecodeError:
            # JSON이 아닌 응답 - 에러로 처리
            return APIResponse.create_error(
                error_message="Invalid JSON response",
                error_code="INVALID_JSON",
                error_details={'raw_response': response.text},
                tr_code=tr_code,
                endpoint=endpoint,
                processing_time=processing_time
            )
            
    def _get_access_token(self, force_refresh: bool = False) -> str:
        """OAuth2 액세스 토큰 발급/갱신"""
        # 토큰이 유효하고 강제 갱신이 아니면 기존 토큰 사용
        if not force_refresh and self.access_token and self.token_expires:
            if datetime.now() < self.token_expires - timedelta(minutes=5):
                return self.access_token
                
        # 토큰 발급 요청
        token_data = {
            'grant_type': 'client_credentials',
            'appkey': self.appkey,
            'secretkey': self.appsecret  # 키움은 secretkey 사용
        }
        
        try:
            response = self.request(
                method='POST',
                endpoint='/oauth2/token',  # 키움증권 토큰 엔드포인트
                json_data=token_data,
                use_rate_limit=False  # 인증 요청은 rate limit 제외
            )
            
            # 키움증권은 'token' 키 사용 (access_token 아님)
            if response.get('token'):
                self.access_token = response['token']
                # 토큰 만료 시간 설정 (24시간 - 5분 여유)
                self.token_expires = datetime.now() + timedelta(hours=23, minutes=55)
                return self.access_token
            else:
                raise KiwoomAPIError(
                    "토큰 발급 실패",
                    error_code=response.get('return_code'),
                    error_msg=response.get('return_msg')
                )
                
        except Exception as e:
            self.logger.error(f"토큰 발급 중 오류: {e}")
            raise
            
    def _get_hashkey(self, data: Dict[str, Any]) -> str:
        """
        POST 요청용 해시키 생성
        키움 API의 일부 POST 요청에 필요
        """
        try:
            # 토큰 확보
            token = self._get_access_token()
            
            # 해시키 요청
            hash_response = self.request(
                method='POST',
                endpoint='/uapi/hashkey',
                json_data=data,
                headers={'Authorization': f'Bearer {token}'},
                use_rate_limit=False
            )
            
            return hash_response.get('HASH')
            
        except Exception as e:
            self.logger.error(f"해시키 생성 중 오류: {e}")
            raise
            
    def make_tr_request(
        self,
        tr_code: str,
        endpoint: str,
        data: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
        method: str = 'POST'
    ) -> APIResponse:
        """
        TR 코드를 사용한 API 요청
        
        Args:
            tr_code: 키움 TR 코드
            endpoint: API 엔드포인트 키
            data: POST 요청 데이터
            params: GET 요청 파라미터
            method: HTTP 메서드
            
        Returns:
            APIResponse 객체
        """
        # 요청 컨텍스트 설정 (응답 처리에서 사용)
        self._current_tr_code = tr_code
        self._current_endpoint = endpoint
        self._request_start_time = time.time()
        
        try:
            # 토큰 확보
            token = self._get_access_token()
            
            # 엔드포인트 URL 가져오기
            endpoint_url = self.ENDPOINTS.get(endpoint)
            if not endpoint_url:
                raise ValueError(f"알 수 없는 엔드포인트: {endpoint}")
                
            # 헤더 준비
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json; charset=UTF-8',
                'tr_id': tr_code,
                'tr_cont': '',  # 연속조회 여부 (공백 제거)
                'custtype': 'P',  # 고객타입 (P: 개인)
                'custnum': self.account_no[:8] if self.account_no else ''  # 고객번호
            }
            
            # POST 요청의 경우 해시키 추가
            if method.upper() == 'POST' and data:
                try:
                    hashkey = self._get_hashkey(data)
                    if hashkey:
                        headers['hashkey'] = hashkey
                except Exception as e:
                    self.logger.warning(f"해시키 생성 실패: {e}")
                    
            # API 요청 실행
            return self.request(
                method=method,
                endpoint=endpoint_url,
                headers=headers,
                params=params,
                json_data=data if method.upper() == 'POST' else None
            )
        
        finally:
            # 컨텍스트 정리
            self._current_tr_code = None
            self._current_endpoint = None
            self._request_start_time = None
        
    def health_check(self) -> Dict[str, Any]:
        """
        API 연결 상태 확인
        간단한 종목 조회로 API 상태 체크
        """
        try:
            # 삼성전자 기본 정보 조회로 연결 테스트
            test_params = {
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": "005930"
            }
            
            result = self.make_tr_request(
                tr_code='ka10001',  # 주식기본정보요청
                endpoint='stock_info',
                params=test_params,
                method='GET'
            )
            
            if result and result.get('rt_cd') == '0':
                return {
                    'status': 'healthy',
                    'connected': True,
                    'api_responsive': True,
                    'test_response': result.get('msg1', 'Success'),
                    'token_valid': bool(self.access_token),
                    'stats': self.get_stats()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'connected': False,
                    'api_responsive': False,
                    'error': result.get('msg1') if result else 'No response',
                    'response_code': result.get('rt_cd') if result else None
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'connected': False,
                'error': str(e),
                'exception_type': type(e).__name__
            }
            
    def convert_stock_code_param(self, stock_code: str, legacy_format: bool = False) -> Dict[str, str]:
        """종목코드 파라미터 변환 헬퍼"""
        if legacy_format:
            return {"FID_INPUT_ISCD": stock_code}
        else:
            return {"stk_cd": stock_code}
            
    def to_dataframe(self, response, output_key: str = None, numeric_fields: list = None):
        """
        API 응답을 DataFrame으로 변환
        
        Args:
            response: APIResponse 객체 또는 dict
            output_key: 데이터 추출할 키
            numeric_fields: 숫자형으로 변환할 필드 목록
            
        Returns:
            DataFrame 또는 None
        """
        try:
            import pandas as pd
        except ImportError:
            self.logger.warning("pandas가 설치되지 않음. DataFrame 변환 불가")
            return None
        
        # APIResponse 객체 처리
        if isinstance(response, APIResponse):
            if not response.success:
                return None
            response_data = response.data
        elif isinstance(response, dict):
            response_data = response
        else:
            return None
            
        # 유효성 검증
        if not response_data:
            return None
            
        # 키움 API 성공 응답 체크 (rt_cd == '0')
        if response_data.get('rt_cd') != '0':
            return None
            
        # 데이터 추출
        data = None
        if output_key:
            data = response_data.get(output_key)
        else:
            # 자동 감지
            for key in ['output', 'output1', 'output2']:
                if key in response_data:
                    data = response_data[key]
                    break
                    
        if not data:
            return None
            
        # DataFrame 생성
        try:
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                return None
                
            # 숫자형 필드 변환
            if numeric_fields:
                for field in numeric_fields:
                    if field in df.columns:
                        try:
                            df[field] = pd.to_numeric(df[field], errors='coerce')
                        except (ValueError, TypeError):
                            continue
                            
            return df
            
        except Exception as e:
            self.logger.error(f"DataFrame 변환 중 오류: {e}")
            return None