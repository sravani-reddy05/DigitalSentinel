import re
from difflib import SequenceMatcher
from urllib.parse import urlparse


SUSPICIOUS_URL_TERMS = {
    "account",
    "auth",
    "billing",
    "claim",
    "login",
    "password",
    "recovery",
    "secure",
    "support",
    "update",
    "verify",
    "wallet",
}


def analyze_brand_url(url, brand_name, official_website=""):
    """Identify common lookalike and credential-themed URL patterns."""
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower().rstrip(".")
    official_host = (urlparse(official_website).hostname or "").lower().rstrip(".")
    normalized_brand = re.sub(r"[^a-z0-9]", "", brand_name.lower())
    labels = hostname.split(".")
    normalized_labels = [
        re.sub(r"[^a-z0-9]", "", label) for label in labels
    ]
    reasons = []

    is_official_host = bool(
        official_host
        and (hostname == official_host or hostname.endswith(f".{official_host}"))
    )

    if any(label.startswith("xn--") for label in labels):
        reasons.append("The hostname contains an internationalized (punycode) label.")

    if normalized_brand and not is_official_host:
        if normalized_brand in re.sub(r"[^a-z0-9]", "", hostname):
            reasons.append(
                "The brand name appears in a hostname outside the registered official website."
            )
        elif len(normalized_brand) >= 4 and any(
            0.75 <= SequenceMatcher(None, normalized_brand, label).ratio() < 1
            for label in normalized_labels
            if label
        ):
            reasons.append("A hostname label closely resembles the brand name.")

    host_terms = {
        term for label in labels for term in re.findall(r"[a-z]+", label)
    }
    path_terms = set(re.findall(r"[a-z]+", parsed.path.lower()))
    matched_terms = sorted((host_terms | path_terms) & SUSPICIOUS_URL_TERMS)
    if matched_terms:
        reasons.append(
            "The URL contains credential or account-themed terms: "
            + ", ".join(matched_terms)
            + "."
        )

    return {
        "hostname": hostname,
        "official_hostname": official_host or None,
        "suspicious_patterns": reasons,
        "has_risk": bool(reasons),
        "method": "Heuristic URL-pattern inspection; the submitted URL is not fetched.",
    }
