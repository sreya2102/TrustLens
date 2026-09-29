import re

PRIVACY_KEYWORDS = {
    "data_collected": [
        "collect", "gather", "information we collect", "personal data", "personal information",
        "email address", "name", "phone number", "ip address", "contact details"
    ],
    "third_party_sharing": [
        "third party", "third-party", "share", "disclose", "partners", "affiliates", 
        "service providers", "sell your", "marketing partners"
    ],
    "cookies": [
        "cookies", "cookie", "tracking pixel", "web beacon", "browser storage", 
        "local storage", "tracking technologies"
    ],
    "advertising": [
        "advertise", "advertising", "marketing", "promotional", "opt-out", 
        "personalized ads", "interest-based", "targeted ads", "opt out"
    ],
    "data_retention": [
        "retain", "retention", "store information", "store your", "how long we keep", 
        "retention period", "storage duration"
    ],
    "user_rights": [
        "user rights", "your rights", "access", "rectify", "delete", "erase", 
        "right to", "gdpr", "ccpa", "portability", "opt-out rights"
    ]
}

def detect_privacy_policy(url: str, title: str, text: str) -> bool:
    """
    Detects if the page represents a Privacy Policy.
    Checks URL slugs, title phrases, and keyword densities.
    """
    url_lower = url.lower()
    title_lower = title.lower()
    
    # Direct slug matches
    privacy_slugs = ["privacy", "privacy-policy", "privacy_policy", "legal/privacy", "privacy-statement"]
    if any(slug in url_lower for slug in privacy_slugs):
        return True
        
    # Title match
    if "privacy" in title_lower and ("policy" in title_lower or "statement" in title_lower or "notice" in title_lower):
        return True
        
    # Content-based heuristic check
    text_lower = text.lower()
    if text_lower.count("privacy policy") >= 2 or text_lower.count("information we collect") >= 1:
        # Check that it's a long legal-ish document
        if len(text_lower) > 2000:
            return True
            
    return False

def summarize_privacy_policy(text: str) -> dict:
    """
    Analyzes the text of the privacy policy and extracts key sentences matching 
    the targeted categories. Compiles a concise bullet summary for each section.
    """
    if not text:
        return {}

    # Split text into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text.strip().replace("\n", " "))
    
    summaries = {
        "dataCollected": "No explicit statements found regarding data collection details.",
        "thirdPartySharing": "No explicit statements found regarding sharing data with third parties.",
        "cookies": "No explicit statements found regarding cookie and tracking usage.",
        "advertising": "No explicit marketing or promotional advertising disclosures identified.",
        "dataRetention": "No explicit statements found regarding data retention policies.",
        "userRights": "No explicit statements found regarding your access or deletion rights."
    }

    # Find the best matches for each category
    category_matches = {cat: [] for cat in PRIVACY_KEYWORDS.keys()}
    
    for sentence in sentences:
        sentence_clean = sentence.strip()
        if len(sentence_clean) < 25 or len(sentence_clean) > 200:
            continue  # Skip too short or too long sentences
            
        sentence_lower = sentence_clean.lower()
        
        for category, keywords in PRIVACY_KEYWORDS.items():
            for kw in keywords:
                if kw in sentence_lower:
                    category_matches[category].append(sentence_clean)
                    break  # Match found for this category, skip other keywords for this sentence

    # Format the matches into bullet points
    # Map snake_case category to camelCase camelCase JSON keys
    key_mapping = {
        "data_collected": "dataCollected",
        "third_party_sharing": "thirdPartySharing",
        "cookies": "cookies",
        "advertising": "advertising",
        "data_retention": "dataRetention",
        "user_rights": "userRights"
    }

    for cat, matches in category_matches.items():
        json_key = key_mapping[cat]
        if matches:
            # Take up to 2 unique, highly relevant sentences as the summary
            unique_matches = list(dict.fromkeys(matches))
            # Sort by length or key match indices
            selected = unique_matches[:2]
            summaries[json_key] = " ".join(selected)

    return summaries
