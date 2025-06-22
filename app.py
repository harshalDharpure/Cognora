import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import tempfile
import os

# Import our modules
from utils import (
    setup_streamlit_config, create_sidebar, get_motivational_quote,
    format_date, format_score_display, get_emotion_emoji, create_sample_data,
    generate_demo_scores, display_loading_spinner, display_success_message,
    display_error_message, display_warning_message, validate_audio_file
)
from agents import EmotionAgent, MemoryAgent, AlertAgent
from scoring import calculate_cognora_score, get_score_color, get_score_emoji
from storage import data_manager, report_generator, alert_manager
from aws_services import transcribe_audio

# Initialize agents
emotion_agent = EmotionAgent()
memory_agent = MemoryAgent()
alert_agent = AlertAgent()

def main():
    """Main application function."""
    setup_streamlit_config()
    
    # Get sidebar navigation
    user_id, page, language, theme = create_sidebar()
    
    # Main content area
    if page == "Dashboard":
        show_dashboard(user_id)
    elif page == "Daily Check-in":
        show_daily_checkin(user_id)
    elif page == "Reports":
        show_reports(user_id)
    elif page == "Alerts":
        show_alerts(user_id)
    elif page == "Settings":
        show_settings()

def show_dashboard(user_id):
    """Displays the main dashboard."""
    st.title("🧠 Cognora+ Dashboard")
    st.markdown("---")
    
    # Get user data
    user_data = create_sample_data()
    demo_scores = generate_demo_scores(7)
    
    # Header with today's score
    col1, col2, col3 = st.columns(3)
    
    with col1:
        today_score = demo_scores[-1]['score']
        st.metric(
            "Today's Cognora Score",
            f"{today_score:.1f}",
            f"{get_score_emoji(today_score)} {demo_scores[-1]['zone'].title()}"
        )
    
    with col2:
        weekly_avg = sum(score['score'] for score in demo_scores) / len(demo_scores)
        st.metric(
            "Weekly Average",
            f"{weekly_avg:.1f}",
            "↗️ +2.3"
        )
    
    with col3:
        st.metric(
            "Days Tracked",
            "7",
            "↗️ +1"
        )
    
    st.markdown("---")
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 7-Day Score Trend")
        
        # Create trend chart
        df_trend = pd.DataFrame(demo_scores)
        df_trend['date'] = pd.to_datetime(df_trend['date'])
        
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
    
    with col2:
        st.subheader("😊 Emotion Timeline")
        
        # Create emotion chart
        emotion_counts = {}
        for score in demo_scores:
            emotion = score['emotion']
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        if emotion_counts:
            fig_emotion = px.pie(
                values=list(emotion_counts.values()),
                names=list(emotion_counts.keys()),
                title="Emotion Distribution"
            )
            fig_emotion.update_layout(height=300)
            st.plotly_chart(fig_emotion, use_container_width=True)
    
    st.markdown("---")
    
    # Recent activity and insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Latest Transcript")
        latest_transcript = user_data['sample_transcripts'][-1]
        st.text_area(
            "Yesterday's Entry",
            latest_transcript,
            height=150,
            disabled=True
        )
        
        # AI interpretation
        st.subheader("🤖 AI Interpretation")
        st.info("""
        **Emotional State**: Content and intellectually stimulated
        **Cognitive Health**: Good vocabulary diversity and coherent thoughts
        **Recommendation**: Continue engaging in intellectual activities
        """)
    
    with col2:
        st.subheader("💡 Motivational Quote")
        quote = get_motivational_quote()
        st.markdown(f"""
        > "{quote['quote']}"
        >
        > — {quote['author']}
        """)
        
        st.subheader("🎯 Wellness Tips")
        st.markdown("""
        - **Stay Social**: Connect with friends and family regularly
        - **Mental Exercise**: Read, solve puzzles, or learn something new
        - **Physical Activity**: Take daily walks or gentle exercises
        - **Mindfulness**: Practice meditation or deep breathing
        """)
    
    # Alert status
    st.markdown("---")
    st.subheader("🔔 Alert Status")
    
    alert_status = alert_manager.check_and_send_alerts(user_id)
    if alert_status['alert_sent']:
        st.error("⚠️ Caregiver alert sent - Low wellness indicators detected")
    else:
        st.success("✅ No alerts needed - Wellness indicators are stable")

def show_daily_checkin(user_id):
    """Displays the daily check-in page."""
    st.title("📝 Daily Wellness Check-in")
    st.markdown("---")
    
    # Input method selection
    input_method = st.radio(
        "Choose your input method:",
        ["Text Input", "Voice Recording"],
        horizontal=True
    )
    
    if input_method == "Text Input":
        show_text_input(user_id)
    else:
        show_voice_input(user_id)

