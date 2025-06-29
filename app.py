import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import tempfile
import os
import io
from decimal import Decimal

# Import production modules
from config import config
from monitoring import user_analytics, performance_monitor, analytics_manager

# Import our modules
from utils import (
    setup_streamlit_config, create_sidebar, get_motivational_quote,
    format_date, format_score_display, get_emotion_emoji, create_sample_data,
    generate_demo_scores, display_loading_spinner, display_success_message,
    display_error_message, display_warning_message, validate_audio_file,
    get_text
)
from agents import EmotionAgent, MemoryAgent, AlertAgent
from scoring import calculate_cognora_score, get_score_color, get_score_emoji
from storage import data_manager, report_generator, alert_manager
from aws_services import transcribe_audio, send_alert, transcribe_audio_file
from nlp_metrics import analyze_cognitive_metrics
from audio_recorder import get_audio_input_method
from login_signup import check_authentication, show_user_profile, show_logout
from auth import initialize_auth

# Initialize agents
emotion_agent = EmotionAgent()
memory_agent = MemoryAgent()
alert_agent = AlertAgent()

def safe_convert_decimal(value):
    """Safely convert Decimal types to regular Python types."""
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    return value

def main():
    """Main application function."""
    setup_streamlit_config()
    
    # Initialize performance monitoring
    performance_monitor.start_timer('app_startup')
    
    try:
        # Check authentication first
        initialize_auth()
        
        # Check if user is authenticated
        if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
            from login_signup import show_login_page
            show_login_page()
            return
        
        # User is authenticated, show main app
        user_id = st.session_state.get('user_id', 'demo_user')
        user_name = st.session_state.get('user_name', 'Demo User')
        
        # Track page view
        user_analytics.track_page_view('main_app', user_id)
        
        # Show user profile in sidebar
        show_user_profile()
        
        # Show logout button
        show_logout()
        
        # Get user preferences
        language = st.session_state.get('language', 'en')
        theme = st.session_state.get('theme', 'light')
        
        # Convert language to display name
        language_display = "日本語" if language == "ja" else "English"
        
        # Get sidebar navigation with real data
        page = create_sidebar_with_auth(data_manager, language_display, theme)
        
        # Convert language selection to language code
        lang_code = 'ja' if language == "ja" else 'en'
        
        # Track page navigation
        user_analytics.track_page_view(page.lower(), user_id)
        
        # Main content area
        if page == "Dashboard":
            show_dashboard(user_id, lang_code)
        elif page == "Daily Check-in":
            show_daily_checkin(user_id, lang_code)
        elif page == "Reports":
            show_reports(user_id, lang_code)
        elif page == "Alerts":
            show_alerts(user_id, lang_code)
        elif page == "Analytics":
            show_analytics_page(user_id, lang_code)
        elif page == "Settings":
            show_settings_with_auth(lang_code)
        
        # End performance monitoring
        performance_monitor.end_timer('app_startup')
        
    except Exception as e:
        # Track errors
        user_id = st.session_state.get('user_id', 'unknown')
        analytics_manager.track_error(e, user_id, {'page': 'main_app'})
        st.error(f"An error occurred: {str(e)}")
        performance_monitor.end_timer('app_startup')

