from unittest.mock import MagicMock, Mock, patch

from pykiwoom_rest.kiwoom_base import KiwoomAPIBase
from pykiwoom_rest.kiwoom_rest import KiwoomRest
from pykiwoom_rest.response_utils import (
    clean_index_price,
    clean_price,
    clean_rate,
    clean_signed_quantity,
    interpret_sign_code,
    normalize_data_values,
    signed_change,
)
from pykiwoom_rest.sector_api import SectorAPI
from pykiwoom_rest.unified_kiwoom_rest import UnifiedKiwoomRest


def test_clean_numeric_helpers():
    assert clean_price("-78,800") == 78800
    assert clean_price("+000000059000") == 59000
    assert clean_rate("+0.94") == 0.94
    assert clean_rate("-1.76%") == -1.76
    assert clean_signed_quantity("--261,000") == -261000
    assert clean_index_price("402055") == 4020.55
    assert clean_index_price("4020.55") == 4020.55
    assert interpret_sign_code("0") == "unchanged"
    assert interpret_sign_code("5") == "down"
    assert signed_change("600", "2") == 600
    assert signed_change("600", "5") == -600
    assert signed_change("-600", None) == -600


def test_normalize_stock_chart_payload_preserves_dates_and_codes():
    payload = {
        "rt_cd": "0",
        "stk_min_pole_chart_qry": [
            {
                "stk_cd": "005930",
                "cntr_tm": "20260113153000",
                "cur_prc": "-78,800",
                "open_pric": "-78,850",
                "high_pric": "-78,900",
                "low_pric": "-78,800",
                "pred_pre": "600",
                "pred_pre_sig": "5",
                "trde_qty": "1,234",
            }
        ],
    }

    result = normalize_data_values(payload, tr_code="ka10080", endpoint="chart")
    row = result["stk_min_pole_chart_qry"][0]

    assert row["stk_cd"] == "005930"
    assert row["cntr_tm"] == "20260113153000"
    assert row["cur_prc"] == 78800
    assert row["open_pric"] == 78850
    assert row["high_pric"] == 78900
    assert row["low_pric"] == 78800
    assert row["pred_pre"] == -600
    assert row["pred_pre_sig"] == "down"
    assert row["trde_qty"] == 1234


def test_normalize_documented_weight_fields_as_rates():
    payload = {
        "stk_ddwkmm": [
            {
                "date": "20260113",
                "for_poss": "5,100",
                "for_wght": "+26.07",
            }
        ],
        "stk_frgnr": [
            {
                "dt": "20260113",
                "wght": "+26.10",
                "trde_wght": "-8.58",
                "frgnr_limit_irds": "-1,200",
            }
        ],
        "acnt_evlt_remn_indv_tot": [
            {
                "buy_wght": "83.2",
                "evlt_wght": "0.0",
            }
        ],
    }

    result = normalize_data_values(payload)

    assert result["stk_ddwkmm"][0]["for_poss"] == 5100
    assert result["stk_ddwkmm"][0]["for_wght"] == 26.07
    assert result["stk_frgnr"][0]["wght"] == 26.10
    assert result["stk_frgnr"][0]["trde_wght"] == -8.58
    assert result["stk_frgnr"][0]["frgnr_limit_irds"] == -1200
    assert result["acnt_evlt_remn_indv_tot"][0]["buy_wght"] == 83.2
    assert result["acnt_evlt_remn_indv_tot"][0]["evlt_wght"] == 0.0


def test_normalize_orderbook_quantity_fields_from_ka10004_docs():
    payload = {
        "sel_fpr_bid": "-78,900",
        "buy_fpr_bid": "+78,800",
        "sel_fpr_req": "+1,500",
        "buy_fpr_req": "-2,500",
        "sel_2th_pre_req": "2,000",
        "buy_10th_pre_req": "900",
        "tot_sel_req": "11,000",
        "tot_buy_req": "12,000",
        "ovt_sel_req": "130",
        "ovt_buy_req": "140",
        "sel_2th_pre_req_pre": "-30",
        "buy_10th_pre_req_pre": "+40",
        "tot_sel_req_jub_pre": "--50",
        "tot_buy_req_jub_pre": "+60",
        "ovt_sel_req_pre": "-70",
        "ovt_buy_req_pre": "+80",
    }

    result = normalize_data_values(payload, tr_code="ka10004", endpoint="stock_info")

    assert result["sel_fpr_bid"] == 78900
    assert result["buy_fpr_bid"] == 78800
    assert result["sel_fpr_req"] == 1500
    assert result["buy_fpr_req"] == 2500
    assert result["sel_2th_pre_req"] == 2000
    assert result["buy_10th_pre_req"] == 900
    assert result["tot_sel_req"] == 11000
    assert result["tot_buy_req"] == 12000
    assert result["ovt_sel_req"] == 130
    assert result["ovt_buy_req"] == 140
    assert result["sel_2th_pre_req_pre"] == -30
    assert result["buy_10th_pre_req_pre"] == 40
    assert result["tot_sel_req_jub_pre"] == -50
    assert result["tot_buy_req_jub_pre"] == 60
    assert result["ovt_sel_req_pre"] == -70
    assert result["ovt_buy_req_pre"] == 80


