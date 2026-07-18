from unittest.mock import Mock, patch

import pytest

from pykiwoom_rest.kiwoom_base import KiwoomAPIBase
from pykiwoom_rest.sector_api import SectorAPI


@pytest.fixture
def sector():
    with patch.object(SectorAPI, "_get_access_token", return_value="token"):
        return SectorAPI(appkey="key", appsecret="secret", account_no="12345678")


@pytest.mark.parametrize(
    ("name", "value", "message"),
    [
        ("base_dt", None, "required"),
        ("base_dt", "", "empty"),
        ("base_dt", "2024-01-01", "YYYYMMDD"),
        ("base_dt", "20240230", "valid"),
        ("sect_cd", "12", "3-4 digit"),
        ("mrkt_tp", "abc", "numeric"),
    ],
)
def test_sector_parameter_validation_rejects_invalid_values(name, value, message):
    with pytest.raises(ValueError, match=message):
        SectorAPI._normalize_sector_value(name, value)


def test_sector_params_and_positional_make_request_are_normalized(sector, monkeypatch):
    assert sector._normalize_sector_params({"sect_cd": " 001 ", "base_dt": "20240101"}) == {
        "sect_cd": "001",
        "base_dt": "20240101",
    }
    request = Mock(return_value={"ok": True})
    monkeypatch.setattr(KiwoomAPIBase, "make_tr_request", request)
    assert sector.make_tr_request("ka", "sector", {"sect_cd": "001"}) == {"ok": True}
    assert request.call_args.args[2] == {"sect_cd": "001"}
    assert sector.make_tr_request(tr_code="ka", endpoint="sector", data={"sect_cd": "001"}) == {"ok": True}
    assert request.call_args.kwargs["data"] == {"sect_cd": "001"}


def test_sector_methods_convert_four_digit_codes(sector):
    sector.make_tr_request = Mock(return_value={})
    sector.get_sector_minute_chart("0001")
    assert sector.make_tr_request.call_args.kwargs["data"]["inds_cd"] == "001"
    sector.get_sector_daily_chart("0001", "20240101")
    assert sector.make_tr_request.call_args.kwargs["data"]["inds_cd"] == "001"
    sector.get_sector_weekly_chart("0001", "20240101")
    assert sector.make_tr_request.call_args.kwargs["data"]["inds_cd"] == "001"
    sector.get_sector_monthly_chart("0001", "20240101")
    assert sector.make_tr_request.call_args.kwargs["data"]["inds_cd"] == "001"
    sector.get_sector_yearly_chart("0001", "20240101")
    assert sector.make_tr_request.call_args.kwargs["data"]["inds_cd"] == "001"


def test_index_daily_handles_empty_error_scalar_and_exception(sector, monkeypatch):
    monkeypatch.setattr(sector, "get_sector_daily_chart", Mock(return_value=None))
    assert sector.get_index_daily_price("001")["msg1"] == "INDEX_DAILY_DATA_ERROR"
    monkeypatch.setattr(sector, "get_sector_daily_chart", Mock(return_value={"rt_cd": "1", "msg1": "bad"}))
    assert sector.get_index_daily_price("001")["msg1"] == "bad"
    monkeypatch.setattr(sector, "get_sector_daily_chart", Mock(return_value={"rt_cd": "0", "output": [{}, {"dt": "20240101"}]}))
    assert sector.get_index_daily_price("001")["output2"][0]["stck_bsop_date"] == "20240101"
    monkeypatch.setattr(sector, "get_sector_daily_chart", Mock(return_value={"rt_cd": "0", "output": {"dt": "20240102"}}))
    assert sector.get_index_daily_price("001")["output2"][0]["stck_bsop_date"] == "20240102"
    monkeypatch.setattr(sector, "get_sector_daily_chart", Mock(side_effect=RuntimeError("broken")))
    assert sector.get_index_daily_price("001")["msg1"] == "broken"
