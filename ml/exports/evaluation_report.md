# TrustLens ML Model Evaluation Report

This report summarizes performance metrics and validation diagnostics for the TrustLens AI classifier.

## 1. Overall Performance Metrics

| Metric | Value |
| :--- | :--- |
| **Accuracy** | 100.0000% |
| **Precision (Weighted)** | 100.0000% |
| **Recall (Sensitivity)** | 100.0000% |
| **F1 Score** | 100.0000% |
| **False Positive Rate (FPR)** | 0.0000% |
| **False Negative Rate (FNR)** | 0.0000% |
| **Average Inference Latency** | 0.0019 ms per page |

## 2. Confusion Matrix

```
Predicted \ Actual | Safe (0) | Caution (1) | Risky (2)
-------------------|----------|-------------|----------
Safe (0)           |   120    |   0         |   0       
Caution (1)        |   0      |   220       |   0       
Risky (2)          |   0      |   0         |   220     
```

## 3. Classifications Interpretation
- **False Positive Rate (FPR)**: 0.0000%. Measures the proportion of benign/safe pages mistakenly identified as caution or risky threat vectors. Low FPR is critical to prevent user alert fatigue.
- **False Negative Rate (FNR)**: 0.0000%. Measures undetected dark patterns and scam pages. Zero/low FNR guarantees robust protection.
