#!/usr/bin/env python3
"""
Quick integration test for PyKiwoom MCP Server
"""

import sys
from pathlib import Path

# Setup paths
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 60)
print("PyKiwoom MCP Server Quick Test")
print("=" * 60)

# Test 1: Import
print("\n[1] 임포트 테스트...")
try:
    from pykiwoom_rest import KiwoomRest
    print("✓ pykiwoom_rest 임포트 성공")
except Exception as e:
    print(f"✗ pykiwoom_rest 임포트 실패: {e}")
    sys.exit(1)

# Test 2: Inspect KiwoomRest methods
print("\n[2] KiwoomRest 메서드 분석...")
import inspect

public_methods = []
for name in dir(KiwoomRest):
    if not name.startswith('_') and name not in ['auth', 'stock', 'chart', 'ranking', 'account', 'order', 'sector', 'websocket']:
        attr = getattr(KiwoomRest, name)
        if callable(attr):
            try:
                sig = inspect.signature(attr)
                public_methods.append(name)
            except (ValueError, TypeError):
                pass

print(f"✓ {len(public_methods)}개의 공개 메서드 발견")
print(f"  예시: {public_methods[:5]}")

# Test 3: Test MCP server script syntax
print("\n[3] MCP 서버 스크립트 구문 검사...")
server_script = Path(__file__).parent / "src" / "pykiwoom_mcp_server" / "server.py"
try:
    import py_compile
    py_compile.compile(str(server_script), doraise=True)
    print(f"✓ {server_script.name} 구문 검사 통과")
except SyntaxError as e:
    print(f"✗ 구문 에러: {e}")
    sys.exit(1)

# Test 4: Count lines
print("\n[4] 코드 통계...")
with open(server_script) as f:
    lines = f.readlines()
    code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
    print(f"✓ 총 라인 수: {len(lines)}")
    print(f"✓ 코드 라인 수: {len(code_lines)}")

# Test 5: Check documentation
print("\n[5] 문서 확인...")
readme = Path(__file__).parent / "README.md"
if readme.exists():
    with open(readme) as f:
        content = f.read()
        print(f"✓ README.md 존재 ({len(content)} bytes)")
        if "동적 Tool 생성" in content:
            print("✓ 동적 Tool 생성 방식 문서화 확인")
else:
    print("✗ README.md 없음")

# Summary
print("\n" + "=" * 60)
print("테스트 요약")
print("=" * 60)
print(f"✓ pykiwoom_rest: {len(public_methods)}개 메서드")
print(f"✓ MCP 서버: 구문 검사 통과")
print(f"✓ 코드 라인: {len(code_lines)}줄")
print("\n🎉 Quick Test 통과!")
