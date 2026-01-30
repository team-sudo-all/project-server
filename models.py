# models.py
from pydantic import BaseModel
from typing import Optional

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

    # [선택 입력 정보]
    address: Optional[str] = None
    email: Optional[str] = None

# models.py 맨 아래에 추가
class UserLoginRequest(BaseModel):
    user_id: str
    password: str
