"""websockets 의존성이 없을 때의 명시적 설치 안내를 검증한다."""

import builtins
import importlib.util
from pathlib import Path

import pytest


def test_websocket_dependency_error_is_actionable(monkeypatch):
    source_path = Path(__file__).parents[1] / "src/pykiwoom_rest/websocket_client.py"
    real_import = builtins.__import__

    def fail_websockets(name, *args, **kwargs):
        if name == "websockets":
            raise ImportError("missing websockets")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fail_websockets)
    spec = importlib.util.spec_from_file_location("isolated_websocket_client", source_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    with pytest.raises(ImportError, match="pip install websockets"):
        spec.loader.exec_module(module)
