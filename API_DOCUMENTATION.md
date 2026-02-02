# 🏥 Medical Service API 명세서 - Final Demo Version

## 📌 서버 정보
- **Base URL**: `http://127.0.0.1:8000`
- **버전**: Final Demo Version (Updated: 942a4c9)
- **CORS**: 모든 Origin 허용 (개발용)
- **자동 문서**:
  - Swagger UI: http://127.0.0.1:8000/docs
  - ReDoc: http://127.0.0.1:8000/redoc

## 🔄 최신 업데이트 (942a4c9)
- **병원 추천 API**: 한/영 이중 언어 지원 (`reason_kr`, `reason_en`)
- **의약품 검색 API**: 한/영 이중 언어 지원 + 이미지 추가 (`image_url`)
- **의약품 검색 API**: **동일 주성분 약품 추천 기능 추가** ⭐ NEW
- **SerpAPI 연동**: 약품 패키지 이미지 자동 검색 기능
- **다국어 지원**: 모든 주요 AI 응답이 한국어/영어 동시 제공

---

## 📋 API 목록

| 번호 | 메서드 | 엔드포인트 | 설명 |
|------|--------|-----------|------|
| 1 | POST | `/api/signup` | 회원가입 |
| 2 | POST | `/api/login` | 로그인 |
| 3 | POST | `/api/generate-chart` | 차트 생성 (저장 X) |
| 4 | POST | `/api/save-chart` | 차트 저장 |
| 5 | POST | `/api/estimate-cost` | 진료비 안내 (AI) |
| 6 | POST | `/api/recommend-hospitals` | 병원 추천 (카카오맵) |
| 7 | POST | `/api/search-medicine` | 의약품 검색 (AI) |
| 8 | POST | `/api/update-user` | 회원 정보 수정 |
| 9 | GET | `/api/history/{user_id}` | 차트 히스토리 조회 |
| 10 | GET | `/api/users` | 전체 사용자 조회 (디버깅) |

---

## 1️⃣ 회원가입 API

### `POST /api/signup`

사용자 회원가입을 처리합니다.

#### 📥 Request Body
```json
{
  "name": "홍길동",
  "birth_date": "1990-01-01",
  "phone_number": "010-1234-5678",
  "insurance_info": "NHIS",
  "allergies": "None",
  "medications": "None",
  "medical_history": "None",
  "user_id": "gildong123",
  "password": "password123",
  "address": "서울시 강남구",
  "email": "gildong@example.com"
}
```

#### 📝 Request Fields

| 필드 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| `name` | string | ✅ | - | 사용자 이름 |
| `birth_date` | string | ✅ | - | 생년월일 (YYYY-MM-DD) |
| `phone_number` | string | ✅ | - | 전화번호 |
| `insurance_info` | string | ✅ | - | 보험 정보 (NHIS/Private) |
| `allergies` | string | ❌ | "None" | 알러지 정보 |
| `medications` | string | ❌ | "None" | 복약 정보 |
| `medical_history` | string | ❌ | "None" | 과거 치료 이력 |
| `user_id` | string | ✅ | - | 로그인 아이디 |
| `password` | string | ✅ | - | 비밀번호 |
| `address` | string | ❌ | null | 주소 |
| `email` | string | ❌ | null | 이메일 |

#### 📤 Response (Success - 200)
```json
{
  "message": "Success",
  "user_name": "홍길동"
}
```

#### ❌ Response (Error - 400)
```json
{
  "detail": "이미 존재하는 아이디입니다."
}
```

---

## 2️⃣ 로그인 API

### `POST /api/login`

사용자 로그인을 처리합니다.

#### 📥 Request Body
```json
{
  "user_id": "gildong123",
  "password": "password123"
}
```

#### 📤 Response (Success - 200)
```json
{
  "message": "Login Success",
  "user_id": "gildong123",
  "user_name": "홍길동"
}
```

#### ❌ Response (Error - 401)
```json
{
  "detail": "존재하지 않는 아이디입니다."
}
```
```json
{
  "detail": "비밀번호가 틀렸습니다."
}
```

---

