#!/usr/bin/env python3
"""
Billing module - Disabled for production without subscription
This module is kept for future reference but billing features are disabled.
"""

import streamlit as st

def show_billing_disabled_message():
    """Show message that billing is disabled."""
    st.info("💳 Billing features are currently disabled. The application is free to use.")

# Placeholder functions for compatibility
class BillingManager:
    """Placeholder billing manager."""
    def __init__(self):
        pass
    
    def get_plan_features(self, plan_id: str):
        return []
    
    def get_plan_limits(self, plan_id: str):
        return {}
    
    def check_usage_limit(self, user_id: str, plan_id: str, usage_type: str, current_usage: int):
        return True  # No limits when billing is disabled

class SubscriptionUI:
    """Placeholder subscription UI."""
    def __init__(self):
        pass
    
    def show_pricing_plans(self, user_id: str = None):
        show_billing_disabled_message()
    
    def show_subscription_status(self, user_id: str):
        show_billing_disabled_message()
    
    def show_usage_metrics(self, user_id: str):
        show_billing_disabled_message()

# Global instances (placeholders)
billing_manager = BillingManager()
subscription_ui = SubscriptionUI() 