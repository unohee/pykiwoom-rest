#!/usr/bin/env python3
"""
PyKiwoom-REST Swagger UI 서버
Flask + Flasgger를 사용하여 Swagger UI를 제공합니다.

사용법:
    python3 swagger_server.py

Swagger UI 접근:
    http://localhost:5000/apidocs
"""

import os
import sys
from typing import Any, Dict, Optional

from flask import Flask, jsonify, request
from flasgger import Flasgger, swag_from

# 프로젝트 경로 추가
sys.path.insert(0, os.path.dirname(__file__))

from src.pykiwoom_rest import KiwoomRest

# Flask 앱 생성
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Swagger/Flasgger 설정
swagger = Flasgger(app)

# 전역 KiwoomRest 인스턴스
kiwoom = None


def init_kiwoom(account_no: str = None, appkey: str = None, appsecret: str = None) -> KiwoomRest:
    """KiwoomRest 인스턴스 초기화"""
    global kiwoom
    try:
        kiwoom = KiwoomRest(
            account_no=account_no or os.getenv("ACCOUNT_NO", "00000000"),
            appkey=appkey or os.getenv("KIWOOM_APPKEY", "dummy"),
            appsecret=appsecret or os.getenv("KIWOOM_APPSECRET", "dummy")
        )
        return kiwoom
    except Exception as e:
        print(f"⚠️ KiwoomRest 초기화 실패: {e}")
        raise


@app.route('/health', methods=['GET'])
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({
        "status": "healthy",
        "service": "PyKiwoom-REST Swagger Server",
        "version": "2.1.0"
    }), 200


@app.route('/api/auth/token', methods=['POST'])
def get_access_token():
    """
    OAuth2 토큰 발급
    ---
    tags:
      - Authentication
    summary: OAuth2 액세스 토큰 발급
    description: 앱키와 시크릿키를 사용하여 OAuth2 액세스 토큰을 발급받습니다
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              appkey:
                type: string
                description: Kiwoom App Key
              appsecret:
                type: string
                description: Kiwoom App Secret
    responses:
      200:
        description: 토큰 발급 성공
        content:
          application/json:
            schema:
              type: object
              properties:
                access_token:
                  type: string
                token_type:
                  type: string
                expires_in:
                  type: integer
                issued_at:
                  type: string
      400:
        description: 요청 파라미터 오류
      401:
        description: 인증 실패
    """
    try:
        data = request.get_json() or {}
        appkey = data.get('appkey')
        appsecret = data.get('appsecret')

        if not appkey or not appsecret:
            return jsonify({
                "error": "Missing appkey or appsecret",
                "code": "INVALID_REQUEST"
            }), 400

        # KiwoomRest 초기화
        init_kiwoom(appkey=appkey, appsecret=appsecret)

        # 토큰 발급
        token_info = kiwoom.get_access_token()
        return jsonify(token_info), 200
    except Exception as e:
        return jsonify({
            "error": str(e),
            "code": "AUTH_ERROR"
        }), 401


@app.route('/api/stock/price', methods=['GET'])
def get_stock_price():
    """
    주식 현재가 조회
    ---
    tags:
      - Stock
    summary: 주식 현재가 및 기본정보 조회
    parameters:
      - name: stock_code
        in: query
        required: true
        type: string
        description: 종목코드 (예: 005930 - 삼성전자)
    responses:
      200:
        description: 주식 정보 조회 성공
    """
    try:
        stock_code = request.args.get('stock_code')
        if not stock_code:
            return jsonify({"error": "stock_code is required"}), 400

        if not kiwoom:
            init_kiwoom()

        result = kiwoom.get_stock_price(stock_code)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/stock/investor-trading', methods=['GET'])
