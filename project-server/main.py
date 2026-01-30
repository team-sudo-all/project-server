from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import random
from datetime import datetime

# models와 logic에서 필요한 것들 가져오기
from models import (
    UserSignupRequest, UserLoginRequest, SymptomRequest, MedicineSearchRequest,
    HospitalRecommendationRequest, HospitalInfo, RecommendationResponse
)
from logic import generate_medical_chart, generate_cost_guide, recommend_department_ai, search_medicine_info

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 메모리 DB (서버 끄면 사라짐)
fake_users_db = {}

# 1. 회원가입
@app.post("/api/signup")
def signup(user: UserSignupRequest):
    if user.user_id in fake_users_db:
        raise HTTPException(status_code=400, detail="이미 존재하는 아이디입니다.")
    
    # 모델을 딕셔너리로 변환해서 저장
    user_dict = user.dict()
    # 차트 히스토리 리스트 명시적 초기화
    user_dict["chart_history"] = [] 
    
    fake_users_db[user.user_id] = user_dict
    
    print(f"✅ 가입 완료: {user.name} (ID: {user.user_id})")
    return {"message": "Success", "user_name": user.name}

# 2. 로그인
@app.post("/api/login")
def login(user: UserLoginRequest):
    if user.user_id not in fake_users_db:
        raise HTTPException(status_code=401, detail="존재하지 않는 아이디입니다.")
    
    stored_user = fake_users_db[user.user_id]
    if stored_user['password'] != user.password:
        raise HTTPException(status_code=401, detail="비밀번호가 틀렸습니다.")
    
    return {
        "message": "Login Success",
        "user_id": user.user_id,
        "user_name": stored_user['name']
    }

# 3. 차트 생성 (히스토리 저장 기능 추가됨!)
@app.post("/api/create-chart")
def create_chart(request: SymptomRequest):
    if request.user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="로그인 정보가 없습니다.")
    
    user_info = fake_users_db[request.user_id]
    
    print(f"🤖 {user_info['name']}님의 차트를 생성 중입니다...")
    
    # 3-1. AI 로직 실행
    chart_result = generate_medical_chart(user_info, request)
    
    # 3-2. 히스토리에 저장 (텍스트와 날짜만 저장)
    save_data = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "symptoms": request.selected_symptoms,
        "detail": request.detail_description,
        "result_text": chart_result
    }
    
    # 혹시 리스트가 없으면 생성 (안전장치)
    if "chart_history" not in user_info:
        user_info["chart_history"] = []
        
    user_info["chart_history"].append(save_data)
    
    print(f"✅ 차트 생성 및 저장 완료! (총 {len(user_info['chart_history'])}건)")
    return {"chart": chart_result}

# 4. 진료비 안내
@app.post("/api/estimate-cost")
def estimate_cost(user_id: str):
    if user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="사용자 정보를 찾을 수 없습니다.")
    
    user_info = fake_users_db[user_id]
    print(f"💰 진료비 안내 요청: {user_info['name']}")
    
    cost_result = generate_cost_guide(user_info)
    return {"cost_guide": cost_result}

# 5. [NEW] 병원 추천 (지도용 데이터 + AI 진료과 추천)
@app.post("/api/recommend-hospitals", response_model=RecommendationResponse)
def recommend_hospitals(req: HospitalRecommendationRequest):
    # 5-1. AI에게 진료과 추천받기
    print(f"🏥 병원 추천 요청: {req.symptoms}")
    dept, urgency, reason = recommend_department_ai(req.symptoms)
    
    # 5-2. (해커톤용) 가짜 병원 데이터 생성
    fake_hospitals = []
    base_names = ["서울", "연세", "바른", "튼튼", "굿모닝", "삼성", "현대"]
    
    for i in range(3): # 3개 병원 추천
        name = f"{random.choice(base_names)}{dept}의원"
        dist = f"{random.randint(100, 3000)}m" # 거리 랜덤
        
        fake_hospitals.append(HospitalInfo(
            name=name,
            department=dept,
            distance=dist,
            address=f"서울시 강남구 역삼동 {random.randint(100, 999)}번지",
            is_open=True
        ))

    return RecommendationResponse(
        recommended_department=dept,
        urgency_level=urgency,
        reason=reason,
        hospitals=fake_hospitals
    )

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