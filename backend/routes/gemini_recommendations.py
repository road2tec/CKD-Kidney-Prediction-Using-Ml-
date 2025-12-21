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
    GEMINI_MODEL = 'gemini-pro'

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
        
        # Create the model
        model = genai.GenerativeModel('gemini-pro')
        
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
            'model': 'gemini-pro'
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
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
        
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
    """Parse and validate the Gemini response"""
    try:
        # Try to find JSON in the response
        import re
        
        # Look for JSON block
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            json_str = json_match.group()
            return json.loads(json_str)
        else:
            return None
    except json.JSONDecodeError:
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
        
        # Call Gemini API
        gemini_response = call_gemini_rest_api(prompt)
        
        if gemini_response['success']:
            # Parse the response
            recommendations = parse_gemini_response(gemini_response['text'])
            
            if recommendations:
                recommendations['source'] = 'gemini-ai'
                recommendations['generated_at'] = datetime.utcnow().isoformat()
            else:
                # Use fallback if parsing fails
                recommendations = get_fallback_recommendations(patient_data, prediction_result)
        else:
            # Use fallback recommendations
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


@gemini_bp.route('/quick-advice', methods=['POST'])
@jwt_required()
def get_quick_advice():
    """Get quick AI advice for specific CKD-related questions"""
    try:
        db = get_db()
        current_user = get_current_user()
        data = request.get_json()
        
        question = data.get('question', '')
        context = data.get('context', {})  # Optional patient context
        
        if not question:
            return jsonify({
                'success': False,
                'message': 'Question is required'
            }), 400
        
        # Create prompt for quick advice
        prompt = f"""You are a helpful medical AI assistant specializing in Chronic Kidney Disease (CKD). 
A patient has the following question:

QUESTION: {question}

PATIENT CONTEXT (if available):
{json.dumps(context, indent=2) if context else 'No additional context provided'}

Please provide a helpful, accurate, and concise response. Important guidelines:
1. Be informative but always recommend consulting healthcare providers for personalized advice
2. If the question involves medication or dosages, emphasize the need for professional guidance
3. Provide practical, actionable advice where appropriate
4. Be empathetic and supportive in your response
5. Keep the response under 300 words

Response:"""

        # Call Gemini API
        gemini_response = call_gemini_rest_api(prompt, max_tokens=1024)
        
        if gemini_response['success']:
            advice = gemini_response['text']
            source = 'gemini-ai'
        else:
            advice = "I apologize, but I couldn't generate a response at this moment. Please try again later or consult with your healthcare provider for guidance on your question."
            source = 'fallback'
        
        # Log the query
        log_entry = {
            'user_id': current_user['id'],
            'question': question,
            'context': context,
            'source': source,
            'created_at': datetime.utcnow()
        }
        db.gemini_quick_advice.insert_one(log_entry)
        
        return jsonify({
            'success': True,
            'advice': advice,
            'source': source,
            'disclaimer': 'This advice is AI-generated and not a substitute for professional medical advice.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


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
