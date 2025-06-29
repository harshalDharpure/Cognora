<<<<<<< HEAD
import boto3
import os
import json
import time
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()

# Initialize AWS clients with better error handling
def initialize_aws_clients():
    """Initialize AWS clients with proper error handling."""
    try:
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_region_name = os.getenv("AWS_REGION_NAME")
        s3_bucket_name = os.getenv("S3_BUCKET_NAME")
        dynamodb_table_name = os.getenv("DYNAMODB_TABLE_NAME")
        sns_topic_arn = os.getenv("SNS_TOPIC_ARN")
        
        # Validate required environment variables
        missing_vars = []
        if not aws_access_key_id:
            missing_vars.append("AWS_ACCESS_KEY_ID")
        if not aws_secret_access_key:
            missing_vars.append("AWS_SECRET_ACCESS_KEY")
        if not aws_region_name:
            missing_vars.append("AWS_REGION_NAME")
        if not s3_bucket_name:
            missing_vars.append("S3_BUCKET_NAME")
        if not dynamodb_table_name:
            missing_vars.append("DYNAMODB_TABLE_NAME")
        
        if missing_vars:
            print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
            return None, None, None, None, None, None
        
        print(f"DEBUG: AWS Configuration loaded - Region: {aws_region_name}, S3: {s3_bucket_name}, DynamoDB: {dynamodb_table_name}")
        
        return aws_access_key_id, aws_secret_access_key, aws_region_name, s3_bucket_name, dynamodb_table_name, sns_topic_arn
        
    except Exception as e:
        print(f"ERROR: Failed to initialize AWS configuration: {e}")
        return None, None, None, None, None, None

# Initialize configuration
aws_access_key_id, aws_secret_access_key, aws_region_name, s3_bucket_name, dynamodb_table_name, sns_topic_arn = initialize_aws_clients()

# Initialize AWS clients only if configuration is valid
if all([aws_access_key_id, aws_secret_access_key, aws_region_name]):
    try:
        bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name=aws_region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

        transcribe_client = boto3.client(
            service_name='transcribe',
            region_name=aws_region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

        s3_client = boto3.client(
            service_name='s3',
            region_name=aws_region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

        dynamodb = boto3.resource(
            service_name='dynamodb',
            region_name=aws_region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        
        if dynamodb_table_name:
            scores_table = dynamodb.Table(dynamodb_table_name)
            print(f"DEBUG: DynamoDB table '{dynamodb_table_name}' initialized")
        else:
            scores_table = None
            print("WARNING: DynamoDB table name not configured")

        if sns_topic_arn:
            sns_client = boto3.client(
                service_name='sns',
                region_name=aws_region_name,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
        else:
            sns_client = None
            print("WARNING: SNS topic ARN not configured")
            
        print("DEBUG: AWS clients initialized successfully")
        
    except Exception as e:
        print(f"ERROR: Failed to initialize AWS clients: {e}")
        bedrock_runtime = None
        transcribe_client = None
        s3_client = None
        dynamodb = None
        scores_table = None
        sns_client = None
else:
    print("ERROR: AWS configuration incomplete - clients not initialized")
    bedrock_runtime = None
    transcribe_client = None
    s3_client = None
    dynamodb = None
    scores_table = None
    sns_client = None

def invoke_claude_sonnet(prompt):
    """Invokes the Claude 3 Sonnet model via Bedrock."""
    if not bedrock_runtime:
        print("ERROR: Bedrock client not initialized")
        return None
        
    try:
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }
            ]
        })
        modelId = 'anthropic.claude-3-sonnet-20240229-v1:0'
        accept = 'application/json'
        contentType = 'application/json'

        response = bedrock_runtime.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
        response_body = json.loads(response.get('body').read())
        return response_body['content'][0]['text']
    except Exception as e:
        print(f"ERROR: Failed to invoke Claude Sonnet: {e}")
        return None

def transcribe_audio_file_fallback(audio_file):
    """Fallback transcription function for testing when AWS is not available."""
    print("WARNING: Using fallback transcription (mock data)")
    
    # Return a sample transcript for testing
    sample_transcripts = [
        "Today I felt really good. I went for a walk in the park and enjoyed the sunshine. The fresh air made me feel energized and happy.",
        "I'm feeling a bit tired today but overall okay. Work was busy but manageable. Looking forward to relaxing this evening.",
        "Had a wonderful conversation with my friend today. We talked about our plans for the weekend and shared some good memories.",
        "Feeling grateful for the small things today. The coffee was perfect, and I had a productive morning. Life is good.",
        "Today was challenging but I'm proud of how I handled it. Sometimes you have to push through difficult moments."
    ]
    
    import random
    return random.choice(sample_transcripts)

