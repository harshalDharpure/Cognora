#!/usr/bin/env python3
"""
Login and Signup UI components for Cognora+
"""

import streamlit as st
from auth import (
    initialize_auth, register_user, login_user, 
    validate_email, validate_password, get_user_by_id
)
from utils import get_text
from decimal import Decimal

def safe_convert_decimal(value):
    """Safely convert Decimal types to regular Python types."""
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    return value

def show_login_page():
    """Display the login page."""
    st.title("🔐 Welcome to Cognora+")
    st.markdown("---")
    
    # Initialize authentication
    initialize_auth()
    
    # Create tabs for login and signup
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        show_login_form()
    
    with tab2:
        show_signup_form()

def show_login_form():
    """Display the login form."""
    st.subheader("Login to Your Account")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submit_button = st.form_submit_button("Login", type="primary")
        with col2:
            forgot_password = st.form_submit_button("Forgot Password?")
        
        if submit_button:
            if email and password:
                success, message, user_data = login_user(email, password)
                
                if success:
                    st.success("✅ Login successful!")
                    
                    # Store user data in session state
                    st.session_state['authenticated'] = True
                    st.session_state['user_id'] = user_data['user_id']
                    st.session_state['user_data'] = user_data
                    st.session_state['user_email'] = user_data['email']
                    st.session_state['user_name'] = user_data['full_name']
                    
                    # Set user preferences
                    preferences = user_data.get('preferences', {})
                    st.session_state['language'] = preferences.get('language', 'en')
                    st.session_state['theme'] = preferences.get('theme', 'light')
                    
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            else:
                st.error("Please enter both email and password")
        
        if forgot_password:
            st.info("Password reset functionality coming soon!")

def show_signup_form():
    """Display the signup form."""
    st.subheader("Create New Account")
    
    with st.form("signup_form"):
        # Personal Information
        st.markdown("**Personal Information**")
        full_name = st.text_input("Full Name", placeholder="Enter your full name")
        email = st.text_input("Email", placeholder="Enter your email address")
        age = st.number_input("Age", min_value=18, max_value=120, value=25)
        
        # Password
        st.markdown("**Security**")
        password = st.text_input("Password", type="password", placeholder="Create a strong password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        # Additional Information
        st.markdown("**Additional Information (Optional)**")
        location = st.text_input("Location", placeholder="City, State/Country")
        caregiver_email = st.text_input("Caregiver Email (Optional)", placeholder="caregiver@example.com")
        
        # Password strength indicator
        if password:
            is_valid, message = validate_password(password)
            if is_valid:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")
        
        # Terms and conditions
        agree_terms = st.checkbox("I agree to the Terms and Conditions and Privacy Policy")
        
        submit_button = st.form_submit_button("Create Account", type="primary")
        
        if submit_button:
            # Validate inputs
            if not all([full_name, email, password, confirm_password]):
                st.error("Please fill in all required fields")
                return
            
            if not validate_email(email):
                st.error("Please enter a valid email address")
                return
            
            if password != confirm_password:
                st.error("Passwords do not match")
                return
            
            is_valid, message = validate_password(password)
            if not is_valid:
                st.error(message)
                return
            
            if not agree_terms:
                st.error("Please agree to the Terms and Conditions")
                return
            
            # Register user
            success, message = register_user(
                email=email,
                password=password,
                full_name=full_name,
                age=age,
                location=location,
                caregiver_email=caregiver_email
            )
            
            if success:
                st.success("✅ Account created successfully!")
                st.info("You can now login with your email and password")
                
                # Clear form
                st.rerun()
            else:
                st.error(f"❌ {message}")

def show_logout():
    """Handle user logout."""
    if st.sidebar.button("🚪 Logout"):
        # Clear session state
        for key in ['authenticated', 'user_id', 'user_data', 'user_email', 'user_name', 'language', 'theme']:
            if key in st.session_state:
                del st.session_state[key]
        
        st.success("Logged out successfully!")
        st.rerun()

def check_authentication():
    """Check if user is authenticated."""
    if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
        show_login_page()
        st.stop()
    
    # Verify user still exists in database
    user_id = st.session_state.get('user_id')
    if user_id:
        user_data = get_user_by_id(user_id)
        if not user_data:
            st.error("User account not found. Please login again.")
            # Clear session state
            for key in ['authenticated', 'user_id', 'user_data', 'user_email', 'user_name', 'language', 'theme']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    return True

def show_user_profile():
    """Display user profile information."""
    if 'user_data' in st.session_state:
        user_data = st.session_state['user_data']
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("**👤 User Profile**")
        st.sidebar.markdown(f"**Name:** {safe_convert_decimal(user_data.get('full_name', 'N/A'))}")
        st.sidebar.markdown(f"**Email:** {safe_convert_decimal(user_data.get('email', 'N/A'))}")
        st.sidebar.markdown(f"**Age:** {safe_convert_decimal(user_data.get('age', 'N/A'))}")
        
        if user_data.get('location'):
            st.sidebar.markdown(f"**Location:** {safe_convert_decimal(user_data['location'])}")
        
        if user_data.get('caregiver_email'):
            st.sidebar.markdown(f"**Caregiver:** {safe_convert_decimal(user_data['caregiver_email'])}")
        
        # Show last login
        if user_data.get('last_login'):
            from datetime import datetime
            try:
                last_login = datetime.fromisoformat(user_data['last_login'].replace('Z', '+00:00'))
                st.sidebar.markdown(f"**Last Login:** {last_login.strftime('%Y-%m-%d %H:%M')}")
            except:
                pass

def show_password_change_form():
    """Display password change form in settings."""
    st.subheader("🔒 Change Password")
    
    with st.form("password_change_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_new_password = st.text_input("Confirm New Password", type="password")
        
        submit_button = st.form_submit_button("Change Password", type="primary")
        
        if submit_button:
            if not all([current_password, new_password, confirm_new_password]):
                st.error("Please fill in all password fields")
                return
            
            if new_password != confirm_new_password:
                st.error("New passwords do not match")
                return
            
            is_valid, message = validate_password(new_password)
            if not is_valid:
                st.error(message)
                return
            
            # Import change_password function
            from auth import change_password
            
            user_id = st.session_state.get('user_id')
            success, message = change_password(user_id, current_password, new_password)
            
            if success:
                st.success("✅ Password changed successfully!")
            else:
                st.error(f"❌ {message}")

def show_account_deactivation():
    """Display account deactivation option."""
    st.subheader("⚠️ Account Management")
    
    if st.button("🗑️ Deactivate Account", type="secondary"):
        # Import deactivate_user function
        from auth import deactivate_user
        
        user_id = st.session_state.get('user_id')
        if deactivate_user(user_id):
            st.success("Account deactivated successfully")
            
            # Clear session state and redirect to login
            for key in ['authenticated', 'user_id', 'user_data', 'user_email', 'user_name', 'language', 'theme']:
                if key in st.session_state:
                    del st.session_state[key]
            
            st.rerun()
        else:
            st.error("Failed to deactivate account")

if __name__ == "__main__":
    show_login_page() 