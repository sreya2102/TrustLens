import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database.connection import Base
from backend.app.models.models import User, ScanHistory, Feedback, ModelInfo

# Create an in-memory SQLite database for isolated database tests
DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(name="db_session")
def fixture_db_session():
    """Fixture to build tables and yield a clean in-memory session."""
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

def test_create_user(db_session):
    """Verify inserting and retrieving user profiles works correctly."""
    new_user = User(user_id="test-uuid-123", email="user@test.com", privacy_mode=True)
    db_session.add(new_user)
    db_session.commit()
    
    user = db_session.query(User).filter(User.user_id == "test-uuid-123").first()
    assert user is not None
    assert user.email == "user@test.com"
    assert user.privacy_mode is True

def test_create_scan_history(db_session):
    """Verify inserting scan records works correctly."""
    # Ensure guest user exists first
    user = User(user_id="test-user")
    db_session.add(user)
    db_session.commit()

    scan = ScanHistory(
        user_id="test-user",
        url_hash="sha256-hash",
        domain="google.com",
        page_title="Google",
        rule_score=0,
        ml_score=0,
        final_score=0,
        risk_label="Safe",
        matched_keywords_json="[]",
        page_text="Hello world"
    )
    db_session.add(scan)
    db_session.commit()

    record = db_session.query(ScanHistory).filter(ScanHistory.url_hash == "sha256-hash").first()
    assert record is not None
    assert record.domain == "google.com"
    assert record.user_id == "test-user"
    assert record.page_title == "Google"

def test_create_feedback(db_session):
    """Verify feedback logging works and links to scans correctly."""
    scan = ScanHistory(
        url_hash="hash-123",
        domain="scam-deals.com",
        rule_score=80,
        ml_score=90,
        final_score=85,
        risk_label="Risky"
    )
    db_session.add(scan)
    db_session.commit()

    feedback = Feedback(
        scan_id=scan.scan_id,
        feedback_type="wrong",
        comment="Actually it is caution"
    )
    db_session.add(feedback)
    db_session.commit()

    fb_record = db_session.query(Feedback).filter(Feedback.scan_id == scan.scan_id).first()
    assert fb_record is not None
    assert fb_record.feedback_type == "wrong"
    assert fb_record.comment == "Actually it is caution"
    assert fb_record.scan.domain == "scam-deals.com"

def test_cascade_delete(db_session):
    """Verify that deleting a scan automatically deletes linked feedback."""
    scan = ScanHistory(
        url_hash="hash-456",
        domain="scam-site.com",
        rule_score=10,
        ml_score=20,
        final_score=15,
        risk_label="Safe"
    )
    db_session.add(scan)
    db_session.commit()

    feedback = Feedback(
        scan_id=scan.scan_id,
        feedback_type="correct"
    )
    db_session.add(feedback)
    db_session.commit()

    # Confirm record presence
    assert db_session.query(Feedback).count() == 1

    # Delete scan history record
    db_session.delete(scan)
    db_session.commit()

    # Verify cascade deleted linked feedback
    assert db_session.query(Feedback).count() == 0

def test_model_info_table(db_session):
    """Verify database can store and retrieve version parameters."""
    m_info = ModelInfo(
        version="1.0.0",
        accuracy=0.98,
        precision=0.97,
        recall=0.98,
        f1_score=0.98,
        trained_date="2026-07-23"
    )
    db_session.add(m_info)
    db_session.commit()

    saved_info = db_session.query(ModelInfo).filter(ModelInfo.version == "1.0.0").first()
    assert saved_info is not None
    assert saved_info.accuracy == 0.98
    assert saved_info.f1_score == 0.98
