from fastapi import APIRouter, HTTPException
from .classifier_models import TextItem, TopicItem, ClassifyTextsRequest, ClassificationResult, ClassifyTextsResponse
from .classifier_backends import get_classifier_backend
from .config import ALLOWED_PROVIDERS, ALLOWED_MODELS, DEFAULT_TEXT_CLASSIFIER_BACKEND, GEMINI_MODEL_NAME

router = APIRouter()

@router.post(
    "/classify-texts",
    response_model=ClassifyTextsResponse,
    summary="Classify texts into topics using LLM or embedding models.",
    tags=["Text Classification"],
)
def classify_texts(request: ClassifyTextsRequest) -> ClassifyTextsResponse:
    """
    Classify a batch of texts into the given topics using the configured or requested backend/model.

    - **provider**: Optional. Preferred model provider (e.g., 'GEMINI', 'MOCK'). If not provided, uses config default.
    - **model_name**: Optional. Preferred model name (e.g., 'gemini-2.5-flash'). If not provided, uses config default for the provider.
    - If provider/model_name are invalid, returns 400 with a clear error message.
    - If GEMINI is used and the API key is missing, returns 500 or raises ValueError.
    - The response contains, for each text, a list of topic IDs it belongs to (empty if none).
    - Supports batch classification in a single call.
    """
    # Determine provider
    provider = (request.provider or DEFAULT_TEXT_CLASSIFIER_BACKEND).upper()
    if provider not in ALLOWED_PROVIDERS:
        raise HTTPException(status_code=400, detail=f"Invalid provider '{provider}'. Allowed: {ALLOWED_PROVIDERS}")
    # Determine model_name
    allowed_models = ALLOWED_MODELS[provider]
    model_name = request.model_name or (GEMINI_MODEL_NAME if provider == "GEMINI" else None)
    if model_name not in allowed_models:
        raise HTTPException(status_code=400, detail=f"Invalid model_name '{model_name}' for provider '{provider}'. Allowed: {allowed_models}")
    # Get backend and classify
    backend = get_classifier_backend(provider=provider, model_name=model_name)
    results = backend.classify(request.texts, request.topics)
    return ClassifyTextsResponse(results=results)
