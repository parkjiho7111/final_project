from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 데이터베이스 연결 정보 가져오기
# Render 배포 시 환경 변수에서 자동으로 가져옴
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
# Render에서는 DB_HOST가 자동으로 설정되므로, 로컬 개발용 기본값만 설정
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "main_db")

# PostgreSQL 연결 URL
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 엔진 생성 (Render 배포를 위한 연결 풀 설정 추가)
# pool_pre_ping=True: 연결이 끊어졌을 때 자동으로 재연결
# pool_recycle=300: 5분마다 연결을 재생성하여 연결 타임아웃 방지
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  # SQL 쿼리 로그 출력 여부 (프로덕션에서는 False)
)

# 세션 로컬 클래스 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성 (models.py에서 상속받아 사용)
Base = declarative_base()

# DB 세션 의존성 함수 (라우터에서 사용)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
