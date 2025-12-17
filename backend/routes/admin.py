# Admin Routes for Smart Patient Healthcare System
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import sys, os, json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MONGO_URI, DATABASE_NAME, COLLECTIONS
from models.user import User, Doctor
from models.appointment import AdminLog

def get_current_user():
    """Helper to get current user identity as dict"""
    identity = get_jwt_identity()
    if isinstance(identity, str):
        try:
            return json.loads(identity)
        except:
            return {"id": identity}
    return identity

admin_bp = Blueprint('admin', __name__)
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

def is_admin(u): return u.get('role') == 'admin'

def log_action(admin_id, action, target_type, target_id, details=None):
    log = AdminLog(admin_id, action, target_type, target_id, details)
    db[COLLECTIONS['admin_logs']].insert_one(log.to_dict())

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    try:
        current_user = get_current_user()
        if not is_admin(current_user):
            return jsonify({"success": False, "message": "Access denied"}), 403
        role = request.args.get('role')
        query = {} if not role else {"role": role}
        users = list(db[COLLECTIONS['users']].find(query, {"password": 0}))
        for u in users: u['_id'] = str(u['_id'])
        return jsonify({"success": True, "users": users}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route('/add-doctor', methods=['POST'])
@jwt_required()
def add_doctor():
    try:
        current_user = get_current_user()
        if not is_admin(current_user):
            return jsonify({"success": False, "message": "Access denied"}), 403
        data = request.get_json()
        required = ['name', 'email', 'password', 'specialization']
        for f in required:
            if not data.get(f):
                return jsonify({"success": False, "message": f"{f} required"}), 400
        if db[COLLECTIONS['users']].find_one({"email": data['email']}):
            return jsonify({"success": False, "message": "Email exists"}), 400
        doctor = Doctor(
            email=data['email'], password=data['password'], name=data['name'],
            phone=data.get('phone'), address=data.get('address'),
            specialization=data['specialization'], qualification=data.get('qualification'),
            experience=data.get('experience'), consultation_fee=data.get('consultation_fee'))
        doc_data = doctor.to_dict()
        result = db[COLLECTIONS['users']].insert_one(doc_data)
        doc_data['user_id'] = result.inserted_id
        db[COLLECTIONS['doctors']].insert_one(doc_data)
        log_action(current_user['id'], 'add', 'doctor', str(result.inserted_id))
        return jsonify({"success": True, "message": "Doctor added", "doctor_id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route('/delete-user/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    try:
        current_user = get_current_user()
        if not is_admin(current_user):
            return jsonify({"success": False, "message": "Access denied"}), 403
        user = db[COLLECTIONS['users']].find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404
        db[COLLECTIONS['users']].update_one({"_id": ObjectId(user_id)}, {"$set": {"is_active": False}})
        if user['role'] == 'doctor':
            db[COLLECTIONS['doctors']].update_one({"user_id": ObjectId(user_id)}, {"$set": {"is_active": False}})
        elif user['role'] == 'patient':
            db[COLLECTIONS['patients']].update_one({"user_id": ObjectId(user_id)}, {"$set": {"is_active": False}})
        log_action(current_user['id'], 'delete', user['role'], user_id)
        return jsonify({"success": True, "message": "User deactivated"}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route('/appointments', methods=['GET'])
@jwt_required()
def get_all_appointments():
    try:
        current_user = get_current_user()
        if not is_admin(current_user):
            return jsonify({"success": False, "message": "Access denied"}), 403
        appointments = list(db[COLLECTIONS['appointments']].find().sort("created_at", -1).limit(100))
        for apt in appointments:
            apt['_id'] = str(apt['_id'])
        return jsonify({"success": True, "appointments": appointments}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    try:
        current_user = get_current_user()
        if not is_admin(current_user):
            return jsonify({"success": False, "message": "Access denied"}), 403
        stats = {
            "patients": db[COLLECTIONS['users']].count_documents({"role": "patient", "is_active": True}),
            "doctors": db[COLLECTIONS['users']].count_documents({"role": "doctor", "is_active": True}),
            "appointments": db[COLLECTIONS['appointments']].count_documents({}),
            "predictions": db[COLLECTIONS['symptoms_logs']].count_documents({})
        }
        return jsonify({"success": True, "stats": stats}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_logs():
    try:
        current_user = get_current_user()
        if not is_admin(current_user):
            return jsonify({"success": False, "message": "Access denied"}), 403
        logs = list(db[COLLECTIONS['admin_logs']].find().sort("created_at", -1).limit(50))
        for log in logs: log['_id'] = str(log['_id'])
        return jsonify({"success": True, "logs": logs}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route('/doctors', methods=['GET'])
@jwt_required()
def get_doctors():
    try:
        current_user = get_current_user()
        if not is_admin(current_user):
            return jsonify({"success": False, "message": "Access denied"}), 403
        doctors = list(db[COLLECTIONS['doctors']].find({}, {"password": 0}))
        for d in doctors:
            d['_id'] = str(d['_id'])
            if 'user_id' in d: d['user_id'] = str(d['user_id'])
        return jsonify({"success": True, "doctors": doctors}), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
