#!/usr/bin/env python3
"""기존 `pykiwoom-mcp-server` 실행 명령을 위한 호환 래퍼."""

# ruff: noqa: E402, I001

import sys
from pathlib import Path


repository_src = Path(__file__).resolve().parents[3] / "src"
if repository_src.is_dir() and str(repository_src) not in sys.path:
    sys.path.insert(0, str(repository_src))

from pykiwoom_rest.mcp_server import PyKiwoomMCPServer, main  # noqa: E402,F401


if __name__ == "__main__":
    main()
