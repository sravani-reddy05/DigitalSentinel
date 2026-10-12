
import re
from difflib import SequenceMatcher

try:
    from rapidfuzz import fuzz
except ImportError:
    fuzz = None


SUSPICIOUS_KEYWORDS = {
    "official", "offers", "deals", "free", "giveaway",
    "discount", "support", "claim", "winner", "promo"
}


def normalize_text(value):
    """Convert text to lowercase and remove punctuation."""
    value = str(value or "").lower()
    return re.sub(r"[^a-z0-9]", "", value)


def analyze_username(username, brand_name):
    username = str(username or "").strip()
    brand_name = str(brand_name or "").strip()

    normalized_username = normalize_text(username)
    # Demo labels and legal suffixes are metadata, not part of the protected name.
    brand_core = re.sub(r"\((?:demo|sample|example)\)", "", brand_name, flags=re.I)
    normalized_brand = normalize_text(brand_core)

    if not normalized_username or not normalized_brand:
        return {
            "username": username,
            "brand_name": brand_name,
            "similarity": 0,
            "contains_brand": False,
            "suspicious_keywords": [],
            "reasons": ["Username or brand name is missing"]
        }

    compare = fuzz.ratio if fuzz else lambda left, right: SequenceMatcher(None, left, right).ratio() * 100
    similarity = compare(normalized_username, normalized_brand)

    # A profile name often adds words such as "support" or "deals" after the
    # brand. Compare meaningful brand terms and substrings so those additions
    # do not hide a close brand match.
    brand_terms = [normalize_text(term) for term in re.findall(r"[A-Za-z0-9]+", brand_core)]
    brand_terms = [term for term in brand_terms if len(term) >= 5 and term not in {"official", "company", "brand"}]
    contained_terms = [term for term in brand_terms if term in normalized_username]
    contains_brand = bool(normalized_brand and normalized_brand in normalized_username) or bool(contained_terms)
    term_scores = [compare(normalized_username, term) for term in brand_terms]
    # Partial match fallback for environments without RapidFuzz.
    if not fuzz:
        for term in brand_terms:
            if len(normalized_username) >= len(term):
                term_scores.append(max(SequenceMatcher(None, term, normalized_username[i:i + len(term)]).ratio() * 100 for i in range(len(normalized_username) - len(term) + 1)))
    similarity = round(max([similarity, *term_scores]), 2)

    words = set(re.findall(r"[a-z0-9]+", username.lower()))
    suspicious = sorted(words.intersection(SUSPICIOUS_KEYWORDS))

    reasons = []

    if contains_brand:
        reasons.append("Username contains a distinctive brand name")

    if similarity >= 80:
        reasons.append("Username is highly similar to the brand name")
    elif similarity >= 55:
        reasons.append("Username has moderate similarity to the brand name")

    if suspicious:
        reasons.append(
            "Potentially promotional keywords: "
            + ", ".join(suspicious)
        )

    return {
        "username": username,
        "brand_name": brand_name,
        "similarity": similarity,
        "contains_brand": contains_brand,
        "suspicious_keywords": suspicious,
        "reasons": reasons
    }
