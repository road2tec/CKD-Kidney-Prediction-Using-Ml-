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
    """Extract text from PDF file using multiple methods including OCR"""
    text = ""
    
    # Method 1: Try pdfplumber first (better for complex PDFs)
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            print(f"PDF extraction success with pdfplumber: {len(text)} chars")
            return text
    except ImportError:
        print("pdfplumber not installed, trying PyPDF2...")
    except Exception as e:
        print(f"pdfplumber error: {e}")
    
    # Method 2: Try PyPDF2
    try:
        import PyPDF2
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            print(f"PDF extraction success with PyPDF2: {len(text)} chars")
            return text
    except Exception as e:
        print(f"PyPDF2 error: {e}")
    
    # Method 3: Try pypdf
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        if text.strip():
            print(f"PDF extraction success with pypdf: {len(text)} chars")
            return text
    except ImportError:
        pass
    except Exception as e:
        print(f"pypdf error: {e}")
    
    # Method 4: OCR for scanned/image-based PDFs
    print("Attempting OCR extraction for scanned PDF...")
    ocr_text = extract_text_with_ocr(file_path)
    if ocr_text and ocr_text.strip():
        print(f"PDF extraction success with OCR: {len(ocr_text)} chars")
        return ocr_text
    
    # If no text extracted, return None
    print("Could not extract text from PDF using any method")
    return None


def extract_text_with_ocr(file_path):
    """Extract text from scanned PDF using OCR (Tesseract)"""
    try:
        from pdf2image import convert_from_path
        import pytesseract
        from PIL import Image
        
        # Set Tesseract path for Windows if needed
        # Common installation paths on Windows
        tesseract_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Tesseract-OCR\tesseract.exe'
        ]
        
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break
        
        # Convert PDF pages to images
        # Try with poppler_path for Windows
        poppler_paths = [
            r'C:\Program Files\poppler\bin',
            r'C:\poppler\bin',
            r'C:\Program Files\poppler-24.02.0\Library\bin',
            None  # Try without specifying path (if in PATH)
        ]
        
        images = None
        for poppler_path in poppler_paths:
            try:
                if poppler_path and os.path.exists(poppler_path):
                    images = convert_from_path(file_path, poppler_path=poppler_path, dpi=300)
                elif poppler_path is None:
                    images = convert_from_path(file_path, dpi=300)
                if images:
                    break
            except Exception as e:
                continue
        
        if not images:
            print("Could not convert PDF to images. Poppler may not be installed.")
            print("Install Poppler for Windows: https://github.com/oschwartz10612/poppler-windows/releases")
            return None
        
        # Extract text from each page using OCR
        text = ""
        for i, image in enumerate(images):
            print(f"Running OCR on page {i+1}...")
            page_text = pytesseract.image_to_string(image, lang='eng')
            if page_text:
                text += page_text + "\n"
        
        return text if text.strip() else None
        
    except ImportError as e:
        print(f"OCR dependencies not installed: {e}")
        print("Install with: pip install pytesseract pdf2image Pillow")
        print("Also install Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
        return None
    except Exception as e:
        print(f"OCR extraction error: {e}")
        return None


def extract_with_gemini_ai(file_path):
    """Extract medical parameters from PDF using Gemini AI vision"""
    try:
        import google.generativeai as genai
        from pdf2image import convert_from_path
        import base64
        from io import BytesIO
        
        # Configure Gemini API
        api_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyD06VglL-lIQ-eDrqvCXB3Rg4fwRpIE46o')
        genai.configure(api_key=api_key)
        
        # Convert PDF to images
        try:
            images = convert_from_path(file_path, dpi=200, first_page=1, last_page=3)
        except Exception as e:
            print(f"Could not convert PDF to images for Gemini: {e}")
            return None
        
        if not images:
            return None
        
        # Take first page image
        img = images[0]
        
        # Convert to base64 for Gemini
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Create Gemini model with vision capability
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prompt for medical data extraction
        prompt = """Analyze this medical report image and extract the following CKD (Chronic Kidney Disease) related parameters. 
        
Return ONLY a valid JSON object with these exact keys (use null for values not found):
{
    "age": <number>,
    "bp": <blood pressure number>,
    "sg": <specific gravity like 1.015>,
    "al": <albumin 0-5>,
    "su": <sugar 0-5>,
    "rbc": "normal" or "abnormal",
    "pc": "normal" or "abnormal",
    "pcc": "present" or "notpresent",
    "ba": "present" or "notpresent",
    "bgr": <blood glucose random>,
    "bu": <blood urea>,
    "sc": <serum creatinine>,
    "sod": <sodium>,
    "pot": <potassium>,
    "hemo": <hemoglobin>,
    "pcv": <packed cell volume>,
    "wc": <white blood cell count>,
    "rc": <red blood cell count>,
    "htn": "yes" or "no",
    "dm": "yes" or "no",
    "cad": "yes" or "no",
    "appet": "good" or "poor",
    "pe": "yes" or "no",
    "ane": "yes" or "no"
}

Important: Return ONLY the JSON object, no other text."""

        # Send image to Gemini
        response = model.generate_content([
            prompt,
            {"mime_type": "image/png", "data": img_base64}
        ])
        
        # Parse response
        response_text = response.text.strip()
        
        # Try to extract JSON from response
        import json
        
        # Clean up response (remove markdown code blocks if present)
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0]
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0]
        
        extracted_values = json.loads(response_text)
        
        # Filter out null values
        extracted_values = {k: v for k, v in extracted_values.items() if v is not None}
        
        if extracted_values:
            # Convert to prediction format
            prediction_data = convert_to_prediction_format(extracted_values)
            return {
                'extracted_values': extracted_values,
                'prediction_data': prediction_data
            }
        
        return None
        
    except ImportError as e:
        print(f"Gemini AI dependencies not available: {e}")
        return None
    except Exception as e:
        print(f"Gemini AI extraction error: {e}")
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
            
            # If text extraction failed, try Gemini AI
            if not extracted_text or len(extracted_text.strip()) < 50:
                print("Text extraction failed or too short, trying Gemini AI...")
                gemini_result = extract_with_gemini_ai(temp_path)
                if gemini_result:
                    return jsonify({
                        'success': True,
                        'message': 'Report processed using AI analysis',
                        'extracted_values': gemini_result.get('extracted_values', {}),
                        'prediction_data': gemini_result.get('prediction_data', {}),
                        'parameters_found': len(gemini_result.get('extracted_values', {})),
                        'extraction_method': 'gemini_ai'
                    })
                
                # If Gemini also failed, return helpful error
                return jsonify({
                    'success': False,
                    'message': 'Could not extract text from this PDF. This might be a scanned document. Please try: 1) A text-based PDF, 2) Manual data entry, or 3) A clearer scan.',
                    'suggestions': [
                        'Use a PDF with selectable text (not a scanned image)',
                        'Try saving the document as a new PDF from the source application',
                        'Use the manual CKD test form to enter values directly'
                    ]
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
