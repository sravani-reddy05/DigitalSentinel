
import re
import unicodedata
from difflib import SequenceMatcher

try:
    from rapidfuzz import fuzz
except ImportError:
    fuzz = None


SUSPICIOUS_KEYWORDS = {
    "official", "offers", "deals", "free", "giveaway",
    "discount", "support", "help", "service", "customer", "team",
    "verify", "account", "claim", "winner", "promo"
}

CONFUSABLE_CHARACTERS = str.maketrans({
    "а": "a", "с": "c", "е": "e", "і": "i", "ј": "j", "к": "k",
    "м": "m", "о": "o", "р": "p", "ѕ": "s", "т": "t", "х": "x",
    "у": "y", "в": "b", "н": "h",
    "α": "a", "ε": "e", "ι": "i", "κ": "k", "ο": "o", "ρ": "p",
    "τ": "t", "υ": "y", "χ": "x",
})
LEET_CHARACTERS = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t"})


def normalize_text(value, map_confusables=True):
    """Normalize Unicode text and remove punctuation for name comparison."""
    value = unicodedata.normalize("NFKD", str(value or "").lower())
    value = "".join(character for character in value if not unicodedata.combining(character))
    if map_confusables:
        value = value.translate(CONFUSABLE_CHARACTERS)
    return re.sub(r"[^a-z0-9]", "", value)


def normalize_lookalike(value):
    """Return a comparison form that also accounts for common digit substitutions."""
    return normalize_text(value).translate(LEET_CHARACTERS)


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
            "lookalike_detected": False,
            "suspicious_keywords": [],
            "reasons": ["Username or brand name is missing"]
        }

    compare = fuzz.ratio if fuzz else lambda left, right: SequenceMatcher(None, left, right).ratio() * 100
    unobfuscated_username = normalize_text(username, map_confusables=False)
    unobfuscated_brand = normalize_text(brand_core, map_confusables=False)
    lookalike_username = normalize_lookalike(username)
    lookalike_brand = normalize_lookalike(brand_core)
    regular_similarity = compare(unobfuscated_username, unobfuscated_brand)
    similarity = max(
        compare(normalized_username, normalized_brand),
        regular_similarity,
        compare(lookalike_username, lookalike_brand)
    )

    # A profile name often adds words such as "support" or "deals" after the
    # brand. Compare meaningful brand terms and substrings so those additions
    # do not hide a close brand match.
    brand_terms = [normalize_text(term) for term in re.findall(r"[A-Za-z0-9]+", brand_core)]
    brand_terms = [term for term in brand_terms if len(term) >= 5 and term not in {"official", "company", "brand"}]
    contained_terms = [term for term in brand_terms if term in unobfuscated_username]
    contains_brand = bool(unobfuscated_brand and unobfuscated_brand in unobfuscated_username) or bool(contained_terms)
    term_scores = []
    for term in brand_terms:
        term_scores.extend((
            compare(normalized_username, term),
            compare(lookalike_username, normalize_lookalike(term)),
        ))
        if fuzz:
            term_scores.extend((
                fuzz.partial_ratio(normalized_username, term),
                fuzz.partial_ratio(lookalike_username, normalize_lookalike(term)),
            ))
        else:
            for candidate in {normalized_username, lookalike_username}:
                if len(candidate) >= len(term):
                    term_scores.append(max(
                        SequenceMatcher(None, normalize_lookalike(term), candidate[index:index + len(term)]).ratio() * 100
                        for index in range(len(candidate) - len(term) + 1)
                    ))
    similarity = round(max([similarity, *term_scores]), 2)

    words = set(re.findall(r"[a-z0-9]+", username.lower()))
    suspicious = sorted(words.intersection(SUSPICIOUS_KEYWORDS))
    brand_tokens = {normalize_text(term) for term in re.findall(r"[A-Za-z0-9]+", brand_core)}
    extra_words = sorted(word for word in words if word not in brand_tokens and not word.isdigit())
    likely_misspelling = bool(similarity >= 55 and not contains_brand)
    lookalike_detected = bool(similarity >= 55 and not contains_brand)
    visually_confusable = (
        lookalike_detected
        and lookalike_username != unobfuscated_username
        and similarity > regular_similarity
    )

    reasons = []

    if contains_brand:
        reasons.append("Username contains a distinctive brand name")

    if visually_confusable:
        reasons.append("Username uses visually confusable characters and resembles the brand name")

    if similarity >= 80:
        reasons.append("Username is highly similar to the brand name")
    elif likely_misspelling:
        reasons.append("Username resembles the brand name; check for a spelling variation")
    elif similarity >= 55:
        reasons.append("Username has moderate similarity to the brand name")

    if suspicious:
        reasons.append("Username includes extra trust or promotion terms: " + ", ".join(suspicious))

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
        "lookalike_detected": lookalike_detected,
        "visually_confusable": visually_confusable,
        "suspicious_keywords": suspicious,
        "extra_words": extra_words,
        "likely_misspelling": likely_misspelling,
        "reasons": reasons
    }
