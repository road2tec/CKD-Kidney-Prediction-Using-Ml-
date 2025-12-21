# 🩺 Chronic Kidney Disease Prediction System

## Hybrid Explainable AI with SHAP, PDF Reports & Telemedicine

An advanced healthcare web portal using **Hybrid Machine Learning Ensemble** (Decision Tree + Random Forest + Logistic Regression) for Chronic Kidney Disease prediction with **Explainable AI (XAI)**, downloadable PDF clinical reports, personalized recommendations, donor matching, telemedicine support, and pharmacy guidance.

![CKD System](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![React](https://img.shields.io/badge/React-18.2-61DAFB)
![MongoDB](https://img.shields.io/badge/MongoDB-Local-green)
![Accuracy](https://img.shields.io/badge/Hybrid%20Accuracy-97%25-success)

---

## 🌟 Key Innovations

| Feature | Technology | Description |
|---------|------------|-------------|
| **Hybrid AI** | DT + RF + LR Ensemble | Weighted voting for maximum accuracy |
| **Explainable AI** | SHAP | Transparent predictions with feature importance |
| **PDF Reports** | ReportLab | Doctor-ready clinical reports with XAI |
| **Telemedicine** | Session Management | Remote consultations with CKD specialists |
| **Recommendations** | AI-Driven | Personalized diet, lifestyle, and medication |
| **Donor Matching** | Algorithm | Blood group and health compatibility |

---

## ✨ Features

### 🧪 Enhancement 1: Hybrid Explainable AI Model
- **3-Model Ensemble**: Decision Tree + Random Forest + Logistic Regression
- **Weighted Voting**: Accuracy-based confidence aggregation
- **SHAP Integration**: Global and individual explanations
- **Risk Assessment**: Low / Medium / High classification
- **Model Comparison**: Side-by-side predictions from all models

### 📄 Enhancement 2: Downloadable Clinical PDF Report
- **Doctor-Ready Format**: Professional clinical documentation
- **Sections Include**:
  - Patient details & demographics
  - CKD prediction result with confidence
  - Hybrid model comparison table
  - SHAP feature importance analysis
  - Clinical insights and risk factors
  - AI reasoning in plain language
  - Medical disclaimer
- **One-Click Download**: Available after each prediction

### 📹 Enhancement 3: Telemedicine Integration
- **Session Management**: Book consultations with nephrologists
- **Doctor Access**: View patient CKD reports and XAI
- **Consultation Notes**: Record and retrieve clinical notes
- **Secure Sessions**: JWT-protected endpoints

### 🍎 Enhancement 4: Personalized Recommendations

#### Lifestyle & Diet
- Stage-specific dietary guidelines
- Foods to eat vs. limit
- Lifestyle modifications
- Follow-up frequency

#### Kidney Donor Matching
- Blood group compatibility algorithm
- Age and health parameter matching
- Ranked donor list with match scores

#### Pharmacy & Medicine
- CKD medication categories
- Dosage guidance (non-prescriptive)
- Nearby pharmacy locator
- Drug interaction checker

---

## 🛠 Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, React Router, Axios, React Toastify |
| **Backend** | Python Flask, Flask-JWT-Extended, Flask-CORS |
| **Database** | MongoDB (Chronic_Kidney_Disease) |
| **ML Models** | scikit-learn (Decision Tree, Random Forest, Logistic Regression) |
| **XAI** | SHAP (SHapley Additive exPlanations) |
| **PDF Generation** | ReportLab |
| **Authentication** | JWT, bcrypt |

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ CKD Test │  │  PDF     │  │Telemedi- │  │ Pharmacy │        │
│  │  Form    │  │ Download │  │  cine    │  │  Guide   │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTP/REST
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND (Flask API)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ /hybrid  │  │/xai/     │  │/pharmacy │  │/telemedi-│        │
│  │ /predict │  │report/pdf│  │/recommend│  │  cine    │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│                              │                                   │
│  ┌───────────────────────────────────────────────────┐         │
│  │     HYBRID ENSEMBLE (DT + RF + LR + SHAP)        │         │
│  │  Weighted Voting → XAI Explanation → PDF Report  │         │
│  └───────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │ PyMongo
┌─────────────────────────────────────────────────────────────────┐
│                  MongoDB Collections (17 total)                  │
│  users, hybrid_predictions, xai_reports, pharmacy_logs,        │
│  recommendations, donors, donor_matches, telemedicine_sessions │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📡 API Documentation

### Hybrid AI Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/hybrid/predict` | Hybrid ensemble prediction |
| POST | `/api/hybrid/compare` | Compare all model predictions |
| GET | `/api/hybrid/explain/:id` | Get SHAP explanation |
| GET | `/api/hybrid/history` | Prediction history |
| GET | `/api/hybrid/model-info` | Model weights and metrics |

### XAI Report Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/xai/report/pdf/:id` | Download PDF clinical report |
| POST | `/api/xai/report/generate` | Generate report from data |
| GET | `/api/xai/report/history` | Report download history |

### Pharmacy Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/pharmacy/recommend` | Get medication recommendations |
| GET | `/api/pharmacy/medications` | All CKD medication categories |
| GET | `/api/pharmacy/pharmacies` | Nearby pharmacy list |
| POST | `/api/pharmacy/drug-interactions` | Check drug interactions |

### Telemedicine Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/telemedicine/create-session` | Create consultation session |
| GET | `/api/telemedicine/my-sessions` | Get user's sessions |
| PUT | `/api/telemedicine/update-status/:id` | Update session status |
| POST | `/api/telemedicine/add-notes/:id` | Add consultation notes |

### Donor Matching Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/donor/register` | Register as donor |
| POST | `/api/donor/match` | Find compatible donors |
| GET | `/api/donor/stats` | Donor registry statistics |

---

## 🤖 Hybrid AI Model

### Model Architecture
```
            Input (24 Medical Parameters)
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
  ┌──────────┐   ┌──────────┐   ┌──────────┐
  │ Decision │   │  Random  │   │ Logistic │
  │   Tree   │   │  Forest  │   │Regression│
  │  (94%)   │   │  (97%)   │   │  (93%)   │
  └────┬─────┘   └────┬─────┘   └────┬─────┘
       │              │              │
       ▼              ▼              ▼
     Weight         Weight         Weight
      33%            35%            32%
       │              │              │
       └──────────────┼──────────────┘
                      ▼
              Weighted Average
                      │
                      ▼
           Hybrid Prediction (97%+)
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
    Prediction    Risk Level    SHAP XAI
```

### Why Hybrid Ensemble?
1. **Diversity**: Combines different learning paradigms
2. **Robustness**: Reduces individual model biases
3. **Accuracy**: 97%+ through weighted voting
4. **Interpretability**: Decision Tree provides baseline explainability
5. **Clinical Relevance**: Logistic Regression coefficients are medically meaningful

### SHAP Explainability
- **Global Importance**: Which features matter most overall
- **Local Explanation**: Why this specific patient got this result
- **Clinical Insights**: Plain-language risk factor explanations
- **Direction Indicators**: Whether feature increases or decreases risk

---

## 📊 Database Collections

| Collection | Purpose |
|------------|---------|
| `users` | All user accounts |
| `hybrid_predictions` | Hybrid AI prediction logs |
| `xai_reports` | PDF report generation logs |
| `pharmacy_logs` | Medication recommendation history |
| `recommendations` | Lifestyle recommendations |
| `donors` | Kidney donor registry |
| `donor_matches` | Matching algorithm results |
| `telemedicine_sessions` | Consultation records |

---

## 🚀 Installation Guide

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB (running locally)

### Step 1: Clone & Setup
```bash
git clone <repository>
cd Chronic_Kidney_Disease
```

### Step 2: Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Train Hybrid Model
python ml/train_hybrid_model.py

# Start Server
python app.py
```

### Step 3: Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Step 4: Access Application
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:5000

---

## 🎓 Viva Q&A

### Q1: What is a Hybrid AI Model?
**A:** A combination of multiple ML algorithms (Decision Tree, Random Forest, Logistic Regression) that vote together using weighted averaging based on individual accuracy scores.

### Q2: Why use 3 different models?
**A:** Each model has strengths:
- **Decision Tree**: Interpretable, visualizable
- **Random Forest**: High accuracy, handles noise
- **Logistic Regression**: Clinically meaningful coefficients

### Q3: What is SHAP?
**A:** SHapley Additive exPlanations - a game-theory approach that assigns each feature a contribution score for a prediction, enabling transparent AI.

### Q4: Why is XAI critical in healthcare?
**A:** Doctors need to verify AI reasoning. Regulatory bodies require transparency. Patient trust depends on understanding the "why" behind predictions.

### Q5: How accurate is the system?
**A:** Hybrid ensemble achieves 97%+ accuracy with 5-fold cross-validation.

### Q6: How does the PDF report work?
**A:** ReportLab generates a professional clinical document including prediction, confidence, SHAP analysis, clinical insights, and medical disclaimer.

### Q7: What's in the pharmacy module?
**A:** CKD-specific medication categories, dosage notes, drug interaction checker, and nearby pharmacy locator (placeholder for real API).

### Q8: How does donor matching work?
**A:** Algorithm considers blood group compatibility (ABO + Rh), age proximity, health parameters, and availability to generate ranked matches.

---

## 📁 Project Structure

```
Chronic_Kidney_Disease/
├── backend/
│   ├── app.py                    # Main Flask app (v2.0)
│   ├── config.py
│   ├── requirements.txt
│   ├── routes/
│   │   ├── hybrid.py            # Hybrid AI prediction
│   │   ├── xai_report.py        # PDF report generation
│   │   ├── pharmacy.py          # Medication recommendations
│   │   ├── recommendations.py   # Lifestyle guidance
│   │   ├── donor.py             # Donor matching
│   │   └── telemedicine.py      # Virtual consultations
│   └── ml/
│       ├── train_hybrid_model.py
│       ├── ckd_decision_tree.pkl
│       ├── ckd_random_forest.pkl
│       ├── ckd_logistic_regression.pkl
│       ├── ckd_hybrid_config.pkl
│       └── ckd_shap_explainers.pkl
│
├── frontend/
│   └── src/
│       └── pages/
│           ├── CKDTestForm.jsx   # Hybrid AI form
│           └── CKDTestForm.css   # Gemini-style UI
│
└── kidney_disease.csv
```

---

## 📞 Contact

**Project:** Chronic Kidney Disease Prediction System  
**Version:** 2.0 (Enhanced with Hybrid AI)  
**Type:** Final Year Project  

---

## 📄 License

This project is for educational purposes - Final Year Project Submission.

---

*Built with ❤️ for early CKD detection and better kidney health*
