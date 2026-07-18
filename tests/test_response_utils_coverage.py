from pykiwoom_rest.response_utils import (
    _is_sector_index_response,
    _parse_numeric,
    clean_index_price,
    clean_price,
    clean_rate,
    interpret_sign_code,
    normalize_data_values,
    normalize_response,
    signed_change,
)


def test_numeric_helpers_handle_empty_invalid_and_signed_values():
    assert _parse_numeric(None) is None
    assert _parse_numeric("-") is None
    assert _parse_numeric(".") is None
    assert _parse_numeric("not-a-number") is None
    assert clean_price("-1,234.9") == 1234
    assert clean_price(None) == 0
    assert clean_rate("+1,234.5") == 1234.5
    assert clean_rate("-") == 0.0
    assert clean_index_price("+1234") == 12.34


def test_sign_helpers_cover_each_meaning_and_unknown_code():
    assert interpret_sign_code(" 1 ") == "limit_up"
    assert interpret_sign_code(2) == "up"
    assert interpret_sign_code("3") == "unchanged"
    assert interpret_sign_code("4") == "limit_down"
    assert interpret_sign_code("5") == "down"
    assert interpret_sign_code("x") == "unknown"
    assert signed_change("1,000", "1") == 1000
    assert signed_change("1,000", "5") == -1000
    assert signed_change("1,000", "3") == 0

    try:
        signed_change("1,000", "x")
    except ValueError as error:
        assert "unknown Kiwoom sign code" in str(error)
    else:
        raise AssertionError("unknown sign code must fail")


def test_normalize_data_values_handles_nested_values_and_bad_signed_value():
    payload = {
        "pred_pre_sig": "2",
        "pred_pre": "-20",
        "cur_prc": "-1,200",
        "flu_rt": "+1.25",
        "volume": "1,500",
        "amount": "2,000",
        "nested": [{"prdy_vrss_sign": "5", "prdy_vrss": "10"}],
        "bad_change": {"pred_pre_sig": "unknown", "pred_pre": "10"},
    }

    normalized = normalize_data_values(payload)

    assert normalized["pred_pre_sig_meaning"] == "up"
    assert normalized["pred_pre"] == 20
    assert normalized["cur_prc"] == 1200
    assert normalized["flu_rt"] == 1.25
    assert normalized["volume"] == 1500
    assert normalized["amount"] == 2000
    assert normalized["nested"][0]["prdy_vrss"] == -10
    assert normalized["bad_change"]["pred_pre"] == "10"
    assert normalize_data_values("unchanged") == "unchanged"
    assert normalize_data_values({"cur_prc": "1234"}, sector_index=True)["cur_prc"] == 12.34


def test_sector_detection_and_response_normalization_preserve_metadata():
    assert _is_sector_index_response("sector/chart", None)
    assert _is_sector_index_response(None, "KA20004")
    assert not _is_sector_index_response("stock_info", "ka10001")

    normalized = normalize_response(
        {"error": "bad", "metadata": {"endpoint": "kept"}},
        tr_code="ka20004",
        endpoint="sector/chart",
        processing_time=0.2,
        headers={"ignored": "header"},
        normalize_data=True,
    )
    assert normalized["rt_cd"] == "1"
    assert normalized["msg1"] == "ERROR"
    assert normalized["metadata"]["endpoint"] == "kept"
    assert normalized["metadata"]["tr_code"] == "ka20004"
    assert normalized["metadata"]["processing_time"] == 0.2
    assert normalized["metadata"]["timestamp"]

    wrapped = normalize_response([{"cur_prc": "+100"}], normalize_data=True)
    assert wrapped["rt_cd"] == "0"
    assert wrapped["msg1"] == "SUCCESS"
    assert wrapped["data"][0]["cur_prc"] == 100
