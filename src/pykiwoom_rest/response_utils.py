"""
Response normalization utilities to unify returned structures.
원시 JSON 응답을 보존하면서 기본 키와 메타데이터를 일관되게 부여합니다.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


def normalize_response(
    data: dict[str, Any],
    *,
    tr_code: str | None = None,
    endpoint: str | None = None,
    processing_time: float | None = None,
    headers: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Ensure unified response structure while preserving original payload.

    - Guarantees presence of keys: 'rt_cd', 'msg1'
    - Adds 'metadata' block with timestamp, tr_code, endpoint, processing_time
    - Does not alter existing keys/values
    """
    if not isinstance(data, dict):
        # Non-dict JSON (rare) -> wrap into dict
        data = {"data": data}

    # Preserve original payload
    out: dict[str, Any] = dict(data)

    # Provide defaults if missing
    if "rt_cd" not in out:
        # If server returned explicit error field, set failure, else success
        out["rt_cd"] = "1" if "error" in out else "0"
    if "msg1" not in out:
        out["msg1"] = "SUCCESS" if out.get("rt_cd") == "0" else out.get("msg", "ERROR")

    # Attach metadata non-destructively
    meta = out.get("metadata", {}) if isinstance(out.get("metadata"), dict) else {}
    meta_update = {
        "timestamp": datetime.now().isoformat(),
        "tr_code": tr_code,
        "endpoint": endpoint,
        "processing_time": processing_time,
    }
    # Only set missing metadata fields
    for k, v in meta_update.items():
        if k not in meta or meta[k] is None:
            meta[k] = v
    out["metadata"] = meta

    return out
