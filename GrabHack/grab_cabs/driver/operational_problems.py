"""
Grab Cabs Driver Operational Problems (Ride-Hailing General) Handler
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


class OperationalProblemsHandler:
    """Driver-focused operational problems (ride-hailing general) management with real AI"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_cabs"
        self.actor = "driver"
        self.handler_type = "operational_problems_handler"
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_no_rides_during_peak_hours(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle not receiving rides during peak hours complaints - TEXT ONLY"""
        logger.info(f"Processing no rides during peak hours complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_no_rides_during_peak_hours",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_unfair_ride_allocation(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle unfair ride allocation complaints - TEXT ONLY"""
        logger.info(f"Processing unfair ride allocation complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_unfair_ride_allocation",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_incorrect_navigation_route(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle incorrect navigation route suggestions complaints - TEXT ONLY"""
        logger.info(f"Processing incorrect navigation route complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_incorrect_navigation_route",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )