#!/usr/bin/env python3
"""
AWS Setup Test Script for Cognora+
This script helps diagnose AWS configuration and data storage issues.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment_variables():
    """Test if all required environment variables are set."""
    print("=== Environment Variables Test ===")
    
    required_vars = {
        "AWS_ACCESS_KEY_ID": "AWS Access Key ID",
        "AWS_SECRET_ACCESS_KEY": "AWS Secret Access Key", 
        "AWS_REGION_NAME": "AWS Region",
        "S3_BUCKET_NAME": "S3 Bucket Name",
        "DYNAMODB_TABLE_NAME": "DynamoDB Table Name"
    }
    
    missing_vars = []
    
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if value:
            print(f"✅ {description}: {value[:10]}..." if len(value) > 10 else f"✅ {description}: {value}")
        else:
            print(f"❌ {description}: NOT SET")
            missing_vars.append(var_name)
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file and ensure all required variables are set.")
        return False
    else:
        print("\n✅ All required environment variables are set!")
        return True

def test_aws_imports():
    """Test if AWS modules can be imported."""
    print("\n=== AWS Module Import Test ===")
    
    try:
        import boto3
        print("✅ boto3 imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import boto3: {e}")
        return False
    
    try:
        from aws_services import test_aws_connection
        print("✅ aws_services module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import aws_services: {e}")
        return False
    
    return True

def test_aws_connection():
    """Test AWS connection and permissions."""
    print("\n=== AWS Connection Test ===")
    
    try:
        from aws_services import test_aws_connection
        test_aws_connection()
        return True
    except Exception as e:
        print(f"❌ AWS connection test failed: {e}")
        return False

def test_data_storage():
    """Test data storage functionality."""
    print("\n=== Data Storage Test ===")
    
    try:
        from storage import DataManager
        from aws_services import store_data_in_s3, save_to_dynamodb
        
        # Initialize data manager
        data_manager = DataManager()
        print("✅ DataManager initialized")
        
        # Test S3 storage
        test_user_id = "test_user_001"
        test_date = "2024-01-15"
        test_data = "This is a test transcript for AWS setup verification."
        
        print("Testing S3 storage...")
        s3_key = store_data_in_s3(test_user_id, test_date, test_data)
        if s3_key:
            print(f"✅ S3 storage test successful: {s3_key}")
        else:
            print("❌ S3 storage test failed")
            return False
        
        # Test DynamoDB storage
        print("Testing DynamoDB storage...")
        success = save_to_dynamodb(
            user_id=test_user_id,
            date=test_date,
            transcript=test_data,
            emotion="test",
            score=75,
            feedback="Test feedback",
            cognitive_metrics={"test": "value"}
        )
        
        if success:
            print("✅ DynamoDB storage test successful")
        else:
            print("❌ DynamoDB storage test failed")
            return False
        
        # Test data retrieval
        print("Testing data retrieval...")
        from aws_services import get_user_data
        retrieved_data = get_user_data(test_user_id)
        
        if retrieved_data:
            print(f"✅ Data retrieval test successful: {len(retrieved_data)} entries found")
            print(f"Sample entry: {retrieved_data[0]}")
        else:
            print("❌ Data retrieval test failed - no data found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Data storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_pipeline():
    """Test the complete analysis and storage pipeline."""
    print("\n=== Complete Pipeline Test ===")
    
    try:
        from storage import DataManager
        from agents import EmotionAgent
        from nlp_metrics import analyze_cognitive_metrics
        from scoring import calculate_cognora_score
        
        # Initialize components
        data_manager = DataManager()
        emotion_agent = EmotionAgent()
        
        # Test text
        test_text = "Today I felt happy and energetic. I went for a walk and talked to my neighbor about gardening."
        
        print("Running complete analysis pipeline...")
        
        # Step 1: Emotion analysis
        emotion_analysis = emotion_agent.analyze_emotion(test_text)
        print(f"✅ Emotion analysis completed: {emotion_analysis}")
        
        # Step 2: Cognitive metrics
        cognitive_metrics = analyze_cognitive_metrics(test_text)
        print(f"✅ Cognitive metrics completed: {cognitive_metrics}")
        
        # Step 3: Score calculation
        score_data = calculate_cognora_score(emotion_analysis, cognitive_metrics)
        print(f"✅ Score calculation completed: {score_data}")
        
        # Step 4: Save to storage
        test_user_id = "test_user_001"
        test_date = "2024-01-15"
        
        success = data_manager.save_daily_entry(
            test_user_id, test_date, test_text, emotion_analysis, cognitive_metrics, score_data
        )
        
        if success:
            print("✅ Complete pipeline test successful!")
            return True
        else:
            print("❌ Complete pipeline test failed at save step")
            return False
            
    except Exception as e:
        print(f"❌ Complete pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🧠 Cognora+ AWS Setup Test")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("AWS Module Imports", test_aws_imports),
        ("AWS Connection", test_aws_connection),
        ("Data Storage", test_data_storage),
        ("Complete Pipeline", test_complete_pipeline)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your AWS setup is working correctly.")
        print("You can now run the Cognora+ application.")
    else:
        print("⚠️  Some tests failed. Please check the errors above and fix the issues.")
        print("\nCommon issues and solutions:")
        print("1. Missing .env file - Create a .env file with your AWS credentials")
        print("2. Invalid AWS credentials - Check your AWS Access Key and Secret Key")
        print("3. Missing AWS resources - Ensure S3 bucket and DynamoDB table exist")
        print("4. Permission issues - Check IAM roles and policies")
        print("5. Region mismatch - Ensure all resources are in the same AWS region")

if __name__ == "__main__":
    main() 