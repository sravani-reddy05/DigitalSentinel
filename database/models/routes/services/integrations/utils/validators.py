
import re
import ipaddress
from urllib.parse import urlparse


SUPPORTED_SOCIAL_PLATFORMS = {
    "Instagram",
    "Facebook",
    "X",
    "TikTok",
    "Other",
}

SUPPORTED_APP_STORES = {
    "Google Play",
    "Apple App Store",
    "Other",
}

ALLOWED_IMAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp",
}


def validate_required_text(value, field_name="Field", max_length=200):
    """Validate that a required text field is present and not too long."""

    if not isinstance(value, str):
        return False, f"{field_name} must be text"

    value = value.strip()

    if not value:
        return False, f"{field_name} is required"

    if len(value) > max_length:
        return False, f"{field_name} must be at most {max_length} characters"

    return True, "Valid"


def validate_optional_text(value, field_name="Field", max_length=2000):
    """Validate an optional text field."""

    if value is None:
        return True, "Valid"

    if not isinstance(value, str):
        return False, f"{field_name} must be text"

    if len(value.strip()) > max_length:
        return False, f"{field_name} must be at most {max_length} characters"

    return True, "Valid"


def validate_http_url(value, required=False):
    """Allow only HTTP/HTTPS URLs with a valid hostname."""

    if not isinstance(value, str):
        return False, "URL must be text"

    value = value.strip()

    if not value:
        if required:
            return False, "URL is required"
        return True, "URL is optional"

    try:
        parsed = urlparse(value)

        if parsed.scheme.lower() not in {"http", "https"}:
            return False, "URL must start with http:// or https://"

        if not parsed.hostname or "." not in parsed.hostname:
            return False, "Enter a valid hostname"

        hostname = parsed.hostname.lower()
        if hostname == "localhost" or hostname.endswith(".local"):
            return False, "Local network URLs are not allowed"
        if hostname.endswith(".internal"):
            return False, "Local network URLs are not allowed"
        try:
            if not ipaddress.ip_address(hostname).is_global:
                return False, "Private or local network URLs are not allowed"
        except ValueError:
            pass
        if hostname.replace(".", "").isdigit():
            octets = hostname.split(".")
            if len(octets) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in octets):
                first, second = int(octets[0]), int(octets[1])
                if first in {0, 10, 127} or first >= 224 or (first == 169 and second == 254) or (first == 172 and 16 <= second <= 31) or (first == 192 and second == 168):
                    return False, "Private or local network URLs are not allowed"

        if parsed.username or parsed.password:
            return False, "URLs must not contain embedded credentials"

        # Reject malformed ports, such as https://example.com:abc
        _ = parsed.port

        return True, "Valid URL"

    except ValueError:
        return False, "Invalid URL"


def validate_platform(platform, platform_type="social"):
    """Check the selected platform against an allowlist."""

    if not isinstance(platform, str):
        return False, "Platform must be text"

    platform = platform.strip()

    if platform_type == "social":
        allowed = SUPPORTED_SOCIAL_PLATFORMS
    elif platform_type == "app":
        allowed = SUPPORTED_APP_STORES
    else:
        return False, "Unknown platform type"

    if platform not in allowed:
        return False, "Unsupported platform"

    return True, "Valid platform"


def validate_image_extension(filename):
    """Check an image filename extension, not its actual file contents."""

    if not isinstance(filename, str) or "." not in filename:
        return False, "A file extension is required"

    extension = filename.rsplit(".", 1)[-1].lower()

    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        return False, "Unsupported image extension"

    return True, "Allowed extension"


def validate_username(username):
    """Validate a submitted username's basic shape."""

    if not isinstance(username, str):
        return False, "Username must be text"

    username = username.strip()

    if not username:
        return False, "Username is required"

    if len(username) > 200:
        return False, "Username is too long"

    if re.search(r"[\r\n]", username):
        return False, "Username cannot contain line breaks"

    return True, "Valid username"
