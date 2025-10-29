"""
Direct Credential Injection Example
환경변수 대신 직접 인증 정보를 주입하는 예제

작성일: 2025-01-27
"""

from pykiwoom_rest import KiwoomRest


def main():
    """
    직접 인증 정보 주입 예제

    이 방식은 다음과 같은 경우 유용합니다:
    - 프로덕션 환경에서 환경변수 설정이 어려운 경우
    - 외부 패키지로 배포하여 사용자가 코드 내에서 설정하고 싶은 경우
    - 여러 계정을 동적으로 전환하며 사용하는 경우
    """

    # ===== 방법 1: 모든 인증 정보 직접 주입 =====
    print("=== 방법 1: 모든 인증 정보 직접 주입 ===")

    kiwoom = KiwoomRest(
        account_no="your-account-number",  # 계좌번호
        appkey="your-app-key",             # 앱키
        appsecret="your-app-secret"        # 앱시크릿
    )

    # 주식 정보 조회
    try:
        stock_price = kiwoom.get_stock_price("005930")  # 삼성전자
        print(f"삼성전자 현재가: {stock_price}")
    except Exception as e:
        print(f"에러: {e}")


    # ===== 방법 2: 일부만 직접 주입 (나머지는 환경변수) =====
    print("\n=== 방법 2: 일부만 직접 주입 ===")

    kiwoom_partial = KiwoomRest(
        appkey="your-app-key",
        appsecret="your-app-secret"
        # account_no는 환경변수 ACC_NO 또는 ACCOUNT_NO에서 로드
    )


    # ===== 방법 3: 여러 계정 동적 전환 =====
    print("\n=== 방법 3: 여러 계정 동적 전환 ===")

    accounts = [
        {
            "account_no": "account-1",
            "appkey": "key-1",
            "appsecret": "secret-1"
        },
        {
            "account_no": "account-2",
            "appkey": "key-2",
            "appsecret": "secret-2"
        }
    ]

    for idx, account_info in enumerate(accounts, 1):
        print(f"\n계정 {idx} 처리 중...")
        kiwoom_multi = KiwoomRest(**account_info)

        # 각 계정별 작업 수행
        try:
            balance = kiwoom_multi.get_account_balance()
            print(f"  계좌 {account_info['account_no']} 잔고: {balance}")
        except Exception as e:
            print(f"  에러: {e}")


    # ===== 방법 4: 외부 설정 파일에서 로드 =====
    print("\n=== 방법 4: 외부 설정 파일 활용 ===")

    # config.json 예시:
    # {
    #   "account_no": "12345678",
    #   "appkey": "your-key",
    #   "appsecret": "your-secret"
    # }

    import json
    import os

    config_path = "config.json"
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        kiwoom_config = KiwoomRest(**config)
        print(f"설정 파일에서 로드 완료: 계좌 {config['account_no']}")
    else:
        print(f"설정 파일 {config_path}이 없습니다.")


    print("\n=== 완료 ===")


if __name__ == "__main__":
    main()
