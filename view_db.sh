#!/bin/bash
# SQLite 데이터베이스 간편 조회 스크립트

echo "================================"
echo "Being Test Database Viewer"
echo "================================"
echo ""

# 데이터베이스 파일 확인
if [ ! -f "being_test.db" ]; then
    echo "❌ being_test.db 파일을 찾을 수 없습니다!"
    exit 1
fi

echo "✅ 데이터베이스 파일 발견: being_test.db"
echo ""

# SQLite3로 데이터베이스 열기
echo "📊 데이터베이스를 열고 있습니다..."
echo ""
echo "사용 가능한 명령어:"
echo "  .tables          - 테이블 목록 보기"
echo "  .schema          - 테이블 구조 보기"
echo "  SELECT * FROM being_test LIMIT 10;  - 처음 10개 레코드 보기"
echo "  .quit            - 종료"
echo ""
echo "================================"
echo ""

sqlite3 being_test.db
