# Donor-Patient Matching Module for CKD/Kidney Transplant

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
donor_bp = Blueprint('donor', __name__)

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# Blood type compatibility matrix
BLOOD_COMPATIBILITY = {
    'A+': ['A+', 'A-', 'O+', 'O-'],
    'A-': ['A-', 'O-'],
    'B+': ['B+', 'B-', 'O+', 'O-'],
    'B-': ['B-', 'O-'],
    'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],  # Universal recipient
    'AB-': ['A-', 'B-', 'AB-', 'O-'],
    'O+': ['O+', 'O-'],
    'O-': ['O-']  # Universal donor
}


@donor_bp.route('/register', methods=['POST'])
@jwt_required()
def register_donor():
    """
    Register as a kidney donor
    Expected JSON: { blood_group, age, weight, height, health_conditions, contact_phone, is_living_donor }
    """
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['blood_group', 'age', 'weight', 'contact_phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "success": False,
                    "message": f"{field} is required"
                }), 400
        
        # Validate age (donors typically 18-65)
        try:
            age = int(data['age'])
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "message": "Age must be a valid number"
            }), 400
            
        if age < 18 or age > 65:
            return jsonify({
                "success": False,
                "message": "Donor age must be between 18 and 65 years"
            }), 400
        
        # Validate weight
        try:
            weight = float(data['weight'])
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "message": "Weight must be a valid number"
            }), 400
        
        # Check if already registered
        existing = db.donors.find_one({'user_id': current_user['id']})
        if existing:
            return jsonify({
                "success": False,
                "message": "You are already registered as a donor"
            }), 400
        
        # Create donor record
        try:
            height = float(data.get('height', 0) or 0)
        except (ValueError, TypeError):
            height = 0.0
            
        donor_record = {
            'user_id': current_user['id'],
            'name': current_user.get('name', 'Unknown'),
            'email': current_user.get('email', ''),
            'blood_group': data['blood_group'].upper(),
            'age': age,
            'weight': weight,
            'height': height,
            'health_conditions': data.get('health_conditions', []),
            'contact_phone': data['contact_phone'],
            'is_living_donor': data.get('is_living_donor', True),
            'is_available': True,
            'is_verified': True,  # Auto-verify for demonstration purposes
            'registration_date': datetime.utcnow(),
            'last_updated': datetime.utcnow()
        }
        
        result = db.donors.insert_one(donor_record)
        
        return jsonify({
            "success": True,
            "message": "Donor registration successful. Medical verification pending.",
            "donor_id": str(result.inserted_id)
        }), 201
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Donor registration failed: {str(e)}"
        }), 500


