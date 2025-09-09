"""
Grab Cabs Customer Driver & Vehicle Issues Handler
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


class DriverVehicleIssuesHandler:
    """Customer-focused driver and vehicle issues management with real AI"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_cabs"
        self.actor = "customer"
        self.handler_type = "driver_vehicle_issues_handler"
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_unsafe_driving_behavior(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle unsafe driving or behavior (rash driving, under influence) complaints - TEXT ONLY"""
        logger.info(f"Processing unsafe driving/behavior complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_unsafe_driving_behavior",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_vehicle_problems(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle vehicle problems (breakdown, condition) complaints - TEXT ONLY"""
        logger.info(f"Processing vehicle problems complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_vehicle_problems",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_accidents_during_ride(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle accidents during ride complaints - TEXT ONLY"""
        logger.info(f"Processing accidents during ride complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_accidents_during_ride",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )