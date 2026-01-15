#!/usr/bin/env python3
"""
데이터베이스 테이블 생성 스크립트
회원가입을 위한 users 및 users_action 테이블을 생성합니다.
"""

import sys
import os
from sqlalchemy import inspect, text
from database import engine, Base
from models import User, UserAction, Policy

def check_table_exists(table_name):
    """테이블이 존재하는지 확인"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def get_table_columns(table_name):
    """테이블의 컬럼 정보 가져오기"""
    inspector = inspect(engine)
    if not check_table_exists(table_name):
        return []
    return inspector.get_columns(table_name)

def create_tables():
    """필요한 테이블 생성"""
    print("=" * 60)
    print("🚀 데이터베이스 테이블 생성 시작")
    print("=" * 60)
    
    try:
        # DB 연결 테스트
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ 데이터베이스 연결 성공")
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        print("\n💡 해결 방법:")
        print("   1. PostgreSQL 서버(Docker 컨테이너)가 실행 중인지 확인하세요")
        print("   2. .env 파일의 DB_HOST, DB_USER, DB_PASSWORD 설정을 확인하세요")
        return False
    
    # 테이블 생성
    tables_to_create = {
        'users': User,
        'users_action': UserAction,
        'being_test': Policy
    }
    
    created_count = 0
    existing_count = 0
    
    for table_name, model_class in tables_to_create.items():
        if check_table_exists(table_name):
            print(f"ℹ️  '{table_name}' 테이블이 이미 존재합니다.")
            existing_count += 1
            
            # 테이블 구조 확인
            columns = get_table_columns(table_name)
            print(f"   컬럼 수: {len(columns)}개")
            if columns:
                print(f"   주요 컬럼: {', '.join([c['name'] for c in columns[:5]])}")
        else:
            try:
                print(f"📝 '{table_name}' 테이블 생성 중...")
                model_class.__table__.create(bind=engine, checkfirst=True)
                print(f"✅ '{table_name}' 테이블 생성 완료")
                created_count += 1
            except Exception as e:
                print(f"❌ '{table_name}' 테이블 생성 실패: {e}")
    
    print("\n" + "=" * 60)
    print("📊 결과 요약")
    print("=" * 60)
    print(f"✅ 새로 생성된 테이블: {created_count}개")
    print(f"ℹ️  기존 테이블: {existing_count}개")
    print(f"📋 총 확인한 테이블: {len(tables_to_create)}개")
    
    # users 테이블 상세 확인
    if check_table_exists('users'):
        print("\n" + "=" * 60)
        print("👤 users 테이블 상세 정보")
        print("=" * 60)
        columns = get_table_columns('users')
        required_columns = ['id', 'email', 'name', 'password', 'provider']
        
        for col in columns:
            col_name = col['name']
            col_type = str(col['type'])
            nullable = "NULL 가능" if col['nullable'] else "NOT NULL"
            is_required = "⭐" if col_name in required_columns else ""
            print(f"  {is_required} {col_name}: {col_type} ({nullable})")
        
        # 필수 컬럼 확인
        existing_col_names = [col['name'] for col in columns]
        missing_cols = [col for col in required_columns if col not in existing_col_names]
        
        if missing_cols:
            print(f"\n⚠️  경고: 필수 컬럼이 누락되었습니다: {', '.join(missing_cols)}")
        else:
            print("\n✅ 모든 필수 컬럼이 존재합니다.")
    
    print("\n" + "=" * 60)
    print("🎉 작업 완료!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = create_tables()
    sys.exit(0 if success else 1)