def show_text_input(user_id):
    """Handles text input for daily check-in."""
    st.subheader("✍️ Share Your Day")
    
    # Text input
    user_text = st.text_area(
        "How are you feeling today? Share your thoughts, experiences, or anything on your mind...",
        height=200,
        placeholder="Today I felt... I did... I'm thinking about..."
    )
    
    # Sample prompts
    with st.expander("💡 Need inspiration? Try these prompts:"):
        st.markdown("""
        - What made you smile today?
        - How did you spend your time?
        - What's on your mind lately?
        - How are you feeling about your relationships?
        - What are you looking forward to?
        """)
    
    # Analyze button
    if st.button("🔍 Analyze My Wellness", type="primary"):
        if user_text.strip():
            analyze_user_input(user_id, user_text)
        else:
            st.warning("Please enter some text to analyze.")

def show_voice_input(user_id):
    """Handles voice input for daily check-in."""
    st.subheader("🎤 Voice Recording")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload an audio file (WAV, MP3, M4A, FLAC)",
        type=['wav', 'mp3', 'm4a', 'flac']
    )
    
    if uploaded_file is not None:
        # Validate file
        if not validate_audio_file(uploaded_file):
            st.error("Invalid audio file. Please check the file format and size.")
            return
        
        # Show file info
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Transcribe button
        if st.button("🎵 Transcribe & Analyze", type="primary"):
            transcribe_and_analyze(user_id, uploaded_file)

def analyze_user_input(user_id, text):
    """Analyzes user input and displays results."""
    with st.spinner("🤖 Analyzing your wellness..."):
        try:
            # Run analysis with agents
            emotion_analysis = emotion_agent.analyze_emotion(text)
            cognitive_analysis = memory_agent.analyze_cognitive_patterns(text)
            
            # Calculate Cognora score
            score_data = calculate_cognora_score(emotion_analysis, cognitive_analysis)
            
            # Display results
            display_analysis_results(user_id, text, emotion_analysis, cognitive_analysis, score_data)
            
        except Exception as e:
            st.error(f"Error during analysis: {e}")

def transcribe_and_analyze(user_id, audio_file):
    """Transcribes audio and analyzes the content."""
    with st.spinner("🎵 Transcribing audio..."):
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                tmp_file.write(audio_file.read())
                tmp_file_path = tmp_file.name
            
            # Transcribe
            job_name = f"cognora_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            transcript = transcribe_audio(tmp_file_path, job_name)
            
            # Clean up temp file
            os.unlink(tmp_file_path)
            
            if transcript and transcript != "Transcription failed.":
                st.success("✅ Audio transcribed successfully!")
                st.text_area("Transcribed Text", transcript, height=100, disabled=True)
                
                # Analyze the transcript
                analyze_user_input(user_id, transcript)
            else:
                st.error("❌ Transcription failed. Please try again or use text input.")
                
        except Exception as e:
            st.error(f"Error during transcription: {e}")

