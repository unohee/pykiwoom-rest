"""
kiwoom CLI — LLM-friendly 키움증권 REST API
진입점: kiwoom <command> [options]
"""

import argparse
import sys
from datetime import datetime, timedelta

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
)
from .formatters import json_output, table_output
from .schema import SchemaTypeNotFound, get_schema, list_types

# ── 장 상태 캐시 (세션당 1회 체크) ──

_market_status = {
    "checked": False,
    "is_holiday": None,
    "last_business_day": None,
    "notice": None,
}

RESPONSE_META_KEYS = {"rt_cd", "msg1", "return_code", "return_msg", "metadata", "header"}
ACCOUNT_HOLDINGS_KEYS = ("output2", "acnt_evlt_remn_indv_tot")
SAFE_QUERY_DOMAINS = ("stock", "chart", "ranking", "account", "sector", "investor", "program")
SAFE_QUERY_METHOD_PREFIXES = ("get_", "list_", "search_")
DANGEROUS_QUERY_METHOD_NAMES = {
    "buy_stock",
    "sell_stock",
    "cancel_order",
    "get_access_token",
    "refresh_token",
    "revoke_token",
}
DANGEROUS_QUERY_METHOD_PREFIXES = (
    "buy_",
    "sell_",
    "cancel_",
    "order_",
    "place_",
    "revoke_",
    "refresh_",
)
CHART_COUNT_MAX = 1000


def _positive_int_arg(value):
    """argparse용 양의 정수 파서."""
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("must be a positive integer") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def _chart_count_arg(value):
    """argparse용 차트 count 파서."""
    parsed = _positive_int_arg(value)
    if parsed > CHART_COUNT_MAX:
        raise argparse.ArgumentTypeError(f"must be between 1 and {CHART_COUNT_MAX}")
    return parsed


def _non_negative_int_arg(value):
    """argparse용 0 이상 정수 파서."""
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("must be a non-negative integer") from exc
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be a non-negative integer")
    return parsed


def _exit_error(args, payload):
    """CLI 오류를 JSON/table 옵션에 맞춰 출력하고 종료."""
    if isinstance(payload, str):
        payload = {"error": payload}
    _out(payload, getattr(args, "pretty", False), False, getattr(args, "format", "json"))
    sys.exit(1)


def _validate_positive_int(name, value, args):
    if value is None:
        _exit_error(args, f"{name} must be a positive integer")
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        _exit_error(args, f"{name} must be a positive integer")
    if parsed <= 0:
        _exit_error(args, f"{name} must be a positive integer")
    return parsed


def _validate_non_negative_int(name, value, args):
    if value is None:
        return 0
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        _exit_error(args, f"{name} must be a non-negative integer")
    if parsed < 0:
        _exit_error(args, f"{name} must be a non-negative integer")
    return parsed


def _validate_chart_count(value, args):
    parsed = _validate_positive_int("--count", value, args)
    if parsed > CHART_COUNT_MAX:
        _exit_error(args, f"--count must be between 1 and {CHART_COUNT_MAX}")
    return parsed


def _is_safe_query_method(method_name):
    if method_name.startswith("_"):
        return False
    if method_name in DANGEROUS_QUERY_METHOD_NAMES:
        return False
    if method_name.startswith(DANGEROUS_QUERY_METHOD_PREFIXES):
        return False
    return method_name.startswith(SAFE_QUERY_METHOD_PREFIXES)


def _safe_query_methods(target):
    return sorted(
        method_name
        for method_name in dir(target)
        if _is_safe_query_method(method_name) and callable(getattr(target, method_name, None))
    )


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
        # 테이블 출력: 재귀적으로 첫 번째 리스트 탐색
        def _find_table_data(obj, depth=0):
            if depth > 3:
                return None
            if isinstance(obj, list) and obj and isinstance(obj[0], dict):
                return obj
            if isinstance(obj, dict):
                for v in obj.values():
                    found = _find_table_data(v, depth + 1)
                    if found:
                        return found
            return None

        table_data = _find_table_data(data)
        if table_data:
            if notice:
                print(f"# {notice}")
            print(table_output(table_data))
        else:
            # 리스트 없으면 가장 깊은 단일 dict 출력
            def _find_deepest_dict(obj, depth=0):
                if depth > 4 or not isinstance(obj, dict):
                    return obj
                for v in obj.values():
                    if isinstance(v, dict) and not any(
                        isinstance(vv, (dict, list)) for vv in v.values()
                    ):
                        return v
                for v in obj.values():
                    if isinstance(v, dict):
                        return _find_deepest_dict(v, depth + 1)
                return obj

            inner = _find_deepest_dict(data)
            if notice:
                print(f"# {notice}")
            print(table_output(inner))
    else:
        print(json_output(data, pretty))


