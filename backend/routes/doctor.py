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
            
            # Get patient details - try multiple ways
            if apt.get('patient_id'):
                patient_id = apt['patient_id']
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
                patient_id = apt['patient_id']
                patient = None
                
                try:
                    patient = db[COLLECTIONS['patients']].find_one(
                        {"user_id": ObjectId(patient_id)}, {"password": 0}
                    )
                except:
                    pass
                
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
        result = db[COLLECTIONS['appointments']].update_one(
            {"_id": ObjectId(data['appointment_id']), "doctor_id": current_user['id']}, {"$set": update_data})
        if result.modified_count == 0:
            return jsonify({"success": False, "message": "Appointment not found"}), 404
        return jsonify({"success": True, "message": f"Status updated to {data['status']}"}), 200
    except Exception as e:
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
