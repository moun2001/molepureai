# Cloud Platform Deployment Guide

## ☁️ Overview

This guide covers deploying the Drug Interaction Prediction API on major cloud platforms including AWS, Google Cloud Platform (GCP), Microsoft Azure, Heroku, and DigitalOcean.

## 🚀 Heroku Deployment

### Prerequisites
- Heroku CLI installed
- Git repository initialized
- Heroku account

### Step-by-Step Deployment

1. **Create Heroku app:**
   ```bash
   heroku create your-drug-api-name
   ```

2. **Create Procfile:**
   ```bash
   echo "web: gunicorn --config config/gunicorn.conf.py app:app" > Procfile
   ```

3. **Set environment variables:**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set DEBUG=False
   heroku config:set LOG_LEVEL=INFO
   ```

4. **Deploy:**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

5. **Scale dynos:**
   ```bash
   heroku ps:scale web=2
   ```

6. **Verify deployment:**
   ```bash
   heroku open
   curl https://your-drug-api-name.herokuapp.com/health
   ```

### Heroku Configuration

**runtime.txt:**
```
python-3.9.18
```

**app.json (for Heroku Button):**
```json
{
  "name": "Drug Interaction Prediction API",
  "description": "ML-powered drug interaction prediction service",
  "repository": "https://github.com/your-username/drug-interaction-api",
  "keywords": ["python", "flask", "machine-learning", "healthcare"],
  "env": {
    "FLASK_ENV": {
      "value": "production"
    },
    "DEBUG": {
      "value": "False"
    },
    "LOG_LEVEL": {
      "value": "INFO"
    }
  },
  "formation": {
    "web": {
      "quantity": 1,
      "size": "standard-1x"
    }
  },
  "buildpacks": [
    {
      "url": "heroku/python"
    }
  ]
}
```

## 🔶 AWS Deployment

### Option 1: AWS Elastic Beanstalk

1. **Install EB CLI:**
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB application:**
   ```bash
   eb init drug-interaction-api
   ```

3. **Create environment:**
   ```bash
   eb create production
   ```

4. **Deploy:**
   ```bash
   eb deploy
   ```

### Option 2: AWS ECS (Fargate)

1. **Create ECR repository:**
   ```bash
   aws ecr create-repository --repository-name drug-interaction-api
   ```

2. **Build and push Docker image:**
   ```bash
   # Get login token
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

   # Build and tag
   docker build -t drug-interaction-api .
   docker tag drug-interaction-api:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/drug-interaction-api:latest

   # Push
   docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/drug-interaction-api:latest
   ```

3. **Create ECS task definition:**
   ```json
   {
     "family": "drug-interaction-api",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "512",
     "memory": "1024",
     "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "drug-api",
         "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/drug-interaction-api:latest",
         "portMappings": [
           {
             "containerPort": 5000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {"name": "FLASK_ENV", "value": "production"},
           {"name": "DEBUG", "value": "False"}
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/drug-interaction-api",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

### Option 3: AWS Lambda (Serverless)

1. **Install Zappa:**
   ```bash
   pip install zappa
   ```

2. **Initialize Zappa:**
   ```bash
   zappa init
   ```

3. **Configure zappa_settings.json:**
   ```json
   {
     "production": {
       "app_function": "app.app",
       "aws_region": "us-east-1",
       "profile_name": "default",
       "project_name": "drug-interaction-api",
       "runtime": "python3.9",
       "s3_bucket": "your-zappa-deployments-bucket",
       "memory_size": 1024,
       "timeout_seconds": 120,
       "environment_variables": {
         "FLASK_ENV": "production"
       }
     }
   }
   ```

4. **Deploy:**
   ```bash
   zappa deploy production
   ```

## 🔵 Google Cloud Platform (GCP)

### Option 1: Cloud Run

1. **Build and push to Container Registry:**
   ```bash
   # Configure Docker for GCP
   gcloud auth configure-docker

   # Build and tag
   docker build -t gcr.io/your-project-id/drug-interaction-api .

   # Push
   docker push gcr.io/your-project-id/drug-interaction-api
   ```

2. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy drug-interaction-api \
     --image gcr.io/your-project-id/drug-interaction-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 2Gi \
     --cpu 1 \
     --timeout 120s \
     --set-env-vars FLASK_ENV=production,DEBUG=False
   ```

### Option 2: App Engine

1. **Create app.yaml:**
   ```yaml
   runtime: python39
   
   env_variables:
     FLASK_ENV: production
     DEBUG: False
     LOG_LEVEL: INFO
   
   resources:
     cpu: 1
     memory_gb: 2
     disk_size_gb: 10
   
   automatic_scaling:
     min_instances: 1
     max_instances: 10
     target_cpu_utilization: 0.6
   ```

2. **Deploy:**
   ```bash
   gcloud app deploy
   ```

## 🔷 Microsoft Azure

### Option 1: Container Instances

1. **Create resource group:**
   ```bash
   az group create --name drug-api-rg --location eastus
   ```

2. **Create container registry:**
   ```bash
   az acr create --resource-group drug-api-rg --name drugapiregistry --sku Basic
   ```

3. **Build and push image:**
   ```bash
   az acr build --registry drugapiregistry --image drug-interaction-api .
   ```

4. **Deploy container:**
   ```bash
   az container create \
     --resource-group drug-api-rg \
     --name drug-api \
     --image drugapiregistry.azurecr.io/drug-interaction-api:latest \
     --cpu 1 \
     --memory 2 \
     --registry-login-server drugapiregistry.azurecr.io \
     --registry-username drugapiregistry \
     --registry-password $(az acr credential show --name drugapiregistry --query "passwords[0].value" -o tsv) \
     --dns-name-label drug-api-unique \
     --ports 5000 \
     --environment-variables FLASK_ENV=production DEBUG=False
   ```

### Option 2: App Service

1. **Create App Service plan:**
   ```bash
   az appservice plan create \
     --name drug-api-plan \
     --resource-group drug-api-rg \
     --sku B1 \
     --is-linux
   ```

2. **Create web app:**
   ```bash
   az webapp create \
     --resource-group drug-api-rg \
     --plan drug-api-plan \
     --name drug-api-webapp \
     --deployment-container-image-name drugapiregistry.azurecr.io/drug-interaction-api:latest
   ```

## 🌊 DigitalOcean

### Option 1: App Platform

1. **Create app spec (app.yaml):**
   ```yaml
   name: drug-interaction-api
   services:
   - name: api
     source_dir: /
     github:
       repo: your-username/drug-interaction-api
       branch: main
     run_command: gunicorn --config config/gunicorn.conf.py app:app
     environment_slug: python
     instance_count: 1
     instance_size_slug: basic-xxs
     envs:
     - key: FLASK_ENV
       value: production
     - key: DEBUG
       value: "False"
     http_port: 5000
     health_check:
       http_path: /health
   ```

2. **Deploy:**
   ```bash
   doctl apps create --spec app.yaml
   ```

### Option 2: Droplets with Docker

1. **Create droplet:**
   ```bash
   doctl compute droplet create drug-api \
     --image docker-20-04 \
     --size s-2vcpu-2gb \
     --region nyc1 \
     --ssh-keys your-ssh-key-id
   ```

2. **Deploy via SSH:**
   ```bash
   # SSH to droplet
   ssh root@your-droplet-ip

   # Clone repository
   git clone https://github.com/your-username/drug-interaction-api.git
   cd drug-interaction-api

   # Deploy with Docker Compose
   docker-compose up -d --build
   ```

## 🔧 Environment-Specific Configurations

### Production Environment Variables

```bash
# Common across all platforms
FLASK_ENV=production
DEBUG=False
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=5000

# Platform-specific
# Heroku: PORT is set automatically
# AWS Lambda: Use serverless configuration
# GCP Cloud Run: PORT is set automatically
```

### Resource Requirements

| Platform | CPU | Memory | Storage | Cost (Est.) |
|----------|-----|--------|---------|-------------|
| Heroku Standard-1X | 1 vCPU | 512MB | - | $25/month |
| AWS Fargate | 0.5 vCPU | 1GB | - | $15/month |
| GCP Cloud Run | 1 vCPU | 2GB | - | $10/month |
| Azure Container | 1 vCPU | 2GB | - | $20/month |
| DigitalOcean | 2 vCPU | 2GB | 50GB | $12/month |

## 📊 Monitoring and Logging

### Platform-Specific Monitoring

**Heroku:**
```bash
# View logs
heroku logs --tail

# Monitor metrics
heroku addons:create newrelic:wayne
```

**AWS:**
```bash
# CloudWatch logs
aws logs describe-log-groups --log-group-name-prefix /ecs/drug-interaction-api
```

**GCP:**
```bash
# Cloud Logging
gcloud logging read "resource.type=cloud_run_revision"
```

**Azure:**
```bash
# Application Insights
az monitor app-insights component create --app drug-api --location eastus --resource-group drug-api-rg
```

## 🔐 Security Considerations

1. **API Keys and Secrets:**
   - Use platform-specific secret management
   - Never commit secrets to version control

2. **Network Security:**
   - Configure firewalls and security groups
   - Use HTTPS/TLS encryption

3. **Access Control:**
   - Implement proper IAM roles
   - Use least privilege principle

## 🚨 Troubleshooting

### Common Issues

1. **Memory errors:** Increase memory allocation
2. **Timeout errors:** Increase timeout limits
3. **Cold starts:** Use warm-up strategies
4. **Model loading issues:** Verify file paths and permissions

### Platform-Specific Debugging

**Heroku:**
```bash
heroku run bash
heroku logs --tail --dyno web.1
```

**AWS:**
```bash
aws ecs describe-tasks --cluster your-cluster --tasks task-id
```

**GCP:**
```bash
gcloud run services describe drug-interaction-api --region us-central1
```

This completes the cloud deployment guide. Each platform has its own advantages and considerations for hosting the Drug Interaction Prediction API.
