#!/usr/bin/env python3
"""
Authentication module for Cognora+
Handles user registration, login, and password management with AWS DynamoDB.
"""

import hashlib
import secrets
import re
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal
import streamlit as st

# AWS DynamoDB table for users
users_table = None

def convert_decimal_types(obj):
    """Convert DynamoDB Decimal types to regular Python types."""
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    elif isinstance(obj, dict):
        return {key: convert_decimal_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal_types(item) for item in obj]
    else:
        return obj

def initialize_auth():
    """Initialize AWS DynamoDB connection for user authentication."""
    global users_table
    
    try:
        # Initialize DynamoDB client
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
        # Create or get users table
        table_name = 'cognora_users'
        try:
            users_table = dynamodb.Table(table_name)
            # Test if table exists
            users_table.table_status
            print(f"✅ Users table '{table_name}' connected")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # Create table if it doesn't exist
                print(f"Creating users table '{table_name}'...")
                users_table = dynamodb.create_table(
                    TableName=table_name,
                    KeySchema=[
                        {
                            'AttributeName': 'user_id',
                            'KeyType': 'HASH'  # Partition key
                        }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'user_id',
                            'AttributeType': 'S'
                        }
                    ],
                    BillingMode='PAY_PER_REQUEST'
                )
                users_table.wait_until_exists()
                print(f"✅ Users table '{table_name}' created successfully")
            else:
                raise e
                
    except Exception as e:
        print(f"❌ Error initializing auth: {e}")
        users_table = None

def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt."""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256()
    hash_obj.update((password + salt).encode('utf-8'))
    return f"{salt}${hash_obj.hexdigest()}"

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        salt, hash_value = hashed_password.split('$')
        hash_obj = hashlib.sha256()
        hash_obj.update((password + salt).encode('utf-8'))
        return hash_obj.hexdigest() == hash_value
    except:
        return False

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> Tuple[bool, str]:
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, "Password is valid"

def generate_user_id(email: str) -> str:
    """Generate a unique user ID based on email."""
    hash_obj = hashlib.sha256()
    hash_obj.update(email.encode('utf-8'))
    return f"user_{hash_obj.hexdigest()[:16]}"

def register_user(email: str, password: str, full_name: str, age: int, location: str = "", caregiver_email: str = "") -> Tuple[bool, str]:
    """
    Register a new user.
    
    Args:
        email: User's email address
        password: User's password
        full_name: User's full name
        age: User's age
        location: User's location (optional)
        caregiver_email: Caregiver's email (optional)
    
    Returns:
        Tuple of (success, message)
    """
    if not users_table:
        return False, "Authentication system not initialized"
    
    # Validate inputs
    if not email or not password or not full_name:
        return False, "All required fields must be filled"
    
    if not validate_email(email):
        return False, "Invalid email format"
    
    password_valid, password_msg = validate_password(password)
    if not password_valid:
        return False, password_msg
    
    if age < 18 or age > 120:
        return False, "Age must be between 18 and 120"
    
    try:
        # Check if user already exists
        user_id = generate_user_id(email)
        response = users_table.get_item(Key={'user_id': user_id})
        
        if 'Item' in response:
            return False, "User with this email already exists"
        
        # Create new user
        hashed_password = hash_password(password)
        user_data = {
            'user_id': user_id,
            'email': email.lower(),
            'password_hash': hashed_password,
            'full_name': full_name,
            'age': age,
            'location': location,
            'caregiver_email': caregiver_email,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'is_active': True,
            'preferences': {
                'language': 'en',
                'theme': 'light',
                'notifications': True,
                'alert_sensitivity': 'medium'
            }
        }
        
        users_table.put_item(Item=user_data)
        print(f"✅ User registered successfully: {user_id}")
        return True, f"User registered successfully! User ID: {user_id}"
        
    except Exception as e:
        print(f"❌ Error registering user: {e}")
        return False, f"Registration failed: {str(e)}"

def login_user(email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
    """
    Authenticate a user.
    
    Args:
        email: User's email address
        password: User's password
    
    Returns:
        Tuple of (success, message, user_data)
    """
    if not users_table:
        return False, "Authentication system not initialized", None
    
    if not email or not password:
        return False, "Email and password are required", None
    
    try:
        # Find user by email
        user_id = generate_user_id(email)
        response = users_table.get_item(Key={'user_id': user_id})
        
        if 'Item' not in response:
            return False, "Invalid email or password", None
        
        user_data = response['Item']
        
        # Convert Decimal types to regular Python types
        user_data = convert_decimal_types(user_data)
        
        # Verify password
        if not verify_password(password, user_data['password_hash']):
            return False, "Invalid email or password", None
        
        # Check if user is active
        if not user_data.get('is_active', True):
            return False, "Account is deactivated", None
        
        # Update last login
        users_table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='SET last_login = :last_login',
            ExpressionAttributeValues={':last_login': datetime.now().isoformat()}
        )
        
        # Remove sensitive data before returning
        safe_user_data = {k: v for k, v in user_data.items() if k != 'password_hash'}
        
        print(f"✅ User logged in successfully: {user_id}")
        return True, "Login successful", safe_user_data
        
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return False, f"Login failed: {str(e)}", None

def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Get user data by user ID."""
    if not users_table:
        return None
    
    try:
        response = users_table.get_item(Key={'user_id': user_id})
        if 'Item' in response:
            user_data = response['Item']
            # Convert Decimal types to regular Python types
            user_data = convert_decimal_types(user_data)
            # Remove sensitive data
            safe_user_data = {k: v for k, v in user_data.items() if k != 'password_hash'}
            return safe_user_data
        return None
    except Exception as e:
        print(f"❌ Error getting user: {e}")
        return None

