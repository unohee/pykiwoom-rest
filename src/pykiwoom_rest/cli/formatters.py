"""출력 포맷터 — JSON / Table"""

import json
from typing import Dict, List, Union

MAX_TABLE_ROWS = 200
MAX_TABLE_CELL_WIDTH = 80


def _truncate_cell(value) -> str:
    text = str(value)
    if len(text) <= MAX_TABLE_CELL_WIDTH:
        return text
    return text[: MAX_TABLE_CELL_WIDTH - 1] + "…"


def json_output(data: dict, pretty: bool = False) -> str:
    indent = 2 if pretty else None
    return json.dumps(data, ensure_ascii=False, indent=indent, default=str)


def table_output(data: Union[List[Dict], Dict]) -> str:
    """리스트 데이터를 텍스트 테이블로 변환 (의존성 없음)"""
    if isinstance(data, dict):
        # 단일 객체: key = value 형식
        if not data:
            return "(empty)"
        max_key = min(max(len(_truncate_cell(k)) for k in data), MAX_TABLE_CELL_WIDTH)
        lines = []
        for k, v in data.items():
            lines.append(f"  {_truncate_cell(k):<{max_key}}  {_truncate_cell(v)}")
        return "\n".join(lines)

    if not data or not isinstance(data, list):
        return "(empty)"

    # 리스트: 테이블 형식
    rows = data[:MAX_TABLE_ROWS]
    if not all(isinstance(row, dict) for row in rows):
        lines = [_truncate_cell(item) for item in rows]
        if len(data) > MAX_TABLE_ROWS:
            lines.append(f"... ({len(data) - MAX_TABLE_ROWS} more rows)")
        return "\n".join(lines)

    headers = []
    for row in rows:
        for h in row:
            if h not in headers:
                headers.append(h)

    col_widths = {h: min(len(_truncate_cell(h)), MAX_TABLE_CELL_WIDTH) for h in headers}
    for row in rows:
        for h in headers:
            val = _truncate_cell(row.get(h, ""))
            col_widths[h] = max(col_widths[h], len(val))

    # 헤더 행
    header_line = "  ".join(_truncate_cell(h).ljust(col_widths[h]) for h in headers)
    sep_line = "  ".join("-" * col_widths[h] for h in headers)

    lines = [header_line, sep_line]
    for row in rows:
        line = "  ".join(_truncate_cell(row.get(h, "")).ljust(col_widths[h]) for h in headers)
        lines.append(line)
    if len(data) > MAX_TABLE_ROWS:
        lines.append(f"... ({len(data) - MAX_TABLE_ROWS} more rows)")

    return "\n".join(lines)
