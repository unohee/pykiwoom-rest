"""
kiwoom CLI — LLM-friendly 키움증권 REST API
진입점: kiwoom <command> [options]
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from .field_map import (
    ACCOUNT_BALANCE,
    CHART_PRICE,
    HOLDING,
    INVESTOR_TREND,
    ORDERBOOK,
    RANKING,
    SECTOR_INDEX,
    STOCK_PRICE,
    remap,
    remap_keep_all,
)
from .formatters import json_output, table_output
from .schema import get_schema, list_types

# ── 장 상태 캐시 (세션당 1회 체크) ──

_market_status = {
    "checked": False,
    "is_holiday": None,
    "last_business_day": None,
    "notice": None,
}


def _check_market_status():
    """주말/장시간 감지. Kiwoom은 is_holiday API가 없으므로 weekday + hour 기반."""
    if _market_status["checked"]:
        return
    _market_status["checked"] = True

    now = datetime.now()
    today_str = now.strftime("%Y%m%d")

    if now.weekday() >= 5:
        # 주말
        _market_status["is_holiday"] = True
        # 직전 금요일 찾기
        days_back = now.weekday() - 4  # 토=1, 일=2
        prev = now - timedelta(days=days_back)
        prev_str = prev.strftime("%Y%m%d")
        bday = prev.strftime("%Y-%m-%d %a")
        _market_status["last_business_day"] = prev_str
        _market_status["notice"] = f"주말 — 데이터는 직전 영업일({bday}) 기준"
    else:
        _market_status["is_holiday"] = False
        _market_status["last_business_day"] = today_str
        hour = now.hour
        if hour < 9:
            _market_status["notice"] = "장 시작 전 — 데이터는 전일 종가 기준"
        elif hour >= 16:
            _market_status["notice"] = "장 마감 후 — 데이터는 금일 종가 기준"


def _create_client():
    """KiwoomRest 인스턴스 생성."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    from pykiwoom_rest import KiwoomRest
    client = KiwoomRest()
    _check_market_status()
    return client


def _out(data, pretty=False, raw=False, fmt="json"):
    """통일된 출력. notice 자동 주입."""
    notice = _market_status.get("notice")
    if notice and isinstance(data, dict) and "data" in data:
        data["_notice"] = notice

    if fmt == "table":
        # 테이블 출력: data 키 안의 리스트를 찾아서 출력
        inner = data.get("data", data) if isinstance(data, dict) else data
        if isinstance(inner, dict):
            # 중첩된 리스트 탐색
            for v in inner.values():
                if isinstance(v, list) and v:
                    print(table_output(v))
                    return
            print(table_output(inner))
        else:
            print(table_output(inner))
    else:
        print(json_output(data, pretty))


def _extract_output(data, key="output"):
    """API 응답에서 output/output2 데이터 추출."""
    if not data or not isinstance(data, dict):
        return None
    return data.get(key)


# ── 핸들러 ──


def cmd_price(args):
    """주식 현재가 조회."""
    client = _create_client()
    code = args.code
    result = {"stock": {"code": code}}

    data = client.get_stock_price(code)
    output = _extract_output(data)
    if output:
        mapped = remap(output, STOCK_PRICE) if not args.raw else output
        result["stock"]["price"] = mapped

    if args.orderbook:
        ob_data = client.get_stock_orderbook(code)
        ob_output = _extract_output(ob_data)
        if ob_output:
            mapped_ob = remap(ob_output, ORDERBOOK) if not args.raw else ob_output
            result["stock"]["orderbook"] = mapped_ob

    _out({"data": result}, args.pretty, args.raw, args.format)


def cmd_chart(args):
    """차트 데이터 조회."""
    client = _create_client()
    code = args.code

    from_date = getattr(args, "from_date", None)
    to_date = getattr(args, "to_date", None)
    count = getattr(args, "count", 100)

    # 차트 타입 결정
    if args.minute:
        interval = args.interval or 5
        data = client.get_minute_chart(code, interval, from_date, to_date, count)
        chart_type = f"minute_{interval}"
    elif args.weekly:
        data = client.get_weekly_chart(code, from_date, to_date)
        chart_type = "weekly"
    elif args.monthly:
        data = client.get_monthly_chart(code, from_date, to_date)
        chart_type = "monthly"
    elif args.yearly:
        data = client.get_yearly_chart(code, from_date, to_date)
        chart_type = "yearly"
    else:
        # 기본값: 일봉
        data = client.get_daily_chart(code, from_date, to_date)
        chart_type = "daily"

    result = {"chart": {"code": code, "type": chart_type}}

    # output2에 차트 데이터가 들어있음
    items = _extract_output(data, "output2")
    if items and isinstance(items, list):
        if not args.raw:
            items = [remap(item, CHART_PRICE) for item in items]
        if count and len(items) > count:
            items = items[:count]
        result["chart"]["data"] = items
        result["chart"]["count"] = len(items)
    else:
        # output에 있을 수도 있음
        output = _extract_output(data)
        if output:
            result["chart"]["data"] = output

    _out({"data": result}, args.pretty, args.raw, args.format)


