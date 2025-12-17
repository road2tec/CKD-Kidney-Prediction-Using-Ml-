# Patient Routes for Smart Patient Healthcare System
# Handles symptom prediction, appointment booking, and patient operations

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import pickle
import os
import sys
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (MONGO_URI, DATABASE_NAME, COLLECTIONS, 
                    MODEL_PATH, VECTORIZER_PATH, LABEL_ENCODER_PATH,
                    DISEASE_TO_SPECIALIZATION, DEFAULT_SPECIALIZATION)
from models.appointment import Appointment, SymptomLog

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
patient_bp = Blueprint('patient', __name__)

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# Load ML model, vectorizer, and label encoder
model = None
vectorizer = None
label_encoder = None

def load_ml_model():
    """Load the trained ML model and vectorizer"""
    global model, vectorizer, label_encoder
    try:
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'rb') as f:
                model = pickle.load(f)
        if os.path.exists(VECTORIZER_PATH):
            with open(VECTORIZER_PATH, 'rb') as f:
                vectorizer = pickle.load(f)
        if os.path.exists(LABEL_ENCODER_PATH):
            with open(LABEL_ENCODER_PATH, 'rb') as f:
                label_encoder = pickle.load(f)
        return True
    except Exception as e:
        print(f"Error loading ML model: {e}")
        return False

# Load model on import
load_ml_model()


@patient_bp.route('/symptoms/predict', methods=['POST'])
@jwt_required()
def predict_disease():
    """
    Predict disease based on symptoms
    Expected JSON: { symptoms: string (comma-separated symptoms) }
    """
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        if not data.get('symptoms'):
            return jsonify({
                "success": False,
                "message": "Symptoms are required"
            }), 400
        
        symptoms_text = data['symptoms'].lower().strip()
        
        # Reload model if not loaded
        if model is None or vectorizer is None:
            load_ml_model()
        
        if model is None or vectorizer is None:
            return jsonify({
                "success": False,
                "message": "Prediction model not available. Please try again later."
            }), 500
        
        # Preprocess symptoms
        symptoms_list = [s.strip().replace(' ', '_') for s in symptoms_text.split(',')]
        symptoms_processed = ' '.join(symptoms_list)
        
        # Transform symptoms using vectorizer
        symptoms_vectorized = vectorizer.transform([symptoms_processed])
        
        # Predict disease
        prediction = model.predict(symptoms_vectorized)
        prediction_proba = model.predict_proba(symptoms_vectorized)
        
        # Get predicted disease name
        if label_encoder:
            predicted_disease = label_encoder.inverse_transform(prediction)[0]
        else:
            predicted_disease = prediction[0]
        
        # Get confidence score
        confidence_score = float(max(prediction_proba[0])) * 100
        
        # Get doctor specialization
        specialization = DISEASE_TO_SPECIALIZATION.get(predicted_disease, DEFAULT_SPECIALIZATION)
        
        # Get top 3 predictions
        top_indices = prediction_proba[0].argsort()[-3:][::-1]
        top_predictions = []
        for idx in top_indices:
            if label_encoder:
                disease = label_encoder.inverse_transform([idx])[0]
            else:
                disease = str(idx)
            prob = prediction_proba[0][idx] * 100
            top_predictions.append({
                "disease": disease,
                "probability": round(prob, 2),
                "specialization": DISEASE_TO_SPECIALIZATION.get(disease, DEFAULT_SPECIALIZATION)
            })
        
        # Find available doctors with the recommended specialization
        doctors = list(db[COLLECTIONS['doctors']].find({
            "specialization": specialization,
            "is_active": True,
            "is_available": True
        }, {"password": 0}))
        
        # Convert ObjectId to string
        for doctor in doctors:
            doctor['_id'] = str(doctor['_id'])
        
        # Log the symptom prediction
        symptom_log = SymptomLog(
            patient_id=current_user['id'],
            symptoms_text=symptoms_text,
            symptoms_list=symptoms_list,
            predicted_disease=predicted_disease,
            predicted_specialization=specialization,
            confidence_score=confidence_score
        )
        db[COLLECTIONS['symptoms_logs']].insert_one(symptom_log.to_dict())
        
        return jsonify({
            "success": True,
            "prediction": {
                "disease": predicted_disease,
                "confidence": round(confidence_score, 2),
                "specialization": specialization,
                "top_predictions": top_predictions
            },
            "available_doctors": doctors,
            "symptoms_analyzed": symptoms_list
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Prediction failed: {str(e)}"
        }), 500