def get_stock_investor_trading():
    """
    투자자별 매매동향
    ---
    tags:
      - Stock
    summary: 투자자별(개인/외국인/기관) 매매동향 조회
    parameters:
      - name: stock_code
        in: query
        required: true
        type: string
        description: 종목코드
    responses:
      200:
        description: 투자자별 매매동향 조회 성공
    """
    try:
        stock_code = request.args.get('stock_code')
        if not stock_code:
            return jsonify({"error": "stock_code is required"}), 400

        if not kiwoom:
            init_kiwoom()

        result = kiwoom.get_stock_investor_trading(stock_code)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/stock/member-trading', methods=['GET'])
def get_stock_member_trading():
    """
    기관별 매매동향
    ---
    tags:
      - Stock
    summary: 증권사별 기관 매매동향 조회
    parameters:
      - name: stock_code
        in: query
        required: true
        type: string
        description: 종목코드
    responses:
      200:
        description: 기관별 매매동향 조회 성공
    """
    try:
        stock_code = request.args.get('stock_code')
        if not stock_code:
            return jsonify({"error": "stock_code is required"}), 400

        if not kiwoom:
            init_kiwoom()

        result = kiwoom.get_stock_member_trading(stock_code)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/stock/program-trading', methods=['GET'])
def get_stock_program_trading():
    """
    프로그램매매동향
    ---
    tags:
      - Stock
    summary: 프로그램 매매 추이 조회
    parameters:
      - name: stock_code
        in: query
        required: true
        type: string
        description: 종목코드
    responses:
      200:
        description: 프로그램매매동향 조회 성공
    """
    try:
        stock_code = request.args.get('stock_code')
        if not stock_code:
            return jsonify({"error": "stock_code is required"}), 400

        if not kiwoom:
            init_kiwoom()

        result = kiwoom.get_stock_program_trading(stock_code)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/chart/minute', methods=['GET'])
def get_minute_chart():
    """
    분봉 차트 데이터
    ---
    tags:
      - Chart
    summary: 분봉 차트 데이터 조회
    parameters:
      - name: stock_code
        in: query
        required: true
        type: string
        description: 종목코드
      - name: interval
        in: query
        type: integer
        default: 5
        description: 분봉 간격 (1, 5, 10, 15, 30, 60)
      - name: count
        in: query
        type: integer
        default: 100
        description: 조회 개수
    responses:
      200:
        description: 분봉 차트 데이터 조회 성공
    """
    try:
        stock_code = request.args.get('stock_code')
        interval = int(request.args.get('interval', 5))
        count = int(request.args.get('count', 100))

        if not stock_code:
            return jsonify({"error": "stock_code is required"}), 400

        if not kiwoom:
            init_kiwoom()

        result = kiwoom.get_minute_chart(stock_code, interval=interval, count=count)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/chart/daily', methods=['GET'])
def get_daily_chart():
    """
    일봉 차트 데이터
    ---
    tags:
      - Chart
    summary: 일봉 차트 데이터 조회
    parameters:
      - name: stock_code
        in: query
        required: true
        type: string
        description: 종목코드
      - name: count
        in: query
        type: integer
        default: 100
        description: 조회 개수
    responses:
      200:
        description: 일봉 차트 데이터 조회 성공
    """
    try:
        stock_code = request.args.get('stock_code')
        count = int(request.args.get('count', 100))

        if not stock_code:
            return jsonify({"error": "stock_code is required"}), 400

        if not kiwoom:
            init_kiwoom()

        result = kiwoom.get_daily_chart(stock_code, count=count)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/account/balance', methods=['GET'])
def get_account_balance():
    """
    계좌 잔고 조회
    ---
    tags:
      - Account
    summary: 현재 계좌의 평가 잔고를 조회합니다
    responses:
      200:
        description: 계좌 잔고 조회 성공
    """
    try:
        if not kiwoom:
            init_kiwoom()

        # 직접 account_api 호출
        result = kiwoom.account_api.get_account_evaluation()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/account/estimated-asset', methods=['GET'])
