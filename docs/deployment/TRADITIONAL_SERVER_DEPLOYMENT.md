# Traditional Server Deployment Guide

## 🖥️ Overview

This guide covers deploying the Drug Interaction Prediction API on traditional Linux servers (Ubuntu/CentOS/RHEL) using systemd, nginx, and Python virtual environments.

## 📋 Prerequisites

- Linux server (Ubuntu 20.04+ or CentOS 8+ recommended)
- Root or sudo access
- At least 2GB RAM and 10GB disk space
- Python 3.9+ installed

## 🚀 Ubuntu/Debian Deployment

### 1. System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx supervisor git curl

# Install Python 3.9 if not available
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install -y python3.9 python3.9-venv python3.9-dev
```

### 2. Create Application User

```bash
# Create dedicated user for the application
sudo useradd -m -s /bin/bash drugapi
sudo usermod -aG www-data drugapi

# Switch to application user
sudo su - drugapi
```

### 3. Application Setup

```bash
# Clone repository
git clone https://github.com/your-username/drug-interaction-api.git
cd drug-interaction-api

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Test application
python app.py &
curl http://localhost:5000/health
kill %1  # Stop test server
```

### 4. Systemd Service Configuration

Create `/etc/systemd/system/drug-interaction-api.service`:

```ini
[Unit]
Description=Drug Interaction Prediction API
After=network.target

[Service]
Type=exec
User=drugapi
Group=www-data
WorkingDirectory=/home/drugapi/drug-interaction-api
Environment=PATH=/home/drugapi/drug-interaction-api/venv/bin
Environment=FLASK_ENV=production
Environment=DEBUG=False
Environment=LOG_LEVEL=INFO
Environment=HOST=127.0.0.1
Environment=PORT=5000
ExecStart=/home/drugapi/drug-interaction-api/venv/bin/gunicorn --config config/gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3
KillMode=mixed
TimeoutStopSec=5

[Install]
WantedBy=multi-user.target
```

### 5. Nginx Configuration

Create `/etc/nginx/sites-available/drug-interaction-api`:

```nginx
upstream drug_api {
    server 127.0.0.1:5000;
}

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    location / {
        # Rate limiting
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://drug_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 120s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }

    # Health check endpoint (no rate limiting)
    location /health {
        proxy_pass http://drug_api/health;
        access_log off;
    }

    # Static files (if any)
    location /static {
        alias /home/drugapi/drug-interaction-api/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Logging
    access_log /var/log/nginx/drug-api-access.log;
    error_log /var/log/nginx/drug-api-error.log;
}
```

### 6. SSL/HTTPS Setup with Let's Encrypt

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

### 7. Service Management

```bash
# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable drug-interaction-api
sudo systemctl start drug-interaction-api

# Enable nginx site
sudo ln -s /etc/nginx/sites-available/drug-interaction-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Check service status
sudo systemctl status drug-interaction-api
sudo systemctl status nginx
```

## 🔴 CentOS/RHEL Deployment

### 1. System Preparation

```bash
# Update system
sudo dnf update -y

# Install EPEL repository
sudo dnf install -y epel-release

# Install required packages
sudo dnf install -y python39 python39-pip python39-devel nginx supervisor git curl gcc

# Install additional development tools
sudo dnf groupinstall -y "Development Tools"
```

### 2. SELinux Configuration

```bash
# Check SELinux status
sestatus

# If SELinux is enforcing, configure policies
sudo setsebool -P httpd_can_network_connect 1
sudo semanage port -a -t http_port_t -p tcp 5000

# Or temporarily disable SELinux (not recommended for production)
sudo setenforce 0
```

### 3. Firewall Configuration

```bash
# Configure firewalld
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

### 4. Application Setup

Follow the same steps as Ubuntu, but use `python3.9` instead of `python3`:

```bash
# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 🔧 Production Configuration

### Gunicorn Configuration

Update `config/gunicorn.conf.py` for production:

```python
import multiprocessing
import os

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = min(multiprocessing.cpu_count() * 2 + 1, 8)
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2

# Restart workers
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "/var/log/drug-api/access.log"
errorlog = "/var/log/drug-api/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "drug-interaction-api"

# Server mechanics
daemon = False
pidfile = "/var/run/drug-api/drug-api.pid"
user = "drugapi"
group = "www-data"

# Preload application
preload_app = True
```

### Log Directory Setup

```bash
# Create log directories
sudo mkdir -p /var/log/drug-api
sudo mkdir -p /var/run/drug-api
sudo chown drugapi:www-data /var/log/drug-api
sudo chown drugapi:www-data /var/run/drug-api

# Setup log rotation
sudo tee /etc/logrotate.d/drug-api << EOF
/var/log/drug-api/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 drugapi www-data
    postrotate
        systemctl reload drug-interaction-api
    endscript
}
EOF
```

## 📊 Monitoring and Maintenance

### System Monitoring

```bash
# Monitor service status
sudo systemctl status drug-interaction-api

# View logs
sudo journalctl -u drug-interaction-api -f