## 3️⃣ 차트 생성 API (저장 안 함)

### `POST /api/generate-chart`

AI가 의료 예진표를 생성합니다. **저장하지 않고** 결과만 반환합니다.  
사용자가 수정 후 `/api/save-chart`로 저장해야 합니다.

#### 🔄 워크플로우
```
1. /api/generate-chart → AI가 차트 생성 (DB 저장 X)
2. 프론트엔드에서 사용자가 수정
3. /api/save-chart → 최종 차트 저장
```

#### 📥 Request Body
```json
{
  "user_id": "gildong123",
  "selected_symptoms": ["두통", "발열", "오한"],
  "detail_description": "어제 저녁부터 머리가 지끈거리고 열이 38도까지 올랐습니다."
}
```

#### 📝 Request Fields

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `user_id` | string | ✅ | 사용자 ID |
| `selected_symptoms` | array[string] | ✅ | 선택된 증상 목록 |
| `detail_description` | string | ✅ | 증상 상세 설명 |

#### 📤 Response (Success - 200)
```json
{
  "chart": "=== 기초 예진 기록 (Medical History Taking) ===\n\n1. 주호소 (Chief Complaint, C.C)\n   - 두통 및 발열 (Onset: 어제 저녁)\n\n2. 현병력 (Present Illness, P.I)\n   * 발병 시기 (Onset): 24시간 전\n   * 부위 및 양상 (Location & Character): 두통 (Headache), 지끈거림\n   * 강도 및 빈도 (Severity & Frequency): 고열 38°C\n   * 동반 증상 (Associated Symptoms): 오한 (Chills)\n   * 악화/완화 요인 (Aggravating/Relieving Factors): 명시되지 않음\n\n3. 특이사항 (Past History & Social Hx)\n   * 기저질환: None\n   * 복용약물: None\n   * 알러지: None\n   * 기타: 없음\n================================================"
}
```

#### ❌ Response (Error - 404)
```json
{
  "detail": "유저 없음"
}
```

---

## 4️⃣ 차트 저장 API

### `POST /api/save-chart`

사용자가 수정한 최종 차트를 히스토리에 저장합니다.

#### 📥 Request Body
```json
{
  "user_id": "gildong123",
  "symptoms": ["두통", "발열", "오한"],
  "detail": "어제 저녁부터 머리가 지끈거리고 열이 38도까지 올랐습니다.",
  "final_chart_text": "=== 수정된 최종 차트 ===\n..."
}
```

#### 📝 Request Fields

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `user_id` | string | ✅ | 사용자 ID |
| `symptoms` | array[string] | ✅ | 증상 목록 |
| `detail` | string | ✅ | 상세 설명 |
| `final_chart_text` | string | ✅ | 사용자가 수정한 최종 차트 |

#### 📤 Response (Success - 200)
```json
{
  "message": "Saved",
  "history_count": 3
}
```

---

## 5️⃣ 진료비 안내 API

### `POST /api/estimate-cost`

사용자의 보험 정보를 기반으로 예상 진료비를 안내합니다.

#### 📥 Request Body
```json
"gildong123"
```
**⚠️ 주의**: JSON 문자열 형태로 전송

#### 📤 Response (Success - 200)
```json
{
  "cost_guide": "=== 💰 Estimated Cost & Guide ===\n1. Insurance Analysis: NHIS (National Health Insurance)\n2. 🏥 Local Clinic (Primary):\n   - Payment: Co-payment (본인부담금)\n   - Est. Cost: 5,000~15,000 KRW\n   - Tip: 가장 저렴하고 빠른 선택\n3. 🏥 University Hospital (Tertiary):\n   - Payment: Referral Letter needed\n   - Est. Cost: 20,000~50,000+ KRW\n   - Procedure: 의뢰서 필요\n================================"
}
```

---

## 6️⃣ 병원 추천 API (카카오맵 연동)

### `POST /api/recommend-hospitals`

사용자의 위치와 증상을 기반으로 실제 병원을 검색합니다.

