"""MCP 호환 패키지가 메인 서버 계약을 그대로 제공하는지 검증한다."""

import json

import pytest
from pykiwoom_rest.mcp_server import PyKiwoomMCPServer


@pytest.fixture
def server():
    return PyKiwoomMCPServer()


def _payload(contents):
    return json.loads(contents[0].text)


def test_server_builds_registry_without_credentials(server):
    assert server.server is not None
    assert server.kiwoom is None
    assert "get_stock_price" in server._method_registry
    assert "subscribe_realtime_quote" not in server._method_registry


@pytest.mark.asyncio
async def test_tool_annotations_match_safety_contract(server):
    tools = {tool.name: tool for tool in await server._list_tools()}

    assert tools["get_stock_price"].annotations.readOnlyHint is True
    assert tools["buy_stock"].annotations.destructiveHint is True
    assert "confirm" in tools["buy_stock"].inputSchema["required"]


@pytest.mark.asyncio
async def test_list_endpoints_is_available_without_api_client(server):
    payload = _payload(await server._call_tool("list_endpoints", {"category": "chart"}))

    assert payload["ok"] is True
    assert payload["totalEndpoints"] > 0
    assert list(payload["endpoints"]) == ["chart"]
    assert server.kiwoom is None


@pytest.mark.asyncio
async def test_order_without_confirmation_is_rejected_before_client_creation(server):
    payload = _payload(
        await server._call_tool(
            "buy_stock",
            {"stock_code": "005930", "quantity": 1, "price": 70000},
        )
    )

    assert payload["ok"] is False
    assert "confirm=true" in payload["error"]
    assert server.kiwoom is None
