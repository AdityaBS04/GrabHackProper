"""
Grab Cabs Driver Operational Issues Handler
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


class OperationalIssuesHandler:
    """Driver-focused operational issues management with real AI"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_cabs"
        self.actor = "driver"
        self.handler_type = "operational_issues_handler"
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_passenger_cancellation_after_arrival(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle passengers cancelling after driver reaches pickup point complaints - TEXT ONLY"""
        logger.info(f"Processing passenger cancellation after arrival complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_passenger_cancellation_after_arrival",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_wrong_pickup_drop_details(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle wrong pickup/drop details from app complaints - TEXT ONLY"""
        logger.info(f"Processing wrong pickup/drop details complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_wrong_pickup_drop_details",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_long_waiting_time_compensation(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle compensation for long waiting times at pickup complaints - TEXT ONLY"""
        logger.info(f"Processing long waiting time compensation complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_long_waiting_time_compensation",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )