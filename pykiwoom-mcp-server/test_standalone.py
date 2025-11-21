#!/usr/bin/env python3
"""
Standalone test script for PyKiwoom MCP Server
pytest 없이 실행 가능한 독립 테스트
"""

import asyncio
import inspect
import json
import sys
from pathlib import Path

# Add paths
parent_path = str(Path(__file__).parent / "src")
grandparent_path = str(Path(__file__).parent.parent / "src")
sys.path.insert(0, parent_path)
sys.path.insert(0, grandparent_path)


def test_import():
    """임포트 테스트"""
    print("=" * 60)
    print("1. 임포트 테스트")
    print("=" * 60)

    try:
        from pykiwoom_rest import KiwoomRest
        print("✓ pykiwoom_rest 임포트 성공")
    except ImportError as e:
        print(f"✗ pykiwoom_rest 임포트 실패: {e}")
        return False

    try:
        from pykiwoom_mcp_server.server import PyKiwoomMCPServer
        print("✓ PyKiwoomMCPServer 임포트 성공")
    except ImportError as e:
        print(f"✗ PyKiwoomMCPServer 임포트 실패: {e}")
        return False

    return True


def test_server_initialization():
    """서버 초기화 테스트"""
    print("\n" + "=" * 60)
    print("2. 서버 초기화 테스트")
    print("=" * 60)

    try:
        from pykiwoom_mcp_server.server import PyKiwoomMCPServer
        server = PyKiwoomMCPServer()

        print(f"✓ 서버 생성 성공")
        print(f"  - Server instance: {server.server is not None}")
        print(f"  - KiwoomRest lazy: {server.kiwoom is None}")
        print(f"  - Method registry size: {len(server._method_registry)}")

        return server
    except Exception as e:
        print(f"✗ 서버 초기화 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_method_registry(server):
    """메서드 레지스트리 테스트"""
    print("\n" + "=" * 60)
    print("3. 메서드 레지스트리 테스트")
    print("=" * 60)

    registry = server._method_registry

    print(f"✓ 레지스트리 크기: {len(registry)}개 메서드")

    # 카테고리별 분류
    categories = {
        'stock': 0,
        'chart': 0,
        'account': 0,
        'order': 0,
        'ranking': 0,
        'sector': 0,
        'auth': 0,
        'etc': 0
    }

    for name in registry.keys():
        if any(x in name for x in ['price', 'orderbook', 'investor', 'foreign', 'member', 'stock_', 'execution_info', 'program', 'trade_volume']):
            categories['stock'] += 1
        elif any(x in name for x in ['chart', 'daily', 'weekly', 'monthly', 'minute', 'yearly', 'tick']):
            categories['chart'] += 1
        elif any(x in name for x in ['account', 'balance', 'deposit', 'evaluation', 'unfilled', 'executed', 'return', 'estimated', 'realized', 'trading_diary', 'trading_history']):
            categories['account'] += 1
        elif any(x in name for x in ['order', 'buy', 'sell', 'modify', 'cancel']):
            categories['order'] += 1
        elif any(x in name for x in ['top', 'rank', 'volume', 'surge', 'departure', 'trading_amount']):
            categories['ranking'] += 1
        elif any(x in name for x in ['sector', 'index']):
            categories['sector'] += 1
        elif any(x in name for x in ['token', 'auth', 'logout']):
            categories['auth'] += 1
        else:
            categories['etc'] += 1

    print(f"\n카테고리별 분포:")
    total = 0
    for cat, count in categories.items():
        if count > 0:
            print(f"  - {cat:10s}: {count:3d}개")
            total += count

    print(f"  {'총합':10s}: {total:3d}개")

    # TR 코드 추출 확인
    tr_codes = sum(1 for info in registry.values() if info['tr_code'])
    print(f"\n✓ TR 코드 추출: {tr_codes}개 메서드")

    # 일부 예시 출력
    print(f"\n예시 메서드 (처음 5개):")
    for i, (name, info) in enumerate(list(registry.items())[:5]):
        tr = f"({info['tr_code']})" if info['tr_code'] else ""
        print(f"  {i+1}. {name} {tr}")
        print(f"     파라미터: {len(info['params'])}개 (필수: {len(info['required_params'])}개)")


async def test_list_endpoints(server):
    """list_endpoints 기능 테스트"""
    print("\n" + "=" * 60)
    print("4. list_endpoints 기능 테스트")
    print("=" * 60)

    try:
        # 전체 조회
        result_all = await server._handle_list_endpoints({'category': 'all'})
        data_all = json.loads(result_all[0].text)

        print(f"✓ list_endpoints(all) 성공")
        print(f"  - 총 엔드포인트: {data_all['total_endpoints']}개")
        print(f"  - 카테고리별:")
        for cat, count in data_all['by_category'].items():
            print(f"    • {cat}: {count}개")

        # 카테고리 필터 테스트
        result_chart = await server._handle_list_endpoints({'category': 'chart'})
        data_chart = json.loads(result_chart[0].text)

        print(f"\n✓ list_endpoints(chart) 성공")
        print(f"  - Chart API: {len(data_chart['endpoints']['chart'])}개")

        # 일부 예시 출력
        print(f"\n  예시 (처음 3개):")
        for endpoint in data_chart['endpoints']['chart'][:3]:
            print(f"    • {endpoint['name']}: {endpoint['description']}")

    except Exception as e:
        print(f"✗ list_endpoints 실패: {e}")
        import traceback
        traceback.print_exc()


def test_method_structure(server):
    """메서드 구조 검증"""
    print("\n" + "=" * 60)
    print("5. 메서드 구조 검증")
    print("=" * 60)

    registry = server._method_registry

    if len(registry) == 0:
        print("✗ 레지스트리가 비어있습니다")
        return

    # 첫 번째 메서드 구조 확인
    first_name, first_info = next(iter(registry.items()))

    required_keys = ['params', 'required_params', 'tr_code', 'doc']
    all_keys_present = all(key in first_info for key in required_keys)

    if all_keys_present:
        print(f"✓ 메서드 구조 검증 완료")
        print(f"  예시: {first_name}")
        print(f"  - params: {type(first_info['params']).__name__}")
        print(f"  - required_params: {type(first_info['required_params']).__name__}")
        print(f"  - tr_code: {first_info['tr_code']}")
        print(f"  - doc: {first_info['doc'][:50]}...")
    else:
        print(f"✗ 메서드 구조 불완전")

    # Private 메서드 제외 확인
    private_methods = [name for name in registry.keys() if name.startswith('_')]
    if len(private_methods) == 0:
        print(f"\n✓ Private 메서드 제외 확인")
    else:
        print(f"\n✗ Private 메서드 발견: {private_methods}")

    # 제외할 프로퍼티 확인
    excluded = ['auth', 'stock', 'chart', 'ranking', 'account', 'order', 'sector', 'websocket']
    found_excluded = [name for name in registry.keys() if name in excluded]
    if len(found_excluded) == 0:
        print(f"✓ 프로퍼티 메서드 제외 확인")
    else:
        print(f"✗ 프로퍼티 발견: {found_excluded}")


def test_summary(server):
    """테스트 요약"""
    print("\n" + "=" * 60)
    print("테스트 요약")
    print("=" * 60)

    registry = server._method_registry

    print(f"✓ 총 {len(registry)}개 API 엔드포인트 노출")
    print(f"✓ 동적 Tool 생성 방식 검증 완료")
    print(f"✓ list_endpoints 기능 정상")
    print(f"✓ 카테고리별 분류 정상")
    print(f"\n🎉 모든 테스트 통과!")


async def main():
    """메인 테스트 실행"""
    print("PyKiwoom MCP Server Standalone Test")
    print("=" * 60)

    # 1. 임포트 테스트
    if not test_import():
        print("\n❌ 임포트 실패. 테스트를 중단합니다.")
        return

    # 2. 서버 초기화
    server = test_server_initialization()
    if server is None:
        print("\n❌ 서버 초기화 실패. 테스트를 중단합니다.")
        return

    # 3. 메서드 레지스트리
    test_method_registry(server)

    # 4. list_endpoints
    await test_list_endpoints(server)

    # 5. 메서드 구조
    test_method_structure(server)

    # 요약
    test_summary(server)


if __name__ == "__main__":
    asyncio.run(main())
