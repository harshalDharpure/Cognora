#!/usr/bin/env python3
"""
Streamlit Cloud Deployment Helper Script
This script helps prepare your Cognora+ app for Streamlit Cloud deployment.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_requirements():
    """Check if all required files exist."""
    required_files = [
        'app.py',
        'requirements.txt',
        '.streamlit/config.toml',
        'config.py',
        'agents.py',
        'scoring.py',
        'storage.py',
        'aws_services.py',
        'auth.py',
        'utils.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files found")
    return True

def check_environment_variables():
    """Check if required environment variables are documented."""
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_DEFAULT_REGION',
        'DYNAMODB_TABLE_NAME',
        'ENVIRONMENT',
        'MARKET'
    ]
    
    print("\n📋 Required Environment Variables for Streamlit Cloud:")
    print("Add these to your Streamlit Cloud app secrets:")
    print()
    
    for var in required_vars:
        print(f"   {var} = \"your_value_here\"")
    
    print("\n📋 Optional Environment Variables:")
    optional_vars = [
        'SENTRY_DSN',
        'MIXPANEL_TOKEN',
        'GOOGLE_ANALYTICS_ID'
    ]
    
    for var in optional_vars:
        print(f"   {var} = \"your_value_here\"")

def validate_requirements_txt():
    """Validate requirements.txt file."""
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
        
        # Check for specific versions
        if 'streamlit==' in content and 'boto3==' in content:
            print("✅ requirements.txt has specific versions")
            return True
        else:
            print("⚠️  requirements.txt should use specific versions (==) for Streamlit Cloud")
            return False
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False

def check_git_status():
    """Check if the repository is ready for deployment."""
    try:
        # Check if this is a git repository
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git repository detected")
            
            # Check if there are uncommitted changes
            result = subprocess.run(['git', 'diff', '--quiet'], capture_output=True)
            if result.returncode == 0:
                print("✅ No uncommitted changes")
            else:
                print("⚠️  You have uncommitted changes. Consider committing them before deployment.")
            
            return True
        else:
            print("❌ Not a git repository. Please initialize git and push to GitHub.")
            return False
    except FileNotFoundError:
        print("❌ Git not found. Please install git and push your code to GitHub.")
        return False

def generate_deployment_checklist():
    """Generate a deployment checklist."""
    print("\n" + "="*60)
    print("🚀 STREAMLIT CLOUD DEPLOYMENT CHECKLIST")
    print("="*60)
    
    print("\n1. 📁 Repository Setup:")
    print("   □ Push your code to GitHub")
    print("   □ Ensure all files are committed")
    print("   □ Verify repository is public (for free tier)")
    
    print("\n2. 🔧 Streamlit Cloud Setup:")
    print("   □ Sign up at share.streamlit.io")
    print("   □ Connect your GitHub account")
    print("   □ Create new app")
    print("   □ Set main file path: app.py")
    
    print("\n3. 🔐 Environment Variables:")
    print("   □ Add AWS credentials to Streamlit Cloud secrets")
    print("   □ Configure app-specific variables")
    print("   □ Test AWS connectivity")
    
    print("\n4. 🏗️ AWS Infrastructure:")
    print("   □ Ensure DynamoDB table exists with correct schema")
    print("   □ Verify SNS topic is configured")
    print("   □ Check IAM permissions")
    
    print("\n5. 🧪 Testing:")
    print("   □ Test authentication flow")
    print("   □ Verify data storage in DynamoDB")
    print("   □ Test caregiver alerts")
    print("   □ Check voice recording features")
    
    print("\n6. 📊 Monitoring:")
    print("   □ Set up error tracking (Sentry)")
    print("   □ Configure analytics (Mixpanel)")
    print("   □ Monitor AWS costs")
    
    print("\n" + "="*60)

def main():
    """Main deployment helper function."""
    print("🧠 Cognora+ Streamlit Cloud Deployment Helper")
    print("="*50)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Please fix missing files before deployment.")
        sys.exit(1)
    
    # Validate requirements.txt
    validate_requirements_txt()
    
    # Check git status
    check_git_status()
    
    # Show environment variables
    check_environment_variables()
    
    # Generate checklist
    generate_deployment_checklist()
    
    print("\n🎉 Deployment preparation complete!")
    print("\nNext steps:")
    print("1. Follow the checklist above")
    print("2. Deploy to Streamlit Cloud")
    print("3. Test all functionality")
    print("4. Monitor performance and costs")
    
    print("\n📚 For detailed instructions, see: STREAMLIT_CLOUD_DEPLOYMENT.md")

if __name__ == "__main__":
    main() 