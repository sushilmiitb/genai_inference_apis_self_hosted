import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# Test data for a valid request
VALID_TEXT = "Test embedding generation."
VALID_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Test data for an invalid model
INVALID_MODEL = "nonexistent-model-xyz"

def test_embeddings_valid():
    """
    Test /embeddings endpoint with valid input and model.
    Checks response status, structure, and embedding size.
    """
    response = client.post("/embeddings", json={"text": VALID_TEXT, "model_name": VALID_MODEL})
    assert response.status_code == 200
    data = response.json()
    assert "embeddings" in data
    assert "model" in data
    assert "embedding_size" in data
    assert isinstance(data["embeddings"], list)
    assert isinstance(data["embedding_size"], int)
    assert data["model"] == VALID_MODEL
    assert len(data["embeddings"]) == data["embedding_size"]

def test_embeddings_invalid_model():
    """
    Test /embeddings endpoint with an invalid model name.
    Should return 400 Bad Request with appropriate error message.
    """
    response = client.post("/embeddings", json={"text": VALID_TEXT, "model_name": INVALID_MODEL})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Failed to load model" in data["detail"]

def test_embeddings_missing_text():
    """
    Test /embeddings endpoint with missing text field.
    Should return 422 Unprocessable Entity.
    """
    response = client.post("/embeddings", json={"model_name": VALID_MODEL})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

def test_embeddings_missing_model_name():
    """
    Test /embeddings endpoint with missing model_name field.
    Should return 422 Unprocessable Entity.
    """
    response = client.post("/embeddings", json={"text": VALID_TEXT})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

def test_batch_embeddings_valid():
    """
    Test /batch-embeddings endpoint with valid input and model.
    Checks response status, structure, and embedding size.
    """
    texts = ["First text", "Second text", "Third text"]
    response = client.post("/batch-embeddings", json={"texts": texts, "model_name": VALID_MODEL})
    assert response.status_code == 200
    data = response.json()
    assert "embeddings" in data
    assert "model" in data
    assert "embedding_size" in data
    assert isinstance(data["embeddings"], list)
    assert isinstance(data["embedding_size"], int)
    assert data["model"] == VALID_MODEL
    assert len(data["embeddings"]) == len(texts)
    for emb in data["embeddings"]:
        assert isinstance(emb, list)
        assert len(emb) == data["embedding_size"]

def test_batch_embeddings_empty_texts():
    """
    Test /batch-embeddings endpoint with empty texts list.
    Should return 400 Bad Request.
    """
    response = client.post("/batch-embeddings", json={"texts": [], "model_name": VALID_MODEL})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "No texts provided."

def test_batch_embeddings_missing_model_name():
    """
    Test /batch-embeddings endpoint with missing model_name field.
    Should return 422 Unprocessable Entity.
    """
    response = client.post("/batch-embeddings", json={"texts": ["Test"]})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

def test_batch_embeddings_missing_texts():
    """
    Test /batch-embeddings endpoint with missing texts field.
    Should return 422 Unprocessable Entity.
    """
    response = client.post("/batch-embeddings", json={"model_name": VALID_MODEL})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
