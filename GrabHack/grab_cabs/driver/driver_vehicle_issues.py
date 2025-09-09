"""
Grab Cabs Driver Vehicle Issues Handler
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
    """Driver-focused vehicle issues management with real AI"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_cabs"
        self.actor = "driver"
        self.handler_type = "driver_vehicle_issues_handler"
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_vehicle_breakdown_during_ride(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle vehicle breakdown during ride complaints - TEXT ONLY"""
        logger.info(f"Processing vehicle breakdown during ride complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_vehicle_breakdown_during_ride",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_passenger_damage_coverage(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle passenger-related damages to vehicle coverage complaints - TEXT ONLY"""
        logger.info(f"Processing passenger damage coverage complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_passenger_damage_coverage",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_insurance_fuel_maintenance_support(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle insurance/fuel/vehicle maintenance support complaints - TEXT ONLY"""
        logger.info(f"Processing insurance/fuel/maintenance support complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_insurance_fuel_maintenance_support",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )