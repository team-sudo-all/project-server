import requests
import os
from openai import OpenAI
from dotenv import load_dotenv

# .env 파일에서 키를 불러옵니다 (보안 필수)
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 1. 의료 차트 생성 AI (프롬프트 100% 유지)
def generate_medical_chart(user_data, symptom_data):
    name = user_data.get('name', '환자')
    age = user_data.get('birth_date', '미상')
    history = user_data.get('medical_history', '특이사항 없음')
    meds = user_data.get('medications', '없음')
    allergies = user_data.get('allergies', '없음')

    prompt = f"""
    당신은 '의료 서기(Medical Scribe)'입니다. 
    환자의 진술을 바탕으로 의사가 진료 시 참고할 '기초 예진표(Pre-clinical Note)'를 작성하세요.

    [작성 원칙]
    1. **진단/조언 금지**: 병명 추측이나 치료 조언을 절대 포함하지 마십시오. 오직 환자가 말한 '증상'과 '사실'만 기록하세요.
    2. **전문 용어 변환**: 환자의 구어체 표현을 간결한 '의학적 표현'으로 다듬으세요. (예: "열이 펄펄 끓음" -> "고열(High Fever)")
    3. **객관적 서술**: 통증의 위치, 시점, 양상을 드라이하게 나열하세요.

    [환자 데이터]
    - 환자명/생년월일: {name} ({age})
    - 기저질환(PHx): {history}
    - 복용약(Rx): {meds}
    - 알러지: {allergies}
    - 입력 증상: {', '.join(symptom_data.selected_symptoms)}
    - 상세 묘사: "{symptom_data.detail_description}"

    [출력 양식 (Text Only)]
    === 기초 예진 기록 (Medical History Taking) ===

    1. 주호소 (Chief Complaint, C.C)
       - (환자가 호소하는 가장 주된 증상 1~2개와 발생 시점)

    2. 현병력 (Present Illness, P.I)
       * 발병 시기 (Onset): 
       * 부위 및 양상 (Location & Character): 
       * 강도 및 빈도 (Severity & Frequency): 
       * 동반 증상 (Associated Symptoms): 
       * 악화/완화 요인 (Aggravating/Relieving Factors): 

    3. 특이사항 (Past History & Social Hx)
       * 기저질환: (환자의 기저질환 데이터 그대로 기재)
       * 복용약물: (환자의 약물 데이터 그대로 기재)
       * 알러지: (환자의 알러지 데이터 그대로 기재)
       * 기타: (환자 진술 중 여행력, 음식 섭취 등 특이사항이 있다면 여기에 건조하게 기록)
    ================================================
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a factual medical scribe. Do not diagnose."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI 차트 생성 실패: {str(e)}"

# 2. 진료비 안내 AI (프롬프트 100% 유지)
def generate_cost_guide(user_data):
    insurance = user_data.get('insurance_info', 'None')
    name = user_data.get('name', 'Unknown')

    prompt = f"""
    You are a strictly realistic 'Hospital Billing Coordinator' in Korea.
    Your goal is to provide accurate cost and procedure guidance based on the patient's specific insurance type.

    [Patient Data]
    - Name: {name}
    - Insurance: "{insurance}"

    [Logic: Branch by Insurance Type]
    CASE A: Insurance is 'NHIS' (National Health Insurance)
    - Patient pays only Co-payment (본인부담금). Very affordable.
    
    CASE B: Insurance is 'Private' or 'Travel Insurance'
    - Patient pays Full Amount Upfront. Expensive. Needs receipt for claim.

    [Output Format (English)]
    === 💰 Estimated Cost & Guide ===
    1. Insurance Analysis: [NHIS or Private]
    2. 🏥 Local Clinic (Primary):
       - Payment: 
       - Est. Cost: (NHIS: 5k~15k KRW / Private: 30k~60k KRW)
       - Tip:
    3. 🏥 University Hospital (Tertiary):
       - Payment: (Referral Letter needed for NHIS)
       - Est. Cost: (NHIS: 20k~50k+ KRW / Private: 150k+ KRW)
       - Procedure:
    ================================
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# 3. 진료과 추천 AI (프롬프트 100% 유지)
def recommend_department_ai(symptom_text):
    prompt = f"""
    You are a medical triage AI.
    Analyze the patient's symptoms and recommend the most suitable 'Medical Department' (in Korean).
    
    [Patient Symptoms]
    "{symptom_text}"

    [Task]
    1. Determine the best department (e.g., 내과, 정형외과, 이비인후과, 피부과, 응급실).
    2. Determine Urgency Level (Emergency, High, Moderate, Low).
    3. Explain briefly why.

    [Output Format]
    Department: [Korean Name]
    Urgency: [Level]
    Reason_kr: [Short explanation in Korean]
    Reason_en: [Short explanation in English]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        
        dept = "내과"
        urgency = "Low"
        reason_kr = "일반 진료"
        reason_en = "normal visit"
        
        lines = content.strip().split('\n')
        for line in lines:
            if "Department:" in line: dept = line.split(":", 1)[1].strip()
            elif "Urgency:" in line: urgency = line.split(":", 1)[1].strip()
            elif "Reason_kr:" in line: reason_kr = line.split(":", 1)[1].strip()
            elif "Reason_en:" in line: reason_en = line.split(":", 1)[1].strip()
            
        return dept, urgency, reason_kr, reason_en
    except:
        return "내과", "Low", "AI 분석 실패", "AI Analysis Fail"

def search_hospitals_real(latitude, longitude, query, radius=2000):
    print("\n" + "="*50)
    print("🚀 [DEBUG] 카카오 병원 검색 시작")
    
    # 1. API 키 확인
    KAKAO_API_KEY = os.getenv("KAKAO_API_KEY")
    
    # 키가 없는 경우 체크
    if not KAKAO_API_KEY:
        print("❌ [DEBUG] KAKAO_API_KEY가 환경변수에 없습니다!")
        # (테스트를 위해 필요하다면 여기에 직접 키를 잠시 넣어보세요)
        # KAKAO_API_KEY = "여기에_키를_직접_넣어보세요"
    else:
        print(f"✅ [DEBUG] API Key 로드 성공 (길이: {len(KAKAO_API_KEY)})")

    # 2. 요청 데이터 확인
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    
    # 카카오 좌표계 확인 (x: 경도, y: 위도)
    params = {
        "query": query, 
        "y": latitude, 
        "x": longitude, 
        "radius": radius, 
        "sort": "distance"
    }
    
    print(f"📍 [DEBUG] 요청 파라미터: {params}")

    try:
        # 3. 실제 요청 보내기
        response = requests.get(url, headers=headers, params=params)
        
        print(f"📡 [DEBUG] 응답 상태 코드: {response.status_code}")
        
        # 4. 결과 분석
        if response.status_code == 200:
            data = response.json()
            documents = data.get("documents", [])
            print(f"📦 [DEBUG] 검색된 병원 수: {len(documents)}개")
            
            if len(documents) == 0:
                print("⚠️ [DEBUG] 검색 결과가 0개입니다. (좌표나 반경을 확인하세요)")

            hospitals = []
            for doc in documents[:5]:
                hospitals.append({
                    "name": doc["place_name"],
                    "department": query,
                    "distance": f"{doc['distance']}m",
                    "address": doc["road_address_name"] or doc["address_name"],
                    "phone": doc["phone"],
                    "url": doc["place_url"],
                    "x": float(doc["x"]), 
                    "y": float(doc["y"])
                })
            print("="*50 + "\n")
            return hospitals
            
        else:
            # 에러 발생 시 카카오가 보낸 메시지 출력
            print(f"❌ [DEBUG] API 호출 실패 원인: {response.text}")
            print("="*50 + "\n")
            return []
            
    except Exception as e:
        print(f"🔥 [DEBUG] 치명적 오류 발생: {str(e)}")
        print("="*50 + "\n")
        return []
    
def get_image(keyword):

    params = {
        "q": keyword + " medicine package",
        "engine": "google_images",
        "api_key": os.getenv("SERPAPI_KEY")
    }

    r = requests.get("https://serpapi.com/search", params=params, timeout=10)

    data = r.json()

    if "images_results" in data and len(data["images_results"]) > 0:
        return data["images_results"][0]["original"]

    return None

def search_medicine_info(user_data, keyword):
    allergies = user_data.get('allergies', 'None')
    
    prompt = f"""
    You are a Korean pharmacist AI.

    User keyword: "{keyword}"
    User allergies: {allergies}

    Follow the template EXACTLY.
    Do NOT change headers.
    Do NOT add extra sections.
    Fill in the blanks only.

    If keyword is a symptom → choose the most common Korean OTC medicine.

    ------------------------

    === MEDICINE INFO KR ===

    === 약품 정보 ===

    1. 약품명 (한글/영문):
    - 

    2. 분류:
    - 일반의약품(OTC) 또는 전문의약품(RX)

    3. 주요 용도:
    - 

    4. 안전성 확인 (알러지: {allergies}):
    - 안전 / 주의 / 위험
    - 이유 한 줄

    5. 예상 가격 (한국):
    - 범위 제시

    6. 복용 팁:
    - 2~3줄

    7. 동일 주성분 약:
    - 약품명 (제약회사) 형식으로 반드시 작성
    - 4~5개


    * 주의: AI 예측입니다. 약사와 상담하세요.

    ------------------------

    === MEDICINE INFO EN ===

    === Medicine Information ===

    1. Name (KR/EN):
    - 

    2. Classification:
    - OTC or RX

    3. Primary Use:
    - 

    4. Safety Check (Allergy: {allergies}):
    - SAFE / CAUTION / RISK
    - one-line reason

    5. Est. Price (Korea):
    - range

    6. Usage Tip:
    - 2–3 lines


    7. Medicines with Same Active Ingredient:
    - brand (manufacturer) format REQUIRED
    - 4 ~ 5 items

    * Disclaimer: AI estimate. Consult a pharmacist.
    """


    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.choices[0].message.content

        # ✅ 파싱
        kr_part = ""
        en_part = ""

        if "=== MEDICINE INFO EN ===" in text:
            kr_part, en_part = text.split("=== MEDICINE INFO EN ===", 1)
            kr_part = kr_part.replace("=== MEDICINE INFO KR ===", "").strip()
            en_part = en_part.strip()
        else:
            kr_part = text.strip()
            en_part = text.strip()

        image_url = get_image(keyword)


        return {
            "medicine_info_kr": kr_part,
            "medicine_info_en": en_part,
            "image_url": image_url
        }

    except Exception as e:
        return {
            "medicine_info_kr": "약 정보 생성 실패",
            "medicine_info_en": f"Medicine info failed: {str(e)}",
            "image_url": None
        }
