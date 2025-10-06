# Nginx & Unix Troubleshooting

This doc explains how to debug network and Nginx issues, manage firewalls, and understand config locations.

## 1. Nginx as a Web Server
- Nginx listens on ports (e.g., 80, 443, 8080) and proxies requests to your app.
- Config files are in `/etc/nginx/sites-enabled/` (one file per port/domain is common).

## 2. Debugging Incoming Requests
- **Check if requests reach the instance:**
  ```bash
  sudo tcpdump port 8080
  ```
- **Check if requests reach Nginx:**
  ```bash
  tail -f /var/log/nginx/access.log
  ```

## 3. Firewall (iptables) Management
- **List rules:**
  ```bash
  sudo iptables -L -n
  ```
- **Allow a port:**
  ```bash
  sudo iptables -I INPUT -p tcp --dport 8080 -j ACCEPT
  ```
- **Save rules permanently:**
  ```bash
  sudo sh -c "iptables-save > /etc/iptables/rules.v4"
  ```

## 4. Nginx Config Management
- **Config location:** `/etc/nginx/sites-enabled/`
- **Edit config:**
  ```bash
  sudo nano /etc/nginx/sites-enabled/<your-config>
  ```
- **Reload Nginx after changes:**
  ```bash
  sudo systemctl reload nginx
  ```

## 5. Oracle Cloud Networking Recap
- Instance: Virtual machine
- vNIC: Virtual network interface
- VCN: Private network
- Subnet: Subdivision of VCN
- Security List: Subnet-level firewall
- NSG: Instance-level firewall
- Gateway: Controls external connectivity
- Route Table: Controls routing

## 6. Best Practices
- Have a config for each port you want to expose.
- Always reload Nginx after changing configs.
- Ensure both Oracle Cloud and internal firewalls allow required ports.
