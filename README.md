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

## Google Cloud SDK Setup (for Deployment)

1. **Install Google Cloud SDK:**
   - Download and install from: [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)
   - Follow the instructions for your operating system (macOS, Windows, Linux).

2. **Initialize the SDK and authenticate:**
   ```bash
   gcloud init
   gcloud auth login
   ```
   - This will open a browser window for you to log in with your Google account.

3. **Set your Google Cloud project:**
   ```bash
   gcloud config set project neat-mechanic-469810-h5
   ```

4. **Enable required Google Cloud APIs:**
   ```bash
   gcloud services enable run.googleapis.com containerregistry.googleapis.com cloudbuild.googleapis.com
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

---

## Deployment: Google Cloud Run (Cloud Build)

### Prerequisites
- Google Cloud project: `neat-mechanic-469810-h5`
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed
- Authenticated: `gcloud auth login`
- Project set: `gcloud config set project neat-mechanic-469810-h5`
- Enable required APIs:
  ```bash
  gcloud services enable run.googleapis.com containerregistry.googleapis.com cloudbuild.googleapis.com
  ```

### Build and Deploy

1. **Submit your code to Google Cloud Build:**
   ```bash
   gcloud builds submit --tag gcr.io/neat-mechanic-469810-h5/genai-inference-api
   ```

2. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy genai-inference-api \
     --image gcr.io/neat-mechanic-469810-h5/genai-inference-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 2Gi \
     --timeout 300
   ```
   - Adjust `--region`, `--memory`, and `--timeout` as needed.

3. **(Optional) Set environment variables:**
   ```bash
   gcloud run services update genai-inference-api \
     --update-env-vars APP_ENV=production
   ```

4. **Access your service:**
   - After deployment, Cloud Run will provide a service URL.
   - Visit `https://<your-service-url>/docs` for the interactive API docs.

---

For more details, see the [Cloud Run Quickstart](https://cloud.google.com/run/docs/quickstarts/build-and-deploy).