@patient_bp.route('/symptoms/all', methods=['GET'])
def get_all_symptoms():
    """Get list of all available symptoms for autocomplete"""
    try:
        # List of all symptoms from the dataset
        symptoms = [
            "itching", "skin_rash", "nodal_skin_eruptions", "continuous_sneezing",
            "shivering", "chills", "joint_pain", "stomach_pain", "acidity",
            "ulcers_on_tongue", "muscle_wasting", "vomiting", "burning_micturition",
            "spotting_urination", "fatigue", "weight_gain", "anxiety",
            "cold_hands_and_feets", "mood_swings", "weight_loss", "restlessness",
            "lethargy", "patches_in_throat", "irregular_sugar_level", "cough",
            "high_fever", "sunken_eyes", "breathlessness", "sweating", "dehydration",
            "indigestion", "headache", "yellowish_skin", "dark_urine", "nausea",
            "loss_of_appetite", "pain_behind_the_eyes", "back_pain", "constipation",
            "abdominal_pain", "diarrhoea", "mild_fever", "yellow_urine",
            "yellowing_of_eyes", "acute_liver_failure", "fluid_overload",
            "swelling_of_stomach", "swelled_lymph_nodes", "malaise",
            "blurred_and_distorted_vision", "phlegm", "throat_irritation",
            "redness_of_eyes", "sinus_pressure", "runny_nose", "congestion",
            "chest_pain", "weakness_in_limbs", "fast_heart_rate",
            "pain_during_bowel_movements", "pain_in_anal_region", "bloody_stool",
            "irritation_in_anus", "neck_pain", "dizziness", "cramps", "bruising",
            "obesity", "swollen_legs", "swollen_blood_vessels", "puffy_face_and_eyes",
            "enlarged_thyroid", "brittle_nails", "swollen_extremeties",
            "excessive_hunger", "extra_marital_contacts", "drying_and_tingling_lips",
            "slurred_speech", "knee_pain", "hip_joint_pain", "muscle_weakness",
            "stiff_neck", "swelling_joints", "movement_stiffness", "spinning_movements",
            "loss_of_balance", "unsteadiness", "weakness_of_one_body_side",
            "loss_of_smell", "bladder_discomfort", "foul_smell_of_urine",
            "continuous_feel_of_urine", "passage_of_gases", "internal_itching",
            "toxic_look_(typhos)", "depression", "irritability", "muscle_pain",
            "altered_sensorium", "red_spots_over_body", "belly_pain",
            "abnormal_menstruation", "dischromic_patches", "watering_from_eyes",
            "increased_appetite", "polyuria", "family_history", "mucoid_sputum",
            "rusty_sputum", "lack_of_concentration", "visual_disturbances",
            "receiving_blood_transfusion", "receiving_unsterile_injections", "coma",
            "stomach_bleeding", "distention_of_abdomen", "history_of_alcohol_consumption",
            "blood_in_sputum", "prominent_veins_on_calf", "palpitations",
            "painful_walking", "pus_filled_pimples", "blackheads", "scurring",
            "skin_peeling", "silver_like_dusting", "small_dents_in_nails",
            "inflammatory_nails", "blister", "red_sore_around_nose", "yellow_crust_ooze"
        ]
        
        return jsonify({
            "success": True,
            "symptoms": symptoms
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error fetching symptoms: {str(e)}"
        }), 500


@patient_bp.route('/appointments/book', methods=['POST'])
@jwt_required()
def book_appointment():
    """
    Book an appointment with a doctor
    Expected JSON: { doctor_id, appointment_date, appointment_time, symptoms, predicted_disease, predicted_specialization, notes }
    """
    try:
        current_user = get_current_user()
        
        # Verify user is a patient
        if current_user['role'] != 'patient':
            return jsonify({
                "success": False,
                "message": "Only patients can book appointments"
            }), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['doctor_id', 'appointment_date', 'appointment_time']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "message": f"{field} is required"
                }), 400
        
        # Check if doctor exists
        doctor = db[COLLECTIONS['doctors']].find_one({"_id": ObjectId(data['doctor_id'])})
        if not doctor:
            return jsonify({
                "success": False,
                "message": "Doctor not found"
            }), 404
        
        # Check for existing appointment at same time
        existing_appointment = db[COLLECTIONS['appointments']].find_one({
            "doctor_id": data['doctor_id'],
            "appointment_date": data['appointment_date'],
            "appointment_time": data['appointment_time'],
            "status": {"$in": ["pending", "confirmed"]}
        })
        
        if existing_appointment:
            return jsonify({
                "success": False,
                "message": "This time slot is already booked. Please choose another time."
            }), 400
        
        # Create appointment
        appointment = Appointment(
            patient_id=current_user['id'],
            doctor_id=data['doctor_id'],
            appointment_date=data['appointment_date'],
            appointment_time=data['appointment_time'],
            symptoms=data.get('symptoms', []),
            predicted_disease=data.get('predicted_disease'),
            predicted_specialization=data.get('predicted_specialization'),
            notes=data.get('notes')
        )
        
        result = db[COLLECTIONS['appointments']].insert_one(appointment.to_dict())
        
        return jsonify({
            "success": True,
            "message": "Appointment booked successfully",
            "appointment_id": str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to book appointment: {str(e)}"
        }), 500


