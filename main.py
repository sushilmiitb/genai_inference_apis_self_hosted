import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from transformers import AutoTokenizer, AutoModel
import torch

# Determine environment: 'development' or 'production'
ENV = os.getenv("APP_ENV", "development")

# Allowed models for production (add more as needed)
ALLOWED_MODELS = [
    "sentence-transformers/all-MiniLM-L6-v2",
    # Add more allowed model names here
]

# Allowed CORS origins for production
PROD_CORS_ORIGINS = [
    # e.g., "https://your-frontend.com", "chrome-extension://your-extension-id"
    "https://www.youtube.com"
]

# Create FastAPI app instance
app = FastAPI()

# Configure CORS based on environment
if ENV == "production":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=PROD_CORS_ORIGINS,  # Restrict to trusted origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all for development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Cache for loaded models and tokenizers to avoid reloading
model_cache: Dict[str, Dict[str, object]] = {}

class EmbeddingRequest(BaseModel):
    """
    Request model for embedding endpoint.
    text: The input text for which embeddings are to be generated.
    model_name: The Hugging Face model to use for embeddings.
    """
    text: str
    model_name: str

class EmbeddingResponse(BaseModel):
    """
    Response model for embedding endpoint.
    embeddings: A list of floats representing the embedding vector.
    model: The name of the model used.
    embedding_size: The size (length) of the embedding vector.
    """
    embeddings: List[float]
    model: str
    embedding_size: int

# Batch request/response models
class BatchEmbeddingRequest(BaseModel):
    """
    Request model for batch embedding endpoint.
    texts: List of input texts for which embeddings are to be generated.
    model_name: The Hugging Face model to use for embeddings.
    """
    texts: List[str]
    model_name: str

class BatchEmbeddingResponse(BaseModel):
    """
    Response model for batch embedding endpoint.
    embeddings: List of embedding vectors (one per input text).
    model: The name of the model used.
    embedding_size: The size (length) of each embedding vector.
    """
    embeddings: List[List[float]]
    model: str
    embedding_size: int

@app.get("/")
def read_root():
    """
    Root endpoint for health check.
    Returns a welcome message.
    """
    return {"message": "Welcome to the Gen AI Inference APIs!"}

def get_tokenizer_and_model(model_name: str):
    """
    Retrieve (and cache) the tokenizer and model for the given model_name.
    Raises HTTPException if loading fails or model is not allowed in production.
    """
    if ENV == "production" and model_name not in ALLOWED_MODELS:
        raise HTTPException(status_code=403, detail=f"Model '{model_name}' is not allowed in production.")
    if model_name in model_cache:
        return model_cache[model_name]["tokenizer"], model_cache[model_name]["model"]
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name)
        model_cache[model_name] = {"tokenizer": tokenizer, "model": model}
        return tokenizer, model
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load model '{model_name}': {str(e)}")

def get_text_embedding(text: str, model_name: str) -> List[float]:
    """
    Generate embeddings for the given text using the specified Hugging Face model.
    Returns a list of floats representing the embedding vector.
    """
    tokenizer, model = get_tokenizer_and_model(model_name)
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()
    if isinstance(embeddings, float):
        embeddings = [embeddings]
    return embeddings

@app.post("/embeddings", response_model=EmbeddingResponse)
def get_embeddings(request: EmbeddingRequest):
    """
    Endpoint to return real embeddings for the given text using the user-specified Hugging Face model.
    Includes the embedding size in the response.
    """
    embedding = get_text_embedding(request.text, request.model_name)
    return EmbeddingResponse(
        embeddings=embedding,
        model=request.model_name,
        embedding_size=len(embedding)
    )

@app.post("/batch-embeddings", response_model=BatchEmbeddingResponse)
def get_batch_embeddings(request: BatchEmbeddingRequest):
    """
    Endpoint to return embeddings for a batch of texts using the user-specified Hugging Face model.
    Returns a list of embedding vectors, model name, and embedding size.
    """
    if not request.texts:
        raise HTTPException(status_code=400, detail="No texts provided.")
    embeddings = [get_text_embedding(text, request.model_name) for text in request.texts]
    embedding_size = len(embeddings[0]) if embeddings else 0
    return BatchEmbeddingResponse(
        embeddings=embeddings,
        model=request.model_name,
        embedding_size=embedding_size
    )
