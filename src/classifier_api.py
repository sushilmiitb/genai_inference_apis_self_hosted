from fastapi import APIRouter, HTTPException
from .classifier_models import TextItem, TopicItem, ClassifyTextsRequest, ClassificationResult, ClassifyTextsResponse
from .classifier_backends import get_classifier_backend
from .config import ALLOWED_PROVIDERS, ALLOWED_MODELS, DEFAULT_TEXT_CLASSIFIER_BACKEND, GEMINI_MODEL_NAME

router = APIRouter()

@router.post("/classify-texts", response_model=ClassifyTextsResponse)
def classify_texts(request: ClassifyTextsRequest) -> ClassifyTextsResponse:
    """
    Classify a batch of texts into the given topics using the configured or requested backend/model.
    Returns only topic IDs for which the classifier is confident; otherwise, the list is empty.
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
