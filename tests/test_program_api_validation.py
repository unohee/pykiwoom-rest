from unittest.mock import Mock, patch

import pytest

from pykiwoom_rest.program_api import ProgramAPI


@pytest.fixture
def program_api():
    with patch.object(ProgramAPI, "_get_access_token", return_value="mock-token"):
        api = ProgramAPI(appkey="test-key", appsecret="test-secret", account_no="12345678")
    api.make_tr_request = Mock(return_value={"return_msg": "정상", "prps_cnctr": [{"stk_cd": "005930"}]})
    return api


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"market": "999"}, "market"),
        ({"include_current_entry": "2"}, "include_current_entry"),
        ({"cycle": "30"}, "cycle"),
        ({"exchange": "9"}, "exchange"),
        ({"concentration_rate": 50}, "concentration_rate"),
        ({"concentration_rate": "101"}, "concentration_rate"),
        ({"pbar_count": "0"}, "pbar_count"),
    ],
)
def test_get_pbar_concentration_rejects_invalid_parameters(program_api, kwargs, message):
    with pytest.raises(ValueError, match=message):
        program_api.get_pbar_concentration(**kwargs)


def test_get_pbar_concentration_normalizes_supply_concentration_response(program_api):
    result = program_api.get_pbar_concentration()

    assert result == {
        "rt_cd": "0",
        "msg1": "정상",
        "prps_cnctr": [{"stk_cd": "005930"}],
        "_source": "ka10025",
    }
    assert program_api.make_tr_request.call_args.kwargs["data"] == {
        "mrkt_tp": "000",
        "prps_cnctr_rt": "50",
        "cur_prc_entry": "0",
        "prpscnt": "10",
        "cycle_tp": "50",
        "stex_tp": "3",
    }


def test_get_pbar_concentration_preserves_nonstandard_response(program_api):
    program_api.make_tr_request.return_value = {"rt_cd": "1", "msg1": "failed"}

    assert program_api.get_pbar_concentration() == {"rt_cd": "1", "msg1": "failed"}