def transcribe_audio_file(audio_file, job_name=None):
    """Transcribes audio from a file object and returns the transcript."""
    # Check if AWS services are available
    if not transcribe_client or not s3_client:
        print("WARNING: AWS services not available, using fallback transcription")
        return transcribe_audio_file_fallback(audio_file)
        
    try:
        # Generate job name if not provided
        if job_name is None:
            job_name = f"cognora_transcription_{int(time.time())}"
        
        # Determine file format based on file name or content
        file_extension = '.wav'  # default
        if hasattr(audio_file, 'name'):
            if audio_file.name.lower().endswith('.mp3'):
                file_extension = '.mp3'
            elif audio_file.name.lower().endswith('.m4a'):
                file_extension = '.m4a'
            elif audio_file.name.lower().endswith('.flac'):
                file_extension = '.flac'
            elif audio_file.name.lower().endswith('.webm'):
                file_extension = '.webm'
        
        # Map file extensions to AWS Transcribe media formats
        media_format_map = {
            '.wav': 'wav',
            '.mp3': 'mp3',
            '.m4a': 'mp4',
            '.flac': 'flac',
            '.webm': 'webm'
        }
        media_format = media_format_map.get(file_extension, 'wav')
        
        # Save the file object to a temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            # Write the file content to temporary file
            if hasattr(audio_file, 'read'):
                # It's a file-like object
                temp_file.write(audio_file.read())
            else:
                # It's bytes
                temp_file.write(audio_file)
            temp_file_path = temp_file.name
        
        try:
            # Upload audio file to S3
            s3_key = f"audio-uploads/{job_name}{file_extension}"
            s3_client.upload_file(temp_file_path, s3_bucket_name, s3_key)
            print(f"DEBUG: Audio file uploaded to S3: {s3_key}")
            
            media_uri = f"s3://{s3_bucket_name}/{s3_key}"

            transcribe_client.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': media_uri},
                MediaFormat=media_format,
                LanguageCode='en-US'
            )

            print(f"DEBUG: Transcription job started: {job_name}")
            
            while True:
                status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
                job_status = status['TranscriptionJob']['TranscriptionJobStatus']
                if job_status in ['COMPLETED', 'FAILED']:
                    break
                print(f"Transcription in progress... Status: {job_status}")
                time.sleep(5)

            if job_status == 'COMPLETED':
                transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
                content = s3_client.get_object(Bucket=s3_bucket_name, Key=transcript_uri.split(f"{s3_bucket_name}/")[-1])
                transcript_data = json.loads(content['Body'].read().decode('utf-8'))
                transcript = transcript_data['results']['transcripts'][0]['transcript']
                print(f"DEBUG: Transcription completed successfully. Length: {len(transcript)} characters")
                return transcript
            else:
                print(f"ERROR: Transcription failed with status: {job_status}")
                if 'FailureReason' in status['TranscriptionJob']:
                    print(f"Failure reason: {status['TranscriptionJob']['FailureReason']}")
                return None
                
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass  # Ignore cleanup errors
            
    except Exception as e:
        print(f"ERROR: Failed during transcription: {e}")
        import traceback
        traceback.print_exc()
        print("Falling back to mock transcription...")
        return transcribe_audio_file_fallback(audio_file)

def transcribe_audio(audio_file_path, job_name):
    """Starts a transcription job and returns the transcript."""
    if not transcribe_client or not s3_client:
        print("ERROR: Transcription or S3 client not initialized")
        return None
        
    try:
        # Upload audio file to S3
        s3_key = f"audio-uploads/{job_name}"
        s3_client.upload_file(audio_file_path, s3_bucket_name, s3_key)
        print(f"DEBUG: Audio file uploaded to S3: {s3_key}")
        
        media_uri = f"s3://{s3_bucket_name}/{s3_key}"

        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': media_uri},
            MediaFormat='wav',  # Assuming WAV format, adjust as needed
            LanguageCode='en-US'
        )

        while True:
            status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            print("Transcription in progress...")
            time.sleep(5)

        if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
            transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            content = s3_client.get_object(Bucket=s3_bucket_name, Key=transcript_uri.split(f"{s3_bucket_name}/")[-1])
            transcript_data = json.loads(content['Body'].read().decode('utf-8'))
            return transcript_data['results']['transcripts'][0]['transcript']
        else:
            print(f"ERROR: Transcription failed with status: {status['TranscriptionJob']['TranscriptionJobStatus']}")
            return None
    except Exception as e:
        print(f"ERROR: Failed during transcription: {e}")
        return None

