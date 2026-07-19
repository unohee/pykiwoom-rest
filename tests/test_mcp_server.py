"""MCP 도구 레지스트리와 안전 게이트 테스트."""

# ruff: noqa: E402, I001

import json

import pytest


pytest.importorskip("mcp")

from pykiwoom_rest.mcp_server import PyKiwoomMCPServer


class FakeKiwoom:
    """네트워크 호출 없이 MCP 경계를 검증하는 최소 클라이언트."""

    created = 0

    def __init__(self, enable_rate_optimizer=True):
        self.enable_rate_optimizer = enable_rate_optimizer
        FakeKiwoom.created += 1

    def get_stock_price(self, stock_code: str):
        """주식 현재가 조회 (ka10001)."""
        return {"code": stock_code, "price": 70000}

    async def get_async_status(self):
        """비동기 상태 조회."""
        return {"status": "ok"}

    def buy_stock(self, stock_code: str, quantity: int, price: int = 0):
        """주식 매수 주문."""
        return {"code": stock_code, "quantity": quantity, "price": price}

    def subscribe_realtime_quote(self, stock_code: str, callback=None):
        """실시간 콜백 구독."""
        raise AssertionError("MCP 도구로 노출되면 안 됩니다")


def _payload(contents):
    return json.loads(contents[0].text)


@pytest.fixture
def server():
    FakeKiwoom.created = 0
    return PyKiwoomMCPServer(client_class=FakeKiwoom)


@pytest.mark.asyncio
async def test_list_endpoints_does_not_create_api_client(server):
    result = await server._call_tool("list_endpoints", {"category": "all"})
    payload = _payload(result)

    assert payload["ok"] is True
    assert payload["totalEndpoints"] == 3
    assert FakeKiwoom.created == 0


@pytest.mark.asyncio
async def test_registry_excludes_callback_tools_and_marks_orders_destructive(server):
    tools = await server._list_tools()
    by_name = {tool.name: tool for tool in tools}

    assert "subscribe_realtime_quote" not in by_name
    assert by_name["get_stock_price"].annotations.readOnlyHint is True
    assert by_name["buy_stock"].annotations.destructiveHint is True
    assert "confirm" in by_name["buy_stock"].inputSchema["required"]


@pytest.mark.asyncio
async def test_real_kiwoom_registry_contract_without_credentials():
    real_server = PyKiwoomMCPServer()
    tools = await real_server._list_tools()
    by_name = {tool.name: tool for tool in tools}

    assert real_server.kiwoom is None
    assert "stock_code" in by_name["get_stock_price"].inputSchema["required"]
    assert by_name["buy_stock"].annotations.destructiveHint is True
    assert by_name["get_access_token"].annotations.destructiveHint is True
    assert by_name["revoke_token"].inputSchema["properties"]["token"]["type"] == [
        "string",
        "null",
    ]
    assert "subscribe_realtime_quote" not in by_name

    revoke_info = real_server._method_registry["revoke_token"]
    assert real_server._validate_arguments(revoke_info, {"token": None, "confirm": True}) is None


def test_real_state_changing_methods_always_require_confirmation():
    real_server = PyKiwoomMCPServer()
    changing_prefixes = (
        "buy_",
        "cancel_",
        "logout",
        "modify_",
        "refresh_",
        "revoke_",
        "sell_",
    )
    changing_names = {
        name
        for name in real_server._method_registry
        if name == "get_access_token" or name.startswith(changing_prefixes)
    }

    assert changing_names
    assert all(real_server._method_registry[name]["destructive"] for name in changing_names)


@pytest.mark.asyncio
async def test_read_only_tool_runs_in_worker_thread(server):
    result = await server._call_tool("get_stock_price", {"stock_code": "005930"})
    payload = _payload(result)

    assert payload == {
        "ok": True,
        "tool": "get_stock_price",
        "data": {"code": "005930", "price": 70000},
    }
    assert FakeKiwoom.created == 1


@pytest.mark.asyncio
async def test_async_tool_is_awaited_directly(server):
    result = await server._call_tool("get_async_status", {})

    assert _payload(result)["data"] == {"status": "ok"}


@pytest.mark.asyncio
async def test_order_requires_explicit_confirmation(server):
    rejected = _payload(
        await server._call_tool(
            "buy_stock", {"stock_code": "005930", "quantity": 1, "price": 70000}
        )
    )
    accepted = _payload(
        await server._call_tool(
            "buy_stock",
            {"stock_code": "005930", "quantity": 1, "price": 70000, "confirm": True},
        )
    )

    assert rejected["ok"] is False
    assert "confirm=true" in rejected["error"]
    assert accepted["ok"] is True
    assert accepted["data"]["quantity"] == 1


@pytest.mark.asyncio
async def test_direct_call_rejects_missing_extra_and_wrong_type_arguments(server):
    missing = _payload(await server._call_tool("get_stock_price", {}))
    extra = _payload(
        await server._call_tool("get_stock_price", {"stock_code": "005930", "extra": 1})
    )
    wrong_type = _payload(await server._call_tool("get_stock_price", {"stock_code": 5930}))

    assert "필수 인자" in missing["error"]
    assert "지원하지 않는 인자" in extra["error"]
    assert "string 타입" in wrong_type["error"]
