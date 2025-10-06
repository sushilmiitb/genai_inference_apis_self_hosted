# Gen AI Inference APIs Self Hosted

## Overview
This project exposes inference APIs for generating embeddings using Hugging Face models. It is designed for self-hosted use, allowing you to run open-source models locally and avoid third-party API costs.

---

## Quickstart: Local Development

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
3. **Run tests:**
   ```bash
   pytest -v
   ```

For detailed development setup, see [doc/development_setup.md](doc/development_setup.md)

---

## Deployment

- **Google Cloud:** See [doc/deploy_google_cloud.md](doc/deploy_google_cloud.md)
- **Oracle Cloud:** See [doc/deploy_oracle_cloud.md](doc/deploy_oracle_cloud.md)
- **Production (Docker + Nginx):** See [doc/deploy_google_cloud.md](doc/deploy_google_cloud.md) or [doc/deploy_oracle_cloud.md](doc/deploy_oracle_cloud.md)

---

## How to Update

- **Development:**
  - Pull latest code: `git pull`
  - Reinstall dependencies if needed: `pip install -r requirements.txt`
  - Restart the server.
- **Production:**
  - Pull latest code: `git pull`
  - Run: `bash setup.sh`
  - This will rebuild and restart the Docker containers and update Nginx configs as needed.

---

## How setup.sh Works

The `setup.sh` script automates the setup of Docker, Nginx, SSL certificates, and firewall rules for production deployment. It:
- Checks and installs Docker, Docker Compose, and Nginx if missing
- Builds and starts the app with Docker Compose
- Configures Nginx as a reverse proxy (HTTP first, then HTTPS after SSL is obtained)
- Obtains SSL certificates with Certbot
- Ensures firewall rules are set
- Enables auto-renewal for SSL certificates

See [doc/setup_sh_explained.md](doc/setup_sh_explained.md) for a detailed, step-by-step explanation, including what happens on first-time setup and on subsequent updates.

---

## API Endpoints

- See [Interactive API Docs](http://127.0.0.1:8000/docs) when running locally.
- For endpoint details, see [doc/development_setup.md](doc/development_setup.md)

---

## More Documentation

- [Development Setup](doc/development_setup.md)
- [Google Cloud Deployment](doc/deploy_google_cloud.md)
- [Oracle Cloud Deployment](doc/deploy_oracle_cloud.md)
- [Nginx & Unix Troubleshooting](doc/nginx_unix_troubleshooting.md)
- [setup.sh Explained](doc/setup_sh_explained.md)

---

## Contributing

Contributions are welcome! Please see [doc/development_setup.md](doc/development_setup.md) for development guidelines.