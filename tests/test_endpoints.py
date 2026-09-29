import pytest
import os
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.main import app
from backend.app.database.connection import get_db, Base
from backend.app.models.models import ModelInfo, ScanHistory, User, Feedback

# Isolated SQLite database for testing API routers
TEST_DB_URL = "sqlite:///./test_endpoints.db"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """DB session override helper."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Hook override session dependency
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True, name="db_setup")
def fixture_db_setup():
    """Setup and teardown local test databases."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Seed model metadata for endpoint checks
    if db.query(ModelInfo).count() == 0:
        seed = ModelInfo(
            version="1.0.0",
            accuracy=1.0,
            precision=1.0,
            recall=1.0,
            f1_score=1.0,
            trained_date="2026-07-14"
        )
        db.add(seed)
        db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    # Remove database file if it exists
    if os.path.exists("test_endpoints.db"):
        try:
            os.remove("test_endpoints.db")
        except Exception:
            pass

def test_health_check():
    """Verify backend health endpoint is online."""
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "online"

def test_api_scan_logistic_regression():
    """Verify scan endpoint outputs values for Logistic Regression model."""
    payload = {
        "pageText": "Hurry up! Flash sale ends in 5 minutes! Only 2 items left.",
        "url": "https://deceptive-deals.com/checkout",
        "title": "Deceptive Checkout",
        "activeModel": "logistic_regression"
      }
    res = client.post("/api/scan", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["scanId"] is not None
    assert data["score"] > 20
    assert data["label"] in ["Caution", "Risky"]
    assert "reasons" in data
    assert data["modelName"] == "Logistic Regression"
    assert data["modelLatency"] >= 0.0
    assert data["modelMemory"] > 0.0
    assert "humanExplanation" in data
    assert len(data["influentialWords"]) > 0

def test_api_scan_mlp_model():
    """Verify scan endpoint routes queries to the MLP classifier."""
    payload = {
        "pageText": "Verify this page. Completely clean.",
        "url": "https://google.com",
        "title": "Google Clean Page",
        "activeModel": "minilm_neural_net"
    }
    res = client.post("/api/scan", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["modelName"] == "MiniLM Neural Net (MLP)"
    assert data["label"] == "Safe"
    assert data["score"] <= 20
    assert data["trustScore"] >= 80

def test_api_scan_privacy_policy_detection():
    """Verify privacy page auto-detection and bullet summary generation."""
    payload = {
        "pageText": "We collect email addresses, names, and phone numbers. We share your personal data with third-party advertising partners for targeted ads. We store your cookies and device information. GDPR user rights include right to delete name.",
        "url": "https://my-site.com/privacy-policy",
        "title": "Our Privacy Statement",
        "activeModel": "logistic_regression"
    }
    res = client.post("/api/scan", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["isPrivacyPolicy"] is True
    assert data["privacySummary"] is not None
    assert "dataCollected" in data["privacySummary"]
    assert "thirdPartySharing" in data["privacySummary"]

def test_api_scan_blacklist_threat():
    """Verify blacklisted scam domains trigger trust score overrides."""
    payload = {
        "pageText": "Completely clean text.",
        "url": "https://scam-shop.com/home",
        "title": "Known Scam Shop",
        "activeModel": "logistic_regression"
    }
    res = client.post("/api/scan", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["reputation"]["isBlacklisted"] is True
    assert data["trustScore"] == 0  # Critical threat blacklist override

def test_api_scan_missing_fields():
    """Verify validation triggers 422 errors when body params are incomplete."""
    res = client.post("/api/scan", json={"url": "http://missing-text.com"})
    assert res.status_code == 422

def test_api_feedback_with_scan_id():
    """Verify feedback logs register correct entries for scan records."""
    # Create fake scan first
    db = TestingSessionLocal()
    scan = ScanHistory(
        url_hash="hashed-url",
        domain="deals.com",
        rule_score=0,
        ml_score=0,
        final_score=0,
        risk_label="Safe"
    )
    db.add(scan)
    db.commit()
    scan_id = scan.scan_id
    db.close()

    feedback_payload = {
        "scanId": scan_id,
        "feedbackType": "correct",
        "comment": "Nice scan details"
    }
    res = client.post("/api/feedback", json=feedback_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["scanId"] == scan_id
    assert data["feedbackType"] == "correct"

def test_api_feedback_missing_scan_id_fallback():
    """Verify local scan feedback automatically logs scan histories first."""
    feedback_payload = {
        "feedbackType": "wrong",
        "comment": "Scan was caution but local showed safe",
        "url": "https://fallback-scanned.com",
        "title": "Local Scanned Site",
        "ruleScore": 10,
        "mlScore": 15,
        "finalScore": 12,
        "riskLabel": "Safe"
    }
    res = client.post("/api/feedback", json=feedback_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["scanId"] is not None  # Automatically seeded scanId
    assert data["feedbackType"] == "wrong"

def test_api_feedback_invalid_missing_url():
    """Verify bad requests are blocked when scan ID and URL are both absent."""
    res = client.post("/api/feedback", json={"feedbackType": "correct"})
    assert res.status_code == 400

def test_api_model_info():
    """Verify version endpoint fetches seeded parameters."""
    res = client.get("/api/model")
    assert res.status_code == 200
    data = res.json()
    assert data["version"] == "1.0.0"
    assert data["accuracy"] == 1.0

def test_api_stats():
    """Verify dashboard aggregator tallies scan counts and categorizations."""
    # Seed 2 scans and 1 feedback
    db = TestingSessionLocal()
    scan1 = ScanHistory(url_hash="h1", domain="google.com", rule_score=10, ml_score=10, final_score=10, risk_label="Safe", matched_keywords_json='[]')
    scan2 = ScanHistory(url_hash="h2", domain="scam.com", rule_score=60, ml_score=70, final_score=65, risk_label="Risky", matched_keywords_json='[{"keyword":"win cash", "category":"FINANCIAL_MANIPULATION", "count":2}]')
    db.add(scan1)
    db.add(scan2)
    db.commit()
    
    feedback = Feedback(scan_id=scan2.scan_id, feedback_type="correct")
    db.add(feedback)
    db.commit()
    db.close()

    res = client.get("/api/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["totalScans"] == 2
    assert data["riskDistribution"]["Safe"] == 1
    assert data["riskDistribution"]["Risky"] == 1
    assert data["feedbackDistribution"]["correct"] == 1
    assert len(data["mostCommonKeywords"]) == 1
    assert data["mostCommonKeywords"][0]["keyword"] == "win cash"
    assert data["averageScore"] == 37.5  # (10 + 65) / 2
