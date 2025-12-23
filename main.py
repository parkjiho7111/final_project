import os
import json
import random
from typing import Optional, List
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, Text, ForeignKey, func, or_
from sqlalchemy.orm import sessionmaker, Session, declarative_base, relationship
import uvicorn

# ==================== [1. 환경 설정 및 DB 연결] ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv()  # .env 파일 로드

# .env에서 정보 가져오기 (없으면 기본값)
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password") # 본인 비번 확인
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "youth_policy")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# DB 엔진 생성
try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except Exception as e:
    print(f"🔥 DB 연결 실패: {e}")
    print("PostgreSQL 서버 상태와 .env 파일을 확인하게.")

# 템플릿/정적파일 경로 설정
template_dir = os.path.join(BASE_DIR, "templates")
if not os.path.exists(template_dir):
    template_dir = BASE_DIR  # templates 폴더 없으면 현재 폴더 사용

templates = Jinja2Templates(directory=template_dir)

# ==================== [2. DB 모델 정의] ====================

class User(Base):
    __tablename__ = "users_final"
    
    id = Column(Text, primary_key=True)
    password = Column(Text, nullable=False)
    name = Column(Text, nullable=False)
    region = Column(Text, nullable=True) # '서울', '경기' 등 한글 저장
    email = Column(Text, nullable=True)
    provider = Column(Text, default="local", nullable=True)

class Policy(Base):
    __tablename__ = "being_test"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False)
    summary = Column(Text)
    period = Column(Text)
    link = Column(Text)
    genre = Column(Text)   # 분야 (주거, 금융 등)
    region = Column(Text)  # 지역 (location -> region 매핑)

class UserAction(Base):
    __tablename__ = "user_actions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Text, ForeignKey("users_final.id"), nullable=False)
    policy_id = Column(Integer, ForeignKey("being_test.id"), nullable=False)
    action_type = Column(Text, nullable=False)  # 'like' or 'pass'

# ==================== [3. 유틸리티 및 매핑] ====================

# 프론트엔드 지역 ID (SVG) -> DB 저장용 한글 명칭
FRONT_TO_DB_REGION = {
    'national': '전국',
    'detail_seoul': '서울', 'detail_gyeonggi': '경기', 'detail_incheon': '인천',
    'gangwon': '강원', 'chungbug': '충북', 'chungnam': '충남', 'detail_chungnam': '충남',
    'jeonbug': '전북', 'jeonnam': '전남', 'detail_jeonnam': '전남',
    'gyeongbug': '경북', 'detail_gyeongbug': '경북',
    'gyeongnam': '경남', 'detail_gyeongnam': '경남',
    'jeju': '제주',
    'detail_busan': '부산', 'detail_daegu': '대구', 'detail_daejun': '대전',
    'detail_gwangju': '광주', 'detail_ulsan': '울산', 'detail_saejong': '세종'
}

# DB 한글 명칭 -> 프론트엔드 지역 ID (역매핑, 필요시 사용)
DB_TO_FRONT_REGION = {v: k for k, v in FRONT_TO_DB_REGION.items()}

def normalize_region_name(input_str: str) -> str:
    """
    JSON 파일 로딩 시 '전라남도' -> '전남' 등으로 변환.
    프론트에서 오는 ID ('detail_seoul')도 '서울'로 변환.
    """
    if not input_str: return "전국"
    
    # 1. 프론트 ID인 경우 매핑 테이블 사용
    if input_str in FRONT_TO_DB_REGION:
        return FRONT_TO_DB_REGION[input_str]
        
    # 2. 한글 긴 이름인 경우 (앞 2글자로 축약)
    # 예외: 충청북도->충북, 강원도->강원 등은 앞 2글자가 맞음.
    # 전라, 경상 등도 마찬가지.
    if len(input_str) >= 2:
        return input_str[:2]
        
    return input_str

def get_image_for_category(category: str) -> str:
    """카테고리에 맞는 랜덤 이미지 URL 반환"""
    cat_code = "welfare"
    if "주거" in category: cat_code = "housing"
    elif "취업" in category or "일자리" in category: cat_code = "job"
    elif "금융" in category: cat_code = "finance"
    elif "창업" in category: cat_code = "startup"
    elif "교육" in category: cat_code = "growth"
    
    return f"/static/images/card_images/{cat_code}_{random.randint(1, 5)}.webp"