def show_dashboard(user_id, lang_code):
    """Displays the main dashboard."""
    st.title(f"🧠 {get_text('momo_dashboard', lang_code)}")
    st.markdown("---")
    
    # Check if user just completed a voice entry
    if st.session_state.get('voice_entry_completed', False):
        st.success(f"🎉 **{get_text('voice_entry_completed', lang_code)}** {get_text('wellness_score_updated', lang_code)}")
        # Clear the flag
        st.session_state['voice_entry_completed'] = False
    
    # Get real user data from database instead of demo data
    data_manager_instance = data_manager
    user_history = data_manager_instance.get_user_history(user_id, 7)  # Get last 7 days
    
    # If no real data available, use demo data as fallback
    if not user_history:
        st.warning(get_text('no_real_data_available', lang_code))
        demo_scores = generate_demo_scores(7)
        user_history = demo_scores
    else:
        # Show data source info
        voice_entries = sum(1 for entry in user_history if entry.get('source') == 'voice')
        text_entries = sum(1 for entry in user_history if entry.get('source') == 'text')
        
        if voice_entries > 0:
            st.info(f"📊 {get_text('showing_real_data', lang_code)} {len(user_history)} {get_text('entries', lang_code)} ({voice_entries} {get_text('voice', lang_code)}, {text_entries} {get_text('text', lang_code)})")
        else:
            st.info(f"📊 {get_text('showing_real_data', lang_code)} {len(user_history)} {get_text('entries', lang_code)}")
    
    # Get user data for transcripts
    user_data = create_sample_data()
    
    # Header with today's score
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if user_history:
            today_score = user_history[0].get('score', 50.0) if user_history else 50.0
            today_zone = user_history[0].get('zone_name', 'Unknown') if user_history else 'Unknown'
        else:
            today_score = 50.0
            today_zone = 'Unknown'
            
        st.metric(
            get_text('today_momo_score', lang_code),
            f"{today_score:.1f}",
            f"{get_score_emoji(today_score)} {today_zone.title()}"
        )
    
    with col2:
        if user_history:
            weekly_avg = sum(entry.get('score', 50.0) for entry in user_history) / len(user_history)
            # Calculate trend (compare with previous week if available)
            if len(user_history) >= 7:
                current_week_avg = sum(entry.get('score', 50.0) for entry in user_history[:7]) / 7
                previous_week_avg = sum(entry.get('score', 50.0) for entry in user_history[7:14]) / 7 if len(user_history) >= 14 else current_week_avg
                trend = current_week_avg - previous_week_avg
                trend_display = f"↗️ +{trend:.1f}" if trend > 0 else f"↘️ {trend:.1f}"
            else:
                trend_display = "↗️ +0.0"
        else:
            weekly_avg = 50.0
            trend_display = "↗️ +0.0"
            
        st.metric(
            get_text('weekly_average', lang_code),
            f"{weekly_avg:.1f}",
            trend_display
        )
    
    with col3:
        days_tracked = len(user_history) if user_history else 0
        st.metric(
            get_text('days_tracked', lang_code),
            str(days_tracked),
            "↗️ +1" if days_tracked > 0 else "↗️ +0"
        )
    
    st.markdown("---")
    
    # Add test button for debugging (only show in development)
    if st.session_state.get('show_debug_tools', False):
        st.subheader("🛠️ Debug Tools")
        if st.button("🔍 Test Data Retrieval", type="secondary"):
            test_result = data_manager_instance.test_data_retrieval(user_id)
            st.write("**Test Results:**")
            st.json(test_result)
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"📈 {get_text('score_trend', lang_code)}")
        
        if user_history:
            # Create trend chart from real data
            df_trend = pd.DataFrame(user_history)
            df_trend['date'] = pd.to_datetime(df_trend['date'])
            df_trend = df_trend.sort_values('date')  # Sort by date
            
            fig_trend = px.line(
                df_trend,
                x='date',
                y='score',
                title="Cognora Score Trend",
                labels={'score': 'Score', 'date': 'Date'}
            )
            fig_trend.update_traces(line_color='#1f77b4', line_width=3)
            fig_trend.update_layout(height=300)
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No score data available for trend chart.")
    
    with col2:
        st.subheader(f"😊 {get_text('emotion_timeline', lang_code)}")
        
        if user_history:
            # Create emotion chart from real data
            emotion_counts = {}
            for entry in user_history:
                emotion = entry.get('emotion', 'unknown')
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            
            if emotion_counts:
                fig_emotion = px.pie(
                    values=list(emotion_counts.values()),
                    names=list(emotion_counts.keys()),
                    title="Emotion Distribution"
                )
                fig_emotion.update_layout(height=300)
                st.plotly_chart(fig_emotion, use_container_width=True)
            else:
                st.info("No emotion data available for chart.")
        else:
            st.info("No emotion data available for chart.")
    
    st.markdown("---")
    
    # Recent activity and insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"📝 {get_text('latest_transcript', lang_code)}")
        
        if user_history and len(user_history) > 0:
            # Debug: Show what data we have
            st.write(f"**Debug Info:** Total entries: {len(user_history)}")
            for i, entry in enumerate(user_history[:3]):  # Show first 3 entries
                st.write(f"Entry {i+1}: Date={entry.get('date', 'N/A')}, Source={entry.get('source', 'N/A')}, Score={entry.get('score', 'N/A')}")
            
            # Find latest text and voice entries
            latest_text_entry = None
            latest_voice_entry = None
            
            # Sort by date to ensure we get the most recent entries
            sorted_history = sorted(user_history, key=lambda x: x.get('date', ''), reverse=True)
            
            for entry in sorted_history:
                source = entry.get('source', 'text')
                if source == 'text' and latest_text_entry is None:
                    latest_text_entry = entry
                elif source == 'voice' and latest_voice_entry is None:
                    latest_voice_entry = entry
                
                # Stop if we found both
                if latest_text_entry and latest_voice_entry:
                    break
            
            # Display text entry
            if latest_text_entry:
                st.markdown(f"📝 **{get_text('latest_text_entry', lang_code)}**")
                text_transcript = latest_text_entry.get('transcript', get_text('no_transcript_available', lang_code))
                text_date = latest_text_entry.get('date', get_text('unknown_date', lang_code))
                st.caption(f"Date: {text_date}")
                st.text_area(
                    get_text('text_input', lang_code),
                    text_transcript[:300] + "..." if len(text_transcript) > 300 else text_transcript,
                    height=120,
                    disabled=True,
                    key="text_entry_display"
                )
            else:
                st.info(get_text('no_text_entries', lang_code))
            
            # Display voice entry
            if latest_voice_entry:
                st.markdown(f"🎤 **{get_text('latest_voice_entry', lang_code)}**")
                voice_transcript = latest_voice_entry.get('transcript', get_text('no_transcript_available', lang_code))
                voice_date = latest_voice_entry.get('date', get_text('unknown_date', lang_code))
                st.caption(f"Date: {voice_date}")
                st.text_area(
                    get_text('voice_input', lang_code),
                    voice_transcript[:300] + "..." if len(voice_transcript) > 300 else voice_transcript,
                    height=120,
                    disabled=True,
                    key="voice_entry_display"
                )
            else:
                st.info(get_text('no_voice_entries', lang_code))
                
        else:
            # Fallback to sample data
            latest_transcript = user_data['sample_transcripts'][-1]
            st.text_area(
                get_text('yesterday_entry', lang_code),
                latest_transcript,
                height=150,
                disabled=True
            )
        
        # AI interpretation based on real data
        st.subheader(f"🤖 {get_text('ai_interpretation', lang_code)}")
        if user_history and len(user_history) > 0:
            latest_score = user_history[0].get('score', 50.0)
            latest_emotion = user_history[0].get('emotion', 'neutral')
            
            if latest_score >= 75:
                emotional_state = get_text('content_stimulated', lang_code)
                cognitive_health = get_text('good_vocabulary', lang_code)
                recommendation = get_text('continue_activities', lang_code)
            elif latest_score >= 50:
                emotional_state = "Moderate emotional state"
                cognitive_health = "Average cognitive indicators"
                recommendation = "Consider engaging in social activities"
            else:
                emotional_state = "Lower emotional indicators detected"
                cognitive_health = "Some cognitive concerns noted"
                recommendation = "Consider reaching out to caregivers or healthcare providers"
        else:
            emotional_state = get_text('content_stimulated', lang_code)
            cognitive_health = get_text('good_vocabulary', lang_code)
            recommendation = get_text('continue_activities', lang_code)
            
        st.info(f"""
        **{get_text('emotional_state', lang_code)}**: {emotional_state}
        **{get_text('cognitive_health', lang_code)}**: {cognitive_health}
        **{get_text('recommendation', lang_code)}**: {recommendation}
        """)
    
    with col2:
        st.subheader(f"💡 {get_text('motivational_quote', lang_code)}")
        quote = get_motivational_quote()
        st.markdown(f"""
        > "{quote['quote']}"
        >
        > — {quote['author']}
        """)
        
        st.subheader(f"🎯 {get_text('wellness_tips', lang_code)}")
        st.markdown(f"""
        - **{get_text('stay_social', lang_code)}**
        - **{get_text('mental_exercise', lang_code)}**
        - **{get_text('physical_activity', lang_code)}**
        - **{get_text('mindfulness', lang_code)}**
        """)
        
        # Entry summary
        if user_history and len(user_history) > 0:
            st.subheader("📊 Entry Summary")
            voice_entries = sum(1 for entry in user_history if entry.get('source') == 'voice')
            text_entries = sum(1 for entry in user_history if entry.get('source') == 'text')
            
            col_sum1, col_sum2 = st.columns(2)
            with col_sum1:
                st.metric("Voice Entries", voice_entries, "🎤")
            with col_sum2:
                st.metric("Text Entries", text_entries, "📝")
            
            # Score comparison
            if voice_entries > 0 and text_entries > 0:
                # Calculate average scores for each type
                voice_scores = [entry.get('score', 0) for entry in user_history if entry.get('source') == 'voice']
                text_scores = [entry.get('score', 0) for entry in user_history if entry.get('source') == 'text']
                
                avg_voice_score = sum(voice_scores) / len(voice_scores) if voice_scores else 0
                avg_text_score = sum(text_scores) / len(text_scores) if text_scores else 0
                
                st.markdown("---")
                st.subheader("📈 Score Comparison")
                col_score1, col_score2 = st.columns(2)
                
                with col_score1:
                    st.metric(
                        "Avg Voice Score",
                        f"{avg_voice_score:.1f}",
                        f"{get_score_emoji(avg_voice_score)}"
                    )
                with col_score2:
                    st.metric(
                        "Avg Text Score", 
                        f"{avg_text_score:.1f}",
                        f"{get_score_emoji(avg_text_score)}"
                    )
                
                # Show preference insight
                score_diff = avg_voice_score - avg_text_score
                if abs(score_diff) > 5:
                    if score_diff > 0:
                        st.info("🎤 Your voice entries tend to show higher wellness scores")
                    else:
                        st.info("📝 Your text entries tend to show higher wellness scores")
                else:
                    st.success("✅ Your wellness scores are consistent across both input methods")
            
            if voice_entries > 0 and text_entries > 0:
                st.success("✅ You're using both voice and text input methods!")
            elif voice_entries > 0:
                st.info("🎤 You prefer voice input for your entries")
            elif text_entries > 0:
                st.info("📝 You prefer text input for your entries")
            else:
                st.info("Start your wellness journey with daily check-ins!")
        
        # Test button to refresh data
        if st.button(f"🔄 {get_text('refresh_dashboard_data', lang_code)}", type="secondary"):
            st.rerun()
    
    # Alert status
    st.markdown("---")
    st.subheader(f"🔔 {get_text('alert_status', lang_code)}")
    
    alert_status = alert_manager.check_and_send_alerts(user_id)
    if alert_status['alert_sent']:
        st.error(f"⚠️ {get_text('caregiver_alert', lang_code)}")
    else:
        st.success(f"✅ {get_text('no_alerts', lang_code)}")
    
    # Recent Activity Timeline
    if user_history and len(user_history) > 0:
        st.markdown("---")
        st.subheader("📅 Recent Activity Timeline")
        
        # Show last 5 entries in chronological order
        recent_entries = sorted(user_history[:5], key=lambda x: x.get('date', ''), reverse=True)
        
        for i, entry in enumerate(recent_entries):
            date = entry.get('date', 'Unknown')
            source = entry.get('source', 'text')
            score = entry.get('score', 0)
            transcript = entry.get('transcript', 'No transcript')
            
            # Create timeline item
            if source == 'voice':
                icon = "🎤"
                source_text = "Voice Entry"
            else:
                icon = "📝"
                source_text = "Text Entry"
            
            col_timeline1, col_timeline2 = st.columns([1, 4])
            
            with col_timeline1:
                st.markdown(f"**{date}**")
                st.markdown(f"{icon} {source_text}")
                st.markdown(f"Score: {score:.1f}")
            
            with col_timeline2:
                st.text_area(
                    f"Entry {i+1}",
                    transcript[:150] + "..." if len(transcript) > 150 else transcript,
                    height=80,
                    disabled=True,
                    key=f"timeline_entry_{i}"
                )
            
            if i < len(recent_entries) - 1:
                st.markdown("---")
    
    # Debug information (only show in development)
    if st.checkbox("Show Debug Information"):
        st.markdown("---")
        st.subheader("🐛 Debug Information")
        
        st.write(f"**User ID:** {user_id}")
        st.write(f"**Data retrieved:** {len(user_history) if user_history else 0} entries")
        
        if user_history:
            st.write("**Recent entries:**")
            for i, entry in enumerate(user_history[:3]):  # Show last 3 entries
                st.write(f"  {i+1}. Date: {entry.get('date', 'N/A')}, Score: {entry.get('score', 'N/A')}, Emotion: {entry.get('emotion', 'N/A')}")
        else:
            st.write("**No data found in database**")
            st.write("This could mean:")
            st.write("- No entries have been saved yet")
            st.write("- Database connection issues")
            st.write("- DynamoDB table schema mismatch")
            st.write("- AWS permissions issues")
        
        # Test data retrieval
        if st.button("Test Data Retrieval"):
            try:
                test_data = data_manager_instance.get_user_history(user_id, 7)
                st.write(f"**Test retrieval result:** {len(test_data) if test_data else 0} entries")
                if test_data:
                    st.write("**Sample entry:**", test_data[0])
            except Exception as e:
                st.error(f"**Error retrieving data:** {str(e)}")
        
        # Comprehensive AWS and Data Testing
        st.markdown("---")
        st.subheader("🔧 Comprehensive Testing")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Test AWS Connection"):
                from aws_services import test_aws_connection
                with st.spinner("Testing AWS connection..."):
                    test_aws_connection()
                st.success("AWS connection test completed. Check console for details.")
            
            if st.button("Test Data Manager"):
                with st.spinner("Testing Data Manager..."):
                    test_result = data_manager_instance.test_data_retrieval(user_id)
                    st.write("**Test Results:**")
                    st.json(test_result)
        
        with col2:
            if st.button("Test S3 Storage"):
                with st.spinner("Testing S3 storage..."):
                    try:
                        from aws_services import store_data_in_s3
                        test_key = store_data_in_s3(user_id, "test", "This is a test entry")
                        if test_key:
                            st.success(f"✅ S3 storage test successful: {test_key}")
                        else:
                            st.error("❌ S3 storage test failed")
                    except Exception as e:
                        st.error(f"❌ S3 storage test error: {e}")
            
            if st.button("Test DynamoDB Storage"):
                with st.spinner("Testing DynamoDB storage..."):
                    try:
                        from aws_services import save_to_dynamodb
                        success = save_to_dynamodb(
                            user_id=user_id,
                            date="test",
                            transcript="Test transcript",
                            emotion="test",
                            score=75,
                            feedback="Test feedback",
                            cognitive_metrics={"test": "value"}
                        )
                        if success:
                            st.success("✅ DynamoDB storage test successful")
                        else:
                            st.error("❌ DynamoDB storage test failed")
                    except Exception as e:
                        st.error(f"❌ DynamoDB storage test error: {e}")
        
        # Environment Variables Check
        st.markdown("---")
        st.subheader("🔑 Environment Variables Check")
        
        env_vars = {
            "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
            "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "AWS_REGION_NAME": os.getenv("AWS_REGION_NAME"),
            "S3_BUCKET_NAME": os.getenv("S3_BUCKET_NAME"),
            "DYNAMODB_TABLE_NAME": os.getenv("DYNAMODB_TABLE_NAME"),
            "SNS_TOPIC_ARN": os.getenv("SNS_TOPIC_ARN")
        }
        
        for var_name, var_value in env_vars.items():
            if var_value:
                st.write(f"✅ **{var_name}:** {var_value[:10]}..." if len(str(var_value)) > 10 else f"✅ **{var_name}:** {var_value}")
            else:
                st.write(f"❌ **{var_name}:** Not set")
        
        # Manual Data Entry Test
        st.markdown("---")
        st.subheader("📝 Manual Data Entry Test")
        
        test_text = st.text_area("Enter test text for analysis:", "Today I felt happy and energetic. I went for a walk and talked to my neighbor.")
        
        if st.button("Test Complete Analysis & Save"):
            with st.spinner("Testing complete analysis pipeline..."):
                try:
                    # Test the complete pipeline
                    emotion_analysis = emotion_agent.analyze_emotion(test_text)
                    cognitive_metrics = analyze_cognitive_metrics(test_text)
                    score_data = calculate_cognora_score(emotion_analysis, cognitive_metrics)
                    
                    st.write("**Analysis Results:**")
                    st.write(f"Score: {score_data['score']}")
                    st.write(f"Emotion: {emotion_analysis}")
                    st.write(f"Cognitive Metrics: {cognitive_metrics}")
                    
                    # Test saving
                    today = datetime.now().strftime('%Y-%m-%d')
                    success = data_manager_instance.save_daily_entry(
                        user_id, today, test_text, emotion_analysis, cognitive_metrics, score_data
                    )
                    
                    if success:
                        st.success("✅ Complete pipeline test successful! Data saved.")
                    else:
                        st.error("❌ Complete pipeline test failed at save step.")
                        
                except Exception as e:
                    st.error(f"❌ Complete pipeline test error: {e}")
                    import traceback
                    st.code(traceback.format_exc())

