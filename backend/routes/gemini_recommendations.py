"""
Gemini AI-Powered Personalized Treatment and Lifestyle Recommendations
Uses Google's Gemini API for intelligent, context-aware recommendations
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId
import json
import os

gemini_bp = Blueprint('gemini', __name__)

# Gemini API Configuration - Import from config or use environment variable
try:
    from config import GEMINI_API_KEY, GEMINI_MODEL
except ImportError:
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    GEMINI_MODEL = 'gemini-2.5-flash'

def get_current_user():
    """Helper to get current user identity as dict"""
    identity = get_jwt_identity()
    if isinstance(identity, str):
        try:
            return json.loads(identity)
        except:
            return {"id": identity}
    return identity


def get_db():
    """Get database connection"""
    from app import db
    return db


def call_gemini_api(prompt, max_tokens=2048):
    """Call Gemini API for generating recommendations"""
    try:
        import google.generativeai as genai
        
        # Configure the Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Create the model - use gemini-2.5-flash
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Configure generation settings
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": max_tokens,
        }
        
        # Safety settings
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        
        # Generate response
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        return {
            'success': True,
            'text': response.text,
            'model': 'gemini-2.5-flash'
        }
        
    except ImportError:
        # If google-generativeai is not installed, use REST API
        return call_gemini_rest_api(prompt, max_tokens)
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def call_gemini_rest_api(prompt, max_tokens=2048):
    """Call Gemini API using REST (fallback method)"""
    try:
        import requests
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": max_tokens,
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                text = result['candidates'][0]['content']['parts'][0]['text']
                return {
                    'success': True,
                    'text': text,
                    'model': 'gemini-pro'
                }
            else:
                return {
                    'success': False,
                    'error': 'No response generated from Gemini'
                }
        else:
            return {
                'success': False,
                'error': f"API Error: {response.status_code} - {response.text}"
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def create_ckd_recommendation_prompt(patient_data, prediction_result):
    """Create a detailed prompt for CKD recommendations"""
    
    # Extract patient information
    age = patient_data.get('age', 'unknown')
    weight = patient_data.get('weight', 'unknown')
    height = patient_data.get('height', 'unknown')
    
    # CKD prediction details
    prediction = prediction_result.get('prediction', 'unknown')
    risk_level = prediction_result.get('risk_level', 'unknown')
    confidence = prediction_result.get('confidence', 'unknown')
    
    # Clinical values
    input_data = patient_data.get('input_data', prediction_result.get('input_data', {}))
    
    # Comorbidities
    has_diabetes = input_data.get('dm', 'no').lower() == 'yes'
    has_hypertension = input_data.get('htn', 'no').lower() == 'yes'
    
    # Lab values
    hemoglobin = input_data.get('hemo', 'unknown')
    serum_creatinine = input_data.get('sc', 'unknown')
    blood_urea = input_data.get('bu', 'unknown')
    sodium = input_data.get('sod', 'unknown')
    potassium = input_data.get('pot', 'unknown')
    
    prompt = f"""You are an expert nephrologist AI assistant providing personalized recommendations for a Chronic Kidney Disease (CKD) patient. Based on the following patient profile and prediction results, provide comprehensive, actionable, and personalized lifestyle and treatment recommendations.

PATIENT PROFILE:
- Age: {age} years
- Weight: {weight} kg
- Height: {height} cm

CKD PREDICTION RESULTS:
- Prediction: {prediction}
- Risk Level: {risk_level}
- Confidence: {confidence}%

CLINICAL VALUES:
- Hemoglobin: {hemoglobin} g/dL
- Serum Creatinine: {serum_creatinine} mg/dL
- Blood Urea: {blood_urea} mg/dL
- Sodium: {sodium} mEq/L
- Potassium: {potassium} mEq/L

COMORBIDITIES:
- Diabetes: {'Yes' if has_diabetes else 'No'}
- Hypertension: {'Yes' if has_hypertension else 'No'}