#### 📥 Request Body
```json
{
  "user_id": "gildong123",
  "symptoms": "배가 너무 아프고 구토를 해요",
  "latitude": 37.5665,
  "longitude": 126.9780,
  "radius": 2000
}
```

#### 📝 Request Fields

| 필드 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| `user_id` | string | ✅ | - | 사용자 ID |
| `symptoms` | string | ✅ | - | 증상 설명 |
| `latitude` | float | ✅ | - | 위도 |
| `longitude` | float | ✅ | - | 경도 |
| `radius` | int | ❌ | 2000 | 검색 반경 (미터) |

#### 📤 Response (Success - 200)
```json
{
  "recommended_department": "소화기내과",
  "urgency_level": "High",
  "reason_kr": "복통과 구토는 소화기 문제일 가능성이 높습니다.",
  "reason_en": "Abdominal pain and vomiting may indicate digestive issues.",
  "hospitals": [
    {
      "name": "서울아산병원",
      "department": "소화기내과",
      "distance": "850m",
      "address": "서울시 송파구 올림픽로 43길 88",
      "phone": "02-3010-3114",
      "url": "http://place.map.kakao.com/12345",
      "x": 127.0856,
      "y": 37.5267
    }
  ]
}
```

#### 📋 Response Fields

| 필드 | 타입 | 설명 |
|------|------|------|
| `recommended_department` | string | AI가 추천한 진료과 |
| `urgency_level` | string | 응급도 (Emergency/High/Moderate/Low) |
| `reason_kr` | string | 추천 이유 (한국어) ⭐ NEW |
| `reason_en` | string | 추천 이유 (영어) ⭐ NEW |
| `hospitals` | array | 실제 병원 목록 (최대 5개) |
| `hospitals[].name` | string | 병원 이름 |
| `hospitals[].department` | string | 진료과 |
| `hospitals[].distance` | string | 거리 (미터) |
| `hospitals[].address` | string | 주소 |
| `hospitals[].phone` | string | 전화번호 |
| `hospitals[].url` | string | 카카오맵 URL |
| `hospitals[].x` | float | 경도 |
| `hospitals[].y` | float | 위도 |

---

## 7️⃣ 의약품 검색 API

### `POST /api/search-medicine`

약품명 또는 증상을 입력하면 AI가 의약품 정보를 **한국어/영어**로 제공합니다.

#### 📥 Request Body
```json
{
  "user_id": "gildong123",
  "keyword": "타이레놀"
}
```

#### 📝 Request Fields

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `user_id` | string | ✅ | 사용자 ID |
| `keyword` | string | ✅ | 약품명 또는 증상 |

#### 📤 Response (Success - 200) ⭐ 변경됨
```json
{
  "medicine_info_kr": "=== 약품 정보 ===\n\n1. 약품명 (한글/영문):\n   - 타이레놀 / Tylenol\n\n2. 분류: 일반의약품 (OTC)\n   - 약국에서 구매 가능\n\n3. 주요 용도:\n   - 해열제, 진통제\n\n4. 안전성 확인 (알러지: 없음): 안전\n   - 알려진 부작용 없음\n\n5. 예상 가격 (한국):\n   - 3,000 ~ 8,000원\n\n6. 복용 팁:\n   - 4-6시간마다 1-2정 복용\n   - 하루 8정 초과 금지\n\n7. 동일 주성분 약:\n   - 판피린 (동화약품)\n   - 펜잘 (한미약품)\n   - 게보린 (삼진제약)\n   - 이지엔6 (현대약품)\n\n* 주의: AI 예측입니다. 약사와 상담하세요.",
  
  "medicine_info_en": "=== Medicine Information ===\n\n1. Name (KR/EN):\n   - 타이레놀 / Tylenol\n\n2. Classification: OTC\n   - Available at Pharmacy\n\n3. Primary Use:\n   - Pain reliever, fever reducer\n\n4. Safety Check (Allergy: None): SAFE\n   - No known conflicts\n\n5. Est. Price (Korea):\n   - 3,000 ~ 8,000 KRW\n\n6. Usage Tip:\n   - Take 1-2 pills every 4-6 hours\n   - Do not exceed 8 pills per day\n\n7. Medicines with Same Active Ingredient:\n   - Panpyrin (Dongwha Pharm)\n   - Fenzal (Hanmi Pharm)\n   - Geworin (Samjin Pharm)\n   - EasyN6 (Hyundai Pharm)\n\n* Disclaimer: AI estimate. Consult a pharmacist.",
  
  "image_url": "https://example.com/tylenol-package.jpg"
}
```