def cmd_rank(args):
    """순위 조회."""
    client = _create_client()
    market = getattr(args, "market", "ALL")

    rank_funcs = {
        "volume": lambda: client.get_daily_volume_top(market),
        "amount": lambda: client.get_trading_amount_top(market),
        "gainers": lambda: client.get_previous_day_rate_top(market),
        "foreign-buy": lambda: client.get_foreign_top_buy(),
        "surge": lambda: client.get_trading_volume_surge(market),
    }

    func = rank_funcs.get(args.type)
    if not func:
        _out({"error": f"Unknown rank type: {args.type}. Available: {', '.join(rank_funcs.keys())}"})
        sys.exit(1)

    data = func()
    result = {"ranking": {"type": args.type, "market": market}}

    items = _extract_output(data, "output2") or _extract_output(data, "output")
    if items and isinstance(items, list):
        if not args.raw:
            items = [remap(item, RANKING) for item in items]
        result["ranking"]["items"] = items
        result["ranking"]["count"] = len(items)
    elif items:
        result["ranking"]["data"] = items

    _out({"data": result}, args.pretty, args.raw, args.format)


def cmd_sector(args):
    """업종 조회."""
    client = _create_client()

    if args.all:
        data = client.get_all_sector_index()
        result = {"sector": {"type": "all"}}
        items = _extract_output(data, "output2") or _extract_output(data, "output")
        if items and isinstance(items, list):
            if not args.raw:
                items = [remap(item, SECTOR_INDEX) for item in items]
            result["sector"]["items"] = items
        elif items:
            result["sector"]["data"] = items
    else:
        code = args.code or "0001"
        data = client.get_sector_current_price(code)
        result = {"sector": {"code": code}}
        output = _extract_output(data)
        if output:
            mapped = remap(output, SECTOR_INDEX) if not args.raw else output
            result["sector"]["data"] = mapped

    _out({"data": result}, args.pretty, args.raw, args.format)


def cmd_investor(args):
    """투자자 매매동향 조회."""
    client = _create_client()
    code = args.code
    result = {"investor": {"code": code}}

    if args.institution:
        data = client.get_institutional_trading_trend(code)
    elif args.program:
        data = client.get_stock_program_trading(code)
    else:
        # 기본: 외국인 매매동향
        data = client.get_foreign_trading(code)

    output = _extract_output(data, "output2") or _extract_output(data, "output")
    if output:
        if isinstance(output, list):
            if not args.raw:
                output = [remap(item, INVESTOR_TREND) for item in output]
            result["investor"]["items"] = output
        else:
            result["investor"]["data"] = remap(output, INVESTOR_TREND) if not args.raw else output

    _out({"data": result}, args.pretty, args.raw, args.format)


def cmd_account(args):
    """계좌 정보 조회."""
    client = _create_client()

    account_funcs = {
        "balance": (client.get_balance_detail, "balance"),
        "deposit": (client.get_deposit_detail, "deposit"),
        "eval": (client.get_account_evaluation, "evaluation"),
        "orders": (client.get_unfilled_orders, "unfilledOrders"),
        "executed": (client.get_executed_orders, "executedOrders"),
        "profit": (client.get_realized_profit_detail, "profit"),
    }

    func_info = account_funcs.get(args.type)
    if not func_info:
        _out({"error": f"Unknown account type: {args.type}. Available: {', '.join(account_funcs.keys())}"})
        sys.exit(1)

    func, key = func_info
    data = func()
    result = {"account": {"type": args.type}}

    # 잔고는 output1 + output2 (보유종목) 구조
    if args.type == "balance":
        output1 = _extract_output(data, "output1") or _extract_output(data, "output")
        output2 = _extract_output(data, "output2")
        if output1:
            result["account"]["summary"] = remap(output1, ACCOUNT_BALANCE) if not args.raw else output1
        if output2 and isinstance(output2, list):
            if not args.raw:
                output2 = [remap(item, HOLDING) for item in output2]
            result["account"]["holdings"] = output2
    else:
        output = _extract_output(data, "output2") or _extract_output(data, "output")
        if output:
            result["account"][key] = output

    _out({"data": result}, args.pretty, args.raw, args.format)