def _extract_output(data, key="output"):
    """API 응답에서 데이터 추출.

    키움 API 응답은 3가지 형태:
    1. {"output": {...}} — 중첩 구조
    2. {"output2": [...]} — 리스트 데이터 (차트, 순위)
    3. {"stk_cd": "005930", ...} — 플랫 구조 (대부분)

    key가 존재하면 해당 키 반환, 없으면 메타데이터 제외 후 응답 자체 반환.
    """
    if not data or not isinstance(data, dict):
        return None
    if key in data:
        return data[key]
    # 플랫 구조: 메타데이터 키 제외하고 응답 자체를 반환
    if key == "output":
        filtered = {k: v for k, v in data.items() if k not in RESPONSE_META_KEYS}
        return filtered if filtered else None
    return None


def _split_account_balance(data):
    """kt00018 잔고 응답을 요약 dict와 보유종목 list로 분리."""
    if not data or not isinstance(data, dict):
        return None, None

    output1 = _extract_output(data, "output1")
    output2 = _extract_output(data, "output2")
    if isinstance(output1, dict) or isinstance(output2, list):
        return output1, output2

    container = _extract_output(data, "output")
    if not isinstance(container, dict):
        container = data

    holdings = None
    for key in ACCOUNT_HOLDINGS_KEYS:
        value = container.get(key)
        if isinstance(value, list):
            holdings = value
            break

    summary = {
        key: value
        for key, value in container.items()
        if key not in RESPONSE_META_KEYS and key not in ACCOUNT_HOLDINGS_KEYS
    }
    return summary or None, holdings


def _find_list_in_response(data):
    """응답에서 첫 번째 리스트 데이터를 자동 탐색.

    키움 차트/순위 응답은 중첩 키 안에 리스트가 있는 경우가 많음:
    예: {"stk_cd": "005930", "stk_dt_pole_chart_qry": [{...}, ...]}
    """
    if not data or not isinstance(data, dict):
        return None
    # output2 우선
    if "output2" in data and isinstance(data["output2"], list):
        return data["output2"]
    # 값 중 리스트 탐색 (메타데이터 제외)
    for k, v in data.items():
        if k not in RESPONSE_META_KEYS and isinstance(v, list) and v and isinstance(v[0], dict):
            return v
    return None


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
    code = args.code

    from_date = getattr(args, "from_date", None)
    to_date = getattr(args, "to_date", None)
    count = _validate_chart_count(getattr(args, "count", 100), args)
    client = _create_client()

    # 차트 타입 결정
    if args.minute:
        interval = args.interval or 5
        data = client.get_minute_chart(code, interval, from_date, to_date, count)
        chart_type = f"minute_{interval}"
    elif args.weekly:
        data = client.get_weekly_chart(code, from_date, to_date, count)
        chart_type = "weekly"
    elif args.monthly:
        data = client.get_monthly_chart(code, from_date, to_date, count)
        chart_type = "monthly"
    elif args.yearly:
        data = client.get_yearly_chart(code, from_date, to_date, count)
        chart_type = "yearly"
    else:
        # 기본값: 일봉
        data = client.get_daily_chart(code, from_date, to_date, count)
        chart_type = "daily"

    result = {"chart": {"code": code, "type": chart_type}}

    # 차트 데이터 추출: output2 → 중첩 리스트 자동 탐색
    items = _extract_output(data, "output2") or _find_list_in_response(data)
    if items and isinstance(items, list):
        if not args.raw:
            items = [remap(item, CHART_PRICE) for item in items]
        if len(items) > count:
            items = items[:count]
        result["chart"]["data"] = items
        result["chart"]["count"] = len(items)
    else:
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
        _out(
            {"error": f"Unknown rank type: {args.type}. Available: {', '.join(rank_funcs.keys())}"}
        )
        sys.exit(1)

    data = func()
    result = {"ranking": {"type": args.type, "market": market}}

    items = _extract_output(data, "output2") or _find_list_in_response(data)
    if items and isinstance(items, list):
        if not args.raw:
            items = [remap(item, RANKING) for item in items]
        result["ranking"]["items"] = items
        result["ranking"]["count"] = len(items)
    else:
        output = _extract_output(data)
        if output:
            result["ranking"]["data"] = output

    _out({"data": result}, args.pretty, args.raw, args.format)


