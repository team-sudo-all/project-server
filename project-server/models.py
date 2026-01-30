from pydantic import BaseModel
from typing import Optional, List, Dict

# [기존] 회원가입 요청
class UserSignupRequest(BaseModel):
    name: str                   # 이름(풀네임)
    birth_date: str             # 생년월일 (YYYY-MM-DD)
    phone_number: str           # 전화번호
    insurance_info: str         # 보험 정보
    allergies: str              # 알러지 정보 (없으면 "None")
    medications: str            # 복약 정보 (없으면 "None")
    medical_history: str        # 치료 정보
    user_id: str                # 아이디
    password: str               # 비밀번호
    # [선택]
    address: Optional[str] = None
    email: Optional[str] = None
    # [추가] 차트 히스토리 저장 공간 (가입 시엔 빈 리스트)
    chart_history: List[Dict] = [] 

# [기존] 로그인 요청
class UserLoginRequest(BaseModel):
    user_id: str
    password: str

# [기존] 증상 입력 요청
class SymptomRequest(BaseModel):
    user_id: str
    selected_symptoms: List[str]
    detail_description: str

# ▼▼▼ [새로 추가된 모델들: 병원 추천용] ▼▼▼
class HospitalRecommendationRequest(BaseModel):
    user_id: str
    symptoms: str  # 예: "배가 너무 아프고 구토를 해요"

class HospitalInfo(BaseModel):
    name: str       # 병원 이름
    department: str # 진료과
    distance: str   # 거리 (예: "1.2km")
    address: str    # 주소
    is_open: bool   # 진료 중 여부

class RecommendationResponse(BaseModel):
    recommended_department: str   # AI가 추천한 진료과 (예: 내과)
    urgency_level: str            # 응급도 (상/중/하)
    reason: str                   # 추천 이유
    hospitals: List[HospitalInfo] # 추천 병원 목록

class MedicineSearchRequest(BaseModel):
    user_id: str
    keyword: str