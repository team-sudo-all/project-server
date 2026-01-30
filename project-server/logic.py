import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # 이 줄이 핵심

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# 1. 의료 차트 생성 AI
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

# 2. 진료비 안내 AI
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

# ▼▼▼ [새로 추가된 함수: 진료과 추천] ▼▼▼
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
    Reason: [Short explanation in Korean]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        
        # 간단한 파싱
        lines = content.strip().split('\n')
        dept = "가정의학과"
        urgency = "Low"
        reason = "일반적인 진료 권장"

        for line in lines:
            if "Department:" in line:
                dept = line.split(":", 1)[1].strip()
            elif "Urgency:" in line:
                urgency = line.split(":", 1)[1].strip()
            elif "Reason:" in line:
                reason = line.split(":", 1)[1].strip()
                
        return dept, urgency, reason

    except Exception as e:
        return "내과", "Low", f"AI 분석 실패: {str(e)}"
    

def search_medicine_info(user_data, keyword):
    allergies = user_data.get('allergies', 'None')
    
    prompt = f"""
    You are a helpful 'Korean Pharmacist AI' assisting a foreigner.
    The user is searching for: "{keyword}".

    [User Profile] Allergies: {allergies}

    [Logic Guidelines for Demo]
    1. **Smart Search**: 
       - If input is a Drug Name (e.g., Tylenol), explain that drug.
       - If input is a Symptom (e.g., Headache), recommend the **most popular Korean OTC drug** (e.g., Geworin, EVE).
    2. **Classification**: Clearly state if it is **OTC** (Pharmacy) or **RX** (Doctor).
    3. **Safety**: Check against user's allergies ({allergies}). If risky, output "WARNING".

    [Output Format]
    === 💊 Medicine Information ===
    1. Name (KR/EN): 
       - (Korean Name) / (English Name)
       
    2. Classification: (OTC or RX)
       - (e.g., "Available at Pharmacy" or "Need Prescription")
       
    3. Primary Use:
       - (Simple explanation: e.g., "Pain reliever", "Cold medicine")

    4. Safety Check (Allergy: {allergies}): (SAFE / WARNING)
       - (If WARNING, explain why briefly)

    5. Est. Price (Korea):
       - (Approx. range, e.g., 3,000 ~ 5,000 KRW)
       
    6. Usage Tip:
       - (Simple tip: e.g., "Take 2 pills after meal", "May cause drowsiness")

    * Disclaimer: AI estimate. Consult a pharmacist.
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