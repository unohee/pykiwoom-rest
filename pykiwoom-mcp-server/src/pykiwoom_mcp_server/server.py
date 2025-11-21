#!/usr/bin/env python3
"""
PyKiwoom MCP Server - Dynamic Tool Generation

MCP 서버 for Kiwoom Securities REST API
모든 KiwoomRest 메서드를 자동으로 MCP tools로 노출
"""

import asyncio
import inspect
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# pykiwoom_rest 패키지 임포트 (부모 디렉토리)
parent_path = str(Path(__file__).parent.parent.parent.parent / "src")
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

try:
    from pykiwoom_rest import KiwoomRest
except ImportError as e:
    raise ImportError(
        "pykiwoom_rest 패키지를 찾을 수 없습니다. "
        "pip install -e ../.. 로 설치하거나 PYTHONPATH를 설정해주세요."
    ) from e


class PyKiwoomMCPServer:
    """PyKiwoom MCP Server 구현 - 동적 Tool 생성"""

    def __init__(self):
        self.server = Server("pykiwoom-mcp-server")
        self.kiwoom: Optional[KiwoomRest] = None
        self._method_registry = {}  # 메서드 이름 -> 메서드 정보 매핑
        self._build_method_registry()
        self._setup_handlers()

    def _build_method_registry(self):
        """KiwoomRest의 모든 공개 메서드를 분석하여 레지스트리 구축"""
        # dir()을 사용하여 모든 속성 탐색
        for name in dir(KiwoomRest):
            # private 메서드, property 제외
            if name.startswith('_') or name in ['auth', 'stock', 'chart', 'ranking',
                                                   'account', 'order', 'sector', 'websocket']:
                continue

            attr = getattr(KiwoomRest, name)
            if not callable(attr):
                continue

            method = attr

            try:
                sig = inspect.signature(method)
                doc = inspect.getdoc(method) or f"{name} 메서드"

                # 파라미터 추출 (self 제외)
                params = {}
                required_params = []

                for param_name, param in sig.parameters.items():
                    if param_name == 'self':
                        continue

                    # 타입 힌트에서 타입 추출
                    param_type = "string"  # 기본값
                    if param.annotation != inspect.Parameter.empty:
                        anno_str = str(param.annotation)
                        if 'int' in anno_str.lower():
                            param_type = "integer"
                        elif 'bool' in anno_str.lower():
                            param_type = "boolean"
                        elif 'dict' in anno_str.lower() or 'list' in anno_str.lower():
                            param_type = "object"

                    params[param_name] = {
                        "type": param_type,
                        "description": f"{param_name} 파라미터"
                    }

                    # 필수 파라미터 판별 (기본값 없음)
                    if param.default == inspect.Parameter.empty:
                        required_params.append(param_name)

                # TR 코드 추출
                tr_code = ""
                for word in doc.split():
                    if word.startswith(('ka', 'tb', 'bo', 'au')) and any(c.isdigit() for c in word):
                        tr_code = word.rstrip(',:)').strip('(')
                        break

                self._method_registry[name] = {
                    'method': method,
                    'params': params,
                    'required_params': required_params,
                    'tr_code': tr_code,
                    'doc': doc.split('\n')[0]  # 첫 줄만
                }
            except Exception as e:
                # 분석 실패한 메서드는 건너뛰기
                print(f"Warning: Failed to analyze method {name}: {e}", file=sys.stderr)
                continue

    def _setup_handlers(self):
        """핸들러 설정"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """사용 가능한 도구 목록 반환 (동적 생성)"""
            tools = []

            # list_endpoints 도구 추가 (메타 도구)
            tools.append(Tool(
                name="list_endpoints",
                description="사용 가능한 모든 API 엔드포인트 목록 조회",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "카테고리 필터 (stock, chart, account, order, ranking, sector, auth, all)",
                            "enum": ["stock", "chart", "account", "order", "ranking", "sector", "auth", "all"]
                        }
                    }
                }
            ))

            # 레지스트리의 모든 메서드를 tools로 변환
            for name, info in sorted(self._method_registry.items()):
                tr_desc = f" ({info['tr_code']})" if info['tr_code'] else ""

                tool = Tool(
                    name=name,
                    description=f"{info['doc']}{tr_desc}",
                    inputSchema={
                        "type": "object",
                        "properties": info['params'],
                        "required": info['required_params']
                    }
                )
                tools.append(tool)

            return tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """도구 호출 처리"""
            try:
                # KiwoomRest 인스턴스 초기화 (lazy initialization)
                if self.kiwoom is None:
                    self.kiwoom = KiwoomRest(enable_rate_optimizer=True)

                # list_endpoints 처리
                if name == "list_endpoints":
                    return await self._handle_list_endpoints(arguments)

                # 레지스트리에서 메서드 찾기
                if name not in self._method_registry:
                    raise ValueError(f"Unknown tool: {name}")

                # 메서드 호출
                method = getattr(self.kiwoom, name)
                result = method(**arguments)

                # 결과 반환
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2),
                    )
                ]

            except Exception as e:
                # API Error 처리
                if hasattr(e, 'error_code'):
                    return [
                        TextContent(
                            type="text",
                            text=f"API Error: {str(e)}\nError Code: {e.error_code}",
                        )
                    ]
                return [
                    TextContent(
                        type="text",
                        text=f"Error: {str(e)}",
                    )
                ]

        async def _handle_list_endpoints(arguments: Dict[str, Any]) -> list[TextContent]:
            """엔드포인트 목록 조회 처리"""
            category = arguments.get('category', 'all')

            # 카테고리별 분류
            categorized = {
                'stock': [],
                'chart': [],
                'account': [],
                'order': [],
                'ranking': [],
                'sector': [],
                'auth': [],
                'etc': []
            }

            for name, info in self._method_registry.items():
                # 카테고리 판별
                if any(x in name for x in ['price', 'orderbook', 'investor', 'foreign', 'member', 'stock_', 'execution_info', 'program', 'trade_volume']):
                    cat = 'stock'
                elif any(x in name for x in ['chart', 'daily', 'weekly', 'monthly', 'minute', 'yearly', 'tick']):
                    cat = 'chart'
                elif any(x in name for x in ['account', 'balance', 'deposit', 'evaluation', 'unfilled', 'executed', 'return', 'estimated', 'realized', 'trading_diary', 'trading_history']):
                    cat = 'account'
                elif any(x in name for x in ['order', 'buy', 'sell', 'modify', 'cancel']):
                    cat = 'order'
                elif any(x in name for x in ['top', 'rank', 'volume', 'surge', 'departure', 'trading_amount']):
                    cat = 'ranking'
                elif any(x in name for x in ['sector', 'index']):
                    cat = 'sector'
                elif any(x in name for x in ['token', 'auth', 'login', 'logout', 'revoke']):
                    cat = 'auth'
                else:
                    cat = 'etc'

                tr = f" ({info['tr_code']})" if info['tr_code'] else ""
                param_count = len(info['params'])
                required_count = len(info['required_params'])

                categorized[cat].append({
                    'name': name,
                    'tr_code': info['tr_code'],
                    'description': info['doc'],
                    'param_count': param_count,
                    'required_count': required_count,
                    'params': list(info['params'].keys())
                })

            # 카테고리 필터링
            if category != 'all' and category in categorized:
                result = {category: categorized[category]}
            else:
                result = categorized

            # 통계 추가
            total_count = sum(len(endpoints) for endpoints in categorized.values())
            summary = {
                'total_endpoints': total_count,
                'by_category': {cat: len(endpoints) for cat, endpoints in categorized.items() if endpoints},
                'endpoints': result
            }

            return [
                TextContent(
                    type="text",
                    text=json.dumps(summary, ensure_ascii=False, indent=2),
                )
            ]

        # _handle_list_endpoints를 인스턴스 메서드로 등록
        self._handle_list_endpoints = _handle_list_endpoints

    async def run(self):
        """서버 실행"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


async def main():
    """메인 진입점"""
    server = PyKiwoomMCPServer()
    print(f"PyKiwoom MCP Server started with {len(server._method_registry)} endpoints",
          file=sys.stderr)
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
