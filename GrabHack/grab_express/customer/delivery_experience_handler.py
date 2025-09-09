"""
Grab Express Customer Delivery Experience Handler
Handles express delivery experience and timing issues
"""

import logging
import sys
import os
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class DeliveryExperienceHandler:
    """Express delivery experience management"""
    
    def __init__(self):
        self.service = "grab_express"
        self.actor = "customer" 
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_delivery_delay(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle express delivery delays"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_delivery_delay",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return "We apologize for the express delivery delay. We are providing compensation and priority handling for your future orders."

    def handle_partial_delivery(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle package not delivered to correct recipient"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_partial_delivery",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return "We are investigating the delivery verification issue. Our team will ensure your package is delivered to the correct recipient."

    def handle_temperature_issues(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle package damaged or opened during transit"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_temperature_issues",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return "We take package integrity very seriously. We are processing a refund and implementing additional security measures."

    def handle_package_tampering(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle package tampered or unsealed"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_package_tampering",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return "Package tampering is a serious concern. We are investigating immediately and will provide full compensation for any losses."

    def handle_multiple_deliveries(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle multiple delivery attempts for same package"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_multiple_deliveries",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return "We understand the inconvenience of multiple delivery attempts. We are optimizing our delivery process to complete in single attempt."