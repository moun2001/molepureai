# Docker Deployment Guide

## 🐳 Overview

This guide covers deploying the Drug Interaction Prediction API using Docker containers. Docker provides a consistent, portable deployment environment across different platforms.

## 📋 Prerequisites

- Docker Engine 20.10+ installed
- Docker Compose 2.0+ (optional, for multi-container setup)
- At least 2GB RAM available
- 5GB disk space

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

1. **Navigate to project directory:**
   ```bash
   cd drug-interaction-api
   ```

2. **Build and start services:**
   ```bash
   docker-compose up --build -d
   ```

3. **Verify deployment:**
   ```bash
   curl http://localhost:5000/health
   ```

### Option 2: Docker Build and Run

1. **Build the image:**
   ```bash
   docker build -t drug-interaction-api .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name drug-api \
     -p 5000:5000 \
     -e FLASK_ENV=production \
     drug-interaction-api
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file for configuration:

```bash
# Server Configuration
HOST=0.0.0.0
PORT=5000
FLASK_ENV=production
DEBUG=False

# Logging
LOG_LEVEL=INFO

# Performance
WORKERS=2
TIMEOUT=120

# Security
ALLOWED_ORIGINS=*
```

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  drug-interaction-api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - HOST=0.0.0.0
      - PORT=5000
      - DEBUG=False
      - LOG_LEVEL=INFO
    volumes:
      - ./src/xgboost_model.pkl:/app/src/xgboost_model.pkl:ro
      - ./src/preprocessing_config.py:/app/src/preprocessing_config.py:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'

  # Optional: Nginx reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deployment/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - drug-interaction-api
    restart: unless-stopped
    profiles:
      - production
```

## 🔒 Production Configuration

### Nginx Reverse Proxy

Create `deployment/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream drug_api {
        server drug-interaction-api:5000;
    }

    server {
        listen 80;
        server_name your-domain.com;

        # Rate limiting
        limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

        location / {
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
        }

        # Health check endpoint
        location /health {
            proxy_pass http://drug_api/health;
            access_log off;
        }
    }
}
```

### SSL/HTTPS Configuration

For HTTPS, add SSL configuration to nginx:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # ... rest of configuration
}
```

## 📊 Monitoring and Logging

### Health Checks

The container includes built-in health checks:

```bash
# Check container health
docker ps

# View health check logs
docker inspect --format='{{json .State.Health}}' drug-api
```

### Log Management

```bash
# View container logs
docker logs drug-api

# Follow logs in real-time
docker logs -f drug-api

# Limit log output
docker logs --tail 100 drug-api
```

### Resource Monitoring

```bash
# Monitor resource usage
docker stats drug-api

# Detailed container info
docker inspect drug-api
```

## 🔄 Scaling and Load Balancing

### Horizontal Scaling

Scale with Docker Compose:

```bash
# Scale to 3 instances
docker-compose up --scale drug-interaction-api=3 -d
```

### Load Balancer Configuration

Update nginx configuration for multiple instances:

```nginx
upstream drug_api {
    least_conn;
    server drug-interaction-api_1:5000;
    server drug-interaction-api_2:5000;
    server drug-interaction-api_3:5000;
}
```

## 🛠 Maintenance

### Updates and Deployments

```bash
# Pull latest changes
git pull origin main

# Rebuild and deploy
docker-compose build --no-cache
docker-compose up -d

# Zero-downtime deployment
docker-compose up -d --no-deps --build drug-interaction-api
```

### Backup and Recovery

```bash
# Backup model files
docker cp drug-api:/app/src/xgboost_model.pkl ./backup/

# Backup configuration
docker cp drug-api:/app/src/preprocessing_config.py ./backup/
```

## 🐛 Troubleshooting

### Common Issues

1. **Container won't start:**
   ```bash
   # Check logs
   docker logs drug-api
   
   # Check if model files are accessible
   docker exec drug-api ls -la /app/src/
   ```

2. **Health check failing:**
   ```bash
   # Test health endpoint manually
   docker exec drug-api curl http://localhost:5000/health
   ```

3. **Memory issues:**
   ```bash
   # Check memory usage
   docker stats drug-api
   
   # Increase memory limits in docker-compose.yml
   ```

4. **Port conflicts:**
   ```bash
   # Check what's using port 5000
   netstat -tulpn | grep 5000
   
   # Use different port
   docker run -p 8080:5000 drug-interaction-api
   ```

### Performance Tuning

1. **Optimize Gunicorn workers:**
   ```bash
   # Calculate optimal workers: (2 x CPU cores) + 1
   docker run -e WORKERS=4 drug-interaction-api
   ```

2. **Memory optimization:**
   ```bash
   # Set memory limits
   docker run --memory=2g drug-interaction-api
   ```

3. **CPU optimization:**
   ```bash
   # Limit CPU usage
   docker run --cpus=1.0 drug-interaction-api
   ```

## 🔐 Security Best Practices

1. **Run as non-root user** (already configured in Dockerfile)
2. **Use read-only model files** (configured in docker-compose.yml)
3. **Implement rate limiting** (nginx configuration)
4. **Use HTTPS in production**
5. **Regular security updates:**
   ```bash
   # Update base image
   docker pull python:3.9-slim
   docker-compose build --no-cache
   ```

## 📈 Production Checklist

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Rate limiting configured
- [ ] Monitoring setup
- [ ] Log rotation configured
- [ ] Backup strategy implemented
- [ ] Health checks working
- [ ] Resource limits set
- [ ] Security hardening applied
- [ ] Load testing completed

## 🆘 Support

For Docker-specific issues:
- Check Docker logs: `docker logs drug-api`
- Verify container health: `docker ps`
- Test connectivity: `docker exec drug-api curl http://localhost:5000/health`
- Review resource usage: `docker stats drug-api`
