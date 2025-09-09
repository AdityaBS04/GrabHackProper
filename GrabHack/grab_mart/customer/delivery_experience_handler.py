"""
Grab Mart Customer Delivery Experience Handler
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


class DeliveryExperienceHandler:
    """Customer-focused delivery experience management with real AI"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_mart"
        self.actor = "customer"
        self.handler_type = "delivery_experience_handler"
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_delivery_delay(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle delay beyond promised time - TEXT ONLY"""
        logger.info(f"Processing delivery delay complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_delivery_delay",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_partial_delivery(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle partial order delivered - REQUIRES IMAGE"""
        logger.info(f"Processing partial delivery complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_partial_delivery",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_temperature_issues(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle cold/frozen items melted or leaked - REQUIRES IMAGE"""
        logger.info(f"Processing temperature issues complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_temperature_issues",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_package_tampering(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle package tampered or unsealed - REQUIRES IMAGE"""
        logger.info(f"Processing package tampering complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_package_tampering",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_multiple_deliveries(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle multiple deliveries for same order - TEXT ONLY"""
        logger.info(f"Processing multiple deliveries complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_multiple_deliveries",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )