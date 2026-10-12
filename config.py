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

    UPLOAD_FOLDER = str(BASE_DIR / "uploads")

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
