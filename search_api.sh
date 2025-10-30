#!/bin/bash
# API 문서 검색 스크립트

if [ -z "$1" ]; then
    echo "사용법: ./search_api.sh <API_ID 또는 키워드>"
    echo "예제: ./search_api.sh ka10001"
    echo "예제: ./search_api.sh 주식호가"
    exit 1
fi

KEYWORD="$1"

echo "🔍 키워드: $KEYWORD"
echo "=" 60

# API ID로 검색
if [ -f "docs/api_details/${KEYWORD}_*.md" ]; then
    echo "📄 직접 매칭:"
    ls docs/api_details/${KEYWORD}_*.md
    echo
    cat docs/api_details/${KEYWORD}_*.md | head -100
else
    # 내용으로 검색
    echo "📄 검색 결과:"
    grep -r -l "$KEYWORD" docs/api_details/ 2>/dev/null | while read file; do
        echo "  - $(basename $file)"
    done
fi
