"""
Disease Prediction Model Training Script
Smart Patient Healthcare System

This script trains a Multinomial Naive Bayes classifier to predict diseases
based on symptoms. The model is saved using pickle for later use in production.

Why Naive Bayes?
1. Works well with text/categorical data
2. Fast training and prediction
3. Performs well even with limited training data
4. Good baseline for medical classification tasks
5. Provides probability estimates for predictions
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os
import sys

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))

def load_and_preprocess_data():
    """Load and preprocess the symptom-disease dataset"""
    
    # Load the dataset
    dataset_path = os.path.join(PROJECT_DIR, 'dataset.csv')
    print(f"Loading dataset from: {dataset_path}")
    
    df = pd.read_csv(dataset_path)
    print(f"Dataset shape: {df.shape}")
    print(f"Diseases found: {df['Disease'].nunique()}")
    
    # Combine all symptom columns into a single text column
    symptom_cols = [col for col in df.columns if 'Symptom' in col]
    
    def combine_symptoms(row):
        symptoms = []
        for col in symptom_cols:
            if pd.notna(row[col]) and str(row[col]).strip():
                symptom = str(row[col]).strip().lower().replace(' ', '_')
                symptoms.append(symptom)
        return ' '.join(symptoms)
    
    df['symptoms_text'] = df.apply(combine_symptoms, axis=1)
    
    # Remove rows with empty symptoms
    df = df[df['symptoms_text'].str.strip() != '']
    
    print(f"Dataset after preprocessing: {df.shape}")
    print(f"\nSample data:")
    print(df[['Disease', 'symptoms_text']].head())
    
    return df

def train_model(df):
    """Train the Naive Bayes model"""
    
    # Prepare features and labels
    X = df['symptoms_text']
    y = df['Disease']
    
    # Encode labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    print(f"\nNumber of classes: {len(label_encoder.classes_)}")
    print(f"Classes: {list(label_encoder.classes_)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    print(f"\nTraining set size: {len(X_train)}")
    print(f"Test set size: {len(X_test)}")
    
    # Create CountVectorizer
    vectorizer = CountVectorizer(
        lowercase=True,
        token_pattern=r'[a-z_]+',
        max_features=500
    )
    
    # Fit and transform training data
    X_train_vectorized = vectorizer.fit_transform(X_train)
    X_test_vectorized = vectorizer.transform(X_test)
    
    print(f"\nVocabulary size: {len(vectorizer.vocabulary_)}")
    
    # Train Multinomial Naive Bayes
    print("\nTraining Multinomial Naive Bayes classifier...")
    model = MultinomialNB(alpha=1.0)
    model.fit(X_train_vectorized, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_vectorized)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n{'='*50}")
    print(f"Model Accuracy: {accuracy * 100:.2f}%")
    print(f"{'='*50}")
    
    # Detailed classification report
    print("\nClassification Report:")
    y_test_labels = label_encoder.inverse_transform(y_test)
    y_pred_labels = label_encoder.inverse_transform(y_pred)
    print(classification_report(y_test_labels, y_pred_labels, zero_division=0))
    
    return model, vectorizer, label_encoder

def save_model(model, vectorizer, label_encoder):
    """Save the trained model and preprocessors"""
    
    # Create ml directory if it doesn't exist
    ml_dir = SCRIPT_DIR
    os.makedirs(ml_dir, exist_ok=True)
    
    # Save model
    model_path = os.path.join(ml_dir, 'model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"\nModel saved to: {model_path}")
    
    # Save vectorizer
    vectorizer_path = os.path.join(ml_dir, 'vectorizer.pkl')
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    print(f"Vectorizer saved to: {vectorizer_path}")
    
    # Save label encoder
    label_encoder_path = os.path.join(ml_dir, 'label_encoder.pkl')
    with open(label_encoder_path, 'wb') as f:
        pickle.dump(label_encoder, f)
    print(f"Label encoder saved to: {label_encoder_path}")

def test_prediction(model, vectorizer, label_encoder):
    """Test the model with sample symptoms"""
    
    print("\n" + "="*50)
    print("Testing predictions with sample symptoms:")
    print("="*50)
    
    test_cases = [
        "itching skin_rash nodal_skin_eruptions",
        "continuous_sneezing shivering chills",
        "stomach_pain acidity ulcers_on_tongue vomiting",
        "chest_pain breathlessness sweating",
        "fatigue weight_loss restlessness high_fever"
    ]
    
    for symptoms in test_cases:
        symptoms_vec = vectorizer.transform([symptoms])
        prediction = model.predict(symptoms_vec)
        proba = model.predict_proba(symptoms_vec)
        disease = label_encoder.inverse_transform(prediction)[0]
        confidence = max(proba[0]) * 100
        
        print(f"\nSymptoms: {symptoms}")
        print(f"Predicted Disease: {disease}")
        print(f"Confidence: {confidence:.2f}%")

def main():
    """Main function to train and save the model"""
    
    print("="*60)
    print("Smart Patient Healthcare System - ML Model Training")
    print("="*60)
    
    # Load and preprocess data
    df = load_and_preprocess_data()
    
    # Train model
    model, vectorizer, label_encoder = train_model(df)
    
    # Save model
    save_model(model, vectorizer, label_encoder)
    
    # Test predictions
    test_prediction(model, vectorizer, label_encoder)
    
    print("\n" + "="*60)
    print("Model training completed successfully!")
    print("="*60)

if __name__ == "__main__":
    main()
