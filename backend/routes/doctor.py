# Doctor Routes for Smart Patient Healthcare System
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import sys, os, json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MONGO_URI, DATABASE_NAME, COLLECTIONS

def get_current_user():
    """Helper to get current user identity as dict"""
    identity = get_jwt_identity()
    if isinstance(identity, str):
        try:
            return json.loads(identity)
        except:
            return {"id": identity}
    return identity

doctor_bp = Blueprint('doctor', __name__)
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

def is_doctor(u): return u.get('role') == 'doctor'


def _serialize_datetime(obj):
    """Recursively convert datetime objects in a dict/list to ISO format strings"""
    if isinstance(obj, dict):
        return {k: _serialize_datetime(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_serialize_datetime(item) for item in obj]
    elif hasattr(obj, 'isoformat'):
        return obj.isoformat()
    return obj


def _find_patient(patient_id):
    """Find a patient record by trying multiple lookup strategies"""
    patient = None
    # Try finding in patients collection by user_id
    try:
        patient = db[COLLECTIONS['patients']].find_one(
            {"user_id": ObjectId(patient_id)}, {"password": 0}
        )
    except:
        pass
    # Try finding by _id in patients
    if not patient:
        try:
            patient = db[COLLECTIONS['patients']].find_one(
                {"_id": ObjectId(patient_id)}, {"password": 0}
            )
        except:
            pass
    # Try finding in users collection
    if not patient:
        try:
            patient = db[COLLECTIONS['users']].find_one(
                {"_id": ObjectId(patient_id), "role": "patient"}, {"password": 0}
            )
        except:
            pass
    if patient:
        patient['_id'] = str(patient['_id'])
        if 'user_id' in patient:
            patient['user_id'] = str(patient['user_id'])
    return patient


def _get_patient_medical_history(patient_id):
    """
    Aggregate complete medical history for a patient.
    Returns dict with: profile, past_appointments, ckd_predictions,
    symptom_logs, uploaded_reports, hybrid_predictions
    """
    import re as _re
    history = {}

    # 1. Patient profile
    patient = _find_patient(patient_id)
    if patient:
        history['profile'] = _serialize_datetime(patient)

    # Resolve patient email for hybrid_predictions lookup
    patient_email = ''
    if patient:
        patient_email = patient.get('email', '')

    # Build flexible $or query to match different ID storage patterns
    # Some collections store patient_id, others store user_id
    id_query = {"$or": [
        {"patient_id": patient_id},
        {"user_id": patient_id},
    ]}

    # 2. Past appointments (all statuses, newest first, limit 20)
    past_appointments = list(
        db[COLLECTIONS['appointments']].find(
            {"patient_id": patient_id}
        ).sort("created_at", -1).limit(20)
    )
    for apt in past_appointments:
        apt['_id'] = str(apt['_id'])
        # Attach doctor info for each past appointment
        if apt.get('doctor_id'):
            doc = None
            try:
                doc = db[COLLECTIONS['doctors']].find_one(
                    {"_id": ObjectId(apt['doctor_id'])}, {"password": 0}
                )
            except:
                pass
            if not doc:
                try:
                    doc = db[COLLECTIONS['users']].find_one(
                        {"_id": ObjectId(apt['doctor_id']), "role": "doctor"}, {"password": 0}
                    )
                except:
                    pass
            if doc:
                doc['_id'] = str(doc['_id'])
                if 'user_id' in doc:
                    doc['user_id'] = str(doc['user_id'])
                apt['doctor'] = _serialize_datetime(doc)
    history['past_appointments'] = _serialize_datetime(past_appointments)

    # 3. CKD prediction history (newest first, limit 10)
    # ckd.py stores: patient_id = current_user['id'], input_features = data
    ckd_predictions = list(
        db.ckd_predictions.find(id_query).sort("created_at", -1).limit(10)
    )
    for pred in ckd_predictions:
        pred['_id'] = str(pred['_id'])
        # Normalize: ckd.py stores raw inputs as 'input_features', frontend expects 'input_data'
        if 'input_features' in pred and 'input_data' not in pred:
            pred['input_data'] = pred.pop('input_features')
    history['ckd_predictions'] = _serialize_datetime(ckd_predictions)

    # 4. Symptom / disease prediction logs (newest first, limit 10)
    symptom_logs = list(
        db[COLLECTIONS['symptoms_logs']].find(id_query).sort("created_at", -1).limit(10)
    )
    for log in symptom_logs:
        log['_id'] = str(log['_id'])
    history['symptom_logs'] = _serialize_datetime(symptom_logs)

    # 5. Uploaded medical reports (newest first, limit 10)
    uploaded_reports = list(
        db.report_uploads.find(id_query).sort("created_at", -1).limit(10)
    )
    for rpt in uploaded_reports:
        rpt['_id'] = str(rpt['_id'])
        # Remove bulky raw text to keep payload manageable
        rpt.pop('extracted_text', None)
    history['uploaded_reports'] = _serialize_datetime(uploaded_reports)

    # 6. Hybrid AI predictions (newest first, limit 10)
    # hybrid.py stores: user_id = raw get_jwt_identity() which is a JSON string like
    # '{"id":"<oid>","email":"...","role":"patient","name":"..."}'
    # or could be a dict. We need to match using multiple strategies.
    hybrid_query_conditions = [
        {"user_id": patient_id},                       # plain id string
        {"patient_id": patient_id},                    # in case field was patient_id
    ]
    # Match JSON-encoded identity containing the patient ObjectId
    escaped_id = _re.escape(patient_id)
    hybrid_query_conditions.append(
        {"user_id": {"$regex": escaped_id}}
    )
    # Also match by email if available
    if patient_email:
        escaped_email = _re.escape(patient_email)
        hybrid_query_conditions.append(
            {"user_id": {"$regex": escaped_email}}
        )

    hybrid_predictions = list(
        db.hybrid_predictions.find(
            {"$or": hybrid_query_conditions}
        ).sort("timestamp", -1).limit(10)
    )
    for hp in hybrid_predictions:
        hp['_id'] = str(hp['_id'])
        # Normalize timestamp → created_at for frontend consistency
        if 'timestamp' in hp and 'created_at' not in hp:
            hp['created_at'] = hp.pop('timestamp')
        # Flatten nested prediction dict if present
        if isinstance(hp.get('prediction'), dict):
            pred_data = hp['prediction']
            hp['risk_level'] = pred_data.get('risk_level', '')
            hp['confidence'] = pred_data.get('confidence', 0)
            hp['ensemble_result'] = pred_data.get('result', '')
        # Include model type info
        if hp.get('model_details'):
            hp['models_used'] = list(hp['model_details'].keys())
    history['hybrid_predictions'] = _serialize_datetime(hybrid_predictions)

    return history


@doctor_bp.route('/appointments', methods=['GET'])
@jwt_required()
def get_doctor_appointments():
    try:
        current_user = get_current_user()
        if not is_doctor(current_user):
            return jsonify({"success": False, "message": "Access denied"}), 403
        status = request.args.get('status')
        query = {"doctor_id": current_user['id']}
        if status: query["status"] = status
        appointments = list(db[COLLECTIONS['appointments']].find(query).sort("appointment_date", 1))
        
        for apt in appointments:
            apt['_id'] = str(apt['_id'])
            
            # Convert datetime objects to strings
            if 'created_at' in apt and hasattr(apt['created_at'], 'isoformat'):
                apt['created_at'] = apt['created_at'].isoformat()
            if 'updated_at' in apt and hasattr(apt['updated_at'], 'isoformat'):
                apt['updated_at'] = apt['updated_at'].isoformat()
            
            # Get patient details
            if apt.get('patient_id'):
                patient = _find_patient(apt['patient_id'])
                if patient:
                    apt['patient'] = patient
                    
        return jsonify({"success": True, "appointments": appointments}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500

@doctor_bp.route('/appointments/upcoming', methods=['GET'])
@jwt_required()
def get_upcoming():
    try:
        current_user = get_current_user()
        if not is_doctor(current_user):
            return jsonify({"success": False, "message": "Access denied"}), 403
        today = datetime.utcnow().strftime('%Y-%m-%d')
        appointments = list(db[COLLECTIONS['appointments']].find({
            "doctor_id": current_user['id'], "status": {"$in": ["pending", "confirmed"]},
            "appointment_date": {"$gte": today}
        }).sort("appointment_date", 1))
        
        for apt in appointments:
            apt['_id'] = str(apt['_id'])
            
            # Convert datetime objects to strings
            if 'created_at' in apt and hasattr(apt['created_at'], 'isoformat'):
                apt['created_at'] = apt['created_at'].isoformat()
            if 'updated_at' in apt and hasattr(apt['updated_at'], 'isoformat'):
                apt['updated_at'] = apt['updated_at'].isoformat()
            
            # Get patient details
            if apt.get('patient_id'):
                patient = _find_patient(apt['patient_id'])
                if patient:
                    apt['patient'] = patient
                    
        return jsonify({"success": True, "appointments": appointments}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500

@doctor_bp.route('/update-status', methods=['PUT'])
@jwt_required()
def update_status():
    try:
        current_user = get_current_user()
        if not is_doctor(current_user):
            return jsonify({"success": False, "message": "Access denied"}), 403
        data = request.get_json()
        if not data.get('appointment_id') or not data.get('status'):
            return jsonify({"success": False, "message": "appointment_id and status required"}), 400
        update_data = {"status": data['status'], "updated_at": datetime.utcnow()}
        if data.get('doctor_notes'): update_data['doctor_notes'] = data['doctor_notes']
        if data.get('prescription'): update_data['prescription'] = data['prescription']

        # Fetch appointment first to get patient_id
        appointment = db[COLLECTIONS['appointments']].find_one(
            {"_id": ObjectId(data['appointment_id']), "doctor_id": current_user['id']}
        )
        if not appointment:
            return jsonify({"success": False, "message": "Appointment not found"}), 404

        result = db[COLLECTIONS['appointments']].update_one(
            {"_id": ObjectId(data['appointment_id']), "doctor_id": current_user['id']},
            {"$set": update_data}
        )
        if result.modified_count == 0:
            return jsonify({"success": False, "message": "Appointment not found or unchanged"}), 404

        response = {"success": True, "message": f"Status updated to {data['status']}"}

        # When doctor accepts (confirms) the appointment, include full medical history
        if data['status'] == 'confirmed' and appointment.get('patient_id'):
            response['medical_history'] = _get_patient_medical_history(appointment['patient_id'])

        return jsonify(response), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500


@doctor_bp.route('/patient-history/<patient_id>', methods=['GET'])
@jwt_required()
def get_patient_history(patient_id):
    """
    Get complete medical history for a patient.
    Accessible by doctors only.
    Returns profile, past appointments, CKD predictions, symptom logs,
    uploaded reports, and hybrid AI predictions.
    """
    try:
        current_user = get_current_user()
        if not is_doctor(current_user):
            return jsonify({"success": False, "message": "Access denied"}), 403

        history = _get_patient_medical_history(patient_id)

        if not history.get('profile'):
            return jsonify({"success": False, "message": "Patient not found"}), 404

        return jsonify({"success": True, "medical_history": history}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500


@doctor_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    try:
        current_user = get_current_user()
        if not is_doctor(current_user):
            return jsonify({"success": False, "message": "Access denied"}), 403
        today = datetime.utcnow().strftime('%Y-%m-%d')
        stats = {
            "total": db[COLLECTIONS['appointments']].count_documents({"doctor_id": current_user['id']}),
            "today": db[COLLECTIONS['appointments']].count_documents({"doctor_id": current_user['id'], "appointment_date": today}),
            "pending": db[COLLECTIONS['appointments']].count_documents({"doctor_id": current_user['id'], "status": "pending"}),
            "completed": db[COLLECTIONS['appointments']].count_documents({"doctor_id": current_user['id'], "status": "completed"})
        }
        return jsonify({"success": True, "stats": stats}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
