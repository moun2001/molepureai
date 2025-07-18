#!/usr/bin/env python3
"""
Create Production Deployment Package

This script creates a comprehensive deployment package with all necessary files
for production hosting of the Drug Interaction Prediction API.
"""

import os
import shutil
import zipfile
import json
from datetime import datetime
from pathlib import Path
import argparse


def create_deployment_package(output_dir: str = ".", package_name: str = None):
    """Create a complete deployment package"""
    
    if not package_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_name = f"drug-interaction-api-production-{timestamp}"
    
    output_path = Path(output_dir)
    package_path = output_path / package_name
    
    print(f"🚀 Creating deployment package: {package_name}")
    print(f"📁 Output directory: {package_path}")
    
    # Create package directory
    package_path.mkdir(parents=True, exist_ok=True)
    
    # Define file structure for deployment
    deployment_structure = {
        # Core application files
        'app.py': 'app.py',
        'requirements.txt': 'requirements.txt',
        'Dockerfile': 'Dockerfile',
        'docker-compose.yml': 'docker-compose.yml',
        'PRODUCTION_CHECKLIST.md': 'PRODUCTION_CHECKLIST.md',
        
        # Source code
        'src/': 'src/',
        
        # Configuration files
        'config/': 'config/',
        
        # Documentation
        'docs/': 'docs/',
        
        # Deployment files
        'deployment/': 'deployment/',
        
        # Scripts
        'scripts/': 'scripts/',
        
        # Tests
        'tests/': 'tests/',
    }
    
    # Copy files and directories
    for source, dest in deployment_structure.items():
        source_path = Path(source)
        dest_path = package_path / dest
        
        if source_path.exists():
            if source_path.is_file():
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, dest_path)
                print(f"  ✅ Copied file: {source}")
            elif source_path.is_dir():
                shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                print(f"  ✅ Copied directory: {source}")
        else:
            print(f"  ⚠️ Not found: {source}")
    
    # Create additional deployment files
    create_systemd_service(package_path)
    create_deployment_readme(package_path)
    create_quick_start_script(package_path)
    create_package_info(package_path, package_name)
    
    # Create compressed archive
    archive_path = output_path / f"{package_name}.zip"
    create_zip_archive(package_path, archive_path)
    
    # Clean up temporary directory
    shutil.rmtree(package_path)
    
    print(f"\n🎉 Deployment package created successfully!")
    print(f"📦 Package: {archive_path}")
    print(f"📊 Size: {archive_path.stat().st_size / (1024*1024):.1f} MB")
    
    return str(archive_path)


def create_systemd_service(package_path: Path):
    """Create systemd service file"""
    service_content = """[Unit]
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
"""
    
    deployment_dir = package_path / 'deployment'
    deployment_dir.mkdir(exist_ok=True)
    
    with open(deployment_dir / 'drug-interaction-api.service', 'w') as f:
        f.write(service_content)
    
    print("  ✅ Created systemd service file")


def create_deployment_readme(package_path: Path):
    """Create deployment-specific README"""
    readme_content = """# Drug Interaction Prediction API - Production Deployment

## 🚀 Quick Start

1. **Extract the package:**
   ```bash
   unzip drug-interaction-api-production-*.zip
   cd drug-interaction-api-production-*
   ```

2. **Run the quick start script:**
   ```bash
   chmod +x quick_start.sh
   sudo ./quick_start.sh
   ```

3. **Verify deployment:**
   ```bash
   curl https://yourdomain.com/health
   ```

## 📋 Manual Deployment

If you prefer manual deployment, follow the detailed instructions in `PRODUCTION_CHECKLIST.md`.

## 📁 Package Contents

- `src/` - Application source code
- `config/` - Configuration files and templates
- `docs/` - Complete API documentation
- `deployment/` - Deployment configurations (nginx, systemd, docker)
- `scripts/` - Utility scripts for monitoring and backup
- `tests/` - Test suites and examples
- `PRODUCTION_CHECKLIST.md` - Detailed deployment checklist

## 🔧 Configuration

1. Copy `config/production.env` to `.env`
2. Update environment variables for your deployment
3. Configure SSL certificates
4. Update domain names in nginx configuration

## 📊 Features

- **Production-ready Flask API** with Gunicorn WSGI server
- **Docker support** with multi-stage builds
- **Nginx reverse proxy** with SSL/TLS and security headers
- **Comprehensive monitoring** with health checks and alerting
- **Automated backups** for model files and configurations
- **Multi-drug analysis** supporting 2-10 drugs per request
- **Rate limiting** and security hardening
- **Complete documentation** including API specs and deployment guides

## 🏥 Clinical Use Cases

- Electronic Health Record (EHR) integration
- Clinical decision support systems
- Pharmacy management systems
- Medication reconciliation workflows

## 📈 Performance

- **Response Time**: ~2 seconds for 2-10 drugs
- **Throughput**: 100+ requests per minute
- **Scalability**: Horizontally scalable with load balancers
- **Reliability**: 99.9% uptime with proper monitoring

## 🆘 Support

For deployment assistance, refer to:
- `PRODUCTION_CHECKLIST.md` - Step-by-step deployment guide
- `docs/deployment/` - Platform-specific deployment guides
- `docs/API_DOCUMENTATION.md` - Complete API reference

## 📄 License

This software is provided for healthcare and research purposes.
Please ensure compliance with applicable regulations and guidelines.
"""
    
    with open(package_path / 'README.md', 'w') as f:
        f.write(readme_content)
    
    print("  ✅ Created deployment README")


