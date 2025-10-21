#!/bin/bash
# 코드 품질 검사 스크립트

set -e

echo "🔍 Running Ruff linter..."
ruff check src/pykiwoom_rest/ tests/ --output-format=github

echo "✅ Ruff linting passed!"

echo ""
echo "🎨 Checking code formatting..."
ruff format src/pykiwoom_rest/ tests/ --check

echo "✅ Code formatting check passed!"

echo ""
echo "✨ All linting checks passed successfully!"
