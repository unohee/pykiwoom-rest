"""
pytest 설정 및 공통 fixture
"""

import pytest
import os
from unittest.mock import Mock, MagicMock, patch
import sys

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pykiwoom_rest import KiwoomRest, StockAPI, ChartAPI, RankingAPI
from pykiwoom_rest.kiwoom_base import KiwoomAPIBase


@pytest.fixture
def mock_env_vars():
    """환경변수 모킹"""
    with patch.dict(os.environ, {
        'ACCOUNT_NO': '12345678',
        'KIWOOM_APPKEY': 'test_app_key',
        'KIWOOM_APPSECRET': 'test_app_secret'
    }):
        yield


@pytest.fixture
def mock_response():
    """표준 API 응답 모킹"""
    return {
        'rt_cd': '0',
        'msg1': 'SUCCESS',
        'output': {
            'stck_prpr': '75000',
            'stck_oprc': '74500',
            'stck_hgpr': '75500',
            'stck_lwpr': '74000',
            'acml_vol': '1000000'
        }
    }


@pytest.fixture
def mock_session():
    """HTTP 세션 모킹"""
    session = MagicMock()
    response = MagicMock()
    response.json.return_value = {
        'rt_cd': '0',
        'msg1': 'SUCCESS',
        'output': {'test': 'data'}
    }
    response.raise_for_status = MagicMock()
    session.request.return_value = response
    return session


@pytest.fixture 
def kiwoom(mock_env_vars, mock_session):
    """KiwoomRest 인스턴스 fixture"""
    with patch('requests.Session', return_value=mock_session):
        # KiwoomRest의 내부 API들에 대해 토큰 패칭
        with patch.object(StockAPI, '_get_access_token', return_value='test_token'):
            with patch.object(ChartAPI, '_get_access_token', return_value='test_token'):
                with patch.object(RankingAPI, '_get_access_token', return_value='test_token'):
                    return KiwoomRest()


@pytest.fixture
def kiwoom_api_base(mock_env_vars, mock_session):
    """KiwoomAPIBase 인스턴스 fixture"""
    with patch('requests.Session', return_value=mock_session):
        with patch.object(KiwoomAPIBase, '_get_access_token', return_value='test_token'):
            return KiwoomAPIBase()


@pytest.fixture
def stock_api(mock_env_vars, mock_session):
    """StockAPI 인스턴스 fixture"""
    with patch('requests.Session', return_value=mock_session):
        with patch.object(StockAPI, '_get_access_token', return_value='test_token'):
            return StockAPI()


@pytest.fixture
def chart_api(mock_env_vars, mock_session):
    """ChartAPI 인스턴스 fixture"""
    with patch('requests.Session', return_value=mock_session):
        with patch.object(ChartAPI, '_get_access_token', return_value='test_token'):
            return ChartAPI()


@pytest.fixture
def ranking_api(mock_env_vars, mock_session):
    """RankingAPI 인스턴스 fixture"""
    with patch('requests.Session', return_value=mock_session):
        with patch.object(RankingAPI, '_get_access_token', return_value='test_token'):
            return RankingAPI()


@pytest.fixture
def api_response_success_dict():
    """성공 원시 JSON 응답 fixture"""
    return {'test': 'data', 'rt_cd': '0', 'msg1': 'SUCCESS'}


@pytest.fixture
def api_response_error_dict():
    """실패 원시 JSON 응답 fixture"""
    return {'rt_cd': '1', 'msg1': 'ERROR', 'error': {'code': 'E001', 'message': 'Test error'}}
