#!/usr/bin/env python3
"""MCP 서버 연결 테스트"""
import asyncio
import json
import subprocess
from mcp.client.stdio import stdio_client, ClientSession

async def test_mcp():
    # MCP 서버 실행 설정
    server_params = {
        "command": "/home/unohee/dev/tools/pykiwoom-rest/.venv-mcp/bin/python3",
        "args": [
            "/home/unohee/dev/tools/pykiwoom-rest/pykiwoom-mcp-server/src/pykiwoom_mcp_server/server.py"
        ],
        "env": {
            "ACCOUNT_NO": "63513804",
            "KIWOOM_APPKEY": "Ayr_sSVO7m520bOTg1KtrCGm-SWkHUX13LwF-z4ePf4",
            "KIWOOM_APPSECRET": "sI_jzlZYUVReTm1sSQivynZgO8puSDfMUEO4EkR6iB0"
        }
    }
    
    print("MCP 서버 연결 중...")
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 서버 초기화
                await session.initialize()
                print("✓ 서버 초기화 완료")
                
                # 도구 목록 가져오기
                tools_result = await session.list_tools()
                tools = tools_result.tools
                
                print(f"\n✓ 총 {len(tools)}개 도구 발견:")
                print("\n처음 10개 도구:")
                for i, tool in enumerate(tools[:10], 1):
                    print(f"  {i}. {tool.name}")
                
                # list_endpoints 도구 테스트
                print("\n✓ list_endpoints 도구 테스트:")
                result = await session.call_tool(
                    "list_endpoints",
                    arguments={"category": "stock"}
                )
                
                data = json.loads(result.content[0].text)
                print(f"  Stock 카테고리: {len(data['endpoints'])}개")
                for endpoint in data['endpoints'][:5]:
                    print(f"    - {endpoint['name']}")
                
    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp())
