"""
Grab Cabs Customer Experience Handler
Uses AI models for intelligent complaint resolution
"""

import logging
import os
import sys
from typing import Optional

# Add parent directory to path to import enhanced_ai_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class CustomerExperienceHandler:
    """Customer-focused experience management with real AI"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_cabs"
        self.actor = "customer"
        self.handler_type = "customer_experience_handler"
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_app_booking_issues(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle app or booking issues (payment, tracking, malfunction) complaints - TEXT ONLY"""
        logger.info(f"Processing app/booking issues complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_app_booking_issues",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_cancellation_refund_policy_complications(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle cancellation/refund policy complications complaints - TEXT ONLY"""
        logger.info(f"Processing cancellation/refund policy complications complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_cancellation_refund_policy_complications",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_airport_booking_problems(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle airport booking problems (missed flights, wrong sync) complaints - TEXT ONLY"""
        logger.info(f"Processing airport booking problems complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_airport_booking_problems",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )