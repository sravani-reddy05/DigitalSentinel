import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:

    SECRET_KEY = os.getenv("SECRET_KEY") or os.urandom(32).hex()

    DATABASE_PATH = os.getenv(
        "DATABASE_PATH",
        str(BASE_DIR / "data" / "digitalsentinel.db")
    )
    SEED_DEMO_DATA = os.getenv("SEED_DEMO_DATA", "true").lower() == "true"

    UPLOAD_FOLDER = os.getenv(
        "UPLOAD_FOLDER",
        str(BASE_DIR / "uploads")
    )

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    ALLOWED_IMAGE_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg",
        "webp"
    }

    JSON_SORT_KEYS = False

    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

    GROQ_MODEL = os.getenv(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile"
    )
    VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")
    SAFE_BROWSING_API_KEY = os.getenv("SAFE_BROWSING_API_KEY", "")
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
