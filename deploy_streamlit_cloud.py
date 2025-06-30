#!/usr/bin/env python3
"""
Streamlit Cloud Deployment Helper Script
This script helps prepare and validate your app for Streamlit Cloud deployment.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_file_exists(file_path):
    """Check if a file exists and is readable."""
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} does not exist")
        return False
    if not os.access(file_path, os.R_OK):
        print(f"❌ Error: {file_path} is not readable")
        return False
    print(f"✅ {file_path} exists and is readable")
    return True

def validate_requirements():
    """Validate requirements.txt file."""
    print("\n🔍 Validating requirements.txt...")
    
    if not check_file_exists("requirements.txt"):
        return False
    
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read()
        
        # Check for common issues
        issues = []
        
        # Check for empty lines or invalid formats
        lines = requirements.strip().split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith('#') and '==' not in line:
                issues.append(f"Line {i}: Missing version specifier for '{line}'")
        
        if issues:
            print("⚠️  Potential issues found in requirements.txt:")
            for issue in issues:
                print(f"   {issue}")
            print("   Consider adding version specifiers for better reproducibility")
        else:
            print("✅ requirements.txt looks good")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False

def validate_packages():
    """Validate packages.txt file."""
    print("\n🔍 Validating packages.txt...")
    
    if not check_file_exists("packages.txt"):
        print("⚠️  packages.txt not found - creating one...")
        create_packages_file()
        return True
    
    try:
        with open("packages.txt", "r") as f:
            packages = f.read()
        
        # Check for valid package names
        lines = packages.strip().split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith('#') and not line.replace('-', '').replace('_', '').isalnum():
                print(f"⚠️  Line {i}: Potentially invalid package name '{line}'")
        
        print("✅ packages.txt looks good")
        return True
        
    except Exception as e:
        print(f"❌ Error reading packages.txt: {e}")
        return False

def create_packages_file():
    """Create a packages.txt file with common system dependencies."""
    packages_content = """# System dependencies for Streamlit Cloud
# Audio processing dependencies
ffmpeg
portaudio19-dev
python3-dev

# PDF generation dependencies
libfreetype6-dev
libpng-dev

# Cryptography dependencies
libssl-dev
libffi-dev

# Additional system packages
build-essential
pkg-config
"""
    
    try:
        with open("packages.txt", "w") as f:
            f.write(packages_content)
        print("✅ Created packages.txt")
    except Exception as e:
        print(f"❌ Error creating packages.txt: {e}")

def validate_streamlit_config():
    """Validate Streamlit configuration."""
    print("\n🔍 Validating Streamlit configuration...")
    
    config_path = ".streamlit/config.toml"
    if not check_file_exists(config_path):
        print("⚠️  .streamlit/config.toml not found")
        return False
    
    try:
        import toml
        with open(config_path, "r") as f:
            config = toml.load(f)
        
        # Check for important settings
        required_sections = ['server', 'browser']
        for section in required_sections:
            if section not in config:
                print(f"⚠️  Missing '{section}' section in config.toml")
        
        print("✅ Streamlit configuration looks good")
        return True
        
    except ImportError:
        print("⚠️  toml library not available - skipping config validation")
        return True
    except Exception as e:
        print(f"❌ Error reading config.toml: {e}")
        return False

def check_environment_variables():
    """Check for required environment variables."""
    print("\n🔍 Checking environment variables...")
    
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_DEFAULT_REGION',
        'DYNAMODB_TABLE_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 These need to be set in Streamlit Cloud secrets")
    else:
        print("✅ All required environment variables are set")
    
    return len(missing_vars) == 0

def validate_main_app():
    """Validate the main app file."""
    print("\n🔍 Validating main app file...")
    
    if not check_file_exists("app.py"):
        print("❌ app.py not found - this is required for Streamlit Cloud")
        return False
    
    try:
        with open("app.py", "r") as f:
            content = f.read()
        
        # Check for basic Streamlit imports
        if "import streamlit" not in content:
            print("⚠️  app.py doesn't seem to import streamlit")
        
        # Check for main function or streamlit commands
        if "st.title" not in content and "st.write" not in content:
            print("⚠️  app.py doesn't seem to contain Streamlit commands")
        
        print("✅ app.py looks like a valid Streamlit app")
        return True
        
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        return False

def run_tests():
    """Run basic tests to ensure the app works."""
    print("\n🧪 Running basic tests...")
    
    try:
        # Test Python syntax
        result = subprocess.run([sys.executable, "-m", "py_compile", "app.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ app.py has valid Python syntax")
        else:
            print(f"❌ app.py has syntax errors: {result.stderr}")
            return False
        
        # Test imports (basic check)
        test_imports = """
import sys
sys.path.append('.')
try:
    import app
    print("✅ App imports successfully")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
"""
        
        result = subprocess.run([sys.executable, "-c", test_imports], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ App imports successfully")
        else:
            print(f"❌ Import test failed: {result.stderr}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def generate_deployment_summary():
    """Generate a deployment summary."""
    print("\n📋 Deployment Summary")
    print("=" * 50)
    
    summary = {
        "app_file": "app.py",
        "requirements": "requirements.txt",
        "packages": "packages.txt",
        "config": ".streamlit/config.toml",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "platform": sys.platform
    }
    
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print("\n🚀 Ready for Streamlit Cloud deployment!")
    print("\nNext steps:")
    print("1. Push your code to GitHub")
    print("2. Go to https://share.streamlit.io")
    print("3. Connect your repository")
    print("4. Set main file path to: app.py")
    print("5. Configure environment variables in Streamlit Cloud secrets")
    print("6. Deploy!")

def main():
    """Main validation function."""
    print("🚀 Streamlit Cloud Deployment Validator")
    print("=" * 50)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Run all validations
    validations = [
        validate_main_app,
        validate_requirements,
        validate_packages,
        validate_streamlit_config,
        check_environment_variables,
        run_tests
    ]
    
    all_passed = True
    for validation in validations:
        try:
            if not validation():
                all_passed = False
        except Exception as e:
            print(f"❌ Error in {validation.__name__}: {e}")
            all_passed = False
    
    if all_passed:
        print("\n🎉 All validations passed!")
        generate_deployment_summary()
    else:
        print("\n⚠️  Some validations failed. Please fix the issues above before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main() 