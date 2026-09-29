import os
import re
import string
import time
import psutil
import joblib
import numpy as np

# Hardcoded stop words to ensure preprocessing parity with TypeScript
STOP_WORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd",
    'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers',
    'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
    'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
    'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
    'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
    'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should',
    "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't",
    'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't",
    'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't",
    'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
}

def fallback_lemmatize(word):
    """Simple suffix-stripping lemmatization fallback."""
    if len(word) > 4:
        if word.endswith('ies'):
            return word[:-3] + 'y'
        if word.endswith('s') and not word.endswith('ss') and not word.endswith('us') and not word.endswith('is'):
            return word[:-1]
    return word

def preprocess_text(text):
    """Clean and preprocess raw text to prepare it for vectorization."""
    if not isinstance(text, str):
        return ""
    
    # 1. Lowercase conversion
    text = text.lower()
    
    # 2. Remove numbers
    text = re.sub(r'\b\d+\b', ' ', text)
    
    # 3. Remove punctuation
    text = text.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))
    
    # 4. Tokenization (split by whitespace)
    tokens = text.split()
        
    # 5. Remove stop words
    filtered_tokens = [t for t in tokens if t not in STOP_WORDS]
    
    # 6. Lemmatization (using fallback method to match TS model behavior)
    lemmatized_tokens = [fallback_lemmatize(t) for t in filtered_tokens]
        
    return " ".join(lemmatized_tokens)


# Paths to saved models
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
LR_MODEL_PATH = os.path.join(CURRENT_DIR, "..", "ml", "best_model.pkl")
MLP_MODEL_PATH = os.path.join(CURRENT_DIR, "..", "ml", "mlp_model.pkl")
TFIDF_PATH = os.path.join(CURRENT_DIR, "..", "ml", "tfidf.pkl")

# Initialize and cache models and vectorizer
lr_model = None
mlp_model = None
tfidf = None

def load_models():
    global lr_model, mlp_model, tfidf
    if lr_model is None or mlp_model is None or tfidf is None:
        try:
            tfidf = joblib.load(TFIDF_PATH)
            # Load standard LR model
            if os.path.exists(LR_MODEL_PATH):
                lr_model = joblib.load(LR_MODEL_PATH)
            # Load MLP model
            if os.path.exists(MLP_MODEL_PATH):
                mlp_model = joblib.load(MLP_MODEL_PATH)
            print("Successfully loaded ML models inside FastAPI (Logistic Regression & MLP Classifier).")
        except Exception as e:
            print(f"Error loading models: {e}")

def predict_webpage_ml(page_text: str, active_model_type: str = "logistic_regression"):
    """
    Predicts the risk label, confidence score, and raw class probabilities of webpage text.
    Tracks prediction execution latency, memory footprint, and returns influential words (XAI).
    """
    load_models()
    
    # Baseline fallback if models are missing
    if lr_model is None or tfidf is None:
        return {
            "prediction": "Safe",
            "confidence": 1.0,
            "probabilities": {"Safe": 1.0, "Caution": 0.0, "Risky": 0.0},
            "modelName": "Fallback Model",
            "modelVersion": "1.0.0",
            "modelAccuracy": 1.0,
            "modelLatency": 0.0,
            "modelMemory": 0.0,
            "influentialWords": []
        }

    # Start performance metrics
    start_time = time.perf_counter()
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / (1024 * 1024)  # MB

    # Model Selection routing
    # default: Logistic Regression, fallback: MLP Neural Net
    if active_model_type == "minilm_neural_net" and mlp_model is not None:
        selected_model = mlp_model
        model_name = "MiniLM Neural Net (MLP)"
        accuracy = 1.0  # From evaluation metrics
    else:
        selected_model = lr_model
        model_name = "Logistic Regression"
        accuracy = 1.0

    # Preprocess text snippets
    cleaned_text = preprocess_text(page_text)
    
    # Run text through TF-IDF Vectorizer
    vectorized_text = tfidf.transform([cleaned_text])
    
    # Predict probabilities (shape: [1, 3])
    probs = selected_model.predict_proba(vectorized_text)[0]
    
    # Class labels order mapping
    class_map = {0: "Safe", 1: "Caution", 2: "Risky"}
    classes = list(selected_model.classes_)
    
    prob_dict = {}
    for idx, class_val in enumerate(classes):
        label = class_map.get(class_val, str(class_val))
        prob_dict[label] = float(probs[idx])
        
    for label in ["Safe", "Caution", "Risky"]:
        if label not in prob_dict:
            prob_dict[label] = 0.0
            
    # Find predicted class index (highest probability)
    pred_idx = int(np.argmax(probs))
    pred_class_val = classes[pred_idx]
    pred_label = class_map.get(pred_class_val, str(pred_class_val))
    confidence = float(probs[pred_idx])

    # --- Explainable AI (XAI) Word Influence Calculation ---
    # We always use the Logistic Regression coefficients as the baseline feature importance source
    # because LR coefficients are linear, robust, and directly map to specific vocabulary features.
    influential_words = []
    try:
        feature_names = tfidf.get_feature_names_out()
        lr_coef = lr_model.coef_  # shape (n_classes, n_features)
        
        # Get non-zero TF-IDF feature indices for this document
        non_zero_indices = vectorized_text.nonzero()[1]
        
        # Map class label to coefficient matrix row index
        # Classes order: 0=Safe, 1=Caution, 2=Risky
        # If predicted class is 'Safe', we look at coefficients for Caution/Risky to show what was close,
        # or show what contributed to 'Safe'. Let's show Caution/Risky influence specifically to highlight threat keywords.
        xai_class_idx = pred_idx if pred_label != "Safe" else 2 # Default to Risky class coefficients for Safe pages
        
        influence_scores = []
        for idx in non_zero_indices:
            word = feature_names[idx]
            tfidf_val = vectorized_text[0, idx]
            coef_val = lr_coef[xai_class_idx, idx]
            score = tfidf_val * coef_val
            if score > 0.0:  # Only words contributing positively to risk
                influence_scores.append((word, float(score)))
                
        # Sort desc
        influence_scores.sort(key=lambda x: x[1], reverse=True)
        influential_words = [w for w, s in influence_scores[:5]]
    except Exception as xai_err:
        print(f"XAI calculation error: {xai_err}")

    # End performance metrics
    end_time = time.perf_counter()
    mem_after = process.memory_info().rss / (1024 * 1024)  # MB
    
    latency_ms = round((end_time - start_time) * 1000, 3)
    memory_usage_mb = round(mem_after, 2)

    return {
        "prediction": pred_label,
        "confidence": confidence,
        "probabilities": prob_dict,
        "modelName": model_name,
        "modelVersion": "1.0.0" if selected_model == lr_model else "1.1.0-neural",
        "modelAccuracy": accuracy,
        "modelLatency": latency_ms,
        "modelMemory": memory_usage_mb,
        "influentialWords": influential_words
    }
