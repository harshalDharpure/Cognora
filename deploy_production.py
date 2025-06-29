#!/usr/bin/env python3
"""
Production Deployment Script for Cognora+
"""

import os
import sys
import subprocess
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List

class ProductionDeployer:
    """Handles production deployment for Cognora+."""
    
    def __init__(self, environment: str = "production", market: str = "global"):
        self.environment = environment
        self.market = market
        self.project_root = Path(__file__).parent
    
    def run_security_checks(self) -> bool:
        """Run security checks before deployment."""
        print("🔒 Running security checks...")
        
        checks = [
            self._check_environment_variables(),
            self._check_aws_credentials(),
            self._check_dependencies()
        ]
        
        all_passed = all(checks)
        if all_passed:
            print("✅ All security checks passed")
        else:
            print("❌ Some security checks failed")
        
        return all_passed
    
    def _check_environment_variables(self) -> bool:
        """Check required environment variables."""
        required_vars = [
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY',
            'AWS_DEFAULT_REGION'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"❌ Missing environment variables: {missing_vars}")
            return False
        
        print("✅ Environment variables configured")
        return True
    
    def _check_aws_credentials(self) -> bool:
        """Check AWS credentials and permissions."""
        try:
            import boto3
            sts = boto3.client('sts')
            identity = sts.get_caller_identity()
            print(f"✅ AWS credentials valid for account: {identity['Account']}")
            return True
        except Exception as e:
            print(f"❌ AWS credentials check failed: {e}")
            return False
    
    def _check_dependencies(self) -> bool:
        """Check Python dependencies."""
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'check'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Dependencies check passed")
                return True
            else:
                print(f"❌ Dependencies check failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Dependencies check error: {e}")
            return False
    
    def setup_environment(self):
        """Setup production environment."""
        print(f"🚀 Setting up {self.environment} environment for {self.market} market...")
        
        # Set environment variables
        os.environ['ENVIRONMENT'] = self.environment
        os.environ['MARKET'] = self.market
        
        # Install dependencies
        self._install_dependencies()
        
        # Setup AWS resources
        self._setup_aws_resources()
        
        # Initialize database
        self._initialize_database()
        
        print("✅ Environment setup complete")
    
    def _install_dependencies(self):
        """Install production dependencies."""
        print("📦 Installing dependencies...")
        
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ], check=True)
            print("✅ Dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            raise
    
    def _setup_aws_resources(self):
        """Setup AWS resources using Terraform."""
        print("☁️ Setting up AWS resources...")
        
        terraform_dir = self.project_root / 'terraform'
        
        try:
            # Initialize Terraform
            subprocess.run(['terraform', 'init'], cwd=terraform_dir, check=True)
            
            # Plan deployment
            subprocess.run([
                'terraform', 'plan',
                f'-var=environment={self.environment}',
                f'-var=market={self.market}',
                '-out=tfplan'
            ], cwd=terraform_dir, check=True)
            
            # Apply changes
            subprocess.run(['terraform', 'apply', 'tfplan'], cwd=terraform_dir, check=True)
            
            print("✅ AWS resources setup complete")
        except subprocess.CalledProcessError as e:
            print(f"❌ AWS setup failed: {e}")
            raise
    
    def _initialize_database(self):
        """Initialize database tables."""
        print("🗄️ Initializing database...")
        
        try:
            # Run database initialization
            subprocess.run([
                sys.executable, '-c',
                'from auth import test_auth_connection; test_auth_connection()'
            ], check=True)
            
            print("✅ Database initialized")
        except subprocess.CalledProcessError as e:
            print(f"❌ Database initialization failed: {e}")
            raise
    
    def deploy_to_streamlit_cloud(self):
        """Deploy to Streamlit Cloud."""
        print("☁️ Deploying to Streamlit Cloud...")
        
        try:
            # Check if git is configured
            result = subprocess.run(['git', 'status'], capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Git repository not configured")
                return False
            
            # Push to remote repository
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', f'Deploy to {self.environment}'], check=True)
            subprocess.run(['git', 'push'], check=True)
            
            print("✅ Deployed to Streamlit Cloud")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Streamlit Cloud deployment failed: {e}")
            return False
    
    def run_tests(self) -> bool:
        """Run production tests."""
        print("🧪 Running production tests...")
        
        tests = [
            'test_auth_system.py',
            'test_aws_setup.py',
            'test_voice_entries.py'
        ]
        
        all_passed = True
        for test_file in tests:
            if (self.project_root / test_file).exists():
                try:
                    result = subprocess.run([
                        sys.executable, test_file
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        print(f"✅ {test_file} passed")
                    else:
                        print(f"❌ {test_file} failed: {result.stderr}")
                        all_passed = False
                except Exception as e:
                    print(f"❌ {test_file} error: {e}")
                    all_passed = False
        
        return all_passed
    
    def generate_deployment_report(self) -> Dict[str, Any]:
        """Generate deployment report."""
        return {
            'environment': self.environment,
            'market': self.market,
            'timestamp': subprocess.run(['date'], capture_output=True, text=True).stdout.strip(),
            'git_commit': subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip(),
            'python_version': sys.version
        }

def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description='Deploy Cognora+ to production')
    parser.add_argument('--environment', default='production', choices=['staging', 'production'])
    parser.add_argument('--market', default='global', choices=['japan', 'us', 'global'])
    parser.add_argument('--skip-checks', action='store_true', help='Skip security checks')
    parser.add_argument('--skip-tests', action='store_true', help='Skip tests')
    
    args = parser.parse_args()
    
    deployer = ProductionDeployer(args.environment, args.market)
    
    print(f"🚀 Starting deployment to {args.environment} for {args.market} market")
    
    # Run security checks
    if not args.skip_checks:
        if not deployer.run_security_checks():
            print("❌ Security checks failed. Aborting deployment.")
            sys.exit(1)
    
    # Setup environment
    deployer.setup_environment()
    
    # Run tests
    if not args.skip_tests:
        if not deployer.run_tests():
            print("❌ Tests failed. Aborting deployment.")
            sys.exit(1)
    
    # Deploy to Streamlit Cloud
    success = deployer.deploy_to_streamlit_cloud()
    
    if success:
        # Generate report
        report = deployer.generate_deployment_report()
        print("\n📊 Deployment Report:")
        print(json.dumps(report, indent=2))
        
        print(f"\n🎉 Deployment to {args.environment} successful!")
        print(f"🌐 Market: {args.market}")
    else:
        print("❌ Deployment failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 