import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..database.connection import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    privacy_mode = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    scans = relationship("ScanHistory", back_populates="user")


class ScanHistory(Base):
    __tablename__ = "scan_history"

    scan_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.user_id"), nullable=True)
    url_hash = Column(String, index=True, nullable=False)
    domain = Column(String, nullable=False)
    page_title = Column(String, nullable=True)
    rule_score = Column(Integer, nullable=False)
    ml_score = Column(Integer, nullable=False)
    final_score = Column(Integer, nullable=False)
    risk_label = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Store matched keywords (JSON string format) for admin statistics
    matched_keywords_json = Column(Text, nullable=True)
    
    # Store complete webpage text only if debugging mode is enabled
    page_text = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="scans")
    feedbacks = relationship("Feedback", back_populates="scan", cascade="all, delete-orphan")


class Feedback(Base):
    __tablename__ = "feedback"

    feedback_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scan_id = Column(Integer, ForeignKey("scan_history.scan_id"), nullable=False)
    feedback_type = Column(String, nullable=False)  # 'correct' or 'wrong'
    comment = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    scan = relationship("ScanHistory", back_populates="feedbacks")


class ModelInfo(Base):
    __tablename__ = "model_info"

    version = Column(String, primary_key=True, index=True)
    accuracy = Column(Float, nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    trained_date = Column(String, nullable=False)
