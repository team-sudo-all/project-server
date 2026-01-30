# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import UserSignupRequest, UserLoginRequest
import uvicorn
from models import SymptomRequest
from logic import generate_medical_chart, generate_cost_guide

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fake_users_db = {}

@app.post("/api/signup")
def signup(user: UserSignupRequest):
    # 1. 아이디 중복 체크
    if user.user_id in fake_users_db:
        raise HTTPException(status_code=400, detail="이미 존재하는 아이디입니다.")
    
    # 2. 저장 (메모리에 저장)
    fake_users_db[user.user_id] = user.dict()
    
    print(f"✅ 가입 완료: {user.name} (ID: {user.user_id})")
    return {"message": "Success", "user_name": user.name}

@app.post("/api/login")
def login(user: UserLoginRequest):
    # 1. 아이디가 DB에 있는지 확인
    if user.user_id not in fake_users_db:
        raise HTTPException(status_code=401, detail="존재하지 않는 아이디입니다.")
    
    # 2. 비밀번호가 맞는지 확인
    stored_user = fake_users_db[user.user_id]
    if stored_user['password'] != user.password:
        raise HTTPException(status_code=401, detail="비밀번호가 틀렸습니다.")
    
    # 3. 로그인 성공! (프론트엔드에게 성공 메시지와 이름 전달)
    return {
        "message": "Login Success",
        "user_id": user.user_id,
        "user_name": stored_user['name']
    }

@app.post("/api/create-chart")
def create_chart(request: SymptomRequest):
    # 1. 사용자 정보 찾기 (DB인 fake_users_db에서)
    if request.user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="로그인 정보가 없습니다.")
    
    user_info = fake_users_db[request.user_id]
    
    # 2. 로직(AI) 실행
    print(f"🤖 {user_info['name']}님의 차트를 생성 중입니다...")
    chart_result = generate_medical_chart(user_info, request)
    
    # 3. 결과 반환
    print("✅ 차트 생성 완료!")
    return {"chart": chart_result}

# [기능 2] 환자용 영어 진료비/절차 안내 (새로 추가됨!)
@app.post("/api/estimate-cost")
def estimate_cost(user_id: str):
    # 사용자 정보 조회
    if user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="사용자 정보를 찾을 수 없습니다.")
    
    user_info = fake_users_db[user_id]
    
    print(f"💰 진료비 안내 요청: {user_info['name']} (보험: {user_info.get('insurance_info')})")
    
    # logic.py의 진료비 안내 함수 호출
    cost_result = generate_cost_guide(user_info)
    
    return {"cost_guide": cost_result}

# 데이터 확인용
@app.get("/api/users")
def get_all_users():
    return fake_users_db

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)