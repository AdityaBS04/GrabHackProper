"""
Grab Express Customer Technical Handler
Handles technical issues for express delivery service
"""

import logging
import sys
import os
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class TechnicalHandler:
    """Express delivery technical issues management"""
    
    def __init__(self):
        self.service = "grab_express"
        self.actor = "customer"
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_auto_cancellation(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle delivery auto-cancelled without reason"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_auto_cancellation",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return "System auto-cancellations are being investigated. We will rebook your delivery immediately and provide compensation for the inconvenience."

    def handle_delivery_status_error(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle app shows delivered but not received"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_delivery_status_error",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return "Delivery status discrepancies are being resolved. We are verifying the actual delivery status and will arrange redelivery if needed."

    def handle_tracking_status_error(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle wrong tracking status"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_tracking_status_error",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return "Tracking system errors are being fixed. We will provide accurate real-time updates and ensure proper delivery completion."

    def handle_coupon_offers_error(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle coupons/offers not applied correctly"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_coupon_offers_error",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return "Promotional offer errors will be corrected immediately. The discount will be applied retroactively and credited to your account within 24 hours."