#!/usr/bin/env python3
"""
노트북 토큰 발급 문제 수정: 토큰 상태 확인 전에 명시적으로 토큰 발급
"""

import json
from pathlib import Path


def fix_token_status_cell(notebook_path: Path):
    """토큰 상태 확인 셀 수정 - 명시적 토큰 발급 추가"""

    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = json.load(f)

    # 토큰 상태 확인 셀 찾기
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue

        source = "".join(cell.get("source", []))

        # 토큰 상태 확인 셀 수정
        if "token_status = kiwoom.get_token_status()" in source:
            new_source = """# 토큰 발급 및 상태 확인
# 먼저 명시적으로 토큰을 발급받습니다
print("🔑 토큰 발급 중...")
try:
    token_info = kiwoom.get_access_token()
    print(f"✅ 토큰 발급 완료")
    print(f"   - 토큰 타입: {token_info.get('token_type', 'N/A')}")
    print(f"   - 유효기간: {token_info.get('expires_in', 0)}초 (24시간)")
    print(f"   - 발급 시각: {token_info.get('issued_at', 'N/A')}")
except Exception as e:
    print(f"❌ 토큰 발급 실패: {e}")

# 토큰 상태 확인 (모든 API 인스턴스에서 토큰 집계)
print("\\n📋 현재 토큰 상태:")
token_status = kiwoom.get_token_status()

print(f"   - 토큰 보유: {token_status['has_token']}")
print(f"   - 유효: {token_status['is_valid']}")
print(f"   - 토큰 프리픽스: {token_status['token_prefix']}")
print(f"   - 만료 시간: {token_status['expires_at']}")
print(f"   - 남은 시간: {token_status['time_to_expiry']}초 ({token_status['time_to_expiry'] // 3600}시간 {(token_status['time_to_expiry'] % 3600) // 60}분)")
print(f"   - 갱신 필요: {token_status['needs_refresh']}")

# 토큰 검증
if not token_status['has_token']:
    print("\\n⚠️  경고: 토큰이 없습니다.")
elif not token_status['is_valid']:
    print("\\n⚠️  경고: 토큰이 만료되었습니다.")
elif token_status['needs_refresh']:
    print("\\n🔄 토큰 갱신 권장 (5분 미만 남음)")
else:
    hours = token_status['time_to_expiry'] // 3600
    minutes = (token_status['time_to_expiry'] % 3600) // 60
    print(f"\\n✅ 토큰이 정상입니다. {hours}시간 {minutes}분 후 만료됩니다.")
"""

            cell["source"] = new_source.splitlines(keepends=True)
            print("✅ 토큰 상태 확인 셀 수정 완료 (명시적 토큰 발급 추가)")
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

    fix_token_status_cell(notebook_path)
    print("✅ Notebook 업데이트 완료")
