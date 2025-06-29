<<<<<<< HEAD
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
        'settings': 'Settings',
        'momo_dashboard': "Momo's Dashboard",
        'daily_checkin_momo': 'Daily Check-in with Momo',
        'share_day_momo': 'Share Your Day with Momo',
        'speak_momo': 'Speak with Momo',
        'ask_momo_analyze': 'Ask Momo to Analyze My Wellness',
        'momo_analyzing': 'Momo is analyzing your wellness...',
        'momo_score': 'Momo Score',
        'today_momo_score': "Today's Momo Score",
        'weekly_average': 'Weekly Average',
        'days_tracked': 'Days Tracked',
        'score_trend': '7-Day Score Trend',
        'emotion_timeline': 'Emotion Timeline',
        'latest_transcript': 'Latest Transcript',
        'yesterday_entry': "Yesterday's Entry",
        'ai_interpretation': 'AI Interpretation',
        'motivational_quote': 'Motivational Quote',
        'wellness_tips': 'Wellness Tips',
        'alert_status': 'Alert Status',
        'reports_analytics': 'Reports & Analytics',
        'weekly_report': 'Weekly Report',
        'data_export': 'Data Export',
        'generate_weekly_report': 'Generate Weekly Report',
        'export_csv': 'Export to CSV',
        'alerts_notifications': 'Alerts & Notifications',
        'current_alert_status': 'Current Alert Status',
        'alert_history': 'Alert History',
        'user_profile': 'User Profile',
        'notification_settings': 'Notification Settings',
        'data_management': 'Data Management',
        'emotional_analysis': 'Emotional Analysis',
        'cognitive_analysis': 'Cognitive Analysis',
        'primary_emotion': 'Primary Emotion',
        'confidence': 'Confidence',
        'intensity': 'Intensity',
        'stability': 'Stability',
        'lexical_diversity': 'Lexical Diversity',
        'avg_sentence_length': 'Avg. Sentence Length',
        'coherence': 'Coherence',
        'save_entry': 'Save Today\'s Entry',
        'entry_saved': 'Today\'s entry saved successfully!',
        'alert_sent': 'Caregiver alert sent based on today\'s analysis',
        'no_alerts': 'No alerts needed - Wellness indicators are stable',
        'caregiver_alert': 'Caregiver alert sent - Low wellness indicators detected',
        'select_user': 'Select User',
        'navigation': 'Navigation',
        'quick_stats': 'Quick Stats',
        'language': 'Language',
        'theme': 'Theme',
        'processing': 'Processing...',
        'generating_report': 'Generating and uploading weekly report...',
        'report_generated': 'Report generated and uploaded to S3',
        'exporting_data': 'Exporting data...',
        'data_exported': 'Data exported successfully!',
        'no_data_available': 'No data available for the selected week.',
        'error_generating_report': 'Error generating report',
        'error_exporting_data': 'Error exporting data',
        'upload_audio': 'Upload an audio file (WAV, MP3, M4A, FLAC)',
        'transcribe_analyze': 'Transcribe & Analyze',
        'audio_transcribed': 'Audio transcribed successfully!',
        'transcription_failed': 'Transcription failed. Please try again or use text input.',
        'invalid_audio': 'Invalid audio file. Please check the file format and size.',
        'file_uploaded': 'File uploaded',
        'need_inspiration': 'Need inspiration? Try these prompts:',
        'prompt_1': 'What made you smile today?',
        'prompt_2': 'How did you spend your time?',
        'prompt_3': 'What\'s on your mind lately?',
        'prompt_4': 'How are you feeling about your relationships?',
        'prompt_5': 'What are you looking forward to?',
        'enter_text_analyze': 'Please enter some text to analyze.',
        'how_feeling_today': 'How are you feeling today? Share your thoughts, experiences, or anything on your mind...',
        'placeholder_text': 'Today I felt... I did... I\'m thinking about...',
        'choose_input_method': 'Choose your input method:',
        'download_weekly_report': 'Download Weekly Report (PDF)',
        'download_csv_export': 'Download CSV Export',
        'active_alert': 'Active Alert: Caregiver notification sent',
        'no_active_alerts': 'No Active Alerts: Wellness indicators are stable',
        'alert_reason': 'Reason',
        'urgency': 'Urgency',
        'sent': 'Sent',
        'failed': 'Failed',
        'no_alert_history': 'No alert history available.',
        'full_name': 'Full Name',
        'location': 'Location',
        'caregiver': 'Caregiver',
        'email_notifications': 'Email notifications',
        'sms_notifications': 'SMS notifications',
        'daily_reminders': 'Daily reminders',
        'alert_sensitivity': 'Alert sensitivity',
        'caregiver_email': 'Caregiver email',
        'clear_all_data': 'Clear All Data',
        'export_all_data': 'Export All Data',
        'action_irreversible': 'This action cannot be undone!',
        'export_coming_soon': 'Export functionality coming soon!',
        'insight_fewer_names': 'Insight: Fewer specific names (people, places) were mentioned today.',
        'concerning_patterns': 'Concerning Patterns',
        'stay_social': 'Stay Social: Connect with friends and family regularly',
        'mental_exercise': 'Mental Exercise: Read, solve puzzles, or learn something new',
        'physical_activity': 'Physical Activity: Take daily walks or gentle exercises',
        'mindfulness': 'Mindfulness: Practice meditation or deep breathing',
        'emotional_state': 'Emotional State',
        'cognitive_health': 'Cognitive Health',
        'recommendation': 'Recommendation',
        'content_stimulated': 'Content and intellectually stimulated',
        'good_vocabulary': 'Good vocabulary diversity and coherent thoughts',
        'continue_activities': 'Continue engaging in intellectual activities',
        'select_week_start': 'Select week start date',
        'number_days_export': 'Number of days to export',
        'age': 'Age',
        'demo_test_notification': 'Demo / Test Notification',
        'send_test_notification': 'Send Test Notification',
        'test_notification_sent': 'Test notification sent to caregiver email!',
        'test_notification_failed': 'Failed to send test notification.',
        'voice_entry_completed': 'Voice entry completed!',
        'wellness_score_updated': 'Your wellness score has been updated.',
        'no_real_data_available': 'No real data available. Showing demo data.',
        'showing_real_data': 'Showing real data from',
        'entries': 'entries',
        'voice': 'voice',
        'text': 'text',
        'latest_text_entry': 'Latest Text Entry',
        'latest_voice_entry': 'Latest Voice Entry',
        'no_text_entries': 'No text entries available',
        'no_voice_entries': 'No voice entries available',
        'no_transcript_available': 'No transcript available',
        'unknown_date': 'Unknown date',
        'refresh_dashboard_data': 'Refresh Dashboard Data',
        'welcome_cognora': 'Welcome to Cognora+',
        'login_to_account': 'Login to Your Account',
        'create_new_account': 'Create New Account',
        'enter_email': 'Enter your email',
        'enter_password': 'Enter your password',
        'login': 'Login',
        'forgot_password': 'Forgot Password?',
        'login_successful': 'Login successful!',
        'invalid_credentials': 'Invalid email or password',
        'enter_both_fields': 'Please enter both email and password',
        'password_reset_coming_soon': 'Password reset functionality coming soon!',
        'personal_information': 'Personal Information',
        'enter_full_name': 'Enter your full name',
        'enter_email_address': 'Enter your email address',
        'security': 'Security',
        'create_strong_password': 'Create a strong password',
        'confirm_password': 'Confirm your password',
        'additional_information': 'Additional Information (Optional)',
        'city_state_country': 'City, State/Country',
        'caregiver_email_optional': 'caregiver@example.com',
        'password_is_valid': 'Password is valid',
        'agree_terms': 'I agree to the Terms and Conditions and Privacy Policy',
        'create_account': 'Create Account',
        'fill_required_fields': 'Please fill in all required fields',
        'invalid_email_format': 'Please enter a valid email address',
        'passwords_not_match': 'Passwords do not match',
        'agree_terms_required': 'Please agree to the Terms and Conditions',
        'account_created_successfully': 'Account created successfully!',
        'login_with_email_password': 'You can now login with your email and password',
        'registration_failed': 'Registration failed',
        'logout': 'Logout',
        'logged_out_successfully': 'Logged out successfully!',
        'user_account_not_found': 'User account not found. Please login again.',
        'user_profile': 'User Profile',
        'last_login': 'Last Login',
        'change_password': 'Change Password',
        'current_password': 'Current Password',
        'new_password': 'New Password',
        'confirm_new_password': 'Confirm New Password',
        'password_changed_successfully': 'Password changed successfully!',
        'current_password_incorrect': 'Current password is incorrect',
        'password_change_failed': 'Password change failed',
        'account_management': 'Account Management',
        'deactivate_account': 'Deactivate Account',
        'account_deactivated_successfully': 'Account deactivated successfully',
        'failed_deactivate_account': 'Failed to deactivate account',
        'profile_updated_contact_support': 'Profile information can be updated by contacting support.',
        'choose_page': 'Choose a page',
        'preferences': 'Preferences',
        'today_score': 'Today\'s Score',
        'no_data_available': 'No data available'
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
        'settings': '設定',
        'momo_dashboard': 'もものダッシュボード',
        'daily_checkin_momo': 'ももとの日次チェックイン',
        'share_day_momo': 'ももと今日の出来事を共有',
        'speak_momo': 'ももと話す',
        'ask_momo_analyze': 'ももに健康状態を分析してもらう',
        'momo_analyzing': 'ももが健康状態を分析中...',
        'momo_score': 'ももスコア',
        'today_momo_score': '今日のももスコア',
        'weekly_average': '週間平均',
        'days_tracked': '記録日数',
        'score_trend': '7日間スコア推移',
        'emotion_timeline': '感情タイムライン',
        'latest_transcript': '最新の記録',
        'yesterday_entry': '昨日の記録',
        'ai_interpretation': 'AI解釈',
        'motivational_quote': '心に響く言葉',
        'wellness_tips': '健康のヒント',
        'alert_status': 'アラート状況',
        'reports_analytics': 'レポート・分析',
        'weekly_report': '週間レポート',
        'data_export': 'データエクスポート',
        'generate_weekly_report': '週間レポート生成',
        'export_csv': 'CSVエクスポート',
        'alerts_notifications': 'アラート・通知',
        'current_alert_status': '現在のアラート状況',
        'alert_history': 'アラート履歴',
        'user_profile': 'ユーザープロフィール',
        'notification_settings': '通知設定',
        'data_management': 'データ管理',
        'emotional_analysis': '感情分析',
        'cognitive_analysis': '認知分析',
        'primary_emotion': '主要感情',
        'confidence': '信頼度',
        'intensity': '強度',
        'stability': '安定性',
        'lexical_diversity': '語彙の多様性',
        'avg_sentence_length': '平均文長',
        'coherence': '一貫性',
        'save_entry': '今日の記録を保存',
        'entry_saved': '今日の記録が正常に保存されました！',
        'alert_sent': '今日の分析に基づいて介護者にアラートを送信しました',
        'no_alerts': 'アラートは不要です - 健康指標は安定しています',
        'caregiver_alert': '介護者アラート送信 - 低い健康指標を検出',
        'select_user': 'ユーザー選択',
        'navigation': 'ナビゲーション',
        'quick_stats': 'クイック統計',
        'language': '言語',
        'theme': 'テーマ',
        'processing': '処理中...',
        'generating_report': '週間レポートを生成・アップロード中...',
        'report_generated': 'レポートが生成され、S3にアップロードされました',
        'exporting_data': 'データをエクスポート中...',
        'data_exported': 'データが正常にエクスポートされました！',
        'no_data_available': '選択された週のデータがありません。',
        'error_generating_report': 'レポート生成エラー',
        'error_exporting_data': 'データエクスポートエラー',
        'upload_audio': '音声ファイルをアップロード（WAV、MP3、M4A、FLAC）',
        'transcribe_analyze': '文字起こし・分析',
        'audio_transcribed': '音声の文字起こしが完了しました！',
        'transcription_failed': '文字起こしに失敗しました。再試行するか、テキスト入力を使用してください。',
        'invalid_audio': '無効な音声ファイルです。ファイル形式とサイズを確認してください。',
        'file_uploaded': 'ファイルがアップロードされました',
        'need_inspiration': 'ヒントが必要ですか？以下のプロンプトを試してみてください：',
        'prompt_1': '今日笑顔になったことは？',
        'prompt_2': '今日はどのように過ごしましたか？',
        'prompt_3': '最近気になっていることは？',
        'prompt_4': '人間関係についてどう感じていますか？',
        'prompt_5': '楽しみにしていることは？',
        'enter_text_analyze': '分析するテキストを入力してください。',
        'how_feeling_today': '今日はどのように感じていますか？考えや経験、心に浮かんだことを共有してください...',
        'placeholder_text': '今日は...感じました。...しました。...について考えています...',
        'choose_input_method': '入力方法を選択してください：',
        'download_weekly_report': '週間レポートをダウンロード（PDF）',
        'download_csv_export': 'CSVエクスポートをダウンロード',
        'active_alert': 'アクティブアラート：介護者に通知を送信',
        'no_active_alerts': 'アクティブアラートなし：健康指標は安定しています',
        'alert_reason': '理由',
        'urgency': '緊急度',
        'sent': '送信済み',
        'failed': '失敗',
        'no_alert_history': 'アラート履歴がありません。',
        'full_name': '氏名',
        'location': '所在地',
        'caregiver': '介護者',
        'email_notifications': 'メール通知',
        'sms_notifications': 'SMS通知',
        'daily_reminders': '日次リマインダー',
        'alert_sensitivity': 'アラート感度',
        'caregiver_email': '介護者メール',
        'clear_all_data': '全データを削除',
        'export_all_data': '全データをエクスポート',
        'action_irreversible': 'この操作は取り消せません！',
        'export_coming_soon': 'エクスポート機能は近日公開予定です！',
        'insight_fewer_names': '洞察：具体的な名前（人、場所）の言及が少ない日でした。',
        'concerning_patterns': '懸念されるパターン',
        'stay_social': '社会的交流：友人や家族と定期的に連絡を取り合いましょう',
        'mental_exercise': '脳の運動：読書、パズル、新しいことを学びましょう',
        'physical_activity': '身体活動：毎日の散歩や軽い運動をしましょう',
        'mindfulness': 'マインドフルネス：瞑想や深呼吸を実践しましょう',
        'emotional_state': '感情状態',
        'cognitive_health': '認知健康',
        'recommendation': '推奨事項',
        'content_stimulated': '満足感があり、知的に刺激されています',
        'good_vocabulary': '語彙の多様性が良く、思考が一貫しています',
        'continue_activities': '知的活動を続けましょう',
        'select_week_start': '週の開始日を選択',
        'number_days_export': 'エクスポートする日数',
        'age': '年齢',
        'demo_test_notification': 'デモ / テスト通知',
        'send_test_notification': 'テスト通知を送信',
        'test_notification_sent': 'テスト通知が介護者のメールに送信されました！',
        'test_notification_failed': 'テスト通知の送信に失敗しました。',
        'voice_entry_completed': '音声入力が完了しました！',
        'wellness_score_updated': '健康スコアが更新されました。',
        'no_real_data_available': '実際のデータがありません。デモデータを表示しています。',
        'showing_real_data': '実際のデータを表示中：',
        'entries': 'エントリ',
        'voice': '音声',
        'text': 'テキスト',
        'latest_text_entry': '最新のテキスト入力',
        'latest_voice_entry': '最新の音声入力',
        'no_text_entries': 'テキスト入力がありません',
        'no_voice_entries': '音声入力がありません',
        'no_transcript_available': '記録がありません',
        'unknown_date': '日付不明',
        'refresh_dashboard_data': 'ダッシュボードデータを更新',
        'welcome_cognora': 'Cognora+へようこそ',
        'login_to_account': 'アカウントにログイン',
        'create_new_account': '新しいアカウントを作成',
        'enter_email': 'メールアドレスを入力',
        'enter_password': 'パスワードを入力',
        'login': 'ログイン',
        'forgot_password': 'パスワードを忘れた',
        'login_successful': 'ログインに成功しました！',
        'invalid_credentials': 'メールアドレスまたはパスワードが無効です',
        'enter_both_fields': 'メールアドレスとパスワードを両方入力してください',
        'password_reset_coming_soon': 'パスワードリセット機能は近日公開予定です！',
        'personal_information': '個人情報',
        'enter_full_name': '氏名を入力',
        'enter_email_address': 'メールアドレスを入力',
        'security': 'セキュリティ',
        'create_strong_password': '強力なパスワードを作成',
        'confirm_password': 'パスワードを確認',
        'additional_information': '追加情報（オプション）',
        'city_state_country': '都市、都道府県/国',
        'caregiver_email_optional': 'caregiver@example.com',
        'password_is_valid': 'パスワードが有効です',
        'agree_terms': '利用規約とプライバシーポリシーに同意する',
        'create_account': 'アカウントを作成',
        'fill_required_fields': '必須フィールドをすべて入力してください',
        'invalid_email_format': '有効なメールアドレスを入力してください',
        'passwords_not_match': 'パスワードが一致しません',
        'agree_terms_required': '利用規約に同意してください',
        'account_created_successfully': 'アカウントが正常に作成されました！',
        'login_with_email_password': 'メールとパスワードを使用してログインできます',
        'registration_failed': '登録に失敗しました',
        'logout': 'ログアウト',
        'logged_out_successfully': '正常にログアウトしました！',
        'user_account_not_found': 'ユーザーアカウントが見つかりません。再度ログインしてください。',
        'user_profile': 'ユーザープロフィール',
        'last_login': '最終ログイン',
        'change_password': 'パスワードを変更',
        'current_password': '現在のパスワード',
        'new_password': '新しいパスワード',
        'confirm_new_password': '新しいパスワードを確認',
        'password_changed_successfully': 'パスワードが正常に変更されました！',
        'current_password_incorrect': '現在のパスワードが無効です',
        'password_change_failed': 'パスワードの変更に失敗しました',
        'account_management': 'アカウント管理',
        'deactivate_account': 'アカウントを無効化',
        'account_deactivated_successfully': 'アカウントが正常に無効化されました',
        'failed_deactivate_account': 'アカウントの無効化に失敗しました',
        'profile_updated_contact_support': 'プロフィール情報はサポートによって更新できます。',
        'choose_page': 'ページを選択',
        'preferences': '設定',
        'today_score': '今日のスコア',
        'no_data_available': 'データがありません'
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

