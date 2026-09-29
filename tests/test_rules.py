import pytest
from backend.app.services.rules_service import analyze_text_rules, RULES

def test_rules_structure():
    """Verify rules list is fully defined with required categories and weights."""
    assert len(RULES) == 5
    categories = {r["category"] for r in RULES}
    assert "URGENCY" in categories
    assert "SCARCITY" in categories
    assert "SUBSCRIPTION_TRAP" in categories
    assert "PRIVACY_RISK" in categories
    assert "FINANCIAL_MANIPULATION" in categories
    
    for r in RULES:
        assert isinstance(r["weight"], int)
        assert len(r["keywords"]) > 0
        assert r["weight"] > 0

def test_rule_matching_empty_text():
    """Verify empty text results in Safe label and zero scores."""
    res = analyze_text_rules("")
    assert res["score"] == 0
    assert res["label"] == "Safe"
    assert len(res["matchedKeywords"]) == 0
    assert len(res["reasons"]) == 0

def test_urgency_rules():
    """Verify urgency phrases trigger correct category and scores."""
    res = analyze_text_rules("Hurry up! Limited time only!")
    assert res["score"] == 40  # "hurry" (+10) + "hurry up" (+10) + "limited time" (+10) + "limited time only" (+10)
    assert res["label"] == "Caution"  # Threshold is > 20 for Caution
    assert any(m["category"] == "URGENCY" for m in res["matchedKeywords"])
    assert "⚠ Urgency language detected" in res["reasons"]

def test_scarcity_rules():
    """Verify scarcity phrases trigger correct caution thresholds."""
    res = analyze_text_rules("Only 2 left! Almost sold out! Selling fast!")
    # "only 2 left" (+15) + "almost sold out" (+15) + "selling fast" (+15) = 45
    assert res["score"] == 45
    assert res["label"] == "Caution"
    assert "⚠ Scarcity language detected" in res["reasons"]

def test_subscription_rules():
    """Verify subscription trap keywords trigger high caution scores."""
    res = analyze_text_rules("Get a free trial with auto renewal and continuous service.")
    # "free trial" (+25) + "auto renewal" (+25) + "continuous service" (+25) = 75 (clamped to 100)
    assert res["score"] == 75
    assert res["label"] == "Risky"
    assert "⚠ Subscription wording detected" in res["reasons"]

def test_privacy_rules():
    """Verify privacy risks trigger correct classifications."""
    res = analyze_text_rules("We share your data with marketing partners and use personalized ads.")
    # "share your data" (+20) + "marketing partners" (+20) + "personalized ads" (+20) = 60
    assert res["score"] == 60
    assert res["label"] == "Risky"
    assert "⚠ Third-party sharing mentioned" in res["reasons"]

def test_financial_rules():
    """Verify financial manipulation words trigger correct risky ratings."""
    res = analyze_text_rules("Instant approval! Earn money fast! No risk!")
    # "instant approval" (+30) + "earn money" (+30) + "no risk" (+30) = 90
    assert res["score"] == 90
    assert res["label"] == "Risky"
    assert "⚠ Financial pressure language detected" in res["reasons"]

def test_boundary_matching():
    """Verify boundary checks prevent matching keywords inside longer words."""
    # "hurry" is an urgency keyword. "hurrying" should not match because of alphanumeric boundaries.
    res1 = analyze_text_rules("I am hurrying home.")
    assert res1["score"] == 0
    
    # "hurry" as standalone word should match
    res2 = analyze_text_rules("Please hurry up.")
    assert res2["score"] == 20  # Matches "hurry" and "hurry up"
 
def test_case_insensitive_matching():
    """Verify rule matching ignores capitalization differences."""
    res = analyze_text_rules("HURRY UP! FREE TRIAL! SELL DATA!")
    assert res["score"] > 50
    assert res["label"] == "Risky"
 
def test_multiple_categories_combined():
    """Verify scoring combined multiple categories correctly."""
    res = analyze_text_rules("Flash sale ends soon (Urgency). Only 3 left (Scarcity). Allow cookies (Privacy).")
    # "flash sale" (+10) + "ends soon" (+10) + "sale ends" (+10) + "only 3 left" (+15) + "allow cookies" (+20) = 65
    assert res["score"] == 65
    assert res["label"] == "Risky"
    assert len(res["reasons"]) == 3
 
