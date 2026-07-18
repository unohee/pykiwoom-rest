from pykiwoom_rest.kiwoom_rest import KiwoomRest
from pykiwoom_rest.response_utils import (
    clean_index_price,
    clean_price,
    clean_rate,
    interpret_sign_code,
    signed_change,
)


class DummyResponse:
    def __init__(self, payload):
        self._payload = payload
        self.text = "{}"

    def json(self):
        return self._payload


def test_default_process_response_preserves_raw_values():
    client = KiwoomRest(appkey="test_appkey", appsecret="test_appsecret", account_no="12345678")
    result = client.api_base._process_response(
        DummyResponse({"cur_prc": "-78,800", "pred_pre": "+1,250"})    )

    assert result["cur_prc"] == "-78,800"
    assert result["pred_pre"] == "+1,250"


def test_normalize_data_converts_stock_chart_ranking_representatives():
    client = KiwoomRest(appkey="test_appkey", appsecret="test_appsecret", account_no="12345678", normalize_data=True)
    result = client.api_base._process_response(
        DummyResponse(
            {
                "cur_prc": "-78,800",
                "pred_pre_sig": "2",
                "pred_pre": "+1,250",
                "flu_rt": "-1.56",
                "acc_trde_qty": "1,234,567",
                "rank_data": [
                    {"cur_prc": "+12,300", "chg_rt": "+3.21", "trde_qty": "2,000"}
                ],
                "chart": [{"open_pric": "-78,000", "high_pric": "+79,000"}],
            }
        )    )

    assert result["cur_prc"] == 78800
    assert result["pred_pre"] == 1250
    assert result["flu_rt"] == -1.56
    assert result["acc_trde_qty"] == 1234567
    assert result["rank_data"][0] == {"cur_prc": 12300, "chg_rt": 3.21, "trde_qty": 2000}
    assert result["chart"][0]["open_pric"] == 78000
    assert result["chart"][0]["high_pric"] == 79000


def test_sign_code_meanings_and_signed_change_ignore_raw_prefix():
    assert {code: interpret_sign_code(code) for code in ["1", "2", "3", "4", "5"]} == {
        "1": "limit_up",
        "2": "up",
        "3": "unchanged",
        "4": "limit_down",
        "5": "down",
    }
    assert signed_change("-1,250", "1") == 1250
    assert signed_change("-1,250", "2") == 1250
    assert signed_change("+1,250", "3") == 0
    assert signed_change("+1,250", "4") == -1250
    assert signed_change("+1,250", "5") == -1250


def test_sector_index_x100_normalization_in_response_path():
    from pykiwoom_rest.response_utils import normalize_response

    result = normalize_response(
        {
            "cur_prc": "402055",
            "inds_dt_pole_qry": [{"cur_prc": 402055, "open_pric": "401000"}],
        },
        endpoint="sector",
        normalize_data=True,
    )

    assert clean_index_price("402055") == 4020.55
    assert result["cur_prc"] == 4020.55
    assert result["inds_dt_pole_qry"][0]["cur_prc"] == 4020.55
    assert result["inds_dt_pole_qry"][0]["open_pric"] == 4010.0


def test_websocket_numeric_helpers_handle_formatted_values():
    assert clean_price("+78,800") == 78800
    assert clean_price("-78,800") == 78800
    assert clean_rate("+1.23") == 1.23
    assert clean_rate("-1.23") == -1.23


def test_signed_change_unknown_sign_code_raises():
    import pytest

    with pytest.raises(ValueError):
        signed_change("1,250", "9")


def test_websocket_dataclass_parsers_handle_formatted_values():
    from pykiwoom_rest.websocket_api import WebSocketAPI

    api = WebSocketAPI.__new__(WebSocketAPI)
    api._realtime_values = lambda data: data
    quote = api._parse_quote("005930", {"stck_prpr": "-78,800", "prdy_vrss": "+1,250", "prdy_ctrt": "-1.56", "acml_vol": "1,234", "stck_oprc": "+78,000", "stck_hgpr": "79,000", "stck_lwpr": "-77,000"})
    assert quote.current_price == 78800
    assert quote.change_price == 1250
    assert quote.change_rate == -1.56
    assert quote.volume == 1234

    orderbook = api._parse_orderbook("005930", {"askp1": "+78,900", "bidp1": "-78,700", "askp_rsqn1": "1,000", "bidp_rsqn1": "2,000", "total_askp_rsqn": "3,000", "total_bidp_rsqn": "4,000"})
    assert orderbook.ask_prices[0] == 78900
    assert orderbook.bid_prices[0] == 78700
    assert orderbook.ask_volumes[0] == 1000
    assert orderbook.bid_volumes[0] == 2000

    trade = api._parse_trade("005930", {"stck_prpr": "+78,800", "cntg_vol": "-500", "stck_cntg_hour": "093000", "prdy_vrss": "-1,250", "prdy_ctrt": "+1.56", "acml_vol": "5,000"})
    assert trade.trade_price == 78800
    assert trade.trade_volume == 500
    assert trade.change_price == -1250
    assert trade.change_rate == 1.56
    assert trade.cumulative_volume == 5000


def test_sector_pykis_conversion_preserves_x100_prices_by_default(monkeypatch):
    client = KiwoomRest(appkey="test_appkey", appsecret="test_appsecret", account_no="12345678")

    monkeypatch.setattr(
        client.sector_api,
        "make_tr_request",
        lambda *args, **kwargs: {
            "rt_cd": "0",
            "output": [{"dt": "20250101", "open": "402055", "high": "+403000", "low": 401000, "close": "402500", "vol": "1,000"}],
        },
    )

    result = client.sector_api.get_index_daily_price("001")
    row = result["output2"][0]
    assert row["bstp_nmix_oprc"] == "402055"
    assert row["bstp_nmix_hgpr"] == "+403000"
    assert row["bstp_nmix_lwpr"] == "401000"
    assert row["bstp_nmix_prpr"] == "402500"


def test_sector_pykis_conversion_decodes_x100_prices_when_opted_in(monkeypatch):
    client = KiwoomRest(appkey="test_appkey", appsecret="test_appsecret", account_no="12345678", normalize_data=True)

    monkeypatch.setattr(
        client.sector_api,
        "make_tr_request",
        lambda *args, **kwargs: {
            "rt_cd": "0",
            "output": [{"dt": "20250101", "open": "402055", "high": "+403000", "low": 401000, "close": "402500", "vol": "1,000"}],
        },
    )

    result = client.sector_api.get_index_daily_price("001")
    row = result["output2"][0]
    assert row["bstp_nmix_oprc"] == "4020.55"
    assert row["bstp_nmix_hgpr"] == "4030.0"
    assert row["bstp_nmix_lwpr"] == "4010.0"
    assert row["bstp_nmix_prpr"] == "4025.0"