def create_sidebar(data_manager=None):
    """
    Creates the Streamlit sidebar with navigation and user info.
    
    Args:
        data_manager: Optional DataManager instance to get real user data
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
        
        # Quick stats - use real data if available
        st.subheader("Quick Stats")
        
        if data_manager:
            try:
                # Get real user data
                user_history = data_manager.get_user_history(user_id, 7)
                
                if user_history:
                    # Today's score (most recent entry)
                    today_score = user_history[0].get('score', 50.0) if user_history else 50.0
                    
                    # Weekly average
                    weekly_avg = sum(entry.get('score', 50.0) for entry in user_history) / len(user_history)
                    
                    # Calculate trend
                    if len(user_history) >= 2:
                        current_score = user_history[0].get('score', 50.0)
                        previous_score = user_history[1].get('score', 50.0)
                        trend = current_score - previous_score
                        trend_display = f"↗️ +{trend:.1f}" if trend > 0 else f"↘️ {trend:.1f}"
                    else:
                        trend_display = "↗️ +0.0"
                    
                    st.metric("Today's Score", f"{today_score:.1f}", trend_display)
                    st.metric("Weekly Avg", f"{weekly_avg:.1f}", "↗️ +0.0")
                else:
                    # Fallback to static data if no real data
                    st.metric("Today's Score", "82", "↗️ +5")
                    st.metric("Weekly Avg", "78", "↗️ +3")
                    
            except Exception as e:
                # Fallback to static data if error
                st.metric("Today's Score", "82", "↗️ +5")
                st.metric("Weekly Avg", "78", "↗️ +3")
        else:
            # Static data when no data manager provided
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
=======
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
>>>>>>> 23a3f924b5333426fb4b4fb6085453f9515378f8
