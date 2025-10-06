# Deploying on Google Cloud

This guide explains how to deploy the project on Google Cloud (Cloud Run or VM).

## 1. Prerequisites
- Google Cloud project
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed
- Authenticated: `gcloud auth login`
- Project set: `gcloud config set project <your-project-id>`
- Enable required APIs:
  ```bash
  gcloud services enable run.googleapis.com containerregistry.googleapis.com cloudbuild.googleapis.com
  ```

## 2. Build and Deploy (Cloud Run)
1. Submit your code to Google Cloud Build:
   ```bash
   gcloud builds submit --tag gcr.io/<your-project-id>/genai-inference-api
   ```
2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy genai-inference-api \
     --image gcr.io/<your-project-id>/genai-inference-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 2Gi \
     --timeout 300
   ```
   - Adjust `--region`, `--memory`, and `--timeout` as needed.
3. (Optional) Set environment variables:
   ```bash
   gcloud run services update genai-inference-api \
     --update-env-vars APP_ENV=production
   ```
4. Access your service:
   - Cloud Run will provide a service URL.
   - Visit `https://<your-service-url>/docs` for API docs.

## 3. Updating the Deployment
- Pull latest code: `git pull`
- Rebuild and redeploy as above.

## 4. VM-based Deployment
- See [../README.md](../README.md#docker--nginx-production-deployment) for Docker + Nginx setup.
- For troubleshooting, see [nginx_unix_troubleshooting.md](nginx_unix_troubleshooting.md)
