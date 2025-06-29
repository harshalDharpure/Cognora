#!/usr/bin/env python3
"""
Cognora+ - AI Wellness Assistant
Clean, working version
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from decimal import Decimal

# Simple imports
from utils import get_text
from storage import DataManager
from scoring import calculate_cognora_score, get_score_emoji
from login_signup import show_login_page

def safe_convert_decimal(value):
    """Safely convert Decimal types to regular Python types."""
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    return value

def main():
    """Main application function."""
    st.set_page_config(
        page_title="Cognora+ - AI Wellness Assistant",
        page_icon="🧠",
        layout="wide"
    )
    
    # Check authentication
    if 'user_id' not in st.session_state:
        show_login_page()
        return
    
    # User is authenticated
    user_id = st.session_state['user_id']
    
    # Simple sidebar
    with st.sidebar:
        st.title("🧠 Cognora+")
        page = st.selectbox("Page", ["Dashboard", "Daily Check-in", "Settings"], index=0)
    
    # Route to page
    if page == "Dashboard":
        show_dashboard(user_id)
    elif page == "Daily Check-in":
        show_daily_checkin(user_id)
    elif page == "Settings":
        show_settings(user_id)

def show_dashboard(user_id):
    """Dashboard page."""
    st.title("🧠 Dashboard")
    st.info(f"👤 User: {user_id}")
    
    try:
        # Get user data
        data_manager = DataManager()
        user_history = data_manager.get_user_history(user_id, 7)
        
        if user_history:
            st.success(f"✅ Found {len(user_history)} entries")
            
            # Show metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                today_score = user_history[0].get('score', 50.0)
                st.metric("Today's Score", f"{today_score:.1f}")
            
            with col2:
                avg_score = sum(entry.get('score', 50.0) for entry in user_history) / len(user_history)
                st.metric("Weekly Average", f"{avg_score:.1f}")
            
            with col3:
                st.metric("Days Tracked", len(user_history))
            
            # Show recent entries
            st.subheader("Recent Entries")
            for entry in user_history[:3]:
                date = entry.get('date', 'Unknown')
                score = entry.get('score', 0)
                emotion = entry.get('emotion', 'Unknown')
                st.write(f"**{date}:** Score {score:.1f} - {emotion}")
        else:
            st.warning("No data available. Start tracking your wellness!")
            
    except Exception as e:
        st.error(f"Error loading data: {e}")

def show_daily_checkin(user_id):
    """Daily check-in page."""
    st.title("📝 Daily Check-in")
    
    with st.form("checkin_form"):
        text = st.text_area("How are you feeling today?", height=150)
        submit = st.form_submit_button("Save Entry")
        
        if submit and text.strip():
            try:
                # Simple analysis
                data_manager = DataManager()
                
                # Calculate simple score
                score_data = calculate_cognora_score(
                    {'primary_emotion': 'neutral', 'confidence': 50},
                    {'sentiment': 0.5, 'complexity': 0.5}
                )
                
                # Save entry
                success = data_manager.save_daily_entry(
                    user_id=user_id,
                    date=datetime.now().strftime('%Y-%m-%d'),
                    transcript=text,
                    emotion_analysis={'primary_emotion': 'neutral'},
                    cognitive_metrics={'sentiment': 0.5},
                    score_data=score_data,
                    source='text'
                )
                
                if success:
                    st.success("✅ Entry saved successfully!")
                    st.balloons()
                else:
                    st.error("❌ Failed to save entry")
                    
            except Exception as e:
                st.error(f"Error saving entry: {e}")

def show_settings(user_id):
    """Settings page."""
    st.title("⚙️ Settings")
    
    if 'user_data' in st.session_state:
        user_data = st.session_state['user_data']
        st.write(f"Name: {safe_convert_decimal(user_data.get('full_name', 'N/A'))}")
        st.write(f"Email: {safe_convert_decimal(user_data.get('email', 'N/A'))}")
    
    if st.button("Logout"):
        for key in ['user_id', 'authenticated', 'user_data']:
            if key in st.session_state:
                del st.session_state[key]
        st.success("Logged out!")
        st.rerun()

if __name__ == "__main__":
    main()
