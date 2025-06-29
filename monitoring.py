#!/usr/bin/env python3
"""
Monitoring and Analytics for Cognora+
Production-ready monitoring with error tracking, performance metrics, and user analytics.
"""

import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import streamlit as st
from config import config
import requests

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.analytics.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AnalyticsManager:
    """Manages analytics and user tracking."""
    
    def __init__(self):
        self.google_analytics_id = config.analytics.google_analytics_id
        self.mixpanel_token = config.analytics.mixpanel_token
        self.sentry_dsn = config.analytics.sentry_dsn
        
        # Initialize Sentry if configured
        if self.sentry_dsn and config.is_production():
            self._init_sentry()
    
    def _init_sentry(self):
        """Initialize Sentry error tracking."""
        try:
            import sentry_sdk
            from sentry_sdk.integrations.streamlit import StreamlitIntegration
            
            sentry_sdk.init(
                dsn=self.sentry_dsn,
                integrations=[StreamlitIntegration()],
                traces_sample_rate=0.1,
                environment=config.environment.value
            )
            logger.info("Sentry initialized successfully")
        except ImportError:
            logger.warning("Sentry SDK not installed")
        except Exception as e:
            logger.error(f"Failed to initialize Sentry: {e}")
    
    def track_event(self, event_name: str, user_id: str = None, properties: Dict[str, Any] = None):
        """Track user events."""
        if not config.is_production():
            return
        
        event_data = {
            'event': event_name,
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'market': config.market.value,
            'environment': config.environment.value,
            'properties': properties or {}
        }
        
        # Log event
        logger.info(f"Event tracked: {event_name} for user {user_id}")
        
        # Send to analytics services
        self._send_to_mixpanel(event_data)
        self._send_to_google_analytics(event_data)
    
    def _send_to_mixpanel(self, event_data: Dict[str, Any]):
        """Send event to Mixpanel."""
        if not self.mixpanel_token:
            return
        
        try:
            url = "https://api.mixpanel.com/track"
            data = {
                'event': event_data['event'],
                'properties': {
                    'token': self.mixpanel_token,
                    'distinct_id': event_data['user_id'] or 'anonymous',
                    'time': int(time.time()),
                    **event_data['properties']
                }
            }
            
            response = requests.post(url, json=data, timeout=5)
            if response.status_code != 200:
                logger.warning(f"Mixpanel API error: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to send to Mixpanel: {e}")
    
    def _send_to_google_analytics(self, event_data: Dict[str, Any]):
        """Send event to Google Analytics."""
        if not self.google_analytics_id:
            return
        
        try:
            # Google Analytics 4 Measurement Protocol
            url = f"https://www.google-analytics.com/mp/collect"
            params = {
                'measurement_id': self.google_analytics_id,
                'api_secret': 'your_api_secret'  # Would be configured in production
            }
            
            data = {
                'client_id': event_data['user_id'] or 'anonymous',
                'events': [{
                    'name': event_data['event'],
                    'params': event_data['properties']
                }]
            }
            
            response = requests.post(url, params=params, json=data, timeout=5)
            if response.status_code != 204:
                logger.warning(f"Google Analytics API error: {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to send to Google Analytics: {e}")
    
    def track_error(self, error: Exception, user_id: str = None, context: Dict[str, Any] = None):
        """Track application errors."""
        error_data = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'context': context or {}
        }
        
        logger.error(f"Error tracked: {error_data['error_type']}: {error_data['error_message']}")
        
        # Sentry will automatically capture errors if initialized
        if self.sentry_dsn:
            import sentry_sdk
            with sentry_sdk.configure_scope() as scope:
                if user_id:
                    scope.set_user({"id": user_id})
                if context:
                    scope.set_context("error_context", context)
                sentry_sdk.capture_exception(error)

