# CKD (Chronic Kidney Disease) Routes with Explainable AI
# Handles CKD prediction, XAI explanations, risk assessment

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import pickle
import os
import sys
import json
import numpy as np
import shap

# Add parent directory to path
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
ckd_bp = Blueprint('ckd', __name__)

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# ML Model paths
ML_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml')
CKD_MODEL_PATH = os.path.join(ML_DIR, 'ckd_best_model.pkl')
CKD_SCALER_PATH = os.path.join(ML_DIR, 'ckd_scaler.pkl')
CKD_TARGET_ENCODER_PATH = os.path.join(ML_DIR, 'ckd_target_encoder.pkl')
CKD_LABEL_ENCODERS_PATH = os.path.join(ML_DIR, 'ckd_label_encoders.pkl')
CKD_FEATURE_NAMES_PATH = os.path.join(ML_DIR, 'ckd_feature_names.pkl')
CKD_METADATA_PATH = os.path.join(ML_DIR, 'ckd_model_metadata.pkl')
CKD_SHAP_PATH = os.path.join(ML_DIR, 'ckd_shap_explainer.pkl')

# Load models on import
ckd_model = None
ckd_scaler = None
ckd_target_encoder = None
ckd_label_encoders = None
ckd_feature_names = None
ckd_metadata = None
shap_explainer = None

def load_ckd_models():
    """Load CKD prediction models and preprocessors"""
    global ckd_model, ckd_scaler, ckd_target_encoder, ckd_label_encoders
    global ckd_feature_names, ckd_metadata, shap_explainer
    
    try:
        if os.path.exists(CKD_MODEL_PATH):
            with open(CKD_MODEL_PATH, 'rb') as f:
                ckd_model = pickle.load(f)
        
        if os.path.exists(CKD_SCALER_PATH):
            with open(CKD_SCALER_PATH, 'rb') as f:
                ckd_scaler = pickle.load(f)
        
        if os.path.exists(CKD_TARGET_ENCODER_PATH):
            with open(CKD_TARGET_ENCODER_PATH, 'rb') as f:
                ckd_target_encoder = pickle.load(f)
        
        if os.path.exists(CKD_LABEL_ENCODERS_PATH):
            with open(CKD_LABEL_ENCODERS_PATH, 'rb') as f:
                ckd_label_encoders = pickle.load(f)
        
        if os.path.exists(CKD_FEATURE_NAMES_PATH):
            with open(CKD_FEATURE_NAMES_PATH, 'rb') as f:
                ckd_feature_names = pickle.load(f)
        
        if os.path.exists(CKD_METADATA_PATH):
            with open(CKD_METADATA_PATH, 'rb') as f:
                ckd_metadata = pickle.load(f)
        
        if os.path.exists(CKD_SHAP_PATH):
            with open(CKD_SHAP_PATH, 'rb') as f:
                shap_data = pickle.load(f)
                shap_explainer = shap_data.get('explainer')
        
        return True
    except Exception as e:
        print(f"Error loading CKD models: {e}")
        return False

# Load models on import
load_ckd_models()


