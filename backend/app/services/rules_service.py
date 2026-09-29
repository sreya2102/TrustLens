import re

RULES = [
    {
        "category": "URGENCY",
        "displayName": "Urgency language",
        "weight": 10,
        "color": "#fef08a",
        "reasonTemplate": "Urgency language detected",
        "keywords": [
            "hurry", "limited time", "offer ends soon", "only today", "last chance",
            "act now", "sale ends", "only few left", "expires soon", "ends soon",
            "dont miss out", "don't miss out", "flash sale", "hurry up",
            "limited time only", "last minute", "last-minute", "one day only",
            "final hours", "tick tock", "tick-tock", "seconds left", "running out"
        ]
    },
    {
        "category": "SCARCITY",
        "displayName": "Scarcity language",
        "weight": 15,
        "color": "#fed7aa",
        "reasonTemplate": "Scarcity language detected",
        "keywords": [
            "only 1 left", "only 2 left", "only 3 left", "only 4 left", "only 5 left",
            "few remaining", "almost sold out", "limited stock", "low stock",
            "selling fast", "high demand", "demand is high", "last items",
            "backorder soon", "almost gone", "limited quantity", "while supplies last"
        ]
    },
    {
        "category": "SUBSCRIPTION_TRAP",
        "displayName": "Subscription traps",
        "weight": 25,
        "color": "#fca5a5",
        "reasonTemplate": "Subscription wording detected",
        "keywords": [
            "free trial", "auto renewal", "auto-renewal", "recurring billing",
            "subscription", "cancel anytime", "cancel any time", "renew automatically",
            "renews automatically", "billed monthly", "billed annually", "membership fee",
            "continuous billing", "auto-renew", "trial period", "after the trial",
            "continuous service", "billed weekly"
        ]
    },
    {
        "category": "PRIVACY_RISK",
        "displayName": "Privacy risks",
        "weight": 20,
        "color": "#fdba74",
        "reasonTemplate": "Third-party sharing mentioned",
        "keywords": [
            "share your data", "share your personal details", "third-party partners",
            "third party partners", "personalized ads", "marketing partners",
            "consent required", "sell data", "sell your data", "track location",
            "access contacts", "device information", "allow cookies", "ad profiling",
            "data collection", "share with partners", "third-party advertising",
            "targeted ads", "advertising networks"
        ]
    },
    {
        "category": "FINANCIAL_MANIPULATION",
        "displayName": "Financial manipulation",
        "weight": 30,
        "color": "#fca5a5",
        "reasonTemplate": "Financial pressure language detected",
        "keywords": [
            "instant approval", "guaranteed loan", "win cash", "congratulations",
            "claim reward", "earn money", "no risk", "risk free", "risk-free",
            "guaranteed returns", "get rich", "double your income", "financial freedom",
            "cash prize", "jackpot", "free gift", "claim now", "make money fast",
            "unlimited cash", "easy money", "no obligation"
        ]
    }
]

def analyze_text_rules(visible_text: str):
    """
    Analyzes webpage text using standard lexical dark pattern rules.
    Matches the exact counts, weights, reasons, and categories of the TypeScript rule engine.
    """
    if not visible_text:
        return {
            "score": 0,
            "label": "Safe",
            "matchedKeywords": [],
            "reasons": []
        }

    # Standardize text whitespace for reliable matching (matching TS normalizedText)
    normalized_text = " ".join(visible_text.split())
    matched_keywords = []

    for rule in RULES:
        for keyword in rule["keywords"]:
            escaped_keyword = re.escape(keyword)
            pattern = escaped_keyword

            # Use word boundaries if keyword starts or ends with alphanumeric chars
            if re.match(r"^\w", keyword):
                pattern = r"\b" + pattern
            if re.search(r"\w$", keyword):
                pattern = pattern + r"\b"

            regex = re.compile(pattern, re.IGNORECASE)
            matches = regex.findall(normalized_text)
            count = len(matches)

            if count > 0:
                matched_keywords.append({
                    "keyword": keyword,
                    "category": rule["category"],
                    "count": count,
                    "weight": rule["weight"],
                    "color": rule["color"]
                })

    # Compute rule score
    rule_score = sum(match["count"] * match["weight"] for match in matched_keywords)
    rule_score = min(rule_score, 100)

    # Determine risk label based on thresholds
    label = "Safe"
    if rule_score > 50:
        label = "Risky"
    elif rule_score > 20:
        label = "Caution"

    # Compile reasons
    matched_categories = {match["category"] for match in matched_keywords}
    reasons = []
    if "URGENCY" in matched_categories:
        reasons.append("⚠ Urgency language detected")
    if "SCARCITY" in matched_categories:
        reasons.append("⚠ Scarcity language detected")
    if "PRIVACY_RISK" in matched_categories:
        reasons.append("⚠ Third-party sharing mentioned")
    if "SUBSCRIPTION_TRAP" in matched_categories:
        reasons.append("⚠ Subscription wording detected")
    if "FINANCIAL_MANIPULATION" in matched_categories:
        reasons.append("⚠ Financial pressure language detected")

    return {
        "score": rule_score,
        "label": label,
        "matchedKeywords": matched_keywords,
        "reasons": reasons
    }
