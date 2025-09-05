"""
PyKiwoom-Rest v2: Kiwoom증권 REST API Python Wrapper (Unified Architecture)
작성일: 2025-01-21
"""

import os
import requests
from datetime import datetime, timedelta


class KiwoomRestBase:
    """Kiwoom증권 REST API 통합 베이스 클래스"""
    
    # 키움증권 REST API 공식 URL
    BASE_URL = "https://api.kiwoom.com"  # 실전투자
    # BASE_URL = "https://mockapi.kiwoom.com"  # 모의투자
    
    # API 엔드포인트 매핑
    ENDPOINTS = {
        # OAuth 인증
        'auth_token': '/oauth2/token',  # 키움증권 토큰 발급
        'auth_revoke': '/oauth2/revoke',
        'hashkey': '/uapi/hashkey',
        
        # 종목정보 (/api/dostk/stkinfo)
        'stock_info': '/api/dostk/stkinfo',
        
        # 시세 (/api/dostk/mrkcond)
        'market_condition': '/api/dostk/mrkcond',
        
        # 차트 (/api/dostk/chart)
        'chart': '/api/dostk/chart',
        
        # 기관/외국인 (/api/dostk/frgnistt)
        'foreign_institution': '/api/dostk/frgnistt',
        
        # 순위정보 (/api/dostk/rkinfo)
        'ranking': '/api/dostk/rkinfo',
        
        # 계좌 (/api/dostk/acnt)
        'account': '/api/dostk/acnt',
        
        # 주문 (/api/dostk/ordr)
        'order': '/api/dostk/ordr',
        
        # 업종 (/api/dostk/sect)
        'sector': '/api/dostk/sect',
        
        # ETF (/api/dostk/etf)
        'etf': '/api/dostk/etf',
        
        # ELW (/api/dostk/elw)
        'elw': '/api/dostk/elw',
        
        # 공매도 (/api/dostk/shsa)
        'short_sale': '/api/dostk/shsa',
        
        # 대차거래 (/api/dostk/slb)
        'securities_lending': '/api/dostk/slb',
        
        # 테마 (/api/dostk/thme)
        'theme': '/api/dostk/thme',
        
        # 신용주문 (/api/dostk/crdordr)
        'credit_order': '/api/dostk/crdordr',
        
        # WebSocket (/api/dostk/websocket)
        'websocket': '/api/dostk/websocket'
    }
    
    # TR 코드 매핑
    TR_CODES = {
        # OAuth 인증
        'auth_token': 'au10001',
        'auth_revoke': 'au10002',
        
        # 종목정보
        'stock_basic_info': 'ka10001',
        'stock_member_info': 'ka10002',
        'execution_info': 'ka10003',
        'credit_trend': 'ka10013',
        'daily_trading_detail': 'ka10015',
        'new_high_low': 'ka10016',
        'upper_lower_limit': 'ka10017',
        'high_low_approach': 'ka10018',
        'price_fluctuation': 'ka10019',
        'volume_update': 'ka10024',
        'supply_concentration': 'ka10025',
        'high_low_per': 'ka10026',
        'open_price_rate': 'ka10028',
        'member_supply_analysis': 'ka10043',
        'new_previous_execution': 'ka10055',
        'investor_daily_trading': 'ka10058',
        'investor_institution_by_stock': 'ka10059',
        'investor_institution_total': 'ka10061',
        'current_previous_execution': 'ka10084',
        'watchlist_info': 'ka10095',
        'stock_info_list': 'ka10099',
        'stock_info_inquiry': 'ka10100',
        'sector_code_list': 'ka10101',
        'member_company_list': 'ka10102',
        'daily_trading_journal': 'ka10170',
        
        # 시세
        'stock_quote': 'ka10004',
        'stock_daily_weekly_monthly': 'ka10005',
        'stock_minute': 'ka10006',
        'market_composition_info': 'ka10007',
        'new_stock_rights_market': 'ka10011',
        'daily_institution_trading': 'ka10044',
        'institution_trading_trend': 'ka10045',
        'execution_strength_hourly': 'ka10046',
        'execution_strength_daily': 'ka10047',
        'investor_trading_intraday': 'ka10063',
        'investor_trading_after_close': 'ka10066',
        'member_trading_trend': 'ka10078',
        'daily_stock_price': 'ka10086',
        'overtime_single_price': 'ka10087',
        
        # 차트
        'tick_chart': 'ka10079',
        'minute_chart': 'ka10080',
        'daily_chart': 'ka10081',
        'weekly_chart': 'ka10082',
        'monthly_chart': 'ka10083',
        'yearly_chart': 'ka10094',
        'investor_institution_chart': 'ka10060',
        'investor_trading_chart': 'ka10064',
        
        # 기관/외국인
        'foreign_trading_by_stock': 'ka10008',
        'institution_inquiry': 'ka10009',
        'institution_foreign_continuous': 'ka10131',
        
        # 순위정보
        'quote_volume_top': 'ka10020',
        'quote_volume_surge': 'ka10021',
        'volume_rate_surge': 'ka10022',
        'trading_volume_surge': 'ka10023',
        'previous_day_rate_top': 'ka10027',
        'expected_rate_top': 'ka10029',
        'daily_volume_top': 'ka10030',
        'previous_volume_top': 'ka10031',
        'trading_amount_top': 'ka10032',
        'credit_ratio_top': 'ka10033',
        'foreign_period_trading_top': 'ka10034',
        'foreign_continuous_trading_top': 'ka10035',
        'foreign_limit_exhaustion_top': 'ka10036',
        'foreign_window_trading_top': 'ka10037',
        'stock_securities_ranking': 'ka10038',
        'securities_trading_top': 'ka10039',
        'daily_major_trader': 'ka10040',
        'net_buy_trader_ranking': 'ka10042',
        'daily_top_departure': 'ka10053',
        'same_net_trading_ranking': 'ka10062',
        'investor_trading_top': 'ka10065',
        'overtime_rate_ranking': 'ka10098',
        
        # 업종
        'sector_program': 'ka10010',
        'sector_investor_net_buy': 'ka10051',
        'sector_current_price': 'ka20001',
        'sector_stock_price': 'ka20002',
        'all_sector_index': 'ka20003',
        'sector_tick_chart': 'ka20004',
        'sector_minute_chart': 'ka20005',
        'sector_daily_chart': 'ka20006',
        'sector_weekly_chart': 'ka20007',
        'sector_monthly_chart': 'ka20008',
        'sector_current_price_daily': 'ka20009',
        'sector_yearly_chart': 'ka20019',
        
        # ETF
        'etf_return': 'ka40001',
        'etf_stock_info': 'ka40002',
        'etf_daily_trend': 'ka40003',
        'etf_all_market': 'ka40004',
        'etf_hourly_trend': 'ka40006',
        'etf_hourly_execution': 'ka40007',
        'etf_daily_execution': 'ka40008',
        'etf_hourly_execution_2': 'ka40009',
        'etf_hourly_trend_2': 'ka40010',
        
        # ELW
        'elw_daily_sensitivity': 'ka10048',
        'elw_sensitivity': 'ka10050',
        'elw_price_fluctuation': 'ka30001',
        'elw_member_net_trading_top': 'ka30002',
        'elw_lp_holding_daily': 'ka30003',
        'elw_deviation_rate': 'ka30004',
        'elw_condition_search': 'ka30005',
        'elw_rate_ranking': 'ka30009',
        'elw_volume_ranking': 'ka30010',
        'elw_approach_rate': 'ka30011',
        'elw_stock_detail_info': 'ka30012',
        
        # 공매도
        'short_sale_trend': 'ka10014',
        
        # 대차거래
        'securities_lending_trend': 'ka10068',
        'securities_lending_top10': 'ka10069',
        'securities_lending_by_stock': 'ka20068',
        'securities_lending_detail': 'ka90012',
        
        # 테마
        'theme_group': 'ka90001',
        'theme_stocks': 'ka90002',
        
        # 프로그램매매
        'program_net_buy_top50': 'ka90003',
        'program_trading_by_stock': 'ka90004',
        'program_trading_hourly': 'ka90005',
        'program_profit_balance': 'ka90006',
        'program_cumulative_trend': 'ka90007',
        'program_trading_by_stock_hourly': 'ka90008',
        'foreign_institution_trading_top': 'ka90009',
        'program_trading_daily': 'ka90010',
        'program_trading_by_stock_daily': 'ka90013',
        
        # 계좌
        'daily_stock_realized_pl_date': 'ka10072',
        'daily_stock_realized_pl_period': 'ka10073',
        'daily_realized_pl': 'ka10074',
        'outstanding_orders': 'ka10075',
        'executions': 'ka10076',
        'daily_realized_pl_detail': 'ka10077',
        'account_return_rate': 'ka10085',
        'outstanding_split_order_detail': 'ka10088',
        'deposit_detail_status': 'kt00001',
        'daily_estimated_deposit_status': 'kt00002',
        'estimated_asset_inquiry': 'kt00003',
        'account_evaluation_status': 'kt00004',
        'execution_balance': 'kt00005',
        'account_order_execution_detail': 'kt00007',
        'account_next_day_settlement': 'kt00008',
        'account_order_execution_status': 'kt00009',
        'order_withdrawal_available_amount': 'kt00010',
        'margin_rate_order_quantity': 'kt00011',
        'credit_margin_rate_order_quantity': 'kt00012',
        'margin_detail_inquiry': 'kt00013',
        'consignment_comprehensive_trading': 'kt00015',
        'daily_account_return_detail': 'kt00016',
        'account_daily_status': 'kt00017',
        'account_evaluation_balance': 'kt00018',
        
        # 주문
        'stock_buy_order': 'kt10000',
        'stock_sell_order': 'kt10001',
        'stock_modify_order': 'kt10002',
        'stock_cancel_order': 'kt10003',
        'credit_buy_order': 'kt10006',
        'credit_sell_order': 'kt10007',
        'credit_modify_order': 'kt10008',
        'credit_cancel_order': 'kt10009',
        'credit_available_stocks': 'kt20016',
        'credit_available_inquiry': 'kt20017',
        
        # 조건검색
        'condition_search_list': 'ka10171',
        'condition_search_general': 'ka10172',
        'condition_search_realtime': 'ka10173',
        'condition_search_realtime_cancel': 'ka10174',
        
        # 실시간 WebSocket
        'ws_order_execution': '00',
        'ws_balance': '04',
        'ws_stock_price': '0A',
        'ws_stock_execution': '0B',
        'ws_stock_priority_quote': '0C',
        'ws_stock_quote_volume': '0D',
        'ws_stock_overtime_quote': '0E',
        'ws_stock_daily_trader': '0F',
        'ws_etf_nav': '0G',
        'ws_stock_expected_execution': '0H',
        'ws_sector_index': '0J',
        'ws_sector_fluctuation': '0U',
        'ws_stock_info': '0g',
        'ws_elw_theoretical_price': '0m',
        'ws_market_start_time': '0s',
        'ws_elw_indicator': '0u',
        'ws_stock_program_trading': '0w',
        'ws_vi_trigger_release': '1h'
    }

    def __init__(self, env_path: str = None, account_no: str = None, appkey: str = None, appsecret: str = None):
        """
        초기화
        Args:
            env_path: .env 파일 경로 (기본값: 프로젝트 루트의 .env)
            account_no: 계좌번호
            appkey: 앱키
            appsecret: 앱시크릿
        """
        env_path = self._find_env_path(env_path)
        self._load_env_file(env_path)
        self._setup_credentials(account_no, appkey, appsecret)
        self._initialize_token_state()
    
    def _find_env_path(self, env_path: str = None) -> str:
        """환경파일 경로 찾기"""
        if env_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            env_path = os.path.join(project_root, '.env')
        return env_path
    
    def _load_env_file(self, env_path: str) -> None:
        """환경파일 로드"""
        if os.path.exists(env_path):
            try:
                import dotenv
                dotenv.load_dotenv(env_path)
            except ImportError:
                # dotenv가 없으면 수동으로 파싱
                self._manual_load_env(env_path)
    
    def _manual_load_env(self, env_path: str) -> None:
        """dotenv 없이 수동으로 환경변수 로드"""
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
        except (FileNotFoundError, PermissionError) as e:
            # .env 파일 없음: 환경변수에서 직접 로드 진행
            # 로그 필요시: print(f"Warning: .env file not accessible: {e}")
            return
    
    def _setup_credentials(self, account_no: str = None, appkey: str = None, appsecret: str = None) -> None:
        """인증정보 설정"""
        self.account_no = account_no or os.getenv('ACC_NO') or os.getenv('ACCOUNT_NO')
        self.appkey = appkey or os.getenv('APPKEY') or os.getenv('KIWOOM_APPKEY')
        self.secretkey = appsecret or os.getenv('APPSECRET') or os.getenv('KIWOOM_SECRETKEY') or os.getenv('KIWOOM_APPSECRET')
        
        if not all([self.account_no, self.appkey, self.secretkey]):
            raise ValueError("계좌번호, APPKEY, SECRETKEY가 필요합니다. .env 파일을 확인하세요.")
    
    def _initialize_token_state(self) -> None:
        """토큰 상태 초기화"""
        self.access_token = None
        self.token_expires = None
    
    def _convert_stock_code_param(self, stock_code: str, legacy_format: bool = False) -> dict:
        """
        종목코드 매개변수 변환 헬퍼
        
        Args:
            stock_code: 종목코드
            legacy_format: True면 FID_INPUT_ISCD 형식, False면 stk_cd 형식
            
        Returns:
            변환된 매개변수 딕셔너리
        """
        if legacy_format:
            return {
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": stock_code
            }
        else:
            return {
                "stk_cd": stock_code
            }

    def _get_hashkey(self, data: dict) -> str:
        """해시키 생성 (키움증권은 해시키 미사용)"""
        # 키움증권 REST API는 해시키를 사용하지 않음
        return None
    
    def _get_access_token(self) -> str:
        """접근토큰 발급/갱신"""
        if self.access_token and self.token_expires and datetime.now() < self.token_expires:
            return self.access_token
            
        url = f"{self.BASE_URL}{self.ENDPOINTS['auth_token']}"
        headers = {'Content-Type': 'application/json;charset=UTF-8'}
        data = {
            "grant_type": "client_credentials",
            "appkey": self.appkey.strip(),
            "secretkey": self.secretkey.strip()
        }
        
        response = requests.post(url, headers=headers, json=data)  # json으로 전송
        
        try:
            result = response.json()
        except requests.exceptions.JSONDecodeError as e:
            raise requests.exceptions.JSONDecodeError(f"토큰 발급 실패: HTTP {response.status_code}, 응답이 JSON이 아님: {response.text[:200]}", e.doc, e.pos)
        
        # 키움증권은 return_code 0이 성공, token 필드 사용
        if response.status_code == 200 and result.get('return_code') == 0:
            self.access_token = result.get('token')  # 키움은 'token' 필드 사용
            # 만료시간 형식: YYYYMMDDHHMMSS
            expires_dt_str = result.get('expires_dt', '')
            if expires_dt_str:
                try:
                    expires_dt = datetime.strptime(expires_dt_str, '%Y%m%d%H%M%S')
                    self.token_expires = expires_dt - timedelta(minutes=1)  # 1분 여유
                except ValueError as e:
                    self.token_expires = datetime.now() + timedelta(hours=23)  # 기본 23시간
            else:
                self.token_expires = datetime.now() + timedelta(hours=23)
            return self.access_token
        else:
            error_detail = {
                'status_code': response.status_code,
                'response': result,
                'url': url,
                'request_data': {k: v for k, v in data.items() if k != 'secretkey'}  # 보안상 secret 제외
            }
            raise requests.exceptions.HTTPError(f"토큰 발급 실패: {error_detail}")
    
    def make_request(self, endpoint_key: str, tr_id_key: str, params: dict = None, data: dict = None, method: str = 'POST') -> dict:
        """
        통합 API 요청 메서드
        
        Args:
            endpoint_key: ENDPOINTS에서 사용할 키
            tr_id_key: TR_CODES에서 사용할 키
            params: GET 파라미터
            data: POST 데이터
            method: HTTP 메서드
            
        Returns:
            API 응답 딕셔너리
        """
        endpoint = self.ENDPOINTS.get(endpoint_key)
        tr_id = self.TR_CODES.get(tr_id_key)
        
        if not endpoint:
            raise ValueError(f"알 수 없는 엔드포인트 키: {endpoint_key}")
        if not tr_id:
            raise ValueError(f"알 수 없는 TR 코드 키: {tr_id_key}")
        
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'authorization': f'Bearer {self._get_access_token()}',  # 소문자
            'api-id': tr_id,  # 키움증권 공식 헤더명
        }
        
        # 연속조회 헤더 (필요시 추가)
        if params:
            if 'cont_yn' in params:
                headers['cont-yn'] = params.pop('cont_yn')
            if 'next_key' in params:
                headers['next-key'] = params.pop('next_key')
        
        # 키움증권은 hashkey 사용하지 않음 (이미 처리됨)
        
        # 키움증권은 대부분의 API가 POST 방식
        if method.upper() == 'GET' and not data:
            # 토큰 발급 등 일부 API만 GET
            response = requests.get(url, headers=headers, params=params)
        else:
            # 시세 조회 등 대부분은 POST with JSON body
            request_data = data if data else params
            response = requests.post(url, headers=headers, json=request_data)
        
        if response.status_code != 200:
            raise Exception(f"API 요청 실패: {response.status_code} - {response.text}")
        
        return response.json()
    
    def to_dataframe(self, response: dict, output_key: str = None, numeric_fields: list = None):
        """
        API 응답을 DataFrame으로 변환
        
        Args:
            response: API 응답
            output_key: 데이터 추출할 키 (자동 감지 가능)
            numeric_fields: 숫자형으로 변환할 필드 목록
            
        Returns:
            변환된 DataFrame
        """
        # pandas 임포트 (필요한 경우만)
        try:
            import pandas as pd
        except ImportError:
            return None
        
        # 유효성 검증
        if not self._is_valid_response(response):
            return None
        
        # 데이터 추출
        data = self._extract_data(response, output_key)
        if not data:
            return None
        
        # DataFrame 생성
        df = self._create_dataframe(data, pd)
        if df is None:
            return None
        
        # 숫자형 변환
        if numeric_fields and not df.empty:
            self._convert_numeric_fields(df, numeric_fields, pd)
        
        return df
    
    def _is_valid_response(self, response: dict) -> bool:
        """응답 유효성 검증 - 키움증권 방식"""
        if not response:
            return False
        # 키움증권은 return_code 또는 rt_cd 사용
        return (response.get("return_code") == 0 or 
                response.get("rt_cd") == "0" or
                "stk_cd" in response or  # 차트 데이터는 stk_cd 포함
                len(response) > 0)  # 응답이 있으면 일단 유효
    
    def _extract_data(self, response: dict, output_key: str = None):
        """응답에서 데이터 추출"""
        if output_key is None:
            for key in ["output", "output1", "output2"]:
                if key in response and response[key]:
                    output_key = key
                    break
        
        if output_key and output_key in response:
            return response[output_key]
        return None
    
    def _create_dataframe(self, data, pd):
        """DataFrame 생성"""
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            return pd.DataFrame([data])
        return None
    
    def _convert_numeric_fields(self, df, numeric_fields: list, pd):
        """숫자형 필드 변환"""
        for field in numeric_fields:
            if field in df.columns:
                try:
                    df[field] = pd.to_numeric(df[field], errors='coerce')
                except (ValueError, TypeError):
                    continue  # 원본 유지
    
    def verify_connection(self) -> dict:
        """
        실제 API 연결 상태 검증
        
        Returns:
            dict: 연결 상태와 상세 정보
        """
        try:
            # 토큰 발급 시도
            token = self._get_access_token()
            if not token:
                return {
                    'connected': False,
                    'error': 'Token acquisition failed',
                    'details': 'Unable to get access token'
                }
            
            # 간단한 API 호출로 실제 연결 테스트
            test_params = {
                "FID_COND_MRKT_DIV_CODE": "J",
                "FID_INPUT_ISCD": "005930"  # 삼성전자
            }
            
            result = self.make_request('stock_info', 'stock_basic_info', params=test_params)
            
            if result and result.get('rt_cd') == '0':
                return {
                    'connected': True,
                    'token_valid': True,
                    'api_responsive': True,
                    'test_response': result.get('msg1', 'Success')
                }
            else:
                return {
                    'connected': False,
                    'token_valid': True,
                    'api_responsive': False,
                    'error': result.get('msg1') if result else 'No response',
                    'response_code': result.get('rt_cd') if result else None
                }
                
        except (requests.RequestException, ConnectionError) as e:
            return {
                'connected': False,
                'error': str(e),
                'exception_type': type(e).__name__
            }
        except (KeyError, ValueError) as e:
            return {
                'connected': False,
                'error': f'데이터 파싱 오류: {str(e)}',
                'exception_type': type(e).__name__
            }


