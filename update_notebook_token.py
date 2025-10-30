#!/usr/bin/env python3
"""
Notebook의 토큰 상태 확인 셀을 최신 패치에 맞게 업데이트
"""

import json
from pathlib import Path


def update_token_status_cell(notebook_path: Path):
    """토큰 상태 확인 셀 업데이트"""

    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = json.load(f)

    # 토큰 상태 확인 셀 찾기
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue

        source = "".join(cell.get("source", []))

        # 토큰 상태 확인 셀 수정
        if "token_status = kiwoom.get_token_status()" in source:
            new_source = """# 토큰 상태 확인 (최신 패치: 모든 API 인스턴스에서 토큰 집계)
token_status = kiwoom.get_token_status()

print("📋 토큰 상태:")
print(f"   - 토큰 보유: {token_status['has_token']}")
print(f"   - 유효: {token_status['is_valid']}")
print(f"   - 토큰 프리픽스: {token_status['token_prefix']}")
print(f"   - 만료 시간: {token_status['expires_at']}")
print(f"   - 남은 시간: {token_status['time_to_expiry']}초 ({token_status['time_to_expiry'] // 3600}시간)")
print(f"   - 갱신 필요: {token_status['needs_refresh']}")

# 토큰 검증
if not token_status['has_token']:
    print("\\n⚠️  경고: 토큰이 없습니다. API 호출 시 자동 발급됩니다.")
elif not token_status['is_valid']:
    print("\\n⚠️  경고: 토큰이 만료되었습니다. 다음 API 호출 시 자동 갱신됩니다.")
elif token_status['needs_refresh']:
    print("\\n🔄 토큰 갱신 권장 (5분 미만 남음)")
    # 수동 갱신 예시:
    # new_token = kiwoom.refresh_token()
    # print(f"✅ 토큰 갱신 완료")
else:
    print(f"\\n✅ 토큰이 정상입니다. {token_status['time_to_expiry'] // 3600}시간 {(token_status['time_to_expiry'] % 3600) // 60}분 후 만료됩니다.")
"""

            cell["source"] = new_source.splitlines(keepends=True)
            print("✅ 토큰 상태 확인 셀 업데이트 완료")
            break

    # 저장
    with open(notebook_path, "w", encoding="utf-8") as f:
        json.dump(notebook, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    notebook_path = (
        Path(__file__).parent / "examples" / "pykiwoom_comprehensive_test.ipynb"
    )

    if not notebook_path.exists():
        print(f"❌ Notebook 파일을 찾을 수 없습니다: {notebook_path}")
        exit(1)

    update_token_status_cell(notebook_path)
    print("\n✅ Notebook 업데이트 완료")
