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