# Monitor resource usage
htop
iostat -x 1
free -h
df -h
```

### Application Monitoring

```bash
# Check application health
curl http://localhost/health

# Monitor nginx access logs
sudo tail -f /var/log/nginx/drug-api-access.log

# Monitor application logs
sudo tail -f /var/log/drug-api/error.log
```

### Performance Monitoring Script

Create `/home/drugapi/monitor.sh`:

```bash
#!/bin/bash

LOG_FILE="/var/log/drug-api/monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Check service status
if systemctl is-active --quiet drug-interaction-api; then
    STATUS="RUNNING"
else
    STATUS="STOPPED"
    echo "$DATE - Service is stopped, attempting restart" >> $LOG_FILE
    sudo systemctl restart drug-interaction-api
fi

# Check health endpoint
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health)

# Log status
echo "$DATE - Service: $STATUS, Health: $HEALTH_STATUS" >> $LOG_FILE

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$DATE - WARNING: Disk usage is ${DISK_USAGE}%" >> $LOG_FILE
fi

# Check memory usage
MEM_USAGE=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
if (( $(echo "$MEM_USAGE > 80" | bc -l) )); then
    echo "$DATE - WARNING: Memory usage is ${MEM_USAGE}%" >> $LOG_FILE
fi
```

Add to crontab:
```bash
# Run monitoring every 5 minutes
*/5 * * * * /home/drugapi/monitor.sh
```

## 🔄 Updates and Deployment

### Automated Deployment Script

Create `/home/drugapi/deploy.sh`:

```bash
#!/bin/bash

set -e

APP_DIR="/home/drugapi/drug-interaction-api"
BACKUP_DIR="/home/drugapi/backups"
DATE=$(date '+%Y%m%d_%H%M%S')

echo "Starting deployment at $(date)"

# Create backup
mkdir -p $BACKUP_DIR
cp -r $APP_DIR $BACKUP_DIR/backup_$DATE

# Pull latest changes
cd $APP_DIR
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run tests
python -m pytest tests/ || {
    echo "Tests failed, rolling back"
    rm -rf $APP_DIR
    cp -r $BACKUP_DIR/backup_$DATE $APP_DIR
    exit 1
}

# Restart service
sudo systemctl restart drug-interaction-api

# Verify deployment
sleep 10
if curl -f http://localhost/health; then
    echo "Deployment successful"
    # Clean old backups (keep last 5)
    ls -t $BACKUP_DIR | tail -n +6 | xargs -I {} rm -rf $BACKUP_DIR/{}
else
    echo "Health check failed, rolling back"
    sudo systemctl stop drug-interaction-api
    rm -rf $APP_DIR
    cp -r $BACKUP_DIR/backup_$DATE $APP_DIR
    sudo systemctl start drug-interaction-api
    exit 1
fi

echo "Deployment completed at $(date)"
```

## 🔐 Security Hardening

### System Security

```bash
# Update system regularly
sudo apt update && sudo apt upgrade -y

# Configure automatic security updates
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# Install fail2ban
sudo apt install -y fail2ban

# Configure fail2ban for nginx
sudo tee /etc/fail2ban/jail.local << EOF
[nginx-http-auth]
enabled = true
filter = nginx-http-auth
logpath = /var/log/nginx/drug-api-error.log
maxretry = 3
bantime = 3600

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/drug-api-error.log
maxretry = 10
bantime = 600
EOF

sudo systemctl restart fail2ban
```

### Application Security

```bash
# Set proper file permissions
sudo chown -R drugapi:www-data /home/drugapi/drug-interaction-api
sudo chmod -R 755 /home/drugapi/drug-interaction-api
sudo chmod 600 /home/drugapi/drug-interaction-api/config/*.conf

# Secure model files
sudo chmod 644 /home/drugapi/drug-interaction-api/src/xgboost_model.pkl
sudo chmod 644 /home/drugapi/drug-interaction-api/src/preprocessing_config.py
```

## 🚨 Troubleshooting

### Common Issues

1. **Service won't start:**
   ```bash
   sudo journalctl -u drug-interaction-api -n 50
   sudo systemctl status drug-interaction-api
   ```

2. **Permission errors:**
   ```bash
   sudo chown -R drugapi:www-data /home/drugapi/drug-interaction-api
   ```

3. **Port conflicts:**
   ```bash
   sudo netstat -tulpn | grep :5000
   sudo lsof -i :5000
   ```

4. **Nginx errors:**
   ```bash
   sudo nginx -t
   sudo tail -f /var/log/nginx/error.log
   ```

### Performance Issues

1. **High memory usage:**
   - Reduce Gunicorn workers
   - Monitor with `htop` and `free -h`

2. **Slow responses:**
   - Check nginx access logs
   - Monitor application logs
   - Verify model file accessibility

3. **High CPU usage:**
   - Limit concurrent requests
   - Optimize Gunicorn configuration

This completes the traditional server deployment guide with comprehensive setup, monitoring, and maintenance procedures.