Please provide recommendations in the following JSON format (ensure valid JSON):
{{
    "summary": "Brief 2-3 sentence summary of the patient's condition and overall recommendation approach",
    "ckd_stage_assessment": "Estimated CKD stage based on the values provided",
    "diet_recommendations": {{
        "daily_calories": "Recommended daily calorie intake",
        "protein_intake": "Recommended protein intake with rationale",
        "sodium_limit": "Daily sodium limit in mg",
        "potassium_guidance": "Guidance on potassium intake based on levels",
        "phosphorus_guidance": "Guidance on phosphorus intake",
        "fluid_intake": "Daily fluid recommendation",
        "foods_to_eat": ["list of recommended foods"],
        "foods_to_avoid": ["list of foods to avoid or limit"]
    }},
    "lifestyle_recommendations": {{
        "exercise": {{
            "type": "Recommended exercise types",
            "duration": "Duration and frequency",
            "precautions": "Any exercise precautions"
        }},
        "sleep": "Sleep recommendations",
        "stress_management": "Stress management techniques",
        "smoking_alcohol": "Guidance on smoking and alcohol"
    }},
    "monitoring_schedule": {{
        "blood_tests": "How often to do blood tests",
        "blood_pressure": "Blood pressure monitoring frequency",
        "weight": "Weight monitoring guidance",
        "urine_tests": "Urine test schedule"
    }},
    "medication_considerations": {{
        "general_guidance": "General medication guidance for CKD",
        "drugs_to_avoid": ["medications to avoid"],
        "supplements": ["recommended supplements if any"]
    }},
    "warning_signs": ["list of symptoms that require immediate medical attention"],
    "specialist_referrals": ["list of specialists to consider consulting"],
    "personalized_tips": ["3-5 personalized tips based on this specific patient's condition"]
}}

