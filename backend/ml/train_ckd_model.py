"""
CKD (Chronic Kidney Disease) Prediction Model Training Script
with Explainable AI (SHAP) Integration

This script trains Decision Tree and Random Forest models to predict CKD
and integrates SHAP for model interpretability.

Models trained:
1. Decision Tree - Primary (interpretable)
2. Random Forest - Secondary (higher accuracy)

Features: XAI using SHAP for global and local explanations
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                              f1_score, classification_report, confusion_matrix)
import pickle
import shap
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
import warnings
warnings.filterwarnings('ignore')

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))

def load_and_preprocess_ckd_data():
    """Load and preprocess the CKD dataset from kidney_disease.csv"""
    
    # Load the dataset
    dataset_path = os.path.join(PROJECT_DIR, 'kidney_disease.csv')
    print(f"Loading CKD dataset from: {dataset_path}")
    
    df = pd.read_csv(dataset_path)
    print(f"Dataset shape: {df.shape}")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nFirst few rows:\n{df.head()}")
    
    # Check target variable distribution
    print(f"\nTarget variable distribution:")
    print(df['classification'].value_counts())
    
    # Handle missing values
    print(f"\nMissing values before cleaning:")
    print(df.isnull().sum())
    
    # Separate numerical and categorical columns
    numerical_cols = ['age', 'bp', 'sg', 'al', 'su', 'bgr', 'bu', 'sc', 
                      'sod', 'pot', 'hemo', 'pcv', 'wc', 'rc']
    categorical_cols = ['rbc', 'pc', 'pcc', 'ba', 'htn', 'dm', 'cad', 
                        'appet', 'pe', 'ane']
    
    # Fill missing values for numerical columns with median
    for col in numerical_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col].fillna(df[col].median(), inplace=True)
    
    # Fill missing values for categorical columns with mode
    for col in categorical_cols:
        if col in df.columns:
            df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'unknown', inplace=True)
    
    # Clean categorical values (remove spaces, standardize)
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.lower()
    
    # Clean target variable
    df['classification'] = df['classification'].astype(str).str.strip().str.lower()
    
    print(f"\nMissing values after cleaning:")
    print(df.isnull().sum().sum())
    
    # Encode categorical variables
    label_encoders = {}
    for col in categorical_cols:
        if col in df.columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            label_encoders[col] = le
    
    # Encode target variable
    target_encoder = LabelEncoder()
    df['classification_encoded'] = target_encoder.fit_transform(df['classification'])
    
    print(f"\nTarget classes: {target_encoder.classes_}")
    print(f"Encoded target distribution:")
    print(df['classification_encoded'].value_counts())
    
    # Drop id column if exists
    if 'id' in df.columns:
        df = df.drop('id', axis=1)
    
    return df, label_encoders, target_encoder

def train_models(df, target_encoder):
    """Train Decision Tree and Random Forest models"""
    
    # Prepare features and target
    X = df.drop(['classification', 'classification_encoded'], axis=1)
    y = df['classification_encoded']
    
    print(f"\n{'='*60}")
    print(f"Training CKD Prediction Models")
    print(f"{'='*60}")
    print(f"Features shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    print(f"Feature names: {list(X.columns)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    
    # Scale features for better performance
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Store feature names for SHAP
    feature_names = list(X.columns)
    
    # ============ Decision Tree Model ============
    print(f"\n{'='*60}")
    print("1. Training Decision Tree Classifier (Interpretable Model)")
    print(f"{'='*60}")
    
    dt_model = DecisionTreeClassifier(
        max_depth=10,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
        class_weight='balanced'
    )
    dt_model.fit(X_train_scaled, y_train)
    
    # Evaluate Decision Tree
    dt_pred = dt_model.predict(X_test_scaled)
    dt_accuracy = accuracy_score(y_test, dt_pred)
    dt_precision = precision_score(y_test, dt_pred, average='weighted', zero_division=0)
    dt_recall = recall_score(y_test, dt_pred, average='weighted', zero_division=0)
    dt_f1 = f1_score(y_test, dt_pred, average='weighted', zero_division=0)
    
    print(f"\nDecision Tree Results:")
    print(f"Accuracy: {dt_accuracy * 100:.2f}%")
    print(f"Precision: {dt_precision * 100:.2f}%")
    print(f"Recall: {dt_recall * 100:.2f}%")
    print(f"F1-Score: {dt_f1 * 100:.2f}%")
    
    # Cross-validation
    dt_cv_scores = cross_val_score(dt_model, X_train_scaled, y_train, cv=5, scoring='accuracy')
    print(f"Cross-validation scores: {dt_cv_scores}")
    print(f"Mean CV Accuracy: {dt_cv_scores.mean() * 100:.2f}% (+/- {dt_cv_scores.std() * 2 * 100:.2f}%)")
    
    # ============ Random Forest Model ============
    print(f"\n{'='*60}")
    print("2. Training Random Forest Classifier (High Accuracy Model)")
    print(f"{'='*60}")
    
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced',
        n_jobs=-1
    )
    rf_model.fit(X_train_scaled, y_train)
    
    # Evaluate Random Forest
    rf_pred = rf_model.predict(X_test_scaled)
    rf_accuracy = accuracy_score(y_test, rf_pred)
    rf_precision = precision_score(y_test, rf_pred, average='weighted', zero_division=0)
    rf_recall = recall_score(y_test, rf_pred, average='weighted', zero_division=0)
    rf_f1 = f1_score(y_test, rf_pred, average='weighted', zero_division=0)
    
    print(f"\nRandom Forest Results:")
    print(f"Accuracy: {rf_accuracy * 100:.2f}%")
    print(f"Precision: {rf_precision * 100:.2f}%")
    print(f"Recall: {rf_recall * 100:.2f}%")
    print(f"F1-Score: {rf_f1 * 100:.2f}%")
    
    # Cross-validation
    rf_cv_scores = cross_val_score(rf_model, X_train_scaled, y_train, cv=5, scoring='accuracy')
    print(f"Cross-validation scores: {rf_cv_scores}")
    print(f"Mean CV Accuracy: {rf_cv_scores.mean() * 100:.2f}% (+/- {rf_cv_scores.std() * 2 * 100:.2f}%)")
    
    # ============ Model Comparison ============
    print(f"\n{'='*60}")
    print("Model Comparison Summary")
    print(f"{'='*60}")
    comparison_df = pd.DataFrame({
        'Model': ['Decision Tree', 'Random Forest'],
        'Accuracy': [dt_accuracy, rf_accuracy],
        'Precision': [dt_precision, rf_precision],
        'Recall': [dt_recall, rf_recall],
        'F1-Score': [dt_f1, rf_f1]
    })
    print(comparison_df.to_string(index=False))
    
    # Select best model
    best_model = rf_model if rf_accuracy > dt_accuracy else dt_model
    best_model_name = "Random Forest" if rf_accuracy > dt_accuracy else "Decision Tree"
    
    print(f"\n🏆 Best Model: {best_model_name}")
    print(f"Best Accuracy: {max(dt_accuracy, rf_accuracy) * 100:.2f}%")
    
    # Detailed classification report for best model
    best_pred = rf_pred if rf_accuracy > dt_accuracy else dt_pred
    print(f"\nDetailed Classification Report ({best_model_name}):")
    print(classification_report(y_test, best_pred, 
                                target_names=target_encoder.classes_,
                                zero_division=0))
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, best_pred)
    print(f"\nConfusion Matrix ({best_model_name}):")
    print(cm)
    
    return {
        'decision_tree': dt_model,
        'random_forest': rf_model,
        'best_model': best_model,
        'best_model_name': best_model_name,
        'scaler': scaler,
        'feature_names': feature_names,
        'X_train': X_train_scaled,
        'X_test': X_test_scaled,
        'y_train': y_train,
        'y_test': y_test,
        'metrics': {
            'dt_accuracy': dt_accuracy,
            'rf_accuracy': rf_accuracy,
            'best_accuracy': max(dt_accuracy, rf_accuracy)
        }
    }

def generate_shap_explanations(models_dict, target_encoder):
    """Generate SHAP explanations for model interpretability"""
    
    print(f"\n{'='*60}")
    print("Generating SHAP Explanations (Explainable AI)")
    print(f"{'='*60}")
    
    best_model = models_dict['best_model']
    X_train = models_dict['X_train']
    X_test = models_dict['X_test']
    feature_names = models_dict['feature_names']
    
    try:
        # Create SHAP explainer
        print("\nCreating SHAP Tree Explainer...")
        explainer = shap.TreeExplainer(best_model)
        
        # Calculate SHAP values for test set (sample for efficiency)
        sample_size = min(100, len(X_test))
        X_test_sample = X_test[:sample_size]
        
        print(f"Calculating SHAP values for {sample_size} samples...")
        shap_values = explainer.shap_values(X_test_sample)
        
        # Save SHAP explainer and values
        shap_data = {
            'explainer': explainer,
            'shap_values': shap_values,
            'X_test_sample': X_test_sample,
            'feature_names': feature_names,
            'base_value': explainer.expected_value
        }
        
        print("\n✓ SHAP explanations generated successfully!")
        print(f"✓ Base value (expected prediction): {explainer.expected_value}")
        print(f"✓ Feature importance calculated for {len(feature_names)} features")
        
        # Feature importance from SHAP
        if isinstance(shap_values, list):
            # Multi-class case
            shap_importance = np.abs(shap_values[1]).mean(axis=0)
        else:
            shap_importance = np.abs(shap_values).mean(axis=0)
        
        feature_importance = pd.DataFrame({
            'feature': feature_names,
            'importance': shap_importance
        }).sort_values('importance', ascending=False)
        
        print(f"\nTop 10 Most Important Features (SHAP):")
        print(feature_importance.head(10).to_string(index=False))
        
        return shap_data
        
    except Exception as e:
        print(f"\n⚠ Warning: Could not generate SHAP explanations: {e}")
        print("Model will still work, but XAI features will be limited.")
        return None

def save_models(models_dict, target_encoder, label_encoders, shap_data):
    """Save all trained models and preprocessors"""
    
    print(f"\n{'='*60}")
    print("Saving Models and Artifacts")
    print(f"{'='*60}")
    
    ml_dir = SCRIPT_DIR
    os.makedirs(ml_dir, exist_ok=True)
    
    # Save Decision Tree model
    dt_path = os.path.join(ml_dir, 'ckd_decision_tree.pkl')
    with open(dt_path, 'wb') as f:
        pickle.dump(models_dict['decision_tree'], f)
    print(f"✓ Decision Tree saved to: {dt_path}")
    
    # Save Random Forest model
    rf_path = os.path.join(ml_dir, 'ckd_random_forest.pkl')
    with open(rf_path, 'wb') as f:
        pickle.dump(models_dict['random_forest'], f)
    print(f"✓ Random Forest saved to: {rf_path}")
    
    # Save best model separately
    best_model_path = os.path.join(ml_dir, 'ckd_best_model.pkl')
    with open(best_model_path, 'wb') as f:
        pickle.dump(models_dict['best_model'], f)
    print(f"✓ Best Model saved to: {best_model_path}")
    
    # Save scaler
    scaler_path = os.path.join(ml_dir, 'ckd_scaler.pkl')
    with open(scaler_path, 'wb') as f:
        pickle.dump(models_dict['scaler'], f)
    print(f"✓ Scaler saved to: {scaler_path}")
    
    # Save target encoder
    target_encoder_path = os.path.join(ml_dir, 'ckd_target_encoder.pkl')
    with open(target_encoder_path, 'wb') as f:
        pickle.dump(target_encoder, f)
    print(f"✓ Target Encoder saved to: {target_encoder_path}")
    
    # Save label encoders
    label_encoders_path = os.path.join(ml_dir, 'ckd_label_encoders.pkl')
    with open(label_encoders_path, 'wb') as f:
        pickle.dump(label_encoders, f)
    print(f"✓ Label Encoders saved to: {label_encoders_path}")
    
    # Save feature names
    feature_names_path = os.path.join(ml_dir, 'ckd_feature_names.pkl')
    with open(feature_names_path, 'wb') as f:
        pickle.dump(models_dict['feature_names'], f)
    print(f"✓ Feature Names saved to: {feature_names_path}")
    
    # Save SHAP data if available
    if shap_data:
        shap_path = os.path.join(ml_dir, 'ckd_shap_explainer.pkl')
        with open(shap_path, 'wb') as f:
            pickle.dump(shap_data, f)
        print(f"✓ SHAP Explainer saved to: {shap_path}")
    
    # Save model metadata
    metadata = {
        'best_model_name': models_dict['best_model_name'],
        'feature_names': models_dict['feature_names'],
        'metrics': models_dict['metrics'],
        'target_classes': target_encoder.classes_.tolist(),
        'shap_available': shap_data is not None
    }
    metadata_path = os.path.join(ml_dir, 'ckd_model_metadata.pkl')
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)
    print(f"✓ Model Metadata saved to: {metadata_path}")

def test_prediction(models_dict, scaler, target_encoder, feature_names):
    """Test the model with sample data"""
    
    print(f"\n{'='*60}")
    print("Testing CKD Prediction with Sample Data")
    print(f"{'='*60}")
    
    # Sample test cases (using median values from dataset with variations)
    test_cases = [
        {
            'name': 'Healthy Individual',
            'data': [50, 80, 1.020, 0, 0, 120, 30, 1.0, 140, 4.0, 14.0, 44, 8000, 5.0,
                    1, 1, 0, 0, 0, 0, 0, 1, 0, 0]  # Normal values
        },
        {
            'name': 'CKD Patient (Stage 3)',
            'data': [65, 90, 1.015, 2, 0, 180, 60, 2.5, 135, 4.5, 10.0, 32, 9000, 3.8,
                    0, 0, 0, 0, 1, 1, 0, 0, 1, 1]  # Elevated values
        },
        {
            'name': 'CKD Patient (Advanced)',
            'data': [70, 100, 1.010, 4, 3, 300, 120, 5.0, 130, 6.0, 7.0, 25, 12000, 3.0,
                    0, 0, 1, 1, 1, 1, 1, 0, 1, 1]  # Severe abnormalities
        }
    ]
    
    best_model = models_dict['best_model']
    
    for test_case in test_cases:
        print(f"\n{'='*40}")
        print(f"Test Case: {test_case['name']}")
        print(f"{'='*40}")
        
        # Prepare data
        X_sample = np.array([test_case['data']])
        X_sample_scaled = scaler.transform(X_sample)
        
        # Predict
        prediction = best_model.predict(X_sample_scaled)
        prediction_proba = best_model.predict_proba(X_sample_scaled)
        
        predicted_class = target_encoder.inverse_transform(prediction)[0]
        confidence = max(prediction_proba[0]) * 100
        
        print(f"Prediction: {predicted_class.upper()}")
        print(f"Confidence: {confidence:.2f}%")
        print(f"Probabilities:")
        for i, class_name in enumerate(target_encoder.classes_):
            print(f"  - {class_name}: {prediction_proba[0][i] * 100:.2f}%")

def main():
    """Main function to train and save CKD prediction models"""
    
    print("="*80)
    print("CKD (Chronic Kidney Disease) Prediction System")
    print("ML Model Training with Explainable AI (SHAP)")
    print("="*80)
    
    # Load and preprocess data
    df, label_encoders, target_encoder = load_and_preprocess_ckd_data()
    
    # Train models
    models_dict = train_models(df, target_encoder)
    
    # Generate SHAP explanations
    shap_data = generate_shap_explanations(models_dict, target_encoder)
    
    # Save models
    save_models(models_dict, target_encoder, label_encoders, shap_data)
    
    # Test predictions
    test_prediction(models_dict, models_dict['scaler'], 
                   target_encoder, models_dict['feature_names'])
    
    print("\n" + "="*80)
    print("✓ CKD Model Training Completed Successfully!")
    print("✓ Models are ready for deployment")
    print("✓ Explainable AI (SHAP) is integrated")
    print("="*80)

if __name__ == "__main__":
    main()
