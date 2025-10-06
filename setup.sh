#!/bin/bash
set -e

APP_DIR="/home/ubuntu/genai_inference_apis_self_hosted"
APP_NAME="genai_inference_apis_self_hosted"
DOMAIN="sattvium.ddns.net"
EMAIL="sushilm.iitb.dev@gmail.com"

# Function to check if a port is in use by an unexpected process
check_port_usage() {
  local port=$1
  local expected=$2
  local output
  output=$(sudo lsof -i :$port -sTCP:LISTEN -nP | grep -v COMMAND || true)
  if [[ -n "$output" ]]; then
    if [[ "$output" != *"$expected"* ]]; then
      echo "[ERROR] Port $port is already in use by another process:"
      echo "$output"
      echo "Please stop the process using port $port and rerun this script."
      exit 1
    fi
  fi
}

# Function to check and allow a port in iptables if not already allowed
ensure_iptables_accept() {
  local port=$1
  if ! sudo iptables -C INPUT -p tcp --dport $port -j ACCEPT 2>/dev/null; then
    echo "[INFO] Allowing TCP port $port in iptables..."
    sudo iptables -I INPUT -p tcp --dport $port -j ACCEPT
    sudo sh -c "iptables-save > /etc/iptables/rules.v4"
  fi
}

# Check for port usage
check_port_usage 80 "nginx"
check_port_usage 443 "nginx"
check_port_usage 8080 "nginx"

# Ensure iptables allows required ports
ensure_iptables_accept 80
ensure_iptables_accept 443
ensure_iptables_accept 8080

# Install Docker if not present
if ! command -v docker &> /dev/null; then
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker $USER
fi

# Install Docker Compose v2 if not present
if ! docker compose version &> /dev/null; then
  echo "Installing Docker Compose v2..."
  DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
  mkdir -p $DOCKER_CONFIG/cli-plugins
  curl -SL https://github.com/docker/compose/releases/download/v2.29.7/docker-compose-linux-x86_64 \
    -o $DOCKER_CONFIG/cli-plugins/docker-compose
  chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
fi

# Optional: backward compatibility alias for older scripts
if ! command -v docker-compose &> /dev/null; then
  sudo ln -s $(which docker) /usr/local/bin/docker-compose || true
fi

cd "$APP_DIR"
echo "Building and starting $APP_NAME with docker compose..."
docker compose up -d --build

echo "Configuring Nginx as a reverse proxy..."
# Install Nginx if not present
if ! command -v nginx &> /dev/null; then
  sudo apt update
  sudo apt install -y nginx
fi

NGINX_CONF="/etc/nginx/sites-available/$APP_NAME"

# HTTPS config
sudo tee $NGINX_CONF > /dev/null <<EOL
server {
    listen 443 ssl;
    server_name $DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL
sudo ln -sf $NGINX_CONF /etc/nginx/sites-enabled/

# HTTP config for local testing
sudo tee /etc/nginx/sites-available/${APP_NAME}_http > /dev/null <<EOL
server {
    listen 8080;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:8081;
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
# Install Certbot with Nginx plugin if not present
if ! command -v certbot &> /dev/null; then
  sudo apt-get update
  sudo apt-get install -y certbot python3-certbot-nginx
fi

if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
  echo "Obtaining SSL certificate using Certbot Nginx plugin..."
  sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m $EMAIL --redirect
else
  echo "SSL certificate already exists for $DOMAIN."
fi

# Ensure Certbot auto-renewal timer is enabled
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

echo "Nginx is configured to proxy to your Docker app on port 8080 with SSL (port 443)."
echo "Certificate auto-renewal is enabled via Certbot."
echo "Done. To update, just git pull and rerun this script."
