import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    # LLM Configuration (Free & Open Source)
    LLM_MODEL = os.getenv("LLM_MODEL", "mistral")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # Google Calendar API
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv(
        "GOOGLE_REDIRECT_URI", "http://localhost:8080/auth/callback")

    # Weather API
    WEATHERAPI_API_KEY = os.getenv("WEATHERAPI_API_KEY")

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///plancast.db")

    # Available LLM Models
    AVAILABLE_MODELS = ["mistral", "llama2",
                        "codellama", "phi2", "neural-chat"]


settings = Settings()
