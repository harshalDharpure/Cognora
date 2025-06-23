# 🧠 Cognora+ - AI-Powered Wellness Assistant

**Cognora+** is a comprehensive GenAI wellness application designed to monitor emotional and cognitive health from daily voice or text conversations, with intelligent caregiver alerting capabilities.

## 🌟 Features

### Core Functionality
- **Voice & Text Analysis**: Process daily conversations via text input or voice recording
- **AI-Powered Analysis**: Claude 3 Sonnet via Amazon Bedrock for emotional and cognitive assessment
- **Cognora Score**: Intelligent wellness scoring (0-100) with color-coded zones
- **Caregiver Alerts**: Automated notifications via AWS SNS when wellness indicators decline
- **Comprehensive Dashboard**: Real-time wellness tracking with charts and insights
- **Report Generation**: Weekly PDF reports and data exports
- **Internationalization**: Support for English and Japanese

### Technical Architecture
- **Frontend**: Streamlit with modern, responsive UI
- **Backend**: Python with modular architecture
- **AI/ML**: LangChain agents for specialized analysis
- **Cloud Infrastructure**: AWS (Bedrock, Transcribe, S3, DynamoDB, SNS)
- **Infrastructure as Code**: Terraform for automated deployment

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- AWS Account with appropriate permissions
- Terraform (for infrastructure deployment)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd cognora
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Environment Configuration
Create a `.env` file in the project root:
```env
AWS_ACCESS_KEY_ID="your_aws_access_key"
AWS_SECRET_ACCESS_KEY="your_aws_secret_access_key"
AWS_REGION_NAME="us-east-1"
S3_BUCKET_NAME="cognora-data-store"
DYNAMODB_TABLE_NAME="CognoraScores"
SNS_TOPIC_ARN="your_sns_topic_arn"
CAREGIVER_EMAIL="caregiver@example.com"
```
*(Note: You will get the `SNS_TOPIC_ARN` after running Terraform in the next step.)*

### 4. Deploy Infrastructure
```bash
cd terraform
terraform init
terraform apply
```
After applying, copy the `sns_topic_arn` from the output and add it to your `.env` file.

### 5. Run the Application
```bash
# Make sure you are in the project's root directory
streamlit run app.py
```

## 📋 Detailed Setup Guide

### AWS Services Setup

#### 1. Amazon Bedrock
- Enable Claude 3 Sonnet model access in your chosen AWS region.
- Configure IAM permissions for the Bedrock runtime.

#### 2. Amazon Transcribe
- Ensure Transcribe service is enabled in your region.
- Configure language settings (default: en-US).

#### 3. S3 Bucket
- Create a bucket for storing transcripts and reports (or let Terraform do it).
- Configure appropriate access policies.

#### 4. DynamoDB Table
- Create a table with `user_id` (hash key) and `date` (range key).
- Enable on-demand billing for cost optimization.

#### 5. SNS Topic
- Create a topic for caregiver alerts.
- Subscribe a caregiver email address.

### Terraform Deployment

The Terraform configuration automatically provisions:
- S3 bucket for data storage
- DynamoDB table for scores
- SNS topic and subscription
- IAM roles and policies
- Lambda function (placeholder)

```bash
# Initialize Terraform
terraform init

# Review the plan
terraform plan

# Apply the configuration
terraform apply

# Get outputs for configuration
terraform output
```

## 🧪 Testing

### Sample Data
The application includes sample data for testing:
- **Sample Transcripts**: `samples/sample_transcripts.json`
- **User Profiles**: `samples/user_profiles.json`

### Test Scenarios
1. **Happy/Positive Transcript**: Should score 75-95.
2. **Lonely/Concerned Transcript**: Should score 30-50.
3. **Confused/Cognitive Issues**: Should trigger alerts.
4. **Voice Input**: Test with `.wav` or `.mp3` audio files.

### Running Tests
```bash
# Test the scoring algorithm
python -c "from scoring import calculate_cognora_score; print('Scoring test passed')"

# Test AWS services (requires credentials)
python -c "from aws_services import *; print('AWS services test passed')"
```

## 📊 Application Structure

```
cognora/
├── app.py                 # Main Streamlit application
├── aws_services.py        # AWS service integrations
├── agents.py              # LangChain agents (Emotion, Memory, Alert)
├── scoring.py             # Cognora Score algorithm
├── storage.py             # Data management and reports
├── nlp_metrics.py         # Detailed NLP analysis pipeline
├── utils.py               # Utility functions and i18n
├── requirements.txt       # Python dependencies
├── .env.example           # Example environment variables
├── .gitignore             # Git ignore patterns
├── README.md              # This file
├── terraform/             # Infrastructure as Code
│   ├── main.tf            # Main Terraform configuration
│   ├── variables.tf       # Input variables
│   ├── outputs.tf         # Output values
│   ├── provider.tf        # AWS provider configuration
│   └── lambda_handler.py  # Lambda function code
└── samples/               # Sample data for testing
    ├── sample_transcripts.json
    └── user_profiles.json
```

## 🎯 Usage Guide

### Daily Check-in Process
1. **Navigate to "Daily Check-in with Momo"** in the sidebar.
2. **Choose Input Method**: Text or Voice.
3. **Share Your Day**: Describe your thoughts, feelings, and experiences.
4. **Review Analysis**: View emotional and cognitive insights.
5. **Save Entry**: Store results for tracking.

### Dashboard Features
- **Today's Score**: Current wellness indicator.
- **7-Day Trend**: Score progression over time.
- **Emotion Timeline**: Emotional state distribution.
- **Latest Transcript**: Yesterday's entry with AI interpretation.
- **Motivational Quote**: Daily inspiration.
- **Alert Status**: Current caregiver notification status.

### Reports and Analytics
- **Weekly Reports**: PDF downloads with comprehensive analysis.
- **Data Export**: CSV format for external analysis.
- **Alert History**: Track all caregiver notifications.

## 🔧 Configuration

### Alert Thresholds
- **Score Alert**: Triggers when Momo Score < 50 for 3 consecutive days.
- **Emotion Alert**: Triggers when "lonely" emotion is detected for 2 consecutive days.
- **Custom Thresholds**: Can be configured per user in the settings.

### Language Support
- **English**: Full support with natural language processing.
- **Japanese**: Basic internationalization support.
- **Extensible**: Easy to add additional languages in `utils.py`.

## 🚀 Deployment Options

### Local Development
```bash
streamlit run app.py
```

### Streamlit Cloud
1. Push code to a GitHub repository.
2. Connect the repository to Streamlit Cloud.
3. Configure environment variables in the settings.
4. Deploy automatically on push.

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 🔒 Security Considerations

### Data Privacy
- All data is encrypted in transit and at rest using AWS services.
- User data is stored with appropriate access controls.

### Access Control
- IAM roles should be reviewed and tightened to the principle of least privilege for production.
- Use a secrets management service like AWS Secrets Manager for production credentials.

## 🐛 Troubleshooting

### Common Issues

#### AWS Credentials Error
Ensure your `.env` file is correctly configured and that your AWS user has the required permissions for Bedrock, S3, DynamoDB, and SNS.
```bash
# Verify AWS credentials
aws sts get-caller-identity
```

#### Terraform Errors
```bash
# Clean and reinitialize if you encounter state issues
rm -rf .terraform
terraform init
```

---

**Cognora+** - Empowering wellness through intelligent conversation analysis. 🧠✨
