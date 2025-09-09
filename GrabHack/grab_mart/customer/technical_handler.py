"""
Grab Mart Customer Technical Handler
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


class TechnicalHandler:
    """Customer-focused technical issues management with real AI"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_mart"
        self.actor = "customer"
        self.handler_type = "technical_handler"
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_auto_cancellation(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle order auto-cancelled without reason - TEXT ONLY"""
        logger.info(f"Processing auto cancellation complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_auto_cancellation",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_delivery_status_error(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle app shows delivered but not received - TEXT ONLY"""
        logger.info(f"Processing delivery status error complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_delivery_status_error",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_tracking_status_error(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle wrong tracking status - TEXT ONLY"""
        logger.info(f"Processing tracking status error complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_tracking_status_error",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_coupon_offers_error(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle coupons/offers not applied correctly - TEXT ONLY"""
        logger.info(f"Processing coupon offers error complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_coupon_offers_error",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )