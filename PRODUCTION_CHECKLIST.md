# Production Deployment Checklist

## 🚀 Pre-Deployment Checklist

### ✅ Environment Setup
- [ ] Python 3.9+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Environment variables configured (copy `config/production.env` to `.env`)
- [ ] SSL certificates obtained and configured
- [ ] Domain name configured and DNS pointing to server

### ✅ Security Configuration
- [ ] Change default SECRET_KEY in environment variables
- [ ] Configure ALLOWED_ORIGINS for your domain
- [ ] Set up firewall rules (ports 80, 443, 22 only)
- [ ] Configure fail2ban for intrusion prevention
- [ ] Set up SSL/TLS certificates (Let's Encrypt recommended)
- [ ] Review and update nginx security headers

### ✅ Model and Data Files
- [ ] Verify `src/xgboost_model.pkl` is present and accessible
- [ ] Verify `src/preprocessing_config.py` is present and accessible
- [ ] Test model loading with health check endpoint
- [ ] Create initial backup of model files

### ✅ Application Configuration
- [ ] Set FLASK_ENV=production
- [ ] Set DEBUG=False
- [ ] Configure appropriate log levels
- [ ] Set up log rotation
- [ ] Configure Gunicorn workers based on CPU cores

### ✅ Database and Storage (if applicable)
- [ ] Set up database connections (if using database logging)
- [ ] Configure Redis (if using caching)
- [ ] Set up backup storage location
- [ ] Test backup and restore procedures

### ✅ Monitoring and Logging
- [ ] Configure log directories with proper permissions
- [ ] Set up log rotation (logrotate)
- [ ] Install and configure monitoring tools
- [ ] Set up health check monitoring
- [ ] Configure alerting (email, Slack, etc.)

### ✅ Load Balancing and Scaling
- [ ] Configure nginx reverse proxy
- [ ] Set up multiple application instances (if needed)
- [ ] Configure load balancing
- [ ] Test failover scenarios

## 🔧 Deployment Steps

### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.9 python3.9-venv nginx supervisor git curl

# Create application user
sudo useradd -m -s /bin/bash drugapi
sudo usermod -aG www-data drugapi
```

### 2. Application Deployment
```bash
# Switch to application user
sudo su - drugapi

# Clone/upload application
git clone <repository-url> drug-interaction-api
cd drug-interaction-api

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test application
python app.py &
curl http://localhost:5000/health
kill %1
```

### 3. Service Configuration
```bash
# Copy systemd service file
sudo cp deployment/drug-interaction-api.service /etc/systemd/system/

# Copy nginx configuration
sudo cp deployment/nginx.conf /etc/nginx/sites-available/drug-interaction-api
sudo ln -s /etc/nginx/sites-available/drug-interaction-api /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable drug-interaction-api
sudo systemctl start drug-interaction-api
sudo systemctl reload nginx
```

### 4. SSL Certificate Setup
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

### 5. Monitoring Setup
```bash
# Set up log directories
sudo mkdir -p /var/log/drug-api
sudo chown drugapi:www-data /var/log/drug-api

# Install monitoring script
sudo cp scripts/health_monitor.py /usr/local/bin/
sudo chmod +x /usr/local/bin/health_monitor.py

# Add to crontab for regular monitoring
echo "*/5 * * * * /usr/local/bin/health_monitor.py --alerts-only" | sudo crontab -u drugapi -
```

## 🧪 Post-Deployment Testing

### ✅ Basic Functionality Tests
- [ ] Health check endpoint responds correctly
- [ ] Basic prediction request works
- [ ] Multi-drug prediction works
- [ ] Error handling works correctly
- [ ] Rate limiting is functioning

### ✅ Performance Tests
- [ ] Response times are acceptable (< 3 seconds)
- [ ] Server handles concurrent requests
- [ ] Memory usage is stable
- [ ] CPU usage is reasonable

### ✅ Security Tests
- [ ] HTTPS is working correctly
- [ ] HTTP redirects to HTTPS
- [ ] Security headers are present
- [ ] Rate limiting prevents abuse
- [ ] Unauthorized access is blocked

### ✅ Monitoring Tests
- [ ] Health monitoring script works
- [ ] Log files are being created
- [ ] Backup scripts work correctly
- [ ] Alerting is functioning

## 📊 Performance Benchmarks

### Expected Performance Metrics
- **Response Time**: < 2.5 seconds for 2-10 drugs
- **Throughput**: 100+ requests per minute
- **Memory Usage**: < 1GB per worker
- **CPU Usage**: < 50% under normal load

### Load Testing Commands
```bash
# Test basic endpoint
ab -n 100 -c 10 https://yourdomain.com/

# Test prediction endpoint
ab -n 50 -c 5 -p test_data.json -T application/json https://yourdomain.com/predict-interactions
```

## 🚨 Troubleshooting Guide

### Common Issues

1. **Service won't start**
   ```bash
   sudo journalctl -u drug-interaction-api -f
   sudo systemctl status drug-interaction-api
   ```

2. **Model loading errors**
   ```bash
   # Check file permissions
   ls -la src/xgboost_model.pkl
   
   # Test model loading
   python -c "import pickle; pickle.load(open('src/xgboost_model.pkl', 'rb'))"
   ```

3. **Nginx errors**
   ```bash
   sudo nginx -t
   sudo tail -f /var/log/nginx/error.log
   ```

4. **High memory usage**
   ```bash
   # Monitor memory
   htop
   
   # Reduce Gunicorn workers
   # Edit gunicorn.conf.py and restart service
   ```

## 📋 Maintenance Tasks

### Daily
- [ ] Check service status
- [ ] Review error logs
- [ ] Monitor resource usage

### Weekly
- [ ] Run health monitoring report
- [ ] Check backup integrity
- [ ] Review performance metrics
- [ ] Update security patches

### Monthly
- [ ] Full backup verification
- [ ] Performance optimization review
- [ ] Security audit
- [ ] Dependency updates

## 🆘 Emergency Procedures

### Service Recovery
```bash
# Restart application service
sudo systemctl restart drug-interaction-api

# Restart nginx
sudo systemctl restart nginx

# Check all services
sudo systemctl status drug-interaction-api nginx
```

### Rollback Procedure
```bash
# Restore from backup
python scripts/backup_model.py restore --backup-name model_backup_YYYYMMDD_HHMMSS --confirm

# Restart service
sudo systemctl restart drug-interaction-api
```

### Emergency Contacts
- System Administrator: [contact info]
- Application Developer: [contact info]
- Infrastructure Team: [contact info]

## ✅ Sign-off

- [ ] Development Team Lead: _________________ Date: _______
- [ ] System Administrator: _________________ Date: _______
- [ ] Security Officer: _____________________ Date: _______
- [ ] Operations Manager: ___________________ Date: _______

**Deployment completed successfully on:** _______________
