#!/bin/bash
set -e

APP_DIR="/home/ubuntu/genai_inference_apis_self_hosted"  # Change this to your actual app path
APP_NAME="genai_inference_apis_self_hosted"

# Install Docker if not present
if ! command -v docker &> /dev/null; then
  curl -fsSL https://get.docker.com | sh
fi
# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
  sudo apt-get update && sudo apt-get install -y docker-compose
fi

cd "$APP_DIR"

echo "Building and starting $APP_NAME with docker-compose..."
docker-compose up -d --build

echo "Done. To update, just git pull and rerun this script."
