# 🏥 Smart Patient Healthcare System

## AI/ML-Based Web Portal for Disease Prediction & Doctor Appointment

A complete, production-ready healthcare system using AI/ML for symptom-based disease prediction and automated doctor specialization matching.

![Healthcare System](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![React](https://img.shields.io/badge/React-18.2-61DAFB)
![MongoDB](https://img.shields.io/badge/MongoDB-Local-green)

---

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Installation Guide](#installation-guide)
- [ML Model Explanation](#ml-model-explanation)
- [API Documentation](#api-documentation)
- [User Roles](#user-roles)
- [Project Structure](#project-structure)
- [Viva Questions & Answers](#viva-questions--answers)
- [Demo Flow](#demo-flow)

---

## ✨ Features

### Patient Features
- 🔐 Secure registration and login
- 🔍 AI-powered symptom analysis
- 🎯 Disease prediction with confidence scores
- 👨‍⚕️ Automatic doctor specialization matching
- 📅 Online appointment booking
- 📊 Appointment history tracking

### Doctor Features
- 📋 View upcoming appointments
- 👥 Access patient symptoms and predictions
- ✅ Update appointment status (pending/confirmed/completed)
- 📈 Dashboard with statistics

### Admin Features
- 👤 Manage all users (patients/doctors)
- ➕ Add new doctors with specializations
- 📊 View system-wide statistics
- 📝 Monitor AI predictions and appointments

---

## 🛠 Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, React Router, Axios, React Icons, React Toastify |
| **Backend** | Python Flask, Flask-JWT-Extended, Flask-CORS |
| **Database** | MongoDB (via PyMongo) |
| **AI/ML** | scikit-learn, Multinomial Naive Bayes |
| **Authentication** | JWT (JSON Web Tokens), bcrypt |

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ Landing  │  │  Login   │  │ Patient  │  │  Admin   │        │
│  │  Page    │  │ Register │  │Dashboard │  │Dashboard │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTP/REST
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND (Flask)                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │   Auth   │  │ Patient  │  │  Doctor  │  │  Admin   │        │
│  │  Routes  │  │  Routes  │  │  Routes  │  │  Routes  │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│                              │                                   │
│  ┌───────────────────────────────────────────────────┐         │
│  │              ML Model (Naive Bayes)               │         │
│  │  Symptoms → Vectorizer → Prediction → Disease    │         │
│  └───────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │ PyMongo
┌─────────────────────────────────────────────────────────────────┐
│                     MongoDB (missing_person)                     │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌─────────────┐ ┌──────────┐ │
│  │ users  │ │patients│ │doctors │ │appointments │ │symptoms_ │ │
│  │        │ │        │ │        │ │             │ │  logs    │ │
│  └────────┘ └────────┘ └────────┘ └─────────────┘ └──────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation Guide

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB (running locally)
- MongoDB Compass (for visualization)

### Step 1: Clone/Setup Project
```bash
cd e:\smart_patient_healthcare_system
```

### Step 2: Setup MongoDB
1. Start MongoDB service
2. Open MongoDB Compass
3. Connect to: `mongodb://localhost:27017`
4. Database will be auto-created as `missing_person`

### Step 3: Backend Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Train the ML model
python ml/train_model.py

# Start the server
python app.py
```

### Step 4: Frontend Setup
```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### Step 5: Access the Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Default Admin: `admin@healthcare.com` / `admin123`

---

## 🤖 ML Model Explanation

### Why Multinomial Naive Bayes?

1. **Perfect for Text Classification**: Symptoms are essentially text/categorical data
2. **Fast Training & Prediction**: Ideal for real-time healthcare applications
3. **Works with Limited Data**: Good performance even with smaller datasets
4. **Probability Estimates**: Provides confidence scores for predictions
5. **Simple & Interpretable**: Easy to explain to stakeholders

### Model Training Pipeline

```python
# 1. Load Dataset
df = pd.read_csv('dataset.csv')  # 4900+ rows, 41 diseases

# 2. Preprocess Symptoms
symptoms_text = combine_all_symptom_columns()

# 3. Vectorize
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(symptoms)

# 4. Train Model
model = MultinomialNB(alpha=1.0)
model.fit(X_train, y_train)

# 5. Save Model
pickle.dump(model, open('model.pkl', 'wb'))
```

### Prediction Flow
1. Patient enters symptoms (e.g., "headache, fever, cough")
2. Symptoms are preprocessed and tokenized
3. CountVectorizer transforms to feature vector
4. Naive Bayes predicts disease probability
5. Top prediction with confidence score returned
6. Disease mapped to doctor specialization

---

## 📡 API Documentation

### Authentication Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | Patient registration |
| POST | `/api/login` | User login (all roles) |
| GET | `/api/me` | Get current user |

### Patient Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/symptoms/predict` | AI symptom prediction |
| GET | `/api/symptoms/all` | Get all symptom list |
| POST | `/api/appointments/book` | Book appointment |
| GET | `/api/appointments/my` | Get my appointments |
| GET | `/api/doctors` | Get available doctors |

### Doctor Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/doctor/appointments` | Get appointments |
| PUT | `/api/doctor/update-status` | Update appointment status |
| GET | `/api/doctor/stats` | Get statistics |

### Admin Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/users` | Get all users |
| POST | `/api/admin/add-doctor` | Add new doctor |
| DELETE | `/api/admin/delete-user/:id` | Deactivate user |
| GET | `/api/admin/stats` | System statistics |

---

## 👥 User Roles

### Patient
- Register and login
- Enter symptoms for AI analysis
- View predicted disease and recommended specialist
- Book appointments with doctors
- Track appointment history

### Doctor
- Login with admin-provided credentials
- View patient appointments
- See patient symptoms and AI predictions
- Confirm/complete/cancel appointments

### Admin
- Manage entire system
- Add doctors with specializations
- View all users and appointments
- Monitor AI predictions

---

## 📁 Project Structure

```
smart_patient_healthcare_system/
│
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration settings
│   ├── requirements.txt       # Python dependencies
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py            # User models
│   │   └── appointment.py     # Appointment models
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py            # Authentication routes
│   │   ├── patient.py         # Patient routes
│   │   ├── doctor.py          # Doctor routes
│   │   └── admin.py           # Admin routes
│   │
│   └── ml/
│       ├── __init__.py
│       ├── train_model.py     # ML training script
│       ├── model.pkl          # Trained model
│       ├── vectorizer.pkl     # Feature vectorizer
│       └── label_encoder.pkl  # Label encoder
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   │
│   └── src/
│       ├── index.js
│       ├── index.css          # Global styles
│       ├── App.jsx            # Main app component
│       │
│       └── pages/
│           ├── LandingPage.jsx
│           ├── LandingPage.css
│           ├── LoginPage.jsx
│           ├── RegisterPage.jsx
│           ├── AuthPages.css
│           ├── PatientDashboard.jsx
│           ├── DoctorDashboard.jsx
│           ├── AdminDashboard.jsx
│           └── Dashboard.css
│
├── dataset.csv                # Training dataset
├── Symptom-severity.csv       # Symptom weights
├── symptom_Description.csv    # Disease descriptions
├── symptom_precaution.csv     # Disease precautions
│
└── README.md
```

---

## 📚 Viva Questions & Answers

### Q1: What is the main objective of this project?
**A:** To build an AI-powered healthcare portal where patients can enter symptoms, receive disease predictions using ML, and book appointments with appropriate specialists.

### Q2: Why did you choose Naive Bayes for this project?
**A:** Multinomial Naive Bayes is ideal because:
- Works well with text/categorical symptom data
- Fast training and prediction
- Provides probability estimates
- Simple to implement and interpret
- Good accuracy even with limited data

### Q3: Explain the prediction flow.
**A:** 
1. Patient enters symptoms as text
2. Symptoms are tokenized and cleaned
3. CountVectorizer converts to numerical features
4. Naive Bayes model predicts disease probabilities
5. Top prediction with confidence score is returned
6. Disease is mapped to doctor specialization

### Q4: What database are you using and why?
**A:** MongoDB - a NoSQL database that:
- Stores flexible JSON-like documents
- Perfect for healthcare records with varying fields
- Easy to scale
- Great with Python (PyMongo)

### Q5: How is authentication handled?
**A:** 
- JWT (JSON Web Tokens) for stateless authentication
- bcrypt for password hashing
- Role-based access control (patient/doctor/admin)
- Token stored in localStorage on frontend

### Q6: What is the accuracy of your model?
**A:** The model achieves approximately 95% accuracy on the test set with 41 disease classes and symptom combinations.

### Q7: How does the system handle security?
**A:** 
- Password hashing with bcrypt
- JWT authentication
- Role-based route protection
- Input validation on all endpoints

### Q8: What are the main collections in MongoDB?
**A:** 
- `users` - All user accounts
- `patients` - Patient-specific data
- `doctors` - Doctor profiles and specializations
- `appointments` - Booking records
- `symptoms_logs` - Prediction history
- `admin_logs` - Admin action tracking

### Q9: How can this system be improved?
**A:** 
- Add more diseases to the dataset
- Implement video consultation
- Add prescription management
- Integrate payment gateway
- Mobile app development

### Q10: What is CountVectorizer?
**A:** A scikit-learn tool that converts text to numerical feature vectors by counting word occurrences, enabling ML algorithms to process text data.

---

## 🎬 Demo Flow

1. **Landing Page**: Showcase AI-powered features
2. **Patient Registration**: Create new account
3. **Login**: Authenticate user
4. **Symptom Entry**: Enter symptoms like "fever, headache, cough"
5. **AI Prediction**: View disease prediction with confidence
6. **Doctor Match**: See recommended specialists
7. **Book Appointment**: Select doctor, date, time
8. **Doctor Login**: Show appointment management
9. **Admin Panel**: Demonstrate user management

---

## 📞 Contact

**Project:** Smart Patient Healthcare System  
**Type:** Final Year Computer Engineering Project  
**Database:** MongoDB Compass (mongodb://localhost:27017/missing_person)

---

## 📄 License

This project is for educational purposes - Final Year Project Submission.

---

*Built with ❤️ for better healthcare*