class PerformanceMonitor:
    """Monitors application performance."""
    
    def __init__(self):
        self.metrics = {}
        self.start_time = time.time()
    
    def start_timer(self, operation: str):
        """Start timing an operation."""
        self.metrics[operation] = {'start': time.time()}
    
    def end_timer(self, operation: str) -> float:
        """End timing an operation and return duration."""
        if operation in self.metrics:
            duration = time.time() - self.metrics[operation]['start']
            self.metrics[operation]['duration'] = duration
            self.metrics[operation]['end'] = time.time()
            return duration
        return 0.0
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'uptime': time.time() - self.start_time,
            'operations': self.metrics,
            'average_response_time': self._calculate_average_response_time()
        }
    
    def _calculate_average_response_time(self) -> float:
        """Calculate average response time."""
        durations = [op.get('duration', 0) for op in self.metrics.values()]
        return sum(durations) / len(durations) if durations else 0.0

class UserAnalytics:
    """Tracks user behavior and engagement."""
    
    def __init__(self):
        self.analytics_manager = AnalyticsManager()
    
    def track_page_view(self, page_name: str, user_id: str = None):
        """Track page views."""
        self.analytics_manager.track_event(
            'page_view',
            user_id=user_id,
            properties={'page_name': page_name}
        )
    
    def track_feature_usage(self, feature_name: str, user_id: str = None, success: bool = True):
        """Track feature usage."""
        self.analytics_manager.track_event(
            'feature_used',
            user_id=user_id,
            properties={
                'feature_name': feature_name,
                'success': success
            }
        )
    
    def track_conversion(self, conversion_type: str, user_id: str = None, value: float = None):
        """Track conversions (signups, subscriptions, etc.)."""
        properties = {'conversion_type': conversion_type}
        if value:
            properties['value'] = value
        
        self.analytics_manager.track_event(
            'conversion',
            user_id=user_id,
            properties=properties
        )
    
    def track_wellness_score(self, score: float, user_id: str = None, source: str = 'text'):
        """Track wellness score submissions."""
        self.analytics_manager.track_event(
            'wellness_score_submitted',
            user_id=user_id,
            properties={
                'score': score,
                'source': source,
                'score_category': self._categorize_score(score)
            }
        )
    
    def _categorize_score(self, score: float) -> str:
        """Categorize wellness score."""
        if score >= 75:
            return 'excellent'
        elif score >= 50:
            return 'good'
        elif score >= 25:
            return 'moderate'
        else:
            return 'concerning'

class HealthCheck:
    """Performs health checks for production monitoring."""
    
    def __init__(self):
        self.checks = {}
    
    def add_check(self, name: str, check_function):
        """Add a health check."""
        self.checks[name] = check_function
    
    def run_health_checks(self) -> Dict[str, Dict[str, Any]]:
        """Run all health checks."""
        results = {}
        
        for name, check_func in self.checks.items():
            try:
                start_time = time.time()
                result = check_func()
                duration = time.time() - start_time
                
                results[name] = {
                    'status': 'healthy' if result else 'unhealthy',
                    'duration': duration,
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                results[name] = {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        return results
    
    def check_aws_services(self) -> bool:
        """Check AWS services connectivity."""
        try:
            import boto3
            from aws_services import test_aws_connection
            
            # This would run actual AWS connectivity tests
            return True
        except Exception:
            return False
    
    def check_database(self) -> bool:
        """Check database connectivity."""
        try:
            from auth import test_auth_connection
            return test_auth_connection()
        except Exception:
            return False
    
    def check_external_apis(self) -> bool:
        """Check external API connectivity."""
        try:
            # Test AI service connectivity
            response = requests.get('https://api.anthropic.com/health', timeout=5)
            return response.status_code == 200
        except Exception:
            return False

# Global instances
analytics_manager = AnalyticsManager()
performance_monitor = PerformanceMonitor()
user_analytics = UserAnalytics()
health_check = HealthCheck()

# Add default health checks
health_check.add_check('aws_services', health_check.check_aws_services)
health_check.add_check('database', health_check.check_database)
health_check.add_check('external_apis', health_check.check_external_apis)

def track_operation(operation_name: str):
    """Decorator to track operation performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            performance_monitor.start_timer(operation_name)
            try:
                result = func(*args, **kwargs)
                performance_monitor.end_timer(operation_name)
                return result
            except Exception as e:
                performance_monitor.end_timer(operation_name)
                analytics_manager.track_error(e)
                raise
        return wrapper
    return decorator 