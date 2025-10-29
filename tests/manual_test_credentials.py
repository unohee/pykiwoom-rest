"""
Manual Test for Direct Credential Injection
pytest 없이 직접 테스트하는 스크립트

작성일: 2025-01-27
"""

import sys
import os

# 프로젝트 루트를 sys.path에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, "src"))

from pykiwoom_rest import KiwoomRest


def test_direct_injection():
    """직접 주입 테스트"""
    print("=== Test 1: 직접 주입 ===")
    try:
        kiwoom = KiwoomRest(
            account_no="test-account",
            appkey="test-key",
            appsecret="test-secret"
        )
        assert kiwoom.stock_api.account_no == "test-account"
        assert kiwoom.stock_api.appkey == "test-key"
        assert kiwoom.stock_api.appsecret == "test-secret"
        print("✓ 직접 주입 성공")
        return True
    except Exception as e:
        print(f"✗ 직접 주입 실패: {e}")
        return False


def test_missing_credentials():
    """누락된 인증 정보 테스트"""
    print("\n=== Test 2: 누락된 인증 정보 ===")
    # 환경변수 임시 제거
    old_env = {}
    env_vars = ["ACC_NO", "ACCOUNT_NO", "APPKEY", "KIWOOM_APPKEY", "APPSECRET", "KIWOOM_SECRETKEY", "KIWOOM_APPSECRET"]
    for var in env_vars:
        if var in os.environ:
            old_env[var] = os.environ.pop(var)

    try:
        kiwoom = KiwoomRest(appkey="test-key")
        print("✗ 에러가 발생해야 하는데 성공함")
        result = False
    except ValueError as e:
        if "필수 인증 정보가 누락되었습니다" in str(e):
            print(f"✓ 예상된 에러 발생: {e}")
            result = True
        else:
            print(f"✗ 예상과 다른 에러: {e}")
            result = False
    except Exception as e:
        print(f"✗ 예상치 못한 에러: {e}")
        result = False
    finally:
        # 환경변수 복구
        for var, value in old_env.items():
            os.environ[var] = value

    return result


def test_direct_injection_overrides_env():
    """직접 주입이 환경변수를 덮어쓰는지 테스트"""
    print("\n=== Test 3: 직접 주입 > 환경변수 우선순위 ===")
    # 환경변수 임시 설정
    os.environ["ACCOUNT_NO"] = "env-account"
    os.environ["KIWOOM_APPKEY"] = "env-key"
    os.environ["KIWOOM_APPSECRET"] = "env-secret"

    try:
        kiwoom = KiwoomRest(
            account_no="direct-account",
            appkey="direct-key",
            appsecret="direct-secret"
        )
        assert kiwoom.stock_api.account_no == "direct-account"
        assert kiwoom.stock_api.appkey == "direct-key"
        assert kiwoom.stock_api.appsecret == "direct-secret"
        print("✓ 직접 주입이 환경변수보다 우선됨")
        return True
    except Exception as e:
        print(f"✗ 테스트 실패: {e}")
        return False
    finally:
        # 환경변수 정리
        os.environ.pop("ACCOUNT_NO", None)
        os.environ.pop("KIWOOM_APPKEY", None)
        os.environ.pop("KIWOOM_APPSECRET", None)


def test_partial_injection():
    """일부만 주입 테스트"""
    print("\n=== Test 4: 일부만 직접 주입 ===")
    # 계좌번호만 환경변수에 설정
    os.environ["ACCOUNT_NO"] = "env-account"

    try:
        kiwoom = KiwoomRest(
            appkey="direct-key",
            appsecret="direct-secret"
        )
        assert kiwoom.stock_api.account_no == "env-account"
        assert kiwoom.stock_api.appkey == "direct-key"
        assert kiwoom.stock_api.appsecret == "direct-secret"
        print("✓ 일부 주입 + 환경변수 혼합 성공")
        return True
    except Exception as e:
        print(f"✗ 테스트 실패: {e}")
        return False
    finally:
        os.environ.pop("ACCOUNT_NO", None)


def main():
    """모든 테스트 실행"""
    print("직접 인증 정보 주입 기능 테스트\n")

    tests = [
        test_direct_injection,
        test_missing_credentials,
        test_direct_injection_overrides_env,
        test_partial_injection
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"테스트 실행 중 에러: {e}")
            results.append(False)

    # 결과 요약
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"테스트 결과: {passed}/{total} 성공")

    if passed == total:
        print("✓ 모든 테스트 통과!")
        return 0
    else:
        print("✗ 일부 테스트 실패")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
