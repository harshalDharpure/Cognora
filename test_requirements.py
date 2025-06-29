#!/usr/bin/env python3
"""
Test script to verify all requirements can be imported successfully.
This helps identify any dependency issues before deployment.
"""

import sys
import importlib

def test_imports():
    """Test importing all required packages."""
    required_packages = [
        'streamlit',
        'boto3',
        'langchain',
        'langchain_aws',
        'python_dotenv',
        'requests',
        'fpdf',
        'pandas',
        'anthropic',
        'plotly',
        'spacy',
        'openai',
        'numpy',
        'sentry_sdk',
        'mixpanel',
        'prometheus_client',
        'cryptography',
        'bcrypt',
        'passlib',
        'jose'
    ]
    
    failed_imports = []
    successful_imports = []
    
    print("🧪 Testing package imports...")
    print("=" * 50)
    
    for package in required_packages:
        try:
            # Handle special cases
            if package == 'python_dotenv':
                importlib.import_module('dotenv')
            elif package == 'langchain_aws':
                importlib.import_module('langchain_aws')
            elif package == 'jose':
                importlib.import_module('jose')
            else:
                importlib.import_module(package)
            
            successful_imports.append(package)
            print(f"✅ {package}")
        except ImportError as e:
            failed_imports.append(package)
            print(f"❌ {package}: {e}")
        except Exception as e:
            failed_imports.append(package)
            print(f"❌ {package}: {e}")
    
    print("=" * 50)
    print(f"✅ Successful imports: {len(successful_imports)}")
    print(f"❌ Failed imports: {len(failed_imports)}")
    
    if failed_imports:
        print("\n❌ Failed packages:")
        for package in failed_imports:
            print(f"   - {package}")
        return False
    else:
        print("\n🎉 All packages imported successfully!")
        return True

def test_app_imports():
    """Test importing app-specific modules."""
    app_modules = [
        'config',
        'agents',
        'scoring',
        'storage',
        'aws_services',
        'auth',
        'utils',
        'nlp_metrics',
        'audio_recorder',
        'login_signup',
        'monitoring'
    ]
    
    failed_imports = []
    successful_imports = []
    
    print("\n🧪 Testing app module imports...")
    print("=" * 50)
    
    for module in app_modules:
        try:
            importlib.import_module(module)
            successful_imports.append(module)
            print(f"✅ {module}")
        except ImportError as e:
            failed_imports.append(module)
            print(f"❌ {module}: {e}")
        except Exception as e:
            failed_imports.append(module)
            print(f"❌ {module}: {e}")
    
    print("=" * 50)
    print(f"✅ Successful imports: {len(successful_imports)}")
    print(f"❌ Failed imports: {len(failed_imports)}")
    
    if failed_imports:
        print("\n❌ Failed modules:")
        for module in failed_imports:
            print(f"   - {module}")
        return False
    else:
        print("\n🎉 All app modules imported successfully!")
        return True

def main():
    """Main test function."""
    print("🧠 Cognora+ Requirements Test")
    print("=" * 50)
    
    # Test package imports
    packages_ok = test_imports()
    
    # Test app module imports
    modules_ok = test_app_imports()
    
    print("\n" + "=" * 50)
    if packages_ok and modules_ok:
        print("🎉 All tests passed! Your app is ready for deployment.")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues before deployment.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 