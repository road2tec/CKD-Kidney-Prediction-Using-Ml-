# Appointment Model for Smart Patient Healthcare System
# Handles appointment data and operations

from datetime import datetime
from bson import ObjectId

class Appointment:
    """Appointment class for managing patient-doctor appointments"""
    
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    
    def __init__(self, patient_id, doctor_id, appointment_date, appointment_time,
                 symptoms=None, predicted_disease=None, predicted_specialization=None,
                 notes=None):
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.appointment_date = appointment_date
        self.appointment_time = appointment_time
        self.symptoms = symptoms or []
        self.predicted_disease = predicted_disease
        self.predicted_specialization = predicted_specialization
        self.notes = notes
        self.status = self.STATUS_PENDING
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.doctor_notes = None
        self.prescription = None
    
    def to_dict(self):
        """Convert appointment object to dictionary"""
        return {
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "appointment_date": self.appointment_date,
            "appointment_time": self.appointment_time,
            "symptoms": self.symptoms,
            "predicted_disease": self.predicted_disease,
            "predicted_specialization": self.predicted_specialization,
            "notes": self.notes,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "doctor_notes": self.doctor_notes,
            "prescription": self.prescription
        }
    
    @staticmethod
    def from_dict(data):
        """Create appointment object from dictionary"""
        appointment = Appointment(
            patient_id=data.get('patient_id'),
            doctor_id=data.get('doctor_id'),
            appointment_date=data.get('appointment_date'),
            appointment_time=data.get('appointment_time'),
            symptoms=data.get('symptoms'),
            predicted_disease=data.get('predicted_disease'),
            predicted_specialization=data.get('predicted_specialization'),
            notes=data.get('notes')
        )
        appointment.status = data.get('status', Appointment.STATUS_PENDING)
        appointment.created_at = data.get('created_at', datetime.utcnow())
        appointment.updated_at = data.get('updated_at', datetime.utcnow())
        appointment.doctor_notes = data.get('doctor_notes')
        appointment.prescription = data.get('prescription')
        return appointment


class SymptomLog:
    """SymptomLog class for tracking patient symptom entries and predictions"""
    
    def __init__(self, patient_id, symptoms_text, symptoms_list, 
                 predicted_disease, predicted_specialization, confidence_score):
        self.patient_id = patient_id
        self.symptoms_text = symptoms_text
        self.symptoms_list = symptoms_list
        self.predicted_disease = predicted_disease
        self.predicted_specialization = predicted_specialization
        self.confidence_score = confidence_score
        self.created_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert symptom log object to dictionary"""
        return {
            "patient_id": self.patient_id,
            "symptoms_text": self.symptoms_text,
            "symptoms_list": self.symptoms_list,
            "predicted_disease": self.predicted_disease,
            "predicted_specialization": self.predicted_specialization,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at
        }


class AdminLog:
    """AdminLog class for tracking admin actions"""
    
    def __init__(self, admin_id, action, target_type, target_id, details=None):
        self.admin_id = admin_id
        self.action = action  # 'add', 'update', 'delete', 'view'
        self.target_type = target_type  # 'doctor', 'patient', 'appointment'
        self.target_id = target_id
        self.details = details
        self.created_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert admin log object to dictionary"""
        return {
            "admin_id": self.admin_id,
            "action": self.action,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "details": self.details,
            "created_at": self.created_at
        }
