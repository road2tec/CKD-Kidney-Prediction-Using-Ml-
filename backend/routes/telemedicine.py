# Telemedicine Module for Remote CKD Consultations

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
import json
import sys
import os

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

# Create blueprint
telemedicine_bp = Blueprint('telemedicine', __name__)

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]


@telemedicine_bp.route('/create-session', methods=['POST'])
@jwt_required()
def create_telemedicine_session():
    """
    Create a telemedicine consultation session
    Expected JSON: { doctor_id, appointment_id, session_type, scheduled_time }
    """
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('doctor_id') or not data.get('session_type'):
            return jsonify({
                "success": False,
                "message": "doctor_id and session_type are required"
            }), 400
        
        # Create session
        session = {
            'patient_id': current_user['id'],
            'doctor_id': data['doctor_id'],
            'appointment_id': data.get('appointment_id'),
            'session_type': data['session_type'],  # video, audio, chat
            'status': 'scheduled',  # scheduled, active, completed, cancelled
            'scheduled_time': data.get('scheduled_time', datetime.utcnow().isoformat()),
            'duration_minutes': data.get('duration_minutes', 30),
            'notes': data.get('notes', ''),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = db.telemedicine_sessions.insert_one(session)
        
        # Update appointment if linked
        if data.get('appointment_id'):
            db[COLLECTIONS['appointments']].update_one(
                {'_id': ObjectId(data['appointment_id'])},
                {'$set': {'telemedicine_session_id': str(result.inserted_id)}}
            )
        
        return jsonify({
            "success": True,
            "message": "Telemedicine session created successfully",
            "session_id": str(result.inserted_id),
            "session_details": {
                "session_type": session['session_type'],
                "scheduled_time": session['scheduled_time'],
                "duration": session['duration_minutes']
            }
        }), 201
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Failed to create session: {str(e)}"
        }), 500


@telemedicine_bp.route('/my-sessions', methods=['GET'])
@jwt_required()
def get_my_sessions():
    """Get all telemedicine sessions for current user"""
    try:
        current_user = get_current_user()
        
        # Check user role
        query = {}
        if current_user.get('role') == 'patient':
            query['patient_id'] = current_user['id']
        elif current_user.get('role') == 'doctor':
            query['doctor_id'] = current_user['id']
        else:
            return jsonify({
                "success": False,
                "message": "Unauthorized access"
            }), 403
        
        sessions = list(db.telemedicine_sessions.find(query).sort('created_at', -1))
        
        # Enrich with user details
        for session in sessions:
            session['_id'] = str(session['_id'])
            
            # Convert datetime to string
            if 'created_at' in session:
                session['created_at'] = session['created_at'].isoformat()
            if 'updated_at' in session:
                session['updated_at'] = session['updated_at'].isoformat()
            
            # Get patient details if doctor
            if current_user.get('role') == 'doctor' and session.get('patient_id'):
                patient = db[COLLECTIONS['users']].find_one(
                    {'_id': ObjectId(session['patient_id'])},
                    {'password': 0}
                )
                if patient:
                    session['patient_name'] = patient.get('name', 'Unknown')
            
            # Get doctor details if patient
            if current_user.get('role') == 'patient' and session.get('doctor_id'):
                doctor = db[COLLECTIONS['doctors']].find_one(
                    {'_id': ObjectId(session['doctor_id'])},
                    {'password': 0}
                )
                if doctor:
                    session['doctor_name'] = doctor.get('name', 'Unknown')
                    session['doctor_specialization'] = doctor.get('specialization', 'General')
        
        return jsonify({
            "success": True,
            "sessions": sessions
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Failed to fetch sessions: {str(e)}"
        }), 500


@telemedicine_bp.route('/session/<session_id>', methods=['GET'])
@jwt_required()
def get_session_details(session_id):
    """Get details of a specific session"""
    try:
        current_user = get_current_user()
        
        session = db.telemedicine_sessions.find_one({'_id': ObjectId(session_id)})
        
        if not session:
            return jsonify({
                "success": False,
                "message": "Session not found"
            }), 404
        
        # Verify access
        if session['patient_id'] != current_user['id'] and session['doctor_id'] != current_user['id']:
            return jsonify({
                "success": False,
                "message": "Unauthorized access to this session"
            }), 403
        
        session['_id'] = str(session['_id'])
        if 'created_at' in session:
            session['created_at'] = session['created_at'].isoformat()
        if 'updated_at' in session:
            session['updated_at'] = session['updated_at'].isoformat()
        
        return jsonify({
            "success": True,
            "session": session
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to fetch session: {str(e)}"
        }), 500