def cmd_sector(args):
    """업종 조회."""
    client = _create_client()

    if args.all:
        data = client.get_all_sector_index()
        result = {"sector": {"type": "all"}}
        items = _extract_output(data, "output2") or _find_list_in_response(data)
        if items and isinstance(items, list):
            if not args.raw:
                items = [remap(item, SECTOR_INDEX) for item in items]
            result["sector"]["items"] = items
        else:
            output = _extract_output(data)
            if output:
                result["sector"]["data"] = output
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

    items = _extract_output(data, "output2") or _find_list_in_response(data)
    if items and isinstance(items, list):
        if not args.raw:
            items = [remap(item, INVESTOR_TREND) for item in items]
        result["investor"]["items"] = items
    else:
        output = _extract_output(data)
        if output:
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
        _out(
            {
                "error": f"Unknown account type: {args.type}. Available: {', '.join(account_funcs.keys())}"
            }
        )
        sys.exit(1)

    func, key = func_info
    data = func()
    result = {"account": {"type": args.type}}

    # 잔고는 output1 + output2 (보유종목) 구조
    if args.type == "balance":
        summary, output2 = _split_account_balance(data)
        if summary:
            result["account"]["summary"] = (
                remap(summary, ACCOUNT_BALANCE) if not args.raw else summary
            )
        if output2:
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
    if args.action == "cancel":
        order_no = args.order_no
        code = args.code
        qty = _validate_positive_int("--qty", args.qty, args)
        if not order_no or not code:
            _exit_error(args, "cancel 명령: code, --order-no, --qty 모두 필요")

        client = _create_client()

        # 확인 프롬프트
        if not args.yes:
            msg = f"주문취소: 주문번호={order_no}, 종목={code}, 수량={qty}"
            confirm = input(f"{msg}\n실행하시겠습니까? (y/N): ")
            if confirm.lower() != "y":
                _out({"cancelled": True, "message": "주문이 취소되었습니다."})
                return

        data = client.cancel_order(order_no, code, qty)
        _out(
            {"data": {"order": {"action": "cancel", "result": data}}},
            args.pretty,
            args.raw,
            args.format,
        )
        return

    # buy / sell
    code = args.code
    if not code:
        _exit_error(args, f"{args.action} 명령: code, --qty 필요")
    qty = _validate_positive_int("--qty", args.qty, args)
    price = _validate_non_negative_int("--price", args.price, args)
    client = _create_client()

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

    _out(
        {"data": {"order": {"action": args.action, "code": code, "result": data}}},
        args.pretty,
        args.raw,
        args.format,
    )


def cmd_query(args):
    """동적 API 호출 — kiwoom query <domain> <method> [key=value ...]"""
    domain = args.domain
    method = args.method

    if domain not in SAFE_QUERY_DOMAINS:
        _exit_error(
            args,
            {
                "error": f"Unsupported query domain: {domain}",
                "available": list(SAFE_QUERY_DOMAINS),
            },
        )

    # key=value 인자 파싱
    kwargs = {}
    for kv in args.args:
        if "=" in kv:
            k, v = kv.split("=", 1)
            # 문자열 그대로 전달 (종목코드 '005930' 등 보존)
            kwargs[k] = v

    client = _create_client()

    # 도메인 → API 객체 매핑
    targets = {
        "stock": client.stock,
        "chart": client.chart,
        "ranking": client.ranking,
        "account": client.account_api,
        "sector": client.sector_api,
        "investor": client.investor_api,
        "program": client.program_api,
    }

    target = targets[domain]
    available_methods = _safe_query_methods(target)

    if not _is_safe_query_method(method):
        _exit_error(
            args,
            {
                "error": f"Unsafe or unsupported query method: {domain}.{method}",
                "available": available_methods,
            },
        )

    fn = getattr(target, method, None)
    if not fn or not callable(fn):
        _exit_error(
            args,
            {"error": f"Unknown method: {domain}.{method}", "available": available_methods},
        )

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
        try:
            print(get_schema(type_name))
        except SchemaTypeNotFound as e:
            print(
                json_output({"error": str(e), "available": e.available}, pretty=True),
                file=sys.stderr,
            )
            sys.exit(1)


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
    parser.add_argument(
        "--format", choices=["json", "table"], default="json", help="출력 형식 (기본: json)"
    )


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
    p.add_argument(
        "--count", type=_chart_count_arg, default=100, help="조회 개수 (1-1000, 기본 100)"
    )
    _add_global_options(p)

    # ── rank ──
    p = sub.add_parser("rank", help="순위 조회")
    p.add_argument(
        "type", choices=["volume", "amount", "gainers", "foreign-buy", "surge"], help="순위 종류"
    )
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
    p.add_argument(
        "type",
        choices=["balance", "deposit", "eval", "orders", "executed", "profit"],
        help="조회 종류",
    )
    _add_global_options(p)

    # ── order ──
    p = sub.add_parser("order", help="주문 실행")
    p.add_argument("action", choices=["buy", "sell", "cancel"], help="주문 종류")
    p.add_argument("code", nargs="?", help="종목코드")
    p.add_argument("--qty", type=_positive_int_arg, help="수량")
    p.add_argument("--price", type=_non_negative_int_arg, help="가격 (미입력시 시장가)")
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
