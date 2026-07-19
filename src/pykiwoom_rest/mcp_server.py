"""PyKiwoom REST API를 MCP 도구로 제공하는 stdio 서버."""

from __future__ import annotations

import asyncio
import inspect
import json
import sys
import types
from datetime import date, datetime
from typing import Any, Union, get_args, get_origin, get_type_hints

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool, ToolAnnotations

from .kiwoom_rest import KiwoomRest

CATEGORIES = ("stock", "chart", "account", "order", "ranking", "sector", "auth", "etc")

# 콜백이나 장기 연결을 요구하는 메서드는 stdio 요청/응답 도구로 안전하게 표현할 수 없다.
EXCLUDED_METHODS = {
    "close",
    "disable_websocket",
    "enable_websocket",
    "reset_rate_limiter",
    "subscribe_realtime_orderbook",
    "subscribe_realtime_quote",
    "subscribe_realtime_trade",
    "unsubscribe_realtime_all",
}

# 계좌/인증 상태를 변경하는 도구는 호출 인자에 명시적 확인이 있어야 실행한다.
DESTRUCTIVE_METHODS = {
    "buy_stock",
    "cancel_order",
    "get_access_token",
    "logout",
    "modify_order",
    "refresh_token",
    "revoke_token",
    "sell_stock",
}


def _json_default(value: Any) -> Any:
    """일반 API 응답을 MCP 텍스트 결과로 직렬화한다."""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return str(value)


def _json_type(annotation: Any) -> tuple[str | list[str], dict[str, Any] | None]:
    """Python 타입 힌트를 JSON Schema의 기본 타입으로 변환한다."""
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin in (Union, getattr(types, "UnionType", None)):
        concrete = [item for item in args if item is not type(None)]
        schema_type, extra = _json_type(concrete[0]) if concrete else ("string", None)
        if len(concrete) != len(args):
            variants = schema_type if isinstance(schema_type, list) else [schema_type]
            return [*variants, "null"], extra
        return schema_type, extra
    if annotation is bool:
        return "boolean", None
    if annotation is int:
        return "integer", None
    if annotation is float:
        return "number", None
    if annotation is dict or origin is dict:
        return "object", None
    if annotation is list or origin is list:
        item_schema: dict[str, Any] = {"type": "string"}
        if args:
            item_type, nested = _json_type(args[0])
            item_schema = {"type": item_type}
            if nested:
                item_schema.update(nested)
        return "array", {"items": item_schema}
    return "string", None


def _category_for(name: str) -> str:
    """메서드 이름을 사용자용 카테고리로 분류한다."""
    rules = (
        ("order", ("order", "buy", "sell", "modify", "cancel")),
        ("chart", ("chart", "daily", "weekly", "monthly", "minute", "yearly", "tick")),
        (
            "account",
            (
                "account",
                "balance",
                "deposit",
                "evaluation",
                "unfilled",
                "executed",
                "estimated",
                "realized",
                "trading_diary",
                "trading_history",
            ),
        ),
        ("sector", ("sector", "index")),
        ("auth", ("token", "auth", "login", "logout", "revoke")),
        ("ranking", ("top", "rank", "volume", "surge", "departure", "trading_amount")),
        (
            "stock",
            (
                "price",
                "orderbook",
                "investor",
                "foreign",
                "member",
                "stock_",
                "execution_info",
                "program",
                "trade_volume",
            ),
        ),
    )
    for category, markers in rules:
        if any(marker in name for marker in markers):
            return category
    return "etc"


def _matches_json_type(value: Any, expected: str | list[str]) -> bool:
    """JSON Schema 기본 타입과 Python 값을 비교한다."""
    if isinstance(expected, list):
        return any(_matches_json_type(value, item) for item in expected)
    checks = {
        "array": lambda item: isinstance(item, list),
        "boolean": lambda item: isinstance(item, bool),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "number": lambda item: isinstance(item, (int, float)) and not isinstance(item, bool),
        "null": lambda item: item is None,
        "object": lambda item: isinstance(item, dict),
        "string": lambda item: isinstance(item, str),
    }
    return checks.get(expected, lambda item: True)(value)


