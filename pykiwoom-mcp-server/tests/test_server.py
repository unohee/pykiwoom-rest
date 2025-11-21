"""
Unit tests for PyKiwoom MCP Server
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add parent directories to path
parent_path = str(Path(__file__).parent.parent / "src")
grandparent_path = str(Path(__file__).parent.parent.parent / "src")
sys.path.insert(0, parent_path)
sys.path.insert(0, grandparent_path)


class TestPyKiwoomMCPServer:
    """PyKiwoomMCPServer 유닛 테스트"""

    @pytest.fixture
    def server(self):
        """MCP 서버 인스턴스 (mock 사용)"""
        # pykiwoom_rest 모듈 mock
        with patch.dict('sys.modules', {'pykiwoom_rest': MagicMock(), 'pykiwoom_rest.exception_utils': MagicMock()}):
            from pykiwoom_mcp_server.server import PyKiwoomMCPServer
            server = PyKiwoomMCPServer()
            return server

    def test_server_initialization(self, server):
        """서버 초기화 테스트"""
        assert server.server is not None
        assert server.kiwoom is None  # lazy initialization
        assert isinstance(server._method_registry, dict)

    def test_method_registry_populated(self, server):
        """메서드 레지스트리가 채워지는지 테스트"""
        assert len(server._method_registry) > 0
        print(f"\n✓ 레지스트리에 {len(server._method_registry)}개 메서드 등록됨")

    def test_method_registry_structure(self, server):
        """레지스트리 구조 테스트"""
        if len(server._method_registry) > 0:
            first_method = next(iter(server._method_registry.values()))

            # 필수 키 확인
            assert 'params' in first_method
            assert 'required_params' in first_method
            assert 'tr_code' in first_method
            assert 'doc' in first_method

            assert isinstance(first_method['params'], dict)
            assert isinstance(first_method['required_params'], list)
            print(f"\n✓ 레지스트리 구조 검증 완료")

    def test_method_registry_categories(self, server):
        """카테고리별 메서드 분류 테스트"""
        categories = {
            'stock': 0,
            'chart': 0,
            'account': 0,
            'order': 0,
            'ranking': 0,
            'sector': 0,
            'auth': 0,
        }

        for name in server._method_registry.keys():
            if any(x in name for x in ['price', 'orderbook', 'investor', 'foreign']):
                categories['stock'] += 1
            elif any(x in name for x in ['chart', 'daily', 'weekly', 'monthly', 'minute']):
                categories['chart'] += 1
            elif any(x in name for x in ['account', 'balance', 'deposit']):
                categories['account'] += 1
            elif any(x in name for x in ['order', 'buy', 'sell']):
                categories['order'] += 1
            elif any(x in name for x in ['top', 'rank', 'volume', 'surge']):
                categories['ranking'] += 1
            elif any(x in name for x in ['sector', 'index']):
                categories['sector'] += 1
            elif any(x in name for x in ['token', 'auth', 'logout']):
                categories['auth'] += 1

        print(f"\n✓ 카테고리별 분류:")
        for cat, count in categories.items():
            if count > 0:
                print(f"  - {cat}: {count}개")

        # 적어도 하나의 카테고리에는 메서드가 있어야 함
        assert sum(categories.values()) > 0

    def test_excluded_methods(self, server):
        """제외되어야 할 메서드들이 제외되었는지 테스트"""
        excluded = ['auth', 'stock', 'chart', 'ranking', 'account', 'order', 'sector', 'websocket']

        for excluded_name in excluded:
            assert excluded_name not in server._method_registry

        print(f"\n✓ 프로퍼티 메서드 제외 확인 완료")

    def test_private_methods_excluded(self, server):
        """private 메서드가 제외되었는지 테스트"""
        for name in server._method_registry.keys():
            assert not name.startswith('_')

        print(f"\n✓ private 메서드 제외 확인 완료")

    def test_parameter_extraction(self, server):
        """파라미터 추출 테스트"""
        # get_stock_price 메서드가 있다면
        if 'get_stock_price' in server._method_registry:
            method_info = server._method_registry['get_stock_price']

            # stock_code 파라미터가 있어야 함
            assert 'stock_code' in method_info['params']
            assert 'stock_code' in method_info['required_params']

            print(f"\n✓ 파라미터 추출 검증 완료 (get_stock_price)")

    def test_tr_code_extraction(self, server):
        """TR 코드 추출 테스트"""
        tr_codes_found = 0

        for name, info in server._method_registry.items():
            if info['tr_code']:
                tr_codes_found += 1

        print(f"\n✓ TR 코드 추출: {tr_codes_found}개 메서드에서 발견")
        assert tr_codes_found > 0  # 적어도 하나는 있어야 함


class TestListEndpoints:
    """list_endpoints 기능 테스트"""

    @pytest.fixture
    def server(self):
        """MCP 서버 인스턴스"""
        with patch.dict('sys.modules', {'pykiwoom_rest': MagicMock(), 'pykiwoom_rest.exception_utils': MagicMock()}):
            from pykiwoom_mcp_server.server import PyKiwoomMCPServer
            return PyKiwoomMCPServer()

    @pytest.mark.asyncio
    async def test_list_endpoints_structure(self, server):
        """list_endpoints 반환 구조 테스트"""
        result = await server._handle_list_endpoints({'category': 'all'})

        assert len(result) == 1
        assert hasattr(result[0], 'text')

        data = json.loads(result[0].text)

        # 필수 키 확인
        assert 'total_endpoints' in data
        assert 'by_category' in data
        assert 'endpoints' in data

        print(f"\n✓ list_endpoints 구조 검증 완료")
        print(f"  총 엔드포인트: {data['total_endpoints']}개")

    @pytest.mark.asyncio
    async def test_list_endpoints_category_filter(self, server):
        """카테고리 필터링 테스트"""
        # 전체 조회
        result_all = await server._handle_list_endpoints({'category': 'all'})
        data_all = json.loads(result_all[0].text)

        # 특정 카테고리 조회
        result_stock = await server._handle_list_endpoints({'category': 'stock'})
        data_stock = json.loads(result_stock[0].text)

        # stock 카테고리만 있어야 함
        assert 'stock' in data_stock['endpoints']
        assert len(data_stock['endpoints']) == 1

        print(f"\n✓ 카테고리 필터링 검증 완료")
        print(f"  전체: {data_all['total_endpoints']}개")
        print(f"  Stock: {len(data_stock['endpoints']['stock'])}개")

    @pytest.mark.asyncio
    async def test_list_endpoints_detail(self, server):
        """엔드포인트 상세 정보 테스트"""
        result = await server._handle_list_endpoints({'category': 'stock'})
        data = json.loads(result[0].text)

        if 'stock' in data['endpoints'] and len(data['endpoints']['stock']) > 0:
            first_endpoint = data['endpoints']['stock'][0]

            # 필수 필드 확인
            assert 'name' in first_endpoint
            assert 'tr_code' in first_endpoint
            assert 'description' in first_endpoint
            assert 'param_count' in first_endpoint
            assert 'required_count' in first_endpoint
            assert 'params' in first_endpoint

            print(f"\n✓ 엔드포인트 상세 정보 검증 완료")
            print(f"  예시: {first_endpoint['name']}")


@pytest.mark.skipif(
    True,  # 실제 API 호출은 기본적으로 스킵
    reason="Requires actual Kiwoom API credentials"
)
class TestIntegration:
    """통합 테스트 (실제 API 호출)"""

    @pytest.mark.asyncio
    async def test_real_api_call(self):
        """실제 API 호출 테스트 (환경변수 필요)"""
        import os

        required_env = ['ACCOUNT_NO', 'KIWOOM_APPKEY', 'KIWOOM_APPSECRET']
        if not all(os.getenv(var) for var in required_env):
            pytest.skip("API credentials not available")

        from pykiwoom_mcp_server.server import PyKiwoomMCPServer
        server = PyKiwoomMCPServer()

        # KiwoomRest 초기화
        from pykiwoom_rest import KiwoomRest
        server.kiwoom = KiwoomRest(enable_rate_optimizer=True)

        # get_stock_price 호출 테스트
        result = server.kiwoom.get_stock_price("005930")
        assert result is not None
        print(f"\n✓ 실제 API 호출 성공: {result}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