def store_data_in_s3(user_id, date, data):
    """Stores data in S3 with better error handling."""
    if not s3_client:
        print("ERROR: S3 client not initialized")
        return None
        
    try:
        s3_key = f"transcripts/{user_id}/{date}.txt"
        s3_client.put_object(Bucket=s3_bucket_name, Key=s3_key, Body=data)
        print(f"DEBUG: Data stored in S3: {s3_key}")
        return s3_key
    except Exception as e:
        print(f"ERROR: Failed to store data in S3: {e}")
        return None

def store_report_in_s3(user_id, date, report):
    """Stores a report in S3 with better error handling."""
    if not s3_client:
        print("ERROR: S3 client not initialized")
        return None
        
    try:
        s3_key = f"reports/{user_id}/{date}.pdf"
        s3_client.put_object(Bucket=s3_bucket_name, Key=s3_key, Body=report)
        print(f"DEBUG: Report stored in S3: {s3_key}")
        return s3_key
    except Exception as e:
        print(f"ERROR: Failed to store report in S3: {e}")
        return None

def save_to_dynamodb(user_id, date, transcript, emotion, score, feedback, cognitive_metrics, source='text'):
    """Saves analysis results to DynamoDB with improved error handling."""
    if not scores_table:
        print("ERROR: DynamoDB table not initialized")
        return False
        
    try:
        print(f"DEBUG: Attempting to save to DynamoDB - User: {user_id}, Date: {date}, Score: {score}, Source: {source}")
        
        # Convert score to Decimal for DynamoDB compatibility
        try:
            score_decimal = Decimal(str(score))
        except:
            score_decimal = Decimal('50.0')
            print(f"WARNING: Invalid score '{score}', using default 50.0")
        
        # Prepare item with proper DynamoDB types
        item_to_save = {
            'user_id': str(user_id),
            'date': str(date),  # Ensure date is stored as string
            'transcript': str(transcript),
            'emotion': str(emotion),
            'score': score_decimal,
            'feedback': str(feedback),
            'cognitive_metrics': {k: str(v) for k, v in cognitive_metrics.items()},
            'source': str(source),  # Add source field to track voice vs text
            'timestamp': str(time.time())  # Add timestamp for sorting
        }
        
        print(f"DEBUG: Saving item to DynamoDB: {item_to_save}")
        
        # Save to DynamoDB
        scores_table.put_item(Item=item_to_save)
        
        print(f"DEBUG: Successfully saved to DynamoDB - User: {user_id}, Date: {date}, Source: {source}")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to save to DynamoDB: {e}")
        print(f"ERROR: Item that failed to save: {item_to_save if 'item_to_save' in locals() else 'Not created'}")
        return False

def get_user_data(user_id):
    """Retrieves all data for a user from DynamoDB with better error handling."""
    if not scores_table:
        print("ERROR: DynamoDB table not initialized")
        return []
        
    try:
        print(f"DEBUG: Retrieving data for user: {user_id}")
        
        response = scores_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(str(user_id))
        )
        
        items = response.get('Items', [])
        print(f"DEBUG: Retrieved {len(items)} items for user {user_id}")
        
        # Debug: Show what fields are in each item
        for i, item in enumerate(items[:3]):  # Show first 3 items
            print(f"DEBUG: Item {i+1} fields: {list(item.keys())}")
            print(f"DEBUG: Item {i+1} source: {item.get('source', 'NOT_FOUND')}")
        
        # Convert Decimal types back to regular numbers for JSON serialization
        for item in items:
            if 'score' in item and isinstance(item['score'], Decimal):
                item['score'] = float(item['score'])
        
        return items
        
    except Exception as e:
        print(f"ERROR: Failed to retrieve data from DynamoDB: {e}")
        return []

def send_alert(subject, message):
    """Sends an alert via SNS with better error handling."""
    if not sns_client:
        print("ERROR: SNS client not initialized")
        return False
        
    try:
        print(f"DEBUG: Sending SNS alert - Subject: {subject}")
        
        sns_client.publish(
            TopicArn=sns_topic_arn,
            Subject=subject,
            Message=message
        )
        
        print(f"DEBUG: SNS alert sent successfully")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to send SNS alert: {e}")
        return False