def display_analysis_results(user_id, text, emotion_analysis, cognitive_analysis, score_data):
    """Displays analysis results."""
    st.markdown("---")
    st.subheader("📊 Analysis Results")
    
    # Score display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        score = score_data['score']
        st.metric(
            "Cognora Score",
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
            emotion_data = json.loads(emotion_analysis)
            st.markdown(f"""
            **Primary Emotion**: {emotion_data.get('primary_emotion', 'Unknown')} {get_emotion_emoji(emotion_data.get('primary_emotion', ''))}
            **Confidence**: {emotion_data.get('confidence', 0):.1%}
            **Intensity**: {emotion_data.get('intensity', 0)}/10
            **Stability**: {emotion_data.get('stability', 'Unknown')}
            """)
            
            if emotion_data.get('concerning_patterns'):
                st.warning(f"**Concerning Patterns**: {', '.join(emotion_data['concerning_patterns'])}")
        except:
            st.info("Emotional analysis completed")
    
    with col2:
        st.subheader("🧠 Cognitive Analysis")
        try:
            cognitive_data = json.loads(cognitive_analysis)
            st.markdown(f"""
            **Lexical Diversity**: {cognitive_data.get('lexical_diversity', 0):.1%}
            **Sentence Fluency**: {cognitive_data.get('sentence_fluency', 0):.1%}
            **Repetition Score**: {cognitive_data.get('repetition_score', 0):.1%}
            **Overall Health**: {cognitive_data.get('overall_cognitive_health', 'Unknown')}
            """)
            
            if cognitive_data.get('cognitive_concerns'):
                st.warning(f"**Cognitive Concerns**: {', '.join(cognitive_data['cognitive_concerns'])}")
        except:
            st.info("Cognitive analysis completed")
    
    # Save results
    if st.button("💾 Save Today's Entry", type="primary"):
        save_entry(user_id, text, emotion_analysis, cognitive_analysis, score_data)

def save_entry(user_id, text, emotion_analysis, cognitive_analysis, score_data):
    """Saves the daily entry."""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        success = data_manager.save_daily_entry(
            user_id, today, text, emotion_analysis, cognitive_analysis, score_data
        )
        
        if success:
            display_success_message("✅ Today's entry saved successfully!")
            
            # Check for alerts
            alert_result = alert_manager.check_and_send_alerts(user_id)
            if alert_result['alert_sent']:
                display_warning_message("⚠️ Caregiver alert sent based on today's analysis")
        else:
            display_error_message("❌ Failed to save entry. Please try again.")
            
    except Exception as e:
        display_error_message(f"❌ Error saving entry: {e}")

def show_reports(user_id):
    """Displays the reports page."""
    st.title("📊 Reports & Analytics")
    st.markdown("---")
    
    # Report options
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Weekly Report")
        week_start = st.date_input(
            "Select week start date",
            value=datetime.now().date() - timedelta(days=7)
        )
        
        if st.button("📄 Generate Weekly Report"):
            generate_weekly_report(user_id, week_start.strftime('%Y-%m-%d'))
    
    with col2:
        st.subheader("📈 Data Export")
        days = st.slider("Number of days to export", 7, 90, 30)
        
        if st.button("📊 Export to CSV"):
            export_data_csv(user_id, days)

def generate_weekly_report(user_id, week_start):
    """Generates and downloads a weekly report."""
    with st.spinner("📄 Generating weekly report..."):
        try:
            report_bytes = report_generator.generate_weekly_report(user_id, week_start)
            
            if report_bytes:
                st.download_button(
                    label="📥 Download Weekly Report (PDF)",
                    data=report_bytes,
                    file_name=f"cognora_weekly_report_{week_start}.pdf",
                    mime="application/pdf"
                )
                display_success_message("✅ Weekly report generated successfully!")
            else:
                display_error_message("❌ No data available for the selected week.")
                
        except Exception as e:
            display_error_message(f"❌ Error generating report: {e}")

def export_data_csv(user_id, days):
    """Exports user data to CSV."""
    with st.spinner("📊 Exporting data..."):
        try:
            csv_data = report_generator.export_data_csv(user_id, days)
            
            if csv_data:
                st.download_button(
                    label="📥 Download CSV Export",
                    data=csv_data,
                    file_name=f"cognora_data_export_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
                display_success_message("✅ Data exported successfully!")
            else:
                display_error_message("❌ No data available for export.")
                
        except Exception as e:
            display_error_message(f"❌ Error exporting data: {e}")

def show_alerts(user_id):
    """Displays the alerts page."""
    st.title("🔔 Alerts & Notifications")
    st.markdown("---")
    
    # Current alert status
    st.subheader("📊 Current Alert Status")
    
    alert_status = alert_manager.check_and_send_alerts(user_id)
    
    if alert_status['alert_sent']:
        st.error("⚠️ **Active Alert**: Caregiver notification sent")
        st.markdown(f"**Reason**: {', '.join(alert_status['alert_status']['reasons'])}")
        st.markdown(f"**Urgency**: {alert_status['alert_status']['urgency']}")
    else:
        st.success("✅ **No Active Alerts**: Wellness indicators are stable")
    
    st.markdown("---")
    
    # Alert history
    st.subheader("📋 Alert History")
    alert_history = alert_manager.get_alert_history(user_id)
    
    if alert_history:
        for alert in alert_history[-5:]:  # Show last 5 alerts
            timestamp = format_date(alert['timestamp'][:10], 'display')
            status = "✅ Sent" if alert['alert_sent'] else "❌ Failed"
            
            st.markdown(f"""
            **{timestamp}** - {status}
            - Reasons: {', '.join(alert['reasons'])}
            - Urgency: {alert['urgency']}
            ---
            """)
    else:
        st.info("No alert history available.")

def show_settings():
    """Displays the settings page."""
    st.title("⚙️ Settings")
    st.markdown("---")
    
    # User profile
    st.subheader("👤 User Profile")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Full Name", value="Sarah Johnson")
        st.number_input("Age", value=72, min_value=18, max_value=120)
    
    with col2:
        st.text_input("Location", value="San Francisco, CA")
        st.text_input("Caregiver", value="Dr. Michael Chen")
    
    st.markdown("---")
    
    # Notification settings
    st.subheader("🔔 Notification Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Email notifications", value=True)
        st.checkbox("SMS notifications", value=False)
        st.checkbox("Daily reminders", value=True)
    
    with col2:
        st.selectbox("Alert sensitivity", ["Low", "Medium", "High"], index=1)
        st.text_input("Caregiver email", value="caregiver@example.com")
    
    st.markdown("---")
    
    # Data management
    st.subheader("💾 Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear All Data", type="secondary"):
            st.warning("This action cannot be undone!")
    
    with col2:
        if st.button("📤 Export All Data", type="secondary"):
            st.info("Export functionality coming soon!")

if __name__ == "__main__":
    main()
