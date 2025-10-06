# Deploying on Oracle Cloud

This guide explains how to deploy the project on Oracle Cloud, including networking, instance setup, and troubleshooting.

## 1. Oracle Cloud Ecosystem Overview

- **Instance:** Like a virtual laptop/server. A core is a physical CPU unit; each core can have multiple threads (hyperthreading). RAM is allocated per instance.
- **vNIC:** Virtual network interface card, like a NIC in a laptop.
- **VCN (Virtual Cloud Network):** Private network for your account, like a university LAN. Each machine has a private IP.
- **Subnet:** Subdivision of a VCN, like a department subnet. Each gets a block of private IPs. vNICs connect to subnets.
- **Network Security List:** Controls which ports/IPs are open for a subnet.
- **NSG (Network Security Group):** Like a security list, but at the instance level.
- **Gateways:** Control how subnets connect to the outside world (Internet Gateway, NAT, etc.).
- **Route Table:** Controls routing for a subnet.

A successful public instance will:
- Have an instance with a vNIC attached to a subnet
- Subnet has a security list with correct ingress/egress rules
- Instance has a public IP (ephemeral or reserved)
- Subnet is connected to a gateway via the route table
- Instance is connected to an NSG with correct rules

## 2. First-Time Setup
1. **Create and configure an instance** (choose shape, RAM, etc.)
2. **Set up VCN, subnet, security list, NSG, and public IP**
3. **SSH into your instance**
4. **Clone the repo and run setup:**
   ```bash
   git clone <repo-url>
   cd genai_inference_apis_self_hosted
   bash setup.sh
   ```
5. **Configure DNS (if needed)**
6. **Check Nginx and firewall rules**

## 3. Updating the Deployment
- Pull latest code: `git pull`
- Run: `bash setup.sh`
- This will rebuild and restart the app and update Nginx/SSL as needed.

## 4. Troubleshooting & Useful Commands
- **Check if requests reach the instance:**
  ```bash
  sudo tcpdump port 8080
  ```
- **Check Nginx access log:**
  ```bash
  tail -f /var/log/nginx/access.log
  ```
- **Check firewall rules:**
  ```bash
  sudo iptables -L -n
  sudo iptables -I INPUT -p tcp --dport 8080 -j ACCEPT
  sudo sh -c "iptables-save > /etc/iptables/rules.v4"
  ```
- **Nginx config location:**
  `/etc/nginx/sites-enabled/`
- **Reload Nginx:**
  ```bash
  sudo systemctl reload nginx
  ```

For more, see [nginx_unix_troubleshooting.md](nginx_unix_troubleshooting.md)