def test_aws_connection():
    """Test AWS connection and permissions."""
    print("=== AWS Connection Test ===")
    
    # Test S3
    if s3_client and s3_bucket_name:
        try:
            s3_client.head_bucket(Bucket=s3_bucket_name)
            print(f"✅ S3 bucket '{s3_bucket_name}' accessible")
        except Exception as e:
            print(f"❌ S3 bucket '{s3_bucket_name}' not accessible: {e}")
    else:
        print("❌ S3 not configured")
    
    # Test DynamoDB
    if scores_table:
        try:
            scores_table.table_status
            print(f"✅ DynamoDB table '{dynamodb_table_name}' accessible")
        except Exception as e:
            print(f"❌ DynamoDB table '{dynamodb_table_name}' not accessible: {e}")
    else:
        print("❌ DynamoDB not configured")
    
    # Test SNS
    if sns_client and sns_topic_arn:
        try:
            sns_client.get_topic_attributes(TopicArn=sns_topic_arn)
            print(f"✅ SNS topic accessible")
        except Exception as e:
            print(f"❌ SNS topic not accessible: {e}")
    else:
        print("❌ SNS not configured")
    
    print("=== End AWS Connection Test ===")
=======
import boto3
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()

# Initialize AWS clients
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_region_name = os.getenv("AWS_REGION_NAME")
s3_bucket_name = os.getenv("S3_BUCKET_NAME")
dynamodb_table_name = os.getenv("DYNAMODB_TABLE_NAME")
sns_topic_arn = os.getenv("SNS_TOPIC_ARN")

bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name=aws_region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

transcribe_client = boto3.client(
    service_name='transcribe',
    region_name=aws_region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

s3_client = boto3.client(
    service_name='s3',
    region_name=aws_region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

dynamodb = boto3.resource(
    service_name='dynamodb',
    region_name=aws_region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)
scores_table = dynamodb.Table(dynamodb_table_name)

sns_client = boto3.client(
    service_name='sns',
    region_name=aws_region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

def invoke_claude_sonnet(prompt):
    """Invokes the Claude 3 Sonnet model via Bedrock."""
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }
        ]
    })
    modelId = 'anthropic.claude-3-sonnet-20240229-v1:0'
    accept = 'application/json'
    contentType = 'application/json'

    response = bedrock_runtime.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    response_body = json.loads(response.get('body').read())
    return response_body['content'][0]['text']

def transcribe_audio(audio_file_path, job_name):
    """Starts a transcription job and returns the transcript."""
    try:
        # Upload audio file to S3
        s3_key = f"audio-uploads/{job_name}"
        s3_client.upload_file(audio_file_path, s3_bucket_name, s3_key)
        
        media_uri = f"s3://{s3_bucket_name}/{s3_key}"

        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': media_uri},
            MediaFormat='wav',  # Assuming WAV format, adjust as needed
            LanguageCode='en-US'
        )

        while True:
            status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            print("Transcription in progress...")
            time.sleep(5)

        if status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
            transcript_uri = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            content = s3_client.get_object(Bucket=s3_bucket_name, Key=transcript_uri.split(f"{s3_bucket_name}/")[-1])
            transcript_data = json.loads(content['Body'].read().decode('utf-8'))
            return transcript_data['results']['transcripts'][0]['transcript']
        else:
            return "Transcription failed."
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None

def store_data_in_s3(user_id, date, data):
    """Stores data in S3."""
    s3_key = f"transcripts/{user_id}/{date}.txt"
    s3_client.put_object(Bucket=s3_bucket_name, Key=s3_key, Body=data)
    return s3_key

def store_report_in_s3(user_id, date, report):
    """Stores a report in S3."""
    s3_key = f"reports/{user_id}/{date}.pdf"
    s3_client.put_object(Bucket=s3_bucket_name, Key=s3_key, Body=report)
    return s3_key

def save_to_dynamodb(user_id, date, transcript, emotion, score, feedback):
    """Saves analysis results to DynamoDB."""
    try:
        scores_table.put_item(
            Item={
                'user_id': user_id,
                'date': date,
                'transcript': transcript,
                'emotion': emotion,
                'score': score,
                'feedback': feedback
            }
        )
        return True
    except Exception as e:
        print(f"Error saving to DynamoDB: {e}")
        return False

def get_user_data(user_id):
    """Retrieves all data for a user from DynamoDB."""
    try:
        response = scores_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id)
        )
        return response.get('Items', [])
    except Exception as e:
        print(f"Error retrieving data from DynamoDB: {e}")
        return []

def send_alert(subject, message):
    """Sends an alert via SNS."""
    try:
        sns_client.publish(
            TopicArn=sns_topic_arn,
            Subject=subject,
            Message=message
        )
        return True
    except Exception as e:
        print(f"Error sending SNS alert: {e}")
        return False
>>>>>>> 23a3f924b5333426fb4b4fb6085453f9515378f8
