# models.py
from pydantic import BaseModel
from typing import Optional, List, Dict

# 1. 회원가입 요청 (신체 정보 포함)
class UserSignupRequest(BaseModel):
    name: str
    birth_date: str
    phone_number: str
    insurance_info: str
    allergies: str = "None"
    medications: str = "None"
    medical_history: str = "None"
    user_id: str
    password: str
    # [선택 입력 정보]
    address: Optional[str] = None
    email: Optional[str] = None
    

# 2. 로그인 요청
class UserLoginRequest(BaseModel):
    user_id: str
    password: str

# 3. 회원 정보 수정 요청 (마이페이지용)
class UserUpdateRequest(BaseModel):
    user_id: str
    phone_number: Optional[str] = None
    insurance_info: Optional[str] = None
    address: Optional[str] = None
    password: Optional[str] = None

# 4. 증상 입력 요청
class SymptomRequest(BaseModel):
    user_id: str
    selected_symptoms: List[str]
    detail_description: str

# 5. [중요] 차트 저장 요청 (수정 단계 이후 호출)
class SaveChartRequest(BaseModel):
    user_id: str
    symptoms: List[str]
    detail: str
    final_chart_text: str # 사용자가 수정한 최종 텍스트

# 6. 병원 추천 요청 (위치 정보 포함)
class HospitalRecommendationRequest(BaseModel):
    user_id: str
    symptoms: str
    latitude: float  # 위도
    longitude: float # 경도
    radius: int = 2000 # 반경 (기본 2km)

class HospitalInfo(BaseModel):
    name: str
    department: str
    distance: str
    address: str
    phone: str
    url: str
    x: float
    y: float

class RecommendationResponse(BaseModel):
    recommended_department: str
    urgency_level: str
    reason: str
    hospitals: List[HospitalInfo]

class MedicineSearchRequest(BaseModel):
    user_id: str
    keyword: str