def test_normalize_documented_trade_detail_numeric_fields():
    payload = {
        "cntr_info": [
            {
                "cntr_tm": "161548",
                "pri_sel_bid_unit": "+68,900",
                "pri_buy_bid_unit": "+53,500",
                "cntr_trde_qty": "-5",
                "acc_trde_qty": "6,265",
                "acc_trde_prica": "383,540,500",
                "cntr_str": "12.99",
            }
        ],
        "stk_dt_pole_qry": [
            {
                "dt": "20241101",
                "cntr_str": "0.00",
                "for_netprps": "-1,234",
                "orgn_netprps": "+5,678",
                "bf_mkrt_trde_prica": "1,000",
                "opmr_trde_prica": "2,000",
                "af_mkrt_trde_prica": "3,000",
            }
        ],
    }

    result = normalize_data_values(payload)
    cntr_row = result["cntr_info"][0]
    daily_row = result["stk_dt_pole_qry"][0]

    assert cntr_row["pri_sel_bid_unit"] == 68900
    assert cntr_row["pri_buy_bid_unit"] == 53500
    assert cntr_row["cntr_str"] == 12.99
    assert daily_row["cntr_str"] == 0.0
    assert daily_row["for_netprps"] == -1234
    assert daily_row["orgn_netprps"] == 5678
    assert daily_row["bf_mkrt_trde_prica"] == 1000
    assert daily_row["opmr_trde_prica"] == 2000
    assert daily_row["af_mkrt_trde_prica"] == 3000


def test_normalize_documented_pre_and_individual_net_purchase_fields():
    payload = {
        "stk_ddwkmm": [
            {
                "dt": "20241101",
                "pre": "+100",
                "for_netprps": "-1,234",
                "orgn_netprps": "+5,678",
                "ind_netprps": "--300",
            }
        ],
        "crd_trde_trend": [
            {
                "dt": "20241101",
                "pre": "-250",
                "pred_pre": "150",
                "pred_pre_sig": "5",
            }
        ],
    }

    result = normalize_data_values(payload)

    weekly_row = result["stk_ddwkmm"][0]
    credit_row = result["crd_trde_trend"][0]

    assert weekly_row["pre"] == 100
    assert weekly_row["for_netprps"] == -1234
    assert weekly_row["orgn_netprps"] == 5678
    assert weekly_row["ind_netprps"] == -300
    assert credit_row["pre"] == -250
    assert credit_row["pred_pre"] == -150
    assert credit_row["pred_pre_sig"] == "down"


def test_normalize_signed_quantity_fields_preserves_direction_from_docs():
    payload = {
        "stk_frgnr": [
            {
                "dt": "20241101",
                "trde_qty": "0",
                "chg_qty": "-3441",
            }
        ],
        "cntr_info": [
            {
                "cntr_tm": "161548",
                "cntr_trde_qty": "-5",
                "acc_trde_qty": "6265",
            }
        ],
        "opmr_invsr_trde": [
            {
                "stk_cd": "005930",
                "acc_trde_qty": "1",
                "netprps_qty": "+1083000",
                "prev_pot_netprps_qty": "+1083000",
                "buy_qty": "+1113000",
                "sell_qty": "--30000",
            },
            {
                "stk_cd": "005930",
                "acc_trde_qty": "0",
                "netprps_qty": "--261000",
                "prev_pot_netprps_qty": "--347000",
                "buy_qty_irds": "+108000",
                "sell_qty_irds": "+22000",
            },
        ],
    }

    result = normalize_data_values(payload)

    assert result["stk_frgnr"][0]["trde_qty"] == 0
    assert result["stk_frgnr"][0]["chg_qty"] == -3441
    assert result["cntr_info"][0]["cntr_trde_qty"] == -5
    assert result["cntr_info"][0]["acc_trde_qty"] == 6265
    assert result["opmr_invsr_trde"][0]["netprps_qty"] == 1083000
    assert result["opmr_invsr_trde"][0]["prev_pot_netprps_qty"] == 1083000
    assert result["opmr_invsr_trde"][0]["buy_qty"] == 1113000
    assert result["opmr_invsr_trde"][0]["sell_qty"] == -30000
    assert result["opmr_invsr_trde"][1]["netprps_qty"] == -261000
    assert result["opmr_invsr_trde"][1]["prev_pot_netprps_qty"] == -347000
    assert result["opmr_invsr_trde"][1]["buy_qty_irds"] == 108000
    assert result["opmr_invsr_trde"][1]["sell_qty_irds"] == 22000


