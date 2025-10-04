# src/config.py

# Default Gemini model name
GEMINI_MODEL_NAME = "gemini-2.5-flash"

# Allowed providers
ALLOWED_PROVIDERS = ["GEMINI", "MOCK"]

# Allowed models per provider
ALLOWED_MODELS = {
    "GEMINI": ["gemini-2.5-flash"],
    "MOCK": [None],  # Mock does not use a model name
}

# Set default backend to MOCK for testing
DEFAULT_TEXT_CLASSIFIER_BACKEND = "MOCK"

# Gemini rate limits
GEMINI_RATE_LIMIT_PER_MINUTE = 60
GEMINI_RATE_LIMIT_PER_DAY = 1000

# Add other project-wide configs here as needed