def create_quick_start_script(package_path: Path):
    """Create quick start deployment script"""
    script_content = """#!/bin/bash
# Quick Start Deployment Script for Drug Interaction API

set -e

echo "🚀 Drug Interaction API - Quick Start Deployment"
echo "================================================"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root (use sudo)"
   exit 1
fi

# Variables
APP_USER="drugapi"
APP_DIR="/home/$APP_USER/drug-interaction-api"
DOMAIN=""

# Get domain name
read -p "Enter your domain name (e.g., api.example.com): " DOMAIN
if [[ -z "$DOMAIN" ]]; then
    echo "❌ Domain name is required"
    exit 1
fi

echo "📋 Deployment Configuration:"
echo "   Domain: $DOMAIN"
echo "   App User: $APP_USER"
echo "   App Directory: $APP_DIR"
echo ""

read -p "Continue with deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

echo "🔧 Step 1: System preparation..."
apt update && apt upgrade -y
apt install -y python3.9 python3.9-venv python3.9-dev nginx supervisor git curl gcc

echo "👤 Step 2: Creating application user..."
if ! id "$APP_USER" &>/dev/null; then
    useradd -m -s /bin/bash $APP_USER
    usermod -aG www-data $APP_USER
    echo "   ✅ User $APP_USER created"
else
    echo "   ✅ User $APP_USER already exists"
fi

echo "📁 Step 3: Setting up application directory..."
sudo -u $APP_USER mkdir -p $APP_DIR
cp -r . $APP_DIR/
chown -R $APP_USER:www-data $APP_DIR

echo "🐍 Step 4: Setting up Python environment..."
sudo -u $APP_USER bash -c "cd $APP_DIR && python3.9 -m venv venv"
sudo -u $APP_USER bash -c "cd $APP_DIR && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"

echo "⚙️ Step 5: Configuring services..."
# Copy systemd service
cp deployment/drug-interaction-api.service /etc/systemd/system/
sed -i "s|/home/drugapi/drug-interaction-api|$APP_DIR|g" /etc/systemd/system/drug-interaction-api.service

# Copy nginx configuration
cp deployment/nginx.conf /etc/nginx/sites-available/drug-interaction-api
sed -i "s/your-domain.com/$DOMAIN/g" /etc/nginx/sites-available/drug-interaction-api
ln -sf /etc/nginx/sites-available/drug-interaction-api /etc/nginx/sites-enabled/

# Remove default nginx site
rm -f /etc/nginx/sites-enabled/default

echo "🔐 Step 6: Setting up SSL certificate..."
apt install -y certbot python3-certbot-nginx
nginx -t && systemctl reload nginx

echo "📊 Step 7: Setting up logging and monitoring..."
mkdir -p /var/log/drug-api
chown $APP_USER:www-data /var/log/drug-api

# Copy monitoring script
cp scripts/health_monitor.py /usr/local/bin/
chmod +x /usr/local/bin/health_monitor.py

echo "🚀 Step 8: Starting services..."
systemctl daemon-reload
systemctl enable drug-interaction-api
systemctl start drug-interaction-api
systemctl enable nginx
systemctl restart nginx

echo "🧪 Step 9: Testing deployment..."
sleep 5

if systemctl is-active --quiet drug-interaction-api; then
    echo "   ✅ Application service is running"
else
    echo "   ❌ Application service failed to start"
    journalctl -u drug-interaction-api --no-pager -n 20
    exit 1
fi

if systemctl is-active --quiet nginx; then
    echo "   ✅ Nginx is running"
else
    echo "   ❌ Nginx failed to start"
    exit 1
fi

# Test health endpoint
if curl -f http://localhost:5000/health >/dev/null 2>&1; then
    echo "   ✅ Health check passed"
else
    echo "   ❌ Health check failed"
    exit 1
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Obtain SSL certificate: certbot --nginx -d $DOMAIN"
echo "   2. Test the API: curl https://$DOMAIN/health"
echo "   3. Review logs: journalctl -u drug-interaction-api -f"
echo "   4. Set up monitoring: crontab -e (add health monitoring)"
echo ""
echo "📖 For detailed configuration, see PRODUCTION_CHECKLIST.md"
"""
    
    with open(package_path / 'quick_start.sh', 'w') as f:
        f.write(script_content)
    
    # Make script executable
    os.chmod(package_path / 'quick_start.sh', 0o755)
    
    print("  ✅ Created quick start script")