IMPORTANT:
1. All recommendations should be evidence-based and appropriate for the patient's condition
2. Include specific numbers and ranges where applicable
3. Consider the patient's comorbidities in all recommendations
4. Adjust recommendations based on the risk level
5. Emphasize the importance of regular follow-up with healthcare providers
6. Output ONLY valid JSON, no additional text before or after"""

    return prompt


def parse_gemini_response(response_text):
    """Parse and validate the Gemini response - handles markdown code blocks"""
    try:
        import re
        
        if not response_text:
            return None
        
        # Strategy 1: Try to parse directly as JSON
        try:
            return json.loads(response_text.strip())
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Strip markdown code fences (```json ... ``` or ``` ... ```)
        cleaned = re.sub(r'^```(?:json)?\s*', '', response_text.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r'```\s*$', '', cleaned.strip(), flags=re.MULTILINE)
        cleaned = cleaned.strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        
        # Strategy 3: Find the first { ... } block (greedy)
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        print(f"[Gemini] WARNING: Could not parse JSON from response: {response_text[:500]}")
        return None
        
    except Exception as e:
        print(f"[Gemini] ERROR parsing response: {e}")
        return None


def get_fallback_recommendations(patient_data, prediction_result):
    """Generate fallback recommendations if Gemini fails"""
    risk_level = prediction_result.get('risk_level', 'Unknown')
    prediction = prediction_result.get('prediction', 'unknown')
    
    if prediction.lower() == 'ckd' or risk_level in ['High', 'Medium']:
        stage = 'Moderate CKD' if risk_level == 'Medium' else 'Advanced CKD'
    else:
        stage = 'Early/No CKD'
    
    return {
        "summary": f"Based on the analysis, the patient shows {risk_level.lower()} risk for CKD. Recommendations are tailored to help manage and slow progression.",
        "ckd_stage_assessment": stage,
        "diet_recommendations": {
            "daily_calories": "25-35 kcal/kg body weight",
            "protein_intake": "0.6-0.8 g/kg body weight for CKD patients",
            "sodium_limit": "Less than 2000mg per day",
            "potassium_guidance": "Limit high-potassium foods if levels are elevated",
            "phosphorus_guidance": "Limit phosphorus to 800-1000mg daily",
            "fluid_intake": "As advised by your nephrologist",
            "foods_to_eat": [
                "Cauliflower, cabbage, bell peppers",
                "Apples, berries, grapes",
                "Fish, egg whites",
                "Whole grains in moderation"
            ],
            "foods_to_avoid": [
                "Processed foods high in sodium",
                "Bananas, oranges (high potassium)",
                "Dairy products (high phosphorus)",
                "Red meat in excess"
            ]
        },
        "lifestyle_recommendations": {
            "exercise": {
                "type": "Walking, swimming, light aerobics",
                "duration": "30 minutes, 5 days a week as tolerated",
                "precautions": "Avoid strenuous exercise, stay hydrated"
            },
            "sleep": "Aim for 7-8 hours of quality sleep",
            "stress_management": "Practice meditation, deep breathing, or yoga",
            "smoking_alcohol": "Complete cessation of smoking; limit or avoid alcohol"
        },
        "monitoring_schedule": {
            "blood_tests": "Every 1-3 months based on CKD stage",
            "blood_pressure": "Daily monitoring at home",
            "weight": "Daily, same time each day",
            "urine_tests": "As per nephrologist's advice"
        },
        "medication_considerations": {
            "general_guidance": "Take medications as prescribed; inform all doctors about CKD",
            "drugs_to_avoid": [
                "NSAIDs (ibuprofen, naproxen)",
                "Certain antibiotics without dose adjustment",
                "Herbal supplements without approval"
            ],
            "supplements": [
                "Vitamin D (if prescribed)",
                "Iron supplements (if anemic)"
            ]
        },
        "warning_signs": [
            "Severe shortness of breath",
            "Swelling in legs, ankles, or face",
            "Decreased or no urine output",
            "Confusion or altered mental state",
            "Chest pain or irregular heartbeat"
        ],
        "specialist_referrals": [
            "Nephrologist for kidney management",
            "Dietitian for renal diet planning",
            "Cardiologist if heart issues present"
        ],
        "personalized_tips": [
            "Monitor your blood pressure daily and keep a log",
            "Stay hydrated but follow fluid restrictions if advised",
            "Prepare meals at home to control sodium intake",
            "Keep all medical appointments and lab tests",
            "Join a CKD support group for emotional support"
        ],
        "source": "fallback",
        "note": "These are general recommendations. Please consult your healthcare provider for personalized advice."
    }


@gemini_bp.route('/personalized-recommendations', methods=['POST'])
@jwt_required()
def get_personalized_recommendations():
    """Get AI-powered personalized treatment and lifestyle recommendations"""
    try:
        db = get_db()
        current_user = get_current_user()
        data = request.get_json()
        
        patient_data = data.get('patient_data', {})
        prediction_result = data.get('prediction_result', {})
        
        # Create the prompt
        prompt = create_ckd_recommendation_prompt(patient_data, prediction_result)
        
        print(f"[Gemini] Calling API with key: {'SET' if GEMINI_API_KEY else 'MISSING'}")
        
        # Call Gemini API
        gemini_response = call_gemini_rest_api(prompt)
        
        print(f"[Gemini] API response success: {gemini_response.get('success')}")
        if not gemini_response.get('success'):
            print(f"[Gemini] API error: {gemini_response.get('error')}")
        else:
            print(f"[Gemini] Raw response (first 300 chars): {gemini_response.get('text', '')[:300]}")
        
        if gemini_response['success']:
            # Parse the response
            recommendations = parse_gemini_response(gemini_response['text'])
            
            if recommendations:
                print(f"[Gemini] JSON parsed successfully, keys: {list(recommendations.keys())}")
                recommendations['source'] = 'gemini-ai'
                recommendations['generated_at'] = datetime.utcnow().isoformat()
            else:
                print("[Gemini] JSON parsing failed, using fallback")
                # Use fallback if parsing fails
                recommendations = get_fallback_recommendations(patient_data, prediction_result)
        else:
            # Use fallback recommendations
            print("[Gemini] API call failed, using fallback")
            recommendations = get_fallback_recommendations(patient_data, prediction_result)
            recommendations['ai_error'] = gemini_response.get('error', 'Unknown error')
        
        # Log the recommendation
        log_entry = {
            'user_id': current_user['id'],
            'patient_data': patient_data,
            'prediction_result': prediction_result,
            'recommendations_source': recommendations.get('source', 'unknown'),
            'created_at': datetime.utcnow()
        }
        db.gemini_recommendations.insert_one(log_entry)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'disclaimer': 'These AI-generated recommendations are for informational purposes only. Always consult with your healthcare provider before making any changes to your treatment or lifestyle.'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@gemini_bp.route('/test-key', methods=['GET'])
def test_gemini_key():
    """Test if Gemini API key is working"""
    if not GEMINI_API_KEY:
        return jsonify({'success': False, 'error': 'GEMINI_API_KEY is not set in environment'}), 400
    
    test_response = call_gemini_rest_api("Say 'API OK' in 5 words.", max_tokens=50)
    return jsonify({
        'key_set': bool(GEMINI_API_KEY),
        'key_prefix': GEMINI_API_KEY[:8] + '...' if GEMINI_API_KEY else 'NOT SET',
        'api_test': test_response
    })



@gemini_bp.route('/quick-advice', methods=['POST'])
@jwt_required()
def get_quick_advice():
    """Get quick AI advice for specific CKD-related questions including medicine recommendations"""
    try:
        db = get_db()
        current_user = get_current_user()
        data = request.get_json()
        
        question = data.get('question', '')
        context = data.get('context', {})  # Optional patient context
        include_medicines = data.get('include_medicines', True)  # Include medicine recommendations
        
        # Get patient info from user profile if available
        user = db.users.find_one({'_id': ObjectId(current_user['id'])})
        age = context.get('age') or (user.get('age') if user else None) or 'unknown'
        gender = context.get('gender') or (user.get('gender') if user else None) or 'unknown'
        risk_level = context.get('risk_level', 'unknown')
        prediction = context.get('prediction', 'unknown')
        
        if not question:
            return jsonify({
                'success': False,
                'message': 'Question is required'
            }), 400
        
        # Create enhanced prompt with medicine recommendations
        medicine_section = ""
        if include_medicines:
            medicine_section = """

