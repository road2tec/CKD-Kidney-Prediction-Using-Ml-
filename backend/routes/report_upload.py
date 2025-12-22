"""
Health Report Upload and CKD Prediction
Allows patients to upload medical reports (PDF) and extract parameters for CKD prediction
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from bson import ObjectId
import json
import os
import re
import tempfile

report_bp = Blueprint('report', __name__)

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


def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        import PyPDF2
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return None


def parse_medical_values(text):
    """
    Parse medical values from extracted text
    Returns a dictionary of parameter values
    """
    # Define parameter patterns with various formats
    patterns = {
        'sg': [
            r'Specific\s*Gravity.*?(\d+\.?\d*)',
            r'\(sg\)\s*(\d+\.?\d*)',
            r'sg\s*[:=]?\s*(\d+\.?\d*)'
        ],
        'al': [
            r'Albumin.*?(\d+)',
            r'\(al\)\s*(\d+)',
            r'al\s*[:=]?\s*(\d+)'
        ],
        'su': [
            r'Sugar.*?(\d+)',
            r'\(su\)\s*(\d+)',
            r'su\s*[:=]?\s*(\d+)'
        ],
        'rbc': [
            r'Red\s*Blood\s*Cells.*?(Normal|Abnormal)',
            r'\(rbc\)\s*(Normal|Abnormal)'
        ],
        'pc': [
            r'Pus\s*Cell[^s].*?(Normal|Abnormal|Present|Not\s*Present)',
            r'\(pc\)\s*(Normal|Abnormal)'
        ],
        'pcc': [
            r'Pus\s*Cell\s*Clumps.*?(Present|Not\s*Present)',
            r'\(pcc\)\s*(Present|Not\s*Present)'
        ],
        'ba': [
            r'Bacteria.*?(Present|Not\s*Present)',
            r'\(ba\)\s*(Present|Not\s*Present)'
        ],
        'bgr': [
            r'Blood\s*Glucose\s*Random.*?(\d+\.?\d*)',
            r'\(bgr\)\s*(\d+\.?\d*)',
            r'bgr\s*[:=]?\s*(\d+\.?\d*)'
        ],
        'bu': [
            r'Blood\s*Urea.*?(\d+\.?\d*)',
            r'\(bu\)\s*(\d+\.?\d*)',
            r'bu\s*[:=]?\s*(\d+\.?\d*)'
        ],
        'sc': [
            r'Serum\s*Creatinine.*?(\d+\.?\d*)',
            r'\(sc\)\s*(\d+\.?\d*)',
            r'sc\s*[:=]?\s*(\d+\.?\d*)'
        ],
        'sod': [
            r'Sodium.*?(\d+\.?\d*)',
            r'\(sod\)\s*(\d+\.?\d*)',
            r'sod\s*[:=]?\s*(\d+\.?\d*)'
        ],
        'pot': [
            r'Potassium.*?(\d+\.?\d*)',
            r'\(pot\)\s*(\d+\.?\d*)',
            r'pot\s*[:=]?\s*(\d+\.?\d*)'
        ],
        'hemo': [
            r'Hemoglobin.*?(\d+\.?\d*)',
            r'\(hemo\)\s*(\d+\.?\d*)',
            r'hemo\s*[:=]?\s*(\d+\.?\d*)'
        ],
        'pcv': [
            r'Packed\s*Cell\s*Volume.*?(\d+\.?\d*)',
            r'\(pcv\)\s*(\d+)',
            r'pcv\s*[:=]?\s*(\d+)'
        ],
        'wc': [
            r'White\s*Blood\s*Cell\s*Count.*?(\d+)',
            r'\(wc\)\s*(\d+)',
            r'wc\s*[:=]?\s*(\d+)'
        ],
        'rc': [
            r'Red\s*Blood\s*Cell\s*Count.*?(\d+\.?\d*)',
            r'\(rc\)\s*(\d+\.?\d*)',
            r'rc\s*[:=]?\s*(\d+\.?\d*)'
        ],
        'htn': [
            r'Hypertension.*?(Yes|No)',
            r'\(htn\)\s*(Yes|No)'
        ],
        'dm': [
            r'Diabetes\s*Mellitus.*?(Yes|No)',
            r'\(dm\)\s*(Yes|No)'
        ],
        'cad': [
            r'Coronary\s*Artery\s*Disease.*?(Yes|No)',
            r'\(cad\)\s*(Yes|No)'
        ],
        'appet': [
            r'Appetite.*?(Good|Poor)',
            r'appet\s*[:=]?\s*(Good|Poor)'
        ],
        'pe': [
            r'Pedal\s*Edema.*?(Yes|No)',
            r'\(pe\)\s*(Yes|No)'
        ],
        'ane': [
            r'Anemia.*?(Yes|No)',
            r'\(ane\)\s*(Yes|No)'
        ]
    }
    
    extracted = {}
    
    for param, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                extracted[param] = value
                break
    
    return extracted


def convert_to_prediction_format(extracted_values):
    """
    Convert extracted values to the format expected by the CKD prediction model
    """
    # Default values for missing parameters
    defaults = {
        'age': 50,
        'bp': 80,
        'sg': 1.020,
        'al': 0,
        'su': 0,
        'rbc': 'normal',
        'pc': 'normal',
        'pcc': 'notpresent',
        'ba': 'notpresent',
        'bgr': 120,
        'bu': 40,
        'sc': 1.2,
        'sod': 140,
        'pot': 4.5,
        'hemo': 14.0,
        'pcv': 44,
        'wc': 8000,
        'rc': 5.0,
        'htn': 'no',
        'dm': 'no',
        'cad': 'no',
        'appet': 'good',
        'pe': 'no',
        'ane': 'no'
    }
    
    result = defaults.copy()
    
    # Map extracted values
    for key, value in extracted_values.items():
        if key in result:
            # Convert numeric values
            if key in ['sg', 'bgr', 'bu', 'sc', 'sod', 'pot', 'hemo', 'rc']:
                try:
                    result[key] = float(value)
                except:
                    pass
            elif key in ['al', 'su', 'pcv', 'wc', 'age', 'bp']:
                try:
                    result[key] = int(float(value))
                except:
                    pass
            else:
                # Convert text values to expected format
                value_lower = value.lower().strip()
                if key == 'rbc':
                    result[key] = 'abnormal' if 'abnormal' in value_lower else 'normal'
                elif key == 'pc':
                    result[key] = 'abnormal' if ('abnormal' in value_lower or 'present' in value_lower) and 'not' not in value_lower else 'normal'
                elif key in ['pcc', 'ba']:
                    result[key] = 'present' if 'present' in value_lower and 'not' not in value_lower else 'notpresent'
                elif key in ['htn', 'dm', 'cad', 'pe', 'ane']:
                    result[key] = 'yes' if 'yes' in value_lower else 'no'
                elif key == 'appet':
                    result[key] = 'poor' if 'poor' in value_lower else 'good'
    
    return result


@report_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_health_report():
    """
    Upload a health report (PDF) and extract medical parameters
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400
        
        # Check file extension
        allowed_extensions = {'pdf'}
        file_ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False,
                'message': 'Only PDF files are allowed'
            }), 400
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Extract text from PDF
            extracted_text = extract_text_from_pdf(temp_path)
            
            if not extracted_text:
                return jsonify({
                    'success': False,
                    'message': 'Could not extract text from PDF. Please ensure the PDF contains readable text.'
                }), 400
            
            # Parse medical values
            extracted_values = parse_medical_values(extracted_text)
            
            if not extracted_values:
                return jsonify({
                    'success': False,
                    'message': 'Could not find medical parameters in the report. Please check the report format.'
                }), 400
            
            # Convert to prediction format
            prediction_data = convert_to_prediction_format(extracted_values)
            
            # Log the upload
            db = get_db()
            current_user = get_current_user()
            
            upload_log = {
                'user_id': current_user['id'],
                'filename': file.filename,
                'extracted_values': extracted_values,
                'prediction_data': prediction_data,
                'extracted_text': extracted_text[:1000],  # First 1000 chars for reference
                'created_at': datetime.utcnow()
            }
            db.report_uploads.insert_one(upload_log)
            
            return jsonify({
                'success': True,
                'message': 'Report processed successfully',
                'extracted_values': extracted_values,
                'prediction_data': prediction_data,
                'parameters_found': len(extracted_values),
                'raw_text_preview': extracted_text[:500]
            })
            
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error processing report: {str(e)}'
        }), 500


