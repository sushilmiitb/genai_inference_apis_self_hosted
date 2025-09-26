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

### Batch Generate Embeddings
- **POST /batch-embeddings**
  - Generates embeddings for a list of texts using the specified Hugging Face model.
  - **Request Body:**
    ```json
    {
      "texts": ["First text", "Second text", "Third text"],
      "model_name": "sentence-transformers/all-MiniLM-L6-v2"
    }
    ```
  - **Response:**
    ```json
    {
      "embeddings": [[...], [...], [...]],
      "model": "sentence-transformers/all-MiniLM-L6-v2",
      "embedding_size": 384
    }
    ```
  - **Error Response (empty texts):**
    ```json
    {
      "detail": "No texts provided."
    }
    ```
  - **Notes:**
    - The order of embeddings matches the order of input texts.
    - All embeddings are generated using the specified model.
    - The endpoint is efficient for batch processing and reduces network overhead.

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


## Deploying on cloud
ssh username@your_vm_ip


---

For more details, see the [Cloud Run Quickstart](https://cloud.google.com/run/docs/quickstarts/build-and-deploy).

### Problems in the deployment in cloud run
When a model is requested for the first time with transformer, it downloads the model and stores it in a file cache. It serves the request from the file cache subsequently.

Google cloud run, when run on request based billing with zero minimum instances, deallocates the machine after a few minutes of idling (probably around 15 minutes). Such an instance is free right now. The way Dockerfile has been configured, it saves the model in the Docker image itself, so when the instance is spawn again, it only needs to load it into memory from file. Right now this is taking ~40 seconds. Also, serving the requests is taking around 6-9 seconds, after the warm up. 

I am trying a pinging solution to keep the instance warm, always.

---

## Docker + Nginx Production Deployment

### 1. Prerequisites
- Docker and Docker Compose installed (setup.sh will install if missing)
- Nginx installed and configured for SSL (see below)
- Your app code cloned to the VM (e.g., /home/ubuntu/genai_inference_apis_self_hosted)

### 2. Quick SSH Workflow

1. **SSH into your VM**
2. **Update code and deploy:**
   ```bash
   git pull
   bash setup.sh
   ```
   - This will build and start the app using Docker Compose.
   - The app will run as the container `genai_inference_apis_self_hosted` and expose port 8080 internally.

3. **Nginx Configuration (on host):**
   - Nginx should listen on ports 80/443 and proxy to `localhost:8080`.
   - Example config:
     ```nginx
     server {
         listen 443 ssl;
         server_name your.domain.com;

         ssl_certificate /etc/letsencrypt/live/your.domain.com/fullchain.pem;
         ssl_certificate_key /etc/letsencrypt/live/your.domain.com/privkey.pem;

         location / {
             proxy_pass http://127.0.0.1:8080;
             proxy_set_header Host $host;
             proxy_set_header X-Real-IP $remote_addr;
             proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
             proxy_set_header X-Forwarded-Proto $scheme;
         }
     }

     server {
         listen 80;
         server_name your.domain.com;
         return 301 https://$host$request_uri;
     }
     ```
   - Reload Nginx after changes:
     ```bash
     sudo systemctl reload nginx
     ```

4. **To update the app:**
   ```bash
   git pull
   bash setup.sh
   ```

---

## Development vs. Production

- **Development:**
  - Run Uvicorn directly, access via `http://localhost:8080`.
- **Production:**
  - Use Docker Compose and Nginx as described above.
  - Only Nginx is exposed to the public; Uvicorn runs in the container and is not public.

---