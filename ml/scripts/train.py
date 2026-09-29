import os
import json
import datetime
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score

try:
    from xgboost import XGBClassifier
    _HAS_XGB = True
except ImportError:
    _HAS_XGB = False
    print("Warning: xgboost is not installed. XGBoost model will be skipped during comparisons.")

# Import our custom preprocessor
from preprocess import preprocess_text

# Paths configuration
DATA_PATH = "ml/data/dataset.csv"
EXPORTS_DIR = "ml/exports"
SRC_ML_DIR = "src/ml"

os.makedirs(EXPORTS_DIR, exist_ok=True)
os.makedirs(SRC_ML_DIR, exist_ok=True)

def load_and_preprocess_data():
    print(f"Loading dataset from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    print("Preprocessing webpage text snippets...")
    # Clean the page text
    df['cleaned_text'] = df['page_text'].apply(preprocess_text)
    
    # Check for empty text after preprocessing and fill
    df['cleaned_text'] = df['cleaned_text'].fillna('')
    
    return df

def export_model_parameters_to_json(vectorizer, lr_model, classes, filepath_exports, filepath_src):
    """
    Exports the TF-IDF vocabulary, IDF weights, and Logistic Regression coefficients/intercepts
    to a JSON format that can be easily loaded and computed in pure TypeScript.
    """
    print(f"Exporting Logistic Regression and TF-IDF parameters to JSON...")
    
    vocab = vectorizer.vocabulary_
    # Sort vocabulary by feature index to match IDF array and coefficients
    sorted_vocab = sorted(vocab.items(), key=lambda x: x[1])
    vocab_dict = {term: int(idx) for term, idx in sorted_vocab}
    
    idf_list = list(vectorizer.idf_)
    
    # Scikit-learn Logistic Regression coefficients are shape (n_classes, n_features)
    # Intercepts are shape (n_classes,)
    coef_list = lr_model.coef_.tolist()
    intercept_list = lr_model.intercept_.tolist()
    
    # If binary classification, Scikit-learn stores coefficients as a 1D array of shape (1, n_features).
    # We convert it to multi-class equivalent (Safe vs Risky) or standard form.
    # But since we have 3 classes (Safe, Caution, Risky), it is multinomial and already multi-class.
    
    parameters = {
        "model_type": "LogisticRegression",
        "classes": [str(c) for c in classes],
        "vocabulary": vocab_dict,
        "idf": idf_list,
        "coefficients": coef_list,
        "intercepts": intercept_list
    }
    
    # Write to exports directory
    with open(filepath_exports, 'w', encoding='utf-8') as f:
        json.dump(parameters, f, indent=2)
        
    # Write to TypeScript src directory
    with open(filepath_src, 'w', encoding='utf-8') as f:
        json.dump(parameters, f, indent=2)
        
    print(f"Parameters successfully exported to {filepath_exports} and {filepath_src}")

def main():
    # 1. Load dataset
    df = load_and_preprocess_data()
    
    # Map text labels to integers for training
    label_map = {'Safe': 0, 'Caution': 1, 'Risky': 2}
    inv_label_map = {0: 'Safe', 1: 'Caution', 2: 'Risky'}
    df['target'] = df['label'].map(label_map)
    
    X = df['cleaned_text']
    y = df['target']
    
    # 2. Split dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"Split data into training ({len(X_train)} records) and testing ({len(X_test)} records) sets.")
    
    # 3. Feature Engineering: TF-IDF Vectorization
    print("Vectorizing text using TF-IDF...")
    vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2), min_df=2)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # Save TF-IDF Vectorizer pickle
    joblib.dump(vectorizer, os.path.join(EXPORTS_DIR, "tfidf.pkl"))
    print("Saved TF-IDF Vectorizer to exports/tfidf.pkl")
    
    # 4. Model Training & Comparison
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Linear SVM": SVC(kernel='linear', probability=True, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "MiniLM Neural Net": MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)
    }
    
    if _HAS_XGB:
        models["XGBoost"] = XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='mlogloss')
        
    results = {}
    best_f1 = 0
    best_model_name = None
    best_model = None
    
    print("\n--- Model Training & Comparison ---")
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train_vec, y_train)
        
        # Predictions
        y_pred = model.predict(X_test_vec)
        y_prob = model.predict_proba(X_test_vec)
        
        # Metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='weighted')
        rec = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        # ROC AUC
        try:
            roc_auc = roc_auc_score(y_test, y_prob, average='weighted', multi_class='ovr')
        except Exception:
            roc_auc = 0.0
            
        cm = confusion_matrix(y_test, y_pred)
        
        print(f"Accuracy : {acc:.4f}")
        print(f"Precision: {prec:.4f}")
        print(f"Recall   : {rec:.4f}")
        print(f"F1 Score : {f1:.4f}")
        print(f"ROC AUC  : {roc_auc:.4f}")
        print(f"Confusion Matrix:\n{cm}")
        
        results[name] = {
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "roc_auc": roc_auc,
            "model": model
        }
        
        # Track overall best model based on F1 Score
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_model = model

    print(f"\n--- Best Model Selected: {best_model_name} (F1 Score: {best_f1:.4f}) ---")
    
    # 5. Export Best Model Pickle and MLP Model Pickle
    best_model_path = os.path.join(EXPORTS_DIR, "best_model.pkl")
    joblib.dump(best_model, best_model_path)
    print(f"Saved best model pickle to {best_model_path}")
    
    mlp_model_path = os.path.join(EXPORTS_DIR, "mlp_model.pkl")
    joblib.dump(models["MiniLM Neural Net"], mlp_model_path)
    print(f"Saved MLP model pickle to {mlp_model_path}")
    
    # 6. Save model parameters for client-side TS inference (Logistic Regression)
    # To run inference in TS, we need the coefficients of a Logistic Regression model.
    # If Logistic Regression was not selected as the best overall model, we still train it and
    # export its weights to parameters.json, so the offline extension works seamlessly.
    lr_model = models["Logistic Regression"]
    classes_mapped = [inv_label_map[c] for c in lr_model.classes_]
    export_model_parameters_to_json(
        vectorizer, 
        lr_model, 
        classes_mapped,
        os.path.join(EXPORTS_DIR, "model_parameters.json"),
        os.path.join(SRC_ML_DIR, "model_parameters.json")
    )
    
    # 7. Write modelInfo.json
    best_metrics = results[best_model_name]
    model_info = {
        "modelName": best_model_name,
        "trainingDate": datetime.date.today().isoformat(),
        "datasetSize": len(df),
        "accuracy": float(best_metrics["accuracy"]),
        "precision": float(best_metrics["precision"]),
        "recall": float(best_metrics["recall"]),
        "f1": float(best_metrics["f1"]),
        "version": "1.0.0"
    }
    
    for dest_dir in [EXPORTS_DIR, SRC_ML_DIR]:
        with open(os.path.join(dest_dir, "modelInfo.json"), 'w', encoding='utf-8') as f:
            json.dump(model_info, f, indent=2)
            
    print(f"Model information saved to exports/modelInfo.json and src/ml/modelInfo.json")

if __name__ == '__main__':
    main()