# ==================== [4. 앱 수명주기 (데이터 적재)] ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. DB 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    # 2. policies_remake.json 데이터 로드 (DB가 비어있을 경우)
    db = SessionLocal()
    try:
        if db.query(Policy).first() is None:
            json_path = os.path.join(BASE_DIR, "policies_remake.json")
            if os.path.exists(json_path):
                print("🚀 [System] JSON 데이터 적재 시작...")
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    policies = []
                    for item in data:
                        raw_loc = item.get("location", "전국")
                        norm_reg = normalize_region_name(raw_loc)
                        
                        p = Policy(
                            title=item.get("title"),
                            summary=item.get("summary"),
                            period=item.get("period"),
                            link=item.get("link"),
                            genre=item.get("genre"),
                            region=norm_reg,
                            original_id=str(item.get("original_id", ""))
                        )
                        policies.append(p)
                    
                    db.add_all(policies)
                    db.commit()
                print(f"✅ [System] {len(policies)}개 정책 데이터 로드 완료!")
            else:
                print("⚠️ [Warning] policies_remake.json 파일이 없습니다.")
    except Exception as e:
        print(f"🔥 데이터 로드 중 오류: {e}")
        db.rollback()
    finally:
        db.close()
    
    yield

app = FastAPI(lifespan=lifespan)

# 정적 파일 마운트
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# DB 세션 의존성
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# ==================== [5. 페이지 렌더링 라우터] ====================

@app.get("/", response_class=HTMLResponse)
async def page_landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/{page_name}.html", response_class=HTMLResponse)
async def page_generic(page_name: str, request: Request):
    try:
        return templates.TemplateResponse(f"{page_name}.html", {"request": request})
    except:
        return templates.TemplateResponse(f"{page_name}", {"request": request})

# ==================== [6. API 엔드포인트] ====================

# --- 회원가입 ---
@app.post("/api/signup")
async def api_signup(
    id: str = Form(...), password: str = Form(...), 
    region: str = Form(...), # 프론트에서 '서울', '경기' 등으로 보낸다고 가정 (혹은 ID)
    name: str = Form("User"), email: str = Form(None), 
    db: Session = Depends(get_db)
):
    if db.query(User).filter(User.id == id).first():
        return JSONResponse(status_code=400, content={"message": "이미 존재하는 ID입니다."})
    
    # 지역명 정규화 ('detail_seoul' -> '서울')
    norm_region = normalize_region_name(region)
    
    new_user = User(
        id=id, password=password, name=name, 
        region=norm_region, email=email
    )
    db.add(new_user)
    db.commit()
    return {"message": "회원가입 완료! 로그인해주세요."}

