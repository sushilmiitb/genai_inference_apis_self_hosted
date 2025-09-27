#!/bin/bash
set -e

APP_DIR="/home/ubuntu/genai_inference_apis_self_hosted"  # Change this to your actual app path
APP_NAME="genai_inference_apis_self_hosted"
DOMAIN="sattvium.ddns.net"  # <-- CHANGE THIS to your actual domain
EMAIL="sushilm.iitb.dev@gmail.com"  # <-- CHANGE THIS to your email

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

echo "Configuring Nginx as a reverse proxy..."
# Install Nginx if not present
if ! command -v nginx &> /dev/null; then
  sudo apt update
  sudo apt install -y nginx
fi

NGINX_CONF="/etc/nginx/sites-available/$APP_NAME"

# Write Nginx config for HTTPS (SSL) on port 443
sudo tee $NGINX_CONF > /dev/null <<EOL
server {
    listen 443 ssl;
    server_name $DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL
sudo ln -sf $NGINX_CONF /etc/nginx/sites-enabled/

# Also write a simple HTTP config for local testing (optional)
sudo tee /etc/nginx/sites-available/${APP_NAME}_http > /dev/null <<EOL
server {
    listen 8080;
    server_name $DOMAIN;
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL
sudo ln -sf /etc/nginx/sites-available/${APP_NAME}_http /etc/nginx/sites-enabled/

sudo nginx -t && sudo systemctl reload nginx

echo "Checking for SSL certificate..."
# Install Certbot if not present
if ! command -v certbot &> /dev/null; then
  sudo apt-get update && sudo apt-get install -y certbot
fi

if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
  echo "Obtaining SSL certificate with Certbot using TLS-ALPN-01 challenge..."
  sudo systemctl stop nginx
  sudo certbot certonly --standalone --preferred-challenges tls-alpn-01 \
    -d $DOMAIN --non-interactive --agree-tos -m $EMAIL
  sudo systemctl start nginx
else
  echo "SSL certificate already exists for $DOMAIN."
fi

echo "Nginx is configured to proxy to your Docker app on port 8080 with SSL (port 443)."

echo "Done. To update, just git pull and rerun this script."