def test_normalize_missing_financial_metrics_preserves_missing_values_from_docs():
    payload = {
        "stk_cd": "005930",
        "mac_wght": "",
        "per": "",
        "eps": None,
        "roe": "0",
        "pbr": "",
        "ev": "",
        "bps": "-75300",
        "sale_amt": "0",
    }

    result = normalize_data_values(payload, tr_code="ka10001", endpoint="stock")

    assert result["mac_wght"] == ""
    assert result["per"] == ""
    assert result["eps"] is None
    assert result["roe"] == 0.0
    assert result["pbr"] == ""
    assert result["ev"] == ""
    assert result["bps"] == -75300.0
    assert result["sale_amt"] == 0


def test_normalize_account_amounts_preserves_profit_loss_direction_from_docs():
    payload = {
        "tot_pur_amt": "000000017598258",
        "tot_evlt_amt": "000000025789890",
        "tot_evlt_pl": "-000000008138825",
        "acnt_evlt_remn_indv_tot": [
            {
                "evltv_prft": "-00000000196888",
                "pur_amt": "000000000373500",
                "evlt_amt": "000000000177000",
            }
        ],
    }

    result = normalize_data_values(payload, tr_code="kt00018", endpoint="account")

    assert result["tot_pur_amt"] == 17598258
    assert result["tot_evlt_amt"] == 25789890
    assert result["tot_evlt_pl"] == -8138825
    assert result["acnt_evlt_remn_indv_tot"][0]["evltv_prft"] == -196888
    assert result["acnt_evlt_remn_indv_tot"][0]["pur_amt"] == 373500
    assert result["acnt_evlt_remn_indv_tot"][0]["evlt_amt"] == 177000


def test_normalize_sector_index_payload_decodes_x100_values():
    payload = {
        "inds_min_pole_qry": [
            {
                "cntr_tm": "20260113153000",
                "cur_prc": "402055",
                "open_pric": "403068",
                "high_pric": "403420",
                "low_pric": "402055",
                "pred_pre": "2604",
                "pred_pre_sig": "2",
            }
        ]
    }

    result = normalize_data_values(payload, tr_code="ka20005", endpoint="chart")
    row = result["inds_min_pole_qry"][0]

    assert row["cur_prc"] == 4020.55
    assert row["open_pric"] == 4030.68
    assert row["high_pric"] == 4034.2
    assert row["low_pric"] == 4020.55
    assert row["pred_pre"] == 26.04
    assert row["pred_pre_sig"] == "up"


def test_normalize_ka20001_preserves_decimal_sector_current_and_time_rows():
    payload = {
        "cur_prc": "-2394.49",
        "pred_pre_sig": "5",
        "pred_pre": "-278.47",
        "flu_rt": "-10.42",
        "trde_qty": "890",
        "open_pric": "-2669.53",
        "high_pric": "-2669.53",
        "low_pric": "-2375.21",
        "inds_cur_prc_tm": [
            {
                "tm_n": "143000",
                "cur_prc_n": "-2394.49",
                "pred_pre_sig_n": "5",
                "pred_pre_n": "-278.47",
                "flu_rt_n": "-10.42",
                "trde_qty_n": "14",
                "acc_trde_qty_n": "890",
            },
            {
                "tm_n": "142930",
                "cur_prc_n": "-2395.62",
                "pred_pre_sig_n": "5",
                "pred_pre_n": "-277.34",
                "flu_rt_n": "-10.38",
                "trde_qty_n": "14",
                "acc_trde_qty_n": "848",
            },
        ],
    }

    result = normalize_data_values(payload, tr_code="ka20001", endpoint="sector")
    first_row = result["inds_cur_prc_tm"][0]
    second_row = result["inds_cur_prc_tm"][1]

    assert result["cur_prc"] == 2394.49
    assert result["pred_pre_sig"] == "down"
    assert result["pred_pre"] == -278.47
    assert result["flu_rt"] == -10.42
    assert result["trde_qty"] == 890
    assert result["open_pric"] == 2669.53
    assert result["high_pric"] == 2669.53
    assert result["low_pric"] == 2375.21
    assert first_row["tm_n"] == "143000"
    assert first_row["cur_prc_n"] == 2394.49
    assert first_row["pred_pre_sig_n"] == "down"
    assert first_row["pred_pre_n"] == -278.47
    assert first_row["flu_rt_n"] == -10.42
    assert first_row["trde_qty_n"] == 14
    assert first_row["acc_trde_qty_n"] == 890
    assert second_row["cur_prc_n"] == 2395.62
    assert second_row["pred_pre_n"] == -277.34


