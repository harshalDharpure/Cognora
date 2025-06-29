# 🧠 Cognora+ - AI-Powered Wellness Assistant

Cognora+ is an intelligent wellness monitoring system that uses AI to analyze user input (text and voice) to track emotional and cognitive health. The system provides real-time insights, generates wellness scores, and can alert caregivers when concerning patterns are detected.

## 🌟 Features

### 🔐 **Authentication System**
- **Secure User Registration**: Create accounts with email validation and strong password requirements
- **User Login**: Secure authentication with password hashing and session management
- **Profile Management**: Store user information including age, location, and caregiver contacts
- **Password Management**: Change passwords securely with validation
- **Account Deactivation**: Safely deactivate accounts when needed
- **AWS Integration**: All user data stored securely in AWS DynamoDB

### 🎤 **Voice Input**
- **Real-time Recording**: Record audio directly in the browser using microphone
- **Multiple Formats**: Support for WAV, MP3, M4A, and FLAC audio files
- **Audio Playback**: Listen to recordings before analysis
- **Download Option**: Save recordings locally
- **AWS Transcription**: Convert speech to text using AWS Transcribe

### 📝 **Text Input**
- **Daily Check-ins**: Share thoughts, experiences, and feelings
- **AI Analysis**: Advanced NLP analysis of emotional and cognitive patterns
- **Real-time Processing**: Instant feedback and insights

### 📊 **Dashboard & Analytics**
- **Wellness Score**: Daily Cognora score based on AI analysis
- **Trend Analysis**: 7-day score trends and patterns
- **Emotion Tracking**: Visual representation of emotional states
- **Dual Input Support**: Separate tracking for voice and text entries
- **Real-time Updates**: Live dashboard with current data

### 🔔 **Alert System**
- **Caregiver Notifications**: Automatic alerts for concerning patterns
- **Configurable Sensitivity**: Adjustable alert thresholds
- **SNS Integration**: AWS SNS for reliable message delivery
- **Alert History**: Track all sent notifications

### 📈 **Reports & Export**
- **Weekly Reports**: Comprehensive wellness summaries
- **Data Export**: CSV export for external analysis
- **S3 Storage**: Secure cloud storage for reports and transcripts

### 🌍 **Internationalization**
- **Multi-language Support**: English and Japanese interfaces
- **Localized Content**: Translated UI elements and messages
- **Cultural Adaptation**: Region-specific wellness insights

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- AWS Account with appropriate permissions
- AWS credentials configured

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd cognora
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure AWS credentials**
   ```bash
   aws configure
   ```

4. **Test AWS connection**
   ```bash
   python test_aws_setup.py
   ```

5. **Test authentication system**
   ```bash
   python test_auth_system.py
   ```

6. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 🔐 Authentication Setup

### First Time Setup
1. **Run the app**: `streamlit run app.py`
2. **Create Account**: Click "Sign Up" tab
3. **Fill Details**: Enter your information and create a strong password
4. **Login**: Use your email and password to access the system

### User Registration Requirements
- **Email**: Valid email format (e.g., user@example.com)
- **Password**: Minimum 8 characters with uppercase, lowercase, and number
- **Age**: Must be 18-120 years
- **Name**: Full name required
- **Optional**: Location and caregiver email

### Security Features
- **Password Hashing**: SHA-256 with salt
- **Session Management**: Secure session state handling
- **Input Validation**: Comprehensive validation for all inputs
- **AWS Security**: IAM roles and policies for data protection

## 🎤 Using Voice Input

1. **Navigate to Daily Check-in**
2. **Select Voice Input tab**
3. **Click "Start Recording"** to begin
4. **Speak clearly** into your microphone
5. **Click "Stop Recording"** when finished
6. **Listen to playback** to verify recording
7. **Click "Use This Recording"** to analyze
8. **Download recording** if needed for backup

## 📊 Understanding Your Dashboard

### Wellness Score
- **75-100**: Excellent wellness indicators
- **50-74**: Good wellness indicators  
- **25-49**: Moderate concerns
- **0-24**: Significant concerns (triggers alerts)

### Dual Input Tracking
- **Voice Entries**: Microphone recordings with transcription
- **Text Entries**: Typed daily check-ins
- **Score Comparison**: Compare wellness patterns between input methods
- **Entry History**: View all past entries with source indicators

## 🔧 Configuration

### AWS Services Required
- **DynamoDB**: User data and wellness scores
- **S3**: Audio files and reports storage
- **SNS**: Alert notifications
- **Transcribe**: Speech-to-text conversion
- **Bedrock**: AI analysis (Claude Sonnet)

### Environment Variables
```bash
AWS_DEFAULT_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

## 🧪 Testing

### Test Authentication
```bash
python test_auth_system.py
```

### Test Voice Entries
```bash
python test_voice_entries.py
```

### Test AWS Setup
```bash
python test_aws_setup.py
```

### Test Japanese Translations
```bash
python test_japanese_translations.py
```

## 📁 Project Structure

```
cognora/
├── app.py                 # Main Streamlit application
├── auth.py               # Authentication system
├── login_signup.py       # Login/signup UI components
├── aws_services.py       # AWS service integrations
├── storage.py            # Data management
├── audio_recorder.py     # Voice recording functionality
├── scoring.py            # Wellness scoring algorithms
├── nlp_metrics.py        # NLP analysis functions
├── agents.py             # AI agent configurations
├── utils.py              # Utility functions and translations
├── requirements.txt      # Python dependencies
├── test_*.py            # Test scripts
└── terraform/           # Infrastructure as code
```

## 🔒 Security & Privacy

- **Data Encryption**: All data encrypted in transit and at rest
- **User Isolation**: Each user's data is completely isolated
- **Password Security**: Industry-standard password hashing
- **Session Security**: Secure session management
- **AWS Compliance**: Follows AWS security best practices

## 🌐 Deployment

### Local Development
```bash
streamlit run app.py
```

### Production Deployment
```bash
# Using Docker
docker build -t cognora .
docker run -p 8501:8501 cognora

# Using AWS
./deploy.sh
```

## 📞 Support

For technical support or questions:
- Check the test scripts for troubleshooting
- Review AWS service logs for errors
- Ensure all dependencies are installed
- Verify AWS credentials and permissions

## 🔄 Updates

The system automatically:
- Updates user preferences
- Tracks login history
- Manages session state
- Syncs data across devices
- Maintains audit trails

---

**Cognora+** - Empowering wellness through intelligent analysis and compassionate care.