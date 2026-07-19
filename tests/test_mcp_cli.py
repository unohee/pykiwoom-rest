"""MCP 선택 의존성 콘솔 진입점 테스트."""

import sys
from types import SimpleNamespace

import pytest

from pykiwoom_rest import mcp_cli


def test_base_install_reports_mcp_extra(monkeypatch):
    monkeypatch.setattr(mcp_cli.importlib.util, "find_spec", lambda name: None)

    with pytest.raises(SystemExit) as exc_info:
        mcp_cli.main()

    assert "pykiwoom-rest[mcp]" in str(exc_info.value)


def test_mcp_install_delegates_to_server(monkeypatch):
    called = []
    fake_server = SimpleNamespace(main=lambda: called.append(True))
    monkeypatch.setattr(mcp_cli.importlib.util, "find_spec", lambda name: object())
    monkeypatch.setitem(sys.modules, "pykiwoom_rest.mcp_server", fake_server)

    mcp_cli.main()

    assert called == [True]
