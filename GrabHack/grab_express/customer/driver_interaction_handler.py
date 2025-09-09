"""
Grab Express Customer Driver Interaction Handler
Handles delivery partner interaction issues for express deliveries
"""

import logging
import sys
import os
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class DriverInteractionHandler:
    """Express delivery partner interaction management"""
    
    def __init__(self):
        self.service = "grab_express"
        self.actor = "customer"
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_rude_behavior(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle rude behavior from delivery partner"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_rude_behavior",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return "We take delivery partner behavior very seriously. We are investigating this incident and taking appropriate action to ensure professional service standards."

    def handle_location_difficulty(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle delivery partner unable to find address"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_location_difficulty",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return "We understand the address location difficulty. We are providing better navigation support and will ensure smooth delivery completion."

    def handle_payment_manipulation(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle delivery partner asks for extra money"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_payment_manipulation",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return "Payment manipulation is strictly prohibited. We are investigating immediately and will take stern action against the delivery partner. Any extra charges will be refunded."

    def handle_false_delivery(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle delivery partner marks delivered but no package received"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_false_delivery",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return "False delivery marking is a serious violation. We are investigating with GPS tracking data and will arrange immediate replacement delivery with full refund if necessary."