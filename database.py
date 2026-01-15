from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Railway나 다른 플랫폼에서 제공하는 DATABASE_URL 우선 사용
# 없으면 개별 환경 변수로 조합
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Railway 등에서 제공하는 DATABASE_URL 사용
    # postgres:// 형식을 postgresql://로 변환 (SQLAlchemy 호환성)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
else:
    # 로컬 개발용: 개별 환경 변수 사용
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_HOST = os.getenv("DB_HOST", "postgresql_db")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "main_db")
    SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 엔진 생성 (Railway 환경에 최적화된 연결 풀 설정)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # 연결 유효성 검사
    pool_recycle=300     # 5분마다 연결 재활용
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
