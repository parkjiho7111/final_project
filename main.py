import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# [중요 1] DB 테이블 생성을 위해 필요한 도구 가져오기
import models
from database import engine

# [중요 2] 우리가 만든 라우터들 가져오기
# (팀원들이 routers 폴더에 해당 파일들을 만들어야 에러가 안 납니다!)
from routers import landing, auth, about, main_page, all, mypage, admin, recommendation

# [중요 3] 서버 시작 시 DB에 없는 테이블(users 등) 자동 생성
# DB 연결 실패 시에도 서버는 시작되도록 에러 핸들링 추가
try:
    models.Base.metadata.create_all(bind=engine)
    print("✅ 데이터베이스 연결 성공 및 테이블 확인 완료")
except Exception as e:
    print(f"⚠️ 데이터베이스 연결 실패: {e}")
    print("⚠️ 서버는 시작되지만 데이터베이스 기능은 사용할 수 없습니다.")
    print("💡 해결 방법: PostgreSQL 서버(Docker 컨테이너)를 시작하거나 .env 파일의 DB_HOST를 확인하세요.")

app = FastAPI()

# --- [핵심 수정] 절대 경로 계산 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. 정적 파일 연결
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# 2. HTML 템플릿 연결
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# --- [중요 4] 라우터 등록 (API 및 페이지 기능 활성화) ---
app.include_router(landing.router)    # 지도 데이터 및 랜딩 기능
app.include_router(auth.router)       # 로그인/회원가입 기능
app.include_router(about.router)      # [NEW] About 페이지 담당자 기능
app.include_router(main_page.router)  # [NEW] Main 페이지 담당자 기능
app.include_router(all.router)        # [NEW] 전체 정책 페이지 기능
app.include_router(mypage.router)     # [NEW] 마이페이지 기능 (찜하기, 통계)
app.include_router(admin.router)      # [NEW] 관리자 페이지 기능 (admin.html)
app.include_router(recommendation.router) # [NEW] 추천/알림 시스템

# --- 페이지 접속 경로 설정 ---

# [1] 랜딩 페이지 (Root)
@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

# [2] 마이 페이지 (복구: API 라우터와 별개로 HTML 페이지 서빙 필요)
@app.get("/mypage.html")
async def read_mypage(request: Request):
    return templates.TemplateResponse("mypage.html", {"request": request})

# [3] 전체 정책 페이지 (아직 라우터 분리 안 됨 -> 여기서 직접 처리)
@app.get("/all.html")
async def read_all_policies(request: Request):
    return templates.TemplateResponse("all.html", {"request": request})

# ------------------------------------------------------------------
# [참고] main.html과 about.html은 어디 갔나요?
# 위에서 app.include_router(main_page.router)와 about.router를 등록했기 때문에,
# 이제 그 파일들(routers/main_page.py, routers/about.py) 안에서 페이지를 띄워줍니다.
# 중복을 막기 위해 여기서는 지웠습니다. (만약 라우터 파일이 없다면 에러가 납니다!)
# ------------------------------------------------------------------

# [5] 직접 실행(Debug)을 위한 코드 추가
# 이 코드가 있어야 'python main.py'로 실행했을 때 서버가 켜집니다.
if __name__ == "__main__":
    import uvicorn
    # reload=True는 코드 수정 시 자동 재시작 기능 (개발용)
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)