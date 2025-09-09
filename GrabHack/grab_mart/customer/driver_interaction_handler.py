"""
Grab Mart Customer Driver Interaction Handler
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


class DriverInteractionHandler:
    """Customer-focused driver interaction management with real AI"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_mart"
        self.actor = "customer"
        self.handler_type = "driver_interaction_handler"
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_rude_behavior(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle rude behavior from delivery partner - TEXT ONLY"""
        logger.info(f"Processing rude behavior complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_rude_behavior",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_location_difficulty(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle driver unable to find address, keeps calling - TEXT ONLY"""
        logger.info(f"Processing location difficulty complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_location_difficulty",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_payment_manipulation(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle driver asks for extra money (COD manipulation) - TEXT ONLY"""
        logger.info(f"Processing payment manipulation complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_payment_manipulation",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_false_delivery(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle driver marks delivered but no package received - TEXT ONLY"""
        logger.info(f"Processing false delivery complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_false_delivery",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )