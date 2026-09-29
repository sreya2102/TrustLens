import pytest
import os
import numpy as np
from backend.app.services.ml_service import (
    preprocess_text,
    fallback_lemmatize,
    load_models,
    predict_webpage_ml,
    LR_MODEL_PATH,
    MLP_MODEL_PATH,
    TFIDF_PATH
)

def test_preprocessing_conversions():
    """Verify raw text is lowercased and numbers are removed."""
    assert preprocess_text("HURRY 123 SALE") == "hurry sale"
    assert preprocess_text("1 2 34567 8") == ""

def test_preprocessing_punctuation():
    """Verify punctuation is stripped and replaced with whitespace."""
    assert preprocess_text("hurry-up! free_trial.") == "hurry free trial"
    assert preprocess_text("claim reward; double income...") == "claim reward double income"

def test_preprocessing_stopwords():
    """Verify stop words from the custom list are filtered."""
    assert preprocess_text("this is a free trial for you and me") == "free trial"
    assert preprocess_text("about against between further once") == ""

def test_lemmatizer_fallback():
    """Verify lemmatization rules match expected TypeScript output."""
    assert fallback_lemmatize("hurries") == "hurry"
    assert fallback_lemmatize("renewals") == "renewal"
    assert fallback_lemmatize("calls") == "call"
    assert fallback_lemmatize("class") == "class"  # Ends with 'ss' - should not strip
    assert fallback_lemmatize("us") == "us"        # Too short - should not strip

def test_models_exist():
    """Verify trained model binary files exist in backend/app/ml/."""
    assert os.path.exists(LR_MODEL_PATH)
    assert os.path.exists(MLP_MODEL_PATH)
    assert os.path.exists(TFIDF_PATH)

def test_model_loading():
    """Verify global model caches are populated successfully."""
    load_models()
    from backend.app.services import ml_service
    assert ml_service.tfidf is not None
    assert ml_service.lr_model is not None
    assert ml_service.mlp_model is not None

def test_lr_predictions():
    """Verify Logistic Regression outputs realistic classifications and probabilities."""
    res = predict_webpage_ml("Hurry up! Free trial! Instant approval!", active_model_type="logistic_regression")
    assert res["prediction"] in ["Safe", "Caution", "Risky"]
    assert res["confidence"] >= 0.0 and res["confidence"] <= 1.0
    assert "Safe" in res["probabilities"]
    assert "Risky" in res["probabilities"]
    assert res["modelName"] == "Logistic Regression"
    assert res["modelVersion"] == "1.0.0"

def test_mlp_predictions():
    """Verify MLP Neural Net outputs realistic classifications and latency numbers."""
    res = predict_webpage_ml("Hurry up! Free trial! Instant approval!", active_model_type="minilm_neural_net")
    assert res["prediction"] in ["Safe", "Caution", "Risky"]
    assert res["modelName"] == "MiniLM Neural Net (MLP)"
    assert res["modelVersion"] == "1.1.0-neural"
    assert res["modelLatency"] > 0.0
    assert res["modelMemory"] > 0.0

def test_xai_influential_words():
    """Verify Explainable AI extracts correct features contributing to risk."""
    text = "Hurry up! Instant approval!"
    res = predict_webpage_ml(text, active_model_type="logistic_regression")
    words = res["influentialWords"]
    assert isinstance(words, list)
    # The extracted words should be present in the preprocessed text
    preprocessed_text = preprocess_text(text)
    for w in words:
        assert w in preprocessed_text

def test_xai_safetab_fallback():
    """Verify XAI extracts valid features even for Safe pages."""
    text = "This is a normal legal document explaining generic terms."
    res = predict_webpage_ml(text, active_model_type="logistic_regression")
    assert isinstance(res["influentialWords"], list)

@pytest.mark.parametrize("model_type", ["logistic_regression", "minilm_neural_net"])
def test_performance_metrics(model_type):
    """Verify that latency is tracked and RAM footprints are calculated correctly."""
    res = predict_webpage_ml("Flash sales, buy now!", active_model_type=model_type)
    assert "modelLatency" in res
    assert "modelMemory" in res
    assert res["modelLatency"] >= 0.0
    assert res["modelMemory"] > 0.0


@pytest.mark.parametrize("word, expected_lemma", [
    ("cookies", "cooky"),
    ("companies", "company"),
    ("partners", "partner"),
    ("technologies", "technology"),
    ("buttons", "button"),
    ("headings", "heading"),
    ("reasons", "reason"),
    ("rules", "rule"),
    ("scams", "scam"),
    ("patterns", "pattern"),
    ("clicks", "click"),
    ("scarcities", "scarcity"),
    ("urgencies", "urgency"),
    ("renewals", "renewal"),
    ("subscriptions", "subscription"),
    ("loans", "loan"),
    ("guarantees", "guarantee"),
    ("returns", "return"),
    ("trackers", "tracker"),
    ("disclosures", "disclosure")
])
def test_lemmatizer_cases(word, expected_lemma):
    """Verify lemmatizer rules produce standard stems on plural/ies forms."""
    assert fallback_lemmatize(word) == expected_lemma