#### 📝 Response Fields

| 필드 | 타입 | 설명 |
|------|------|------|
| `medicine_info_kr` | string | 약품 정보 (한국어) |
| `medicine_info_en` | string | 약품 정보 (영어) |
| `image_url` | string \| null | 약품 패키지 이미지 URL (SerpAPI 검색) ⭐ NEW |

#### 🤖 AI 특징
- **스마트 검색**: 약품명 또는 증상으로 검색 가능
- **분류**: OTC(일반의약품) vs RX(처방의약품) 구분
- **알러지 체크**: 사용자의 알러지 정보와 비교
- **가격 정보**: 한국 약국 기준 예상 가격
- **복용 방법**: 간단한 복용 팁 제공
- **동일 주성분 약품**: 같은 성분의 대체 약품 4~5개 추천 ⭐ NEW
- **이중 언어**: 한국어/영어 동시 제공
- **이미지 검색**: SerpAPI를 통한 약품 패키지 이미지 자동 제공

#### 💡 동일 주성분 약품 추천 (NEW)
검색한 약품과 동일한 주성분을 포함하는 다른 제조사의 약품을 추천합니다.
- **형식**: `약품명 (제약회사)` 형태로 제공
- **개수**: 4~5개 추천
- **용도**: 가격 비교, 구매 가능성 증대, 대체 약품 선택 시 참고

**예시:**
- 타이레놀 검색 시 → 판피린, 펜잘, 게보린, 이지엔6 등 추천
- 모두 아세트아미노펜 성분 함유

#### 🔧 기술 스택
- **AI**: OpenAI GPT-4o-mini
- **이미지 검색**: SerpAPI (Google Images)
- **이미지 검색 쿼리**: `{keyword} + "medicine package"`

---

## 8️⃣ 회원 정보 수정 API

### `POST /api/update-user`

사용자의 개인 정보를 수정합니다.

#### 📥 Request Body
```json
{
  "user_id": "gildong123",
  "phone_number": "010-9999-8888",
  "insurance_info": "Private",
  "address": "서울시 서초구"
}
```

#### 📝 Request Fields

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `user_id` | string | ✅ | 사용자 ID |
| `phone_number` | string | ❌ | 새 전화번호 |
| `insurance_info` | string | ❌ | 새 보험 정보 |
| `address` | string | ❌ | 새 주소 |

**⚠️ 주의**: 변경하려는 필드만 포함하면 됩니다.

#### 📤 Response (Success - 200)
```json
{
  "message": "Updated successfully"
}
```

---

## 9️⃣ 히스토리 조회 API

### `GET /api/history/{user_id}`

사용자의 과거 차트 저장 기록을 조회합니다.

#### 📥 Request Parameters

| 파라미터 | 위치 | 타입 | 필수 | 설명 |
|----------|------|------|------|------|
| `user_id` | path | string | ✅ | 사용자 ID |

#### 📌 Request Example
```
GET http://127.0.0.1:8000/api/history/gildong123
```

#### 📤 Response (Success - 200)
```json
{
  "history": [
    {
      "date": "2026-01-30 14:45",
      "symptoms": ["두통", "발열"],
      "detail": "어제부터 증상 시작",
      "result_text": "=== 기초 예진 기록 ===\n..."
    }
  ]
}
```

---

## 🔟 전체 사용자 조회 API (디버깅용)

### `GET /api/users`

서버에 저장된 모든 사용자 정보를 조회합니다.

#### ⚠️ 주의사항
**개발/디버깅 전용입니다!**
- 프로덕션 환경에서는 반드시 제거하거나 인증 추가 필요
- 비밀번호가 평문으로 노출됨

#### 📥 Request
```
GET http://127.0.0.1:8000/api/users
```

