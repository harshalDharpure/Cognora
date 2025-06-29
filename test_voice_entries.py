#!/usr/bin/env python3
"""
Test script to verify voice entries are being saved and retrieved correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from storage import DataManager
from aws_services import get_user_data, save_to_dynamodb
from datetime import datetime

def test_voice_entries():
    """Test voice entry saving and retrieval."""
    print("=== Testing Voice Entries ===")
    
    # Test user ID
    test_user_id = "test_user_123"
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Test data
    test_transcript = "This is a test voice entry for Cognora+"
    test_emotion = "happy"
    test_score = 85.0
    test_feedback = "Positive test entry"
    test_cognitive_metrics = {
        "vocabulary_richness": "0.8",
        "sentence_complexity": "0.7",
        "emotional_expression": "0.9"
    }
    
    print(f"Testing with user: {test_user_id}")
    print(f"Date: {today}")
    print(f"Source: voice")
    
    # Test 1: Save a voice entry
    print("\n--- Test 1: Saving Voice Entry ---")
    success = save_to_dynamodb(
        user_id=test_user_id,
        date=today,
        transcript=test_transcript,
        emotion=test_emotion,
        score=test_score,
        feedback=test_feedback,
        cognitive_metrics=test_cognitive_metrics,
        source='voice'
    )
    
    if success:
        print("✅ Voice entry saved successfully")
    else:
        print("❌ Failed to save voice entry")
        return
    
    # Test 2: Save a text entry for comparison
    print("\n--- Test 2: Saving Text Entry ---")
    text_success = save_to_dynamodb(
        user_id=test_user_id,
        date=today,
        transcript="This is a test text entry for Cognora+",
        emotion="neutral",
        score=75.0,
        feedback="Text test entry",
        cognitive_metrics=test_cognitive_metrics,
        source='text'
    )
    
    if text_success:
        print("✅ Text entry saved successfully")
    else:
        print("❌ Failed to save text entry")
    
    # Test 3: Retrieve and verify data
    print("\n--- Test 3: Retrieving Data ---")
    retrieved_data = get_user_data(test_user_id)
    
    if retrieved_data:
        print(f"✅ Retrieved {len(retrieved_data)} entries")
        
        # Find voice and text entries
        voice_entries = [entry for entry in retrieved_data if entry.get('source') == 'voice']
        text_entries = [entry for entry in retrieved_data if entry.get('source') == 'text']
        
        print(f"Voice entries found: {len(voice_entries)}")
        print(f"Text entries found: {len(text_entries)}")
        
        # Show details of each entry
        for i, entry in enumerate(retrieved_data):
            print(f"\nEntry {i+1}:")
            print(f"  Date: {entry.get('date', 'N/A')}")
            print(f"  Source: {entry.get('source', 'N/A')}")
            print(f"  Score: {entry.get('score', 'N/A')}")
            print(f"  Emotion: {entry.get('emotion', 'N/A')}")
            print(f"  Transcript: {entry.get('transcript', 'N/A')[:50]}...")
        
        # Test DataManager
        print("\n--- Test 4: Testing DataManager ---")
        data_manager = DataManager()
        history = data_manager.get_user_history(test_user_id, days=30)
        
        if history:
            print(f"✅ DataManager retrieved {len(history)} entries")
            
            # Find latest entries by source
            latest_voice = None
            latest_text = None
            
            sorted_history = sorted(history, key=lambda x: x.get('date', ''), reverse=True)
            
            for entry in sorted_history:
                source = entry.get('source', 'text')
                if source == 'voice' and latest_voice is None:
                    latest_voice = entry
                elif source == 'text' and latest_text is None:
                    latest_text = entry
                
                if latest_voice and latest_text:
                    break
            
            print(f"Latest voice entry: {latest_voice.get('date') if latest_voice else 'None'}")
            print(f"Latest text entry: {latest_text.get('date') if latest_text else 'None'}")
            
        else:
            print("❌ DataManager returned no data")
    
    else:
        print("❌ No data retrieved")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_voice_entries() 