class PyKiwoomMCPServer:
    """`KiwoomRest` 공개 API를 안전한 MCP 도구로 노출한다."""

    def __init__(self, client_class: type[KiwoomRest] = KiwoomRest):
        self.server = Server("pykiwoom-mcp-server")
        self._client_class = client_class
        self.kiwoom: KiwoomRest | None = None
        self._method_registry: dict[str, dict[str, Any]] = {}
        self._build_method_registry()
        self._setup_handlers()

    def _build_method_registry(self) -> None:
        """호출 가능한 공개 API와 JSON Schema를 한 번만 분석한다."""
        for name in sorted(dir(self._client_class)):
            if name.startswith("_") or name in EXCLUDED_METHODS:
                continue

            method = getattr(self._client_class, name)
            if not callable(method):
                continue

            try:
                signature = inspect.signature(method)
                try:
                    type_hints = get_type_hints(method)
                except (NameError, TypeError):
                    type_hints = {}
                doc = inspect.getdoc(method) or f"{name} 메서드"
                properties: dict[str, dict[str, Any]] = {}
                required: list[str] = []

                for param_name, param in signature.parameters.items():
                    if param_name == "self":
                        continue
                    annotation = type_hints.get(param_name, param.annotation)
                    schema_type, extra = _json_type(annotation)
                    schema: dict[str, Any] = {
                        "type": schema_type,
                        "description": f"{param_name} 파라미터",
                    }
                    if extra:
                        schema.update(extra)
                    if param.default is inspect.Parameter.empty:
                        required.append(param_name)
                    elif param.default is not None:
                        schema["default"] = param.default
                    properties[param_name] = schema

                destructive = name in DESTRUCTIVE_METHODS
                if destructive:
                    properties["confirm"] = {
                        "type": "boolean",
                        "description": "실제 계좌 또는 인증 상태 변경을 명시적으로 승인",
                    }
                    required.append("confirm")

                tr_code = next(
                    (
                        word.rstrip(" ,:)").lstrip("(")
                        for word in doc.split()
                        if word.startswith(("ka", "kt", "tb", "bo", "au"))
                        and any(char.isdigit() for char in word)
                    ),
                    "",
                )
                self._method_registry[name] = {
                    "properties": properties,
                    "required": required,
                    "tr_code": tr_code,
                    "description": doc.splitlines()[0],
                    "category": _category_for(name),
                    "destructive": destructive,
                }
            except (TypeError, ValueError) as exc:
                print(f"메서드 분석 실패: {name}: {exc}", file=sys.stderr)

    def _setup_handlers(self) -> None:
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            tools = [
                Tool(
                    name="list_endpoints",
                    title="키움 API 도구 목록",
                    description="사용 가능한 키움 API 도구를 카테고리별로 조회합니다.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "조회할 도구 카테고리",
                                "enum": [*CATEGORIES, "all"],
                                "default": "all",
                            }
                        },
                    },
                    annotations=ToolAnnotations(
                        title="키움 API 도구 목록",
                        readOnlyHint=True,
                        destructiveHint=False,
                        idempotentHint=True,
                        openWorldHint=False,
                    ),
                )
            ]

            for name, info in self._method_registry.items():
                tr_suffix = f" ({info['tr_code']})" if info["tr_code"] else ""
                tools.append(
                    Tool(
                        name=name,
                        title=info["description"],
                        description=f"{info['description']}{tr_suffix}",
                        inputSchema={
                            "type": "object",
                            "properties": info["properties"],
                            "required": info["required"],
                            "additionalProperties": False,
                        },
                        annotations=ToolAnnotations(
                            title=info["description"],
                            readOnlyHint=not info["destructive"],
                            destructiveHint=info["destructive"],
                            idempotentHint=not info["destructive"],
                            openWorldHint=True,
                        ),
                    )
                )
            return tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
            payload = dict(arguments or {})
            if name == "list_endpoints":
                return self._list_endpoints(payload)
            if name not in self._method_registry:
                return self._error(f"알 수 없는 도구입니다: {name}")

            info = self._method_registry[name]
            if info["destructive"] and payload.get("confirm") is not True:
                return self._error(
                    "계좌 또는 인증 상태를 변경하는 도구입니다. 사용자 승인을 받은 뒤 confirm=true로 다시 호출하세요."
                )
            validation_error = self._validate_arguments(info, payload)
            if validation_error:
                return self._error(validation_error)
            payload.pop("confirm", None)

            try:
                if self.kiwoom is None:
                    self.kiwoom = self._client_class(enable_rate_optimizer=True)
                method = getattr(self.kiwoom, name)
                if inspect.iscoroutinefunction(method):
                    result = await method(**payload)
                else:
                    result = await asyncio.to_thread(method, **payload)
                return self._content({"ok": True, "tool": name, "data": result})
            except Exception as exc:  # MCP 경계에서 모든 API 예외를 구조화해 반환한다.
                error: dict[str, Any] = {
                    "ok": False,
                    "tool": name,
                    "error": str(exc),
                    "errorType": type(exc).__name__,
                }
                if hasattr(exc, "error_code"):
                    error["errorCode"] = exc.error_code
                return self._content(error)

        self._call_tool = call_tool
        self._list_tools = list_tools

    @staticmethod
    def _content(payload: dict[str, Any]) -> list[TextContent]:
        return [
            TextContent(
                type="text",
                text=json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default),
            )
        ]

    def _error(self, message: str) -> list[TextContent]:
        return self._content({"ok": False, "error": message})

    @staticmethod
    def _validate_arguments(info: dict[str, Any], arguments: dict[str, Any]) -> str | None:
        """직접 호출에서도 MCP 도구 스키마의 기본 계약을 검증한다."""
        properties = info["properties"]
        missing = [name for name in info["required"] if name not in arguments]
        if missing:
            return f"필수 인자가 없습니다: {', '.join(missing)}"

        unexpected = sorted(set(arguments) - set(properties))
        if unexpected:
            return f"지원하지 않는 인자입니다: {', '.join(unexpected)}"

        for name, value in arguments.items():
            expected = properties[name]["type"]
            if not _matches_json_type(value, expected):
                expected_text = ", ".join(expected) if isinstance(expected, list) else expected
                return f"{name} 인자는 {expected_text} 타입이어야 합니다"
        return None

    def _list_endpoints(self, arguments: dict[str, Any]) -> list[TextContent]:
        category = arguments.get("category", "all")
        if category not in (*CATEGORIES, "all"):
            return self._error(f"지원하지 않는 카테고리입니다: {category}")

        grouped: dict[str, list[dict[str, Any]]] = {item: [] for item in CATEGORIES}
        for name, info in self._method_registry.items():
            grouped[info["category"]].append(
                {
                    "name": name,
                    "trCode": info["tr_code"],
                    "description": info["description"],
                    "parameters": list(info["properties"]),
                    "required": info["required"],
                    "destructive": info["destructive"],
                }
            )

        selected = grouped if category == "all" else {category: grouped[category]}
        return self._content(
            {
                "ok": True,
                "totalEndpoints": sum(len(items) for items in grouped.values()),
                "byCategory": {key: len(items) for key, items in grouped.items() if items},
                "endpoints": selected,
            }
        )

    async def run(self) -> None:
        """stdio 전송으로 MCP 서버를 실행한다."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


async def _run() -> None:
    server = PyKiwoomMCPServer()
    print(
        f"PyKiwoom MCP 서버 시작: {len(server._method_registry)}개 도구",
        file=sys.stderr,
    )
    await server.run()


def main() -> None:
    """콘솔 스크립트 진입점."""
    asyncio.run(_run())


if __name__ == "__main__":
    main()