@ckd_bp.route('/predict', methods=['POST'])
@jwt_required()
def predict_ckd():
    """
    Predict CKD based on medical test results
    Expected JSON: { age, bp, sg, al, su, rbc, pc, pcc, ba, bgr, bu, sc, sod, pot, hemo, pcv, wc, rc, htn, dm, cad, appet, pe, ane }
    """
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        # Reload models if not loaded
        if ckd_model is None or ckd_scaler is None:
            load_ckd_models()
        
        if ckd_model is None or ckd_scaler is None:
            return jsonify({
                "success": False,
                "message": "CKD prediction model not available. Please ensure the model is trained."
            }), 500
        
        # Feature order (must match training data)
        feature_order = ['age', 'bp', 'sg', 'al', 'su', 'bgr', 'bu', 'sc', 
                        'sod', 'pot', 'hemo', 'pcv', 'wc', 'rc',
                        'rbc', 'pc', 'pcc', 'ba', 'htn', 'dm', 'cad', 
                        'appet', 'pe', 'ane']
        
        # Extract and validate features
        features = []
        missing_fields = []
        
        for feature in feature_order:
            if feature not in data or data[feature] is None or data[feature] == '':
                missing_fields.append(feature)
                # Use default value (0 for numerical, 0 for categorical encoded)
                features.append(0)
            else:
                value = data[feature]
                # Encode categorical features if needed
                if feature in ['rbc', 'pc', 'pcc', 'ba', 'htn', 'dm', 'cad', 'appet', 'pe', 'ane']:
                    if ckd_label_encoders and feature in ckd_label_encoders:
                        try:
                            # Convert to string and lowercase for encoding
                            value = str(value).strip().lower()
                            value = ckd_label_encoders[feature].transform([value])[0]
                        except:
                            value = 0  # Default if encoding fails
                features.append(float(value))
        
        # Prepare input
        X_input = np.array([features])
        X_input_scaled = ckd_scaler.transform(X_input)
        
        # Predict
        prediction = ckd_model.predict(X_input_scaled)
        prediction_proba = ckd_model.predict_proba(X_input_scaled)
        
        # Get predicted class
        predicted_class = ckd_target_encoder.inverse_transform(prediction)[0]
        confidence_score = float(max(prediction_proba[0])) * 100
        
        # Determine risk level
        ckd_probability = prediction_proba[0][1] if predicted_class == 'ckd' else prediction_proba[0][0]
        if predicted_class == 'notckd':
            ckd_probability = 1 - ckd_probability
        
        risk_level = "Low"
        if ckd_probability > 0.7:
            risk_level = "High"
        elif ckd_probability > 0.4:
            risk_level = "Medium"
        
        # Get probabilities for both classes
        probabilities = {}
        for i, class_name in enumerate(ckd_target_encoder.classes_):
            probabilities[class_name] = round(float(prediction_proba[0][i]) * 100, 2)
        
        # Log the prediction
        prediction_log = {
            'patient_id': current_user['id'],
            'prediction': predicted_class,
            'confidence': confidence_score,
            'risk_level': risk_level,
            'probabilities': probabilities,
            'input_features': data,
            'missing_fields': missing_fields,
            'created_at': datetime.utcnow()
        }
        db.ckd_predictions.insert_one(prediction_log)
        
        return jsonify({
            "success": True,
            "prediction": {
                "result": predicted_class,
                "confidence": round(confidence_score, 2),
                "risk_level": risk_level,
                "probabilities": probabilities,
                "ckd_probability": round(float(ckd_probability) * 100, 2)
            },
            "warning": "This is a preliminary prediction. Please consult a doctor for proper diagnosis." if missing_fields else None,
            "missing_fields": missing_fields if missing_fields else None
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"CKD prediction failed: {str(e)}"
        }), 500


