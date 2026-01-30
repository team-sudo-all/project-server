from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

# models.py와 logic.py에서 모든 클래스와 함수 가져오기
from models import * 
from logic import * 
app = FastAPI()

# CORS 설정 (프론트엔드 통신 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 메모리 DB (서버 끄면 초기화)
fake_users_db = {}

# ==========================================
# 1. 회원가입 (기존 유지)
# ==========================================
@app.post("/api/signup")
def signup(user: UserSignupRequest):
    if user.user_id in fake_users_db:
        raise HTTPException(status_code=400, detail="이미 존재하는 아이디입니다.")
    
    user_dict = user.dict()
    user_dict["chart_history"] = [] # 히스토리 공간 생성
    fake_users_db[user.user_id] = user_dict
    
    print(f"✅ 가입 완료: {user.name} (ID: {user.user_id})")
    return {"message": "Success", "user_name": user.name}

# ==========================================
# 2. 로그인 (기존 유지)
# ==========================================
@app.post("/api/login")
def login(user: UserLoginRequest):
    if user.user_id not in fake_users_db:
        raise HTTPException(status_code=401, detail="존재하지 않는 아이디입니다.")
    
    stored = fake_users_db[user.user_id]
    if stored['password'] != user.password:
        raise HTTPException(status_code=401, detail="비밀번호가 틀렸습니다.")
    
    return {
        "message": "Login Success", 
        "user_id": user.user_id, 
        "user_name": stored['name']
    }

# ==========================================
# 3. 차트 생성 (수정됨: 저장하지 않고 결과만 반환)
# - 이유: 사용자가 내용을 수정(Edit)할 수 있어야 하므로
# ==========================================
@app.post("/api/generate-chart")
def generate_chart_only(request: SymptomRequest):
    if request.user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="유저 없음")
    
    user_info = fake_users_db[request.user_id]
    print(f"🤖 차트 생성 중... (저장 대기)")
    
    # logic.py의 AI 함수 호출
    chart_result = generate_medical_chart(user_info, request)
    return {"chart": chart_result}

# ==========================================
# 4. 차트 최종 저장 (신규 추가: 수정 완료 후 호출)
# ==========================================
@app.post("/api/save-chart")
def save_chart_db(request: SaveChartRequest):
    if request.user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="유저 없음")
    
    user_info = fake_users_db[request.user_id]
    
    save_data = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "symptoms": request.symptoms,
        "detail": request.detail,
        "result_text": request.final_chart_text
    }
    
    if "chart_history" not in user_info:
        user_info["chart_history"] = []
    
    user_info["chart_history"].append(save_data)
    
    print(f"💾 차트 최종 저장 완료! 총 {len(user_info['chart_history'])}건")
    return {"message": "Saved", "history_count": len(user_info["chart_history"])}

# ==========================================
# 5. 진료비 안내 (기존 유지)
# ==========================================
@app.post("/api/estimate-cost")
def estimate_cost(user_id: str):
    if user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="유저 없음")
    
    user_info = fake_users_db[user_id]
    cost_result = generate_cost_guide(user_info)
    return {"cost_guide": cost_result}

# ==========================================
# 6. 병원 추천 (수정됨: 랜덤 삭제 -> 실제 카카오 API 연동)
# ==========================================
@app.post("/api/recommend-hospitals", response_model=RecommendationResponse)
def recommend_hospitals(req: HospitalRecommendationRequest):
    print(f"🏥 위치({req.latitude}, {req.longitude}) 기반 병원 검색")
    
    # 6-1. AI 진료과 추천 (logic.py)
    dept, urgency, reason = recommend_department_ai(req.symptoms)
    
    # 6-2. 카카오 API로 실제 병원 검색 (logic.py)
    real_hospitals = search_hospitals_real(req.latitude, req.longitude, dept, req.radius)
    
    # 데이터 변환 (Frontend용 포맷으로)
    final_list = []
    for h in real_hospitals:
        final_list.append(HospitalInfo(
            name=h['name'], 
            department=h['department'], 
            distance=h['distance'],
            address=h['address'], 
            phone=h['phone'], 
            url=h['url'], 
            x=h['x'], 
            y=h['y']
        ))

    return RecommendationResponse(
        recommended_department=dept, 
        urgency_level=urgency, 
        reason=reason, 
        hospitals=final_list
    )

# ==========================================
# 8. 사용자 정보 수정 (신규 추가: 마이페이지용)
# ==========================================
@app.post("/api/update-user")
def update_user(req: UserUpdateRequest):
    if req.user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="유저 없음")
    
    user = fake_users_db[req.user_id]
    
    if req.phone_number: user['phone_number'] = req.phone_number
    if req.insurance_info: user['insurance_info'] = req.insurance_info
    if req.address: user['address'] = req.address
    
    return {"message": "Updated successfully"}


@app.post("/api/search-medicine")
def search_medicine(request: MedicineSearchRequest):
    if request.user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # logic.py 호출
    result = search_medicine_info(fake_users_db[request.user_id], request.keyword)
    return {"medicine_info": result}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

# 6. [NEW] 히스토리 조회 (마이페이지용)
@app.get("/api/history/{user_id}")
def get_history(user_id: str):
    if user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="유저 없음")
    return {"history": fake_users_db[user_id].get("chart_history", [])}



# 데이터 확인용 (디버깅)
@app.get("/api/users")
def get_all_users():
    return fake_users_db

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)