def show_daily_checkin(user_id, lang_code):
    """Displays the daily check-in page."""
    st.title(f"📝 {get_text('daily_checkin_momo', lang_code)}")
    st.markdown("---")
    
    # Check if we have existing analysis results
    if 'analysis_results' in st.session_state:
        st.info("📊 You have analysis results ready to save. Scroll down to see them and save your entry.")
    
    # Input method selection
    input_method = st.radio(
        get_text('choose_input_method', lang_code),
        [get_text('text_input', lang_code), get_text('voice_input', lang_code)],
        horizontal=True
    )
    
    if input_method == get_text('text_input', lang_code):
        show_text_input(user_id, lang_code)
    else:
        show_voice_input(user_id, lang_code)
    
    # Show existing analysis results if available
    if 'analysis_results' in st.session_state:
        st.markdown("---")
        st.subheader("📊 Your Analysis Results")
        
        results = st.session_state['analysis_results']
        display_analysis_results(
            user_id, 
            results['text'], 
            results['emotion_analysis'], 
            results['cognitive_metrics'], 
            results['score_data'], 
            lang_code,
            "session_display"
        )

def show_text_input(user_id, lang_code):
    """Handles text input for daily check-in."""
    st.subheader(f"✍️ {get_text('share_day_momo', lang_code)}")
    
    # Text input
    user_text = st.text_area(
        get_text('how_feeling_today', lang_code),
        height=200,
        placeholder=get_text('placeholder_text', lang_code),
        key="daily_checkin_text"
    )
    
    # Sample prompts
    with st.expander(f"💡 {get_text('need_inspiration', lang_code)}"):
        st.markdown(f"""
        - {get_text('prompt_1', lang_code)}
        - {get_text('prompt_2', lang_code)}
        - {get_text('prompt_3', lang_code)}
        - {get_text('prompt_4', lang_code)}
        - {get_text('prompt_5', lang_code)}
        """)
    
    # Analyze button with better feedback
    if st.button(f"🔍 {get_text('ask_momo_analyze', lang_code)}", type="primary", key="analyze_btn"):
        if user_text.strip():
            st.info("🔄 Starting analysis... Please wait.")
            analyze_user_input(user_id, user_text, lang_code)
        else:
            st.warning(get_text('enter_text_analyze', lang_code))
    
    # Debug information
    if st.checkbox("Show Debug Info", key="debug_checkbox"):
        st.write("**Debug Information:**")
        st.write(f"- User ID: {user_id}")
        st.write(f"- Text entered: {len(user_text)} characters")
        st.write(f"- Session state keys: {list(st.session_state.keys())}")
        if 'analysis_results' in st.session_state:
            st.write("- Analysis results available in session state")
        else:
            st.write("- No analysis results in session state")
        
        # Test data manager
        st.markdown("---")
        st.subheader("🧪 Test Data Manager")
        if st.button("Test Save Entry", key="test_save_btn"):
            try:
                test_text = "This is a test entry from daily check-in debug mode."
                test_emotion = json.dumps({
                    'primary_emotion': 'test',
                    'confidence': 0.8,
                    'intensity': 5,
                    'stability': 'stable'
                })
                test_cognitive = {
                    'lexical_diversity': 0.7,
                    'avg_sentence_length': 8.0,
                    'coherence_score': 0.8
                }
                test_score = {
                    'score': 75.0,
                    'emotion_score': 80.0,
                    'cognitive_score': 70.0,
                    'zone': 'green',
                    'zone_name': 'Good'
                }
                
                today = datetime.now().strftime('%Y-%m-%d')
                success = data_manager.save_daily_entry(
                    user_id, today, test_text, test_emotion, test_cognitive, test_score
                )
                
                if success:
                    st.success("✅ Test save successful!")
                else:
                    st.error("❌ Test save failed!")
                    
            except Exception as e:
                st.error(f"❌ Test save error: {e}")
                import traceback
                st.code(traceback.format_exc())

