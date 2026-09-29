from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    user_id: str = Field(alias="userId")
    email: Optional[str] = None
    privacy_mode: bool = Field(False, alias="privacyMode")

    class Config:
        populate_by_name = True
        from_attributes = True


class UserResponse(BaseModel):
    user_id: str = Field(alias="userId")
    email: Optional[str] = None
    privacy_mode: bool = Field(alias="privacyMode")
    created_at: datetime = Field(alias="createdAt")

    class Config:
        populate_by_name = True
        from_attributes = True


class ScanRequest(BaseModel):
    page_text: str = Field(alias="pageText")
    url: str
    title: str
    user_id: Optional[str] = Field(None, alias="userId")
    active_model: Optional[str] = Field("logistic_regression", alias="activeModel")

    class Config:
        populate_by_name = True


class KeywordMatchSchema(BaseModel):
    keyword: str
    category: str
    count: int
    weight: int
    color: str


class ScanResponse(BaseModel):
    scan_id: int = Field(alias="scanId")
    url: str
    title: str
    score: int  # Final combined score
    label: str  # Final combined label
    matched_keywords: List[KeywordMatchSchema] = Field(alias="matchedKeywords")
    reasons: List[str]
    timestamp: str
    rule_score: int = Field(alias="ruleScore")
    ml_score: int = Field(alias="mlScore")
    ml_prediction: str = Field(alias="mlPrediction")
    ml_confidence: float = Field(alias="mlConfidence")
    model_name: str = Field(alias="modelName")
    model_version: str = Field(alias="modelVersion")
    model_accuracy: float = Field(alias="modelAccuracy")
    model_latency: float = Field(alias="modelLatency")
    model_memory: float = Field(alias="modelMemory")
    human_explanation: str = Field(alias="humanExplanation")
    influential_words: List[str] = Field(alias="influentialWords")
    is_privacy_policy: bool = Field(alias="isPrivacyPolicy")
    privacy_summary: Optional[dict] = Field(None, alias="privacySummary")
    reputation: dict = Field(alias="reputation")
    trust_score: int = Field(alias="trustScore")

    class Config:
        populate_by_name = True
        from_attributes = True


class FeedbackRequest(BaseModel):
    scan_id: Optional[int] = Field(None, alias="scanId")
    feedback_type: str = Field(alias="feedbackType")
    comment: Optional[str] = None
    
    # Optional scan details for local-scanned fallback logs
    url: Optional[str] = None
    title: Optional[str] = None
    rule_score: Optional[int] = Field(None, alias="ruleScore")
    ml_score: Optional[int] = Field(None, alias="mlScore")
    final_score: Optional[int] = Field(None, alias="finalScore")
    risk_label: Optional[str] = Field(None, alias="riskLabel")
    ml_prediction: Optional[str] = Field(None, alias="mlPrediction")
    ml_confidence: Optional[float] = Field(None, alias="mlConfidence")

    class Config:
        populate_by_name = True


class FeedbackResponse(BaseModel):
    feedback_id: int = Field(alias="feedbackId")
    scan_id: int = Field(alias="scanId")
    feedback_type: str = Field(alias="feedbackType")
    comment: Optional[str] = None
    timestamp: datetime

    class Config:
        populate_by_name = True
        from_attributes = True


class ModelInfoResponse(BaseModel):
    version: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float = Field(alias="f1Score")
    trained_date: str = Field(alias="trainedDate")
    dataset_size: Optional[int] = Field(560, alias="datasetSize")

    class Config:
        populate_by_name = True
        from_attributes = True


class StatsResponse(BaseModel):
    total_scans: int = Field(alias="totalScans")
    average_score: float = Field(alias="averageScore")
    risk_distribution: dict = Field(alias="riskDistribution")
    most_common_keywords: List[dict] = Field(alias="mostCommonKeywords")
    feedback_distribution: dict = Field(alias="feedbackDistribution")
    recent_scans: List[dict] = Field(alias="recentScans")
    daily_scans: List[dict] = Field(alias="dailyScans")
    common_categories: List[dict] = Field(alias="commonCategories")
    top_domains: List[dict] = Field(alias="topDomains")

    class Config:
        populate_by_name = True
