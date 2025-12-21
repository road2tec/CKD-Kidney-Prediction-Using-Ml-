# Configuration file for the Smart Patient Healthcare System
# This file contains all the configuration settings for the backend
# All sensitive data is loaded from .env file

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB Configuration - from .env
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/Chronic_Kidney_Disease')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'Chronic_Kidney_Disease')

# Collection Names
COLLECTIONS = {
    "users": "users",
    "patients": "patients",
    "doctors": "doctors",
    "admins": "admins",
    "appointments": "appointments",
    "symptoms_logs": "symptoms_logs",
    "admin_logs": "admin_logs"
}

# JWT Configuration - from .env
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'smart_healthcare_super_secret_key_2024')
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES_HOURS', '24')))

# Flask Configuration - from .env
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))

# Default Admin Credentials - from .env
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@healthcare.com')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
ADMIN_NAME = os.getenv('ADMIN_NAME', 'System Admin')

# CORS Configuration - from .env
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000')
CORS_ORIGINS = [origin.strip() for origin in cors_origins.split(',')]

# ML Model Configuration
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml', 'model.pkl')
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), 'ml', 'vectorizer.pkl')
LABEL_ENCODER_PATH = os.path.join(os.path.dirname(__file__), 'ml', 'label_encoder.pkl')

# Gemini AI Configuration - from .env
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-pro')

# Doctor Specializations mapping to diseases
DISEASE_TO_SPECIALIZATION = {
    # General Physician
    "Fungal infection": "General Physician",
    "Allergy": "General Physician",
    "Common Cold": "General Physician",
    "Typhoid": "General Physician",
    "Chicken pox": "General Physician",
    "Malaria": "General Physician",
    "Dengue": "General Physician",
    "Gastroenteritis": "General Physician",
    
    # Gastroenterologist
    "GERD": "Gastroenterologist",
    "Chronic cholestasis": "Gastroenterologist",
    "Peptic ulcer diseae": "Gastroenterologist",
    "hepatitis A": "Gastroenterologist",
    "Hepatitis B": "Gastroenterologist",
    "Hepatitis C": "Gastroenterologist",
    "Hepatitis D": "Gastroenterologist",
    "Hepatitis E": "Gastroenterologist",
    "Alcoholic hepatitis": "Gastroenterologist",
    "Jaundice": "Gastroenterologist",
    
    # Dermatologist
    "Drug Reaction": "Dermatologist",
    "Psoriasis": "Dermatologist",
    "Acne": "Dermatologist",
    "Impetigo": "Dermatologist",
    
    # Cardiologist
    "Heart attack": "Cardiologist",
    "Varicose veins": "Cardiologist",
    "Hypertension ": "Cardiologist",
    
    # Pulmonologist
    "Bronchial Asthma": "Pulmonologist",
    "Pneumonia": "Pulmonologist",
    "Tuberculosis": "Pulmonologist",
    
    # Endocrinologist
    "Diabetes ": "Endocrinologist",
    "Hypothyroidism": "Endocrinologist",
    "Hyperthyroidism": "Endocrinologist",
    "Hypoglycemia": "Endocrinologist",
    
    # Neurologist
    "Migraine": "Neurologist",
    "(vertigo) Paroymsal  Positional Vertigo": "Neurologist",
    "Cervical spondylosis": "Neurologist",
    "Paralysis (brain hemorrhage)": "Neurologist",
    
    # Orthopedic
    "Osteoarthristis": "Orthopedic",
    "Arthritis": "Orthopedic",
    
    # Urologist
    "Urinary tract infection": "Urologist",
    
    # Proctologist
    "Dimorphic hemmorhoids(piles)": "Proctologist",
    
    # Infectious Disease Specialist
    "AIDS": "Infectious Disease Specialist"
}

# Default specialization for unknown diseases
DEFAULT_SPECIALIZATION = "General Physician"
