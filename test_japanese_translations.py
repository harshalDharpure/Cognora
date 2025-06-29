#!/usr/bin/env python3
"""
Test script to verify Japanese translations for Reports, Alerts, and Settings pages.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import get_text

def test_japanese_translations():
    """Test Japanese translations for key pages."""
    print("=== Testing Japanese Translations ===")
    
    # Test Reports page translations
    print("\n--- Reports Page ---")
    reports_keys = [
        'reports_analytics',
        'weekly_report', 
        'data_export',
        'select_week_start',
        'generate_weekly_report',
        'number_days_export',
        'export_csv'
    ]
    
    for key in reports_keys:
        en_text = get_text(key, 'en')
        ja_text = get_text(key, 'ja')
        print(f"{key}:")
        print(f"  EN: {en_text}")
        print(f"  JA: {ja_text}")
    
    # Test Alerts page translations
    print("\n--- Alerts Page ---")
    alerts_keys = [
        'alerts_notifications',
        'current_alert_status',
        'active_alert',
        'no_active_alerts',
        'alert_reason',
        'urgency',
        'alert_history',
        'sent',
        'failed',
        'no_alert_history',
        'demo_test_notification',
        'send_test_notification',
        'test_notification_sent',
        'test_notification_failed'
    ]
    
    for key in alerts_keys:
        en_text = get_text(key, 'en')
        ja_text = get_text(key, 'ja')
        print(f"{key}:")
        print(f"  EN: {en_text}")
        print(f"  JA: {ja_text}")
    
    # Test Settings page translations
    print("\n--- Settings Page ---")
    settings_keys = [
        'settings',
        'user_profile',
        'full_name',
        'age',
        'location',
        'caregiver',
        'notification_settings',
        'email_notifications',
        'sms_notifications',
        'daily_reminders',
        'alert_sensitivity',
        'caregiver_email',
        'data_management',
        'clear_all_data',
        'export_all_data',
        'action_irreversible',
        'export_coming_soon'
    ]
    
    for key in settings_keys:
        en_text = get_text(key, 'en')
        ja_text = get_text(key, 'ja')
        print(f"{key}:")
        print(f"  EN: {en_text}")
        print(f"  JA: {ja_text}")
    
    # Test Dashboard translations
    print("\n--- Dashboard Page ---")
    dashboard_keys = [
        'voice_entry_completed',
        'wellness_score_updated',
        'no_real_data_available',
        'showing_real_data',
        'entries',
        'voice',
        'text',
        'latest_text_entry',
        'latest_voice_entry',
        'no_text_entries',
        'no_voice_entries',
        'no_transcript_available',
        'unknown_date',
        'refresh_dashboard_data'
    ]
    
    for key in dashboard_keys:
        en_text = get_text(key, 'en')
        ja_text = get_text(key, 'ja')
        print(f"{key}:")
        print(f"  EN: {en_text}")
        print(f"  JA: {ja_text}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_japanese_translations() 