# Railway 무료 배포 가이드

이 가이드는 FastAPI 애플리케이션을 Railway.app에 무료로 배포하는 방법을 설명합니다.

## Railway의 장점

- **무료 크레딧**: $5/월 (충분한 무료 사용량)
- **자동 배포**: GitHub 푸시 시 자동 재배포
- **간단한 설정**: 복잡한 설정 파일 불필요
- **PostgreSQL 자동 연결**: `DATABASE_URL` 자동 제공
- **SSL 자동 제공**: HTTPS 자동 설정

---

## 사전 준비

1. **GitHub 저장소 준비**
   - 코드가 GitHub에 푸시되어 있어야 합니다
   - 저장소 URL을 확인해두세요

2. **OAuth 키 준비** (선택사항)
   - Google OAuth: Client ID, Client Secret
   - Naver OAuth: Client ID, Client Secret
   - 배포 후 Railway URL로 리다이렉트 URI 업데이트 필요

---

## 배포 단계

### 1단계: Railway 계정 생성 및 GitHub 연결

1. **Railway 접속**
   - https://railway.app 접속
   - "Start a New Project" 클릭

2. **GitHub 계정 연결**
   - "Deploy from GitHub repo" 선택
   - GitHub 계정으로 로그인
   - 저장소 선택 화면에서 권한 부여

3. **저장소 선택**
   - 배포할 저장소 선택 (예: `parkjiho7111/final_project`)
   - Railway가 자동으로 프로젝트 생성

---

### 2단계: PostgreSQL 데이터베이스 추가

1. **데이터베이스 생성**
   - 프로젝트 대시보드에서 "New" 버튼 클릭
   - "Database" → "Add PostgreSQL" 선택

2. **자동 설정 확인**
   - Railway가 자동으로 `DATABASE_URL` 환경 변수를 설정합니다
   - Web Service에서 이 변수를 자동으로 사용할 수 있습니다

3. **데이터베이스 정보 확인** (선택사항)
   - PostgreSQL 서비스 클릭
   - "Variables" 탭에서 `DATABASE_URL` 확인 가능

---

### 3단계: Web Service 설정

1. **서비스 자동 감지**
   - Railway가 `requirements.txt`와 `Procfile`을 자동으로 감지합니다
   - 자동으로 빌드 및 시작 명령어를 설정합니다

2. **수동 설정** (필요한 경우)
   - Web Service → "Settings" 탭
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - (일반적으로 자동 설정되므로 수정 불필요)

3. **Python 버전 확인**
   - Railway는 `runtime.txt` 파일을 자동으로 읽습니다
   - 현재 설정: `python-3.12.12`

---

### 4단계: 환경 변수 설정

1. **Web Service 환경 변수 추가**
   - Web Service → "Variables" 탭 클릭
   - "New Variable" 버튼으로 다음 변수 추가:

#### OAuth 환경 변수 (필수)

```
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-secret
GOOGLE_REDIRECT_URI=https://your-app.up.railway.app/api/auth/google/callback

NAVER_CLIENT_ID=your-naver-client-id
NAVER_CLIENT_SECRET=your-naver-secret
NAVER_REDIRECT_URI=https://your-app.up.railway.app/api/auth/naver/callback
```

**중요**: 
- `GOOGLE_REDIRECT_URI`와 `NAVER_REDIRECT_URI`는 Railway에서 생성된 URL로 설정해야 합니다
- 배포 후 생성된 URL을 확인하고 업데이트하세요

#### 프로덕션 모드 설정 (선택사항)

```
ENV=production
```

이 변수를 설정하면 개발 모드의 자동 재시작 기능이 비활성화됩니다.

---

### 5단계: 배포 및 확인

1. **자동 배포 시작**
   - Railway가 GitHub 저장소를 감지하면 자동으로 배포를 시작합니다
   - "Deployments" 탭에서 배포 진행 상황 확인

