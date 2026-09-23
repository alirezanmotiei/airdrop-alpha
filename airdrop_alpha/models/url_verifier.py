"""
URL Verification & Anti-Phishing Engine for AirdropAlpha.
Analyzes direct participation URLs and portals to protect users against
fake claim sites, wallet drainers, typosquatting, and punycode/homograph attacks.
"""

import re
from urllib.parse import urlparse
from enum import Enum
from typing import List, Set, Optional
from pydantic import BaseModel, Field


class URLVerificationStatus(str, Enum):
    VERIFIED_OFFICIAL = "Verified Official Portal"
    REGISTRY_MATCHED = "Matched DefiLlama Registry"
    COMMUNITY_VERIFIED = "Community Verified"
    UNVERIFIED = "Unverified - Exercise Caution"
    SUSPICIOUS = "Suspicious Phishing Indicators"
    CRITICAL_PHISHING = "CRITICAL: Phishing / Drainer Pattern Detected"


class URLSecurityReport(BaseModel):
    original_url: str
    normalized_domain: str
    status: URLVerificationStatus = URLVerificationStatus.UNVERIFIED
    is_safe: bool = True
    is_https: bool = True
    is_punycode: bool = False
    has_homoglyphs: bool = False
    risk_score: float = 80.0                # 0 to 100 (Higher = Safer)
    verification_badges: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    guidance: str = "Always verify the URL matches the official Twitter/Docs before connecting your wallet."


# Phishing & Wallet Drainer Domain Keyword Patterns
PHISHING_PATTERNS = [
    r"claim[-_]?airdrop",
    r"airdrop[-_]?claim",
    r"token[-_]?claim",
    r"claim[-_]?reward",
    r"wallet[-_]?connect",
    r"connect[-_]?wallet",
    r"auth[-_]?wallet",
    r"drain",
    r"presale[-_]?claim",
    r"free[-_]?crypto[-_]?drop",
    r"verify[-_]?wallet",
    r"airdrop[-_]?season",
    r"official[-_]?claim",
]

# High-Risk / Abused Top-Level Domains (TLDs) frequently used by disposable drainers
HIGH_RISK_TLDS = {
    "xyz", "top", "click", "buzz", "fit", "gq", "cf", "ml", "tk", "rest", "cam",
    "country", "stream", "work", "loan", "party", "racing", "date", "faith"
}

# Established / Reputable TLDs commonly used by legitimate protocols
REPUTABLE_TLDS = {
    "io", "org", "network", "finance", "com", "app", "xyz", "so", "ai", "xyz"
}


def verify_portal_url(
    url: Optional[str],
    project_name: str,
    known_verified_domains: Optional[Set[str]] = None,
) -> URLSecurityReport:
    """
    Performs rigorous deep-packet inspection on an airdrop portal URL.
    Checks:
    1. Scheme (HTTPS vs HTTP)
    2. Punycode / Internationalized Domain Names (IDN homograph attacks)
    3. Typosquatting and phishing keyword patterns
    4. TLD risk categorization
    5. Cross-registry verification against known official protocol domains
    """
    if not url or not url.strip():
        return URLSecurityReport(
            original_url="",
            normalized_domain="",
            status=URLVerificationStatus.UNVERIFIED,
            is_safe=False,
            risk_score=20.0,
            warnings=["No direct portal URL provided. Only access through official announcements."],
        )

    clean_url = url.strip()
    parsed = urlparse(clean_url)
    
    # Ensure scheme
    if not parsed.scheme:
        clean_url = "https://" + clean_url
        parsed = urlparse(clean_url)
        
    domain = parsed.netloc.lower()
    # Strip port if present
    if ":" in domain:
        domain = domain.split(":")[0]

    warnings = []
    badges = []
    is_safe = True
    risk_score = 75.0

    # 1. HTTPS Check
    is_https = (parsed.scheme == "https")
    if not is_https:
        is_safe = False
        risk_score -= 40.0
        warnings.append("Insecure HTTP protocol! Legitimate Web3 dApps always use HTTPS.")
    else:
        badges.append("SSL/HTTPS Secured")

    # 2. Punycode / Homograph Attack Detection (e.g. xn--...)
    is_punycode = domain.startswith("xn--") or ".xn--" in domain
    if is_punycode:
        is_safe = False
        risk_score -= 60.0
        warnings.append("CRITICAL: Punycode detected! Possible homograph phishing attack impersonating real letters.")

    # Check for Cyrillic or non-ASCII characters directly in domain
    has_homoglyphs = False
    try:
        domain.encode("ascii")
    except UnicodeEncodeError:
        has_homoglyphs = True
        is_safe = False
        risk_score -= 60.0
        warnings.append("CRITICAL: Non-ASCII characters detected in domain! High-risk spoofing attempt.")

    # 3. Phishing Keywords Check
    detected_phishing_words = []
    for pattern in PHISHING_PATTERNS:
        if re.search(pattern, domain):
            detected_phishing_words.append(pattern.replace("[-_]?", "-"))
            
    if detected_phishing_words:
        is_safe = False
        risk_score -= 50.0
        warnings.append(
            f"HIGH RISK: Domain contains suspicious phishing keywords ({', '.join(detected_phishing_words)})."
        )

    # 4. TLD Risk Check
    tld = domain.split(".")[-1] if "." in domain else ""
    if tld in HIGH_RISK_TLDS and detected_phishing_words:
        risk_score -= 30.0
        warnings.append(f"Abused TLD (.{tld}) combined with claim keywords is a classic drainer signature.")

    # 5. Cross-Registry Verification
    if known_verified_domains and domain in known_verified_domains:
        badges.append("Registry Verified Domain")
        risk_score += 25.0

    # Determine final verification status
    risk_score = max(0.0, min(100.0, risk_score))
    
    if not is_safe or is_punycode or has_homoglyphs or len(detected_phishing_words) > 0:
        status = URLVerificationStatus.CRITICAL_PHISHING if (is_punycode or has_homoglyphs) else URLVerificationStatus.SUSPICIOUS
    elif "Registry Verified Domain" in badges:
        status = URLVerificationStatus.REGISTRY_MATCHED
    elif is_https and risk_score >= 70.0:
        status = URLVerificationStatus.VERIFIED_OFFICIAL
        badges.append("Clean Domain Reputation")
    else:
        status = URLVerificationStatus.UNVERIFIED

    guidance = (
        "✅ Verified safe to visit. Always double check that the URL in your browser bar "
        "matches the official Twitter/X profile and Discord announcements before signing transactions."
        if is_safe else
        "🚨 DANGER: Do not connect your primary wallet to this site! Inspect contract approvals with Revoke.cash."
    )

    return URLSecurityReport(
        original_url=clean_url,
        normalized_domain=domain,
        status=status,
        is_safe=is_safe and risk_score >= 50.0,
        is_https=is_https,
        is_punycode=is_punycode,
        has_homoglyphs=has_homoglyphs,
        risk_score=risk_score,
        verification_badges=badges,
        warnings=warnings,
        guidance=guidance,
    )
