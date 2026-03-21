"""출력 포맷터 — JSON / Table"""

import json
from typing import Any, Dict, List, Optional, Union


def json_output(data: dict, pretty: bool = False) -> str:
    indent = 2 if pretty else None
    return json.dumps(data, ensure_ascii=False, indent=indent, default=str)


def table_output(data: Union[List[Dict], Dict]) -> str:
    """리스트 데이터를 텍스트 테이블로 변환 (의존성 없음)"""
    if isinstance(data, dict):
        # 단일 객체: key = value 형식
        if not data:
            return "(empty)"
        max_key = max(len(str(k)) for k in data.keys())
        lines = []
        for k, v in data.items():
            lines.append(f"  {str(k):<{max_key}}  {v}")
        return "\n".join(lines)

    if not data or not isinstance(data, list):
        return "(empty)"

    # 리스트: 테이블 형식
    headers = list(data[0].keys())
    col_widths = {h: len(str(h)) for h in headers}
    for row in data:
        for h in headers:
            val = str(row.get(h, ""))
            col_widths[h] = max(col_widths[h], len(val))

    # 헤더 행
    header_line = "  ".join(str(h).ljust(col_widths[h]) for h in headers)
    sep_line = "  ".join("-" * col_widths[h] for h in headers)

    lines = [header_line, sep_line]
    for row in data:
        line = "  ".join(str(row.get(h, "")).ljust(col_widths[h]) for h in headers)
        lines.append(line)

    return "\n".join(lines)
