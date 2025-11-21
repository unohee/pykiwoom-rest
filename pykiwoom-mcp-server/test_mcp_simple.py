#!/usr/bin/env python3
"""간단한 MCP JSON-RPC 테스트"""
import json
import subprocess
import sys

def test_mcp():
    # MCP 서버 시작
    cmd = [
        "/home/unohee/dev/tools/pykiwoom-rest/.venv-mcp/bin/python3",
        "/home/unohee/dev/tools/pykiwoom-rest/pykiwoom-mcp-server/src/pykiwoom_mcp_server/server.py"
    ]
    
    env = {
        "ACCOUNT_NO": "63513804",
        "KIWOOM_APPKEY": "Ayr_sSVO7m520bOTg1KtrCGm-SWkHUX13LwF-z4ePf4",
        "KIWOOM_APPSECRET": "sI_jzlZYUVReTm1sSQivynZgO8puSDfMUEO4EkR6iB0"
    }
    
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
        bufsize=1
    )
    
    # Initialize 요청
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"}
        }
    }
    
    print("MCP 서버 초기화 요청...")
    proc.stdin.write(json.dumps(init_request) + "\n")
    proc.stdin.flush()
    
    # 응답 읽기
    stderr_line = proc.stderr.readline()
    print(f"서버 시작: {stderr_line.strip()}")
    
    response = proc.stdout.readline()
    result = json.loads(response)
    
    if "result" in result:
        print(f"✓ 초기화 성공: {result['result']['serverInfo']['name']}")
    
    # tools/list 요청
    list_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    print("\n도구 목록 요청...")
    proc.stdin.write(json.dumps(list_request) + "\n")
    proc.stdin.flush()
    
    response = proc.stdout.readline()
    result = json.loads(response)
    
    if "result" in result:
        tools = result['result']['tools']
        print(f"✓ 총 {len(tools)}개 도구 발견")
        print("\n처음 15개 도구:")
        for i, tool in enumerate(tools[:15], 1):
            print(f"  {i:2d}. {tool['name']}")
    
    proc.terminate()
    print("\n✅ MCP 서버 테스트 완료!")

if __name__ == "__main__":
    try:
        test_mcp()
    except Exception as e:
        print(f"❌ 에러: {e}")
        import traceback
        traceback.print_exc()
