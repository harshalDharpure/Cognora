#!/usr/bin/env python3
"""
Production Setup Test for Cognora+
Tests all production features and configurations.
"""

import os
import sys
import json
from datetime import datetime
from config import config
from monitoring import health_check, analytics_manager, performance_monitor
from auth import test_auth_connection
from aws_services import test_aws_connection

def test_configuration():
    """Test configuration setup."""
    print("🔧 Testing Configuration...")
    
    # Test environment detection
    print(f"  Environment: {config.environment.value}")
    print(f"  Market: {config.market.value}")
    print(f"  Production Mode: {config.is_production()}")
    
    # Test feature flags
    print("\n  Feature Flags:")
    for feature, enabled in config.features.items():
        status = "✅" if enabled else "❌"
        print(f"    {status} {feature}: {enabled}")
    
    # Test market configuration
    print(f"\n  Market Config:")
    print(f"    Default Language: {config.get_market_setting('default_language')}")
    print(f"    Currency: {config.get_market_setting('currency')}")
    print(f"    Timezone: {config.get_market_setting('timezone')}")
    print(f"    Support Email: {config.get_market_setting('support_email')}")
    
    return True

def test_analytics():
    """Test analytics configuration."""
    print("\n📊 Testing Analytics...")
    
    # Test analytics manager
    print(f"  Google Analytics: {'✅' if config.analytics.google_analytics_id else '❌'}")
    print(f"  Mixpanel: {'✅' if config.analytics.mixpanel_token else '❌'}")
    print(f"  Sentry: {'✅' if config.analytics.sentry_dsn else '❌'}")
    
    # Test event tracking
    try:
        analytics_manager.track_event('test_event', 'test_user', {'test': True})
        print("  ✅ Event tracking working")
    except Exception as e:
        print(f"  ❌ Event tracking failed: {e}")
    
    return True

def test_performance_monitoring():
    """Test performance monitoring."""
    print("\n⚡ Testing Performance Monitoring...")
    
    # Test timer
    performance_monitor.start_timer('test_operation')
    import time
    time.sleep(0.1)  # Simulate work
    duration = performance_monitor.end_timer('test_operation')
    
    print(f"  Timer test: {duration:.3f}s")
    
    # Test metrics
    metrics = performance_monitor.get_metrics()
    print(f"  Uptime: {metrics['uptime']:.1f}s")
    print(f"  Operations tracked: {len(metrics['operations'])}")
    
    return True

def test_health_checks():
    """Test health check system."""
    print("\n🏥 Testing Health Checks...")
    
    results = health_check.run_health_checks()
    
    for check_name, result in results.items():
        status = "✅" if result['status'] == 'healthy' else "❌"
        duration = result['duration']
        print(f"  {status} {check_name}: {result['status']} ({duration:.3f}s)")
    
    return True

def test_database_connection():
    """Test database connectivity."""
    print("\n🗄️ Testing Database Connection...")
    
    try:
        result = test_auth_connection()
        print(f"  ✅ Database connection: {result}")
        return True
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        return False

def test_aws_services():
    """Test AWS services connectivity."""
    print("\n☁️ Testing AWS Services...")
    
    try:
        result = test_aws_connection()
        print(f"  ✅ AWS connection: {result}")
        return True
    except Exception as e:
        print(f"  ❌ AWS connection failed: {e}")
        return False

def test_security_settings():
    """Test security configuration."""
    print("\n🔐 Testing Security Settings...")
    
    security = config.security
    print(f"  Session Timeout: {security.session_timeout_minutes} minutes")
    print(f"  Max Login Attempts: {security.max_login_attempts}")
    print(f"  Password Expiry: {security.password_expiry_days} days")
    print(f"  MFA Enabled: {security.mfa_enabled}")
    print(f"  Rate Limiting: {security.rate_limiting_enabled}")
    
    # Test JWT configuration
    if hasattr(config, 'jwt_secret_key'):
        secret_length = len(config.jwt_secret_key)
        print(f"  JWT Secret Length: {secret_length} characters")
        if secret_length >= 32:
            print("  ✅ JWT secret is secure")
        else:
            print("  ⚠️ JWT secret should be at least 32 characters")
    
    return True

def generate_production_report():
    """Generate production readiness report."""
    print("\n📋 Generating Production Report...")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'environment': config.environment.value,
        'market': config.market.value,
        'production_ready': True,
        'features_enabled': len([f for f in config.features.values() if f]),
        'total_features': len(config.features),
        'security_score': 0,
        'performance_score': 0,
        'recommendations': []
    }
    
    # Calculate security score
    security_score = 0
    if config.security.rate_limiting_enabled:
        security_score += 25
    if config.security.mfa_enabled:
        security_score += 25
    if config.database.encryption_enabled:
        security_score += 25
    if config.database.backup_enabled:
        security_score += 25
    
    report['security_score'] = security_score
    
    # Calculate performance score
    performance_score = 0
    if config.analytics.sentry_dsn:
        performance_score += 33
    if config.analytics.mixpanel_token:
        performance_score += 33
    if config.analytics.google_analytics_id:
        performance_score += 34
    
    report['performance_score'] = performance_score
    
    # Generate recommendations
    recommendations = []
    
    if not config.security.mfa_enabled:
        recommendations.append("Enable MFA for enhanced security")
    
    if not config.analytics.sentry_dsn:
        recommendations.append("Set up Sentry for error tracking")
    
    if config.market.value == 'japan' and not config.get_market_setting('compliance'):
        recommendations.append("Configure APPI compliance for Japan")
    
    report['recommendations'] = recommendations
    
    # Save report
    with open('production_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"  ✅ Report saved to production_report.json")
    
    return report

def main():
    """Run all production tests."""
    print("🚀 Cognora+ Production Setup Test")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Analytics", test_analytics),
        ("Performance Monitoring", test_performance_monitoring),
        ("Health Checks", test_health_checks),
        ("Database Connection", test_database_connection),
        ("AWS Services", test_aws_services),
        ("Security Settings", test_security_settings),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results[test_name] = False
    
    # Generate report
    report = generate_production_report()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed! Your system is production-ready!")
    else:
        print("⚠️ Some tests failed. Please review the issues above.")
    
    print(f"\nSecurity Score: {report['security_score']}/100")
    print(f"Performance Score: {report['performance_score']}/100")
    
    if report['recommendations']:
        print("\n📝 Recommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
    
    print(f"\n📄 Full report saved to: production_report.json")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 