import os
import hashlib
import json
from urllib.parse import urlparse
from datetime import datetime, timedelta
from collections import Counter
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from ..database.connection import get_db
from ..models.models import User, ScanHistory, Feedback, ModelInfo
from ..schemas import schemas
from ..services.rules_service import analyze_text_rules
from ..services.ml_service import predict_webpage_ml
from ..services.privacy_summarizer import detect_privacy_policy, summarize_privacy_policy
from ..services.reputation_service import evaluate_website_reputation, calculate_unified_trust_score

router = APIRouter(prefix="/api")

# Debugging Mode Config: If set to True/1, the full text of analyzed pages is stored.
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1", "yes")

def hash_url(url: str) -> str:
    """Helper to hash URLs using SHA-256 for privacy."""
    return hashlib.sha256(url.encode("utf-8")).hexdigest()

def extract_domain(url: str) -> str:
    """Helper to extract domain name from a URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        # Clean up port names if present (e.g. localhost:8000 -> localhost)
        if ":" in domain:
            domain = domain.split(":")[0]
        return domain if domain else "unknown"
    except Exception:
        return "unknown"


def generate_human_explanation(matched_keywords, ml_prediction, risk_label):
    """Generates a contextual, human-readable summary of risk findings."""
    if risk_label == "Safe" and not matched_keywords:
        return "This webpage does not present significant manipulation risks, scam indicators, or privacy-intrusive patterns."
    
    categories = {k["category"] for k in matched_keywords}
    desc_map = {
        "URGENCY": "manipulative urgency language",
        "SCARCITY": "artificial scarcity tactics",
        "SUBSCRIPTION_TRAP": "subscription trap wording",
        "PRIVACY_RISK": "privacy risks (data collection or third-party sharing details)",
        "FINANCIAL_MANIPULATION": "financial pressure language or aggressive quick-gain assertions"
    }
    matched_descs = [desc_map[c] for c in categories if c in desc_map]
    
    if not matched_descs:
        if ml_prediction != "Safe":
            return f"This webpage contains semantic patterns associated with {ml_prediction.lower()}-risk sites."
        return "This webpage is classified as safe with minimal risk indicators."
        
    explanation = "This webpage contains "
    if len(matched_descs) == 1:
        explanation += matched_descs[0] + "."
    elif len(matched_descs) == 2:
        explanation += f"{matched_descs[0]} and {matched_descs[1]}."
    else:
        explanation += ", ".join(matched_descs[:-1]) + f", and {matched_descs[-1]}."
        
    # Append the AI verdict context
    if ml_prediction != "Safe":
        explanation += f" Furthermore, the AI model has flagged this page as {ml_prediction.lower()}."
        
    return explanation


@router.post("/scan", response_model=schemas.ScanResponse)
def scan_page(req: schemas.ScanRequest, db: Session = Depends(get_db)):
    """
    POST /api/scan
    Scans the webpage text using Rule-Based Risk Detection and the Machine Learning Classifier.
    """
    # 1. Lexical Scoring Engine (Rule Engine)
    rule_results = analyze_text_rules(req.page_text)
    rule_score = rule_results["score"]
    
    # 2. Machine Learning Classification (with dynamic model routing)
    ml_results = predict_webpage_ml(req.page_text, req.active_model)
    ml_prediction = ml_results["prediction"]
    ml_confidence = ml_results["confidence"]
    probs = ml_results["probabilities"]
    
    # ML Score calculation continuous scaling: P(Caution)*50 + P(Risky)*100
    ml_score = round(probs.get("Caution", 0.0) * 50 + probs.get("Risky", 0.0) * 100)
    
    # Combine scores: 60% rule engine + 40% ML prediction
    final_score = round(0.6 * rule_score + 0.4 * ml_score)
    
    # Determine risk label based on thresholds
    risk_label = "Safe"
    if final_score > 50:
        risk_label = "Risky"
    elif final_score > 20:
        risk_label = "Caution"

    # Combine explainability reasons
    reasons = list(rule_results["reasons"])
    if ml_prediction != "Safe":
        pct = round(ml_confidence * 100)
        reasons.append(f"🤖 ML Model predicted {ml_prediction} ({pct}% confidence)")

    # Generate human explanation
    human_explanation = generate_human_explanation(rule_results["matchedKeywords"], ml_prediction, risk_label)

    # 3. Privacy Policy detection and parsing
    is_privacy_policy = detect_privacy_policy(req.url, req.title, req.page_text)
    privacy_summary = summarize_privacy_policy(req.page_text) if is_privacy_policy else None

    # 4. Domain Reputation Evaluation & trust score blend
    reputation_data = evaluate_website_reputation(req.url)
    trust_score = calculate_unified_trust_score(final_score, reputation_data)

    # Prepare database records
    hashed_url = hash_url(req.url)
    domain_name = extract_domain(req.url)
    
    # Silent user registration/validation if user_id is provided
    if req.user_id:
        user_record = db.query(User).filter(User.user_id == req.user_id).first()
        if not user_record:
            user_record = User(user_id=req.user_id)
            db.add(user_record)
            db.commit()

    # Save to ScanHistory (note: we store trust_score in DB final_score or keep final_score as dark-pattern risk)
    scan_history = ScanHistory(
        user_id=req.user_id,
        url_hash=hashed_url,
        domain=domain_name,
        page_title=req.title,
        rule_score=rule_score,
        ml_score=ml_score,
        final_score=final_score,
        risk_label=risk_label,
        matched_keywords_json=json.dumps(rule_results["matchedKeywords"]),
        page_text=req.page_text if DEBUG_MODE else None,
        timestamp=datetime.utcnow()
    )
    
    db.add(scan_history)
    db.commit()
    db.refresh(scan_history)

    # Return standardized response compatible with extension
    return {
        "scanId": scan_history.scan_id,
        "url": req.url,
        "title": req.title,
        "score": final_score,
        "label": risk_label,
        "matchedKeywords": rule_results["matchedKeywords"],
        "reasons": reasons,
        "timestamp": scan_history.timestamp.strftime("%m/%d/%Y, %I:%M:%S %p"),
        "ruleScore": rule_score,
        "mlScore": ml_score,
        "mlPrediction": ml_prediction,
        "mlConfidence": ml_confidence,
        "modelName": ml_results["modelName"],
        "modelVersion": ml_results["modelVersion"],
        "modelAccuracy": ml_results["modelAccuracy"],
        "modelLatency": ml_results["modelLatency"],
        "modelMemory": ml_results["modelMemory"],
        "humanExplanation": human_explanation,
        "influentialWords": ml_results["influentialWords"],
        "isPrivacyPolicy": is_privacy_policy,
        "privacySummary": privacy_summary,
        "reputation": reputation_data,
        "trustScore": trust_score
    }


@router.post("/feedback", response_model=schemas.FeedbackResponse)
def submit_feedback(req: schemas.FeedbackRequest, db: Session = Depends(get_db)):
    """
    POST /api/feedback
    Stores user feedback (correct/wrong scan classification).
    Supports logging localized fallback scans (from Local analysis) on-the-fly.
    """
    scan_id = req.scan_id

    # Fallback log creation for offline/local scans
    if not scan_id:
        if not req.url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either a valid scanId or URL metadata must be provided for feedback logging."
            )
            
        hashed_url = hash_url(req.url)
        domain_name = extract_domain(req.url)
        
        # Create scan history placeholder
        scan_history = ScanHistory(
            url_hash=hashed_url,
            domain=domain_name,
            page_title=req.title or "Offline Scanned Webpage",
            rule_score=req.rule_score or 0,
            ml_score=req.ml_score or 0,
            final_score=req.final_score or 0,
            risk_label=req.risk_label or "Safe",
            matched_keywords_json=json.dumps([]),
            page_text=None,
            timestamp=datetime.utcnow()
        )
        db.add(scan_history)
        db.commit()
        db.refresh(scan_history)
        scan_id = scan_history.scan_id

    # Verify scan exists
    scan_record = db.query(ScanHistory).filter(ScanHistory.scan_id == scan_id).first()
    if not scan_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan record with ID {scan_id} does not exist."
        )

    # Save user feedback
    feedback_record = Feedback(
        scan_id=scan_id,
        feedback_type=req.feedback_type,
        comment=req.comment,
        timestamp=datetime.utcnow()
    )
    db.add(feedback_record)
    db.commit()
    db.refresh(feedback_record)

    return feedback_record


@router.get("/model", response_model=schemas.ModelInfoResponse)
def get_model_info(db: Session = Depends(get_db)):
    """
    GET /api/model
    Returns model training parameters, metadata, and validation metrics.
    """
    # Fetch latest model details from the DB
    model_record = db.query(ModelInfo).order_by(ModelInfo.version.desc()).first()
    
    if not model_record:
        # Load from disk modelInfo.json backup
        current_dir = os.path.dirname(os.path.abspath(__file__))
        disk_path = os.path.join(current_dir, "..", "ml", "modelInfo.json")
        try:
            with open(disk_path, "r", encoding="utf-8") as f:
                info = json.load(f)
                return {
                    "version": info.get("version", "1.0.0"),
                    "accuracy": info.get("accuracy", 1.0),
                    "precision": info.get("precision", 1.0),
                    "recall": info.get("recall", 1.0),
                    "f1Score": info.get("f1", 1.0),
                    "trainedDate": info.get("trainingDate", "2026-07-14"),
                    "datasetSize": info.get("datasetSize", 560)
                }
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model parameters metadata is currently unavailable."
            )

    return {
        "version": model_record.version,
        "accuracy": model_record.accuracy,
        "precision": model_record.precision,
        "recall": model_record.recall,
        "f1Score": model_record.f1_score,
        "trainedDate": model_record.trained_date,
        "datasetSize": 560
    }


@router.get("/stats", response_model=schemas.StatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    GET /api/stats
    Computes dashboard KPIs, scan distribution, keyword frequencies, domains list, and feedback logs.
    """
    # 1. Total Scans
    total_scans = db.query(ScanHistory).count()

    # 1b. Average Score
    avg_score = db.query(func.avg(ScanHistory.final_score)).scalar() or 0.0
    average_score = round(float(avg_score), 1)

    # 2. Risk Label Distribution
    safe_cnt = db.query(ScanHistory).filter(ScanHistory.risk_label == "Safe").count()
    caution_cnt = db.query(ScanHistory).filter(ScanHistory.risk_label == "Caution").count()
    risky_cnt = db.query(ScanHistory).filter(ScanHistory.risk_label == "Risky").count()
    
    risk_distribution = {
        "Safe": safe_cnt,
        "Caution": caution_cnt,
        "Risky": risky_cnt
    }

    # 3. Feedback Distribution
    correct_cnt = db.query(Feedback).filter(Feedback.feedback_type == "correct").count()
    wrong_cnt = db.query(Feedback).filter(Feedback.feedback_type == "wrong").count()
    
    feedback_distribution = {
        "correct": correct_cnt,
        "wrong": wrong_cnt
    }

    # 4. Most Common Matched Keywords & Categories
    keyword_counter = Counter()
    category_counter = Counter()
    
    all_scans = db.query(ScanHistory.matched_keywords_json).all()
    for (kw_json,) in all_scans:
        if kw_json:
            try:
                kw_list = json.loads(kw_json)
                for kw in kw_list:
                    keyword_counter[kw["keyword"]] += kw["count"]
                    category_counter[kw["category"]] += kw["count"]
            except Exception:
                pass

    most_common_keywords = [
        {"keyword": k, "count": v} for k, v in keyword_counter.most_common(10)
    ]
    common_categories = [
        {"category": k, "count": v} for k, v in category_counter.most_common()
    ]

    # 5. Top Reported Risky Domains
    top_domains_query = (
        db.query(ScanHistory.domain, func.count(ScanHistory.scan_id).label("count"))
        .group_by(ScanHistory.domain)
        .order_by(func.count(ScanHistory.scan_id).desc())
        .limit(5)
        .all()
    )
    top_domains = [{"domain": d, "count": c} for d, c in top_domains_query]

    # 6. Daily Scans count (Last 7 Days)
    daily = {}
    today = datetime.utcnow().date()
    for i in range(7):
        day = today - timedelta(days=i)
        daily[day.strftime("%Y-%m-%d")] = 0

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_scans_date = db.query(ScanHistory.timestamp).filter(ScanHistory.timestamp >= seven_days_ago).all()
    
    for (ts,) in recent_scans_date:
        d_str = ts.date().strftime("%Y-%m-%d")
        if d_str in daily:
            daily[d_str] += 1
            
    daily_scans = [{"date": k, "count": v} for k, v in sorted(daily.items())]

    # 7. Recent Scans (Last 10 Scans)
    recent_scans = []
    scans_query = db.query(ScanHistory).order_by(ScanHistory.timestamp.desc()).limit(10).all()
    
    for scan in scans_query:
        # Check if there are feedback ratings
        feedback_types = [f.feedback_type for f in scan.feedbacks]
        user_feedback = feedback_types[0] if feedback_types else None

        recent_scans.append({
            "scanId": scan.scan_id,
            "domain": scan.domain,
            "title": scan.page_title or "No Title",
            "finalScore": scan.final_score,
            "riskLabel": scan.risk_label,
            "feedback": user_feedback,
            "timestamp": scan.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })

    return {
        "totalScans": total_scans,
        "averageScore": average_score,
        "riskDistribution": risk_distribution,
        "mostCommonKeywords": most_common_keywords,
        "feedbackDistribution": feedback_distribution,
        "recentScans": recent_scans,
        "dailyScans": daily_scans,
        "commonCategories": common_categories,
        "topDomains": top_domains
    }
