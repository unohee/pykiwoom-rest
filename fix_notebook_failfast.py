#!/usr/bin/env python3
"""
Jupyter notebook의 .get() 패턴을 fail-fast 방식으로 수정하는 스크립트
"""

import json
import re
from pathlib import Path


def fix_get_pattern(code: str) -> str:
    """
    .get(key, default) 패턴을 [key]로 변경하여 fail-fast 방식으로 수정

    예시:
    - price_info.get('cur_prc', '0') → price_info['cur_prc']
    - price_info.get('cur_prc', '0').replace(...) → price_info['cur_prc'].replace(...)
    - item.get("cntr_tm", "") → item["cntr_tm"]
    """

    # .get() 패턴을 [] 패턴으로 변경
    # dict.get('key', default) → dict['key']
    # dict.get("key", default) → dict["key"]

    # 패턴: variable.get('key', default) 에서 default 부분 제거
    patterns = [
        # dict.get('key', '0') → dict['key']
        (r"(\w+)\.get\(['\"](\w+)['\"]\s*,\s*['\"]0['\"]\)", r"\1['\2']"),
        # dict.get('key', '') → dict['key']
        (r"(\w+)\.get\(['\"](\w+)['\"]\s*,\s*['\"]['\"]?\)", r"\1['\2']"),
        # dict.get('key', 0) → dict['key']
        (r"(\w+)\.get\(['\"](\w+)['\"]\s*,\s*0\)", r"\1['\2']"),
        # dict.get("key", "0") → dict["key"] (double quotes)
        (r'(\w+)\.get\("(\w+)"\s*,\s*"0"\)', r'\1["\2"]'),
        # dict.get("key", "") → dict["key"]
        (r'(\w+)\.get\("(\w+)"\s*,\s*""?\)', r'\1["\2"]'),
    ]

    fixed_code = code
    for pattern, replacement in patterns:
        fixed_code = re.sub(pattern, replacement, fixed_code)

    return fixed_code


def add_exception_handling(code: str) -> str:
    """
    fail-fast를 위한 예외 처리 추가
    """

    # 이미 try-except가 있으면 그대로 반환
    if "try:" in code and "except KeyError" in code:
        return code

    # 특정 패턴이 있는 경우에만 예외 처리 주석 추가
    if "price_info[" in code or "item[" in code or "orderbook[" in code:
        # 맨 앞에 주석 추가
        comment = (
            "# Fail-fast: 필수 필드가 없으면 KeyError 발생\n"
            "# API 응답이 예상과 다를 때 즉시 문제를 파악할 수 있습니다.\n"
        )
        return comment + code

    return code


def fix_notebook(notebook_path: Path):
    """Jupyter notebook 파일 수정"""

    print(f"📝 Notebook 수정 중: {notebook_path}")

    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = json.load(f)

    modified_cells = 0

    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue

        source = cell.get("source", [])
        if not source:
            continue

        # source는 리스트 형태 (각 줄이 별도 항목)
        original_code = "".join(source)

        # .get() 패턴 수정
        fixed_code = fix_get_pattern(original_code)

        # 예외 처리 주석 추가
        fixed_code = add_exception_handling(fixed_code)

        if fixed_code != original_code:
            # 다시 줄 단위로 분리
            cell["source"] = fixed_code.splitlines(keepends=True)
            modified_cells += 1

            print(f"  ✓ Cell {cell.get('id', 'unknown')} 수정됨")

    # 수정된 notebook 저장
    if modified_cells > 0:
        with open(notebook_path, "w", encoding="utf-8") as f:
            json.dump(notebook, f, ensure_ascii=False, indent=1)

        print(f"\n✅ 총 {modified_cells}개 셀 수정 완료")
    else:
        print("\n⚠️  수정할 내용이 없습니다.")


if __name__ == "__main__":
    notebook_path = Path(__file__).parent / "examples" / "pykiwoom_comprehensive_test.ipynb"

    if not notebook_path.exists():
        print(f"❌ Notebook 파일을 찾을 수 없습니다: {notebook_path}")
        exit(1)

    fix_notebook(notebook_path)
