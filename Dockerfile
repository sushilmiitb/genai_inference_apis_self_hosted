# Use official Python image
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port (Cloud Run expects 8080)
EXPOSE 8080

# Set environment variable for production
ENV APP_ENV=production

# Start the server
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080" ]
