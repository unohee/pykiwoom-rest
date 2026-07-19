import re

import pytest

from pykiwoom_rest.cli.field_map import (
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
from pykiwoom_rest.cli.main import SAFE_QUERY_DOMAINS
from pykiwoom_rest.cli.schema import get_schema, list_types


def _type_fields(type_name):
    schema = get_schema(type_name)
    return set(re.findall(r"^\s{2}([A-Za-z_][A-Za-z0-9_]*):", schema, re.MULTILINE))


def test_orderbook_schema_exposes_all_mapped_fields():
    assert set(ORDERBOOK.values()) <= _type_fields("Orderbook")


def test_orderbook_schema_documents_ten_quote_levels():
    schema = get_schema("Orderbook")

    for level in range(1, 11):
        assert f"askPrice{level}: String" in schema
        assert f"bidPrice{level}: String" in schema
        assert f"askVolume{level}: String" in schema
        assert f"bidVolume{level}: String" in schema

    assert "totalAskVolume: String" in schema
    assert "totalBidVolume: String" in schema


def test_orderbook_field_map_accepts_official_ka10004_keys():
    output = {
        "sel_fpr_bid": "70100",
        "sel_2th_pre_bid": "70200",
        "sel_10th_pre_bid": "71000",
        "buy_fpr_bid": "70000",
        "buy_2th_pre_bid": "69900",
        "buy_10th_pre_bid": "69100",
        "sel_fpr_req": "100",
        "sel_2th_pre_req": "200",
        "sel_10th_pre_req": "1000",
        "buy_fpr_req": "150",
        "buy_2th_pre_req": "250",
        "buy_10th_pre_req": "1050",
        "tot_sel_req": "5500",
        "tot_buy_req": "6600",
    }

    mapped = remap(output, ORDERBOOK)

    assert mapped["askPrice1"] == "70100"
    assert mapped["askPrice2"] == "70200"
    assert mapped["askPrice10"] == "71000"
    assert mapped["bidPrice1"] == "70000"
    assert mapped["bidPrice2"] == "69900"
    assert mapped["bidPrice10"] == "69100"
    assert mapped["askVolume1"] == "100"
    assert mapped["askVolume2"] == "200"
    assert mapped["askVolume10"] == "1000"
    assert mapped["bidVolume1"] == "150"
    assert mapped["bidVolume2"] == "250"
    assert mapped["bidVolume10"] == "1050"
    assert mapped["totalAskVolume"] == "5500"
    assert mapped["totalBidVolume"] == "6600"


def test_get_schema_raises_for_unknown_type():
    with pytest.raises(ValueError, match="타입 'MissingType'을 찾을 수 없습니다"):
        get_schema("MissingType")


def test_list_types_includes_cli_output_types():
    assert {
        "StockPrice",
        "Orderbook",
        "ChartCandle",
        "Ranking",
        "AccountBalance",
        "Holding",
        "Sector",
        "InvestorTrend",
        "TokenStatus",
    } <= set(list_types())


@pytest.mark.parametrize(
    ("type_name", "field_map"),
    [
        ("StockPrice", STOCK_PRICE),
        ("Orderbook", ORDERBOOK),
        ("ChartCandle", CHART_PRICE),
        ("Ranking", RANKING),
        ("AccountBalance", ACCOUNT_BALANCE),
        ("Holding", HOLDING),
        ("Sector", SECTOR_INDEX),
        ("InvestorTrend", INVESTOR_TREND),
    ],
)
def test_cli_output_schema_matches_field_map(type_name, field_map):
    assert _type_fields(type_name) == set(field_map.values())


def test_account_schema_matches_cli_wrapper_shape():
    fields = _type_fields("Account")

    assert fields == {
        "type",
        "summary",
        "holdings",
        "deposit",
        "evaluation",
        "unfilledOrders",
        "executedOrders",
        "profit",
    }
    assert "balance" not in fields


def test_sector_and_investor_schemas_include_list_wrappers():
    assert {"type", "code", "data", "items"} <= _type_fields("SectorResult")
    assert {"code", "data", "items"} <= _type_fields("InvestorResult")
    assert "allSectors" not in _type_fields("SectorResult")


def test_token_status_schema_matches_cli_snake_case_output():
    assert _type_fields("TokenStatus") == {
        "has_token",
        "is_valid",
        "token_prefix",
        "expires_at",
        "time_to_expiry",
        "needs_refresh",
    }


def test_query_schema_documents_runtime_allowlist():
    schema = get_schema("Query")

    assert ", ".join(SAFE_QUERY_DOMAINS) in schema
    for blocked_domain in {"order", "auth", "client"}:
        assert blocked_domain not in schema
