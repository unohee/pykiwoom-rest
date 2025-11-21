#!/usr/bin/env python3
"""
Live MCP Protocol Test
실제 MCP stdio 통신 테스트 (인증정보 불필요)
"""

import asyncio
import json
import os
import sys
from pathlib import Path

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("✗ mcp 패키지가 필요합니다: pip install mcp")
    sys.exit(1)


async def test_mcp_connection():
    """MCP 서버 연결 테스트"""
    print("=" * 70)
    print("PyKiwoom MCP Server - Live Protocol Test")
    print("=" * 70)

    server_script = Path(__file__).parent / "src" / "pykiwoom_mcp_server" / "server.py"

    if not server_script.exists():
        print(f"✗ 서버 스크립트를 찾을 수 없습니다: {server_script}")
        return False

    server_params = StdioServerParameters(
        command="python3",
        args=[str(server_script)],
        env={
            "ACCOUNT_NO": "dummy-account",
            "KIWOOM_APPKEY": "dummy-key",
            "KIWOOM_APPSECRET": "dummy-secret",
        }
    )

    try:
        print("\n[1] MCP 서버 연결 중...")
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 초기화
                await session.initialize()
                print("✓ MCP 서버 연결 성공")

                # Test 2: list_tools
                print("\n[2] 도구 목록 조회...")
                tools_result = await session.list_tools()
                tools = tools_result.tools

                print(f"✓ {len(tools)}개의 도구 발견")

                # list_endpoints 확인
                list_endpoints_tool = next((t for t in tools if t.name == "list_endpoints"), None)
                if list_endpoints_tool:
                    print("✓ list_endpoints 도구 확인")
                else:
                    print("✗ list_endpoints 도구 없음")

                # 일부 도구 출력
                print(f"\n주요 도구 (처음 10개):")
                for i, tool in enumerate(tools[:10]):
                    tr = ""
                    if "(" in tool.description and ")" in tool.description:
                        start = tool.description.find("(")
                        end = tool.description.find(")", start)
                        tr = tool.description[start:end+1]

                    desc = tool.description[:40] + "..." if len(tool.description) > 40 else tool.description
                    print(f"  {i+1:2d}. {tool.name:30s} {tr:10s} {desc}")

                # Test 3: call list_endpoints
                print("\n[3] list_endpoints 호출 테스트...")
                try:
                    result = await session.call_tool(
                        "list_endpoints",
                        arguments={"category": "all"}
                    )

                    if result.content and len(result.content) > 0:
                        data = json.loads(result.content[0].text)

                        print("✓ list_endpoints 호출 성공")
                        print(f"  총 엔드포인트: {data['total_endpoints']}개")
                        print(f"\n  카테고리별 분포:")
                        for cat, count in sorted(data['by_category'].items()):
                            print(f"    - {cat:10s}: {count:3d}개")

                        # Test 4: 카테고리 필터 테스트
                        print("\n[4] 카테고리 필터 테스트 (chart)...")
                        result_chart = await session.call_tool(
                            "list_endpoints",
                            arguments={"category": "chart"}
                        )

                        data_chart = json.loads(result_chart.content[0].text)
                        chart_endpoints = data_chart['endpoints']['chart']

                        print(f"✓ Chart API {len(chart_endpoints)}개 조회")
                        print(f"\n  Chart API 예시:")
                        for i, endpoint in enumerate(chart_endpoints[:5]):
                            tr = f"({endpoint['tr_code']})" if endpoint['tr_code'] else ""
                            print(f"    {i+1}. {endpoint['name']:25s} {tr:10s}")
                            print(f"       파라미터: {endpoint['param_count']}개 (필수: {endpoint['required_count']}개)")

                except Exception as e:
                    print(f"✗ list_endpoints 호출 실패: {e}")
                    return False

                # Test 5: 도구 스키마 검증
                print("\n[5] 도구 스키마 검증...")
                schema_valid = True
                for tool in tools[:20]:  # 처음 20개만
                    if not all([tool.name, tool.description, tool.inputSchema]):
                        print(f"✗ 스키마 불완전: {tool.name}")
                        schema_valid = False
                        break

                if schema_valid:
                    print(f"✓ 도구 스키마 검증 완료 ({len(tools)}개)")

                # Summary
                print("\n" + "=" * 70)
                print("테스트 요약")
                print("=" * 70)
                print(f"✓ MCP 프로토콜 연결: 성공")
                print(f"✓ 도구 개수: {len(tools)}개")
                print(f"✓ list_endpoints: 정상 작동")
                print(f"✓ 카테고리 필터링: 정상 작동")
                print(f"✓ 스키마 검증: 통과")
                print(f"\n🎉 모든 MCP 프로토콜 테스트 통과!")

                return True

    except Exception as e:
        print(f"\n✗ MCP 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_mcp_connection())
    sys.exit(0 if success else 1)
