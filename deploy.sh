#!/bin/bash

# 🚀 Cognora+ Deployment Script
# This script helps you deploy your Cognora+ application

set -e  # Exit on any error

echo "🧠 Cognora+ Deployment Script"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    print_error "app.py not found. Please run this script from the Cognora+ project directory."
    exit 1
fi

print_status "Found Cognora+ project files"

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating template..."
    cat > .env << EOF
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION_NAME=us-east-1
S3_BUCKET_NAME=cognora-data-store
DYNAMODB_TABLE_NAME=CognoraScores
SNS_TOPIC_ARN=arn:aws:sns:region:account:topic
EOF
    print_warning "Please edit .env file with your AWS credentials before deploying."
fi

# Function to deploy to Streamlit Cloud
deploy_streamlit_cloud() {
    echo ""
    echo "🌐 Deploying to Streamlit Cloud..."
    echo "=================================="
    
    # Check if git is initialized
    if [ ! -d ".git" ]; then
        print_warning "Git repository not initialized. Initializing..."
        git init
        git add .
        git commit -m "Initial commit for deployment"
    fi
    
    print_status "Git repository ready"
    
    # Check if remote is set
    if ! git remote get-url origin > /dev/null 2>&1; then
        print_warning "Git remote not set. Please add your GitHub repository:"
        echo "git remote add origin https://github.com/yourusername/cognora-plus.git"
        echo "git push -u origin main"
    else
        print_status "Git remote configured"
        print_warning "Push your changes to GitHub:"
        echo "git add ."
        echo "git commit -m 'Update for deployment'"
        echo "git push origin main"
    fi
    
    echo ""
    print_status "Next steps for Streamlit Cloud deployment:"
    echo "1. Go to https://share.streamlit.io"
    echo "2. Sign in with GitHub"
    echo "3. Click 'New app'"
    echo "4. Select your repository: yourusername/cognora-plus"
    echo "5. Set main file path: app.py"
    echo "6. Add your AWS credentials in the secrets section"
    echo "7. Click 'Deploy'"
    echo ""
    echo "Your app will be available at: https://your-app-name.streamlit.app"
}

# Function to deploy to AWS EC2
deploy_aws_ec2() {
    echo ""
    echo "☁️  Deploying to AWS EC2..."
    echo "============================"
    
    print_warning "This will help you set up deployment on an EC2 instance."
    
    # Create deployment script
    cat > deploy_ec2.sh << 'EOF'
#!/bin/bash
# EC2 Deployment Script

echo "🚀 Setting up Cognora+ on EC2..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv gcc g++ curl -y

# Create virtual environment
python3 -m venv cognora-env
source cognora-env/bin/activate

# Install Python packages
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Create systemd service
sudo tee /etc/systemd/system/cognora.service > /dev/null << 'SERVICE_EOF'
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
SERVICE_EOF

# Enable and start service
sudo systemctl enable cognora
sudo systemctl start cognora

echo "✅ Cognora+ deployed on EC2!"
echo "🌐 Access at: http://your-ec2-ip:8501"
EOF
    
    chmod +x deploy_ec2.sh
    
    print_status "Created EC2 deployment script: deploy_ec2.sh"
    print_warning "Upload this script to your EC2 instance and run it."
}

# Function to deploy with Docker
deploy_docker() {
    echo ""
    echo "🐳 Deploying with Docker..."
    echo "============================"
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker not found. Please install Docker first."
        exit 1
    fi
    
    print_status "Docker found"
    
    # Build Docker image
    print_status "Building Docker image..."
    docker build -t cognora-plus .
    
    print_status "Docker image built successfully"
    
    # Create docker-compose file
    cat > docker-compose.yml << 'EOF'
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
EOF
    
    print_status "Created docker-compose.yml"
    
    echo ""
    print_status "To run with Docker Compose:"
    echo "docker-compose up -d"
    echo ""
    print_status "To run with Docker directly:"
    echo "docker run -p 8501:8501 --env-file .env cognora-plus"
}

# Main menu
echo ""
echo "Choose deployment option:"
echo "1. Streamlit Cloud (Recommended - Free)"
echo "2. AWS EC2 (Production)"
echo "3. Docker (Containerized)"
echo "4. All options"
echo "5. Exit"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        deploy_streamlit_cloud
        ;;
    2)
        deploy_aws_ec2
        ;;
    3)
        deploy_docker
        ;;
    4)
        deploy_streamlit_cloud
        deploy_aws_ec2
        deploy_docker
        ;;
    5)
        print_status "Exiting..."
        exit 0
        ;;
    *)
        print_error "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
print_status "Deployment setup complete!"
echo ""
print_warning "Remember to:"
echo "- Set up your AWS credentials in .env file"
echo "- Test the application locally before deploying"
echo "- Monitor the application after deployment"
echo ""
print_status "Happy deploying! 🎉" 