def cmd_order(args):
    """주문 실행."""
    client = _create_client()

    if args.action == "cancel":
        order_no = args.order_no
        code = args.code
        qty = args.qty
        if not all([order_no, code, qty]):
            _out({"error": "cancel 명령: order_no, code, --qty 모두 필요"})
            sys.exit(1)

        # 확인 프롬프트
        if not args.yes:
            msg = f"주문취소: 주문번호={order_no}, 종목={code}, 수량={qty}"
            confirm = input(f"{msg}\n실행하시겠습니까? (y/N): ")
            if confirm.lower() != "y":
                _out({"cancelled": True, "message": "주문이 취소되었습니다."})
                return

        data = client.cancel_order(order_no, code, qty)
        _out({"data": {"order": {"action": "cancel", "result": data}}}, args.pretty, args.raw, args.format)
        return

    # buy / sell
    code = args.code
    qty = args.qty
    price = args.price or 0

    if not code or not qty:
        _out({"error": f"{args.action} 명령: code, --qty 필요"})
        sys.exit(1)

    # 확인 프롬프트
    if not args.yes:
        action_kr = "매수" if args.action == "buy" else "매도"
        price_str = f"{price:,}원" if price else "시장가"
        msg = f"{action_kr}: 종목={code}, 수량={qty}, 가격={price_str}"
        confirm = input(f"{msg}\n실행하시겠습니까? (y/N): ")
        if confirm.lower() != "y":
            _out({"cancelled": True, "message": "주문이 취소되었습니다."})
            return

    if args.action == "buy":
        data = client.buy_stock(code, qty, price)
    else:
        data = client.sell_stock(code, qty, price)

    _out({"data": {"order": {"action": args.action, "code": code, "result": data}}}, args.pretty, args.raw, args.format)


def cmd_query(args):
    """동적 API 호출 — kiwoom query <domain> <method> [key=value ...]"""
    client = _create_client()
    domain = args.domain
    method = args.method

    # key=value 인자 파싱
    kwargs = {}
    for kv in args.args:
        if "=" in kv:
            k, v = kv.split("=", 1)
            # 숫자 자동 변환
            if v.isdigit():
                v = int(v)
            kwargs[k] = v

    # 도메인 → API 객체 매핑
    targets = {
        "stock": client.stock,
        "chart": client.chart,
        "ranking": client.ranking,
        "account": client.account_api,
        "order": client.order_api,
        "sector": client.sector_api,
        "investor": client.investor_api,
        "program": client.program_api,
        "auth": client.auth,
        "client": client,
    }

    target = targets.get(domain)
    if not target:
        _out({"error": f"Unknown domain: {domain}", "available": list(targets.keys())})
        sys.exit(1)

    fn = getattr(target, method, None)
    if not fn or not callable(fn):
        methods = [
            m for m in dir(target)
            if not m.startswith("_") and callable(getattr(target, m, None))
        ]
        _out({"error": f"Unknown method: {domain}.{method}", "available": methods})
        sys.exit(1)

    try:
        result = fn(**kwargs)
        _out({"data": result}, args.pretty, args.raw, args.format)
    except Exception as e:
        _out({"error": str(e), "type": type(e).__name__})
        sys.exit(1)


def cmd_schema(args):
    """GraphQL SDL 스키마 출력."""
    type_name = getattr(args, "type_name", None)

    if args.json:
        types = list_types()
        print(json_output({"types": types}, pretty=True))
    else:
        print(get_schema(type_name))


def cmd_status(args):
    """연결 상태 및 통계 조회."""
    client = _create_client()
    result = {"status": {}}

    try:
        conn = client.verify_connection()
        result["status"]["connection"] = conn
    except Exception as e:
        result["status"]["connection"] = {"error": str(e)}

    try:
        stats = client.get_stats()
        result["status"]["stats"] = stats
    except Exception as e:
        result["status"]["stats"] = {"error": str(e)}

    _out({"data": result}, args.pretty, args.raw, args.format)


def cmd_token(args):
    """토큰 상태 조회."""
    client = _create_client()
    status = client.get_token_status()
    _out({"data": {"token": status}}, args.pretty, args.raw, args.format)


# ── 파서 빌드 ──


