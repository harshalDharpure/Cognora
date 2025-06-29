#!/usr/bin/env python3
"""
Production Configuration for Cognora+
Handles environment variables, feature flags, and deployment settings.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class Market(Enum):
    JAPAN = "japan"
    US = "us"
    GLOBAL = "global"

@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    table_name: str
    region: str
    backup_enabled: bool
    encryption_enabled: bool

@dataclass
class SecurityConfig:
    """Security configuration settings."""
    session_timeout_minutes: int
    max_login_attempts: int
    password_expiry_days: int
    mfa_enabled: bool
    rate_limiting_enabled: bool

@dataclass
class AnalyticsConfig:
    """Analytics and monitoring configuration."""
    google_analytics_id: str
    mixpanel_token: str
    sentry_dsn: str
    log_level: str

class Config:
    """Main configuration class for Cognora+."""
    
    def __init__(self):
        self.environment = Environment(os.getenv("ENVIRONMENT", "development"))
        self.market = Market(os.getenv("MARKET", "global"))
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # AWS Configuration
        self.aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        
        # Database Configuration
        self.database = DatabaseConfig(
            table_name=os.getenv("DYNAMODB_TABLE_NAME", "cognora_users"),
            region=self.aws_region,
            backup_enabled=os.getenv("DB_BACKUP_ENABLED", "true").lower() == "true",
            encryption_enabled=os.getenv("DB_ENCRYPTION_ENABLED", "true").lower() == "true"
        )
        
        # Security Configuration
        self.security = SecurityConfig(
            session_timeout_minutes=int(os.getenv("SESSION_TIMEOUT_MINUTES", "480")),  # 8 hours
            max_login_attempts=int(os.getenv("MAX_LOGIN_ATTEMPTS", "5")),
            password_expiry_days=int(os.getenv("PASSWORD_EXPIRY_DAYS", "90")),
            mfa_enabled=os.getenv("MFA_ENABLED", "false").lower() == "true",
            rate_limiting_enabled=os.getenv("RATE_LIMITING_ENABLED", "true").lower() == "true"
        )
        
        # Analytics Configuration
        self.analytics = AnalyticsConfig(
            google_analytics_id=os.getenv("GOOGLE_ANALYTICS_ID", ""),
            mixpanel_token=os.getenv("MIXPANEL_TOKEN", ""),
            sentry_dsn=os.getenv("SENTRY_DSN", ""),
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )
        
        # Feature Flags (Billing disabled)
        self.features = {
            "voice_recording": os.getenv("FEATURE_VOICE_RECORDING", "true").lower() == "true",
            "ai_analysis": os.getenv("FEATURE_AI_ANALYSIS", "true").lower() == "true",
            "caregiver_alerts": os.getenv("FEATURE_CAREGIVER_ALERTS", "true").lower() == "true",
            "reports": os.getenv("FEATURE_REPORTS", "true").lower() == "true",
            "multi_language": os.getenv("FEATURE_MULTI_LANGUAGE", "true").lower() == "true",
            "subscription_billing": False,  # Disabled
            "mfa": os.getenv("FEATURE_MFA", "false").lower() == "true",
            "api_access": os.getenv("FEATURE_API_ACCESS", "false").lower() == "true"
        }
        
        # Market-specific configurations
        self.market_config = self._get_market_config()
    
    def _get_market_config(self) -> Dict[str, Any]:
        """Get market-specific configuration."""
        configs = {
            Market.JAPAN: {
                "default_language": "ja",
                "supported_languages": ["ja", "en"],
                "currency": "JPY",
                "timezone": "Asia/Tokyo",
                "compliance": ["GDPR", "APPI"],  # Japanese privacy law
                "support_email": "support@cognora.jp",
                "legal_entity": "Cognora Japan K.K.",
                "terms_url": "https://cognora.jp/terms",
                "privacy_url": "https://cognora.jp/privacy"
            },
            Market.US: {
                "default_language": "en",
                "supported_languages": ["en", "es"],
                "currency": "USD",
                "timezone": "America/New_York",
                "compliance": ["GDPR", "CCPA", "HIPAA"],
                "support_email": "support@cognora.com",
                "legal_entity": "Cognora Inc.",
                "terms_url": "https://cognora.com/terms",
                "privacy_url": "https://cognora.com/privacy"
            },
            Market.GLOBAL: {
                "default_language": "en",
                "supported_languages": ["en", "ja", "es", "fr", "de"],
                "currency": "USD",
                "timezone": "UTC",
                "compliance": ["GDPR"],
                "support_email": "support@cognora.global",
                "legal_entity": "Cognora Global Ltd.",
                "terms_url": "https://cognora.global/terms",
                "privacy_url": "https://cognora.global/privacy"
            }
        }
        
        return configs.get(self.market, configs[Market.GLOBAL])
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled."""
        return self.features.get(feature_name, False)
    
    def get_market_setting(self, setting_name: str) -> Any:
        """Get market-specific setting."""
        return self.market_config.get(setting_name)

# Global configuration instance
config = Config() 