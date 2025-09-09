"""
Grab Cabs Driver Customer Experience Handler (Driver's POV)
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
    """Driver-focused customer experience management with real AI (Driver's POV)"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_cabs"
        self.actor = "driver"
        self.handler_type = "customer_experience_handler"
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_passenger_harassment_complaint(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle passenger harassment/rude behavior complaints - TEXT ONLY"""
        logger.info(f"Processing passenger harassment complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_passenger_harassment_complaint",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_false_complaint_rating_reduction(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle false complaints that reduced rating complaints - TEXT ONLY"""
        logger.info(f"Processing false complaint rating reduction complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_false_complaint_rating_reduction",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_unresolved_passenger_disputes(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle escalation of unresolved disputes with passengers complaints - TEXT ONLY"""
        logger.info(f"Processing unresolved passenger disputes complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_unresolved_passenger_disputes",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )