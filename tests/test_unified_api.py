from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from pykiwoom_rest.api_facade import KiwoomAPIFacade, RequestPriority
from pykiwoom_rest.unified_kiwoom_base import KiwoomAPIError, UnifiedKiwoomAPIBase
from pykiwoom_rest.unified_kiwoom_rest import UnifiedKiwoomRest


@pytest.fixture(autouse=True)
def reset_facade():
    KiwoomAPIFacade.reset_instance()
    UnifiedKiwoomAPIBase._facade_ref_counts.clear()
    yield
    KiwoomAPIFacade.reset_instance()
    UnifiedKiwoomAPIBase._facade_ref_counts.clear()


@pytest.fixture
def base():
    return UnifiedKiwoomAPIBase(account_no="12345678", appkey="key", appsecret="secret")


def test_base_rejects_missing_or_unsupported_configuration(monkeypatch):
    monkeypatch.delenv("ACCOUNT_NO", raising=False)
    monkeypatch.delenv("KIWOOM_APPKEY", raising=False)
    monkeypatch.delenv("KIWOOM_APPSECRET", raising=False)
    with pytest.raises(ValueError, match="필요합니다"):
        UnifiedKiwoomAPIBase()
    with pytest.raises(ValueError, match="max_retries"):
        UnifiedKiwoomAPIBase(account_no="a", appkey="k", appsecret="s", max_retries=2)
    with pytest.raises(ValueError, match="enable_rate_optimizer"):
        UnifiedKiwoomAPIBase(account_no="a", appkey="k", appsecret="s", enable_rate_optimizer=True)


def test_token_is_cached_and_hashkey_requires_hash(base):
    base.facade.make_request = Mock(return_value={"access_token": "token", "expires_in": 600})
    assert base._get_access_token() == "token"
    assert base._get_access_token() == "token"
    assert base.facade.make_request.call_count == 1

    base.facade.make_request = Mock(return_value={"HASH": "hash"})
    assert base._get_hashkey({"code": "005930"}) == "hash"
    with pytest.raises(KiwoomAPIError, match="해시키"):
        base.facade.make_request = Mock(return_value={})
        base._get_hashkey({})


def test_token_refresh_and_tr_requests_include_auth_hash_and_continuation(base):
    base.access_token = "old"
    base.token_expires = datetime.now() - timedelta(seconds=1)
    base.facade.make_request = Mock(
        side_effect=[
            {"access_token": "fresh", "expires_in": 600},
            {"HASH": "hash"},
            {"value": 1},
            {"HASH": "hash-2"},
            {"items": [], "cont-yn": "Y", "next-key": "next"},
        ]
    )

    assert base.make_tr_request("ka10001", "stock_info", {"stk_cd": "005930"}, method="POST") == {"value": 1}
    request_kwargs = base.facade.make_request.call_args_list[2].kwargs
    assert request_kwargs["endpoint"] == "/api/dostk/stkinfo"
    assert request_kwargs["headers"]["api-id"] == "ka10001"
    assert request_kwargs["headers"]["hashkey"] == "hash"

    continued = base.make_tr_request_continuous(
        "ka10001", "/custom", {"stk_cd": "005930"}, cont_yn="Y", next_key="cursor", method="POST"
    )
    assert continued == {"data": {"items": [], "cont-yn": "Y", "next-key": "next"}, "cont_yn": "Y", "next_key": "next"}
    assert base.facade.make_request.call_args_list[-1].kwargs["headers"]["next-key"] == "cursor"


def test_base_closed_health_stats_and_reference_counted_close(base):
    sibling = UnifiedKiwoomAPIBase(account_no="12345678", appkey="key", appsecret="secret")
    base.facade.health_check = Mock(return_value={"status": "healthy"})
    assert base.health_check()["authentication"] == "required"
    assert base.get_stats()["unified_kiwoom_base"]["use_mock"] is False
    base.close()
    assert not getattr(base.facade.base_api.session, "closed", False)
    with pytest.raises(KiwoomAPIError, match="종료"):
        base.make_tr_request("ka", "stock_info")
    sibling.close()
    assert KiwoomAPIFacade._instance is None


def test_unified_rest_delegates_public_surfaces_and_closes():
    rest = UnifiedKiwoomRest(account_no="12345678", appkey="key", appsecret="secret")
    rest.stock_api.get_stock_basic_info = Mock(return_value={"price": 70000})
    rest.chart_api.get_minute_chart = Mock(return_value={"items": []})
    rest.account_api.get_deposit_detail = Mock(return_value={"cash": 1})
    rest.order_api.buy_stock = Mock(return_value={"order": "1"})
    rest.sector_api.get_sector_current_price = Mock(return_value={"index": 1})

    assert rest.get_stock_price("005930") == {"price": 70000}
    assert rest.get_minute_chart("005930", 5) == {"items": []}
    assert rest.get_deposit_detail() == {"cash": 1}
    assert rest.buy_stock("005930", 1) == {"order": "1"}
    assert rest.get_sector_current_price() == {"index": 1}
    assert rest.stock is rest.stock_api
    assert rest.facade is rest.api_base.facade
    rest.close()
    rest.close()
