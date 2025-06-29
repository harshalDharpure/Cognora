#!/usr/bin/env python3
"""
Test script for the authentication system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth import (
    initialize_auth, register_user, login_user, 
    validate_email, validate_password, get_user_by_id,
    change_password, deactivate_user, test_auth_connection
)

def test_authentication_system():
    """Test the complete authentication system."""
    print("=== Testing Authentication System ===")
    
    # Test 1: Initialize authentication
    print("\n--- Test 1: Initialize Authentication ---")
    initialize_auth()
    
    # Test 2: Test AWS connection
    print("\n--- Test 2: Test AWS Connection ---")
    if test_auth_connection():
        print("✅ AWS connection successful")
    else:
        print("❌ AWS connection failed")
        return
    
    # Test 3: Test email validation
    print("\n--- Test 3: Email Validation ---")
    test_emails = [
        "test@example.com",
        "invalid-email",
        "user@domain.co.uk",
        "test.email@subdomain.example.org"
    ]
    
    for email in test_emails:
        is_valid = validate_email(email)
        print(f"{email}: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    # Test 4: Test password validation
    print("\n--- Test 4: Password Validation ---")
    test_passwords = [
        "weak",
        "StrongPass123",
        "no_numbers",
        "NO_LOWERCASE123",
        "no_uppercase123",
        "ValidPass123"
    ]
    
    for password in test_passwords:
        is_valid, message = validate_password(password)
        print(f"'{password}': {'✅ Valid' if is_valid else '❌ Invalid'} - {message}")
    
    # Test 5: Register a test user
    print("\n--- Test 5: User Registration ---")
    test_email = "testuser@example.com"
    test_password = "TestPass123"
    test_name = "Test User"
    test_age = 30
    
    success, message = register_user(
        email=test_email,
        password=test_password,
        full_name=test_name,
        age=test_age,
        location="Test City",
        caregiver_email="caregiver@example.com"
    )
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
        # If user already exists, that's okay for testing
    
    # Test 6: Login with test user
    print("\n--- Test 6: User Login ---")
    success, message, user_data = login_user(test_email, test_password)
    
    if success:
        print(f"✅ {message}")
        print(f"User ID: {user_data['user_id']}")
        print(f"Name: {user_data['full_name']}")
        print(f"Email: {user_data['email']}")
        print(f"Age: {user_data['age']}")
        print(f"Location: {user_data.get('location', 'N/A')}")
        print(f"Caregiver: {user_data.get('caregiver_email', 'N/A')}")
        print(f"Created: {user_data.get('created_at', 'N/A')}")
        print(f"Last Login: {user_data.get('last_login', 'N/A')}")
        print(f"Preferences: {user_data.get('preferences', 'N/A')}")
        
        user_id = user_data['user_id']
    else:
        print(f"❌ {message}")
        return
    
    # Test 7: Get user by ID
    print("\n--- Test 7: Get User by ID ---")
    retrieved_user = get_user_by_id(user_id)
    
    if retrieved_user:
        print(f"✅ User retrieved successfully")
        print(f"Name: {retrieved_user['full_name']}")
        print(f"Email: {retrieved_user['email']}")
    else:
        print("❌ Failed to retrieve user")
    
    # Test 8: Test invalid login
    print("\n--- Test 8: Invalid Login Test ---")
    success, message, user_data = login_user(test_email, "wrongpassword")
    
    if not success:
        print(f"✅ Invalid login correctly rejected: {message}")
    else:
        print("❌ Invalid login was accepted (this is wrong)")
    
    # Test 9: Change password
    print("\n--- Test 9: Change Password ---")
    new_password = "NewTestPass456"
    
    success, message = change_password(user_id, test_password, new_password)
    
    if success:
        print(f"✅ {message}")
        
        # Test login with new password
        success, message, user_data = login_user(test_email, new_password)
        if success:
            print("✅ Login with new password successful")
        else:
            print(f"❌ Login with new password failed: {message}")
    else:
        print(f"❌ {message}")
    
    # Test 10: Test duplicate registration
    print("\n--- Test 10: Duplicate Registration Test ---")
    success, message = register_user(
        email=test_email,
        password="AnotherPass123",
        full_name="Another User",
        age=25
    )
    
    if not success:
        print(f"✅ Duplicate registration correctly rejected: {message}")
    else:
        print("❌ Duplicate registration was accepted (this is wrong)")
    
    # Test 11: Deactivate user
    print("\n--- Test 11: Deactivate User ---")
    success = deactivate_user(user_id)
    
    if success:
        print("✅ User deactivated successfully")
        
        # Test login with deactivated account
        success, message, user_data = login_user(test_email, new_password)
        if not success:
            print(f"✅ Login correctly rejected for deactivated account: {message}")
        else:
            print("❌ Login accepted for deactivated account (this is wrong)")
    else:
        print("❌ Failed to deactivate user")
    
    print("\n=== Authentication System Test Complete ===")

if __name__ == "__main__":
    test_authentication_system() 