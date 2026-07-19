import logging

import pytest

from pykiwoom_rest.exception_utils import RaiseWithTraceMixin, rethrow_with_trace, trace_exceptions
from pykiwoom_rest.response_model import APIResponse


def test_api_response_success_dict_compatibility_and_kiwoom_helpers():
    response = APIResponse.create_success(
        {"rt_cd": "0", "msg1": "ok", "output": [1]}, tr_code="ka10001", endpoint="stock", processing_time=0.1
    )
    assert response.success and bool(response)
    assert response.data["rt_cd"] == "0"
    assert response["success"] and response["rt_cd"] == "0"
    assert "rt_cd" in response and list(response) == ["rt_cd", "msg1", "output"]
    assert list(response.keys()) == ["rt_cd", "msg1", "output"]
    assert list(response.values())[0] == "0"
    assert dict(response.items())["msg1"] == "ok"
    assert response.is_kiwoom_success() and response.get_kiwoom_message() == "ok"
    assert response.has_output_data() and response.get_output_data() == [1]
    response["extra"] = 1
    response.update({"more": 2})
    assert response.get("missing", "default") == "default"
    assert response.to_legacy_dict()["more"] == 2
    assert response.to_dict()["data"]["extra"] == 1
    assert response.raw_response["metadata"]["tr_code"] == "ka10001"
    assert "SUCCESS" in str(response)


def test_api_response_error_and_missing_data_paths():
    response = APIResponse.create_error("broken", "E1", {"reason": "bad"})
    assert not response and response.error == {"message": "broken", "code": "E1", "details": {"reason": "bad"}}
    assert not response.is_kiwoom_success()
    assert response.get_kiwoom_message() is None
    assert not response.has_output_data("other") and response.get_output_data("other") is None
    response["error"] = {"message": "changed"}
    response["metadata"] = {"request_id": "fixed"}
    with pytest.raises(KeyError, match="not found"):
        _ = response["missing"]
    assert "ERROR" in repr(response)


def test_rethrow_decorator_and_context_manager_log_and_raise(caplog):
    logger = logging.getLogger("test.exceptions")

    @rethrow_with_trace(logger)
    def fails():
        raise RuntimeError("boom")

    with caplog.at_level(logging.ERROR), pytest.raises(RuntimeError, match="boom"):
        fails()
    assert "Unhandled exception" in caplog.text

    with caplog.at_level(logging.ERROR), pytest.raises(ValueError, match="bad"):
        with trace_exceptions(logger, "during test"):
            raise ValueError("bad")
    with caplog.at_level(logging.ERROR), pytest.raises(ValueError):
        with trace_exceptions(logger):
            raise ValueError("bad")


def test_raise_with_trace_mixin_uses_custom_or_fallback_logger(caplog):
    class WithLogger(RaiseWithTraceMixin):
        logger = logging.getLogger("test.mixin")

    class WithoutLogger(RaiseWithTraceMixin):
        pass

    assert WithoutLogger()._trace_logger.name == "WithoutLogger"
    with caplog.at_level(logging.ERROR), pytest.raises(RuntimeError, match="boom"):
        try:
            raise RuntimeError("boom")
        except RuntimeError as exc:
            WithLogger().raise_with_trace(exc, "context")
    with caplog.at_level(logging.ERROR), pytest.raises(RuntimeError):
        try:
            raise RuntimeError("again")
        except RuntimeError as exc:
            WithoutLogger().raise_with_trace(exc)
