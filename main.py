#!/usr/bin/env python3
"""
PyKiwoom REST API - 메인 진입점
키움증권 REST API Python 클라이언트

사용법:
    python main.py --help
    python main.py --demo    # 데모 실행
    python main.py --test    # 테스트 실행
"""

import os
import sys
import argparse
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_demo():
    """데모 실행"""
    import runpy

    print("PyKiwoom REST API 데모 실행")
    print("-" * 40)

    try:
        # example.py 실행 (runpy 사용으로 보안성 향상)
        demo_path = project_root / "example.py"
        if demo_path.exists():
            runpy.run_path(str(demo_path), run_name="__main__")
        else:
            print("example.py 파일을 찾을 수 없습니다.")
            return False
    except Exception as e:
        import traceback
        print(f"데모 실행 오류: {e}\n{traceback.format_exc()}")
        raise  # Fail-fast 원칙

    return True

def run_tests():
    """테스트 실행"""
    print("PyKiwoom REST API 테스트 실행")
    print("-" * 40)
    
    import subprocess
    
    tests_dir = project_root / "tests"
    if not tests_dir.exists():
        print("tests 디렉토리를 찾을 수 없습니다.")
        return False
    
    try:
        # pytest 실행
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            str(tests_dir), "-v"
        ], cwd=project_root)
        return result.returncode == 0
    except Exception as e:
        import traceback
        print(f"테스트 실행 오류: {e}\n{traceback.format_exc()}")
        raise  # Fail-fast 원칙

def show_info():
    """프로젝트 정보 표시"""
    print("PyKiwoom REST API")
    print("=" * 40)
    print("키움증권 REST API Python 클라이언트")
    print()
    print("주요 기능:")
    print("• 실시간 주가 조회")
    print("• 차트 데이터 수집")
    print("• 호가 정보 조회")
    print("• 계좌 정보 관리")
    print()
    print("사용법:")
    print("  python main.py --demo    # 데모 실행")
    print("  python main.py --test    # 테스트 실행")
    print()
    
    # 환경변수 설정 안내
    print("환경변수 설정 필요:")
    print("  ACCOUNT_NO=계좌번호")
    print("  KIWOOM_APPKEY=앱키")
    print("  KIWOOM_APPSECRET=앱시크릿")

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="PyKiwoom REST API 클라이언트"
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--demo", action="store_true", help="데모 실행")
    group.add_argument("--test", action="store_true", help="테스트 실행")
    group.add_argument("--info", action="store_true", help="프로젝트 정보")
    
    args = parser.parse_args()
    
    if args.demo:
        success = run_demo()
        sys.exit(0 if success else 1)
    elif args.test:
        success = run_tests()
        sys.exit(0 if success else 1)
    elif args.info:
        show_info()
    else:
        # 기본: 정보 표시
        show_info()

if __name__ == "__main__":
    main()