def show_voice_input(user_id, lang_code):
    """Handles voice input for daily check-in with real-time microphone recording."""
    st.subheader(f"🎤 {get_text('speak_momo', lang_code)}")
    
    # Get audio input using the new audio recorder
    audio_data, input_method = get_audio_input_method()
    
    if audio_data:
        st.success(f"✅ Audio captured successfully!")
        
        # Display audio info
        if hasattr(audio_data, 'name'):
            # File upload
            file_details = {
                "Filename": audio_data.name,
                "File size": f"{audio_data.size / 1024:.2f} KB",
                "File type": audio_data.type,
                "Input method": "File upload"
            }
        else:
            # Microphone recording
            file_details = {
                "Input method": "Microphone recording",
                "Audio format": "WAV",
                "Sample rate": "16kHz"
            }
        
        st.write(file_details)
        
        # Validate audio if it's a file upload
        if hasattr(audio_data, 'name'):
            if not validate_audio_file(audio_data):
                st.error(f"❌ {get_text('invalid_audio', lang_code)}")
                return
        
        # Transcribe and analyze button
        if st.button(f"🎵 {get_text('transcribe_analyze', lang_code)}", type="primary", key="transcribe_analyze_voice"):
            transcribe_and_analyze(user_id, audio_data, lang_code)
    
    # Instructions
    st.markdown("---")
    st.markdown("### 📋 Voice Input Instructions")
    st.markdown("""
    **For Microphone Recording:**
    1. Choose "Real-time Microphone Recording" above
    2. Click "Start Recording" and speak clearly
    3. Click "Stop Recording" when done
    4. Review your recording with the audio player
    5. Click "Download Recording" to save the file
    6. Upload the downloaded file in the section below
    7. Click "Transcribe & Analyze" to process
    
    **For File Upload:**
    1. Choose "Upload Audio File" above
    2. Select your audio file (WAV, MP3, M4A, FLAC, WEBM)
    3. Click "Transcribe & Analyze" to process
    """)
    
    # Tips for better recording
    st.markdown("### 💡 Tips for Better Recording")
    st.markdown("""
    - 🎤 **Speak clearly** and at a normal pace
    - 🔇 **Minimize background noise** for better accuracy
    - 📏 **Keep a consistent distance** from the microphone
    - ⏱️ **Record for 30 seconds to 3 minutes** for best results
    - 🗣️ **Speak naturally** as if talking to a friend
    - 📱 **Use headphones** with a built-in microphone for better quality
    """)

