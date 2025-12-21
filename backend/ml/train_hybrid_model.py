"""
Hybrid Explainable AI Model Training for CKD Prediction
Implements: Decision Tree + Random Forest + Logistic Regression with weighted voting
Includes: SHAP explanations for all models
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
import pickle
import os
import warnings
warnings.filterwarnings('ignore')

# Try to import SHAP
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    print("Warning: SHAP not available. Install with: pip install shap")

print("=" * 70)
print("HYBRID EXPLAINABLE AI MODEL - CKD PREDICTION SYSTEM")
print("Decision Tree + Random Forest + Logistic Regression + SHAP")
print("=" * 70)

# ============== LOAD AND PREPROCESS DATA ==============
print("\n[1/8] Loading dataset...")

# Find dataset
dataset_paths = [
    '../kidney_disease.csv',
    '../../kidney_disease.csv',
    'kidney_disease.csv',
    '../data/kidney_disease.csv'
]

df = None
for path in dataset_paths:
    if os.path.exists(path):
        df = pd.read_csv(path)
        print(f"   ✓ Loaded: {path} ({len(df)} records)")
        break

if df is None:
    raise FileNotFoundError("kidney_disease.csv not found!")

# ============== DATA PREPROCESSING ==============
print("\n[2/8] Preprocessing data...")

# Clean column names
df.columns = df.columns.str.strip()

# Handle target variable
df['classification'] = df['classification'].str.strip().replace({
    'ckd': 1, 'notckd': 0, 'ckd\t': 1, 'notckd\t': 0
})

# Define feature types
numerical_features = ['age', 'bp', 'sg', 'al', 'su', 'bgr', 'bu', 'sc', 'sod', 'pot', 'hemo', 'pcv', 'wc', 'rc']
categorical_features = ['rbc', 'pc', 'pcc', 'ba', 'htn', 'dm', 'cad', 'appet', 'pe', 'ane']

# Clean and convert numerical features
for col in numerical_features:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col].fillna(df[col].median(), inplace=True)

# Clean and encode categorical features
label_encoders = {}
for col in categorical_features:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip().str.lower()
        df[col] = df[col].replace({'?': np.nan, '': np.nan, 'nan': np.nan})
        df[col].fillna(df[col].mode()[0] if len(df[col].mode()) > 0 else 'unknown', inplace=True)
        
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le

print(f"   ✓ Processed {len(numerical_features)} numerical features")
print(f"   ✓ Encoded {len(categorical_features)} categorical features")

# ============== PREPARE FEATURES ==============
print("\n[3/8] Preparing features...")

feature_columns = numerical_features + categorical_features
X = df[feature_columns].copy()
y = df['classification'].copy()

# Handle any remaining NaN
X = X.fillna(X.median())

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Target encoder
target_encoder = LabelEncoder()
y_encoded = target_encoder.fit_transform(y)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

print(f"   ✓ Training samples: {len(X_train)}")
print(f"   ✓ Testing samples: {len(X_test)}")
print(f"   ✓ Feature count: {X_scaled.shape[1]}")

# ============== TRAIN INDIVIDUAL MODELS ==============
print("\n[4/8] Training individual models...")

# Model 1: Decision Tree (Interpretability)
dt_model = DecisionTreeClassifier(
    max_depth=10,
    min_samples_split=10,
    min_samples_leaf=5,
    class_weight='balanced',
    random_state=42
)
dt_model.fit(X_train, y_train)
dt_accuracy = accuracy_score(y_test, dt_model.predict(X_test))
dt_cv_scores = cross_val_score(dt_model, X_scaled, y_encoded, cv=5)
print(f"   ✓ Decision Tree: {dt_accuracy*100:.2f}% (CV: {dt_cv_scores.mean()*100:.2f}% ± {dt_cv_scores.std()*100:.2f}%)")

# Model 2: Random Forest (Accuracy)
rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=15,
    min_samples_split=5,
    min_samples_leaf=2,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train, y_train)
rf_accuracy = accuracy_score(y_test, rf_model.predict(X_test))
rf_cv_scores = cross_val_score(rf_model, X_scaled, y_encoded, cv=5)
print(f"   ✓ Random Forest: {rf_accuracy*100:.2f}% (CV: {rf_cv_scores.mean()*100:.2f}% ± {rf_cv_scores.std()*100:.2f}%)")

# Model 3: Logistic Regression (Clinical Relevance)
lr_model = LogisticRegression(
    max_iter=1000,
    class_weight='balanced',
    random_state=42,
    solver='lbfgs'
)
lr_model.fit(X_train, y_train)
lr_accuracy = accuracy_score(y_test, lr_model.predict(X_test))
lr_cv_scores = cross_val_score(lr_model, X_scaled, y_encoded, cv=5)
print(f"   ✓ Logistic Regression: {lr_accuracy*100:.2f}% (CV: {lr_cv_scores.mean()*100:.2f}% ± {lr_cv_scores.std()*100:.2f}%)")

# ============== HYBRID MODEL WEIGHTS ==============
print("\n[5/8] Creating hybrid ensemble...")

# Calculate weights based on accuracy
total_accuracy = dt_accuracy + rf_accuracy + lr_accuracy
weights = {
    'decision_tree': dt_accuracy / total_accuracy,
    'random_forest': rf_accuracy / total_accuracy,
    'logistic_regression': lr_accuracy / total_accuracy
}

print(f"   Model Weights (accuracy-based):")
print(f"   - Decision Tree:       {weights['decision_tree']*100:.2f}%")
print(f"   - Random Forest:       {weights['random_forest']*100:.2f}%")
print(f"   - Logistic Regression: {weights['logistic_regression']*100:.2f}%")

# Hybrid prediction function
def hybrid_predict(X_input):
    """Weighted voting ensemble prediction"""
    dt_proba = dt_model.predict_proba(X_input)
    rf_proba = rf_model.predict_proba(X_input)
    lr_proba = lr_model.predict_proba(X_input)
    
    # Weighted average
    hybrid_proba = (
        weights['decision_tree'] * dt_proba +
        weights['random_forest'] * rf_proba +
        weights['logistic_regression'] * lr_proba
    )
    
    return hybrid_proba

# Test hybrid model
hybrid_proba_test = hybrid_predict(X_test)
hybrid_predictions = np.argmax(hybrid_proba_test, axis=1)
hybrid_accuracy = accuracy_score(y_test, hybrid_predictions)
hybrid_precision = precision_score(y_test, hybrid_predictions, average='weighted')
hybrid_recall = recall_score(y_test, hybrid_predictions, average='weighted')
hybrid_f1 = f1_score(y_test, hybrid_predictions, average='weighted')

print(f"\n   ✓ HYBRID MODEL PERFORMANCE:")
print(f"     - Accuracy:  {hybrid_accuracy*100:.2f}%")
print(f"     - Precision: {hybrid_precision*100:.2f}%")
print(f"     - Recall:    {hybrid_recall*100:.2f}%")
print(f"     - F1-Score:  {hybrid_f1*100:.2f}%")

# ============== SHAP EXPLAINERS ==============
print("\n[6/8] Creating SHAP explainers...")

shap_explainers = {}
if SHAP_AVAILABLE:
    try:
        # Tree explainer for tree-based models
        print("   Creating TreeExplainer for Random Forest...")
        rf_explainer = shap.TreeExplainer(rf_model)
        shap_explainers['random_forest'] = rf_explainer
        
        print("   Creating TreeExplainer for Decision Tree...")
        dt_explainer = shap.TreeExplainer(dt_model)
        shap_explainers['decision_tree'] = dt_explainer
        
        # Linear explainer for logistic regression
        print("   Creating LinearExplainer for Logistic Regression...")
        lr_explainer = shap.LinearExplainer(lr_model, X_train)
        shap_explainers['logistic_regression'] = lr_explainer
        
        print("   ✓ All SHAP explainers created successfully")
        
        # Calculate global feature importance
        print("   Calculating global feature importance...")
        sample_size = min(100, len(X_test))
        X_sample = X_test[:sample_size]
        
        rf_shap_values = rf_explainer.shap_values(X_sample)
        if isinstance(rf_shap_values, list):
            global_importance = np.abs(rf_shap_values[1]).mean(axis=0)
        else:
            global_importance = np.abs(rf_shap_values).mean(axis=0)
        
        feature_importance_df = pd.DataFrame({
            'feature': feature_columns,
            'importance': global_importance
        }).sort_values('importance', ascending=False)
        
        print("\n   Top 10 Most Important Features:")
        for idx, row in feature_importance_df.head(10).iterrows():
            print(f"     {row['feature']:15s}: {row['importance']:.4f}")
            
    except Exception as e:
        print(f"   Warning: SHAP error: {e}")
        print("   Continuing without SHAP explainers...")

# ============== SAVE MODELS AND ARTIFACTS ==============
print("\n[7/8] Saving models and artifacts...")

# Create ml directory if needed
os.makedirs('.', exist_ok=True)

# Save individual models
pickle.dump(dt_model, open('ckd_decision_tree.pkl', 'wb'))
pickle.dump(rf_model, open('ckd_random_forest.pkl', 'wb'))
pickle.dump(lr_model, open('ckd_logistic_regression.pkl', 'wb'))
print("   ✓ Saved: ckd_decision_tree.pkl")
print("   ✓ Saved: ckd_random_forest.pkl")
print("   ✓ Saved: ckd_logistic_regression.pkl")

# Save preprocessing artifacts
pickle.dump(scaler, open('ckd_scaler.pkl', 'wb'))
pickle.dump(target_encoder, open('ckd_target_encoder.pkl', 'wb'))
pickle.dump(label_encoders, open('ckd_label_encoders.pkl', 'wb'))
pickle.dump(feature_columns, open('ckd_feature_names.pkl', 'wb'))
print("   ✓ Saved: preprocessing artifacts")

# Save SHAP explainers
if shap_explainers:
    pickle.dump(shap_explainers, open('ckd_shap_explainers.pkl', 'wb'))
    print("   ✓ Saved: ckd_shap_explainers.pkl")

# Save hybrid model configuration
hybrid_config = {
    'weights': weights,
    'models': ['decision_tree', 'random_forest', 'logistic_regression'],
    'metrics': {
        'decision_tree': {'accuracy': dt_accuracy, 'cv_mean': dt_cv_scores.mean(), 'cv_std': dt_cv_scores.std()},
        'random_forest': {'accuracy': rf_accuracy, 'cv_mean': rf_cv_scores.mean(), 'cv_std': rf_cv_scores.std()},
        'logistic_regression': {'accuracy': lr_accuracy, 'cv_mean': lr_cv_scores.mean(), 'cv_std': lr_cv_scores.std()},
        'hybrid': {'accuracy': hybrid_accuracy, 'precision': hybrid_precision, 'recall': hybrid_recall, 'f1': hybrid_f1}
    },
    'feature_names': feature_columns,
    'target_classes': list(target_encoder.classes_) if hasattr(target_encoder, 'classes_') else [0, 1],
    'class_labels': {0: 'notckd', 1: 'ckd'}
}
pickle.dump(hybrid_config, open('ckd_hybrid_config.pkl', 'wb'))
print("   ✓ Saved: ckd_hybrid_config.pkl")

# ============== SUMMARY ==============
print("\n" + "=" * 70)
print("HYBRID MODEL TRAINING COMPLETE")
print("=" * 70)
print(f"""
Model Performance Summary:
{'='*50}
| Model                 | Accuracy | CV Score       |
|----------------------|----------|----------------|
| Decision Tree        | {dt_accuracy*100:6.2f}%  | {dt_cv_scores.mean()*100:.2f}% ± {dt_cv_scores.std()*100:.2f}% |
| Random Forest        | {rf_accuracy*100:6.2f}%  | {rf_cv_scores.mean()*100:.2f}% ± {rf_cv_scores.std()*100:.2f}% |
| Logistic Regression  | {lr_accuracy*100:6.2f}%  | {lr_cv_scores.mean()*100:.2f}% ± {lr_cv_scores.std()*100:.2f}% |
| HYBRID ENSEMBLE      | {hybrid_accuracy*100:6.2f}%  | F1: {hybrid_f1*100:.2f}%       |
{'='*50}

Saved Artifacts:
- ckd_decision_tree.pkl
- ckd_random_forest.pkl  
- ckd_logistic_regression.pkl
- ckd_hybrid_config.pkl
- ckd_scaler.pkl
- ckd_target_encoder.pkl
- ckd_label_encoders.pkl
- ckd_feature_names.pkl
- ckd_shap_explainers.pkl

✅ Hybrid Explainable AI Model Ready for Production!
""")