2. **로그 확인**
   - Web Service → "Deployments" → 최신 배포 클릭
   - "View Logs" 버튼으로 빌드 및 실행 로그 확인
   - 다음 메시지 확인:
     - `✅ 데이터베이스 연결 성공 및 테이블 확인 완료`
     - `Application startup complete`
     - `Uvicorn running on`

3. **서비스 URL 확인**
   - Web Service → "Settings" 탭
   - "Generate Domain" 버튼 클릭하여 도메인 생성
   - 생성된 URL (예: `https://your-app.up.railway.app`)로 접속 테스트

4. **OAuth 리다이렉트 URI 업데이트**
   - Google Cloud Console:
     - APIs & Services → Credentials → OAuth 2.0 Client IDs
     - 승인된 리다이렉트 URI에 Railway URL 추가
   - Naver Developers:
     - 내 애플리케이션 → API 설정 → Callback URL에 Railway URL 추가

---

## 문제 해결

### 빌드 실패

**증상**: 배포가 실패하거나 빌드 오류 발생

**해결 방법**:
1. "Deployments" → "View Logs"에서 오류 메시지 확인
2. `requirements.txt`에 모든 의존성이 포함되어 있는지 확인
3. Python 버전이 `runtime.txt`와 일치하는지 확인

### 데이터베이스 연결 실패

**증상**: 로그에 `⚠️ 데이터베이스 연결 실패` 메시지

**해결 방법**:
1. PostgreSQL 서비스가 "Active" 상태인지 확인
2. Web Service의 "Variables" 탭에서 `DATABASE_URL`이 자동으로 설정되었는지 확인
3. PostgreSQL 서비스와 Web Service가 같은 프로젝트에 있는지 확인

### OAuth 로그인 실패

**증상**: 소셜 로그인 시 오류 발생

**해결 방법**:
1. 환경 변수의 리다이렉트 URI가 Railway URL과 정확히 일치하는지 확인
2. Google/Naver OAuth 콘솔에서 승인된 리다이렉트 URI에 Railway URL이 추가되었는지 확인
3. 환경 변수의 Client ID와 Secret이 올바른지 확인

### 서비스가 슬리프 모드로 진입

**증상**: 일정 시간 비활성 후 첫 요청이 느림

**해결 방법**:
- Railway 무료 플랜의 정상 동작입니다
- 첫 요청 시 자동으로 깨어나며, 이후 요청은 정상 속도로 처리됩니다
- 항상 활성 상태를 유지하려면 유료 플랜 사용 필요

---

## 자동 배포 설정

Railway는 GitHub 저장소와 연결되면 자동으로 배포됩니다:

1. **자동 배포 활성화**
   - Web Service → "Settings" → "Source" 탭
   - "Auto Deploy" 옵션이 활성화되어 있는지 확인

2. **배포 트리거**
   - `main` 브랜치에 푸시하면 자동 배포
   - Pull Request 머지 시에도 자동 배포

3. **수동 배포**
   - "Deployments" 탭 → "Redeploy" 버튼으로 수동 재배포 가능

---

## 추가 팁

### 환경 변수 관리

- 민감한 정보(비밀번호, API 키)는 환경 변수로 관리
- `.env` 파일은 로컬 개발용이며, Railway에서는 환경 변수로 설정

### 로그 모니터링

- "Deployments" 탭에서 실시간 로그 확인 가능
- 오류 발생 시 로그를 확인하여 문제 진단

### 비용 관리

- Railway 무료 크레딧: $5/월
- 사용량은 대시보드에서 확인 가능
- 크레딧 소진 시 알림 설정 가능

---

## 다음 단계

배포가 완료되면:

1. 웹사이트 접속 테스트
2. 데이터베이스 연결 확인
3. OAuth 로그인 테스트
4. 모든 기능 정상 작동 확인

문제가 발생하면 Railway 대시보드의 로그를 확인하거나, 이 가이드의 "문제 해결" 섹션을 참고하세요.

---

## 참고 자료

- Railway 공식 문서: https://docs.railway.app
- Railway Discord 커뮤니티: https://discord.gg/railway
- FastAPI 문서: https://fastapi.tiangolo.com
