# Lifestyle & Diet Recommendations Routes for CKD Patients

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MONGO_URI, DATABASE_NAME

def get_current_user():
    """Helper to get current user identity as dict"""
    identity = get_jwt_identity()
    if isinstance(identity, str):
        try:
            return json.loads(identity)
        except:
            return {"id": identity}
    return identity

# Create blueprint
recommendations_bp = Blueprint('recommendations', __name__)

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]


# CKD Stage-based recommendations database
CKD_RECOMMENDATIONS = {
    "ckd_early": {
        "stage": "Early CKD (Stage 1-2)",
        "diet": {
            "foods_to_eat": [
                "Fresh fruits (apples, berries, grapes)",
                "Fresh vegetables (cauliflower, cabbage, bell peppers)",
                "Whole grains (brown rice, oats, whole wheat)",
                "Lean proteins (chicken, fish, egg whites)",
                "Healthy fats (olive oil, omega-3 rich fish)"
            ],
            "foods_to_limit": [
                "High sodium foods (processed foods, canned soups)",
                "Red meat and processed meats",
                "High potassium foods if levels are elevated",
                "Excessive dairy products",
                "Added sugars and sugary drinks"
            ],
            "daily_water_intake": "1.5-2 liters (consult doctor)",
            "protein_intake": "0.8-1.0 g/kg body weight per day"
        },
        "lifestyle": [
            "Exercise regularly (30 minutes, 5 days a week)",
            "Maintain healthy weight (BMI 18.5-24.9)",
            "Monitor blood pressure regularly",
            "Control blood sugar if diabetic",
            "Quit smoking and limit alcohol",
            "Get adequate sleep (7-8 hours)",
            "Manage stress through meditation or yoga",
            "Regular kidney function checkups"
        ],
        "medications": [
            "Take prescribed blood pressure medications",
            "Control diabetes with prescribed medications",
            "Avoid NSAIDs (ibuprofen, aspirin) unless prescribed",
            "Consult doctor before taking any new medication"
        ]
    },
    "ckd_moderate": {
        "stage": "Moderate CKD (Stage 3)",
        "diet": {
            "foods_to_eat": [
                "Low potassium fruits (apples, berries, grapes, pineapple)",
                "Low potassium vegetables (cabbage, cauliflower, lettuce)",
                "Limited protein (fish, egg whites, small amounts of chicken)",
                "Whole grains in moderation",
                "Unsalted foods"
            ],
            "foods_to_limit": [
                "High potassium foods (bananas, oranges, potatoes, tomatoes)",
                "High phosphorus foods (dairy, nuts, beans, cola)",
                "Salt and sodium (limit to 2g/day)",
                "Protein (limit to 0.6-0.8 g/kg per day)",
                "Processed and packaged foods"
            ],
            "daily_water_intake": "As advised by doctor (may need restriction)",
            "protein_intake": "0.6-0.8 g/kg body weight per day"
        },
        "lifestyle": [
            "Moderate exercise with doctor's approval",
            "Daily blood pressure monitoring",
            "Strict blood sugar control if diabetic",
            "Complete smoking cessation",
            "Weight management",
            "Limit physical strain",
            "Monthly kidney function tests",
            "Regular nephrologist consultations"
        ],
        "medications": [
            "Strict adherence to prescribed medications",
            "Phosphate binders if prescribed",
            "Vitamin D supplements if needed",
            "Avoid over-the-counter medications without consultation",
            "Regular monitoring of medication side effects"
        ]
    },
    "ckd_advanced": {
        "stage": "Advanced CKD (Stage 4-5)",
        "diet": {
            "foods_to_eat": [
                "Very low potassium fruits (apples, berries)",
                "Very low potassium vegetables (cabbage, cauliflower)",
                "Strictly limited protein (as per renal dietitian)",
                "Low phosphorus foods",
                "Homemade low-sodium meals"
            ],
            "foods_to_limit": [
                "Strict potassium restriction (avoid bananas, oranges, tomatoes)",
                "Strict phosphorus restriction (avoid dairy, beans, nuts)",
                "Very low sodium (1-2g per day)",
                "Minimal protein intake (0.6g/kg or less)",
                "Limit fluid intake as prescribed"
            ],
            "daily_water_intake": "Strictly as prescribed by nephrologist (often restricted)",
            "protein_intake": "0.6 g/kg or less per day (renal dietitian guidance)"
        },
        "lifestyle": [
            "Light exercise only with doctor approval",
            "Daily monitoring of weight and blood pressure",
            "Prepare for potential dialysis or transplant",
            "Complete avoidance of tobacco and alcohol",
            "Energy conservation techniques",
            "Frequent medical monitoring",
            "Psychological support and counseling",
            "Family education about CKD management"
        ],
        "medications": [
            "Complex medication regimen - strict adherence critical",
            "Phosphate binders with meals",
            "Vitamin D and other supplements",
            "Erythropoietin for anemia if prescribed",
            "Regular medication reviews with nephrologist",
            "Immediate reporting of side effects"
        ]
    },
    "no_ckd": {
        "stage": "Healthy - No CKD",
        "diet": {
            "foods_to_eat": [
                "Variety of fruits and vegetables",
                "Whole grains",
                "Lean proteins",
                "Healthy fats",
                "Low-fat dairy"
            ],
            "foods_to_limit": [
                "Excessive salt",
                "Processed foods",
                "Excessive red meat",
                "Added sugars"
            ],
            "daily_water_intake": "2-3 liters",
            "protein_intake": "0.8-1.2 g/kg body weight per day"
        },
        "lifestyle": [
            "Regular exercise (150 minutes per week)",
            "Maintain healthy weight",
            "Regular health checkups",
            "Manage stress",
            "Adequate sleep",
            "Limit alcohol consumption",
            "Don't smoke"
        ],
        "medications": [
            "Take prescribed medications as directed",
            "Regular health screenings",
            "Preventive care"
        ]
    }
}


