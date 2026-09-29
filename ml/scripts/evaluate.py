import os
import sys
import time
import joblib
import pandas as pd
import numpy as np

from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    roc_curve,
    auc
)
from sklearn.preprocessing import label_binarize

# Check if matplotlib is available for charts, fallback silently if not
_HAS_MATPLOTLIB = True
try:
    import matplotlib.pyplot as plt
except ImportError:
    _HAS_MATPLOTLIB = False

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
DATA_PATH = os.path.join(BASE_DIR, "data", "dataset.csv")
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
LR_MODEL_PATH = os.path.join(EXPORTS_DIR, "best_model.pkl")
TFIDF_PATH = os.path.join(EXPORTS_DIR, "tfidf.pkl")

# Import the custom training preprocessor
sys.path.append(SCRIPTS_DIR)
try:
    from preprocess import preprocess_text
except ImportError:
    # Minimal fallback text cleaner
    def preprocess_text(text):
        import re
        import string
        if not isinstance(text, str):
            return ""
        text = text.lower()
        text = re.sub(r'\b\d+\b', ' ', text)
        text = text.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))
        return " ".join(text.split())

def main():
    print("Starting Model Evaluation...")
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    
    # 1. Load Data
    if not os.path.exists(DATA_PATH):
        print(f"Error: Dataset not found at {DATA_PATH}")
        return
        
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded dataset containing {len(df)} records.")
    
    # Preprocess text
    df['clean_text'] = df['page_text'].apply(preprocess_text).fillna('')
    
    # Encode label mapping
    label_map = {"Safe": 0, "Caution": 1, "Risky": 2}
    y = df['label'].map(label_map).values
    
    # 2. Load trained vectorizer and model
    if not os.path.exists(LR_MODEL_PATH) or not os.path.exists(TFIDF_PATH):
        print("Error: Model or TF-IDF pickle is missing in exports.")
        return
        
    vectorizer = joblib.load(TFIDF_PATH)
    model = joblib.load(LR_MODEL_PATH)
    
    # 3. Vectorize text and predict
    X = vectorizer.transform(df['clean_text'])
    
    start_time = time.perf_counter()
    y_pred = model.predict(X)
    y_prob = model.predict_proba(X)
    end_time = time.perf_counter()
    
    avg_latency_ms = ((end_time - start_time) / len(df)) * 1000
    
    # 4. Compute Metrics
    acc = accuracy_score(y, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y, y_pred, average='weighted')
    cm = confusion_matrix(y, y_pred)
    
    # Compute FPR/FNR for Caution/Risky combined (as positive class) vs Safe (as negative)
    # Safe class is 0, Threat classes are 1 and 2
    # Binary confusion matrix:
    # TN: y=0, pred=0
    # FP: y=0, pred in (1,2)
    # FN: y in (1,2), pred=0
    # TP: y in (1,2), pred in (1,2)
    y_binary = (y > 0).astype(int)
    y_pred_binary = (y_pred > 0).astype(int)
    bin_cm = confusion_matrix(y_binary, y_pred_binary)
    
    tn, fp, fn, tp = bin_cm.ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    
    print("\n--- Performance Metrics Summary ---")
    print(f"Accuracy                 : {acc:.4%}")
    print(f"Weighted Precision       : {precision:.4%}")
    print(f"Weighted Recall (Sensitivity): {recall:.4%}")
    print(f"Weighted F1 Score        : {f1:.4%}")
    print(f"False Positive Rate (FPR): {fpr:.4%}")
    print(f"False Negative Rate (FNR): {fnr:.4%}")
    print(f"Average Inference Latency: {avg_latency_ms:.4f} ms per page")
    print(f"Confusion Matrix:\n{cm}")
    
    # 5. Export Report Markdown
    report_path = os.path.join(EXPORTS_DIR, "evaluation_report.md")
    report_content = f"""# TrustLens ML Model Evaluation Report

This report summarizes performance metrics and validation diagnostics for the TrustLens AI classifier.

## 1. Overall Performance Metrics

| Metric | Value |
| :--- | :--- |
| **Accuracy** | {acc:.4%} |
| **Precision (Weighted)** | {precision:.4%} |
| **Recall (Sensitivity)** | {recall:.4%} |
| **F1 Score** | {f1:.4%} |
| **False Positive Rate (FPR)** | {fpr:.4%} |
| **False Negative Rate (FNR)** | {fnr:.4%} |
| **Average Inference Latency** | {avg_latency_ms:.4f} ms per page |

## 2. Confusion Matrix

```
Predicted \\ Actual | Safe (0) | Caution (1) | Risky (2)
-------------------|----------|-------------|----------
Safe (0)           |   {cm[0][0]:<6} |   {cm[0][1]:<9} |   {cm[0][2]:<8}
Caution (1)        |   {cm[1][0]:<6} |   {cm[1][1]:<9} |   {cm[1][2]:<8}
Risky (2)          |   {cm[2][0]:<6} |   {cm[2][1]:<9} |   {cm[2][2]:<8}
```

## 3. Classifications Interpretation
- **False Positive Rate (FPR)**: {fpr:.4%}. Measures the proportion of benign/safe pages mistakenly identified as caution or risky threat vectors. Low FPR is critical to prevent user alert fatigue.
- **False Negative Rate (FNR)**: {fnr:.4%}. Measures undetected dark patterns and scam pages. Zero/low FNR guarantees robust protection.
"""
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"Saved evaluation markdown report to {report_path}")
    
    # 6. Plot Charts
    if _HAS_MATPLOTLIB:
        try:
            # Chart 1: Confusion Matrix Visual
            plt.figure(figsize=(6, 5))
            plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
            plt.title("Confusion Matrix")
            plt.colorbar()
            tick_marks = np.arange(3)
            plt.xticks(tick_marks, ["Safe", "Caution", "Risky"])
            plt.yticks(tick_marks, ["Safe", "Caution", "Risky"])
            
            # Print values inside blocks
            thresh = cm.max() / 2.
            for i in range(cm.shape[0]):
                for j in range(cm.shape[1]):
                    plt.text(j, i, format(cm[i, j], 'd'),
                             horizontalalignment="center",
                             color="white" if cm[i, j] > thresh else "black")
            
            plt.ylabel("True Class")
            plt.xlabel("Predicted Class")
            plt.tight_layout()
            cm_chart_path = os.path.join(EXPORTS_DIR, "confusion_matrix.png")
            plt.savefig(cm_chart_path)
            plt.close()
            print(f"Saved confusion matrix chart to {cm_chart_path}")
            
            # Chart 2: ROC Curve (Binarized Multi-class)
            y_bin = label_binarize(y, classes=[0, 1, 2])
            n_classes = 3
            
            plt.figure(figsize=(6, 5))
            colors = ['green', 'orange', 'red']
            labels = ["Safe", "Caution", "Risky"]
            
            for i in range(n_classes):
                fpr_c, tpr_c, _ = roc_curve(y_bin[:, i], y_prob[:, i])
                roc_auc = auc(fpr_c, tpr_c)
                plt.plot(fpr_c, tpr_c, color=colors[i], lw=2,
                         label=f'ROC {labels[i]} (AUC = {roc_auc:.2f})')
                         
            plt.plot([0, 1], [0, 1], 'k--', lw=2)
            plt.xlim([0.0, 1.0])
            plt.ylim([0.0, 1.05])
            plt.xlabel('False Positive Rate')
            plt.ylabel('True Positive Rate')
            plt.title('Receiver Operating Characteristic (ROC) Curves')
            plt.legend(loc="lower right")
            roc_chart_path = os.path.join(EXPORTS_DIR, "roc_curve.png")
            plt.savefig(roc_chart_path)
            plt.close()
            print(f"Saved ROC curve chart to {roc_chart_path}")
        except Exception as chart_err:
            print(f"Chart plotting error: {chart_err}")
    else:
        print("Skipping PNG chart rendering because matplotlib is not installed.")

if __name__ == "__main__":
    main()
