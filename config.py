import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# config.py:
# This file manages configuration settings for the application.

class Config:
    # Weaviate database URL
    WEAVIATE_URL = os.environ.get("WEAVIATE_URL", "http://localhost:8080")
    # Jan.ai API URL for language model interactions
    JANAI_API_URL = os.environ.get("JANAI_API_URL", "http://localhost:1337/v1/chat/completions")
    # Name of the language model to use
    JANAI_MODEL_NAME = os.environ.get("JANAI_MODEL_NAME", "mistral-ins-7b-q4")
    # Optional API key for Jan.ai/OpenAI-compatible endpoint
    JANAI_API_KEY = os.environ.get("JANAI_API_KEY", None)
    # Max tokens for LLM output (many servers reject very large numbers)
    JANAI_MAX_TOKENS = int(os.environ.get("JANAI_MAX_TOKENS", "1024"))
    # Maximum number of retries for API calls
    MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))
    # Base delay for exponential backoff in seconds
    BASE_DELAY = float(os.environ.get("BASE_DELAY", "1"))
    # Comma-separated list of API keys allowed to access our FastAPI endpoints
    # Example: ALLOWED_API_KEYS="key1,key2,key3". If empty, auth is disabled.
    ALLOWED_API_KEYS = [
        k.strip() for k in os.environ.get("ALLOWED_API_KEYS", "").split(",") if k.strip()
    ]
