"""
Chronic Kidney Disease Prediction System - Main Flask Application
Hybrid Explainable AI with SHAP, PDF Reports, Telemedicine & Recommendations
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from datetime import datetime
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import (MONGO_URI, DATABASE_NAME, JWT_SECRET_KEY, 
                    JWT_ACCESS_TOKEN_EXPIRES, FLASK_DEBUG, FLASK_HOST, FLASK_PORT)
from routes.auth import auth_bp
from routes.patient import patient_bp
from routes.doctor import doctor_bp
from routes.admin import admin_bp
# CKD System Routes
from routes.ckd import ckd_bp
from routes.recommendations import recommendations_bp
from routes.donor import donor_bp
from routes.telemedicine import telemedicine_bp
# Enhanced AI Routes
from routes.hybrid import hybrid_bp
from routes.xai_report import xai_report_bp
from routes.pharmacy import pharmacy_bp
from routes.gemini_recommendations import gemini_bp
from routes.report_upload import report_bp
# Translation Service
from routes.translation import translation_bp
# WebRTC Signaling
from routes.signaling import init_socketio

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = JWT_ACCESS_TOKEN_EXPIRES

# Initialize extensions
CORS(app, resources={r"/api/*": {"origins": "*"}, r"/socket.io/*": {"origins": "*"}})
jwt = JWTManager(app)

# Initialize Socket.IO for WebRTC signaling
socketio = init_socketio(app)

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(patient_bp, url_prefix='/api')
app.register_blueprint(doctor_bp, url_prefix='/api/doctor')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
# CKD System Blueprints
app.register_blueprint(ckd_bp, url_prefix='/api/ckd')
app.register_blueprint(recommendations_bp, url_prefix='/api/recommendations')
app.register_blueprint(donor_bp, url_prefix='/api/donor')
app.register_blueprint(telemedicine_bp, url_prefix='/api/telemedicine')
# Enhanced AI Blueprints
app.register_blueprint(hybrid_bp, url_prefix='/api/hybrid')
app.register_blueprint(xai_report_bp, url_prefix='/api/xai/report')
app.register_blueprint(pharmacy_bp, url_prefix='/api/pharmacy')
app.register_blueprint(gemini_bp, url_prefix='/api/gemini')
app.register_blueprint(report_bp, url_prefix='/api/report')
# Translation Service Blueprint
app.register_blueprint(translation_bp, url_prefix='/api/translate')

# JWT error handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"success": False, "message": "Token has expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"success": False, "message": "Invalid token"}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"success": False, "message": "Authorization required"}), 401

# JWT identity serialization - convert dict to JSON string
import json

@jwt.user_identity_loader
def user_identity_lookup(user):
    if isinstance(user, dict):
        return json.dumps(user)
    return user

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    try:
        return json.loads(identity)
    except:
        return identity

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        client.admin.command('ping')
        db_status = "connected"
    except:
        db_status = "disconnected"
    
    return jsonify({
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "message": "CKD Prediction System - Hybrid Explainable AI API",
        "version": "2.0.0",
        "endpoints": {
            "auth": "/api/register, /api/login",
            "hybrid_ai": "/api/hybrid/predict, /api/hybrid/compare",
            "xai_report": "/api/xai/report/pdf/:id",
            "recommendations": "/api/recommendations/lifestyle",
            "pharmacy": "/api/pharmacy/recommend",
            "donor": "/api/donor/match, /api/donor/register",
            "telemedicine": "/api/telemedicine/create-session",
            "translation": "/api/translate/translate, /api/translate/languages"
        }
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "message": "Resource not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"success": False, "message": "Internal server error"}), 500

def init_database():
    """Initialize database with collections and default admin"""
    from models.user import Admin
    from config import ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_NAME
    
    # All collections including admins and CKD system
    collections = [
        'users', 'patients', 'doctors', 'admins', 'appointments', 'symptoms_logs', 'admin_logs',
        # CKD System Collections
        'ckd_predictions', 'xai_explanations', 'lifestyle_recommendations', 
        'donors', 'donor_matches', 'telemedicine_sessions',
        # Enhanced AI Collections
        'hybrid_predictions', 'xai_reports', 'pharmacy_logs', 'recommendations',
        # Translation Cache
        'translations_cache'
    ]
    
    for coll in collections:
        if coll not in db.list_collection_names():
            db.create_collection(coll)
            print(f"Created collection: {coll}")
    
    # Create default admin if not exists (credentials from .env)
    if not db.users.find_one({"email": ADMIN_EMAIL}):
        admin = Admin(
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD,
            name=ADMIN_NAME,
            phone="1234567890"
        )
        admin_data = admin.to_dict()
        # Insert into users collection
        result = db.users.insert_one(admin_data)
        # Also insert into admins collection with user_id reference
        admin_data['user_id'] = result.inserted_id
        admin_data.pop('_id', None)
        db.admins.insert_one(admin_data)
        print(f"Default admin created: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")

if __name__ == '__main__':
    print("="*60)
    print("CKD Prediction System - Explainable AI Backend Server")
    print("="*60)
    
    # Initialize database
    init_database()
    
    print(f"\nServer running at: http://{FLASK_HOST}:{FLASK_PORT}")
    print(f"MongoDB: {MONGO_URI}")
    print("WebRTC Signaling: Socket.IO enabled")
    print("="*60)
    
    # Use socketio.run instead of app.run for WebSocket support
    socketio.run(app, host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