@recommendations_bp.route('/lifestyle', methods=['POST'])
@jwt_required()
def get_lifestyle_recommendations():
    """
    Get personalized lifestyle and diet recommendations based on CKD prediction
    Expected JSON: { prediction, risk_level, age, weight, comorbidities }
    """
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        prediction = data.get('prediction', 'notckd').lower()
        risk_level = data.get('risk_level', 'Low')
        age = data.get('age', 50)
        weight = data.get('weight', 70)
        
        # Determine CKD stage category
        if prediction == 'notckd':
            category = 'no_ckd'
        elif risk_level == 'High':
            category = 'ckd_advanced'
        elif risk_level == 'Medium':
            category = 'ckd_moderate'
        else:
            category = 'ckd_early'
        
        recommendations = CKD_RECOMMENDATIONS.get(category, CKD_RECOMMENDATIONS['no_ckd'])
        
        # Add personalized notes
        personalized_notes = []
        
        if data.get('has_diabetes', False) or data.get('dm', '').lower() == 'yes':
            personalized_notes.append("Monitor blood sugar levels strictly")
            personalized_notes.append("Follow diabetic diet plan")
        
        if data.get('has_hypertension', False) or data.get('htn', '').lower() == 'yes':
            personalized_notes.append("Monitor blood pressure daily")
            personalized_notes.append("Reduce sodium intake significantly")
        
        if age > 60:
            personalized_notes.append("Consider age-appropriate exercises")
            personalized_notes.append("Regular bone health monitoring")
        
        # Calculate protein requirement
        if weight:
            protein_range = recommendations['diet']['protein_intake']
            # Extract numeric values from string like "0.6-0.8 g/kg"
            try:
                if '-' in protein_range:
                    low, high = protein_range.split('-')
                    low_val = float(low.strip().split()[0])
                    high_val = float(high.strip().split()[0])
                    protein_grams = f"{int(low_val * weight)}-{int(high_val * weight)} grams"
                else:
                    val = float(protein_range.split()[0])
                    protein_grams = f"~{int(val * weight)} grams"
                personalized_notes.append(f"Daily protein target: {protein_grams}")
            except:
                pass
        
        # Save recommendation log
        recommendation_log = {
            'patient_id': current_user['id'],
            'ckd_category': category,
            'recommendations': recommendations,
            'personalized_notes': personalized_notes,
            'created_at': datetime.utcnow()
        }
        db.lifestyle_recommendations.insert_one(recommendation_log)
        
        return jsonify({
            "success": True,
            "recommendations": {
                **recommendations,
                "personalized_notes": personalized_notes,
                "category": category
            },
            "message": "Please consult with a healthcare provider for personalized medical advice"
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Failed to generate recommendations: {str(e)}"
        }), 500


@recommendations_bp.route('/history', methods=['GET'])
@jwt_required()
def get_recommendations_history():
    """Get recommendation history for current user"""
    try:
        current_user = get_current_user()
        
        history = list(db.lifestyle_recommendations.find({
            'patient_id': current_user['id']
        }).sort('created_at', -1).limit(10))
        
        for item in history:
            item['_id'] = str(item['_id'])
            if 'created_at' in item:
                item['created_at'] = item['created_at'].isoformat()
        
        return jsonify({
            "success": True,
            "history": history
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to fetch history: {str(e)}"
        }), 500


@recommendations_bp.route('/emergency-guidelines', methods=['GET'])
def get_emergency_guidelines():
    """Get emergency guidelines for CKD patients"""
    guidelines = {
        "seek_immediate_help": [
            "Severe shortness of breath",
            "Chest pain or pressure",
            "Severe swelling in legs, ankles, or face",
            "Decreased or no urine output",
            "Confusion or altered mental state",
            "Persistent nausea and vomiting",
            "Irregular heartbeat",
            "Seizures"
        ],
        "call_doctor": [
            "Fever above 100.4°F (38°C)",
            "Blood in urine",
            "Sudden weight gain (>2 kg in a day)",
            "Persistent headache",
            "Muscle weakness or cramps",
            "Unusual tiredness",
            "Changes in urine color or amount",
            "Swelling that worsens"
        ],
        "emergency_contacts": {
            "ambulance": "108 / 102",
            "kidney_helpline": "1800-XXX-XXXX (Update with local number)",
            "poison_control": "1800-XXX-XXXX (Update with local number)"
        }
    }
    
    return jsonify({
        "success": True,
        "emergency_guidelines": guidelines
    }), 200