def test_clamping_max_score():
    """Verify total score is clamped to a maximum value of 100."""
    giant_text = "Hurry up! Free trial! Instant approval! Guaranteed returns! Win cash! Share your data! Track location!"
    res = analyze_text_rules(giant_text)
    assert res["score"] == 100
 
@pytest.mark.parametrize("input_text, expected_score, expected_label", [
    ("This is a completely normal page with no dark patterns.", 0, "Safe"),
    ("Hurry now, flash sale!", 20, "Safe"),
    ("Only 3 left, almost sold out!", 30, "Caution"),
    ("Free trial with auto-renewal cancel anytime.", 75, "Risky"),
    ("Instant approval, win cash prize, easy money!", 100, "Risky"),
    ("Instant approval, win cash prize, easy money! Limited time only!", 100, "Risky"),
])
def test_parameterized_scans(input_text, expected_score, expected_label):
    """Run parameter scans to check score increments and label thresholds."""
    res = analyze_text_rules(input_text)
    assert res["score"] == expected_score
    assert res["label"] == expected_label


@pytest.mark.parametrize("keyword, expected_category, expected_weight", [
    ("hurry", "URGENCY", 10),
    ("limited time", "URGENCY", 10),
    ("offer ends soon", "URGENCY", 10),
    ("only today", "URGENCY", 10),
    ("last chance", "URGENCY", 10),
    ("act now", "URGENCY", 10),
    ("sale ends", "URGENCY", 10),
    ("expires soon", "URGENCY", 10),
    ("flash sale", "URGENCY", 10),
    ("running out", "URGENCY", 10),
    ("only 1 left", "SCARCITY", 15),
    ("only 2 left", "SCARCITY", 15),
    ("few remaining", "SCARCITY", 15),
    ("almost sold out", "SCARCITY", 15),
    ("limited stock", "SCARCITY", 15),
    ("low stock", "SCARCITY", 15),
    ("selling fast", "SCARCITY", 15),
    ("high demand", "SCARCITY", 15),
    ("last items", "SCARCITY", 15),
    ("almost gone", "SCARCITY", 15),
    ("free trial", "SUBSCRIPTION_TRAP", 25),
    ("auto renewal", "SUBSCRIPTION_TRAP", 25),
    ("auto-renewal", "SUBSCRIPTION_TRAP", 25),
    ("recurring billing", "SUBSCRIPTION_TRAP", 25),
    ("subscription", "SUBSCRIPTION_TRAP", 25),
    ("cancel anytime", "SUBSCRIPTION_TRAP", 25),
    ("renew automatically", "SUBSCRIPTION_TRAP", 25),
    ("membership fee", "SUBSCRIPTION_TRAP", 25),
    ("continuous service", "SUBSCRIPTION_TRAP", 25),
    ("billed weekly", "SUBSCRIPTION_TRAP", 25),
    ("share your data", "PRIVACY_RISK", 20),
    ("third-party partners", "PRIVACY_RISK", 20),
    ("personalized ads", "PRIVACY_RISK", 20),
    ("marketing partners", "PRIVACY_RISK", 20),
    ("consent required", "PRIVACY_RISK", 20),
    ("sell data", "PRIVACY_RISK", 20),
    ("track location", "PRIVACY_RISK", 20),
    ("access contacts", "PRIVACY_RISK", 20),
    ("allow cookies", "PRIVACY_RISK", 20),
    ("data collection", "PRIVACY_RISK", 20),
    ("instant approval", "FINANCIAL_MANIPULATION", 30),
    ("guaranteed loan", "FINANCIAL_MANIPULATION", 30),
    ("win cash", "FINANCIAL_MANIPULATION", 30),
    ("congratulations", "FINANCIAL_MANIPULATION", 30),
    ("claim reward", "FINANCIAL_MANIPULATION", 30),
    ("earn money", "FINANCIAL_MANIPULATION", 30),
    ("no risk", "FINANCIAL_MANIPULATION", 30),
    ("guaranteed returns", "FINANCIAL_MANIPULATION", 30),
    ("get rich", "FINANCIAL_MANIPULATION", 30),
    ("make money fast", "FINANCIAL_MANIPULATION", 30),
])
def test_individual_keyword_matching(keyword, expected_category, expected_weight):
    """Verify that each dark pattern keyword is correctly matched and categorized."""
    res = analyze_text_rules(f"This is a dummy sentence containing {keyword} inside it.")
    assert any(
        m["keyword"] == keyword and 
        m["category"] == expected_category and 
        m["weight"] == expected_weight 
        for m in res["matchedKeywords"]
    )
