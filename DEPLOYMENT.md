# 🚀 Cognora+ Deployment Guide

This guide will help you deploy your Cognora+ application to make it live and accessible to users.

## 📋 Prerequisites

Before deploying, ensure you have:

- ✅ AWS Account with S3, DynamoDB, and SNS access
- ✅ GitHub account
- ✅ Streamlit Cloud account (free)
- ✅ All AWS services configured (from previous setup)

## 🎯 Deployment Options

### Option 1: Streamlit Cloud (Recommended - Free)

**Best for:** Quick deployment, free hosting, automatic updates

#### Step 1: Prepare Your Repository

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/cognora-plus.git
   git push -u origin main
   ```

2. **Verify Files:**
   - ✅ `app.py` (main application)
   - ✅ `requirements.txt` (dependencies)
   - ✅ `.streamlit/config.toml` (configuration)
   - ✅ All Python modules

#### Step 2: Deploy to Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Sign in with GitHub**
3. **Click "New app"**
4. **Configure deployment:**
   - **Repository:** `yourusername/cognora-plus`
   - **Branch:** `main`
   - **Main file path:** `app.py`
   - **App URL:** `cognora-plus` (or your preferred name)

#### Step 3: Set Environment Variables

In Streamlit Cloud dashboard:

1. **Go to your app settings**
2. **Add secrets** with your AWS credentials:
   ```toml
   AWS_ACCESS_KEY_ID = "your_access_key"
   AWS_SECRET_ACCESS_KEY = "your_secret_key"
   AWS_REGION_NAME = "us-east-1"
   S3_BUCKET_NAME = "cognora-data-store"
   DYNAMODB_TABLE_NAME = "CognoraScores"
   SNS_TOPIC_ARN = "arn:aws:sns:region:account:topic"
   ```

#### Step 4: Deploy

1. **Click "Deploy"**
2. **Wait for deployment** (usually 2-3 minutes)
3. **Your app will be live at:** `https://cognora-plus.streamlit.app`

### Option 2: AWS EC2 (Production)

**Best for:** Full control, production workloads, custom domains

#### Step 1: Launch EC2 Instance

1. **Launch Ubuntu 20.04 LTS instance**
2. **Security Group:** Allow port 8501 (Streamlit)
3. **Instance Type:** t3.medium or larger

#### Step 2: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install system dependencies
sudo apt install gcc g++ curl -y

# Create virtual environment
python3 -m venv cognora-env
source cognora-env/bin/activate

# Install Python packages
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

#### Step 3: Configure Environment

```bash
# Create .env file
nano .env

# Add your AWS credentials
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION_NAME=us-east-1
S3_BUCKET_NAME=cognora-data-store
DYNAMODB_TABLE_NAME=CognoraScores
SNS_TOPIC_ARN=arn:aws:sns:region:account:topic
```

#### Step 4: Run Application

```bash
# Run in background
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &

# Or use systemd service
sudo nano /etc/systemd/system/cognora.service
```

**Systemd service file:**
```ini
[Unit]
Description=Cognora+ Streamlit App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/cognora
Environment=PATH=/home/ubuntu/cognora-env/bin
ExecStart=/home/ubuntu/cognora-env/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable cognora
sudo systemctl start cognora
```

### Option 3: Docker Deployment

**Best for:** Containerized environments, Kubernetes, consistent deployments

#### Step 1: Build Docker Image

```bash
# Build image
docker build -t cognora-plus .

# Test locally
docker run -p 8501:8501 --env-file .env cognora-plus
```

#### Step 2: Deploy to Cloud

**AWS ECS:**
```bash
# Create ECR repository
aws ecr create-repository --repository-name cognora-plus

# Push image
docker tag cognora-plus:latest your-account.dkr.ecr.region.amazonaws.com/cognora-plus:latest
aws ecr get-login-password --region region | docker login --username AWS --password-stdin your-account.dkr.ecr.region.amazonaws.com
docker push your-account.dkr.ecr.region.amazonaws.com/cognora-plus:latest
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  cognora:
    build: .
    ports:
      - "8501:8501"
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_REGION_NAME=${AWS_REGION_NAME}
      - S3_BUCKET_NAME=${S3_BUCKET_NAME}
      - DYNAMODB_TABLE_NAME=${DYNAMODB_TABLE_NAME}
      - SNS_TOPIC_ARN=${SNS_TOPIC_ARN}
    restart: unless-stopped
```

## 🔒 Security Considerations

### Environment Variables
- ✅ Never commit `.env` files to Git
- ✅ Use AWS Secrets Manager for production
- ✅ Rotate AWS keys regularly

### Network Security
- ✅ Use HTTPS in production
- ✅ Configure proper firewall rules
- ✅ Enable AWS CloudTrail for audit logs

### Data Protection
- ✅ Encrypt data at rest and in transit
- ✅ Implement proper IAM roles
- ✅ Regular security updates

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# Check application status
curl http://your-domain:8501/_stcore/health

# Monitor logs
tail -f /var/log/cognora.log
```

### Backup Strategy
- ✅ Regular DynamoDB backups
- ✅ S3 versioning enabled
- ✅ Database snapshots

### Updates
```bash
# Pull latest code
git pull origin main

# Restart application
sudo systemctl restart cognora
```

## 🚨 Troubleshooting

### Common Issues

**1. Port Already in Use**
```bash
# Find process using port 8501
sudo lsof -i :8501
# Kill process
sudo kill -9 <PID>
```

**2. AWS Credentials Error**
```bash
# Test AWS credentials
aws sts get-caller-identity
# Check environment variables
echo $AWS_ACCESS_KEY_ID
```

**3. Memory Issues**
```bash
# Monitor memory usage
htop
# Increase swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📈 Performance Optimization

### Streamlit Configuration
```toml
[server]
maxUploadSize = 200
enableXsrfProtection = false
enableCORS = false

[browser]
gatherUsageStats = false
```

### AWS Optimization
- ✅ Use CloudFront for static assets
- ✅ Enable DynamoDB auto-scaling
- ✅ Configure S3 lifecycle policies

## 🎉 Success Checklist

- ✅ Application accessible via URL
- ✅ AWS services connected
- ✅ Data saving working
- ✅ Alerts functioning
- ✅ HTTPS enabled
- ✅ Monitoring configured
- ✅ Backup strategy in place

## 📞 Support

If you encounter issues:

1. **Check logs:** Application and AWS CloudWatch
2. **Verify configuration:** Environment variables and AWS permissions
3. **Test locally:** Ensure it works before deploying
4. **Documentation:** Refer to AWS and Streamlit docs

---

**Your Cognora+ application is now live! 🎉**

Users can access it at your deployment URL and start using the wellness features. 