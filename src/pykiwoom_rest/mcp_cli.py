"""선택 의존성을 안전하게 확인하는 MCP 콘솔 진입점."""

import importlib.util


def main():
    """MCP SDK 설치 여부를 확인한 뒤 stdio 서버를 시작한다."""
    if importlib.util.find_spec("mcp") is None:
        raise SystemExit(
            "kiwoom-mcp를 실행하려면 MCP 추가 기능이 필요합니다. "
            "pip install 'pykiwoom-rest[mcp]'로 설치하세요."
        )

    from .mcp_server import main as run

    return run()


if __name__ == "__main__":
    main()
