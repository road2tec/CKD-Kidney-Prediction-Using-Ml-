# Authentication Routes for Smart Patient Healthcare System
# Handles user registration, login, and authentication

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from bson import ObjectId
import bcrypt
from datetime import datetime
import sys
import os
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MONGO_URI, DATABASE_NAME, COLLECTIONS
from models.user import User, Patient, Doctor, Admin

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
auth_bp = Blueprint('auth', __name__)

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new patient
    Expected JSON: { name, email, password, phone, age, gender, blood_group, address }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "message": f"{field} is required"
                }), 400
        
        # Check if email already exists
        existing_user = db[COLLECTIONS['users']].find_one({"email": data['email']})
        if existing_user:
            return jsonify({
                "success": False,
                "message": "Email already registered"
            }), 400
        
        # Create patient object
        patient = Patient(
            email=data['email'],
            password=data['password'],
            name=data['name'],
            phone=data.get('phone'),
            address=data.get('address'),
            age=data.get('age'),
            gender=data.get('gender'),
            blood_group=data.get('blood_group')
        )
        
        # Insert into users collection
        user_data = patient.to_dict()
        user_result = db[COLLECTIONS['users']].insert_one(user_data)
        
        # Also insert into patients collection with user reference
        patient_data = patient.to_dict()
        patient_data['user_id'] = user_result.inserted_id
        db[COLLECTIONS['patients']].insert_one(patient_data)
        
        # Generate access token
        access_token = create_access_token(identity={
            "id": str(user_result.inserted_id),
            "email": data['email'],
            "role": "patient",
            "name": data['name']
        })
        
        return jsonify({
            "success": True,
            "message": "Registration successful",
            "token": access_token,
            "user": {
                "id": str(user_result.inserted_id),
                "name": data['name'],
                "email": data['email'],
                "role": "patient"
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Registration failed: {str(e)}"
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user (patient, doctor, or admin)
    Expected JSON: { email, password, role (optional) }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({
                "success": False,
                "message": "Email and password are required"
            }), 400
        
        # Find user by email
        user = db[COLLECTIONS['users']].find_one({"email": data['email']})
        
        if not user:
            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401
        
        # Verify password
        if not User.verify_password(data['password'], user['password']):
            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401
        
        # Check if user is active
        if not user.get('is_active', True):
            return jsonify({
                "success": False,
                "message": "Account is deactivated"
            }), 401
        
        # Generate access token
        access_token = create_access_token(identity={
            "id": str(user['_id']),
            "email": user['email'],
            "role": user['role'],
            "name": user['name']
        })
        
        return jsonify({
            "success": True,
            "message": "Login successful",
            "token": access_token,
            "user": {
                "id": str(user['_id']),
                "name": user['name'],
                "email": user['email'],
                "role": user['role']
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Login failed: {str(e)}"
        }), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current logged in user details"""
    try:
        current_user = get_current_user()
        user = db[COLLECTIONS['users']].find_one(
            {"_id": ObjectId(current_user['id'])},
            {"password": 0}  # Exclude password
        )
        
        if not user:
            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404
        
        user['_id'] = str(user['_id'])
        
        return jsonify({
            "success": True,
            "user": user
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error fetching user: {str(e)}"
        }), 500


@auth_bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        # Fields that can be updated
        update_fields = {}
        allowed_fields = ['name', 'phone', 'address', 'age', 'gender', 'blood_group']
        
        for field in allowed_fields:
            if field in data:
                update_fields[field] = data[field]
        
        update_fields['updated_at'] = datetime.utcnow()
        
        # Update user in users collection
        db[COLLECTIONS['users']].update_one(
            {"_id": ObjectId(current_user['id'])},
            {"$set": update_fields}
        )
        
        # If patient, also update patients collection
        if current_user['role'] == 'patient':
            db[COLLECTIONS['patients']].update_one(
                {"user_id": ObjectId(current_user['id'])},
                {"$set": update_fields}
            )
        
        return jsonify({
            "success": True,
            "message": "Profile updated successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error updating profile: {str(e)}"
        }), 500


@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({
                "success": False,
                "message": "Current password and new password are required"
            }), 400
        
        # Get user
        user = db[COLLECTIONS['users']].find_one({"_id": ObjectId(current_user['id'])})
        
        if not user:
            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404
        
        # Verify current password
        if not User.verify_password(data['current_password'], user['password']):
            return jsonify({
                "success": False,
                "message": "Current password is incorrect"
            }), 400
        
        # Hash new password
        new_password_hash = User.hash_password(data['new_password'])
        
        # Update password
        db[COLLECTIONS['users']].update_one(
            {"_id": ObjectId(current_user['id'])},
            {"$set": {
                "password": new_password_hash,
                "updated_at": datetime.utcnow()
            }}
        )
        
        return jsonify({
            "success": True,
            "message": "Password changed successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error changing password: {str(e)}"
        }), 500
