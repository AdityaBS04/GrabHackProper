"""
Grab Cabs Customer Operational Problems (Ride-Hailing General) Handler
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
    """Customer-focused operational problems (ride-hailing general) management with real AI"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_cabs"
        self.actor = "customer"
        self.handler_type = "operational_problems_handler"
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_driver_availability(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle driver availability (peak hours, remote areas) complaints - TEXT ONLY"""
        logger.info(f"Processing driver availability complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_driver_availability",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_driver_cancellations(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle driver cancellations (personal reasons, chasing fares) complaints - TEXT ONLY"""
        logger.info(f"Processing driver cancellations complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_driver_cancellations",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_late_arrivals_no_shows(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle late arrivals & no-shows complaints - TEXT ONLY"""
        logger.info(f"Processing late arrivals/no-shows complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_late_arrivals_no_shows",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )