# Gen AI Inference APIs Self Hosted

## Overview
This project exposes inference APIs for generating embeddings using Hugging Face models. It is designed for self-hosted use, allowing you to run open-source models locally and avoid third-party API costs.

---

## Setup

1. **Clone the repository and set up the environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run the FastAPI server:**
   ```bash
   uvicorn main:app --reload
   ```

---

## API Endpoints

### Health Check
- **GET /**
  - Returns a welcome message.
  - **Response:**
    ```json
    { "message": "Welcome to the Gen AI Inference APIs!" }
    ```

### Generate Embeddings
- **POST /embeddings**
  - Generates embeddings for the provided text using the specified Hugging Face model.
  - **Request Body:**
    ```json
    {
      "text": "Your input text here",
      "model_name": "sentence-transformers/all-MiniLM-L6-v2"
    }
    ```
  - **Response:**
    ```json
    {
      "embeddings": [0.123, 0.456, ...],
      "model": "sentence-transformers/all-MiniLM-L6-v2",
      "embedding_size": 384
    }
    ```
  - **Error Response (invalid model):**
    ```json
    {
      "detail": "Failed to load model 'nonexistent-model-xyz': ..."
    }
    ```

---

## Model Caching & Performance
- Models and tokenizers are loaded and cached in memory on first use for each `model_name`.
- Subsequent requests for the same model are fast and do not require reloading or re-downloading.
- If a model is not found locally, it will be downloaded from the Hugging Face Hub on first use.

---

## Testing
- Run all tests with:
  ```bash
  pytest -v
  ```

---

## Extensibility
- You can add more endpoints or support additional model types by extending `main.py`.
- For production, consider adding authentication, rate limiting, and model whitelisting.

---

## Interactive API Docs
- Once the server is running, visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for interactive Swagger UI documentation.