class KiwoomRest(KiwoomRestBase):
    """Kiwoom증권 REST API 래퍼 클래스 - 고레벨 메서드 제공"""
    
    # ========== 시세 관련 메서드 ==========
    
    def get_stock_price(self, stock_code: str) -> dict:
        """주식기본정보요청 (ka10001)"""
        params = self._convert_stock_code_param(stock_code, legacy_format=False)
        return self.make_request('stock_info', 'stock_basic_info', data=params)
    
    def get_stock_orderbook(self, stock_code: str) -> dict:
        """주식호가요청 (ka10004)"""
        params = {
            "stk_cd": stock_code
        }
        return self.make_request('market_condition', 'stock_quote', data=params)
    
    def get_execution_info(self, stock_code: str) -> dict:
        """체결정보요청 (ka10003)"""
        params = {
            "stk_cd": stock_code
        }
        return self.make_request('stock_info', 'execution_info', data=params)
    
    # ========== 차트 데이터 메서드 ==========
    
    def get_tick_chart(self, stock_code: str, count: int = 100) -> dict:
        """주식틱차트조회요청 (ka10079)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_INPUT_CNT_1": str(count)
        }
        return self.make_request('chart', 'tick_chart', params=params)
    
    def get_minute_chart(self, stock_code: str, interval: int = 1, start_date: str = None, end_date: str = None) -> dict:
        """주식분봉차트조회요청 (ka10080)"""
        params = {
            "stk_cd": stock_code,
            "tic_scope": str(interval),
            "upd_stkpc_tp": "1"
        }
        return self.make_request('chart', 'minute_chart', data=params)
    
    def get_daily_chart(self, stock_code: str, start_date: str = None, end_date: str = None) -> dict:
        """주식일봉차트조회요청 (ka10081)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
            
        params = {
            "stk_cd": stock_code,
            "base_dt": end_date,
            "upd_stkpc_tp": "1"
        }
        return self.make_request('chart', 'daily_chart', data=params)
    
    def get_weekly_chart(self, stock_code: str, start_date: str = None, end_date: str = None) -> dict:
        """주식주봉차트조회요청 (ka10082)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
            
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_PERIOD_DIV_CODE": "W",
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('chart', 'weekly_chart', params=params)
    
    def get_monthly_chart(self, stock_code: str, start_date: str = None, end_date: str = None) -> dict:
        """주식월봉차트조회요청 (ka10083)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365*3)).strftime("%Y%m%d")
            
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_PERIOD_DIV_CODE": "M",
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('chart', 'monthly_chart', params=params)
    
    def get_yearly_chart(self, stock_code: str, start_date: str = None, end_date: str = None) -> dict:
        """주식년봉차트조회요청 (ka10094)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365*10)).strftime("%Y%m%d")
            
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_PERIOD_DIV_CODE": "Y",
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('chart', 'yearly_chart', params=params)
    
    # ========== 기관/외국인 매매 메서드 ==========
    
    def get_foreign_trading(self, stock_code: str) -> dict:
        """주식외국인종목별매매동향 (ka10008)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_request('foreign_institution', 'foreign_trading_by_stock', params=params)
    
    def get_institutional_daily_trading(self, stock_code: str, start_date: str = None, end_date: str = None) -> dict:
        """일별기관매매종목요청 (ka10044)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
            
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('market_condition', 'daily_institution_trading', params=params)
    
    def get_institutional_trading_trend(self, stock_code: str, start_date: str = None, end_date: str = None) -> dict:
        """종목별기관매매추이요청 (ka10045)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
            
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('market_condition', 'institution_trading_trend', params=params)
    
    # ========== 순위 정보 메서드 ==========
    
    def get_volume_top(self, market: str = "ALL", count: int = 50) -> dict:
        """호가잔량상위요청 (ka10020)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_COND_SCR_DIV_CODE": "20",
            "FID_INPUT_ISCD": "0000",
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_INPUT_CNT_1": str(count),
            "FID_PRC_CLS_CODE": "1",
            "FID_INPUT_PRICE_1": "",
            "FID_INPUT_PRICE_2": "",
            "FID_VOL_CNT": "",
            "FID_INPUT_OPTION_1": "",
            "FID_INPUT_OPTION_2": ""
        }
        return self.make_request('ranking', 'quote_volume_top', params=params)
    
    def get_foreign_top_buy(self, period: str = "1") -> dict:
        """외인기간별매매상위요청 (ka10034)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_COND_SCR_DIV_CODE": "20",
            "FID_INPUT_ISCD": "0000",
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_INPUT_CNT_1": "50",
            "FID_PRC_CLS_CODE": "1",
            "FID_INPUT_PRICE_1": "",
            "FID_INPUT_PRICE_2": "",
            "FID_VOL_CNT": "",
            "FID_INPUT_OPTION_1": period,
            "FID_INPUT_OPTION_2": ""
        }
        return self.make_request('ranking', 'foreign_period_trading_top', params=params)
    
    # ========== 프로그램매매 메서드 ==========
    
    def get_program_top_buy(self) -> dict:
        """프로그램순매수상위50요청 (ka90003)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_COND_SCR_DIV_CODE": "20",
            "FID_INPUT_ISCD": "0000",
            "FID_RANK_SORT_CLS_CODE": "0",
            "FID_INPUT_CNT_1": "50"
        }
        return self.make_request('stock_info', 'program_net_buy_top50', params=params)
    
    def get_program_trading_daily(self, stock_code: str, start_date: str = None, end_date: str = None) -> dict:
        """종목일별프로그램매매추이요청 (ka90013)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
            
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('market_condition', 'program_trading_by_stock_daily', params=params)
    
    # ========== 기타 시세 정보 메서드 ==========
    
    def get_daily_price(self, stock_code: str) -> dict:
        """일별주가요청 (ka10086)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_PERIOD_DIV_CODE": "D"
        }
        return self.make_request('market_condition', 'daily_stock_price', params=params)
    
    def get_daily_trading_detail(self, stock_code: str) -> dict:
        """일별거래상세요청 (ka10015)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_PERIOD_DIV_CODE": "D"
        }
        return self.make_request('stock_info', 'daily_trading_detail', params=params)
    
    # ========== 페이지네이션 메서드 ==========
    
    def get_minute_chart_paginated(self, stock_code: str, interval: int = 1, 
                                 start_date: str = None, end_date: str = None, 
                                 max_records: int = 1000) -> list:
        """분봉 데이터 페이지네이션 조회"""
        all_data = []
        
        # 날짜 기본값 설정
        end_date = end_date or datetime.now().strftime("%Y%m%d")
        start_date = start_date or datetime.now().strftime("%Y%m%d")
        
        current_end = end_date
        records_collected = 0
        
        while records_collected < max_records:
            result = self._fetch_minute_chart_page(
                stock_code, interval, start_date, current_end
            )
            
            if not result:
                break
            
            # 데이터 포매팅 및 수집
            new_records = self._format_chart_data(result, max_records - records_collected)
            all_data.extend(new_records)
            records_collected += len(new_records)
            
            # 다음 페이지 확인
            current_end = self._get_next_page_date(result, current_end)
            if not current_end:
                break
        
        return all_data
    
    def _fetch_minute_chart_page(self, stock_code: str, interval: int, 
                                start_date: str, end_date: str) -> dict:
        """분봉 차트 페이지 조회"""
        result = self.get_minute_chart(stock_code, interval, start_date, end_date)
        if result and 'output2' in result and result['output2']:
            return result['output2']
        return None
    
    def _format_chart_data(self, data: list, limit: int) -> list:
        """차트 데이터 포매팅"""
        formatted = []
        for i, item in enumerate(data):
            if i >= limit:
                break
            formatted.append({
                'date': item.get('stck_bsop_date', ''),
                'time': item.get('stck_cntg_hour', ''),
                'open': float(item.get('stck_oprc', 0)),
                'high': float(item.get('stck_hgpr', 0)),
                'low': float(item.get('stck_lwpr', 0)),
                'close': float(item.get('stck_prpr', 0)),
                'volume': int(item.get('acml_vol', 0))
            })
        return formatted
    
    def _get_next_page_date(self, data: list, current_end: str) -> str:
        """다음 페이지 날짜 계산"""
        if len(data) < 100:  # 더 이상 데이터 없음
            return None
        
        last_date = data[-1].get('stck_bsop_date', '')
        if last_date and last_date != current_end:
            return last_date
        return None
    
    # ========== 추가 종목정보 메서드 ==========
    
    def get_stock_member_info(self, stock_code: str) -> dict:
        """주식거래원요청 (ka10002)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_request('stock_info', 'stock_member_info', params=params)
    
    def get_credit_trend(self, stock_code: str) -> dict:
        """신용매매동향요청 (ka10013)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_request('stock_info', 'credit_trend', params=params)
    
    def get_new_high_low(self, market: str = "ALL") -> dict:
        """신고저가요청 (ka10016)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_COND_SCR_DIV_CODE": "20",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('stock_info', 'new_high_low', params=params)
    
    def get_upper_lower_limit(self, market: str = "ALL") -> dict:
        """상하한가요청 (ka10017)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_COND_SCR_DIV_CODE": "20",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('stock_info', 'upper_lower_limit', params=params)
    
    def get_price_fluctuation(self, market: str = "ALL") -> dict:
        """가격급등락요청 (ka10019)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_COND_SCR_DIV_CODE": "20",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('stock_info', 'price_fluctuation', params=params)
    
    # ========== 추가 시세 메서드 ==========
    
    def get_stock_daily_weekly_monthly(self, stock_code: str, period: str = "D") -> dict:
        """주식일주월시분요청 (ka10005)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_PERIOD_DIV_CODE": period
        }
        return self.make_request('market_condition', 'stock_daily_weekly_monthly', params=params)
    
    def get_overtime_single_price(self, stock_code: str) -> dict:
        """시간외단일가요청 (ka10087)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_request('market_condition', 'overtime_single_price', params=params)
    
    # ========== 추가 순위정보 메서드 ==========
    
    def get_trading_volume_surge(self, market: str = "ALL") -> dict:
        """거래량급증요청 (ka10023)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_COND_SCR_DIV_CODE": "20",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('ranking', 'trading_volume_surge', params=params)
    
    def get_previous_day_rate_top(self, market: str = "ALL") -> dict:
        """전일대비등락률상위요청 (ka10027)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_COND_SCR_DIV_CODE": "20",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('ranking', 'previous_day_rate_top', params=params)
    
    def get_daily_volume_top(self, market: str = "ALL") -> dict:
        """당일거래량상위요청 (ka10030)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_COND_SCR_DIV_CODE": "20",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('ranking', 'daily_volume_top', params=params)
    
    def get_trading_amount_top(self, market: str = "ALL") -> dict:
        """거래대금상위요청 (ka10032)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_COND_SCR_DIV_CODE": "20",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('ranking', 'trading_amount_top', params=params)
    
    # ========== 업종 관련 메서드 ==========
    
    def get_sector_current_price(self, sector_code: str = "0001") -> dict:
        """업종현재가요청 (ka20001)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "U",
            "FID_INPUT_ISCD": sector_code
        }
        return self.make_request('sector', 'sector_current_price', params=params)
    
    def get_all_sector_index(self) -> dict:
        """전업종지수요청 (ka20003)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "U",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('sector', 'all_sector_index', params=params)
    
    # ========== ETF 관련 메서드 ==========
    
    def get_etf_return(self, etf_code: str) -> dict:
        """ETF수익율요청 (ka40001)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": etf_code
        }
        return self.make_request('etf', 'etf_return', params=params)
    
    def get_etf_all_market(self) -> dict:
        """ETF전체시세요청 (ka40004)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('etf', 'etf_all_market', params=params)
    
    # ========== 공매도 관련 메서드 ==========
    
    def get_short_sale_trend(self, stock_code: str, start_date: str = None, end_date: str = None) -> dict:
        """공매도추이요청 (ka10014)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('short_sale', 'short_sale_trend', params=params)
    
    # ========== 테마 관련 메서드 ==========
    
    def get_theme_group(self) -> dict:
        """테마그룹별요청 (ka90001)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('theme', 'theme_group', params=params)
    
    def get_theme_stocks(self, theme_code: str) -> dict:
        """테마구성종목요청 (ka90002)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": theme_code
        }
        return self.make_request('theme', 'theme_stocks', params=params)

    # ========== 종목정보 관련 추가 메서드 ==========
    
    def get_stock_high_low_approach(self, market: str = "ALL") -> dict:
        """고저가근접요청 (ka10018)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J" if market == "ALL" else "Q",
            "FID_COND_SCR_DIV_CODE": "20171",
            "FID_DIV_CLS_CODE": "0",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('ranking', 'high_low_approach', params=params)
    
    def get_volume_renewal(self, market: str = "ALL") -> dict:
        """거래량갱신요청 (ka10024)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J" if market == "ALL" else "Q",
            "FID_COND_SCR_DIV_CODE": "20171",
            "FID_DIV_CLS_CODE": "0",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('ranking', 'volume_renewal', params=params)
    
    def get_volume_concentration(self, stock_code: str) -> dict:
        """매물대집중요청 (ka10025)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_request('stock_info', 'volume_concentration', params=params)
    
    def get_high_low_per(self, market: str = "ALL") -> dict:
        """고저PER요청 (ka10026)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J" if market == "ALL" else "Q",
            "FID_COND_SCR_DIV_CODE": "20171",
            "FID_DIV_CLS_CODE": "0",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('ranking', 'high_low_per', params=params)
    
    def get_market_price_rate(self, stock_code: str) -> dict:
        """시가대비등락률요청 (ka10028)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_request('stock_info', 'market_price_rate', params=params)
    
    def get_trader_volume_analysis(self, stock_code: str) -> dict:
        """거래원매물대분석요청 (ka10043)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_request('stock_info', 'trader_volume_analysis', params=params)
    
    def get_trader_instant_volume(self, stock_code: str) -> dict:
        """거래원순간거래량요청 (ka10052)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_request('stock_info', 'trader_instant_volume', params=params)
    
    def get_volatility_interruption_stocks(self, market: str = "ALL") -> dict:
        """변동성완화장치발동종목요청 (ka10054)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J" if market == "ALL" else "Q",
            "FID_COND_SCR_DIV_CODE": "20171",
            "FID_DIV_CLS_CODE": "0",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('ranking', 'volatility_interruption', params=params)
    
    def get_current_previous_volume(self, stock_code: str) -> dict:
        """당일전일체결량요청 (ka10055)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_request('stock_info', 'current_previous_volume', params=params)
    
    def get_investor_daily_trading(self, stock_code: str, start_date: str = None, end_date: str = None) -> dict:
        """투자자별일별매매종목요청 (ka10058)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('stock_info', 'investor_daily_trading', params=params)
    
    def get_stock_investor_institutional(self, stock_code: str, start_date: str = None, end_date: str = None) -> dict:
        """종목별투자자기관별요청 (ka10059)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('stock_info', 'investor_institutional', params=params)
    
    def get_stock_investor_institutional_summary(self, stock_code: str, start_date: str = None, end_date: str = None) -> dict:
        """종목별투자자기관별합계요청 (ka10061)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('stock_info', 'investor_institutional_summary', params=params)
    
    def get_current_previous_execution(self, stock_code: str) -> dict:
        """당일전일체결요청 (ka10084)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_request('stock_info', 'current_previous_execution', params=params)
    
    def get_watchlist_info(self, watchlist_code: str = "1") -> dict:
        """관심종목정보요청 (ka10095)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": watchlist_code
        }
        return self.make_request('stock_info', 'watchlist_info', params=params)
    
    def get_stock_list(self, market: str = "ALL") -> dict:
        """종목정보 리스트 (ka10099)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J" if market == "ALL" else "Q",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('stock_info', 'stock_list', params=params)
    
    def get_stock_info_detail(self, stock_code: str) -> dict:
        """종목정보 조회 (ka10100)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_request('stock_info', 'stock_info_detail', params=params)
    
    def get_sector_code_list(self) -> dict:
        """업종코드 리스트 (ka10101)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('stock_info', 'sector_code_list', params=params)
    
    def get_member_company_list(self) -> dict:
        """회원사 리스트 (ka10102)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('stock_info', 'member_company_list', params=params)
    
    def get_program_trading_status(self, stock_code: str) -> dict:
        """종목별프로그램매매현황요청 (ka90004)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_request('stock_info', 'program_trading_status', params=params)

    # ========== 순위정보 관련 추가 메서드 ==========
    
    def get_bid_ask_volume_top(self, market: str = "ALL") -> dict:
        """호가잔량상위요청 (ka10020)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J" if market == "ALL" else "Q",
            "FID_COND_SCR_DIV_CODE": "20171",
            "FID_DIV_CLS_CODE": "0",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('ranking', 'bid_ask_volume_top', params=params)
    
    def get_bid_ask_volume_surge(self, market: str = "ALL") -> dict:
        """호가잔량급증요청 (ka10021)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J" if market == "ALL" else "Q",
            "FID_COND_SCR_DIV_CODE": "20171",
            "FID_DIV_CLS_CODE": "0",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('ranking', 'bid_ask_volume_surge', params=params)
    
    def get_remaining_volume_surge(self, market: str = "ALL") -> dict:
        """잔량율급증요청 (ka10022)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J" if market == "ALL" else "Q",
            "FID_COND_SCR_DIV_CODE": "20171",
            "FID_DIV_CLS_CODE": "0",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('ranking', 'remaining_volume_surge', params=params)
    
    def get_expected_execution_rate_top(self, market: str = "ALL") -> dict:
        """예상체결등락률상위요청 (ka10029)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J" if market == "ALL" else "Q",
            "FID_COND_SCR_DIV_CODE": "20171",
            "FID_DIV_CLS_CODE": "0",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('ranking', 'expected_execution_rate_top', params=params)
    
    def get_credit_ratio_top(self, market: str = "ALL") -> dict:
        """신용비율상위요청 (ka10033)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J" if market == "ALL" else "Q",
            "FID_COND_SCR_DIV_CODE": "20171",
            "FID_DIV_CLS_CODE": "0",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('ranking', 'credit_ratio_top', params=params)
    
    def get_foreign_consecutive_buy_top(self, market: str = "ALL") -> dict:
        """외인연속순매매상위요청 (ka10035)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J" if market == "ALL" else "Q",
            "FID_COND_SCR_DIV_CODE": "20171",
            "FID_DIV_CLS_CODE": "0",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('ranking', 'foreign_consecutive_buy_top', params=params)
    
    def get_foreign_limit_exhaustion_top(self, market: str = "ALL") -> dict:
        """외인한도소진율증가상위 (ka10036)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J" if market == "ALL" else "Q",
            "FID_COND_SCR_DIV_CODE": "20171",
            "FID_DIV_CLS_CODE": "0",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('ranking', 'foreign_limit_exhaustion_top', params=params)
    
    def get_foreign_bank_trading_top(self, market: str = "ALL") -> dict:
        """외국계창구매매상위요청 (ka10037)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J" if market == "ALL" else "Q",
            "FID_COND_SCR_DIV_CODE": "20171",
            "FID_DIV_CLS_CODE": "0",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('ranking', 'foreign_bank_trading_top', params=params)
    
    def get_stock_securities_ranking(self, stock_code: str) -> dict:
        """종목별증권사순위요청 (ka10038)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_request('ranking', 'stock_securities_ranking', params=params)
    
    def get_securities_trading_top(self, market: str = "ALL") -> dict:
        """증권사별매매상위요청 (ka10039)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J" if market == "ALL" else "Q",
            "FID_COND_SCR_DIV_CODE": "20171",
            "FID_DIV_CLS_CODE": "0",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('ranking', 'securities_trading_top', params=params)
    
    def get_daily_major_traders(self, stock_code: str) -> dict:
        """당일주요거래원요청 (ka10040)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_request('ranking', 'daily_major_traders', params=params)
    
    def get_net_buy_trader_ranking(self, market: str = "ALL") -> dict:
        """순매수거래원순위요청 (ka10042)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J" if market == "ALL" else "Q",
            "FID_COND_SCR_DIV_CODE": "20171",
            "FID_DIV_CLS_CODE": "0",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('ranking', 'net_buy_trader_ranking', params=params)
    
    def get_daily_top_departure(self, market: str = "ALL") -> dict:
        """당일상위이탈원요청 (ka10053)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J" if market == "ALL" else "Q",
            "FID_COND_SCR_DIV_CODE": "20171",
            "FID_DIV_CLS_CODE": "0",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('ranking', 'daily_top_departure', params=params)
    
    def get_same_net_trading_ranking(self, market: str = "ALL") -> dict:
        """동일순매매순위요청 (ka10062)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J" if market == "ALL" else "Q",
            "FID_COND_SCR_DIV_CODE": "20171",
            "FID_DIV_CLS_CODE": "0",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('ranking', 'same_net_trading_ranking', params=params)
    
    def get_intraday_investor_trading_top(self, market: str = "ALL") -> dict:
        """장중투자자별매매상위요청 (ka10065)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J" if market == "ALL" else "Q",
            "FID_COND_SCR_DIV_CODE": "20171",
            "FID_DIV_CLS_CODE": "0",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('ranking', 'intraday_investor_trading_top', params=params)
    
    def get_overtime_single_price_rate_ranking(self, market: str = "ALL") -> dict:
        """시간외단일가등락율순위요청 (ka10098)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J" if market == "ALL" else "Q",
            "FID_COND_SCR_DIV_CODE": "20171",
            "FID_DIV_CLS_CODE": "0",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('ranking', 'overtime_single_price_rate_ranking', params=params)
    
    def get_foreign_institutional_trading_top(self, market: str = "ALL") -> dict:
        """외국인기관매매상위요청 (ka90009)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J" if market == "ALL" else "Q",
            "FID_COND_SCR_DIV_CODE": "20171",
            "FID_DIV_CLS_CODE": "0",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('ranking', 'foreign_institutional_trading_top', params=params)

    # ========== 시세 관련 추가 메서드 ==========
    
    def get_stock_minute_price(self, stock_code: str) -> dict:
        """주식시분요청 (ka10006)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_request('market_condition', 'stock_minute_price', params=params)
    
    def get_market_condition_info(self, market: str = "ALL") -> dict:
        """시세표성정보요청 (ka10007)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J" if market == "ALL" else "Q",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('market_condition', 'market_condition_info', params=params)
    
    def get_subscription_rights_market(self) -> dict:
        """신주인수권전체시세요청 (ka10011)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('market_condition', 'subscription_rights_market', params=params)
    
    def get_execution_strength_time(self, stock_code: str, start_date: str = None, end_date: str = None) -> dict:
        """체결강도추이시간별요청 (ka10046)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('market_condition', 'execution_strength_time', params=params)
    
    def get_execution_strength_daily(self, stock_code: str, start_date: str = None, end_date: str = None) -> dict:
        """체결강도추이일별요청 (ka10047)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('market_condition', 'execution_strength_daily', params=params)
    
    def get_intraday_investor_trading(self, stock_code: str) -> dict:
        """장중투자자별매매요청 (ka10063)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_request('market_condition', 'intraday_investor_trading', params=params)
    
    def get_after_market_investor_trading(self, stock_code: str) -> dict:
        """장마감후투자자별매매요청 (ka10066)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_request('market_condition', 'after_market_investor_trading', params=params)
    
    def get_securities_stock_trading_trend(self, stock_code: str, start_date: str = None, end_date: str = None) -> dict:
        """증권사별종목매매동향요청 (ka10078)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('market_condition', 'securities_stock_trading_trend', params=params)
    
    def get_program_trading_time(self, start_date: str = None, end_date: str = None) -> dict:
        """프로그램매매추이요청 시간대별 (ka90005)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('market_condition', 'program_trading_time', params=params)
    
    def get_program_trading_balance_trend(self, start_date: str = None, end_date: str = None) -> dict:
        """프로그램매매차익잔고추이요청 (ka90006)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('market_condition', 'program_trading_balance_trend', params=params)
    
    def get_program_trading_cumulative_trend(self, start_date: str = None, end_date: str = None) -> dict:
        """프로그램매매누적추이요청 (ka90007)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('market_condition', 'program_trading_cumulative_trend', params=params)
    
    def get_stock_time_program_trading_trend(self, stock_code: str, start_date: str = None, end_date: str = None) -> dict:
        """종목시간별프로그램매매추이요청 (ka90008)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('market_condition', 'stock_time_program_trading_trend', params=params)
    
    def get_stock_daily_program_trading_trend(self, stock_code: str, start_date: str = None, end_date: str = None) -> dict:
        """종목일별프로그램매매추이요청 (ka90013)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('market_condition', 'stock_daily_program_trading_trend', params=params)

    # ========== 차트 관련 추가 메서드 ==========
    
    def get_stock_investor_institutional_chart(self, stock_code: str, start_date: str = None, end_date: str = None) -> dict:
        """종목별투자자기관별차트요청 (ka10060)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('chart', 'stock_investor_institutional_chart', params=params)
    
    def get_intraday_investor_trading_chart(self, stock_code: str) -> dict:
        """장중투자자별매매차트요청 (ka10064)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_request('chart', 'intraday_investor_trading_chart', params=params)
    
    def get_sector_tick_chart(self, sector_code: str = "0001", count: int = 100) -> dict:
        """업종틱차트조회요청 (ka20004)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": sector_code,
            "FID_INPUT_CNT_1": str(count)
        }
        return self.make_request('chart', 'sector_tick_chart', params=params)
    
    def get_sector_minute_chart(self, sector_code: str = "0001", interval: int = 1) -> dict:
        """업종분봉조회요청 (ka20005)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": sector_code,
            "FID_INPUT_HOUR_1": str(interval)
        }
        return self.make_request('chart', 'sector_minute_chart', params=params)
    
    def get_sector_daily_chart(self, sector_code: str = "0001", start_date: str = None, end_date: str = None) -> dict:
        """업종일봉조회요청 (ka20006)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=100)).strftime("%Y%m%d")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": sector_code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('chart', 'sector_daily_chart', params=params)
    
    def get_sector_weekly_chart(self, sector_code: str = "0001", start_date: str = None, end_date: str = None) -> dict:
        """업종주봉조회요청 (ka20007)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": sector_code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('chart', 'sector_weekly_chart', params=params)
    
    def get_sector_monthly_chart(self, sector_code: str = "0001", start_date: str = None, end_date: str = None) -> dict:
        """업종월봉조회요청 (ka20008)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365*3)).strftime("%Y%m%d")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": sector_code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('chart', 'sector_monthly_chart', params=params)
    
    def get_sector_yearly_chart(self, sector_code: str = "0001", start_date: str = None, end_date: str = None) -> dict:
        """업종년봉조회요청 (ka20019)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365*10)).strftime("%Y%m%d")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": sector_code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('chart', 'sector_yearly_chart', params=params)

    # ========== 업종 관련 추가 메서드 ==========
    
    def get_sector_program(self, sector_code: str = "0001") -> dict:
        """업종프로그램요청 (ka10010)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": sector_code
        }
        return self.make_request('sector', 'sector_program', params=params)
    
    def get_sector_investor_net_buy(self, sector_code: str = "0001", start_date: str = None, end_date: str = None) -> dict:
        """업종별투자자순매수요청 (ka10051)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": sector_code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('sector', 'sector_investor_net_buy', params=params)
    
    def get_sector_stock_price(self, sector_code: str = "0001") -> dict:
        """업종별주가요청 (ka20002)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": sector_code
        }
        return self.make_request('sector', 'sector_stock_price', params=params)
    
    def get_sector_current_price_daily(self, sector_code: str = "0001", start_date: str = None, end_date: str = None) -> dict:
        """업종현재가일별요청 (ka20009)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": sector_code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('sector', 'sector_current_price_daily', params=params)

    # ========== 기관/외국인 관련 추가 메서드 ==========
    
    def get_institutional_request(self, stock_code: str) -> dict:
        """주식기관요청 (ka10009)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code
        }
        return self.make_request('foreign_institution', 'institutional_request', params=params)
    
    def get_institutional_foreign_consecutive_trading(self, market: str = "ALL", start_date: str = None, end_date: str = None) -> dict:
        """기관외국인연속매매현황요청 (ka10131)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J" if market == "ALL" else "Q",
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('foreign_institution', 'institutional_foreign_consecutive_trading', params=params)

    # ========== 대차거래 관련 메서드 ==========
    
    def get_lending_trading_trend(self, stock_code: str, start_date: str = None, end_date: str = None) -> dict:
        """대차거래추이요청 (ka10068)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('lending', 'lending_trading_trend', params=params)
    
    def get_lending_trading_top10(self, market: str = "ALL") -> dict:
        """대차거래상위10종목요청 (ka10069)"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J" if market == "ALL" else "Q",
            "FID_INPUT_ISCD": "0000"
        }
        return self.make_request('lending', 'lending_trading_top10', params=params)
    
    def get_lending_trading_trend_by_stock(self, stock_code: str, start_date: str = None, end_date: str = None) -> dict:
        """대차거래추이요청(종목별) (ka20068)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": stock_code,
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('lending', 'lending_trading_trend_by_stock', params=params)
    
    def get_lending_trading_details(self, market: str = "ALL", start_date: str = None, end_date: str = None) -> dict:
        """대차거래내역요청 (ka90012)"""
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        params = {
            "FID_COND_MRKT_DIV_CODE": "J" if market == "ALL" else "Q",
            "FID_INPUT_DATE_1": start_date,
            "FID_INPUT_DATE_2": end_date
        }
        return self.make_request('lending', 'lending_trading_details', params=params)