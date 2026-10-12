
import re
import unicodedata


def normalize_text(value):
    """
    Convert text to lowercase and remove spaces and punctuation.
    Example: 'Adidas Official!' -> 'adidasofficial'
    """

    if value is None:
        return ""

    value = unicodedata.normalize("NFKC", str(value))
    value = value.lower()

    return re.sub(r"[^a-z0-9]", "", value)


def normalize_username(username):
    """
    Normalize a username while preserving letters and numbers.
    Separators such as dots and underscores are removed.
    """

    if username is None:
        return ""

    username = unicodedata.normalize("NFKC", str(username))
    username = username.strip().lower()
    username = username.lstrip("@")

    return re.sub(r"[^a-z0-9]", "", username)


def clean_text(value):
    """Remove unwanted control characters and repeated whitespace."""

    if value is None:
        return ""

    value = unicodedata.normalize("NFKC", str(value))

    # Remove control characters except ordinary whitespace.
    value = "".join(
        character
        for character in value
        if character.isprintable() or character in "\t\n"
    )

    return re.sub(r"\s+", " ", value).strip()


def truncate_text(value, max_length=200, suffix="..."):
    """Shorten text to a maximum length."""

    value = clean_text(value)

    if max_length < 0:
        raise ValueError("max_length cannot be negative")

    if len(value) <= max_length:
        return value

    if max_length <= len(suffix):
        return suffix[:max_length]

    return value[:max_length - len(suffix)].rstrip() + suffix


def contains_keyword(text, keywords):
    """Return keywords found as whole words or phrases."""

    text = clean_text(text).lower()
    found = []

    for keyword in keywords:
        keyword = clean_text(keyword).lower()

        if not keyword:
            continue

        pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"

        if re.search(pattern, text):
            found.append(keyword)

    return found


def extract_hashtags(text):
    """Extract hashtag words from a text string."""

    if not text:
        return []

    return re.findall(r"(?<!\w)#([A-Za-z0-9_]+)", str(text))


def mask_sensitive_value(value, visible_characters=3):
    """Show only a short prefix of a value."""

    value = str(value or "")

    if not value:
        return ""

    if len(value) <= visible_characters:
        return "*" * len(value)

    return value[:visible_characters] + "*" * (len(value) - visible_characters)