MEDICINE RECOMMENDATIONS:
Also provide medication suggestions for CKD management considering the patient's profile. Include:
- Common prescribed medications for CKD based on their risk level
- Dosage guidance (general ranges - emphasize doctor consultation for specific doses)
- Important drug interactions to avoid
- Over-the-counter medicines that are safe or should be avoided

Format the medicine recommendations clearly with:
💊 RECOMMENDED MEDICATIONS:
- [Medicine Name]: [Purpose] - [General dosage range]

⚠️ MEDICATIONS TO AVOID:
- [Medicine Name]: [Reason to avoid]

📋 IMPORTANT NOTES:
- Key considerations for this patient's age and condition"""
        
        prompt = f"""You are a helpful medical AI assistant specializing in Chronic Kidney Disease (CKD). 
A patient has the following question:

QUESTION: {question}

PATIENT PROFILE:
- Age: {age} years
- Gender: {gender}
- CKD Prediction: {prediction}
- Risk Level: {risk_level}

RESPONSE RULES:
1. Give a helpful and complete answer in 200-300 words
2. DO NOT use any markdown formatting - no *, **, #, ###, or bullet points with *
3. Use plain text only. Use numbered lists (1. 2. 3.) or dashes (-) for lists
4. Structure your answer with clear sections using UPPERCASE headers followed by colon (e.g. WHAT IS CKD:)
5. Give direct, practical advice the patient can follow
6. Always end your response with a complete sentence - never cut off mid-sentence
7. Mention "Consult your doctor" at the end
8. Use simple language a patient can understand
9. If medicines are relevant, mention 2-3 key ones with brief purpose{medicine_section}

Provide a complete, well-structured answer that ends with a full sentence."""

        # Call Gemini API
        gemini_response = call_gemini_rest_api(prompt, max_tokens=2048)
        
        if gemini_response['success']:
            advice = gemini_response['text']
            # Clean any markdown formatting from response
            import re
            advice = re.sub(r'\*\*(.+?)\*\*', r'\1', advice)  # Remove **bold**
            advice = re.sub(r'\*(.+?)\*', r'\1', advice)      # Remove *italic*
            advice = re.sub(r'^#{1,6}\s*', '', advice, flags=re.MULTILINE)  # Remove ### headers
            advice = re.sub(r'^\*\s+', '- ', advice, flags=re.MULTILINE)    # Replace * bullets with -
            advice = advice.strip()
            source = 'gemini-ai'
        else:
            # Fallback with medicine recommendations
            advice = get_fallback_advice_with_medicines(age, gender, risk_level, question)
            source = 'fallback'
        
        # Log the query
        log_entry = {
            'user_id': current_user['id'],
            'question': question,
            'context': context,
            'age': age,
            'gender': gender,
            'risk_level': risk_level,
            'source': source,
            'created_at': datetime.utcnow()
        }
        db.gemini_quick_advice.insert_one(log_entry)
        
        return jsonify({
            'success': True,
            'advice': advice,
            'source': source,
            'patient_profile': {
                'age': age,
                'gender': gender,
                'risk_level': risk_level
            },
            'disclaimer': 'This advice is AI-generated and not a substitute for professional medical advice. Always consult your doctor before taking any medication.'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


def get_fallback_advice_with_medicines(age, gender, risk_level, question):
    """Generate fallback advice with medicine recommendations"""
    
    # Age-based considerations
    if age != 'unknown':
        try:
            age_num = int(age)
            if age_num >= 65:
                age_note = "For patients 65+, lower starting doses are typically recommended."
            elif age_num < 18:
                age_note = "Pediatric dosing requires special consideration."
            else:
                age_note = "Standard adult dosing applies."
        except:
            age_note = ""
    else:
        age_note = ""
    
    # Risk level based recommendations
    if risk_level in ['High', 'high']:
        meds_section = """
💊 COMMONLY PRESCRIBED MEDICATIONS FOR HIGH-RISK CKD:
- ACE Inhibitors (e.g., Lisinopril, Enalapril): Help protect kidneys and control blood pressure - Typical dose: 5-40mg daily
- ARBs (e.g., Losartan, Telmisartan): Alternative to ACE inhibitors - Typical dose: 25-100mg daily  
- Diuretics (e.g., Furosemide): Help manage fluid retention - Dose varies by kidney function
- Phosphate Binders: Control phosphorus levels
- Erythropoietin: For CKD-related anemia

⚠️ MEDICATIONS TO AVOID:
- NSAIDs (Ibuprofen, Naproxen): Can worsen kidney function
- Certain antibiotics without dose adjustment
- High-dose Vitamin C supplements
- Herbal supplements (many are not tested for safety in CKD)"""
    elif risk_level in ['Medium', 'medium']:
        meds_section = """
💊 COMMONLY PRESCRIBED MEDICATIONS FOR MODERATE RISK:
- ACE Inhibitors or ARBs: First-line for kidney protection
- Blood pressure medications as needed
- Statins: For cardiovascular protection
- Vitamin D supplements (if deficient)

⚠️ MEDICATIONS TO AVOID:
- NSAIDs (use sparingly if at all)
- Certain herbal supplements
- High-sodium antacids"""
    else:
        meds_section = """
💊 PREVENTIVE MEDICATIONS:
- Blood pressure control medications if hypertensive
- Diabetes medications if diabetic
- Statins for cardiovascular health

⚠️ GENERAL PRECAUTIONS:
- Avoid overuse of pain medications
- Stay hydrated appropriately
- Regular monitoring of kidney function"""
    
    response = f"""Thank you for your question about CKD management.

{age_note}

GENERAL ADVICE:
Based on available information about Chronic Kidney Disease, here are some key points to consider:

1. Regular monitoring of kidney function is essential
2. Blood pressure and blood sugar control are crucial for kidney protection
3. Maintaining a kidney-friendly diet helps slow disease progression
4. Staying adequately hydrated supports kidney function

{meds_section}

📋 IMPORTANT NOTES:
- All medications should be prescribed and monitored by your healthcare provider
- Dosages may need adjustment based on your specific kidney function
- Report any side effects immediately to your doctor
- Keep a list of all medications including supplements

⚠️ DISCLAIMER: This information is for educational purposes only. Please consult your nephrologist or healthcare provider for personalized medication recommendations and proper dosing based on your specific condition."""

    return response


@gemini_bp.route('/diet-plan', methods=['POST'])
@jwt_required()
def generate_diet_plan():
    """Generate a personalized weekly meal plan for CKD patients"""
    try:
        db = get_db()
        current_user = get_current_user()
        data = request.get_json()
        
        patient_profile = data.get('patient_profile', {})
        preferences = data.get('preferences', {})
        restrictions = data.get('restrictions', [])
        
        # Create meal plan prompt
        prompt = f"""You are a renal dietitian AI creating personalized meal plans for CKD patients.

PATIENT PROFILE:
- Age: {patient_profile.get('age', 'unknown')}
- Weight: {patient_profile.get('weight', 'unknown')} kg
- CKD Stage: {patient_profile.get('ckd_stage', 'unknown')}
- Has Diabetes: {patient_profile.get('has_diabetes', False)}
- Has Hypertension: {patient_profile.get('has_hypertension', False)}

DIETARY PREFERENCES:
- Vegetarian: {preferences.get('vegetarian', False)}
- Cuisine Preference: {preferences.get('cuisine', 'Indian/General')}

RESTRICTIONS:
{', '.join(restrictions) if restrictions else 'None specified'}

Create a 7-day meal plan with the following JSON structure:
{{
    "daily_guidelines": {{
        "calories": "recommended calories",
        "protein": "protein limit",
        "sodium": "sodium limit",
        "potassium": "potassium guidance",
        "phosphorus": "phosphorus limit",
        "fluid": "fluid allowance"
    }},
    "meal_plan": [
        {{
            "day": "Monday",
            "breakfast": {{"meal": "description", "approximate_values": {{"calories": 0, "protein": "Xg", "sodium": "Xmg"}}}},
            "mid_morning_snack": {{"meal": "description"}},
            "lunch": {{"meal": "description", "approximate_values": {{}}}},
            "evening_snack": {{"meal": "description"}},
            "dinner": {{"meal": "description", "approximate_values": {{}}}}
        }}
    ],
    "snack_options": ["list of CKD-friendly snacks"],
    "cooking_tips": ["tips for preparing kidney-friendly meals"],
    "shopping_list": ["weekly essentials"]
}}

Make the meals realistic, tasty, and culturally appropriate. Include variety while staying within CKD dietary limits.
Output ONLY valid JSON, no additional text."""

        # Call Gemini API
        gemini_response = call_gemini_rest_api(prompt, max_tokens=4096)
        
        if gemini_response['success']:
            meal_plan = parse_gemini_response(gemini_response['text'])
            if meal_plan:
                meal_plan['source'] = 'gemini-ai'
                meal_plan['generated_at'] = datetime.utcnow().isoformat()
            else:
                meal_plan = get_fallback_meal_plan()
        else:
            meal_plan = get_fallback_meal_plan()
        
        # Log the request
        log_entry = {
            'user_id': current_user['id'],
            'patient_profile': patient_profile,
            'preferences': preferences,
            'source': meal_plan.get('source', 'unknown'),
            'created_at': datetime.utcnow()
        }
        db.gemini_diet_plans.insert_one(log_entry)
        
        return jsonify({
            'success': True,
            'diet_plan': meal_plan,
            'disclaimer': 'This meal plan is AI-generated. Please consult a registered dietitian for personalized dietary advice.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


def get_fallback_meal_plan():
    """Provide a basic fallback meal plan"""
    return {
        "daily_guidelines": {
            "calories": "1800-2200 kcal",
            "protein": "0.6-0.8 g/kg body weight",
            "sodium": "< 2000 mg",
            "potassium": "< 2000 mg (if restricted)",
            "phosphorus": "800-1000 mg",
            "fluid": "As advised by doctor"
        },
        "meal_plan": [
            {
                "day": "Sample Day",
                "breakfast": {"meal": "Poha with vegetables, herbal tea"},
                "mid_morning_snack": {"meal": "Apple slices"},
                "lunch": {"meal": "Rice with dal (moderate portion), mixed vegetables, cucumber raita"},
                "evening_snack": {"meal": "Rice crackers with hummus"},
                "dinner": {"meal": "Chapati with vegetable curry, small portion of paneer"}
            }
        ],
        "snack_options": [
            "Rice cakes",
            "Apple or berries",
            "Cucumber sticks",
            "Plain popcorn (unsalted)"
        ],
        "cooking_tips": [
            "Use herbs and spices instead of salt",
            "Leach potatoes and vegetables to reduce potassium",
            "Avoid processed and canned foods"
        ],
        "shopping_list": [
            "Fresh vegetables (cauliflower, cabbage, bell peppers)",
            "Fruits (apples, berries)",
            "Rice, wheat flour",
            "Lean proteins (chicken, fish, paneer)"
        ],
        "source": "fallback",
        "note": "This is a sample plan. Please work with a dietitian for personalized meal planning."
    }


@gemini_bp.route('/history', methods=['GET'])
@jwt_required()
def get_recommendation_history():
    """Get user's AI recommendation history"""
    try:
        db = get_db()
        current_user = get_current_user()
        
        recommendations = list(db.gemini_recommendations.find(
            {'user_id': current_user['id']}
        ).sort('created_at', -1).limit(10))
        
        for rec in recommendations:
            rec['_id'] = str(rec['_id'])
            if rec.get('created_at'):
                rec['created_at'] = rec['created_at'].isoformat()
        
        return jsonify({
            'success': True,
            'history': recommendations
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
