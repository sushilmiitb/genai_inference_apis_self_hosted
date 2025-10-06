# Development Setup

This guide explains how to set up the project for local development, run tests, and update your environment.

## 1. Clone the Repository
```bash
git clone <repo-url>
cd genai_inference_apis_self_hosted
```

## 2. Set Up Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3. Run the FastAPI Server
```bash
uvicorn main:app --reload
```
- Access the API docs at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 4. Run Tests
```bash
pytest -v
```

## 5. Updating Your Development Environment
- Pull latest code: `git pull`
- If dependencies change: `pip install -r requirements.txt`
- Restart the server if needed.

## 6. API Endpoints
- See the interactive docs at `/docs` when running locally.
- Main endpoints:
  - `GET /` — Health check
  - `POST /embeddings` — Generate embeddings for a single text
  - `POST /batch-embeddings` — Generate embeddings for a list of texts

## 7. Notes
- For Gemini backend, see [../README.md](../README.md#setting-up-gemini-api-key-required-for-gemini-backend)
- For production/deployment, see the deployment docs in this folder.