def update_user_preferences(user_id: str, preferences: Dict) -> bool:
    """Update user preferences."""
    if not users_table:
        return False
    
    try:
        users_table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='SET preferences = :preferences',
            ExpressionAttributeValues={':preferences': preferences}
        )
        return True
    except Exception as e:
        print(f"❌ Error updating preferences: {e}")
        return False

def change_password(user_id: str, current_password: str, new_password: str) -> Tuple[bool, str]:
    """Change user password."""
    if not users_table:
        return False, "Authentication system not initialized"
    
    try:
        # Get current user data
        response = users_table.get_item(Key={'user_id': user_id})
        if 'Item' not in response:
            return False, "User not found"
        
        user_data = response['Item']
        
        # Verify current password
        if not verify_password(current_password, user_data['password_hash']):
            return False, "Current password is incorrect"
        
        # Validate new password
        password_valid, password_msg = validate_password(new_password)
        if not password_valid:
            return False, password_msg
        
        # Hash new password
        new_hashed_password = hash_password(new_password)
        
        # Update password
        users_table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='SET password_hash = :password_hash',
            ExpressionAttributeValues={':password_hash': new_hashed_password}
        )
        
        return True, "Password changed successfully"
        
    except Exception as e:
        print(f"❌ Error changing password: {e}")
        return False, f"Password change failed: {str(e)}"

def deactivate_user(user_id: str) -> bool:
    """Deactivate a user account."""
    if not users_table:
        return False
    
    try:
        users_table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='SET is_active = :is_active',
            ExpressionAttributeValues={':is_active': False}
        )
        return True
    except Exception as e:
        print(f"❌ Error deactivating user: {e}")
        return False

def test_auth_connection():
    """Test AWS connection for authentication."""
    print("=== Testing Authentication System ===")
    
    try:
        initialize_auth()
        
        if users_table:
            print("✅ Authentication system initialized successfully")
            
            # Test table access
            try:
                users_table.table_status
                print("✅ Users table accessible")
                return True
            except Exception as e:
                print(f"❌ Users table not accessible: {e}")
                return False
        else:
            print("❌ Authentication system initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing auth connection: {e}")
        return False

if __name__ == "__main__":
    test_auth_connection() 