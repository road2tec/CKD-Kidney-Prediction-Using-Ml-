"""
Hybrid Explainable AI Routes for CKD Prediction
Implements: Weighted ensemble prediction with comprehensive SHAP explanations
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
import os
from bson import ObjectId

hybrid_bp = Blueprint('hybrid', __name__)

# Load models and artifacts
ML_DIR = os.path.join(os.path.dirname(__file__), '..', 'ml')

# Initialize models
dt_model = None
rf_model = None
lr_model = None
hybrid_config = None
scaler = None
target_encoder = None
label_encoders = None
feature_names = None
shap_explainers = None

def load_hybrid_models():
    """Load all hybrid model components"""
    global dt_model, rf_model, lr_model, hybrid_config, scaler
    global target_encoder, label_encoders, feature_names, shap_explainers
    
    try:
        dt_model = pickle.load(open(os.path.join(ML_DIR, 'ckd_decision_tree.pkl'), 'rb'))
        rf_model = pickle.load(open(os.path.join(ML_DIR, 'ckd_random_forest.pkl'), 'rb'))
        lr_model = pickle.load(open(os.path.join(ML_DIR, 'ckd_logistic_regression.pkl'), 'rb'))
        hybrid_config = pickle.load(open(os.path.join(ML_DIR, 'ckd_hybrid_config.pkl'), 'rb'))
        scaler = pickle.load(open(os.path.join(ML_DIR, 'ckd_scaler.pkl'), 'rb'))
        target_encoder = pickle.load(open(os.path.join(ML_DIR, 'ckd_target_encoder.pkl'), 'rb'))
        label_encoders = pickle.load(open(os.path.join(ML_DIR, 'ckd_label_encoders.pkl'), 'rb'))
        feature_names = pickle.load(open(os.path.join(ML_DIR, 'ckd_feature_names.pkl'), 'rb'))
        
        try:
            shap_explainers = pickle.load(open(os.path.join(ML_DIR, 'ckd_shap_explainers.pkl'), 'rb'))
        except:
            shap_explainers = None
            
        print("✓ Hybrid models loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Error loading hybrid models: {e}")
        return False

# Load models on module import
load_hybrid_models()

def preprocess_input(data):
    """Preprocess patient input for prediction"""
    numerical_features = ['age', 'bp', 'sg', 'al', 'su', 'bgr', 'bu', 'sc', 'sod', 'pot', 'hemo', 'pcv', 'wc', 'rc']
    categorical_features = ['rbc', 'pc', 'pcc', 'ba', 'htn', 'dm', 'cad', 'appet', 'pe', 'ane']
    
    processed = {}
    
    # Process numerical features
    for feat in numerical_features:
        val = data.get(feat, 0)
        try:
            processed[feat] = float(val) if val != '' else 0
        except:
            processed[feat] = 0
    
    # Process categorical features
    for feat in categorical_features:
        val = str(data.get(feat, '')).lower().strip()
        if feat in label_encoders:
            try:
                processed[feat] = label_encoders[feat].transform([val])[0]
            except:
                processed[feat] = 0
        else:
            processed[feat] = 0
    
    # Create feature vector in correct order
    feature_vector = [processed.get(f, 0) for f in feature_names]
    return np.array(feature_vector).reshape(1, -1)

def get_risk_level(probability, prediction):
    """Determine risk level based on CKD probability"""
    if prediction == 1:  # CKD
        if probability >= 0.85:
            return "High"
        elif probability >= 0.65:
            return "Medium"
        else:
            return "Low"
    else:  # Not CKD
        if probability >= 0.85:
            return "Low"
        elif probability >= 0.65:
            return "Low"
        else:
            return "Medium"

def generate_shap_explanation(X_scaled, raw_data):
    """Generate comprehensive SHAP explanation"""
    explanation = {
        'explanation_available': False,
        'feature_importance': [],
        'text_explanation': '',
        'clinical_insights': [],
        'risk_factors': [],
        'protective_factors': []
    }
    
    if shap_explainers is None or 'random_forest' not in shap_explainers:
        return explanation
    
    try:
        import shap
        
        # Get SHAP values from Random Forest (most reliable for trees)
        rf_explainer = shap_explainers['random_forest']
        shap_values = rf_explainer.shap_values(X_scaled)
        
        # Handle different SHAP output formats
        if isinstance(shap_values, list):
            # For binary classification, use CKD class (index 1)
            shap_vals = shap_values[1][0]
        else:
            shap_vals = shap_values[0]
        
        # Create feature importance list
        feature_importance = []
        for idx, (feat, shap_val) in enumerate(zip(feature_names, shap_vals)):
            raw_value = raw_data.get(feat, X_scaled[0][idx])
            feature_importance.append({
                'feature': feat,
                'shap_value': float(shap_val),
                'raw_value': raw_value,
                'impact': abs(float(shap_val)),
                'direction': 'increases' if shap_val > 0 else 'decreases'
            })
        
        # Sort by absolute impact
        feature_importance.sort(key=lambda x: x['impact'], reverse=True)
        
        # Separate risk and protective factors
        risk_factors = [f for f in feature_importance if f['direction'] == 'increases'][:5]
        protective_factors = [f for f in feature_importance if f['direction'] == 'decreases'][:5]
        
        # Generate text explanation
        top_factors = feature_importance[:5]
        text_parts = []
        for f in top_factors:
            if f['direction'] == 'increases':
                text_parts.append(f"{f['feature']} = {f['raw_value']} (increases CKD risk)")
            else:
                text_parts.append(f"{f['feature']} = {f['raw_value']} (decreases CKD risk)")
        
        text_explanation = "The prediction is primarily influenced by: " + "; ".join(text_parts)
        
        # Generate clinical insights
        clinical_insights = []
        for f in feature_importance[:10]:
            insight = get_clinical_insight(f['feature'], f['raw_value'], f['direction'])
            if insight:
                clinical_insights.append(insight)
        
        explanation = {
            'explanation_available': True,
            'feature_importance': feature_importance[:10],
            'text_explanation': text_explanation,
            'clinical_insights': clinical_insights[:5],
            'risk_factors': risk_factors,
            'protective_factors': protective_factors
        }
        
    except Exception as e:
        explanation['error'] = str(e)
    
    return explanation

def get_clinical_insight(feature, value, direction):
    """Generate clinical insight for a feature"""
    insights = {
        'sc': {'high': 'Elevated serum creatinine indicates reduced kidney filtration', 'low': 'Normal creatinine suggests healthy kidney function'},
        'bu': {'high': 'High blood urea indicates impaired kidney waste removal', 'low': 'Normal urea levels suggest adequate kidney function'},
        'hemo': {'high': 'Good hemoglobin levels indicate healthy blood cell production', 'low': 'Low hemoglobin may indicate CKD-related anemia'},
        'bp': {'high': 'Elevated blood pressure can damage kidney blood vessels', 'low': 'Controlled blood pressure protects kidney health'},
        'al': {'high': 'Albumin in urine indicates kidney filter damage', 'low': 'No albumin suggests healthy kidney filters'},
        'sg': {'high': 'Normal specific gravity indicates good concentration ability', 'low': 'Low specific gravity may suggest dilute urine'},
        'htn': {'high': 'Hypertension is a major CKD risk factor', 'low': 'No hypertension reduces CKD risk'},
        'dm': {'high': 'Diabetes can damage kidney blood vessels over time', 'low': 'No diabetes reduces CKD risk'},
        'age': {'high': 'Older age increases CKD risk', 'low': 'Younger age is protective'},
        'bgr': {'high': 'High blood glucose can damage kidneys', 'low': 'Controlled glucose protects kidneys'}
    }
    
    if feature in insights:
        if direction == 'increases':
            return {'feature': feature, 'insight': insights[feature].get('high', ''), 'severity': 'warning'}
        else:
            return {'feature': feature, 'insight': insights[feature].get('low', ''), 'severity': 'positive'}
    return None


@hybrid_bp.route('/predict', methods=['POST'])
@jwt_required()
def hybrid_predict():
    """
    Hybrid ensemble CKD prediction with weighted voting
    """
    try:
        from app import db
        current_user = get_jwt_identity()
        data = request.get_json()
        
        if not all([dt_model, rf_model, lr_model, hybrid_config]):
            return jsonify({
                'success': False,
                'message': 'Hybrid models not loaded. Please train models first.'
            }), 500
        
        # Preprocess input
        X_raw = preprocess_input(data)
        X_scaled = scaler.transform(X_raw)
        
        # Get individual model predictions
        dt_proba = dt_model.predict_proba(X_scaled)[0]
        rf_proba = rf_model.predict_proba(X_scaled)[0]
        lr_proba = lr_model.predict_proba(X_scaled)[0]
        
        # Weighted ensemble
        weights = hybrid_config['weights']
        hybrid_proba = (
            weights['decision_tree'] * dt_proba +
            weights['random_forest'] * rf_proba +
            weights['logistic_regression'] * lr_proba
        )
        
        # Final prediction
        prediction = int(np.argmax(hybrid_proba))
        confidence = float(np.max(hybrid_proba) * 100)
        
        # Get risk level
        risk_level = get_risk_level(np.max(hybrid_proba), prediction)
        
        # Result mapping
        result = 'ckd' if prediction == 1 else 'notckd'
        
        # Individual model details
        model_details = {
            'decision_tree': {
                'prediction': 'ckd' if np.argmax(dt_proba) == 1 else 'notckd',
                'confidence': float(np.max(dt_proba) * 100),
                'weight': weights['decision_tree'] * 100
            },
            'random_forest': {
                'prediction': 'ckd' if np.argmax(rf_proba) == 1 else 'notckd',
                'confidence': float(np.max(rf_proba) * 100),
                'weight': weights['random_forest'] * 100
            },
            'logistic_regression': {
                'prediction': 'ckd' if np.argmax(lr_proba) == 1 else 'notckd',
                'confidence': float(np.max(lr_proba) * 100),
                'weight': weights['logistic_regression'] * 100
            }
        }
        
        # Generate SHAP explanation
        xai_explanation = generate_shap_explanation(X_scaled, data)
        
        # Prepare prediction record
        prediction_record = {
            'user_id': current_user,
            'input_data': data,
            'prediction': {
                'result': result,
                'confidence': confidence,
                'risk_level': risk_level,
                'probabilities': {
                    'ckd': float(hybrid_proba[1]) * 100 if len(hybrid_proba) > 1 else float(hybrid_proba[0]) * 100,
                    'notckd': float(hybrid_proba[0]) * 100
                }
            },
            'model_details': model_details,
            'xai_explanation': xai_explanation,
            'model_type': 'hybrid_ensemble',
            'timestamp': datetime.utcnow()
        }
        
        # Save to MongoDB
        result_id = db.hybrid_predictions.insert_one(prediction_record).inserted_id
        
        return jsonify({
            'success': True,
            'prediction': prediction_record['prediction'],
            'model_details': model_details,
            'xai_explanation': xai_explanation,
            'prediction_id': str(result_id),
            'model_type': 'Hybrid Ensemble (DT + RF + LR)'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@hybrid_bp.route('/explain/<prediction_id>', methods=['GET'])
@jwt_required()
def get_explanation(prediction_id):
    """Get detailed XAI explanation for a prediction"""
    try:
        from app import db
        
        prediction = db.hybrid_predictions.find_one({'_id': ObjectId(prediction_id)})
        
        if not prediction:
            return jsonify({
                'success': False,
                'message': 'Prediction not found'
            }), 404
        
        return jsonify({
            'success': True,
            'prediction': prediction['prediction'],
            'xai_explanation': prediction.get('xai_explanation', {}),
            'model_details': prediction.get('model_details', {}),
            'timestamp': prediction['timestamp'].isoformat() if prediction.get('timestamp') else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@hybrid_bp.route('/history', methods=['GET'])
@jwt_required()
def get_prediction_history():
    """Get user's prediction history"""
    try:
        from app import db
        import re
        current_user = get_jwt_identity()
        
        # Get email from identity (works with both dict and string formats)
        if isinstance(current_user, dict):
            user_email = current_user.get('email', '')
        else:
            user_email = current_user
        
        # Query by multiple formats:
        # 1. Exact match with current identity
        # 2. Regex match for email in JSON string
        # 3. Direct email string
        predictions = list(db.hybrid_predictions.find({
            '$or': [
                {'user_id': current_user},
                {'user_id': {'$regex': f'"email":\\s*"{re.escape(user_email)}"'}},
                {'user_id': user_email}
            ]
        }).sort('timestamp', -1).limit(20))
        
        for pred in predictions:
            pred['_id'] = str(pred['_id'])
            if pred.get('timestamp'):
                pred['timestamp'] = pred['timestamp'].isoformat()
        
        return jsonify({
            'success': True,
            'predictions': predictions,
            'count': len(predictions)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@hybrid_bp.route('/model-info', methods=['GET'])
def get_model_info():
    """Get hybrid model information and metrics"""
    if not hybrid_config:
        return jsonify({
            'success': False,
            'message': 'Hybrid model not loaded'
        }), 500
    
    return jsonify({
        'success': True,
        'model_info': {
            'type': 'Hybrid Ensemble',
            'models': hybrid_config['models'],
            'weights': {k: f"{v*100:.2f}%" for k, v in hybrid_config['weights'].items()},
            'metrics': hybrid_config['metrics'],
            'features': hybrid_config['feature_names'],
            'target_classes': hybrid_config['class_labels']
        }
    })


@hybrid_bp.route('/compare', methods=['POST'])
@jwt_required()
def compare_models():
    """Compare predictions from all models"""
    try:
        data = request.get_json()
        
        if not all([dt_model, rf_model, lr_model]):
            return jsonify({
                'success': False,
                'message': 'Models not loaded'
            }), 500
        
        # Preprocess
        X_raw = preprocess_input(data)
        X_scaled = scaler.transform(X_raw)
        
        # Individual predictions
        dt_proba = dt_model.predict_proba(X_scaled)[0]
        rf_proba = rf_model.predict_proba(X_scaled)[0]
        lr_proba = lr_model.predict_proba(X_scaled)[0]
        
        # Hybrid
        weights = hybrid_config['weights']
        hybrid_proba = (
            weights['decision_tree'] * dt_proba +
            weights['random_forest'] * rf_proba +
            weights['logistic_regression'] * lr_proba
        )
        
        comparison = {
            'decision_tree': {
                'prediction': 'CKD' if np.argmax(dt_proba) == 1 else 'No CKD',
                'ckd_probability': float(dt_proba[1]) * 100 if len(dt_proba) > 1 else 0,
                'confidence': float(np.max(dt_proba)) * 100,
                'model_accuracy': hybrid_config['metrics']['decision_tree']['accuracy'] * 100
            },
            'random_forest': {
                'prediction': 'CKD' if np.argmax(rf_proba) == 1 else 'No CKD',
                'ckd_probability': float(rf_proba[1]) * 100 if len(rf_proba) > 1 else 0,
                'confidence': float(np.max(rf_proba)) * 100,
                'model_accuracy': hybrid_config['metrics']['random_forest']['accuracy'] * 100
            },
            'logistic_regression': {
                'prediction': 'CKD' if np.argmax(lr_proba) == 1 else 'No CKD',
                'ckd_probability': float(lr_proba[1]) * 100 if len(lr_proba) > 1 else 0,
                'confidence': float(np.max(lr_proba)) * 100,
                'model_accuracy': hybrid_config['metrics']['logistic_regression']['accuracy'] * 100
            },
            'hybrid_ensemble': {
                'prediction': 'CKD' if np.argmax(hybrid_proba) == 1 else 'No CKD',
                'ckd_probability': float(hybrid_proba[1]) * 100 if len(hybrid_proba) > 1 else 0,
                'confidence': float(np.max(hybrid_proba)) * 100,
                'model_accuracy': hybrid_config['metrics']['hybrid']['accuracy'] * 100
            }
        }
        
        # Check agreement
        predictions = [np.argmax(dt_proba), np.argmax(rf_proba), np.argmax(lr_proba)]
        agreement = predictions.count(predictions[0]) == len(predictions)
        
        return jsonify({
            'success': True,
            'comparison': comparison,
            'all_models_agree': agreement,
            'recommendation': 'High confidence' if agreement else 'Models disagree - review carefully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
