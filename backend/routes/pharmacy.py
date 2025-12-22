"""
Pharmacy & Medicine Recommendation System for CKD Patients
Dynamic pharmacy management with CRUD operations for admins
Medicine search functionality for patients
Database-backed storage for pharmacies and medicines
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId
import json
import re

pharmacy_bp = Blueprint('pharmacy', __name__)


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


def init_default_data(db):
    """Initialize default pharmacies and medicines if not exist"""
    # Default CKD Medicines
    if db.medicines.count_documents({}) == 0:
        default_medicines = [
            # Blood Pressure
            {
                'name': 'ACE Inhibitors (Lisinopril, Enalapril)',
                'category': 'blood_pressure',
                'category_name': 'Antihypertensives',
                'purpose': 'Lower blood pressure and protect kidneys',
                'notes': 'First-line for CKD with diabetes',
                'common_dosage': 'As prescribed by physician',
                'requires_prescription': True,
                'ckd_relevance': 'High',
                'price_range': '₹50-200',
                'is_active': True,
                'created_at': datetime.utcnow()
            },
            {
                'name': 'ARBs (Losartan, Valsartan)',
                'category': 'blood_pressure',
                'category_name': 'Antihypertensives',
                'purpose': 'Alternative to ACE inhibitors for BP control',
                'notes': 'Useful if ACE inhibitor causes cough',
                'common_dosage': 'As prescribed by physician',
                'requires_prescription': True,
                'ckd_relevance': 'High',
                'price_range': '₹80-300',
                'is_active': True,
                'created_at': datetime.utcnow()
            },
            {
                'name': 'Calcium Channel Blockers (Amlodipine)',
                'category': 'blood_pressure',
                'category_name': 'Antihypertensives',
                'purpose': 'Additional BP control',
                'notes': 'Often combined with ACE/ARB',
                'common_dosage': 'As prescribed by physician',
                'requires_prescription': True,
                'ckd_relevance': 'Medium',
                'price_range': '₹30-150',
                'is_active': True,
                'created_at': datetime.utcnow()
            },
            # Diabetes Management
            {
                'name': 'SGLT2 Inhibitors (Dapagliflozin, Empagliflozin)',
                'category': 'diabetes_management',
                'category_name': 'Antidiabetics',
                'purpose': 'Blood sugar control + kidney protection',
                'notes': 'Shown to slow CKD progression',
                'common_dosage': 'As prescribed by physician',
                'requires_prescription': True,
                'ckd_relevance': 'High',
                'price_range': '₹500-1500',
                'is_active': True,
                'created_at': datetime.utcnow()
            },
            {
                'name': 'Metformin',
                'category': 'diabetes_management',
                'category_name': 'Antidiabetics',
                'purpose': 'First-line diabetes treatment',
                'notes': 'Dose adjustment needed in CKD',
                'common_dosage': 'Reduced dose in CKD Stage 3+',
                'requires_prescription': True,
                'ckd_relevance': 'Medium',
                'price_range': '₹20-100',
                'is_active': True,
                'created_at': datetime.utcnow()
            },
            # Anemia Management
            {
                'name': 'Erythropoiesis-Stimulating Agents (ESAs)',
                'category': 'anemia_management',
                'category_name': 'Anemia Treatment',
                'purpose': 'Increase red blood cell production',
                'notes': 'For CKD-related anemia',
                'common_dosage': 'Injectable, as prescribed',
                'requires_prescription': True,
                'ckd_relevance': 'High',
                'price_range': '₹2000-5000',
                'is_active': True,
                'created_at': datetime.utcnow()
            },
            {
                'name': 'Iron Supplements (Oral/IV)',
                'category': 'anemia_management',
                'category_name': 'Anemia Treatment',
                'purpose': 'Treat iron deficiency anemia',
                'notes': 'Often used with ESAs',
                'common_dosage': 'As prescribed based on iron levels',
                'requires_prescription': True,
                'ckd_relevance': 'Medium',
                'price_range': '₹100-500',
                'is_active': True,
                'created_at': datetime.utcnow()
            },
            # Phosphate Binders
            {
                'name': 'Sevelamer (Renvela)',
                'category': 'phosphate_binders',
                'category_name': 'Mineral Management',
                'purpose': 'Lower phosphorus levels',
                'notes': 'Taken with meals',
                'common_dosage': 'As prescribed',
                'requires_prescription': True,
                'ckd_relevance': 'High',
                'price_range': '₹800-2000',
                'is_active': True,
                'created_at': datetime.utcnow()
            },
            {
                'name': 'Calcium Acetate',
                'category': 'phosphate_binders',
                'category_name': 'Mineral Management',
                'purpose': 'Bind dietary phosphorus',
                'notes': 'Also provides calcium',
                'common_dosage': 'With meals, as prescribed',
                'requires_prescription': True,
                'ckd_relevance': 'Medium',
                'price_range': '₹200-600',
                'is_active': True,
                'created_at': datetime.utcnow()
            },
            # Supplements
            {
                'name': 'Vitamin D (Calcitriol)',
                'category': 'supplements',
                'category_name': 'Nutritional Supplements',
                'purpose': 'Maintain bone health',
                'notes': 'Active form often needed in CKD',
                'common_dosage': 'As prescribed based on levels',
                'requires_prescription': True,
                'ckd_relevance': 'Medium',
                'price_range': '₹100-400',
                'is_active': True,
                'created_at': datetime.utcnow()
            },
            {
                'name': 'Omega-3 Fatty Acids',
                'category': 'supplements',
                'category_name': 'Nutritional Supplements',
                'purpose': 'Heart health, reduce triglycerides',
                'notes': 'Pharmaceutical grade recommended',
                'common_dosage': '1-4g daily (consult doctor)',
                'requires_prescription': False,
                'ckd_relevance': 'Low',
                'price_range': '₹200-800',
                'is_active': True,
                'created_at': datetime.utcnow()
            },
            {
                'name': 'B-Complex Vitamins',
                'category': 'supplements',
                'category_name': 'Nutritional Supplements',
                'purpose': 'Support for dialysis patients',
                'notes': 'Water-soluble vitamins lost in dialysis',
                'common_dosage': 'As recommended',
                'requires_prescription': False,
                'ckd_relevance': 'Low',
                'price_range': '₹50-200',
                'is_active': True,
                'created_at': datetime.utcnow()
            },
            # Potassium Management
            {
                'name': 'Sodium Polystyrene Sulfonate (Kayexalate)',
                'category': 'potassium_management',
                'category_name': 'Electrolyte Management',
                'purpose': 'Lower high potassium levels',
                'notes': 'For hyperkalemia',
                'common_dosage': 'As prescribed for acute management',
                'requires_prescription': True,
                'ckd_relevance': 'High',
                'price_range': '₹300-800',
                'is_active': True,
                'created_at': datetime.utcnow()
            },
            {
                'name': 'Patiromer (Veltassa)',
                'category': 'potassium_management',
                'category_name': 'Electrolyte Management',
                'purpose': 'Long-term potassium management',
                'notes': 'Newer potassium binder',
                'common_dosage': 'Daily, as prescribed',
                'requires_prescription': True,
                'ckd_relevance': 'High',
                'price_range': '₹1500-4000',
                'is_active': True,
                'created_at': datetime.utcnow()
            }
        ]
        db.medicines.insert_many(default_medicines)
        print("Initialized default medicines")

    # Default Pharmacies
    if db.pharmacies.count_documents({}) == 0:
        default_pharmacies = [
            {
                'name': 'MedPlus Pharmacy',
                'type': 'Chain Store',
                'address': '123 Main Street, City Center',
                'city': 'Mumbai',
                'distance': '0.5 km',
                'availability': 'Most CKD medications available',
                'hours': '8 AM - 10 PM',
                'contact': '+91 1800-123-4567',
                'email': 'medplus@example.com',
                'delivers': True,
                'rating': 4.5,
                'is_active': True,
                'latitude': 19.0760,
                'longitude': 72.8777,
                'created_at': datetime.utcnow()
            },
            {
                'name': 'Apollo Pharmacy',
                'type': 'Hospital Pharmacy',
                'address': '456 Hospital Road, Health District',
                'city': 'Mumbai',
                'distance': '1.2 km',
                'availability': 'Full CKD medication stock',
                'hours': '24 Hours',
                'contact': '+91 1800-234-5678',
                'email': 'apollo@example.com',
                'delivers': True,
                'rating': 4.8,
                'is_active': True,
                'latitude': 19.0800,
                'longitude': 72.8800,
                'created_at': datetime.utcnow()
            },
            {
                'name': 'Wellness Forever',
                'type': 'Retail Pharmacy',
                'address': '789 Shopping Complex, Mall Road',
                'city': 'Mumbai',
                'distance': '0.8 km',
                'availability': 'Common medications available',
                'hours': '9 AM - 9 PM',
                'contact': '+91 9876-543-210',
                'email': 'wellness@example.com',
                'delivers': True,
                'rating': 4.2,
                'is_active': True,
                'latitude': 19.0720,
                'longitude': 72.8750,
                'created_at': datetime.utcnow()
            }
        ]
        db.pharmacies.insert_many(default_pharmacies)
        print("Initialized default pharmacies")


# ==================== ADMIN ROUTES - PHARMACY MANAGEMENT ====================

@pharmacy_bp.route('/admin/pharmacies', methods=['GET'])
@jwt_required()
def admin_get_all_pharmacies():
    """Admin: Get all pharmacies with pagination"""
    try:
        db = get_db()
        init_default_data(db)
        current_user = get_current_user()
        
        # Check admin role
        user = db.users.find_one({'_id': ObjectId(current_user['id'])})
        if not user or user.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        skip = (page - 1) * limit
        
        pharmacies = list(db.pharmacies.find().sort('created_at', -1).skip(skip).limit(limit))
        total = db.pharmacies.count_documents({})
        
        for pharmacy in pharmacies:
            pharmacy['_id'] = str(pharmacy['_id'])
            if pharmacy.get('created_at'):
                pharmacy['created_at'] = pharmacy['created_at'].isoformat()
        
        return jsonify({
            'success': True,
            'pharmacies': pharmacies,
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@pharmacy_bp.route('/admin/pharmacy', methods=['POST'])
@jwt_required()
def admin_add_pharmacy():
    """Admin: Add a new pharmacy with location and medicine list"""
    try:
        db = get_db()
        current_user = get_current_user()
        
        # Check admin role
        user = db.users.find_one({'_id': ObjectId(current_user['id'])})
        if not user or user.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'type', 'address', 'contact', 'hours']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field} is required'}), 400
        
        # Process available medicines list
        available_medicines = []
        if data.get('available_medicines'):
            for med in data['available_medicines']:
                available_medicines.append({
                    'medicine_id': med.get('medicine_id'),
                    'name': med.get('name'),
                    'in_stock': med.get('in_stock', True),
                    'quantity': med.get('quantity', 0),
                    'price': med.get('price', 0)
                })
        
        pharmacy = {
            'name': data['name'],
            'type': data['type'],
            'address': data['address'],
            'city': data.get('city', ''),
            'state': data.get('state', ''),
            'pincode': data.get('pincode', ''),
            'distance': data.get('distance', 'N/A'),
            'availability': data.get('availability', 'Available'),
            'hours': data['hours'],
            'contact': data['contact'],
            'email': data.get('email', ''),
            'delivers': data.get('delivers', False),
            'rating': data.get('rating', 0),
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'available_medicines': available_medicines,
            'total_medicines': len(available_medicines),
            'is_active': True,
            'created_at': datetime.utcnow(),
            'created_by': current_user['id']
        }
        
        result = db.pharmacies.insert_one(pharmacy)
        pharmacy['_id'] = str(result.inserted_id)
        pharmacy['created_at'] = pharmacy['created_at'].isoformat()
        
        return jsonify({
            'success': True,
            'message': 'Pharmacy added successfully',
            'pharmacy': pharmacy
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@pharmacy_bp.route('/admin/pharmacy/<pharmacy_id>', methods=['PUT'])
@jwt_required()
def admin_update_pharmacy(pharmacy_id):
    """Admin: Update a pharmacy"""
    try:
        db = get_db()
        current_user = get_current_user()
        
        # Check admin role
        user = db.users.find_one({'_id': ObjectId(current_user['id'])})
        if not user or user.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        
        data = request.get_json()
        
        update_data = {k: v for k, v in data.items() if k not in ['_id', 'created_at', 'created_by']}
        update_data['updated_at'] = datetime.utcnow()
        update_data['updated_by'] = current_user['id']
        
        result = db.pharmacies.update_one(
            {'_id': ObjectId(pharmacy_id)},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'success': False, 'message': 'Pharmacy not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Pharmacy updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@pharmacy_bp.route('/admin/pharmacy/<pharmacy_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_pharmacy(pharmacy_id):
    """Admin: Delete (deactivate) a pharmacy"""
    try:
        db = get_db()
        current_user = get_current_user()
        
        # Check admin role
        user = db.users.find_one({'_id': ObjectId(current_user['id'])})
        if not user or user.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        
        result = db.pharmacies.update_one(
            {'_id': ObjectId(pharmacy_id)},
            {'$set': {'is_active': False, 'deleted_at': datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            return jsonify({'success': False, 'message': 'Pharmacy not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Pharmacy deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@pharmacy_bp.route('/admin/pharmacy/<pharmacy_id>/medicines', methods=['GET'])
@jwt_required()
def admin_get_pharmacy_medicines(pharmacy_id):
    """Admin: Get medicines available in a specific pharmacy"""
    try:
        db = get_db()
        current_user = get_current_user()
        
        user = db.users.find_one({'_id': ObjectId(current_user['id'])})
        if not user or user.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        
        pharmacy = db.pharmacies.find_one({'_id': ObjectId(pharmacy_id)})
        if not pharmacy:
            return jsonify({'success': False, 'message': 'Pharmacy not found'}), 404
        
        return jsonify({
            'success': True,
            'pharmacy_name': pharmacy.get('name'),
            'medicines': pharmacy.get('available_medicines', []),
            'total': len(pharmacy.get('available_medicines', []))
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@pharmacy_bp.route('/admin/pharmacy/<pharmacy_id>/medicines', methods=['POST'])
@jwt_required()
def admin_add_pharmacy_medicine(pharmacy_id):
    """Admin: Add a medicine to a pharmacy's inventory"""
    try:
        db = get_db()
        current_user = get_current_user()
        
        user = db.users.find_one({'_id': ObjectId(current_user['id'])})
        if not user or user.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'success': False, 'message': 'Medicine name is required'}), 400
        
        new_medicine = {
            'medicine_id': data.get('medicine_id', str(ObjectId())),
            'name': data['name'],
            'category': data.get('category', 'General'),
            'in_stock': data.get('in_stock', True),
            'quantity': data.get('quantity', 0),
            'price': data.get('price', 0),
            'unit': data.get('unit', 'per strip'),
            'added_at': datetime.utcnow().isoformat()
        }
        
        result = db.pharmacies.update_one(
            {'_id': ObjectId(pharmacy_id)},
            {
                '$push': {'available_medicines': new_medicine},
                '$inc': {'total_medicines': 1},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        
        if result.matched_count == 0:
            return jsonify({'success': False, 'message': 'Pharmacy not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Medicine added to pharmacy',
            'medicine': new_medicine
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@pharmacy_bp.route('/admin/pharmacy/<pharmacy_id>/medicines/<medicine_id>', methods=['DELETE'])
@jwt_required()
def admin_remove_pharmacy_medicine(pharmacy_id, medicine_id):
    """Admin: Remove a medicine from a pharmacy's inventory"""
    try:
        db = get_db()
        current_user = get_current_user()
        
        user = db.users.find_one({'_id': ObjectId(current_user['id'])})
        if not user or user.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        
        result = db.pharmacies.update_one(
            {'_id': ObjectId(pharmacy_id)},
            {
                '$pull': {'available_medicines': {'medicine_id': medicine_id}},
                '$inc': {'total_medicines': -1},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        
        if result.matched_count == 0:
            return jsonify({'success': False, 'message': 'Pharmacy not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Medicine removed from pharmacy'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@pharmacy_bp.route('/admin/pharmacy/<pharmacy_id>/medicines/bulk', methods=['POST'])
@jwt_required()
def admin_bulk_add_pharmacy_medicines(pharmacy_id):
    """Admin: Add multiple medicines to a pharmacy at once"""
    try:
        db = get_db()
        current_user = get_current_user()
        
        user = db.users.find_one({'_id': ObjectId(current_user['id'])})
        if not user or user.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        
        data = request.get_json()
        medicines = data.get('medicines', [])
        
        if not medicines:
            return jsonify({'success': False, 'message': 'No medicines provided'}), 400
        
        processed_medicines = []
        for med in medicines:
            processed_medicines.append({
                'medicine_id': med.get('medicine_id', str(ObjectId())),
                'name': med.get('name', 'Unknown'),
                'category': med.get('category', 'General'),
                'in_stock': med.get('in_stock', True),
                'quantity': med.get('quantity', 0),
                'price': med.get('price', 0),
                'unit': med.get('unit', 'per strip'),
                'added_at': datetime.utcnow().isoformat()
            })
        
        result = db.pharmacies.update_one(
            {'_id': ObjectId(pharmacy_id)},
            {
                '$push': {'available_medicines': {'$each': processed_medicines}},
                '$inc': {'total_medicines': len(processed_medicines)},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        
        if result.matched_count == 0:
            return jsonify({'success': False, 'message': 'Pharmacy not found'}), 404
        
        return jsonify({
            'success': True,
            'message': f'{len(processed_medicines)} medicines added to pharmacy',
            'added_count': len(processed_medicines)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== ADMIN ROUTES - MEDICINE MANAGEMENT ====================

@pharmacy_bp.route('/admin/medicines', methods=['GET'])
@jwt_required()
def admin_get_all_medicines():
    """Admin: Get all medicines with pagination"""
    try:
        db = get_db()
        init_default_data(db)
        current_user = get_current_user()
        
        # Check admin role
        user = db.users.find_one({'_id': ObjectId(current_user['id'])})
        if not user or user.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        skip = (page - 1) * limit
        category = request.args.get('category')
        
        query = {}
        if category:
            query['category'] = category
        
        medicines = list(db.medicines.find(query).sort('category', 1).skip(skip).limit(limit))
        total = db.medicines.count_documents(query)
        
        for medicine in medicines:
            medicine['_id'] = str(medicine['_id'])
            if medicine.get('created_at'):
                medicine['created_at'] = medicine['created_at'].isoformat()
        
        return jsonify({
            'success': True,
            'medicines': medicines,
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@pharmacy_bp.route('/admin/medicine', methods=['POST'])
@jwt_required()
def admin_add_medicine():
    """Admin: Add a new medicine"""
    try:
        db = get_db()
        current_user = get_current_user()
        
        # Check admin role
        user = db.users.find_one({'_id': ObjectId(current_user['id'])})
        if not user or user.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'category', 'purpose']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field} is required'}), 400
        
        medicine = {
            'name': data['name'],
            'category': data['category'],
            'category_name': data.get('category_name', data['category'].replace('_', ' ').title()),
            'purpose': data['purpose'],
            'notes': data.get('notes', ''),
            'common_dosage': data.get('common_dosage', 'As prescribed'),
            'requires_prescription': data.get('requires_prescription', True),
            'ckd_relevance': data.get('ckd_relevance', 'Medium'),
            'price_range': data.get('price_range', 'N/A'),
            'is_active': True,
            'created_at': datetime.utcnow(),
            'created_by': current_user['id']
        }
        
        result = db.medicines.insert_one(medicine)
        medicine['_id'] = str(result.inserted_id)
        medicine['created_at'] = medicine['created_at'].isoformat()
        
        return jsonify({
            'success': True,
            'message': 'Medicine added successfully',
            'medicine': medicine
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@pharmacy_bp.route('/admin/medicine/<medicine_id>', methods=['PUT'])
@jwt_required()
def admin_update_medicine(medicine_id):
    """Admin: Update a medicine"""
    try:
        db = get_db()
        current_user = get_current_user()
        
        # Check admin role
        user = db.users.find_one({'_id': ObjectId(current_user['id'])})
        if not user or user.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        
        data = request.get_json()
        
        update_data = {k: v for k, v in data.items() if k not in ['_id', 'created_at', 'created_by']}
        update_data['updated_at'] = datetime.utcnow()
        update_data['updated_by'] = current_user['id']
        
        result = db.medicines.update_one(
            {'_id': ObjectId(medicine_id)},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'success': False, 'message': 'Medicine not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Medicine updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@pharmacy_bp.route('/admin/medicine/<medicine_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_medicine(medicine_id):
    """Admin: Delete (deactivate) a medicine"""
    try:
        db = get_db()
        current_user = get_current_user()
        
        # Check admin role
        user = db.users.find_one({'_id': ObjectId(current_user['id'])})
        if not user or user.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        
        result = db.medicines.update_one(
            {'_id': ObjectId(medicine_id)},
            {'$set': {'is_active': False, 'deleted_at': datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            return jsonify({'success': False, 'message': 'Medicine not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'Medicine deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== PATIENT ROUTES - SEARCH & VIEW ====================

@pharmacy_bp.route('/search/medicines', methods=['GET'])
def search_medicines():
    """Search medicines by name, category, or purpose"""
    try:
        db = get_db()
        init_default_data(db)
        
        query_text = request.args.get('q', '')
        category = request.args.get('category')
        ckd_relevance = request.args.get('relevance')
        prescription_only = request.args.get('prescription')
        
        query = {'is_active': True}
        
        if query_text:
            # Create regex for case-insensitive search
            regex = re.compile(query_text, re.IGNORECASE)
            query['$or'] = [
                {'name': regex},
                {'purpose': regex},
                {'notes': regex},
                {'category_name': regex}
            ]
        
        if category:
            query['category'] = category
        
        if ckd_relevance:
            query['ckd_relevance'] = ckd_relevance
        
        if prescription_only == 'true':
            query['requires_prescription'] = True
        elif prescription_only == 'false':
            query['requires_prescription'] = False
        
        medicines = list(db.medicines.find(query).sort('ckd_relevance', 1).limit(50))
        
        for medicine in medicines:
            medicine['_id'] = str(medicine['_id'])
            if medicine.get('created_at'):
                medicine['created_at'] = medicine['created_at'].isoformat()
        
        return jsonify({
            'success': True,
            'medicines': medicines,
            'total': len(medicines),
            'query': query_text
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@pharmacy_bp.route('/search/pharmacies', methods=['GET'])
def search_pharmacies():
    """Search pharmacies by name, city, or type"""
    try:
        db = get_db()
        init_default_data(db)
        
        query_text = request.args.get('q', '')
        city = request.args.get('city')
        pharmacy_type = request.args.get('type')
        delivers = request.args.get('delivers')
        
        query = {'is_active': True}
        
        if query_text:
            regex = re.compile(query_text, re.IGNORECASE)
            query['$or'] = [
                {'name': regex},
                {'address': regex},
                {'city': regex}
            ]
        
        if city:
            query['city'] = re.compile(city, re.IGNORECASE)
        
        if pharmacy_type:
            query['type'] = pharmacy_type
        
        if delivers == 'true':
            query['delivers'] = True
        
        pharmacies = list(db.pharmacies.find(query).sort('rating', -1).limit(20))
        
        for pharmacy in pharmacies:
            pharmacy['_id'] = str(pharmacy['_id'])
            if pharmacy.get('created_at'):
                pharmacy['created_at'] = pharmacy['created_at'].isoformat()
        
        return jsonify({
            'success': True,
            'pharmacies': pharmacies,
            'total': len(pharmacies),
            'query': query_text
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@pharmacy_bp.route('/categories', methods=['GET'])
def get_medicine_categories():
    """Get all medicine categories"""
    categories = [
        {'id': 'blood_pressure', 'name': 'Antihypertensives', 'description': 'Blood pressure management'},
        {'id': 'diabetes_management', 'name': 'Antidiabetics', 'description': 'Diabetes control'},
        {'id': 'anemia_management', 'name': 'Anemia Treatment', 'description': 'Red blood cell support'},
        {'id': 'phosphate_binders', 'name': 'Mineral Management', 'description': 'Phosphorus control'},
        {'id': 'supplements', 'name': 'Nutritional Supplements', 'description': 'Vitamin and mineral support'},
        {'id': 'potassium_management', 'name': 'Electrolyte Management', 'description': 'Potassium level control'}
    ]
    return jsonify({'success': True, 'categories': categories})


# ==================== EXISTING ROUTES (UPDATED) ====================

def get_ckd_stage(risk_level, creatinine=None, gfr=None):
    """Estimate CKD stage based on risk level and markers"""
    if risk_level == 'High':
        return {'stage': 'Stage 4-5', 'description': 'Severe to End-Stage CKD'}
    elif risk_level == 'Medium':
        return {'stage': 'Stage 3', 'description': 'Moderate CKD'}
    else:
        return {'stage': 'Stage 1-2', 'description': 'Early CKD or At-Risk'}


def get_medication_recommendations(prediction_data, patient_conditions, db):
    """Generate personalized medication recommendations from database"""
    recommendations = []
    
    risk_level = prediction_data.get('risk_level', 'Unknown')
    input_data = prediction_data.get('input_data', {})
    
    # Get all active medicines from database
    all_medicines = list(db.medicines.find({'is_active': True}))
    
    # Group by category
    categories = {}
    for med in all_medicines:
        cat = med['category']
        if cat not in categories:
            categories[cat] = {
                'category': med.get('category_name', cat.replace('_', ' ').title()),
                'medications': [],
                'priority': 'Low',
                'reason': ''
            }
        categories[cat]['medications'].append({
            'name': med['name'],
            'purpose': med['purpose'],
            'notes': med.get('notes', ''),
            'common_dosage': med.get('common_dosage', 'As prescribed'),
            'requires_prescription': med.get('requires_prescription', True),
            'price_range': med.get('price_range', 'N/A')
        })
    
    # Check for hypertension
    if patient_conditions.get('htn') == 'yes' or input_data.get('htn') == 'yes':
        if 'blood_pressure' in categories:
            bp_meds = categories['blood_pressure'].copy()
            bp_meds['priority'] = 'High'
            bp_meds['reason'] = 'Hypertension detected - blood pressure control is crucial for kidney protection'
            recommendations.append(bp_meds)
    
    # Check for diabetes
    if patient_conditions.get('dm') == 'yes' or input_data.get('dm') == 'yes':
        if 'diabetes_management' in categories:
            dm_meds = categories['diabetes_management'].copy()
            dm_meds['priority'] = 'High'
            dm_meds['reason'] = 'Diabetes detected - glucose control helps protect kidneys'
            recommendations.append(dm_meds)
    
    # Check for anemia (low hemoglobin)
    hemo = input_data.get('hemo', 0)
    try:
        hemo = float(hemo)
        if hemo < 10 and 'anemia_management' in categories:
            anemia_meds = categories['anemia_management'].copy()
            anemia_meds['priority'] = 'Medium'
            anemia_meds['reason'] = f'Low hemoglobin ({hemo} g/dL) detected - anemia management may be needed'
            recommendations.append(anemia_meds)
    except:
        pass
    
    # High risk recommendations
    if risk_level in ['High', 'Medium']:
        if 'phosphate_binders' in categories:
            phosphate_meds = categories['phosphate_binders'].copy()
            phosphate_meds['priority'] = 'Medium' if risk_level == 'High' else 'Low'
            phosphate_meds['reason'] = 'May be needed to manage phosphorus levels'
            recommendations.append(phosphate_meds)
        
        if 'supplements' in categories:
            supps = categories['supplements'].copy()
            supps['priority'] = 'Low'
            supps['reason'] = 'Nutritional support for CKD patients'
            recommendations.append(supps)
    
    # Check for high potassium risk
    pot = input_data.get('pot', 0)
    try:
        pot = float(pot)
        if pot > 5.5 and 'potassium_management' in categories:
            k_meds = categories['potassium_management'].copy()
            k_meds['priority'] = 'High'
            k_meds['reason'] = f'Elevated potassium ({pot} mEq/L) - may need management'
            recommendations.append(k_meds)
    except:
        pass
    
    return recommendations


@pharmacy_bp.route('/recommend', methods=['POST'])
@jwt_required()
def get_pharmacy_recommendations():
    """Get personalized medication recommendations based on CKD prediction"""
    try:
        db = get_db()
        init_default_data(db)
        current_user = get_jwt_identity()
        data = request.get_json()
        
        prediction_data = data.get('prediction', {})
        patient_conditions = data.get('conditions', {})
        
        # Get CKD stage estimate
        ckd_stage = get_ckd_stage(
            prediction_data.get('risk_level', 'Unknown'),
            data.get('input_data', {}).get('sc')
        )
        
        # Get medication recommendations from database
        medications = get_medication_recommendations(prediction_data, patient_conditions, db)
        
        # Sort by priority
        priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
        medications.sort(key=lambda x: priority_order.get(x.get('priority', 'Low'), 2))
        
        # Get active pharmacies from database
        pharmacies = list(db.pharmacies.find({'is_active': True}).limit(5))
        for p in pharmacies:
            p['_id'] = str(p['_id'])
        
        response = {
            'ckd_stage': ckd_stage,
            'medication_categories': medications,
            'pharmacies': pharmacies,
            'warnings': [
                'All medications require a doctor\'s prescription and supervision',
                'Dosages must be adjusted for kidney function',
                'Never start or change medications without consulting your nephrologist',
                'This is informational only - not a prescription'
            ],
            'generated_at': datetime.utcnow().isoformat()
        }
        
        # Log recommendation
        log_entry = {
            'user_id': current_user,
            'prediction_data': prediction_data,
            'recommendations_count': len(medications),
            'timestamp': datetime.utcnow()
        }
        db.pharmacy_logs.insert_one(log_entry)
        
        return jsonify({
            'success': True,
            'recommendations': response
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@pharmacy_bp.route('/medications', methods=['GET'])
def get_all_medications():
    """Get all CKD medication categories from database"""
    try:
        db = get_db()
        init_default_data(db)
        
        # Get all active medicines grouped by category
        medicines = list(db.medicines.find({'is_active': True}))
        
        # Group by category
        categories = {}
        for med in medicines:
            cat = med['category']
            if cat not in categories:
                categories[cat] = {
                    'category': med.get('category_name', cat.replace('_', ' ').title()),
                    'medications': []
                }
            categories[cat]['medications'].append({
                'name': med['name'],
                'purpose': med['purpose'],
                'notes': med.get('notes', ''),
                'common_dosage': med.get('common_dosage', 'As prescribed'),
                'requires_prescription': med.get('requires_prescription', True),
                'price_range': med.get('price_range', 'N/A')
            })
        
        return jsonify({
            'success': True,
            'medications': categories,
            'disclaimer': 'This information is for educational purposes only. Always consult a healthcare provider.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@pharmacy_bp.route('/pharmacies', methods=['GET'])
def get_nearby_pharmacies():
    """Get list of nearby pharmacies from database"""
    try:
        db = get_db()
        init_default_data(db)
        
        pharmacies = list(db.pharmacies.find({'is_active': True}).sort('rating', -1).limit(10))
        
        for pharmacy in pharmacies:
            pharmacy['_id'] = str(pharmacy['_id'])
            if pharmacy.get('created_at'):
                pharmacy['created_at'] = pharmacy['created_at'].isoformat()
        
        return jsonify({
            'success': True,
            'pharmacies': pharmacies,
            'note': 'Pharmacies are sorted by rating. Use search for more specific results.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@pharmacy_bp.route('/check-availability', methods=['POST'])
@jwt_required()
def check_medication_availability():
    """Check if specific medications are available at pharmacies"""
    try:
        db = get_db()
        init_default_data(db)
        data = request.get_json()
        medications = data.get('medications', [])
        
        pharmacies = list(db.pharmacies.find({'is_active': True}).limit(5))
        
        # Simulated availability check (in production, integrate with pharmacy inventory API)
        availability = []
        for med in medications:
            pharmacy_avail = []
            for p in pharmacies:
                # Simulate availability based on pharmacy type
                is_available = p.get('type') in ['Hospital Pharmacy', 'Chain Store']
                pharmacy_avail.append({
                    'name': p['name'],
                    'available': is_available,
                    'stock': 'In Stock' if is_available else 'Limited Stock',
                    'contact': p.get('contact', '')
                })
            availability.append({
                'medication': med,
                'pharmacies': pharmacy_avail
            })
        
        return jsonify({
            'success': True,
            'availability': availability,
            'checked_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@pharmacy_bp.route('/drug-interactions', methods=['POST'])
@jwt_required()
def check_drug_interactions():
    """Check for potential drug interactions (basic implementation)"""
    try:
        data = request.get_json()
        medications = data.get('medications', [])
        
        # Known CKD-relevant interactions (simplified)
        known_interactions = [
            {
                'drugs': ['ACE Inhibitors', 'Potassium Supplements'],
                'severity': 'High',
                'warning': 'May cause dangerous increase in potassium levels'
            },
            {
                'drugs': ['ACE Inhibitors', 'ARBs'],
                'severity': 'Medium',
                'warning': 'Dual RAAS blockade - increased risk of kidney problems'
            },
            {
                'drugs': ['NSAIDs', 'ACE Inhibitors'],
                'severity': 'High',
                'warning': 'NSAIDs can reduce effectiveness and harm kidneys'
            },
            {
                'drugs': ['Metformin', 'Contrast Dye'],
                'severity': 'High',
                'warning': 'Risk of lactic acidosis - hold metformin before contrast'
            }
        ]
        
        found_interactions = []
        for interaction in known_interactions:
            drug_set = set([d.lower() for d in interaction['drugs']])
            med_set = set([m.lower() for m in medications])
            if drug_set.issubset(med_set):
                found_interactions.append(interaction)
        
        return jsonify({
            'success': True,
            'medications_checked': medications,
            'interactions_found': len(found_interactions),
            'interactions': found_interactions,
            'disclaimer': 'This is a basic check. Always consult pharmacist for complete interaction analysis.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@pharmacy_bp.route('/history', methods=['GET'])
@jwt_required()
def get_pharmacy_history():
    """Get user's pharmacy recommendation history"""
    try:
        db = get_db()
        current_user = get_jwt_identity()
        
        logs = list(db.pharmacy_logs.find(
            {'user_id': current_user}
        ).sort('timestamp', -1).limit(10))
        
        for log in logs:
            log['_id'] = str(log['_id'])
            if log.get('timestamp'):
                log['timestamp'] = log['timestamp'].isoformat()
        
        return jsonify({
            'success': True,
            'history': logs
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
