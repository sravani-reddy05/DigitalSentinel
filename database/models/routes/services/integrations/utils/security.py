
from pathlib import Path
from werkzeug.utils import secure_filename


ALLOWED_UPLOAD_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp",
}


def secure_filename_value(filename):
    """
    Return a sanitized filename.
    Do not use the original user-provided filename as a storage path.
    """

    if not isinstance(filename, str):
        return ""

    return secure_filename(filename)


def is_safe_filename(filename):
    """Check the sanitized filename and its extension."""

    if not isinstance(filename, str) or not filename.strip():
        return False

    # Reject path separators and traversal-like input.
    if "/" in filename or "\\" in filename or ".." in filename:
        return False

    safe_name = secure_filename(filename)

    if not safe_name or safe_name != filename:
        return False

    if "." not in safe_name:
        return False

    extension = safe_name.rsplit(".", 1)[-1].lower()

    return extension in ALLOWED_UPLOAD_EXTENSIONS


def is_path_inside_directory(file_path, base_directory):
    """
    Check whether a resolved path stays inside the intended directory.
    Use this before accessing a path derived from user input.
    """

    try:
        base = Path(base_directory).resolve()
        candidate = Path(file_path).resolve()

        return candidate == base or base in candidate.parents

    except (OSError, RuntimeError, ValueError):
        return False


def validate_request_size(value, max_characters=4000):
    """Limit the size of a text value received from a request."""

    if not isinstance(value, str):
        return False, "Input must be text"

    if len(value) > max_characters:
        return False, "Input exceeds the permitted length"

    return True, "Valid"


def mask_secret(secret, visible_characters=4):
    """Mask a token or secret before displaying it in a UI."""

    if not secret:
        return ""

    secret = str(secret)

    if len(secret) <= visible_characters:
        return "*" * len(secret)

    return (
        secret[:visible_characters]
        + "*" * (len(secret) - visible_characters)
    )
