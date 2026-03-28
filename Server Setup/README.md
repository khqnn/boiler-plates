```markdown
# Setup Server

This guide provides step-by-step instructions to set up a production server with **Nginx**, **Docker Compose**, **Git**, and **SSL** (using Certbot). It includes configuration examples, firewall rules, and placeholders for sensitive information such as domain names, email addresses, and repository URLs.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Step 1: System Update and Dependency Installation](#step-1-system-update-and-dependency-installation)
- [Step 2: Configure Nginx](#step-2-configure-nginx)
- [Step 3: Set Up Swap (Optional)](#step-3-set-up-swap-optional)
- [Step 4: Configure Firewall (iptables)](#step-4-configure-firewall-iptables)
- [Step 5: Start and Verify Nginx](#step-5-start-and-verify-nginx)
- [Step 6: Generate SSH Key](#step-6-generate-ssh-key)
- [Step 7: Clone the Repository](#step-7-clone-the-repository)
- [Step 8: Application Initialization](#step-8-application-initialization)
- [Step 9: Install SSL/TLS Certificate](#step-9-install-ssltls-certificate)
- [Step 10: Configure Inbound Rules (Cloud Firewall)](#step-10-configure-inbound-rules-cloud-firewall)
- [Notes and Troubleshooting](#notes-and-troubleshooting)

## Prerequisites
- A server running **Ubuntu 20.04+** (or CentOS/RHEL 7+ with adjustments)
- Root or sudo access
- A domain name pointing to the server’s public IP
- Basic familiarity with the command line

---

## Step 1: System Update and Dependency Installation
Update the package list and install required packages:

```bash
sudo apt update
sudo apt install nginx docker-compose git -y
```

> **For CentOS/RHEL**, replace `apt` with `yum` and ensure EPEL is enabled.

---

## Step 2: Configure Nginx
Create an Nginx configuration file for your application. Replace `<your-domain.com>` with your actual domain (or leave as `_` for testing).

```bash
sudo nano /etc/nginx/conf.d/mydomain.conf
```

Paste the following configuration:

```nginx
server {
    listen 80;
    server_name _;  # Change to your domain, e.g., api-stag.techpurview.co
    location / {
        proxy_pass http://127.0.0.1:8080;  # Adjust to your app’s internal port
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

- If you are proxying to a Docker container or another service, adjust `proxy_pass` accordingly.
- Save and exit.

---

## Step 3: Set Up Swap (Optional)
If your server has low memory (e.g., 1–2 GB), adding swap can help prevent out-of-memory issues:

```bash
sudo fallocate -l 2G /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

Make the swap permanent by adding to `/etc/fstab`:
```bash
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## Step 4: Configure Firewall (iptables)
If your server uses `iptables` and port 80 is blocked, allow HTTP traffic:

```bash
# List current INPUT rules
sudo iptables -L INPUT -n --line-numbers

# Insert a rule at position 5 (adjust the number as needed)
sudo iptables -I INPUT 5 -p tcp --dport 80 -m state --state NEW -j ACCEPT
```

Save the rules (persist across reboots) using `iptables-save` or your distribution’s method.

> **Note**: If you are using **ufw** or a cloud firewall (e.g., AWS Security Groups), manage rules there instead.

---

## Step 5: Start and Verify Nginx
Start Nginx and enable it to run on boot:

```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

Verify that Nginx is running and the configuration is correct:

```bash
sudo nginx -t
sudo systemctl status nginx
```

Test by visiting `http://<your-server-ip>` in a browser. You should see the default Nginx page or your proxied application if it’s already running.

---

## Step 6: Generate SSH Key
Generate an Ed25519 SSH key pair for secure authentication (e.g., to push to GitHub):

```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
```

View and copy the public key:

```bash
cat ~/.ssh/id_ed25519.pub
```

Add this public key to your Git hosting service (GitHub, GitLab, etc.) under **SSH Keys**.

---

## Step 7: Clone the Repository
Replace `<repo-url>` with your repository’s SSH URL and `<repo-name>` with the directory name:

```bash
git clone <repo-url>
cd <repo-name>
```

---

## Step 8: Application Initialization
Follow the instructions in the repository’s own `README.md` or documentation to set up the application. This typically includes:
- Environment variables (create `.env` files)
- Building Docker images or installing dependencies
- Running database migrations
- Starting the application (e.g., with `docker-compose up -d`)

**Important**: Ensure the application listens on the port specified in the Nginx proxy (e.g., `8080`).

---

## Step 9: Install SSL/TLS Certificate
Secure your site with a free Let’s Encrypt certificate using Certbot.

### For Ubuntu / Debian
```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### For CentOS / RHEL
```bash
sudo apt update
sudo apt install python3.12-venv
sudo python3 -m venv /opt/certbot/
sudo /opt/certbot/bin/pip install --upgrade pip
sudo /opt/certbot/bin/pip install certbot certbot-nginx
sudo ln -s /opt/certbot/bin/certbot /usr/bin/certbot
sudo certbot certonly --nginx
sudo certbot install --nginx
```

Follow the interactive prompts, providing your email and domain name. Certbot will automatically modify your Nginx configuration to use HTTPS and set up auto-renewal.

After installation, update your Nginx config to listen on port 443 and redirect HTTP to HTTPS. Certbot usually does this automatically. Verify by visiting `https://your-domain.com`.

---

## Step 10: Configure Inbound Rules (Cloud Firewall)
If your server is hosted on a cloud provider (AWS, GCP, DigitalOcean, etc.), ensure the following ports are open in the firewall / security group:
- **80 (HTTP)**
- **443 (HTTPS)**
- **22 (SSH)** (already open)
- Any other ports your application needs (e.g., `8080` if exposed directly)

Refer to your provider’s documentation to add these rules.

---

## Notes and Troubleshooting

- **Nginx configuration**: Always test with `sudo nginx -t` before reloading.
- **Docker**: If your application uses Docker Compose, make sure the containers are running and the port mapping matches the Nginx proxy pass.
- **SSL renewal**: Certbot’s auto-renewal cron job or systemd timer is usually set up automatically. Check with `sudo certbot renew --dry-run`.
- **Firewall**: If you use `ufw`, allow HTTP/HTTPS with `sudo ufw allow 80/tcp` and `sudo ufw allow 443/tcp`.
- **Swap**: Use `free -h` to check if swap is active. Adjust size based on server memory.
- **Port conflicts**: Ensure no other service is using the same ports as Nginx or your application.

---

## Placeholders Used
| Placeholder                | Description                                      |
|----------------------------|--------------------------------------------------|
| `<your-domain.com>`        | Your fully qualified domain name (e.g., `example.com`) |
| `<your-email@example.com>` | Email address for SSL certificate registration   |
| `<repo-url>`               | SSH URL of your Git repository                   |
| `<repo-name>`              | Name of the directory after cloning              |

Replace these placeholders with your actual values before running commands.
```