import os
from dotenv import load_dotenv


load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
JWT_SECRET = os.getenv("JWT_SECRET", "change-this-secret-in-production")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI",
    "http://localhost:8000/auth/google/callback",
)
AI_REQUEST_TIMEOUT_SECONDS = int(os.getenv("AI_REQUEST_TIMEOUT_SECONDS", "60"))
AI_MAX_RETRIES = int(os.getenv("AI_MAX_RETRIES", "2"))
AI_RETRY_DELAY_SECONDS = float(os.getenv("AI_RETRY_DELAY_SECONDS", "1"))
AI_INPUT_COST_PER_1K = float(os.getenv("AI_INPUT_COST_PER_1K", "0"))
AI_OUTPUT_COST_PER_1K = float(os.getenv("AI_OUTPUT_COST_PER_1K", "0"))


LOCAL_FRONTEND_URL = "http://localhost:5173"


def _normalize_url(value: str) -> str:
    return value.strip().rstrip("/")


FRONTEND_URL = _normalize_url(os.getenv("FRONTEND_URL", LOCAL_FRONTEND_URL))


def _load_cors_origins() -> list[str]:
    configured = os.getenv("CORS_ORIGINS", "")
    origins = [
        _normalize_url(origin)
        for origin in configured.split(",")
        if origin.strip()
    ]

    for origin in (LOCAL_FRONTEND_URL, FRONTEND_URL):
        if origin not in origins:
            origins.append(origin)

    return origins


CORS_ORIGINS = _load_cors_origins()