#### 📤 Response (Success - 200)
```json
{
  "gildong123": {
    "name": "홍길동",
    "birth_date": "1990-01-01",
    "phone_number": "010-1234-5678",
    "insurance_info": "NHIS",
    "allergies": "None",
    "medications": "None",
    "medical_history": "None",
    "user_id": "gildong123",
    "password": "password123",
    "chart_history": [...]
  }
}
```

---

## 🔧 기술 스택

| 항목 | 기술 |
|------|------|
| **프레임워크** | FastAPI |
| **서버** | Uvicorn (Hot Reload) |
| **AI 모델** | OpenAI GPT-4o-mini |
| **지도 API** | 카카오맵 로컬 검색 |
| **데이터 저장** | In-Memory (개발용) |
| **환경변수** | python-dotenv |

---

## 🚀 서버 실행 방법

### 1. 패키지 설치
```bash
pip install fastapi uvicorn openai python-dotenv requests
```

### 2. 환경변수 설정
`.env` 파일 생성 또는 환경변수 설정:
```bash
export OPENAI_API_KEY="your-openai-key"
export KAKAO_API_KEY="your-kakao-rest-api-key"
```

### 3. 서버 실행
```bash
cd project-server
python main.py
```

### 4. 서버 확인
- 서버 주소: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs

---

## 🧪 테스트 방법

### curl 예시

#### 1. 회원가입
```bash
curl -X POST http://127.0.0.1:8000/api/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "홍길동",
    "birth_date": "1990-01-01",
    "phone_number": "010-1234-5678",
    "insurance_info": "NHIS",
    "user_id": "gildong123",
    "password": "password123"
  }'
```

#### 2. 로그인
```bash
curl -X POST http://127.0.0.1:8000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "gildong123",
    "password": "password123"
  }'
```

#### 3. 차트 생성
```bash
curl -X POST http://127.0.0.1:8000/api/generate-chart \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "gildong123",
    "selected_symptoms": ["두통", "발열"],
    "detail_description": "어제부터 머리가 아프고 열이 납니다."
  }'
```

#### 4. 병원 추천 (서울시청 기준)
```bash
curl -X POST http://127.0.0.1:8000/api/recommend-hospitals \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "gildong123",
    "symptoms": "배가 아파요",
    "latitude": 37.5665,
    "longitude": 126.9780,
    "radius": 2000
  }'
```

#### 5. 의약품 검색
```bash
curl -X POST http://127.0.0.1:8000/api/search-medicine \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "gildong123",
    "keyword": "타이레놀"
  }'
```

---

## 🔒 보안 고려사항

### ⚠️ 현재 구현의 보안 이슈

| 이슈 | 현재 상태 | 프로덕션 조치 |
|------|-----------|---------------|
| 비밀번호 | 평문 저장 ❌ | bcrypt 해싱 필수 |
| 인증 | 없음 ❌ | JWT 또는 세션 필요 |
| HTTPS | HTTP만 ❌ | HTTPS 인증서 필수 |
| CORS | 모든 Origin ❌ | 특정 도메인만 허용 |
| API 키 | 환경변수 노출 ❌ | Secret Manager 사용 |
| 디버그 API | 공개 ❌ | `/api/users` 제거 |

---

## 📞 문의 및 지원

- **프로젝트**: Medical Service API
- **버전**: Final Demo Version
- **최종 업데이트**: 2026-01-30
- **GitHub**: team-sudo-all/project-server

---

## 📝 변경 이력

### Final Demo Version (2026-01-30)
- ✨ 의약품 검색 기능 추가 (`/api/search-medicine`)
- 🐛 카카오맵 API 디버그 로그 추가
- 🔄 모델 간소화 (키/몸무게 필드 제거)
- 📝 코드 주석 및 정리

### v2.0 (2026-01-30)
- ✨ 차트 생성/저장 분리
- ✨ 카카오맵 API 연동
- ✨ 회원 정보 수정 기능

### v1.0
- ✅ 기본 회원가입/로그인
- ✅ AI 차트 생성
- ✅ 진료비 안내
