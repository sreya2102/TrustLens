import hashlib
from urllib.parse import urlparse

# Pre-seeded local blacklist of known deceptive/phishing domains for testing
BLACKLIST_DOMAINS = {
    "scam-shop.com",
    "phishing-bank-login.net",
    "double-income-now.info",
    "win-jackpot-claims.cc",
    "get-rich-fast.biz",
    "guaranteed-loan-approval.org",
    "cheap-deals-fake.site",
    "track-user-cookies.xyz"
}

def check_domain_blacklist(domain: str) -> bool:
    """Checks if a domain name is blacklisted."""
    return domain.lower() in BLACKLIST_DOMAINS

def calculate_domain_age(domain: str) -> int:
    """
    Returns the domain age in years.
    Utilizes a consistent deterministic hash check for mocking
    reproducible academic domain ages without network WHOIS latency.
    """
    # Deterministic simulation based on domain name hash
    hash_val = int(hashlib.md5(domain.encode()).hexdigest(), 16)
    # Map to age between 0 (brand new) and 15 (mature) years
    simulated_age = hash_val % 16
    return simulated_age

def evaluate_website_reputation(url: str) -> dict:
    """
    Evaluates website parameters:
    - HTTPS status
    - Blacklist membership
    - Domain age (simulated/mocked)
    - Returns a domain reputation rating out of 100
    """
    is_https = url.lower().startswith("https://")
    
    # Extract domain
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        if ":" in domain:
            domain = domain.split(":")[0]
        domain = domain.lower() if domain else "unknown"
    except Exception:
        domain = "unknown"

    # Evaluate checks
    is_blacklisted = check_domain_blacklist(domain)
    domain_age_years = calculate_domain_age(domain)
    
    # Calculate reputation base score (out of 100)
    reputation_score = 100
    
    if not is_https:
        reputation_score -= 30  # Secure protocol penalty
        
    if domain_age_years <= 1:
        reputation_score -= 20  # Brand new domain penalty
    elif domain_age_years <= 3:
        reputation_score -= 10  # Young domain penalty
        
    if is_blacklisted:
        reputation_score = 0  # Severe blacklist penalty

    reputation_score = max(0, reputation_score)
    
    # Verdict mapping
    if is_blacklisted:
        verdict = "Blacklisted (Malicious)"
    elif reputation_score >= 80:
        verdict = "Trusted"
    elif reputation_score >= 50:
        verdict = "Suspicious"
    else:
        verdict = "Untrusted"

    return {
        "domain": domain,
        "isHttps": is_https,
        "isBlacklisted": is_blacklisted,
        "domainAge": f"{domain_age_years} years" if domain_age_years > 0 else "Less than 1 year",
        "domainAgeYears": domain_age_years,
        "reputationScore": reputation_score,
        "verdict": verdict
    }

def calculate_unified_trust_score(scan_risk_score: int, reputation_data: dict) -> int:
    """
    Combines the Dark Pattern / Lexical scan risk score (60% Rule + 40% ML)
    with the Website Reputation assessment (HTTPS, domain age, blacklist).
    Returns a unified Trust Score out of 100.
    """
    reputation_score = reputation_data["reputationScore"]
    
    if reputation_data["isBlacklisted"]:
        return 0  # Blacklisted sites get absolute zero trust
        
    # Threat score is (100 - scan_risk_score)
    threat_component = 100 - scan_risk_score
    
    # Blended score: 50% threat detection + 50% technical reputation
    trust_score = round(0.5 * threat_component + 0.5 * reputation_score)
    
    # Hard clamp HTTP sites to a maximum trust score of 50 to enforce secure protocols
    if not reputation_data["isHttps"]:
        trust_score = min(trust_score, 50)
        
    return max(0, min(100, trust_score))
