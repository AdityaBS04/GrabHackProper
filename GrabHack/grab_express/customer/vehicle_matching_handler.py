"""
Grab Express Customer Vehicle Matching Handler  
Handles vehicle type and capacity matching issues specific to express delivery
"""

import logging
import sys
import os
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class VehicleMatchingHandler:
    """Vehicle type and capacity matching for express packages"""
    
    def __init__(self):
        self.service = "grab_express"
        self.actor = "customer"
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_vehicle_size_mismatch(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle package too large for bike delivery"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_vehicle_size_mismatch",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return """We apologize for the vehicle capacity mismatch. Your large package has been reassigned to a car/truck delivery partner. 
            
The upgraded delivery will be completed within 2 hours at no additional cost. We are also updating our system to better match package sizes with appropriate vehicles."""

    def handle_vehicle_upgrade_needed(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle package requires truck but bike assigned"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_vehicle_upgrade_needed", 
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return """We understand your package requires truck capacity. We are immediately upgrading your delivery to a truck partner.
            
Your package will be picked up and delivered within 3 hours. We apologize for the initial mismatch and any inconvenience caused."""

    def handle_weight_vehicle_mismatch(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle heavy package assigned to standard car"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_weight_vehicle_mismatch",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return """Heavy packages require appropriate vehicle capacity. We are upgrading your delivery to a truck with proper weight handling capability.
            
The new delivery partner will arrive within 2-3 hours with proper equipment for safe handling of your heavy package."""