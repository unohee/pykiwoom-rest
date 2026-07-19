#!/usr/bin/env python3
"""
종목시간별 프로그램매매 추이요청 (ka90008) 테스트 스크립트 (예제)
원본 테스트 파일을 examples로 이동하여 pytest 충돌을 방지
"""

import sys
import os
import time
from datetime import datetime, timedelta

# 절대 경로로 src 디렉토리를 sys.path에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from pykiwoom_rest.kiwoom_rest import KiwoomRest
from dotenv import load_dotenv


def test_hourly_program_trading():
    load_dotenv()
    kiwoom = KiwoomRest()
    test_date = "20250109"

    # 단일 요청 예제
    result = kiwoom.get_hourly_program_trading(stock_code="005930", date=test_date, amount_or_quantity="1")
    print(result)


if __name__ == "__main__":
    test_hourly_program_trading()

