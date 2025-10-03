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

# Add other project-wide configs here as needed
