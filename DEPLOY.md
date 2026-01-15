# Render 배포 가이드

## 🚀 배포 방법

### 방법 1: Render 웹 대시보드 사용 (가장 쉬움)

1. **GitHub에 코드 푸시**
   ```bash
   git push origin main
   ```

2. **Render 대시보드 접속**
   - https://dashboard.render.com 접속
   - GitHub 계정으로 로그인

3. **새 Web Service 생성**
   - "New +" 버튼 클릭
   - "Web Service" 선택
   - GitHub 저장소 연결: `parkjiho7111/final_project`
   - Branch: `main` 선택

4. **서비스 설정**
   - **Name**: `being-geul-platform`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free 선택

5. **PostgreSQL 데이터베이스 생성**
   - "New +" → "PostgreSQL" 선택
   - **Name**: `being-geul-db`
   - **Database**: `main_db`
   - **User**: `admin`
   - **Plan**: Free 선택
   - "Create Database" 클릭

6. **환경 변수 설정**
   Web Service의 "Environment" 탭에서 다음 변수 추가:
   
   **데이터베이스 연결 정보** (PostgreSQL 서비스에서 복사):
   ```
   DB_HOST=<PostgreSQL 내부 호스트>
   DB_PORT=5432
   DB_NAME=main_db
   DB_USER=admin
   DB_PASSWORD=<PostgreSQL 비밀번호>
   ```
   
   **OAuth 설정** (.env 파일에서 복사):
   ```
   GOOGLE_CLIENT_ID=<your-google-client-id>
   GOOGLE_CLIENT_SECRET=<your-google-secret>
   GOOGLE_REDIRECT_URI=https://your-app.onrender.com/api/auth/google/callback
   NAVER_CLIENT_ID=<your-naver-client-id>
   NAVER_CLIENT_SECRET=<your-naver-secret>
   NAVER_REDIRECT_URI=https://your-app.onrender.com/api/auth/naver/callback
   ```

7. **배포 시작**
   - "Create Web Service" 클릭
   - 자동으로 빌드 및 배포 시작
   - 완료되면 URL 확인 (예: `https://being-geul-platform.onrender.com`)

### 방법 2: render.yaml 사용 (Infrastructure as Code)

Render CLI를 사용하여 render.yaml 파일로 배포:

```bash
# 1. GitHub에 코드 푸시
git push origin main

# 2. Render에서 Blueprint 생성 및 배포
# (웹 대시보드에서 "New Blueprint" 선택 후 GitHub 저장소 연결)
```

## 📋 배포 전 체크리스트

- [x] `render.yaml` 파일 생성 완료
- [x] `Procfile` 생성 완료
- [x] `runtime.txt` 생성 완료
- [x] `main.py` 포트 환경 변수 지원 추가
- [x] `.gitignore` 업데이트
- [ ] GitHub에 코드 푸시 완료
- [ ] Render에서 PostgreSQL 데이터베이스 생성
- [ ] 환경 변수 설정 완료
- [ ] OAuth 리다이렉트 URL 업데이트 (Render URL로)

## 🔧 문제 해결

### 배포 실패 시 체크리스트

**1. 빌드 실패:**
- `requirements.txt` 확인 (psycopg2-binary만 사용, psycopg2 제거)
- Python 버전 확인 (`runtime.txt`: python-3.12.7)
- 빌드 로그에서 구체적인 오류 메시지 확인

**2. 시작 실패:**
- `Procfile` 명령어 확인: `web: uvicorn main:app --host 0.0.0.0 --port $PORT`
- 포트 환경 변수 사용 확인 (`$PORT`)
- 서비스 로그에서 시작 오류 확인

**3. 데이터베이스 연결 실패:**
- PostgreSQL 서비스가 실행 중인지 확인
- `render.yaml`에서 데이터베이스 자동 연결 설정 확인
- 환경 변수가 올바르게 설정되었는지 확인
- `database.py`의 연결 풀 설정 확인 (`pool_pre_ping=True`)

**4. 일반적인 오류:**
- **"Module not found"**: `requirements.txt`에 패키지 추가
- **"Port already in use"**: `$PORT` 환경 변수 사용 확인
- **"Database connection refused"**: DB_HOST, DB_PORT, DB_NAME 확인
- **"psycopg2 error"**: `psycopg2-binary`만 사용 (일반 `psycopg2` 제거)

## 📝 참고

- Render 무료 티어: 750시간/월
- 무료 티어는 15분 비활성 시 슬리프 모드
- PostgreSQL 무료 티어: 90일 후 자동 백업 필요
