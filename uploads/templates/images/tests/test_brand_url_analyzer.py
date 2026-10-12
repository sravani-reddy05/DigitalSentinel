from database.models.routes.services.brand_url_analyzer import analyze_brand_url


def test_official_domain_does_not_raise_brand_match():
    result = analyze_brand_url(
        "https://shop.example.com/products",
        "Example",
        "https://example.com",
    )

    assert result["has_risk"] is False
    assert result["suspicious_patterns"] == []


def test_brand_name_on_unofficial_domain_is_flagged():
    result = analyze_brand_url(
        "https://example-login.attacker.test/account/verify",
        "Example",
        "https://example.com",
    )

    assert result["has_risk"] is True
    assert any("brand name" in reason.lower() for reason in result["suspicious_patterns"])
    assert any("credential or account" in reason.lower() for reason in result["suspicious_patterns"])


def test_credential_terms_are_flagged_without_brand_match():
    result = analyze_brand_url(
        "https://attacker.test/login",
        "Example",
        "https://example.com",
    )

    assert result["has_risk"] is True
    assert len(result["suspicious_patterns"]) == 1
