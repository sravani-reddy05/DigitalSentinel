
import re
from urllib.parse import urlparse


def validate_brand_name(name):
    name = str(name or "").strip()

    if not name:
        return False, "Brand name is required"

    if len(name) > 120:
        return False, "Brand name must be 120 characters or fewer"

    return True, "Valid brand name"


def validate_website(url):
    url = str(url or "").strip()

    if not url:
        return True, "Website is optional"

    try:
        parsed = urlparse(url)
        valid_scheme = parsed.scheme in {"http", "https"}
        valid_host = bool(parsed.hostname and "." in parsed.hostname)

        if not valid_scheme or not valid_host:
            return False, "Enter a valid HTTP or HTTPS website URL"

        # Reject URLs containing embedded login credentials.
        if parsed.username or parsed.password:
            return False, "Website URLs must not contain login credentials"

        return True, "Valid website URL"

    except ValueError:
        return False, "Invalid website URL"


def validate_asset_url(url):
    return validate_website(url)
