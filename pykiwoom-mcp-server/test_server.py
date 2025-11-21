#!/usr/bin/env python3
"""
PyKiwoom MCP Server 테스트 스크립트

MCP 서버의 기본 기능을 테스트합니다.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# 부모 디렉토리의 pykiwoom_rest 패키지를 사용
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("❌ mcp 패키지를 찾을 수 없습니다.")
    print("   pip install mcp 로 설치해주세요.")
    sys.exit(1)


async def test_mcp_server():
    """MCP 서버 기본 기능 테스트"""

    # 환경 변수 확인
    required_env = ["ACCOUNT_NO", "KIWOOM_APPKEY", "KIWOOM_APPSECRET"]
    missing_env = [var for var in required_env if not os.getenv(var)]

    if missing_env:
        print(f"❌ 필수 환경 변수가 설정되지 않았습니다: {', '.join(missing_env)}")
        print("   .env 파일을 생성하거나 환경 변수를 설정해주세요.")
        return

    print("🚀 MCP 서버 테스트 시작...\n")

    server_script = Path(__file__).parent / "src" / "pykiwoom_mcp_server" / "server.py"

    server_params = StdioServerParameters(
        command="python",
        args=[str(server_script)],
        env={
            "ACCOUNT_NO": os.getenv("ACCOUNT_NO"),
            "KIWOOM_APPKEY": os.getenv("KIWOOM_APPKEY"),
            "KIWOOM_APPSECRET": os.getenv("KIWOOM_APPSECRET"),
        }
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 초기화
                await session.initialize()
                print("✅ MCP 서버 초기화 성공\n")

                # 도구 목록 확인
                tools = await session.list_tools()
                print(f"📋 사용 가능한 도구 ({len(tools)}개):")
                for tool in tools:
                    print(f"   - {tool.name}: {tool.description}")
                print()

                # 테스트 1: 주식 현재가 조회
                print("📈 테스트 1: 삼성전자(005930) 현재가 조회")
                try:
                    result = await session.call_tool(
                        "get_stock_price",
                        arguments={"stock_code": "005930"}
                    )
                    if result.content:
                        data = json.loads(result.content[0].text)
                        print(f"   현재가: {data.get('cur_prc', 'N/A')}")
                        print(f"   전일대비: {data.get('prdy_vrss', 'N/A')} ({data.get('prdy_ctrt', 'N/A')}%)")
                        print("   ✅ 테스트 성공\n")
                except Exception as e:
                    print(f"   ❌ 테스트 실패: {e}\n")

                # 테스트 2: 호가 조회
                print("📊 테스트 2: 삼성전자(005930) 호가 조회")
                try:
                    result = await session.call_tool(
                        "get_stock_orderbook",
                        arguments={"stock_code": "005930"}
                    )
                    if result.content:
                        data = json.loads(result.content[0].text)
                        print(f"   매도호가1: {data.get('askp1', 'N/A')}")
                        print(f"   매수호가1: {data.get('bidp1', 'N/A')}")
                        print("   ✅ 테스트 성공\n")
                except Exception as e:
                    print(f"   ❌ 테스트 실패: {e}\n")

                # 테스트 3: 순위 정보 조회
                print("🏆 테스트 3: 상승률 상위 종목 조회")
                try:
                    result = await session.call_tool(
                        "get_top_gainers",
                        arguments={"market": "KOSPI"}
                    )
                    if result.content:
                        data = json.loads(result.content[0].text)
                        if isinstance(data, list) and len(data) > 0:
                            print(f"   1위: {data[0].get('hts_kor_isnm', 'N/A')} "
                                  f"({data[0].get('prdy_ctrt', 'N/A')}%)")
                            print("   ✅ 테스트 성공\n")
                        else:
                            print(f"   데이터: {data}")
                            print("   ✅ 응답 성공 (장 외 시간일 수 있음)\n")
                except Exception as e:
                    print(f"   ❌ 테스트 실패: {e}\n")

                print("✅ 모든 테스트 완료!")

    except Exception as e:
        print(f"❌ MCP 서버 연결 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # .env 파일 로드
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print("✅ .env 파일 로드 완료\n")
    else:
        print("⚠️  .env 파일을 찾을 수 없습니다. 환경 변수를 직접 설정해주세요.\n")

    asyncio.run(test_mcp_server())