# --- 로그인 ---
@app.post("/api/login")
async def api_login(id: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user or user.password != password:
        return JSONResponse(status_code=401, content={"detail": "아이디 또는 비밀번호 오류"})
    
    # 프론트엔드가 이 정보를 받아 localStorage에 저장함
    return {
        "user_id": user.id,
        "username": user.name,
        "region": user.region  # 예: '서울'
    }

# --- [핵심] 정책 카드 데이터 조회 ---
@app.get("/api/cards")
async def api_get_cards(
    region: Optional[str] = "national", 
    user_id: Optional[str] = None,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    1. 메인페이지(Tinder): region 파라미터로 호출 -> 해당 지역 + 전국 정책 + 섞어서 + 본거 제외
    2. 전체보기(All): category 또는 keyword로 검색
    """
    query = db.query(Policy)
    
    # 1. 틴더/메인 로직 (검색어가 없을 때)
    if not category and not keyword:
        # 지역 필터링 (선택 지역 + 전국)
        target_name = normalize_region_name(region)
        targets = [target_name, '전국', '중앙부처']
        query = query.filter(Policy.region.in_(targets))
        
        # 이미 본 카드(Like/Pass) 제외 (로그인 유저만)
        if user_id and user_id != 'guest':
            viewed_subq = db.query(UserAction.policy_id).filter(UserAction.user_id == user_id)
            query = query.filter(Policy.id.not_in(viewed_subq))
            
        # 랜덤 셔플 (최대 50개)
        policies = query.limit(50).all()
        random.shuffle(policies)
        
    # 2. 검색/전체보기 로직
    else:
        if category and category != 'all':
            query = query.filter(Policy.genre.like(f"%{category}%"))
        
        if keyword:
            search_pattern = f"%{keyword}%"
            query = query.filter(or_(
                Policy.title.like(search_pattern),
                Policy.summary.like(search_pattern)
            ))
            
        policies = query.limit(100).all()

    # JSON 응답 포맷 (프론트엔드 script.js createCardHTML과 호환)
    result = []
    for p in policies:
        result.append({
            "id": p.id,
            "title": p.title,
            "desc": p.summary or "상세 내용을 확인하세요.",
            "category": p.genre or "기타",
            "date": p.period or "상시 모집",
            "image": get_image_for_category(p.genre), # 랜덤 이미지 할당
            "link": p.link or "#",
            "region": p.region
        })
        
    return result

# --- 좋아요/패스 액션 저장 ---
@app.post("/api/action")
async def api_action(
    user_id: str = Form(...), 
    policy_id: int = Form(...), 
    action_type: str = Form(...), # 'like' or 'pass'
    db: Session = Depends(get_db)
):
    if user_id == 'guest': return {"status": "ok"}
    
    # 중복 체크
    exists = db.query(UserAction).filter_by(user_id=user_id, policy_id=policy_id).first()
    if exists:
        return {"status": "exists", "message": "이미 처리됨"}
        
    new_action = UserAction(
        user_id=user_id, policy_id=policy_id, action_type=action_type
    )
    db.add(new_action)
    db.commit()
    return {"status": "success"}

# --- 마이페이지: 찜한 목록 ---
@app.get("/api/user/{user_id}/liked")
async def api_get_liked(user_id: str, db: Session = Depends(get_db)):
    # Like한 액션 조회
    actions = db.query(UserAction).filter_by(user_id=user_id, action_type="like").all()
    policy_ids = [a.policy_id for a in actions]
    
    if not policy_ids: return []
    
    policies = db.query(Policy).filter(Policy.id.in_(policy_ids)).all()
    
    return [{
        "id": p.id,
        "title": p.title,
        "desc": p.summary,
        "category": p.genre,
        "date": p.period,
        "image": get_image_for_category(p.genre),
        "link": p.link
    } for p in policies]

# --- 마이페이지: 통계 ---
@app.get("/api/user/{user_id}/stats")
async def api_get_stats(user_id: str, db: Session = Depends(get_db)):
    liked_count = db.query(UserAction).filter_by(user_id=user_id, action_type="like").count()
    return {"liked_count": liked_count}

# --- 지도 통계 (Landing Page) ---
@app.get("/api/map/stats")
async def api_map_stats(db: Session = Depends(get_db)):
    """
    지역별 정책 개수 반환.
    프론트엔드 키: 'detail_seoul', 'gangwon' 등.
    DB 저장값: '서울', '강원' 등.
    -> DB 값을 집계한 후, 프론트엔드 키로 역변환하거나,
       프론트엔드에서 '서울'이라는 이름을 툴팁에 쓰므로,
       여기서는 {'서울': 100, '경기': 50} 형태로 반환하고 프론트 로직에 맞김.
    """
    rows = db.query(Policy.region, func.count(Policy.id)).group_by(Policy.region).all()
    
    # {'서울': 120, '경기': 500 ...} 형태
    stats = {r[0]: r[1] for r in rows if r[0]}
    
    # 프론트엔드가 ID('detail_seoul')를 키로 원한다면 변환 로직 추가 가능
    # 현재 script.js는 DB에 있는 한글 이름('name')과 매칭하므로,
    # 프론트엔드 REGION_DATA의 매핑 로직을 활용하기 위해
    # 여기선 2글자 키('서울', '경기')로 통일해서 주는 것이 안전함.
    
    return stats

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)