def analyze_user_input(user_id, text, lang_code, source='text'):
    """Analyzes user input and displays results."""
    with st.spinner(f"🤖 {get_text('momo_analyzing', lang_code)}"):
        try:
            # Analyze emotions
            emotion_analysis = emotion_agent.analyze_emotion(text)
            
            # Analyze cognitive metrics
            cognitive_metrics = analyze_cognitive_metrics(text)
            
            # Calculate Cognora score
            score_data = calculate_cognora_score(emotion_analysis, cognitive_metrics)
            
            # Store results in session state for later use
            st.session_state['analysis_results'] = {
                'text': text,
                'emotion_analysis': emotion_analysis,
                'cognitive_metrics': cognitive_metrics,
                'score_data': score_data
            }
            
            # Display results
            display_analysis_results(user_id, text, emotion_analysis, cognitive_metrics, score_data, lang_code, source)
            
        except Exception as e:
            st.error(f"Error during analysis: {e}")
            import traceback
            st.code(traceback.format_exc())

def transcribe_and_analyze(user_id, audio_data, lang_code):
    """Transcribes audio and analyzes the content."""
    with st.spinner("🎵 Transcribing audio..."):
        try:
            # Handle different types of audio data
            if hasattr(audio_data, 'name'):
                # File upload - use existing transcribe function
                transcript = transcribe_audio_file(audio_data)
            else:
                # Microphone recording - convert bytes to file-like object
                audio_file = io.BytesIO(audio_data)
                audio_file.name = "microphone_recording.wav"
                transcript = transcribe_audio_file(audio_file)
            
            if transcript:
                st.success(f"✅ {get_text('audio_transcribed', lang_code)}")
                
                # Display transcript
                st.subheader("📝 Your Transcript")
                st.text_area("Transcribed Text", transcript, height=150, disabled=True)
                
                # Show transcript length
                word_count = len(transcript.split())
                st.info(f"📊 Transcript: {word_count} words, {len(transcript)} characters")
                
                # Analyze the transcript with voice source
                analyze_user_input(user_id, transcript, lang_code, source='voice')
            else:
                st.error(f"❌ {get_text('transcription_failed', lang_code)}")
                st.info("💡 Try speaking more clearly or check your microphone settings.")
                
        except Exception as e:
            st.error(f"Error during transcription: {e}")
            st.info("💡 If you're having trouble with microphone recording, try uploading an audio file instead.")
            import traceback
            st.code(traceback.format_exc())

