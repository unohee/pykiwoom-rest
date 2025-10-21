#!/bin/bash
# 코드 포맷팅 자동 적용 스크립트

set -e

echo "🎨 Formatting code with Ruff..."
ruff format src/pykiwoom_rest/ tests/

echo ""
echo "🔧 Auto-fixing linting issues..."
ruff check src/pykiwoom_rest/ tests/ --fix --unsafe-fixes || true

echo ""
echo "✅ Code formatting completed!"
echo "💡 Run './scripts/lint.sh' to verify formatting"
