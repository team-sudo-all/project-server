# logic.py
import os
from openai import OpenAI

# [중요] 여기에 API 키를 넣으세요
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_medical_chart(user_data, symptom_data):
    # 1. 사용자 기본 정보 꺼내기
    name = user_data.get('name', '환자')
    age = user_data.get('birth_date', '미상')
    history = user_data.get('medical_history', '특이사항 없음')
    meds = user_data.get('medications', '없음')
    allergies = user_data.get('allergies', '없음')

    # 2. 프롬프트 (그대로 유지)
    # 2. 전문적인 의무기록 생성을 위한 프롬프트
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

    # 3. GPT 호출 (최신 문법 적용됨)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 가성비 모델
            messages=[
                {"role": "system", "content": "You are a factual medical scribe. Do not diagnose."},
                {"role": "user", "content": prompt}
            ]
        )
        # 응답 추출 방식도 변경됨 (객체 접근)
        return response.choices[0].message.content
    except Exception as e:
        return f"AI 차트 생성 실패: {str(e)}"
    
def generate_cost_guide(user_data):
    insurance = user_data.get('insurance_info', 'None')
    name = user_data.get('name', 'Unknown')

    prompt = f"""
    You are a strictly realistic 'Hospital Billing Coordinator' in Korea.
    Your goal is to provide accurate cost and procedure guidance based on the patient's specific insurance type.

    [Patient Data]
    - Name: {name}
    - Insurance: "{insurance}"

    [⚠️ System Logic: Branch by Insurance Type]
    
    CASE A: If Insurance is 'NHIS' (National Health Insurance / 국민건강보험)
    - Billing: The patient only pays the **Co-payment (본인부담금)** at the desk. 
    - Process: Pay by card/cash -> Take the prescription to a pharmacy. (No refund claim needed).
    - Cost: Very affordable due to government support.
    
    CASE B: If Insurance is 'Private' or 'Travel Insurance' (민간/여행자 보험)
    - Billing: Must **Pay Full Amount Upfront** at most clinics. 
    - Process: Pay -> Get English receipt & Itemized bill -> Claim refund from their own insurance company.
    - Cost: Much higher than NHIS (Standard non-insured rates).

    [Output Format (English)]
    === 💰 Estimated Cost & Guide ===

    1. Insurance Analysis:
       - [State clearly if the user is treated as NHIS or Private Insurance holder]

    2. 🏥 If you visit a Local Clinic (Primary):
       - **Payment**: (Describe based on CASE A or B)
       - **Est. Cost**: (NHIS: 5,000~15,000 KRW / Private: 30,000~60,000 KRW)
       - **Tip**: (If Private, remind them to get documents for reimbursement)

    3. 🏥 If you visit a University Hospital (Tertiary):
       - **Payment**: (Mention 'Referral Letter' is CRITICAL for NHIS to get benefits)
       - **Est. Cost**: (NHIS: 20,000~50,000+ KRW / Private: 150,000+ KRW)
       - **Procedure**: (Mention International Healthcare Center for Private insurance holders)
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