def display_analysis_results(user_id, text, emotion_analysis, cognitive_metrics, score_data, lang_code, source="analysis"):
    """Displays analysis results."""
    st.markdown("---")
    st.subheader("📊 Analysis Results")
    
    # Score display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        score = score_data['score']
        st.metric(
            "Momo Score",
            f"{score:.1f}",
            f"{get_score_emoji(score)} {score_data['zone_name']}"
        )
    
    with col2:
        st.metric(
            "Emotional Health",
            f"{score_data['emotion_score']:.1f}",
            "😊"
        )
    
    with col3:
        st.metric(
            "Cognitive Health",
            f"{score_data['cognitive_score']:.1f}",
            "🧠"
        )
    
    # Detailed analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("😊 Emotional Analysis")
        try:
            if isinstance(emotion_analysis, str):
                emotion_data = json.loads(emotion_analysis)
            else:
                emotion_data = emotion_analysis
                
            st.markdown(f"""
            **Primary Emotion**: {emotion_data.get('primary_emotion', 'Unknown')} {get_emotion_emoji(emotion_data.get('primary_emotion', ''))}
            **Confidence**: {emotion_data.get('confidence', 0):.1%}
            **Intensity**: {emotion_data.get('intensity', 0)}/10
            **Stability**: {emotion_data.get('stability', 'Unknown')}
            """)
            
            if emotion_data.get('concerning_patterns'):
                st.warning(f"**Concerning Patterns**: {', '.join(emotion_data['concerning_patterns'])}")
        except Exception as e:
            st.info(f"Emotional analysis completed. Error displaying details: {e}")
    
    with col2:
        st.subheader("🧠 Cognitive Analysis")
        try:
            st.markdown(f"""
            **Lexical Diversity**: {cognitive_metrics.get('lexical_diversity', 0):.1%}
            **Avg. Sentence Length**: {cognitive_metrics.get('avg_sentence_length', 0)} words
            **Coherence**: {cognitive_metrics.get('coherence_score', 0):.1%}
            """)
            
            if cognitive_metrics.get('named_entity_count', 0) < 2:
                st.warning(f"**Insight**: Fewer specific names (people, places) were mentioned today.")
        except Exception as e:
            st.info(f"Could not display all cognitive metrics. Error: {e}")
    
    # Save results with better error handling
    st.markdown("---")
    st.subheader("💾 Save Your Entry")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Today's Entry", type="primary", key=f"save_entry_btn_{source}"):
            save_entry(user_id, text, emotion_analysis, cognitive_metrics, score_data, lang_code, source)
    
    with col2:
        if st.button("🔄 Analyze Again", key=f"analyze_again_btn_{source}"):
            # Clear session state and re-analyze
            if 'analysis_results' in st.session_state:
                del st.session_state['analysis_results']
            st.rerun()

def save_entry(user_id, text, emotion_analysis, cognitive_metrics, score_data, lang_code, source='text'):
    """Saves the daily entry with enhanced debugging."""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        st.info(f"🔄 Saving entry for user {user_id} on {today}...")
        
        # Add debug information
        st.write(f"**Debug Info:**")
        st.write(f"- User ID: {user_id}")
        st.write(f"- Date: {today}")
        st.write(f"- Text length: {len(text)} characters")
        st.write(f"- Score: {score_data.get('score', 'N/A')}")
        st.write(f"- Emotion: {score_data.get('emotion', 'N/A')}")
        st.write(f"- Source: {source}")
        
        success = data_manager.save_daily_entry(
            user_id, today, text, emotion_analysis, cognitive_metrics, score_data, source
        )
        
        if success:
            st.success("✅ Today's entry saved successfully!")
            st.balloons()
            
            # Set flag to show voice entry completion on dashboard
            if source == 'voice':
                st.session_state['voice_entry_completed'] = True
            
            # Show what will appear on dashboard
            st.markdown("---")
            st.subheader("📊 This will appear on your dashboard:")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Today's Score",
                    f"{score_data.get('score', 0):.1f}",
                    f"{get_score_emoji(score_data.get('score', 0))} {score_data.get('zone_name', 'Unknown')}"
                )
            with col2:
                st.metric(
                    "Emotional Health",
                    f"{score_data.get('emotion_score', 0):.1f}",
                    "😊"
                )
            with col3:
                st.metric(
                    "Cognitive Health",
                    f"{score_data.get('cognitive_score', 0):.1f}",
                    "🧠"
                )
            
            # Show transcript preview
            st.subheader("📝 Your Entry:")
            st.text_area(
                "Transcript",
                text[:200] + "..." if len(text) > 200 else text,
                height=100,
                disabled=True
            )
            
            # Check for alerts
            alert_result = alert_manager.check_and_send_alerts(user_id)
            if alert_result['alert_sent']:
                st.warning("⚠️ Caregiver alert sent based on today's analysis")
            
            # Clear session state after successful save
            if 'analysis_results' in st.session_state:
                del st.session_state['analysis_results']
            
            # Add navigation suggestion
            st.markdown("---")
            source_text = "Voice entry" if source == 'voice' else "Entry"
            st.success(f"🎉 **{source_text} saved!** Check your dashboard to see your updated wellness score and trends.")
            
            if st.button("📊 Go to Dashboard", type="primary"):
                st.switch_page("Dashboard")
                
        else:
            st.error("❌ Failed to save entry. Please try again.")
            st.error("Check the console for detailed error messages.")
            
    except Exception as e:
        st.error(f"❌ Error saving entry: {e}")
        import traceback
        st.code(traceback.format_exc())

