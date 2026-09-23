import pytest
from airdrop_alpha.models.url_verifier import (
    verify_portal_url, URLVerificationStatus
)


def test_verify_portal_url_legitimate():
    report = verify_portal_url("https://app.midas.app", "Midas")
    assert report.is_safe is True
    assert report.is_https is True
    assert report.is_punycode is False
    assert report.status in [URLVerificationStatus.VERIFIED_OFFICIAL, URLVerificationStatus.REGISTRY_MATCHED]
    assert report.risk_score >= 70.0


def test_verify_portal_url_insecure_http():
    report = verify_portal_url("http://example-testnet.com", "Testnet")
    assert report.is_https is False
    assert any("Insecure HTTP" in w for w in report.warnings)
    assert report.risk_score < 70.0


def test_verify_portal_url_phishing_keywords():
    report = verify_portal_url("https://arbitrum-claim-airdrop.xyz", "Arbitrum")
    assert report.is_safe is False
    assert report.status in [URLVerificationStatus.SUSPICIOUS, URLVerificationStatus.CRITICAL_PHISHING]
    assert any("phishing keywords" in w for w in report.warnings)


def test_verify_portal_url_punycode_attack():
    report = verify_portal_url("https://xn--claim-arbitrum-70a.top", "Arbitrum")
    assert report.is_safe is False
    assert report.is_punycode is True
    assert report.status == URLVerificationStatus.CRITICAL_PHISHING
    assert any("Punycode detected" in w for w in report.warnings)


def test_verify_portal_url_homoglyph_attack():
    # Cyrillic 'а' (U+0430) instead of Latin 'a'
    homoglyph_domain = "https://\u0430rbitrum.io"
    report = verify_portal_url(homoglyph_domain, "Arbitrum")
    assert report.is_safe is False
    assert report.has_homoglyphs is True
    assert report.status == URLVerificationStatus.CRITICAL_PHISHING
