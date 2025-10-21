#!/bin/bash
# 테스트 실행 스크립트

set -e

echo "🧪 Running unit tests..."
pytest tests/ -v --tb=short --maxfail=5 -m "not slow"

echo ""
echo "📊 Running tests with coverage..."
pytest tests/ --cov=src/pykiwoom_rest --cov-report=term-missing --cov-report=html

echo ""
echo "✅ All tests completed!"
echo "📈 Coverage report generated in htmlcov/index.html"