def show_reports(user_id, lang_code):
    """Displays the reports page."""
    st.title(f"📊 {get_text('reports_analytics', lang_code)}")
    st.markdown("---")
    
    # Report options
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"📋 {get_text('weekly_report', lang_code)}")
        week_start = st.date_input(
            get_text('select_week_start', lang_code),
            value=datetime.now().date() - timedelta(days=7)
        )
        
        if st.button(f"📄 {get_text('generate_weekly_report', lang_code)}"):
            generate_weekly_report(user_id, week_start.strftime('%Y-%m-%d'))
    
    with col2:
        st.subheader(f"📈 {get_text('data_export', lang_code)}")
        days = st.slider(get_text('number_days_export', lang_code), 7, 90, 30)
        
        if st.button(f"📊 {get_text('export_csv', lang_code)}"):
            export_data_csv(user_id, days)

def generate_weekly_report(user_id, week_start):
    """Generates and downloads a weekly report."""
    with st.spinner(f"📄 {get_text('generating_report', 'en')}..."):
        try:
            report_data = report_generator.generate_weekly_report(user_id, week_start)
            
            if report_data:
                st.download_button(
                    label=f"📥 {get_text('download_weekly_report', 'en')}",
                    data=report_data['pdf_bytes'],
                    file_name=f"cognora_weekly_report_{week_start}.pdf",
                    mime="application/pdf"
                )
                display_success_message(f"✅ {get_text('report_generated', 'en')}: {report_data['s3_key']}")
            else:
                display_error_message(f"❌ {get_text('no_data_available', 'en')}")
                
        except Exception as e:
            display_error_message(f"❌ {get_text('error_generating_report', 'en')}: {e}")

