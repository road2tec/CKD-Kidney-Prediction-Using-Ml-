# User Model for Smart Patient Healthcare System
# Handles user data validation and operations

from datetime import datetime
from bson import ObjectId
import bcrypt

class User:
    """Base User class with common attributes and methods"""
    
    def __init__(self, email, password, name, role, phone=None, address=None):
        self.email = email
        self.password = self.hash_password(password) if password else None
        self.name = name
        self.role = role  # 'patient', 'doctor', 'admin'
        self.phone = phone
        self.address = address
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.is_active = True
    
    @staticmethod
    def hash_password(password):
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)
    
    @staticmethod
    def verify_password(password, hashed_password):
        """Verify password against hash"""
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            "email": self.email,
            "password": self.password,
            "name": self.name,
            "role": self.role,
            "phone": self.phone,
            "address": self.address,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_active": self.is_active
        }
    
    @staticmethod
    def from_dict(data):
        """Create user object from dictionary"""
        user = User(
            email=data.get('email'),
            password=None,
            name=data.get('name'),
            role=data.get('role'),
            phone=data.get('phone'),
            address=data.get('address')
        )
        user.password = data.get('password')
        user.created_at = data.get('created_at', datetime.utcnow())
        user.updated_at = data.get('updated_at', datetime.utcnow())
        user.is_active = data.get('is_active', True)
        return user


class Patient(User):
    """Patient class extending User"""
    
    def __init__(self, email, password, name, phone=None, address=None, 
                 age=None, gender=None, blood_group=None, medical_history=None):
        super().__init__(email, password, name, 'patient', phone, address)
        self.age = age
        self.gender = gender
        self.blood_group = blood_group
        self.medical_history = medical_history or []
    
    def to_dict(self):
        """Convert patient object to dictionary"""
        data = super().to_dict()
        data.update({
            "age": self.age,
            "gender": self.gender,
            "blood_group": self.blood_group,
            "medical_history": self.medical_history
        })
        return data


class Doctor(User):
    """Doctor class extending User"""
    
    def __init__(self, email, password, name, phone=None, address=None,
                 specialization=None, qualification=None, experience=None,
                 consultation_fee=None, available_days=None, available_timings=None):
        super().__init__(email, password, name, 'doctor', phone, address)
        self.specialization = specialization
        self.qualification = qualification
        self.experience = experience
        self.consultation_fee = consultation_fee
        self.available_days = available_days or ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.available_timings = available_timings or "09:00 AM - 05:00 PM"
        self.is_available = True
    
    def to_dict(self):
        """Convert doctor object to dictionary"""
        data = super().to_dict()
        data.update({
            "specialization": self.specialization,
            "qualification": self.qualification,
            "experience": self.experience,
            "consultation_fee": self.consultation_fee,
            "available_days": self.available_days,
            "available_timings": self.available_timings,
            "is_available": self.is_available
        })
        return data


class Admin(User):
    """Admin class extending User"""
    
    def __init__(self, email, password, name, phone=None, address=None, 
                 admin_level=None):
        super().__init__(email, password, name, 'admin', phone, address)
        self.admin_level = admin_level or 'super'
    
    def to_dict(self):
        """Convert admin object to dictionary"""
        data = super().to_dict()
        data.update({
            "admin_level": self.admin_level
        })
        return data
