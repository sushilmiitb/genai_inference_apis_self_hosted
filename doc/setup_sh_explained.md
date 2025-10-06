# setup.sh Explained

This document explains the sequence of execution in `setup.sh` and what happens during first-time setup vs. subsequent updates.

## Sequence of Execution

1. **Check and allow required ports in iptables**
   - Ensures ports 80, 443, and 8080 are open in the firewall.
2. **Install Docker and Docker Compose if missing**
   - Installs Docker and Docker Compose v2 if not present.
3. **Build and start the app with Docker Compose**
   - Builds the Docker image and starts the container.
4. **Install Nginx if missing**
   - Installs Nginx web server if not present.
5. **Write and enable only the HTTP Nginx config**
   - Creates a config for port 8080 and enables it.
6. **Reload Nginx with only HTTP config**
   - Ensures Nginx starts without SSL errors.
7. **Install Certbot if missing**
   - Installs Certbot and the Nginx plugin for SSL certificates.
8. **Obtain SSL certificate with Certbot**
   - Uses Certbot to get a certificate for your domain (if not already present).
9. **Write and enable the HTTPS Nginx config**
   - Creates a config for port 443 with SSL and enables it.
10. **Reload Nginx with both HTTP and HTTPS configs**
    - Nginx now serves both HTTP and HTTPS.
11. **Enable Certbot auto-renewal**
    - Ensures SSL certificates are renewed automatically.

## First-Time Setup vs. Updates

- **First-Time Setup:**
  - Installs all dependencies (Docker, Nginx, Certbot)
  - Opens firewall ports
  - Obtains SSL certificate
  - Sets up and starts everything from scratch
- **Subsequent Updates:**
  - Pull latest code and run `setup.sh` again
  - Rebuilds Docker image and restarts the app
  - Updates Nginx configs if needed
  - Renews SSL certificate if needed
  - Skips already-installed dependencies and existing certificates

## References
- For more, see the top-level [README.md](../README.md)
- For troubleshooting, see [nginx_unix_troubleshooting.md](nginx_unix_troubleshooting.md)