def _add_global_options(parser):
    """모든 서브커맨드에 공통 옵션 추가."""
    parser.add_argument("--pretty", "-p", action="store_true", help="들여쓰기된 JSON 출력")
    parser.add_argument("--raw", action="store_true", help="필드명 변환 없이 원본 출력")
    parser.add_argument("--format", choices=["json", "table"], default="json", help="출력 형식 (기본: json)")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="kiwoom",
        description="kiwoom CLI — LLM-friendly 키움증권 REST API",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
    sub = parser.add_subparsers(dest="command", help="명령")

    # ── price ──
    p = sub.add_parser("price", help="주식 현재가 조회")
    p.add_argument("code", help="종목코드 (예: 005930)")
    p.add_argument("--orderbook", action="store_true", help="호가 정보 포함")
    _add_global_options(p)

    # ── chart ──
    p = sub.add_parser("chart", help="차트 데이터 조회")
    p.add_argument("code", help="종목코드")
    p.add_argument("--minute", action="store_true", help="분봉 (기본 5분)")
    p.add_argument("--daily", action="store_true", help="일봉 (기본값)")
    p.add_argument("--weekly", action="store_true", help="주봉")
    p.add_argument("--monthly", action="store_true", help="월봉")
    p.add_argument("--yearly", action="store_true", help="년봉")
    p.add_argument("--interval", type=int, help="분봉 간격 (1,3,5,10,15,30,60)")
    p.add_argument("--from", dest="from_date", help="시작일 (YYYYMMDD)")
    p.add_argument("--to", dest="to_date", help="종료일 (YYYYMMDD)")
    p.add_argument("--count", type=int, default=100, help="조회 개수 (기본 100)")
    _add_global_options(p)

    # ── rank ──
    p = sub.add_parser("rank", help="순위 조회")
    p.add_argument("type", choices=["volume", "amount", "gainers", "foreign-buy", "surge"],
                    help="순위 종류")
    p.add_argument("--market", default="ALL", help="시장 (ALL, KOSPI, KOSDAQ)")
    _add_global_options(p)

    # ── sector ──
    p = sub.add_parser("sector", help="업종 정보 조회")
    p.add_argument("code", nargs="?", default=None, help="업종코드 (예: 0001)")
    p.add_argument("--all", action="store_true", help="전체 업종 지수")
    _add_global_options(p)

    # ── investor ──
    p = sub.add_parser("investor", help="투자자 매매동향 조회")
    p.add_argument("code", help="종목코드")
    p.add_argument("--foreign", action="store_true", help="외국인 매매 (기본값)")
    p.add_argument("--institution", action="store_true", help="기관 매매")
    p.add_argument("--program", action="store_true", help="프로그램 매매")
    _add_global_options(p)

    # ── account ──
    p = sub.add_parser("account", help="계좌 정보 조회")
    p.add_argument("type", choices=["balance", "deposit", "eval", "orders", "executed", "profit"],
                    help="조회 종류")
    _add_global_options(p)

    # ── order ──
    p = sub.add_parser("order", help="주문 실행")
    p.add_argument("action", choices=["buy", "sell", "cancel"], help="주문 종류")
    p.add_argument("code", nargs="?", help="종목코드 (buy/sell) 또는 주문번호 (cancel)")
    p.add_argument("--qty", type=int, help="수량")
    p.add_argument("--price", type=int, help="가격 (미입력시 시장가)")
    p.add_argument("--yes", "-y", action="store_true", help="확인 없이 실행")
    # cancel 전용
    p.add_argument("--order-no", dest="order_no", help="취소할 주문번호")
    _add_global_options(p)

    # ── query ──
    p = sub.add_parser("query", help="API 직접 호출 (동적 디스패치)")
    p.add_argument("domain", help="도메인 (stock, chart, ranking, account, ...)")
    p.add_argument("method", help="메서드명")
    p.add_argument("args", nargs="*", help="인자 (key=value 형식)")
    _add_global_options(p)

    # ── schema ──
    p = sub.add_parser("schema", help="API 스키마 조회 (LLM introspection)")
    p.add_argument("type_name", nargs="?", default=None, help="특정 타입 (예: Stock, Chart)")
    p.add_argument("--json", action="store_true", help="타입 목록을 JSON으로 출력")
    _add_global_options(p)

    # ── status ──
    p = sub.add_parser("status", help="연결 상태 및 통계")
    _add_global_options(p)

    # ── token ──
    p = sub.add_parser("token", help="토큰 상태 조회")
    _add_global_options(p)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not getattr(args, "command", None):
        parser.print_help()
        sys.exit(0)

    handlers = {
        "price": cmd_price,
        "chart": cmd_chart,
        "rank": cmd_rank,
        "sector": cmd_sector,
        "investor": cmd_investor,
        "account": cmd_account,
        "order": cmd_order,
        "query": cmd_query,
        "schema": cmd_schema,
        "status": cmd_status,
        "token": cmd_token,
    }

    handler = handlers.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
