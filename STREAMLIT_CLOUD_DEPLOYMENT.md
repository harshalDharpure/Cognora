# Streamlit Cloud Deployment Guide for Cognora+

This guide will help you deploy your Cognora+ AI wellness assistant to Streamlit Cloud.

## Prerequisites

1. **GitHub Account**: Your code must be in a GitHub repository
2. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **AWS Account**: For DynamoDB, SNS, and other AWS services
4. **Environment Variables**: You'll need to configure these in Streamlit Cloud

## Step 1: Prepare Your Repository

### 1.1 Ensure Your Repository Structure
Your repository should have this structure:
```
cognora/
├── app.py                 # Main Streamlit app
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── config.toml       # Streamlit configuration
├── config.py             # Configuration management
├── agents.py             # AI agents
├── scoring.py            # Scoring logic
├── storage.py            # Data storage
├── aws_services.py       # AWS services
├── auth.py               # Authentication
├── utils.py              # Utilities
└── ... (other files)
```

### 1.2 Update Requirements (Already Done)
The `requirements.txt` has been updated with specific versions for Streamlit Cloud compatibility.

### 1.3 Environment Variables Setup
You'll need to configure these environment variables in Streamlit Cloud:

#### Required AWS Variables:
```
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1
```

#### Required App Variables:
```
DYNAMODB_TABLE_NAME=cognora_users
ENVIRONMENT=production
MARKET=global
```

#### Optional Variables:
```
SENTRY_DSN=your_sentry_dsn
MIXPANEL_TOKEN=your_mixpanel_token
GOOGLE_ANALYTICS_ID=your_ga_id
```

## Step 2: Deploy to Streamlit Cloud

### 2.1 Connect Your GitHub Repository

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository: `your-username/cognora`
5. Set the main file path: `app.py`
6. Set the app URL (optional): `cognora-plus`

### 2.2 Configure Environment Variables

1. In your app settings, go to "Secrets"
2. Add your environment variables in TOML format:

```toml
AWS_ACCESS_KEY_ID = "your_aws_access_key"
AWS_SECRET_ACCESS_KEY = "your_aws_secret_key"
AWS_DEFAULT_REGION = "us-east-1"
DYNAMODB_TABLE_NAME = "cognora_users"
ENVIRONMENT = "production"
MARKET = "global"
SENTRY_DSN = "your_sentry_dsn"
MIXPANEL_TOKEN = "your_mixpanel_token"
GOOGLE_ANALYTICS_ID = "your_ga_id"
```

### 2.3 Deploy Settings

- **Python version**: 3.9 or 3.10 (recommended)
- **Package manager**: pip
- **Main file path**: `app.py`

## Step 3: Post-Deployment Configuration

### 3.1 AWS Setup Verification

Ensure your AWS resources are properly configured:

1. **DynamoDB Table**: `cognora_users` should exist with correct schema
2. **SNS Topic**: For caregiver alerts
3. **IAM Permissions**: Your AWS credentials should have access to:
   - DynamoDB (read/write)
   - SNS (publish)
   - Transcribe (if using voice features)

### 3.2 Test Your Deployment

1. **Authentication**: Test login/signup functionality
2. **Data Storage**: Verify data is being saved to DynamoDB
3. **Alerts**: Test caregiver alert functionality
4. **Voice Features**: Test audio recording and transcription

## Step 4: Monitoring and Maintenance

### 4.1 Streamlit Cloud Monitoring

- Monitor app performance in Streamlit Cloud dashboard
- Check logs for any errors
- Monitor resource usage

### 4.2 AWS Monitoring

- Set up CloudWatch alarms for DynamoDB usage
- Monitor SNS delivery status
- Track costs and usage

## Troubleshooting Common Issues

### Issue 1: Import Errors
**Problem**: Module not found errors
**Solution**: Ensure all dependencies are in `requirements.txt` with correct versions

### Issue 2: AWS Connection Errors
**Problem**: Cannot connect to AWS services
**Solution**: 
- Verify AWS credentials in Streamlit Cloud secrets
- Check IAM permissions
- Ensure AWS region is correct

### Issue 3: Memory Issues
**Problem**: App crashes due to memory limits
**Solution**:
- Optimize data processing
- Use pagination for large datasets
- Consider using Streamlit's caching

### Issue 4: File Upload Issues
**Problem**: Audio files not uploading
**Solution**:
- Check `maxUploadSize` in `.streamlit/config.toml`
- Ensure proper file validation

### Issue 5: Authentication Issues
**Problem**: Login not working
**Solution**:
- Verify session state management
- Check if authentication is properly initialized
- Ensure secure cookie settings

## Security Considerations

1. **Environment Variables**: Never commit sensitive data to your repository
2. **AWS Credentials**: Use IAM roles with minimal required permissions
3. **HTTPS**: Streamlit Cloud provides HTTPS by default
4. **Session Management**: Implement proper session timeouts

## Performance Optimization

1. **Caching**: Use `@st.cache_data` for expensive computations
2. **Lazy Loading**: Load data only when needed
3. **Connection Pooling**: Reuse AWS connections
4. **Error Handling**: Implement proper error boundaries

## Cost Management

1. **AWS Costs**: Monitor DynamoDB read/write units
2. **Streamlit Cloud**: Free tier available, paid plans for more resources
3. **Optimization**: Use efficient queries and caching

## Support and Resources

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Forum](https://discuss.streamlit.io/)
- [AWS Documentation](https://docs.aws.amazon.com/)

## Next Steps

After successful deployment:

1. Set up custom domain (optional)
2. Configure monitoring and alerting
3. Set up CI/CD pipeline for automated deployments
4. Implement backup and disaster recovery
5. Plan for scaling as user base grows

---

**Note**: This deployment guide assumes you have already set up your AWS infrastructure using the Terraform scripts in the `terraform/` directory. If not, please follow the `DEPLOYMENT.md` guide first. 