def test_normalize_ka20003_preserves_decimal_sector_index_list_values():
    payload = {
        "all_inds_idex": [
            {
                "stk_cd": "001",
                "stk_nm": "종합(KOSPI)",
                "cur_prc": "-2393.33",
                "pre_sig": "5",
                "pred_pre": "-279.63",
                "flu_rt": "-10.46",
                "trde_qty": "993",
                "wght": "",
                "trde_prica": "46494",
            },
            {
                "stk_cd": "002",
                "stk_nm": "대형주",
                "cur_prc": "+2379.14",
                "pre_sig": "2",
                "pred_pre": "+326.94",
                "flu_rt": "+12.08",
                "trde_qty": "957",
                "wght": "",
                "trde_prica": "44563",
            },
        ],
    }

    result = normalize_data_values(payload, tr_code="ka20003", endpoint="sector")
    first_row = result["all_inds_idex"][0]
    second_row = result["all_inds_idex"][1]

    assert first_row["stk_cd"] == "001"
    assert first_row["stk_nm"] == "종합(KOSPI)"
    assert first_row["cur_prc"] == 2393.33
    assert first_row["pre_sig"] == "down"
    assert first_row["pred_pre"] == -279.63
    assert first_row["flu_rt"] == -10.46
    assert first_row["trde_qty"] == 993
    assert first_row["wght"] == ""
    assert first_row["trde_prica"] == 46494
    assert second_row["cur_prc"] == 2379.14
    assert second_row["pre_sig"] == "up"
    assert second_row["pred_pre"] == 326.94
    assert second_row["flu_rt"] == 12.08


def test_normalize_ka20009_preserves_decimal_index_current_values():
    payload = {
        "cur_prc": "-2384.71",
        "pred_pre_sig": "5",
        "pred_pre": "-288.25",
        "flu_rt": "-10.78",
        "trde_qty": "1103",
        "open_pric": "-2669.53",
        "high_pric": "-2669.53",
        "low_pric": "-2375.21",
        "inds_cur_prc_daly_rept": [
            {
                "dt_n": "20241122",
                "cur_prc_n": "-2384.71",
                "pred_pre_sig_n": "5",
                "pred_pre_n": "-288.25",
                "flu_rt_n": "-10.78",
                "acc_trde_qty_n": "1103",
            },
            {
                "dt_n": "20241121",
                "cur_prc_n": "+2672.96",
                "pred_pre_sig_n": "2",
                "pred_pre_n": "+25.56",
                "flu_rt_n": "+0.97",
                "acc_trde_qty_n": "444",
            },
        ],
    }

    result = normalize_data_values(payload, tr_code="ka20009", endpoint="sector")
    first_row = result["inds_cur_prc_daly_rept"][0]
    second_row = result["inds_cur_prc_daly_rept"][1]

    assert result["cur_prc"] == 2384.71
    assert result["pred_pre_sig"] == "down"
    assert result["pred_pre"] == -288.25
    assert result["flu_rt"] == -10.78
    assert result["trde_qty"] == 1103
    assert result["open_pric"] == 2669.53
    assert result["high_pric"] == 2669.53
    assert result["low_pric"] == 2375.21
    assert first_row["dt_n"] == "20241122"
    assert first_row["cur_prc_n"] == 2384.71
    assert first_row["pred_pre_sig_n"] == "down"
    assert first_row["pred_pre_n"] == -288.25
    assert first_row["flu_rt_n"] == -10.78
    assert first_row["acc_trde_qty_n"] == 1103
    assert second_row["cur_prc_n"] == 2672.96
    assert second_row["pred_pre_sig_n"] == "up"
    assert second_row["pred_pre_n"] == 25.56
    assert second_row["flu_rt_n"] == 0.97
    assert second_row["acc_trde_qty_n"] == 444