def create_package_info(package_path: Path, package_name: str):
    """Create package information file"""
    package_info = {
        'name': 'Drug Interaction Prediction API',
        'version': '1.0.0',
        'package_name': package_name,
        'created': datetime.now().isoformat(),
        'description': 'Production-ready API for drug-drug interaction prediction using machine learning',
        'features': [
            'XGBoost-based interaction prediction',
            'Multi-drug analysis (2-10 drugs)',
            'RESTful API with comprehensive documentation',
            'Docker containerization support',
            'Production-ready with monitoring and backup',
            'Security hardening and rate limiting',
            'Nginx reverse proxy configuration',
            'Automated deployment scripts'
        ],
        'requirements': {
            'python': '3.9+',
            'memory': '2GB minimum, 4GB recommended',
            'cpu': '2 cores minimum, 4 cores recommended',
            'disk': '10GB minimum',
            'os': 'Ubuntu 20.04+ or CentOS 8+'
        },
        'deployment_options': [
            'Docker containers',
            'Traditional Linux servers',
            'Cloud platforms (AWS, GCP, Azure)',
            'Platform-as-a-Service (Heroku, DigitalOcean)'
        ],
        'support': {
            'documentation': 'docs/',
            'api_reference': 'docs/API_DOCUMENTATION.md',
            'deployment_guide': 'PRODUCTION_CHECKLIST.md',
            'examples': 'tests/',
            'monitoring': 'scripts/health_monitor.py'
        }
    }
    
    with open(package_path / 'package_info.json', 'w') as f:
        json.dump(package_info, f, indent=2)
    
    print("  ✅ Created package information file")


def create_zip_archive(source_dir: Path, archive_path: Path):
    """Create compressed zip archive"""
    print(f"📦 Creating zip archive: {archive_path}")
    
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in source_dir.rglob('*'):
            if file_path.is_file():
                # Calculate relative path
                relative_path = file_path.relative_to(source_dir.parent)
                zipf.write(file_path, relative_path)
    
    print(f"  ✅ Archive created successfully")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Create Drug Interaction API deployment package')
    parser.add_argument('--output-dir', default='.', help='Output directory (default: current directory)')
    parser.add_argument('--package-name', help='Package name (default: auto-generated with timestamp)')
    
    args = parser.parse_args()
    
    try:
        package_path = create_deployment_package(args.output_dir, args.package_name)
        print(f"\n✅ Deployment package ready: {package_path}")
        print("\n📋 To deploy:")
        print("   1. Transfer the zip file to your server")
        print("   2. Extract: unzip drug-interaction-api-production-*.zip")
        print("   3. Run: sudo ./quick_start.sh")
        print("   4. Follow the prompts for domain configuration")
        
    except Exception as e:
        print(f"❌ Failed to create deployment package: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
