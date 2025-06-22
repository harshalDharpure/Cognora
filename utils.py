import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import streamlit as st

# Internationalization support
TRANSLATIONS = {
    'en': {
        'welcome': 'Welcome to Cognora+',
        'daily_checkin': 'Daily Wellness Check-in',
        'voice_input': 'Voice Input',
        'text_input': 'Text Input',
        'analyze': 'Analyze',
        'score': 'Cognora Score',
        'dashboard': 'Dashboard',
        'reports': 'Reports',
        'alerts': 'Alerts',
        'settings': 'Settings'
    },
    'ja': {
        'welcome': 'Cognora+へようこそ',
        'daily_checkin': '日次健康チェックイン',
        'voice_input': '音声入力',
        'text_input': 'テキスト入力',
        'analyze': '分析',
        'score': 'Cognoraスコア',
        'dashboard': 'ダッシュボード',
        'reports': 'レポート',
        'alerts': 'アラート',
        'settings': '設定'
    }
}

def get_text(key: str, lang: str = 'en') -> str:
    """
    Gets translated text for the given key and language.
    
    Args:
        key: Text key
        lang: Language code ('en' or 'ja')
    
    Returns:
        Translated text
    """
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

def get_motivational_quote() -> Dict[str, str]:
    """
    Fetches a motivational quote from ZenQuotes API.
    
    Returns:
        Dictionary with quote and author
    """
    try:
        response = requests.get('https://zenquotes.io/api/random')
        if response.status_code == 200:
            data = response.json()[0]
            return {
                'quote': data['q'],
                'author': data['a']
            }
    except Exception as e:
        print(f"Error fetching quote: {e}")
    
    # Fallback quotes
    fallback_quotes = [
        {"quote": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
        {"quote": "Health is the greatest gift, contentment the greatest wealth, faithfulness the best relationship.", "author": "Buddha"},
        {"quote": "Every day is a new beginning. Take a deep breath and start again.", "author": "Anonymous"}
    ]
    
    import random
    return random.choice(fallback_quotes)

def format_date(date_str: str, format_type: str = 'display') -> str:
    """
    Formats date strings for different purposes.
    
    Args:
        date_str: Date string (YYYY-MM-DD)
        format_type: 'display', 'short', or 'full'
    
    Returns:
        Formatted date string
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        
        if format_type == 'display':
            return date_obj.strftime('%B %d, %Y')
        elif format_type == 'short':
            return date_obj.strftime('%b %d')
        elif format_type == 'full':
            return date_obj.strftime('%A, %B %d, %Y')
        else:
            return date_str
    except:
        return date_str

def get_week_dates(date_str: str) -> Dict[str, str]:
    """
    Gets the start and end dates of the week containing the given date.
    
    Args:
        date_str: Date string (YYYY-MM-DD)
    
    Returns:
        Dictionary with 'start' and 'end' dates
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        start_of_week = date_obj - timedelta(days=date_obj.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        return {
            'start': start_of_week.strftime('%Y-%m-%d'),
            'end': end_of_week.strftime('%Y-%m-%d')
        }
    except:
        return {'start': date_str, 'end': date_str}

def validate_audio_file(audio_file) -> bool:
    """
    Validates uploaded audio file.
    
    Args:
        audio_file: Streamlit uploaded file
    
    Returns:
        True if valid, False otherwise
    """
    if audio_file is None:
        return False
    
    # Check file extension
    allowed_extensions = ['.wav', '.mp3', '.m4a', '.flac']
    file_extension = audio_file.name.lower()
    
    if not any(file_extension.endswith(ext) for ext in allowed_extensions):
        return False
    
    # Check file size (max 10MB)
    if audio_file.size > 10 * 1024 * 1024:
        return False
    
    return True

def create_sample_data() -> Dict[str, Any]:
    """
    Creates sample data for demonstration purposes.
    
    Returns:
        Sample user data
    """
    return {
        'user_id': 'demo_user_001',
        'name': 'Sarah Johnson',
        'age': 72,
        'location': 'San Francisco, CA',
        'caregiver': 'Dr. Michael Chen',
        'sample_transcripts': [
            "Today was wonderful! I went for a walk in the park and met some lovely people. The weather was perfect and I felt so energized. I'm looking forward to tomorrow.",
            "I'm feeling a bit lonely today. My children are busy with work and I haven't heard from them in a few days. I miss our weekly calls.",
            "I had a great conversation with my neighbor this morning. We talked about gardening and she gave me some tips for my roses. I feel quite happy and content.",
            "I'm a bit confused about my medication schedule today. I think I might have missed a dose yesterday. I should call my doctor to clarify.",
            "I spent the afternoon reading a fascinating book about history. It's amazing how much there is to learn. I feel intellectually stimulated and grateful for my education."
        ]
    }

def generate_demo_scores(days: int = 7) -> list:
    """
    Generates demo Cognora scores for testing.
    
    Args:
        days: Number of days to generate
    
    Returns:
        List of demo scores
    """
    import random
    
    base_scores = [85, 78, 92, 65, 88, 75, 82]
    demo_scores = []
    
    for i in range(days):
        if i < len(base_scores):
            score = base_scores[i]
        else:
            score = random.randint(60, 95)
        
        demo_scores.append({
            'date': (datetime.now() - timedelta(days=days-i-1)).strftime('%Y-%m-%d'),
            'score': score,
            'emotion_score': score + random.randint(-10, 10),
            'cognitive_score': score + random.randint(-10, 10),
            'emotion': random.choice(['happy', 'calm', 'lonely', 'anxious', 'content']),
            'zone': 'green' if score >= 75 else 'yellow' if score >= 50 else 'red'
        })
    
    return demo_scores

def setup_streamlit_config():
    """
    Sets up Streamlit page configuration.
    """
    st.set_page_config(
        page_title="Cognora+ - AI Wellness Assistant",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def create_sidebar():
    """
    Creates the Streamlit sidebar with navigation and user info.
    """
    with st.sidebar:
        st.title("🧠 Cognora+")
        st.markdown("---")
        
        # User selection
        user_id = st.selectbox(
            "Select User",
            ["demo_user_001", "user_002", "user_003"],
            index=0
        )
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["Dashboard", "Daily Check-in", "Reports", "Alerts", "Settings"]
        )
        
        st.markdown("---")
        
        # Quick stats
        st.subheader("Quick Stats")
        st.metric("Today's Score", "82", "↗️ +5")
        st.metric("Weekly Avg", "78", "↗️ +3")
        
        st.markdown("---")
        
        # Settings
        st.subheader("Settings")
        language = st.selectbox("Language", ["English", "日本語"])
        theme = st.selectbox("Theme", ["Light", "Dark"])
        
        return user_id, page, language, theme

def display_loading_spinner(message: str = "Processing..."):
    """
    Displays a loading spinner with custom message.
    
    Args:
        message: Loading message to display
    """
    with st.spinner(message):
        import time
        time.sleep(0.5)  # Simulate processing

def display_success_message(message: str):
    """
    Displays a success message.
    
    Args:
        message: Success message to display
    """
    st.success(message)

def display_error_message(message: str):
    """
    Displays an error message.
    
    Args:
        message: Error message to display
    """
    st.error(message)

def display_warning_message(message: str):
    """
    Displays a warning message.
    
    Args:
        message: Warning message to display
    """
    st.warning(message)

def format_score_display(score: float) -> str:
    """
    Formats score for display with appropriate styling.
    
    Args:
        score: Cognora score (0-100)
    
    Returns:
        Formatted score string
    """
    if score >= 75:
        return f"🟢 {score:.1f}"
    elif score >= 50:
        return f"🟡 {score:.1f}"
    else:
        return f"🔴 {score:.1f}"

def get_emotion_emoji(emotion: str) -> str:
    """
    Returns an emoji for the given emotion.
    
    Args:
        emotion: Emotion string
    
    Returns:
        Emoji string
    """
    emotion_emojis = {
        'happy': '😊',
        'sad': '😢',
        'anxious': '😰',
        'lonely': '😔',
        'angry': '😠',
        'calm': '😌',
        'confused': '😕',
        'excited': '🤩',
        'content': '😌',
        'worried': '😟'
    }
    
    return emotion_emojis.get(emotion.lower(), '😐')