@ckd_bp.route('/explain', methods=['POST'])
@jwt_required()
def explain_prediction():
    """
    Generate XAI explanation for a CKD prediction using SHAP
    Expected JSON: Same as /predict endpoint
    """
    try:
        current_user = get_current_user()
        data = request.get_json()
        
        # Reload models if not loaded
        if ckd_model is None or ckd_scaler is None:
            load_ckd_models()
        
        if ckd_model is None:
            return jsonify({
                "success": False,
                "message": "CKD model not available"
            }), 500
        
        # Feature order
        feature_order = ['age', 'bp', 'sg', 'al', 'su', 'bgr', 'bu', 'sc', 
                        'sod', 'pot', 'hemo', 'pcv', 'wc', 'rc',
                        'rbc', 'pc', 'pcc', 'ba', 'htn', 'dm', 'cad', 
                        'appet', 'pe', 'ane']
        
        # Extract features (same as predict)
        features = []
        for feature in feature_order:
            value = data.get(feature, 0)
            if feature in ['rbc', 'pc', 'pcc', 'ba', 'htn', 'dm', 'cad', 'appet', 'pe', 'ane']:
                if ckd_label_encoders and feature in ckd_label_encoders:
                    try:
                        value = str(value).strip().lower()
                        value = ckd_label_encoders[feature].transform([value])[0]
                    except:
                        value = 0
            features.append(float(value))
        
        X_input = np.array([features])
        X_input_scaled = ckd_scaler.transform(X_input)
        
        # Get prediction first
        prediction = ckd_model.predict(X_input_scaled)
        prediction_proba = ckd_model.predict_proba(X_input_scaled)
        predicted_class = ckd_target_encoder.inverse_transform(prediction)[0]
        
        # Generate SHAP explanation
        explanation = {
            "prediction": predicted_class,
            "confidence": round(float(max(prediction_proba[0])) * 100, 2)
        }
        
        # Try to use SHAP explainer
        if shap_explainer is not None:
            try:
                shap_values = shap_explainer.shap_values(X_input_scaled)
                
                # Get SHAP values for the predicted class
                if isinstance(shap_values, list):
                    # Multi-class: get values for CKD class (index 0 or 1)
                    ckd_idx = list(ckd_target_encoder.classes_).index('ckd')
                    shap_vals = shap_values[ckd_idx][0]
                else:
                    shap_vals = shap_values[0]
                
                # Create feature importance list
                feature_importance = []
                for i, feature_name in enumerate(feature_order):
                    feature_importance.append({
                        "feature": feature_name,
                        "value": round(float(features[i]), 2),
                        "impact": round(float(shap_vals[i]), 4),
                        "direction": "increases" if shap_vals[i] > 0 else "decreases"
                    })
                
                # Sort by absolute impact
                feature_importance.sort(key=lambda x: abs(x['impact']), reverse=True)
                
                explanation["feature_importance"] = feature_importance[:10]  # Top 10
                explanation["explanation_available"] = True
                
                # Generate text explanation
                top_3 = feature_importance[:3]
                text_explanation = f"The prediction of '{predicted_class}' is primarily influenced by: "
                factors = []
                for feat in top_3:
                    factors.append(f"{feat['feature']} ({feat['value']}) which {feat['direction']} CKD risk")
                text_explanation += ", ".join(factors) + "."
                
                explanation["text_explanation"] = text_explanation
                
            except Exception as e:
                print(f"SHAP explanation error: {e}")
                explanation["explanation_available"] = False
                explanation["fallback_explanation"] = "Detailed feature-level explanation unavailable"
        else:
            # Fallback: use feature values to generate basic explanation
            high_risk_features = []
            
            # Check key CKD markers
            if data.get('sc', 0) > 1.5:
                high_risk_features.append(f"High serum creatinine ({data.get('sc')})")
            if data.get('bu', 0) > 50:
                high_risk_features.append(f"High blood urea ({data.get('bu')})")
            if data.get('hemo', 0) < 10:
                high_risk_features.append(f"Low hemoglobin ({data.get('hemo')})")
            if data.get('htn', '').lower() == 'yes':
                high_risk_features.append("Presence of hypertension")
            if data.get('dm', '').lower() == 'yes':
                high_risk_features.append("Presence of diabetes")
            
            explanation["explanation_available"] = False
            explanation["key_risk_factors"] = high_risk_features
            explanation["text_explanation"] = " ".join(high_risk_features) if high_risk_features else "No major risk factors identified"
        
        # Save explanation log
        explanation_log = {
            'patient_id': current_user['id'],
            'prediction': predicted_class,
            'explanation': explanation,
            'created_at': datetime.utcnow()
        }
        db.xai_explanations.insert_one(explanation_log)
        
        return jsonify({
            "success": True,
            "explanation": explanation
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Explanation generation failed: {str(e)}"
        }), 500


@ckd_bp.route('/history', methods=['GET'])
@jwt_required()
def get_ckd_history():
    """Get CKD prediction history for the current user"""
    try:
        current_user = get_current_user()
        
        predictions = list(db.ckd_predictions.find({
            'patient_id': current_user['id']
        }).sort('created_at', -1).limit(20))
        
        for pred in predictions:
            pred['_id'] = str(pred['_id'])
            if 'created_at' in pred:
                pred['created_at'] = pred['created_at'].isoformat()
        
        return jsonify({
            "success": True,
            "history": predictions
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to fetch history: {str(e)}"
        }), 500


@ckd_bp.route('/model-info', methods=['GET'])
def get_model_info():
    """Get information about the CKD prediction model"""
    try:
        if ckd_metadata is None:
            load_ckd_models()
        
        if ckd_metadata:
            return jsonify({
                "success": True,
                "model_info": {
                    "model_type": ckd_metadata.get('best_model_name', 'Unknown'),
                    "accuracy": round(ckd_metadata.get('metrics', {}).get('best_accuracy', 0) * 100, 2),
                    "features_count": len(ckd_metadata.get('feature_names', [])),
                    "target_classes": ckd_metadata.get('target_classes', []),
                    "xai_enabled": ckd_metadata.get('shap_available', False)
                }
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Model metadata not available"
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Failed to fetch model info: {str(e)}"
        }), 500