@report_bp.route('/predict-from-report', methods=['POST'])
@jwt_required()
def predict_from_report():
    """
    Make CKD prediction using parameters extracted from uploaded report
    """
    try:
        data = request.get_json()
        prediction_data = data.get('prediction_data', {})
        
        if not prediction_data:
            return jsonify({
                'success': False,
                'message': 'No prediction data provided'
            }), 400
        
        # Import hybrid prediction function
        from routes.hybrid import make_prediction
        
        # Make prediction
        prediction_result = make_prediction(prediction_data)
        
        if prediction_result:
            # Store prediction
            db = get_db()
            current_user = get_current_user()
            
            prediction_record = {
                'user_id': current_user['id'],
                'source': 'report_upload',
                'input_data': prediction_data,
                'prediction': prediction_result,
                'timestamp': datetime.utcnow()
            }
            db.ckd_predictions.insert_one(prediction_record)
            
            return jsonify({
                'success': True,
                'prediction': prediction_result,
                'source': 'report_upload'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Prediction failed'
            }), 500
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@report_bp.route('/history', methods=['GET'])
@jwt_required()
def get_upload_history():
    """Get user's report upload history"""
    try:
        db = get_db()
        current_user = get_current_user()
        
        uploads = list(db.report_uploads.find(
            {'user_id': current_user['id']}
        ).sort('created_at', -1).limit(10))
        
        for upload in uploads:
            upload['_id'] = str(upload['_id'])
            if upload.get('created_at'):
                upload['created_at'] = upload['created_at'].isoformat()
        
        return jsonify({
            'success': True,
            'uploads': uploads
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