@patient_bp.route('/appointments/my', methods=['GET'])
@jwt_required()
def get_my_appointments():
    """Get all appointments for the current patient"""
    try:
        current_user = get_current_user()
        
        # Get appointments
        appointments = list(db[COLLECTIONS['appointments']].find({
            "patient_id": current_user['id']
        }).sort("created_at", -1))
        
        # Enrich with doctor details
        for appointment in appointments:
            appointment['_id'] = str(appointment['_id'])
            
            # Convert datetime objects to strings
            if 'created_at' in appointment and hasattr(appointment['created_at'], 'isoformat'):
                appointment['created_at'] = appointment['created_at'].isoformat()
            if 'updated_at' in appointment and hasattr(appointment['updated_at'], 'isoformat'):
                appointment['updated_at'] = appointment['updated_at'].isoformat()
            
            # Get doctor details - try multiple ways to find the doctor
            if appointment.get('doctor_id'):
                doctor_id = appointment['doctor_id']
                doctor = None
                
                # Try finding by _id first
                try:
                    doctor = db[COLLECTIONS['doctors']].find_one(
                        {"_id": ObjectId(doctor_id)},
                        {"password": 0}
                    )
                except:
                    pass
                
                # If not found, try by user_id
                if not doctor:
                    try:
                        doctor = db[COLLECTIONS['doctors']].find_one(
                            {"user_id": ObjectId(doctor_id)},
                            {"password": 0}
                        )
                    except:
                        pass
                
                # If still not found, try in users collection
                if not doctor:
                    try:
                        doctor = db[COLLECTIONS['users']].find_one(
                            {"_id": ObjectId(doctor_id), "role": "doctor"},
                            {"password": 0}
                        )
                    except:
                        pass
                
                if doctor:
                    doctor['_id'] = str(doctor['_id'])
                    if 'user_id' in doctor:
                        doctor['user_id'] = str(doctor['user_id'])
                    appointment['doctor'] = doctor
        
        return jsonify({
            "success": True,
            "appointments": appointments
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Error fetching appointments: {str(e)}"
        }), 500


@patient_bp.route('/appointments/<appointment_id>', methods=['GET'])
@jwt_required()
def get_appointment_details(appointment_id):
    """Get details of a specific appointment"""
    try:
        current_user = get_current_user()
        
        appointment = db[COLLECTIONS['appointments']].find_one({
            "_id": ObjectId(appointment_id),
            "patient_id": current_user['id']
        })
        
        if not appointment:
            return jsonify({
                "success": False,
                "message": "Appointment not found"
            }), 404
        
        appointment['_id'] = str(appointment['_id'])
        
        # Get doctor details
        if appointment.get('doctor_id'):
            doctor = db[COLLECTIONS['doctors']].find_one(
                {"_id": ObjectId(appointment['doctor_id'])},
                {"password": 0}
            )
            if doctor:
                doctor['_id'] = str(doctor['_id'])
                appointment['doctor'] = doctor
        
        return jsonify({
            "success": True,
            "appointment": appointment
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error fetching appointment: {str(e)}"
        }), 500


@patient_bp.route('/appointments/<appointment_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    try:
        current_user = get_current_user()
        
        # Find and update appointment
        result = db[COLLECTIONS['appointments']].update_one(
            {
                "_id": ObjectId(appointment_id),
                "patient_id": current_user['id'],
                "status": {"$in": ["pending", "confirmed"]}
            },
            {
                "$set": {
                    "status": "cancelled",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            return jsonify({
                "success": False,
                "message": "Appointment not found or already cancelled/completed"
            }), 404
        
        return jsonify({
            "success": True,
            "message": "Appointment cancelled successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error cancelling appointment: {str(e)}"
        }), 500


@patient_bp.route('/doctors', methods=['GET'])
@jwt_required()
def get_doctors():
    """Get list of all available doctors"""
    try:
        specialization = request.args.get('specialization')
        
        # Query for active doctors (is_active True or not set)
        query = {"$or": [{"is_active": True}, {"is_active": {"$exists": False}}]}
        if specialization:
            query["specialization"] = specialization
        
        doctors = list(db[COLLECTIONS['doctors']].find(query, {"password": 0}))
        
        for doctor in doctors:
            doctor['_id'] = str(doctor['_id'])
            if 'user_id' in doctor:
                doctor['user_id'] = str(doctor['user_id'])
        
        return jsonify({
            "success": True,
            "doctors": doctors
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error fetching doctors: {str(e)}"
        }), 500


@patient_bp.route('/prediction-history', methods=['GET'])
@jwt_required()
def get_prediction_history():
    """Get symptom prediction history for the current patient"""
    try:
        current_user = get_current_user()
        
        logs = list(db[COLLECTIONS['symptoms_logs']].find({
            "patient_id": current_user['id']
        }).sort("created_at", -1).limit(10))
        
        for log in logs:
            log['_id'] = str(log['_id'])
        
        return jsonify({
            "success": True,
            "history": logs
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error fetching prediction history: {str(e)}"
        }), 500
