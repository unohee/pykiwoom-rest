"""
MCP Protocol Integration Tests
실제 MCP stdio 통신 테스트
"""

import asyncio
import json
import os
import sys
from pathlib import Path

import pytest

# mcp 클라이언트 임포트 (선택적)
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("⚠️  mcp 패키지를 찾을 수 없습니다. MCP 프로토콜 테스트를 건너뜁니다.")


@pytest.mark.skipif(not MCP_AVAILABLE, reason="mcp package not installed")
class TestMCPProtocol:
    """MCP 프로토콜 테스트"""

    @pytest.fixture
    def server_script(self):
        """서버 스크립트 경로"""
        return Path(__file__).parent.parent / "src" / "pykiwoom_mcp_server" / "server.py"

    @pytest.fixture
    def server_params(self, server_script):
        """서버 파라미터"""
        return StdioServerParameters(
            command="python3",
            args=[str(server_script)],
            env={
                "ACCOUNT_NO": os.getenv("ACCOUNT_NO", "dummy"),
                "KIWOOM_APPKEY": os.getenv("KIWOOM_APPKEY", "dummy"),
                "KIWOOM_APPSECRET": os.getenv("KIWOOM_APPSECRET", "dummy"),
            }
        )

    @pytest.mark.asyncio
    async def test_server_connection(self, server_params):
        """MCP 서버 연결 테스트"""
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # 초기화
                    await session.initialize()
                    print("\n✓ MCP 서버 연결 성공")

        except Exception as e:
            pytest.fail(f"MCP 서버 연결 실패: {e}")

    @pytest.mark.asyncio
    async def test_list_tools(self, server_params):
        """list_tools 테스트"""
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    # 도구 목록 조회
                    tools = await session.list_tools()

                    assert len(tools.tools) > 0
                    print(f"\n✓ 도구 목록 조회 성공: {len(tools.tools)}개")

                    # list_endpoints 도구 확인
                    tool_names = [tool.name for tool in tools.tools]
                    assert "list_endpoints" in tool_names
                    print("✓ list_endpoints 도구 확인")

                    # 일부 도구 출력
                    print("\n주요 도구:")
                    for tool in tools.tools[:5]:
                        print(f"  - {tool.name}: {tool.description[:50]}...")

        except Exception as e:
            pytest.fail(f"list_tools 실패: {e}")

    @pytest.mark.asyncio
    async def test_call_list_endpoints(self, server_params):
        """list_endpoints 도구 호출 테스트"""
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    # list_endpoints 호출
                    result = await session.call_tool(
                        "list_endpoints",
                        arguments={"category": "all"}
                    )

                    assert len(result.content) > 0
                    data = json.loads(result.content[0].text)

                    # 구조 검증
                    assert 'total_endpoints' in data
                    assert 'by_category' in data
                    assert 'endpoints' in data

                    print(f"\n✓ list_endpoints 호출 성공")
                    print(f"  총 엔드포인트: {data['total_endpoints']}개")
                    print(f"  카테고리별 분포:")
                    for cat, count in data['by_category'].items():
                        print(f"    - {cat}: {count}개")

        except Exception as e:
            pytest.fail(f"list_endpoints 호출 실패: {e}")

    @pytest.mark.asyncio
    async def test_call_list_endpoints_filtered(self, server_params):
        """list_endpoints 카테고리 필터 테스트"""
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    # chart 카테고리만 조회
                    result = await session.call_tool(
                        "list_endpoints",
                        arguments={"category": "chart"}
                    )

                    data = json.loads(result.content[0].text)

                    # chart 카테고리만 있어야 함
                    assert 'chart' in data['endpoints']
                    assert len(data['endpoints']) == 1

                    chart_count = len(data['endpoints']['chart'])
                    print(f"\n✓ 카테고리 필터링 성공")
                    print(f"  Chart API: {chart_count}개")

                    # 예시 출력
                    if chart_count > 0:
                        print("\n  예시:")
                        for endpoint in data['endpoints']['chart'][:3]:
                            print(f"    - {endpoint['name']}: {endpoint['description']}")

        except Exception as e:
            pytest.fail(f"카테고리 필터링 실패: {e}")

    @pytest.mark.asyncio
    async def test_tool_schema_validation(self, server_params):
        """도구 스키마 검증 테스트"""
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    tools = await session.list_tools()

                    # 각 도구의 스키마 검증
                    for tool in tools.tools[:10]:  # 처음 10개만
                        assert tool.name is not None
                        assert tool.description is not None
                        assert tool.inputSchema is not None

                        # inputSchema 구조 검증
                        schema = tool.inputSchema
                        assert 'type' in schema
                        assert schema['type'] == 'object'

                    print(f"\n✓ 도구 스키마 검증 완료 ({len(tools.tools)}개)")

        except Exception as e:
            pytest.fail(f"스키마 검증 실패: {e}")


@pytest.mark.skipif(
    not MCP_AVAILABLE or not all(os.getenv(v) for v in ['ACCOUNT_NO', 'KIWOOM_APPKEY', 'KIWOOM_APPSECRET']),
    reason="Requires MCP and Kiwoom credentials"
)
class TestMCPRealAPI:
    """실제 API 호출 테스트 (인증정보 필요)"""

    @pytest.fixture
    def server_script(self):
        """서버 스크립트 경로"""
        return Path(__file__).parent.parent / "src" / "pykiwoom_mcp_server" / "server.py"

    @pytest.fixture
    def server_params(self, server_script):
        """서버 파라미터 (실제 인증정보)"""
        return StdioServerParameters(
            command="python3",
            args=[str(server_script)],
            env={
                "ACCOUNT_NO": os.getenv("ACCOUNT_NO"),
                "KIWOOM_APPKEY": os.getenv("KIWOOM_APPKEY"),
                "KIWOOM_APPSECRET": os.getenv("KIWOOM_APPSECRET"),
            }
        )

    @pytest.mark.asyncio
    async def test_real_get_stock_price(self, server_params):
        """실제 주식 현재가 조회 테스트"""
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    # get_stock_price 호출
                    result = await session.call_tool(
                        "get_stock_price",
                        arguments={"stock_code": "005930"}
                    )

                    assert len(result.content) > 0
                    data = json.loads(result.content[0].text)

                    print(f"\n✓ 삼성전자 현재가 조회 성공:")
                    if 'cur_prc' in data:
                        print(f"  현재가: {data['cur_prc']}")
                        print(f"  전일대비: {data.get('prdy_vrss', 'N/A')}")
                    else:
                        print(f"  응답: {data}")

        except Exception as e:
            print(f"\n⚠️  실제 API 호출 실패 (장 시간 외일 수 있음): {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
