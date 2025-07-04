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
    """Display the login page with a beautiful healthcare UI."""
    st.markdown(
        """
        <style>
        .login-card {
            background-color: #E3F6FF;
            border-radius: 18px;
            padding: 2.5rem 2rem 2rem 2rem;
            box-shadow: 0 4px 24px rgba(46,139,192,0.10);
            margin: 2rem auto 2rem auto;
            max-width: 420px;
        }
        .login-header {
            text-align: center;
            color: #2E8BC0;
            font-size: 2.1rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .login-subtext {
            text-align: center;
            color: #222B45;
            font-size: 1.1rem;
            margin-bottom: 1.5rem;
        }
        body {
            background-color: #F6FBFF !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-header">🩺 Cognora+ Healthcare Portal</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtext">Welcome! Please sign in to continue.<br>Your wellness journey starts here.</div>', unsafe_allow_html=True)
    # Tabs for login and signup
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        show_login_form()
    with tab2:
        show_signup_form()
    st.markdown('</div>', unsafe_allow_html=True)

def show_login_form():
    """Display the login form with healthcare styling."""
    st.subheader("")  # Remove subheader for cleaner look
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns([2, 1])
        with col1:
            submit_button = st.form_submit_button("Sign In", type="primary")
        with col2:
            forgot_password = st.form_submit_button("Forgot Password?")
        if submit_button:
            if email and password:
                success, message, user_data = login_user(email, password)
                if success:
                    st.success("✅ Login successful!")
                    st.session_state['authenticated'] = True
                    st.session_state['user_id'] = user_data['user_id']
                    st.session_state['user_data'] = user_data
                    st.session_state['user_email'] = user_data['email']
                    st.session_state['user_name'] = user_data['full_name']
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
    """Display user profile information with beautiful healthcare-themed UI."""
    if 'user_data' in st.session_state:
        user_data = st.session_state['user_data']

        # Add custom CSS for beautiful profile styling
        st.sidebar.markdown(
            """
            <style>
            .profile-header-card {
                background: linear-gradient(135deg, #f8f9ff 0%, #e8f4fd 100%);
                border-radius: 16px;
                padding: 1.5rem 1rem 1rem 1rem;
                margin: 1rem 0 1.5rem 0;
                border: 1px solid #e1e8ed;
                box-shadow: 0 4px 20px rgba(46,139,192,0.08);
                text-align: center;
            }
            .profile-avatar {
                width: 80px;
                height: 80px;
                border-radius: 50%;
                background: linear-gradient(135deg, #2E8BC0 0%, #1E5F8A 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 1rem auto;
                font-size: 2rem;
                color: white;
                box-shadow: 0 4px 15px rgba(46,139,192,0.3);
            }
            .profile-name {
                font-size: 1.3rem;
                font-weight: 700;
                color: #2E8BC0;
                margin-bottom: 0.2rem;
            }
            .profile-subtitle {
                font-size: 0.95rem;
                color: #6c757d;
                font-weight: 500;
                margin-bottom: 0.5rem;
            }
            .profile-info-card {
                background: #fff;
                border-radius: 12px;
                padding: 1rem 1.2rem;
                margin-bottom: 1rem;
                border-left: 4px solid #2E8BC0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                display: flex;
                flex-direction: column;
                gap: 0.2rem;
            }
            .profile-info-label {
                font-size: 0.85rem;
                font-weight: 600;
                color: #2E8BC0;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 0.1rem;
                display: flex;
                align-items: center;
                gap: 0.3rem;
            }
            .profile-info-value {
                font-size: 1.05rem;
                font-weight: 600;
                color: #2c3e50;
            }
            .caregiver-card {
                background: linear-gradient(135deg, #fff5f5 0%, #ffe8e8 100%);
                border: 1px solid #ffd6d6;
                border-left: 4px solid #e74c3c;
            }
            .caregiver-card .profile-info-label {
                color: #e74c3c;
            }
            .caregiver-card .profile-info-value {
                color: #e74c3c;
            }
            .last-login-card {
                background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%);
                border: 1px solid #b3d9ff;
                border-left: 4px solid #3498db;
            }
            .last-login-card .profile-info-label {
                color: #3498db;
            }
            .last-login-card .profile-info-value {
                color: #3498db;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Get user initials for avatar
        full_name = safe_convert_decimal(user_data.get('full_name', 'N/A'))
        initials = ''.join([name[0].upper() for name in full_name.split() if name]) if full_name != 'N/A' else 'U'

        # Profile header card
        st.sidebar.markdown(
            f"""
            <div class="profile-header-card">
                <div class="profile-avatar">{initials}</div>
                <div class="profile-name">{full_name}</div>
                <div class="profile-subtitle">Cognora+ User</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Email card
        st.sidebar.markdown(
            f"""
            <div class="profile-info-card">
                <div class="profile-info-label">📧 Email Address</div>
                <div class="profile-info-value">{safe_convert_decimal(user_data.get('email', 'N/A'))}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Age card
        st.sidebar.markdown(
            f"""
            <div class="profile-info-card">
                <div class="profile-info-label">🎂 Age</div>
                <div class="profile-info-value">{safe_convert_decimal(user_data.get('age', 'N/A'))} years old</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Location card
        if user_data.get('location'):
            st.sidebar.markdown(
                f"""
                <div class="profile-info-card">
                    <div class="profile-info-label">📍 Location</div>
                    <div class="profile-info-value">{safe_convert_decimal(user_data['location'])}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Caregiver card
        if user_data.get('caregiver_email'):
            st.sidebar.markdown(
                f"""
                <div class="profile-info-card caregiver-card">
                    <div class="profile-info-label">🧑‍⚕️ Caregiver Contact</div>
                    <div class="profile-info-value">{safe_convert_decimal(user_data['caregiver_email'])}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Last login card
        if user_data.get('last_login'):
            from datetime import datetime
            try:
                last_login = datetime.fromisoformat(user_data['last_login'].replace('Z', '+00:00'))
                formatted_date = last_login.strftime('%B %d, %Y')
                formatted_time = last_login.strftime('%I:%M %p')
                st.sidebar.markdown(
                    f"""
                    <div class="profile-info-card last-login-card">
                        <div class="profile-info-label">🕒 Last Login</div>
                        <div class="profile-info-value">{formatted_date}<br><small>{formatted_time}</small></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
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