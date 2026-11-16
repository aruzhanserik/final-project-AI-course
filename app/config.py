"""Settings read from environment variables (never hard-code keys)."""
import os
from pathlib import Path

try:  # optional: load a local .env file if python-dotenv is installed
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

ROOT = Path(__file__).resolve().parent.parent
CARE_DB_PATH = Path(os.getenv("CARE_DB_PATH", ROOT / "data" / "care_db.json"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
# Model names change often; "gemini-flash-latest" is Google's alias for the current Flash model.
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()
# Backup models, tried in order if the main one is busy, over quota or retired (comma-separated).
GEMINI_FALLBACK_MODELS = [m.strip() for m in os.getenv(
    "GEMINI_FALLBACK_MODELS", "gemini-3.8-flash,gemini-flash-lite-latest,gemini-flash-latest"
).split(",") if m.strip()]
# Seconds to wait for Gemini. Newer models can "think" for a while, so 60 s was too short.
GEMINI_TIMEOUT = int(os.getenv("GEMINI_TIMEOUT", "150"))
PLANTNET_API_KEY =os.getenv("PLANTNET_API_KEY", "").strip()

MAX_UPLOAD_MB = 8