@patch.dict(
    "os.environ",
    {
        "ACCOUNT_NO": "12345678",
        "KIWOOM_APPKEY": "test_app_key",
        "KIWOOM_APPSECRET": "test_app_secret",
    },
)
@patch("requests.Session")
def test_kiwoom_rest_passes_normalize_data_to_modules(mock_session_class):
    mock_session_class.return_value = MagicMock()

    default_client = KiwoomRest()
    normalized_client = KiwoomRest(normalize_data=True)

    assert default_client.stock_api.normalize_data is False
    assert default_client.chart_api.normalize_data is False
    assert normalized_client.stock_api.normalize_data is True
    assert normalized_client.chart_api.normalize_data is True
    assert normalized_client.ranking_api.normalize_data is True
    assert normalized_client.sector_api.normalize_data is True


@patch.dict(
    "os.environ",
    {
        "ACCOUNT_NO": "12345678",
        "KIWOOM_APPKEY": "test_app_key",
        "KIWOOM_APPSECRET": "test_app_secret",
    },
)
@patch("requests.Session")
def test_unified_kiwoom_rest_passes_normalize_data_to_api_base(mock_session_class):
    mock_session_class.return_value = MagicMock()
    facade = MagicMock()
    facade.make_request.return_value = {
        "rt_cd": "0",
        "cur_prc": "-78,800",
        "pred_pre": "600",
        "pre_sig": "5",
        "for_wght": "+26.07",
    }

    with patch(
        "pykiwoom_rest.unified_kiwoom_base.KiwoomAPIFacade.get_instance",
        return_value=facade,
    ):
        normalized_client = UnifiedKiwoomRest(normalize_data=True)
        normalized_client.api_base._get_access_token = Mock(return_value="test_token")

        result = normalized_client.api_base.make_tr_request(
            tr_code="ka10001",
            endpoint="stock_info",
        )

        assert normalized_client.api_base.normalize_data is True
        assert result["cur_prc"] == 78800
        assert result["pred_pre"] == -600
        assert result["pre_sig"] == "down"
        assert result["for_wght"] == 26.07


@patch.dict(
    "os.environ",
    {
        "ACCOUNT_NO": "12345678",
        "KIWOOM_APPKEY": "test_app_key",
        "KIWOOM_APPSECRET": "test_app_secret",
    },
)
@patch("requests.Session")
def test_process_response_normalizes_only_when_enabled(mock_session_class):
    mock_session_class.return_value = MagicMock()
    raw_response = MagicMock()
    raw_response.json.return_value = {
        "rt_cd": "0",
        "cur_prc": "-78,800",
        "pred_pre": "600",
        "pre_sig": "5",
    }

    raw_api = KiwoomAPIBase()
    normalized_api = KiwoomAPIBase(normalize_data=True)

    assert raw_api._process_response(raw_response)["cur_prc"] == "-78,800"

    result = normalized_api._process_response(raw_response)
    assert result["cur_prc"] == 78800
    assert result["pred_pre"] == -600
    assert result["pre_sig"] == "down"


def test_sector_index_daily_price_decodes_kiwoom_x100_for_pykis_output():
    api = SectorAPI.__new__(SectorAPI)
    api.get_sector_daily_chart = Mock(
        return_value={
            "rt_cd": "0",
            "inds_dt_pole_qry": [
                {
                    "dt": "20251220",
                    "open_pric": "405578",
                    "high_pric": "405578",
                    "low_pric": "399705",
                    "cur_prc": "402055",
                    "trde_qty": "413598",
                    "trde_prica": "16470368",
                }
            ],
        }
    )

    result = api.get_index_daily_price("001", count=1)
    row = result["output2"][0]

    assert row["stck_bsop_date"] == "20251220"
    assert row["bstp_nmix_oprc"] == "4055.78"
    assert row["bstp_nmix_hgpr"] == "4055.78"
    assert row["bstp_nmix_lwpr"] == "3997.05"
    assert row["bstp_nmix_prpr"] == "4020.55"
    assert row["acml_vol"] == "413598"
    assert row["acml_tr_pbmn"] == "16470368"


def test_sector_index_daily_price_does_not_decode_twice_when_already_normalized():
    api = SectorAPI.__new__(SectorAPI)
    api.get_sector_daily_chart = Mock(
        return_value={
            "rt_cd": "0",
            "inds_dt_pole_qry": [
                {
                    "dt": "20251220",
                    "open_pric": 4055.78,
                    "high_pric": 4055.78,
                    "low_pric": 3997.05,
                    "cur_prc": 4020.55,
                    "trde_qty": 413598,
                    "trde_prica": 16470368,
                }
            ],
        }
    )

    row = api.get_index_daily_price("001", count=1)["output2"][0]

    assert row["bstp_nmix_oprc"] == "4055.78"
    assert row["bstp_nmix_prpr"] == "4020.55"
    assert row["acml_vol"] == "413598"
    assert row["acml_tr_pbmn"] == "16470368"