@telemedicine_bp.route('/session/<session_id>/update-status', methods=['PUT'])
@jwt_required()
def update_session_status(session_id):
    """
    Update session status (start, end, cancel)
    Expected JSON: { status, notes }
    """
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        new_status = data.get('status', 'active')
        notes = data.get('notes', '')
        
        # Verify session exists and user has access
        session = db.telemedicine_sessions.find_one({'_id': ObjectId(session_id)})
        
        if not session:
            return jsonify({
                "success": False,
                "message": "Session not found"
            }), 404
        
        if session['patient_id'] != current_user['id'] and session['doctor_id'] != current_user['id']:
            return jsonify({
                "success": False,
                "message": "Unauthorized"
            }), 403
        
        # Update session
        update_data = {
            'status': new_status,
            'updated_at': datetime.utcnow()
        }
        
        if new_status == 'active':
            update_data['started_at'] = datetime.utcnow()
        elif new_status == 'completed':
            update_data['completed_at'] = datetime.utcnow()
            if notes:
                update_data['consultation_notes'] = notes
        
        db.telemedicine_sessions.update_one(
            {'_id': ObjectId(session_id)},
            {'$set': update_data}
        )
        
        return jsonify({
            "success": True,
            "message": f"Session status updated to: {new_status}"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to update session: {str(e)}"
        }), 500


@telemedicine_bp.route('/session/<session_id>/add-note', methods=['POST'])
@jwt_required()
def add_session_note(session_id):
    """
    Add consultation notes to a session (doctor only)
    Expected JSON: { note, prescription, follow_up_date }
    """
    try:
        current_user = get_current_user()
        
        if current_user.get('role') != 'doctor':
            return jsonify({
                "success": False,
                "message": "Only doctors can add consultation notes"
            }), 403
        
        data = request.get_json()
        
        # Verify session
        session = db.telemedicine_sessions.find_one({'_id': ObjectId(session_id)})
        
        if not session or session['doctor_id'] != current_user['id']:
            return jsonify({
                "success": False,
                "message": "Session not found or unauthorized"
            }), 404
        
        # Add note
        note = {
            'doctor_id': current_user['id'],
            'note': data.get('note', ''),
            'prescription': data.get('prescription', []),
            'follow_up_date': data.get('follow_up_date'),
            'vital_signs': data.get('vital_signs', {}),
            'diagnosis': data.get('diagnosis', ''),
            'created_at': datetime.utcnow()
        }
        
        db.telemedicine_sessions.update_one(
            {'_id': ObjectId(session_id)},
            {
                '$push': {'consultation_notes': note},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        
        return jsonify({
            "success": True,
            "message": "Consultation note added successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to add note: {str(e)}"
        }), 500


@telemedicine_bp.route('/available-slots', methods=['GET'])
@jwt_required()
def get_available_slots():
    """Get available telemedicine slots for next 7 days"""
    try:
        doctor_id = request.args.get('doctor_id')
        
        if not doctor_id:
            return jsonify({
                "success": False,
                "message": "doctor_id is required"
            }), 400
        
        # Get doctor's existing sessions
        existing_sessions = list(db.telemedicine_sessions.find({
            'doctor_id': doctor_id,
            'status': {'$in': ['scheduled', 'active']}
        }))
        
        booked_times = [session.get('scheduled_time') for session in existing_sessions]
        
        # Generate available slots (9 AM - 5 PM, every 30 minutes)
        available_slots = []
        for day in range(7):
            date = datetime.utcnow() + timedelta(days=day)
            for hour in range(9, 17):  # 9 AM to 5 PM
                for minute in [0, 30]:
                    slot_time = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    if slot_time.isoformat() not in booked_times and slot_time > datetime.utcnow():
                        available_slots.append(slot_time.isoformat())
        
        return jsonify({
            "success": True,
            "available_slots": available_slots[:50]  # Return first 50 slots
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to fetch slots: {str(e)}"
        }), 500


@telemedicine_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_telemedicine_statistics():
    """Get telemedicine statistics for current user"""
    try:
        current_user = get_current_user()
        
        query = {}
        if current_user.get('role') == 'patient':
            query['patient_id'] = current_user['id']
        elif current_user.get('role') == 'doctor':
            query['doctor_id'] = current_user['id']
        
        total_sessions = db.telemedicine_sessions.count_documents(query)
        completed_sessions = db.telemedicine_sessions.count_documents({**query, 'status': 'completed'})
        upcoming_sessions = db.telemedicine_sessions.count_documents({**query, 'status': 'scheduled'})
        
        return jsonify({
            "success": True,
            "statistics": {
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "upcoming_sessions": upcoming_sessions
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to fetch statistics: {str(e)}"
        }), 500