@donor_bp.route('/match', methods=['POST'])
@jwt_required()
def find_matching_donors():
    """
    Find compatible kidney donors for a patient
    Expected JSON: { blood_group, age, urgency_level }
    """
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        patient_blood_group = data.get('blood_group', '').upper()
        patient_age = int(data.get('age', 50))
        urgency_level = data.get('urgency_level', 'normal')  # critical, high, normal
        
        if not patient_blood_group:
            return jsonify({
                "success": False,
                "message": "Patient blood group is required"
            }), 400
        
        # Get compatible blood groups
        compatible_groups = BLOOD_COMPATIBILITY.get(patient_blood_group, [])
        
        # Query for compatible donors
        query = {
            'blood_group': {'$in': compatible_groups},
            'is_available': True,
            'is_verified': True
        }
        
        # Age proximity (prefer donors within ±15 years)
        age_range = 15
        
        donors = list(db.donors.find(query))
        
        # New Scoring System (Max 100)
        # Blood Match: 40
        # Age Match: 20
        # Health Status: 25
        # Availability: 15

        scored_donors = []
        for donor in donors:
            score = 0
            reasons = []
            
            # 1. Blood Match (40 pts) - Already filtered for compatibility
            # Hard constraint met, so base 40.
            score += 40
            reasons.append("Blood group compatible (+40)")
            
            # 2. Age Match (20 pts)
            # Ideal gap +/- 15 years. Closer is better? 
            # User said: "Ideal age gap: ±15 years. Larger gaps reduce compatibility score"
            age_diff = abs(donor['age'] - patient_age)
            age_score = 0
            if age_diff <= 5:
                age_score = 20
                reasons.append(f"Age difference {age_diff} years (Optimally matched +20)")
            elif age_diff <= 10:
                age_score = 15
                reasons.append(f"Age difference {age_diff} years (Well matched +15)")
            elif age_diff <= 15:
                age_score = 10
                reasons.append(f"Age difference {age_diff} years (Within safe range +10)")
            else:
                age_score = 5
                reasons.append(f"Age difference {age_diff} years (Acceptable match +5)")
            
            score += age_score
            
            # 3. Health Status (25 pts)
            health_score = 0
            conditions = donor.get('health_conditions', [])
            if not conditions:
                health_score = 25
                reasons.append("Donor health optimal (+25)")
            elif len(conditions) == 1:
                health_score = 15
                reasons.append(f"Minor health risk: {conditions[0]} (+15)")
            else:
                health_score = 5
                reasons.append(f"Multiple health factors: {', '.join(conditions)} (+5)")
            
            score += health_score
            
            # 4. Availability (15 pts) - Verified by query
            if donor.get('is_available'):
                score += 15
                reasons.append("Currently available (+15)")
            
            donor['compatibility_score'] = score
            donor['match_reason'] = reasons
            donor['age_difference'] = age_diff
            donor['_id'] = str(donor['_id'])
            
            # Remove sensitive info
            donor.pop('user_id', None)
            donor.pop('email', None)
            
            scored_donors.append(donor)
        
        # Sort by compatibility score
        scored_donors.sort(key=lambda x: x['compatibility_score'], reverse=True)
        
        # Log the match request
        match_log = {
            'patient_id': current_user['id'],
            'patient_blood_group': patient_blood_group,
            'urgency_level': urgency_level,
            'matches_found': len(scored_donors),
            'top_match_score': scored_donors[0]['compatibility_score'] if scored_donors else 0,
            'created_at': datetime.utcnow()
        }
        db.donor_matches.insert_one(match_log)
        
        return jsonify({
            "success": True,
            "matches_found": len(scored_donors),
            "compatible_donors": scored_donors[:5],  # Top 5 matches as requested
            "patient_blood_group": patient_blood_group,
            "compatible_blood_groups": compatible_groups,
            "message": "Top 5 medically compatible donors identified based on weighted scoring"
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Donor matching failed: {str(e)}"
        }), 500


@donor_bp.route('/my-profile', methods=['GET'])
@jwt_required()
def get_donor_profile():
    """Get current user's donor profile"""
    try:
        current_user = get_current_user()
        
        donor = db.donors.find_one({'user_id': current_user['id']})
        
        if not donor:
            return jsonify({
                "success": False,
                "message": "Not registered as a donor"
            }), 404
        
        donor['_id'] = str(donor['_id'])
        if 'registration_date' in donor:
            donor['registration_date'] = donor['registration_date'].isoformat()
        if 'last_updated' in donor:
            donor['last_updated'] = donor['last_updated'].isoformat()
        
        return jsonify({
            "success": True,
            "donor_profile": donor
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to fetch donor profile: {str(e)}"
        }), 500


@donor_bp.route('/update-availability', methods=['PUT'])
@jwt_required()
def update_availability():
    """Update donor availability status"""
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        is_available = data.get('is_available', True)
        
        result = db.donors.update_one(
            {'user_id': current_user['id']},
            {
                '$set': {
                    'is_available': is_available,
                    'last_updated': datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            return jsonify({
                "success": False,
                "message": "Donor profile not found"
            }), 404
        
        return jsonify({
            "success": True,
            "message": f"Availability updated to: {'Available' if is_available else 'Not Available'}"
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Update failed: {str(e)}"
        }), 500


@donor_bp.route('/statistics', methods=['GET'])
def get_donor_statistics():
    """Get donor statistics (public endpoint)"""
    try:
        # Count all registered donors regardless of verification status
        total_donors = db.donors.count_documents({})
        # Count only available and verified donors for availability
        available_donors = db.donors.count_documents({'is_available': True, 'is_verified': True})
        
        # Count successful matches
        successful_matches = db.donor_matches.count_documents({})

        # Blood group distribution (for Verified donors only to ensure quality)
        pipeline = [
            {'$match': {'is_verified': True}},
            {'$group': {'_id': '$blood_group', 'count': {'$sum': 1}}}
        ]
        blood_group_dist = list(db.donors.aggregate(pipeline))
        
        blood_group_stats = {item['_id']: item['count'] for item in blood_group_dist}
        
        return jsonify({
            "success": True,
            "statistics": {
                "total_registered_donors": total_donors,
                "available_donors": available_donors,
                "successful_matches": successful_matches,
                "blood_group_distribution": blood_group_stats
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to fetch statistics: {str(e)}"
        }), 500
