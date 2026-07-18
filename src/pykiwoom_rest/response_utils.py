"""
Response normalization utilities to unify returned structures.
원시 JSON 응답을 보존하면서 기본 키와 메타데이터를 일관되게 부여합니다.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

SIGN_CODE_MAP = {
    "0": "unchanged",
    "1": "limit_up",
    "2": "up",
    "3": "unchanged",
    "4": "limit_down",
    "5": "down",
}

SIGN_CODE_ALIASES = {
    "limit_up": 1,
    "up": 1,
    "unchanged": 0,
    "flat": 0,
    "same": 0,
    "limit_down": -1,
    "down": -1,
}

SIGN_CODE_FIELDS = {"pre_sig", "pred_pre_sig", "prdy_vrss_sign", "sign"}
CHANGE_FIELDS = {"pre", "pred_pre", "prdy_vrss", "stck_prdy_vrss", "bstp_nmix_prdy_vrss"}
SECTOR_INDEX_TR_CODES = {
    "ka20004",
    "ka20005",
    "ka20006",
    "ka20007",
    "ka20008",
    "ka20019",
}
SECTOR_DECIMAL_INDEX_TR_CODES = {"ka20001", "ka20003", "ka20009"}
INDEX_PRICE_FIELDS = {
    "cur_prc",
    "open_pric",
    "high_pric",
    "low_pric",
    "bstp_nmix_prpr",
    "bstp_nmix_oprc",
    "bstp_nmix_hgpr",
    "bstp_nmix_lwpr",
}
PRICE_FIELDS = {
    "cur_prc",
    "open_pric",
    "high_pric",
    "low_pric",
    "close_pric",
    "base_pric",
    "upl_pric",
    "lst_pric",
    "exp_cntr_pric",
    "repl_pric",
    "stck_prpr",
    "stck_oprc",
    "stck_hgpr",
    "stck_lwpr",
    "stck_clpr",
    "prpr",
    "oprc",
    "hgpr",
    "lwpr",
    "opn_prc",
    "hgh_prc",
    "low_prc",
    "cls_prc",
    "avg_pric",
    "pchs_avg_pric",
    "pur_pric",
    "pred_close_pric",
    "250hgst",
    "250lwst",
    "oyr_hgst",
    "oyr_lwst",
    "sel_fpr_bid",
    "buy_fpr_bid",
    "pri_sel_bid_unit",
    "pri_buy_bid_unit",
}
FLOAT_FIELDS = {"per", "pbr", "roe", "ev", "eps", "bps", "mac_wght", "cntr_str"}
ABSOLUTE_QUANTITY_FIELDS = {
    "trde_qty",
    "pred_trde_qty",
    "acc_trde_qty",
    "bf_mkrt_trde_qty",
    "opmr_trde_qty",
    "af_mkrt_trde_qty",
    "prid_trde_qty",
    "dt_trde_qty",
    "shrts_qty",
    "ovr_shrts_qty",
    "cntr_qty",
    "exp_cntr_qty",
    "rmnd_qty",
    "trde_able_qty",
    "hldg_qty",
    "ord_psbl_qty",
    "ord_qty",
    "tot_ccld_qty",
    "poss_stkcnt",
    "gain_pos_stkcnt",
    "frgnr_limit",
    "for_poss",
}
SIGNED_QUANTITY_FIELDS = {
    "chg_qty",
    "cntr_trde_qty",
    "netprps_qty",
    "netprps_irds",
    "prev_pot_netprps_qty",
    "buy_qty",
    "buy_qty_irds",
    "sell_qty",
    "sell_qty_irds",
    "netslmt_qty",
    "prsn_ntby_qty",
    "frgn_ntby_qty",
    "orgn_ntby_qty",
    "inst_ntby_qty",
    "dfrt_trst_netprps_qty",
    "ndiffpro_trst_netprps_qty",
    "all_dfrt_trst_netprps_qty",
    "for_netprps_qty",
    "orgn_netprps_qty",
    "ind_netprps_qty",
    "prm_netprps_qty",
    "prm_netprps_qty_irds",
    "frgnr_limit_irds",
}
SIGNED_AMOUNT_FIELDS = {
    "tot_evlt_pl",
    "tot_evltv_prft",
    "evltv_prft",
    "evlu_pfls_smtl",
    "evlu_pfls_smtl_amt",
    "evlu_pfls_amt",
    "netslmt_amt",
    "dfrt_trst_netprps_amt",
    "ndiffpro_trst_netprps_amt",
    "all_dfrt_trst_netprps_amt",
    "d1_slby_exct_amt",
    "d2_slby_exct_amt",
    "for_netprps",
    "orgn_netprps",
    "ind_netprps",
    "netprps_amt",
    "prev_netprps_amt",
    "netprps_amt_irds",
    "netprps_prica",
    "for_netprps_amt",
    "orgn_netprps_amt",
    "ind_netprps_amt",
    "prm_netprps_amt",
    "prm_netprps_amt_irds",
}
MONETARY_AMOUNT_FIELDS = {
    "amt",
    "amount",
    "trde_prica",
    "trde_pre",
    "acc_trde_prica",
    "bf_mkrt_trde_prica",
    "opmr_trde_prica",
    "af_mkrt_trde_prica",
    "acml_vol",
    "acml_tr_pbmn",
    "trd_vol",
    "trd_amt",
    "volume",
    "mac",
    "cap",
    "fav",
    "flo_stk",
    "dstr_stk",
    "sale_amt",
    "bus_pro",
    "cup_nga",
    "tot_pur_amt",
    "tot_buy_amt",
    "tot_evlt_amt",
    "prsm_dpst_aset_amt",
    "tot_loan_amt",
    "tot_crd_loan_amt",
    "tot_crd_ls_amt",
    "pur_amt",
    "evlt_amt",
    "pur_cmsn",
    "sell_cmsn",
    "tax",
    "sum_cmsn",
    "dbst_bal",
    "day_stk_asst",
    "pchs_amt",
    "pchs_amt_smtl",
    "evlu_amt",
    "evlu_amt_smtl",
    "dnca_tot_amt",
    "scts_evlu_amt",
    "tot_evlu_amt",
    "d2_auto_rdpt_amt",
}
NON_NUMERIC_FIELDS = {
    "rt_cd",
    "msg1",
    "msg",
    "stk_cd",
    "stk_nm",
    "pdno",
    "mksc_shrn_iscd",
    "hts_kor_isnm",
    "dt",
    "date",
    "tm",
    "time",
    "cntr_tm",
    "stck_bsop_date",
    "stck_cntg_hour",
    "sect_cd",
    "inds_cd",
    "bstp_cls_code",
    "bstp_cls_nm",
    "metadata",
    "header",
}


def _numeric_text(value: Any) -> str:
    if value is None:
        raise ValueError("missing numeric value")
    text = str(value).replace(",", "").replace("%", "").strip()
    if text == "":
        raise ValueError("missing numeric value")
    return text


def _split_leading_signs(text: str) -> tuple[int, str]:
    index = 0
    while index < len(text) and text[index] in "+-":
        index += 1

    sign_text = text[:index]
    number_text = text[index:]
    if number_text == "":
        raise ValueError("missing numeric value")

    sign = -1 if "-" in sign_text else 1
    return sign, number_text


def _to_float(value: Any) -> float:
    sign, number_text = _split_leading_signs(_numeric_text(value))
    return sign * float(number_text)


def _to_signed_int(value: Any) -> int:
    return int(_to_float(value))


def _parse_numeric(value: Any) -> float | None:
    """호환용 숫자 파서: 잘못된 입력은 ``None``으로 표현한다."""
    try:
        return _to_float(value)
    except (TypeError, ValueError):
        return None


def clean_price(value: Any) -> int:
    """부호와 쉼표를 제거한 가격 정수로 변환합니다."""
    parsed = _parse_numeric(value)
    return abs(int(parsed)) if parsed is not None else 0


def clean_rate(value: Any) -> float:
    """등락률/비율 문자열을 부호 보존 float로 변환합니다."""
    parsed = _parse_numeric(value)
    return parsed if parsed is not None else 0.0


def clean_signed_number(value: Any) -> int:
    """순매수/손익처럼 방향이 있는 정수값을 부호 보존 정수로 변환합니다."""
    return _to_signed_int(value)


def clean_signed_quantity(value: Any) -> int:
    """순매수/변동처럼 방향이 있는 수량을 부호 보존 정수로 변환합니다."""
    return clean_signed_number(value)


def clean_index_price(value: Any) -> float:
    """업종/지수 x100 가격 인코딩을 실제 지수값으로 변환합니다."""
    if isinstance(value, float):
        return abs(value)
    text = _numeric_text(value)
    if "." in text:
        return abs(_to_float(value))
    return clean_price(value) / 100


def clean_decimal_price(value: Any) -> float:
    """이미 소수 실값인 가격 문자열의 부호 접두사만 제거합니다."""
    return abs(_to_float(value))


def interpret_sign_code(code: Any) -> str:
    """전일대비 기호 코드를 안정적인 문자열 라벨로 변환합니다."""
    return SIGN_CODE_MAP.get(str(code).strip(), "unknown")


def signed_change(change: Any, sign_code: Any = None) -> int:
    """대비기호를 기준으로 실제 부호가 있는 등락값을 계산합니다."""
    if sign_code in (None, ""):
        return _to_signed_int(change)

    code = str(sign_code).strip()
    direction = SIGN_CODE_ALIASES.get(code, SIGN_CODE_ALIASES.get(SIGN_CODE_MAP.get(code, "")))
    if direction is None:
        raise ValueError(f"unknown Kiwoom sign code: {sign_code!r}")
    if direction == 0:
        return 0
    return clean_price(change) * direction


def _signed_decimal_change(change: Any, sign_code: Any = None) -> float:
    if sign_code in (None, ""):
        return _to_float(change)

    code = str(sign_code).strip()
    direction = SIGN_CODE_ALIASES.get(code, SIGN_CODE_ALIASES.get(SIGN_CODE_MAP.get(code, "")))
    if direction is None:
        return _to_float(change)
    if direction == 0:
        return 0.0
    return clean_decimal_price(change) * direction


def normalize_data_values(
    data: Any,
    *,
    tr_code: str | None = None,
    endpoint: str | None = None,
    sector_index: bool = False,
) -> Any:
    """Kiwoom 숫자 문자열을 필드 의미에 맞는 Python 값으로 정규화합니다."""
    endpoint_text = str(endpoint or "").lower()
    tr_code_text = str(tr_code or "").lower()
    is_sector_index = sector_index or tr_code_text in SECTOR_INDEX_TR_CODES or any(
        term in endpoint_text for term in ("sector", "index", "inds")
    )
    is_decimal_sector_index = tr_code in SECTOR_DECIMAL_INDEX_TR_CODES
    return _normalize_node(
        data,
        is_sector_index=is_sector_index,
        is_decimal_sector_index=is_decimal_sector_index,
        endpoint=endpoint,
    )


def _normalize_node(
    data: Any,
    *,
    is_sector_index: bool,
    is_decimal_sector_index: bool,
    endpoint: str | None,
) -> Any:
    if isinstance(data, list):
        return [
            _normalize_node(
                item,
                is_sector_index=is_sector_index,
                is_decimal_sector_index=is_decimal_sector_index,
                endpoint=endpoint,
            )
            for item in data
        ]
    if not isinstance(data, dict):
        return data

    normalized: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, (dict, list)):
            normalized[key] = _normalize_node(
                value,
                is_sector_index=is_sector_index,
                is_decimal_sector_index=is_decimal_sector_index,
                endpoint=endpoint,
            )
            continue
        normalized[key] = _normalize_scalar(
            key,
            value,
            row=data,
            is_sector_index=is_sector_index,
            is_decimal_sector_index=is_decimal_sector_index,
        )
        if _normalization_key(key) in SIGN_CODE_FIELDS:
            normalized[f"{key}_meaning"] = interpret_sign_code(value)
    return normalized


def _normalize_scalar(
    key: str,
    value: Any,
    *,
    row: dict[str, Any],
    is_sector_index: bool,
    is_decimal_sector_index: bool,
) -> Any:
    normalized_key = _normalization_key(key)
    if normalized_key in NON_NUMERIC_FIELDS:
        return value
    if value is None or (isinstance(value, str) and not value.strip()):
        return value

    try:
        if normalized_key in SIGN_CODE_FIELDS:
            return interpret_sign_code(value)
        if normalized_key in CHANGE_FIELDS:
            return _normalize_change(
                normalized_key,
                value,
                row,
                original_key=key,
                is_sector_index=is_sector_index,
                is_decimal_sector_index=is_decimal_sector_index,
            )
        if is_sector_index and normalized_key in INDEX_PRICE_FIELDS:
            return clean_index_price(value)
        if is_decimal_sector_index and normalized_key in INDEX_PRICE_FIELDS:
            return clean_decimal_price(value)
        if normalized_key in PRICE_FIELDS or _is_orderbook_price_field(normalized_key):
            return clean_price(value)
        if normalized_key in FLOAT_FIELDS:
            return clean_rate(value)
        if _is_rate_field(normalized_key):
            return clean_rate(value)
        if (
            normalized_key in SIGNED_QUANTITY_FIELDS
            or _is_orderbook_quantity_change_field(normalized_key)
            or _is_signed_net_purchase_quantity_field(normalized_key)
        ):
            return clean_signed_quantity(value)
        if normalized_key in SIGNED_AMOUNT_FIELDS or _is_signed_net_purchase_amount_field(
            normalized_key
        ):
            return clean_signed_number(value)
        if (
            normalized_key in ABSOLUTE_QUANTITY_FIELDS
            or normalized_key in MONETARY_AMOUNT_FIELDS
            or _is_orderbook_quantity_field(normalized_key)
            or _is_trader_volume_rank_field(normalized_key)
        ):
            return clean_price(value)
    except (TypeError, ValueError):
        return value

    return value


def _normalization_key(key: str) -> str:
    if key.endswith("_n"):
        base_key = key[:-2]
        if _is_normalizable_key(base_key):
            return base_key
    return key


def _is_normalizable_key(key: str) -> bool:
    return (
        key in NON_NUMERIC_FIELDS
        or key in SIGN_CODE_FIELDS
        or key in CHANGE_FIELDS
        or key in INDEX_PRICE_FIELDS
        or key in PRICE_FIELDS
        or key in FLOAT_FIELDS
        or key in SIGNED_QUANTITY_FIELDS
        or key in SIGNED_AMOUNT_FIELDS
        or key in ABSOLUTE_QUANTITY_FIELDS
        or key in MONETARY_AMOUNT_FIELDS
        or _is_rate_field(key)
        or _is_orderbook_price_field(key)
        or _is_orderbook_quantity_change_field(key)
        or _is_signed_net_purchase_quantity_field(key)
        or _is_signed_net_purchase_amount_field(key)
        or _is_orderbook_quantity_field(key)
        or _is_trader_volume_rank_field(key)
    )


def _normalize_change(
    key: str,
    value: Any,
    row: dict[str, Any],
    *,
    original_key: str,
    is_sector_index: bool,
    is_decimal_sector_index: bool,
):
    sign_code = _find_change_sign_code(row, original_key)
    if is_decimal_sector_index:
        return _signed_decimal_change(value, sign_code)

    change = signed_change(value, sign_code)
    if is_sector_index or key == "bstp_nmix_prdy_vrss":
        return change / 100
    return change


def _find_change_sign_code(row: dict[str, Any], original_key: str) -> Any:
    suffix = "_n" if original_key.endswith("_n") else ""
    for sign_key in ("pred_pre_sig", "pre_sig", "prdy_vrss_sign", "sign"):
        suffixed_key = f"{sign_key}{suffix}"
        if suffix and suffixed_key in row:
            return row.get(suffixed_key)
        if sign_key in row:
            return row.get(sign_key)
    return None


def _is_rate_field(key: str) -> bool:
    if key == "rt_cd":
        return False
    return (
        key == "wght"
        or key.endswith("_rt")
        or key.endswith("_rate")
        or key.endswith("_wght")
        or "ctrt" in key
    )


def _is_sector_index_response(endpoint: str | None, tr_code: str | None) -> bool:
    endpoint_text = str(endpoint or "").lower()
    return str(tr_code or "").lower() in SECTOR_INDEX_TR_CODES or any(
        term in endpoint_text for term in ("sector", "index", "inds")
    )


def _is_orderbook_price_field(key: str) -> bool:
    if key.startswith(("askp", "bidp")) and "rsqn" not in key:
        return key[4:].isdigit()
    return key.startswith(("sel_", "buy_")) and key.endswith("_bid")


def _is_orderbook_quantity_field(key: str) -> bool:
    if key in {
        "total_askp_rsqn",
        "total_bidp_rsqn",
        "sel_fpr_req",
        "buy_fpr_req",
        "tot_sel_req",
        "tot_buy_req",
        "ovt_sel_req",
        "ovt_buy_req",
    }:
        return True
    for prefix in ("askp_rsqn", "bidp_rsqn"):
        if key.startswith(prefix) and key[len(prefix) :].isdigit():
            return True
    return key.startswith(("sel_", "buy_")) and key.endswith("_pre_req")


def _is_orderbook_quantity_change_field(key: str) -> bool:
    if key in {
        "tot_sel_req_jub_pre",
        "tot_buy_req_jub_pre",
        "ovt_sel_req_pre",
        "ovt_buy_req_pre",
    }:
        return True
    return key.startswith(("sel_", "buy_")) and key.endswith("_req_pre")


def _is_signed_net_purchase_quantity_field(key: str) -> bool:
    return key.endswith(("_netprps_qty", "_netprps_qty_irds"))


def _is_signed_net_purchase_amount_field(key: str) -> bool:
    return key.endswith(("_netprps", "_netprps_amt", "_netprps_amt_irds", "_netprps_prica"))


def _is_trader_volume_rank_field(key: str) -> bool:
    for prefix in ("sel_trde_qty_", "buy_trde_qty_"):
        if key.startswith(prefix) and key[len(prefix) :].isdigit():
            return True
    return False


def normalize_response(
    data: dict[str, Any],
    *,
    tr_code: str | None = None,
    endpoint: str | None = None,
    processing_time: float | None = None,
    headers: dict[str, Any] | None = None,
    normalize_data: bool = False,
) -> dict[str, Any]:
    """
    Ensure unified response structure while preserving original payload.

    - Guarantees presence of keys: 'rt_cd', 'msg1'
    - Adds 'metadata' block with timestamp, tr_code, endpoint, processing_time
    - Does not alter existing keys/values
    """
    if not isinstance(data, dict):
        # Non-dict JSON (rare) -> wrap into dict
        data = {"data": data}

    # 기본값은 원본 보존이며, 호출자가 요청한 경우에만 숫자 필드를 정규화한다.
    out: dict[str, Any] = dict(data)
    if normalize_data:
        out = normalize_data_values(out, tr_code=tr_code, endpoint=endpoint)

    # Provide defaults if missing
    if "rt_cd" not in out:
        # If server returned explicit error field, set failure, else success
        out["rt_cd"] = "1" if "error" in out else "0"
    if "msg1" not in out:
        out["msg1"] = "SUCCESS" if out.get("rt_cd") == "0" else out.get("msg", "ERROR")

    # Attach metadata non-destructively
    meta = out.get("metadata", {}) if isinstance(out.get("metadata"), dict) else {}
    meta_update = {
        "timestamp": datetime.now().isoformat(),
        "tr_code": tr_code,
        "endpoint": endpoint,
        "processing_time": processing_time,
    }
    # Only set missing metadata fields
    for k, v in meta_update.items():
        if k not in meta or meta[k] is None:
            meta[k] = v
    out["metadata"] = meta

    return out