def get_estimated_asset():
    """
    추정자산 조회
    ---
    tags:
      - Account
    summary: 추정자산 현황을 조회합니다
    responses:
      200:
        description: 추정자산 조회 성공
    """
    try:
        if not kiwoom:
            init_kiwoom()

        result = kiwoom.account_api.get_estimated_asset()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/account/deposit-detail', methods=['GET'])
def get_deposit_detail():
    """
    예수금 상세 조회
    ---
    tags:
      - Account
    summary: 계좌의 예수금 상세 현황을 조회합니다
    responses:
      200:
        description: 예수금 상세 조회 성공
    """
    try:
        if not kiwoom:
            init_kiwoom()

        result = kiwoom.account_api.get_deposit_detail()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/account/realized-profit', methods=['GET'])
def get_realized_profit():
    """
    실현손익 조회
    ---
    tags:
      - Account
    summary: 당일 실현손익 상세를 조회합니다
    responses:
      200:
        description: 실현손익 조회 성공
    """
    try:
        if not kiwoom:
            init_kiwoom()

        result = kiwoom.account_api.get_realized_profit_detail()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/ranking/volume', methods=['GET'])
def get_volume_top():
    """
    거래량 상위 종목
    ---
    tags:
      - Ranking
    summary: 거래량이 많은 상위 종목들을 조회합니다
    parameters:
      - name: market
        in: query
        type: string
        default: ALL
        description: 시장 (ALL, KOSPI, KOSDAQ)
      - name: count
        in: query
        type: integer
        default: 50
        description: 조회 개수
    responses:
      200:
        description: 거래량 상위 종목 조회 성공
    """
    try:
        market = request.args.get('market', 'ALL')
        count = int(request.args.get('count', 50))

        if not kiwoom:
            init_kiwoom()

        result = kiwoom.get_volume_top(market=market, count=count)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.errorhandler(404)
def not_found(error):
    """404 에러 핸들러"""
    return jsonify({
        "error": "Not Found",
        "message": "요청한 엔드포인트를 찾을 수 없습니다",
        "available_endpoints": [
            "/apidocs - Swagger UI",
            "/health - 헬스 체크",
            "/api/auth/token",
            "/api/stock/price",
            "/api/stock/investor-trading",
            "/api/stock/member-trading",
            "/api/stock/program-trading",
            "/api/chart/minute",
            "/api/chart/daily",
            "/api/account/balance",
            "/api/account/estimated-asset",
            "/api/account/deposit-detail",
            "/api/account/realized-profit",
            "/api/ranking/volume"
        ]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500 에러 핸들러"""
    return jsonify({
        "error": "Internal Server Error",
        "message": str(error)
    }), 500


if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════╗
║     PyKiwoom-REST Swagger UI Server v2.1.0             ║
╚════════════════════════════════════════════════════════╝

📍 서버 시작 중...

🌐 액세스 주소:
   • Swagger UI: http://localhost:5000/apidocs
   • REST API:  http://localhost:5000/api/*
   • 헬스 체크: http://localhost:5000/health

📝 사용 방법:
   1. http://localhost:5000/apidocs 접속
   2. "Try it out" 버튼으로 각 엔드포인트 테스트
   3. 응답 결과 확인

🔐 인증:
   • 먼저 /api/auth/token으로 토큰 발급
   • 또는 .env 파일에 KIWOOM_APPKEY, KIWOOM_APPSECRET 설정

⚙️ 설정:
   • 포트: 5000
   • 호스트: localhost (0.0.0.0로 변경 가능)
   • 디버그: ON

종료: Ctrl+C

════════════════════════════════════════════════════════
    """)

    # KiwoomRest 초기화 시도
    try:
        init_kiwoom()
        print("✅ KiwoomRest 초기화 성공\n")
    except Exception as e:
        print(f"⚠️ KiwoomRest 초기화 실패: {e}")
        print("💡 팁: .env 파일에 ACCOUNT_NO, KIWOOM_APPKEY, KIWOOM_APPSECRET을 설정하세요\n")

    # Flask 앱 실행
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False
    )