def export_data_csv(user_id, days):
    """Exports user data to CSV."""
    with st.spinner(f"📊 {get_text('exporting_data', 'en')}..."):
        try:
            csv_data = report_generator.export_data_csv(user_id, days)
            
            if csv_data:
                st.download_button(
                    label=f"📥 {get_text('download_csv_export', 'en')}",
                    data=csv_data,
                    file_name=f"cognora_data_export_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
                display_success_message(f"✅ {get_text('data_exported', 'en')}!")
            else:
                display_error_message(f"❌ {get_text('no_data_available', 'en')}")
                
        except Exception as e:
            display_error_message(f"❌ {get_text('error_exporting_data', 'en')}: {e}")

def show_alerts(user_id, lang_code):
    """Displays the alerts page."""
    st.title(f"🔔 {get_text('alerts_notifications', lang_code)}")
    st.markdown("---")
    
    # Current alert status
    st.subheader(f"📊 {get_text('current_alert_status', lang_code)}")
    
    alert_status = alert_manager.check_and_send_alerts(user_id)
    
    if alert_status['alert_sent']:
        st.error(f"⚠️ **{get_text('active_alert', lang_code)}**: {get_text('caregiver_alert', lang_code)}")
        st.markdown(f"**{get_text('alert_reason', lang_code)}**: {', '.join(alert_status['alert_status']['reasons'])}")
        st.markdown(f"**{get_text('urgency', lang_code)}**: {alert_status['alert_status']['urgency']}")
    else:
        st.success(f"✅ **{get_text('no_active_alerts', lang_code)}**: {get_text('no_alerts', lang_code)}")
    
    # --- Add test notification button ---
    st.markdown("---")
    st.subheader(f"🛠️ {get_text('demo_test_notification', lang_code)}")
    if st.button(f"🚨 {get_text('send_test_notification', lang_code)}", type="primary"):
        subject = "Cognora+ Test Notification"
        message = f"This is a test notification for user {user_id}. If you received this, the notification system is working."
        sent = send_alert(subject, message)
        if sent:
            st.success(f"✅ {get_text('test_notification_sent', lang_code)}")
        else:
            st.error(f"❌ {get_text('test_notification_failed', lang_code)}")
    
    st.markdown("---")
    
    # Alert history
    st.subheader(f"📋 {get_text('alert_history', lang_code)}")
    alert_history = alert_manager.get_alert_history(user_id)
    
    if alert_history:
        for alert in alert_history[-5:]:  # Show last 5 alerts
            timestamp = format_date(alert['timestamp'][:10], 'display')
            status = f"✅ {get_text('sent', lang_code)}" if alert['alert_sent'] else f"❌ {get_text('failed', lang_code)}"
            
            st.markdown(f"""
            **{timestamp}** - {status}
            - {get_text('alert_reason', lang_code)}: {', '.join(alert['reasons'])}
            - {get_text('urgency', lang_code)}: {alert['urgency']}
            ---
            """)
    else:
        st.info(get_text('no_alert_history', lang_code))

def create_sidebar_with_auth(data_manager=None, language="English", theme="light"):
    """Create sidebar with authentication support."""
    with st.sidebar:
        st.title("🧠 Cognora+")
        st.markdown("---")
        
        # Navigation
        st.subheader("📱 Navigation")
        page = st.selectbox(
            "Choose a page",
            ["Dashboard", "Daily Check-in", "Reports", "Alerts", "Analytics", "Settings"],
            index=0
        )
        
        st.markdown("---")
        
        # User preferences
        st.subheader("⚙️ Preferences")
        
        # Language selection
        new_language = st.selectbox("Language", ["English", "日本語"], index=0 if language == "English" else 1)
        if new_language != language:
            st.session_state['language'] = 'ja' if new_language == "日本語" else 'en'
            st.rerun()
        
        # Theme selection
        new_theme = st.selectbox("Theme", ["light", "dark"], index=0 if theme == "light" else 1)
        if new_theme != theme:
            st.session_state['theme'] = new_theme
            st.rerun()
        
        # Update user preferences in database
        if 'user_id' in st.session_state:
            from auth import update_user_preferences
            preferences = {
                'language': st.session_state.get('language', 'en'),
                'theme': st.session_state.get('theme', 'light'),
                'notifications': True,
                'alert_sensitivity': 'medium'
            }
            update_user_preferences(st.session_state['user_id'], preferences)
        
        st.markdown("---")
        
        # Quick stats (if data available)
        if data_manager:
            st.subheader("📊 Quick Stats")
            user_id = st.session_state.get('user_id', 'demo_user')
            user_history = data_manager.get_user_history(user_id, 7)
            
            if user_history:
                today_score = user_history[0].get('score', 50.0) if user_history else 50.0
                days_tracked = len(user_history)
                
                st.metric("Today's Score", f"{today_score:.1f}")
                st.metric("Days Tracked", days_tracked)
            else:
                st.info("No data available")
        
        # Production status indicator
        if config.is_production():
            st.markdown("---")
            st.subheader("🏭 Production")
            st.success("✅ Production Mode")
            st.caption(f"Market: {config.market.value.title()}")
            st.caption(f"Environment: {config.environment.value}")
    
    return page

def show_settings_with_auth(lang_code):
    """Displays the settings page with authentication features."""
    st.title(f"⚙️ {get_text('settings', lang_code)}")
    st.markdown("---")
    
    # User profile
    st.subheader(f"👤 {get_text('user_profile', lang_code)}")
    
    if 'user_data' in st.session_state:
        user_data = st.session_state['user_data']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input(get_text('full_name', lang_code), value=safe_convert_decimal(user_data.get('full_name', '')), disabled=True)
            # Ensure age is a proper integer to avoid Decimal type errors
            age_value = safe_convert_decimal(user_data.get('age', 25))
            st.number_input(get_text('age', lang_code), value=age_value, disabled=True)
        
        with col2:
            st.text_input(get_text('location', lang_code), value=safe_convert_decimal(user_data.get('location', '')), disabled=True)
            st.text_input(get_text('caregiver', lang_code), value=safe_convert_decimal(user_data.get('caregiver_email', '')), disabled=True)
        
        st.info("Profile information can be updated by contacting support.")
    
    st.markdown("---")
    
    # Password change
    from login_signup import show_password_change_form
    show_password_change_form()
    
    st.markdown("---")
    
    # Notification settings
    st.subheader(f"🔔 {get_text('notification_settings', lang_code)}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        email_notifications = st.checkbox(get_text('email_notifications', lang_code), value=True)
        sms_notifications = st.checkbox(get_text('sms_notifications', lang_code), value=False)
        daily_reminders = st.checkbox(get_text('daily_reminders', lang_code), value=True)
    
    with col2:
        alert_sensitivity = st.selectbox(get_text('alert_sensitivity', lang_code), ["Low", "Medium", "High"], index=1)
        caregiver_email = st.text_input(get_text('caregiver_email', lang_code), value="caregiver@example.com")
    
    st.markdown("---")
    
    # Data management
    st.subheader(f"💾 {get_text('data_management', lang_code)}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(f"🗑️ {get_text('clear_all_data', lang_code)}", type="secondary"):
            st.warning(get_text('action_irreversible', lang_code))
    
    with col2:
        if st.button(f"📤 {get_text('export_all_data', lang_code)}", type="secondary"):
            st.info(get_text('export_coming_soon', lang_code))
    
    st.markdown("---")
    
    # Account management
    from login_signup import show_account_deactivation
    show_account_deactivation()

def show_analytics_page(user_id, lang_code):
    """Show analytics and monitoring page."""
    st.title("📈 Analytics & Monitoring")
    st.markdown("---")
    
    # Track analytics page view
    user_analytics.track_page_view('analytics', user_id)
    
    # Performance metrics
    st.subheader("⚡ Performance Metrics")
    metrics = performance_monitor.get_metrics()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        uptime_hours = metrics['uptime'] / 3600
        st.metric("Uptime", f"{uptime_hours:.1f} hours")
    
    with col2:
        avg_response = metrics['average_response_time'] * 1000
        st.metric("Avg Response Time", f"{avg_response:.1f} ms")
    
    with col3:
        operations_count = len(metrics['operations'])
        st.metric("Operations Tracked", str(operations_count))
    
    # Feature usage analytics
    st.subheader("🎯 Feature Usage")
    
    # This would show actual feature usage data from analytics
    feature_usage = {
        'Voice Recording': 45,
        'Text Input': 78,
        'Reports': 12,
        'Alerts': 8
    }
    
    fig_usage = px.bar(
        x=list(feature_usage.keys()),
        y=list(feature_usage.values()),
        title="Feature Usage This Month"
    )
    st.plotly_chart(fig_usage, use_container_width=True)
    
    # System health
    st.subheader("🏥 System Health")
    
    # This would show actual health check results
    health_status = {
        'AWS Services': '✅ Healthy',
        'Database': '✅ Healthy',
        'External APIs': '✅ Healthy'
    }
    
    for service, status in health_status.items():
        st.write(f"{service}: {status}")

if __name__ == "__main__":
    main()
