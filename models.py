# [수정] String 추가!
from sqlalchemy import Column, Integer, Text, String, DateTime, Date
from database import Base

# 1. 정책 테이블 (기존)
class Policy(Base):
    __tablename__ = "being_test"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False)
    summary = Column(Text)
    period = Column(Text)
    link = Column(Text)
    genre = Column(Text)
    region = Column(Text)
    original_id = Column(Text)
    created_at = Column(DateTime)
    end_date = Column(Date)
    view_count = Column(Integer, default=0)

# 2. 사용자 테이블 (신규)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 여기서 String을 사용하기 때문에 맨 위 import에 String이 꼭 있어야 합니다.
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, nullable=True)
    region = Column(String, nullable=True)


# 3. 사용자 행동(좋아요/패스) 테이블 (신규)
from datetime import datetime

class UserAction(Base):
    __tablename__ = "users_action"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_email = Column(String, nullable=False, index=True) 
    policy_id = Column(Integer, nullable=False) # Policy 테이블 조인용
    type = Column(String, nullable=False) # 'like' 또는 'pass' 저장
    created_at = Column(DateTime, default=datetime.now)