# 🚀 Medical Service API - Render.com 배포 가이드

## 📋 배포 전 준비사항

### 1. 필요한 API 키
- **OpenAI API Key**: GPT-4o-mini 사용
- **Kakao Map API Key**: 병원 검색 기능
- **SerpAPI Key**: 약품 이미지 검색

### 2. GitHub 저장소
- 이 프로젝트가 GitHub에 push 되어 있어야 합니다.

---

## 🔧 Render.com 배포 단계

### Step 1: Render.com 회원가입
1. https://render.com 접속
2. GitHub 계정으로 회원가입

### Step 2: 새 Web Service 생성
1. Dashboard에서 **"New +"** 클릭
2. **"Web Service"** 선택
3. GitHub 저장소 연결 (Render.com에 GitHub 액세스 권한 부여)
4. 이 저장소(`project-server`) 선택

### Step 3: 서비스 설정
다음 정보를 입력하세요:

| 항목 | 값 |
|------|-----|
| **Name** | `medical-service-api` (또는 원하는 이름) |
| **Region** | `Singapore` (한국과 가까운 서버) |
| **Branch** | `main` |
| **Root Directory** | 비워두기 (또는 `project-server`) |
| **Environment** | `Python 3` |
| **Build Command** | `cd project-server && pip install -r ../requirements.txt` |
| **Start Command** | `cd project-server && uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | `Free` |

### Step 4: 환경변수 설정 ⚠️ 중요!
**Environment Variables** 섹션에서 다음 3개를 추가하세요:

```
OPENAI_API_KEY = sk-proj-GhQGzDD3e5wP8yzf1twx25ySEuMCDmnma41_5bio...
KAKAO_API_KEY = b0db93725d369d5b4188b7b274cc8d19
SERPAPI_KEY = a35ae2418c601e239f8c1e0d563a0e0dcfc0acbc6bf40adca6cdcd8afc3ce1b5
```

### Step 5: 배포 시작
1. **"Create Web Service"** 클릭
2. 자동으로 빌드 및 배포가 시작됩니다 (약 2~3분 소요)
3. 배포 완료 후 URL이 생성됩니다:
   - 예: `https://medical-service-api.onrender.com`

---

## ✅ 배포 확인

배포가 완료되면 다음 URL로 확인할 수 있습니다:

- **API 문서 (Swagger UI)**: `https://your-app.onrender.com/docs`
- **API 문서 (ReDoc)**: `https://your-app.onrender.com/redoc`
- **Health Check**: `https://your-app.onrender.com/api/users`

---

## 🔄 자동 배포 (CI/CD)

GitHub에 새 코드를 push하면 자동으로 재배포됩니다!

```bash
git add .
git commit -m "Update API"
git push origin main
```

→ Render.com이 자동으로 감지하고 새 버전을 배포합니다.

---

## ⚠️ 주의사항

### 1. Free Tier 제한
- **Sleep 모드**: 15분간 요청이 없으면 서버가 자동 종료됩니다.
- **첫 요청**: Sleep 모드에서 깨어나는 데 30초~1분 소요됩니다.
- **해결 방법**: 
  - 유료 플랜 사용 ($7/월부터)
  - 또는 UptimeRobot 같은 서비스로 5분마다 ping

### 2. CORS 설정
프론트엔드 배포 후, `main.py`의 CORS 설정을 수정하세요:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-url.vercel.app",  # 실제 프론트엔드 URL
        "http://localhost:3000"  # 로컬 개발용
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. 환경변수 보안
- `.env` 파일은 절대 GitHub에 push하지 마세요!
- `.gitignore`에 `.env`가 포함되어 있는지 확인하세요.

---

## 🐛 문제 해결

### 배포 실패 시
1. Render.com의 **Logs** 탭에서 에러 메시지 확인
2. `requirements.txt`에 모든 패키지가 포함되어 있는지 확인
3. Python 버전 확인 (Python 3.9+ 필요)

### API 키 오류
- Render.com Dashboard → Settings → Environment → 키 값 재확인
- 키 값에 공백이나 따옴표가 포함되지 않았는지 확인

### 500 Internal Server Error
- Logs에서 Python traceback 확인
- 환경변수가 제대로 설정되었는지 확인

---

## 📚 추가 자료

- [Render.com 공식 문서](https://render.com/docs)
- [FastAPI 배포 가이드](https://fastapi.tiangolo.com/deployment/)
- [Render Python 가이드](https://render.com/docs/deploy-fastapi)

---

## 💡 배포 후 프론트엔드 연결

배포된 API URL을 프론트엔드 코드에서 사용하세요:

```javascript
// 프론트엔드 (예: React)
const API_BASE_URL = "https://medical-service-api.onrender.com";

// API 호출 예시
const response = await fetch(`${API_BASE_URL}/api/recommend-hospitals`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: "user123",
    symptoms: "두통",
    latitude: 37.5665,
    longitude: 126.9780
  })
});
```

---

**배포 성공하시길 바랍니다! 🎉**

문제가 발생하면 Render.com의 Logs를 확인하거나 문의해주세요.
