"""실제 stdio 전송을 사용하는 MCP 프로토콜 통합 테스트."""

import json
import os
import sys
from pathlib import Path

import pytest

mcp = pytest.importorskip("mcp")

from mcp import ClientSession, StdioServerParameters  # noqa: E402
from mcp.client.stdio import stdio_client  # noqa: E402


@pytest.fixture
def server_params():
    script = Path(__file__).resolve().parent.parent / "src" / "pykiwoom_mcp_server" / "server.py"
    return StdioServerParameters(
        command=sys.executable,
        args=[str(script)],
        env=dict(os.environ),
    )


@pytest.mark.asyncio
async def test_server_initializes_and_lists_tools(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.list_tools()

    names = {tool.name for tool in result.tools}
    assert "list_endpoints" in names
    assert "get_stock_price" in names
    assert "subscribe_realtime_quote" not in names


@pytest.mark.asyncio
async def test_list_endpoints_round_trip_without_credentials(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("list_endpoints", {"category": "order"})

    payload = json.loads(result.content[0].text)
    assert payload["ok"] is True
    assert list(payload["endpoints"]) == ["order"]
    assert any(item["destructive"] for item in payload["endpoints"]["order"])


@pytest.mark.asyncio
async def test_order_confirmation_gate_round_trip(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "buy_stock",
                {"stock_code": "005930", "quantity": 1, "price": 70000},
            )

    assert result.isError is True
    assert "confirm" in result.content[0].text


@pytest.mark.asyncio
async def test_tool_schema_rejects_wrong_type_and_extra_arguments(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            wrong_type = await session.call_tool("get_stock_price", {"stock_code": 5930})
            extra = await session.call_tool("get_stock_price", {"stock_code": "005930", "extra": 1})

    assert wrong_type.isError is True
    assert "not of type 'string'" in wrong_type.content[0].text
    assert extra.isError is True
    assert "Additional properties" in extra.content[0].text


@pytest.mark.integration
@pytest.mark.skipif(
    not all(os.getenv(name) for name in ("ACCOUNT_NO", "KIWOOM_APPKEY", "KIWOOM_APPSECRET")),
    reason="키움 API 인증 정보가 필요합니다",
)
@pytest.mark.asyncio
async def test_real_stock_price(server_params):
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("get_stock_price", {"stock_code": "005930"})

    payload = json.loads(result.content[0].text)
    assert payload["ok"] is True
    assert payload["data"]
