"""
Grab Express Customer Express Service Handler
Handles express delivery urgency and speed requirements
"""

import logging
import sys
import os
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class ExpressServiceHandler:
    """Express delivery urgency and speed management"""
    
    def __init__(self):
        self.service = "grab_express"
        self.actor = "customer"
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_urgency_vehicle_conflict(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle same day delivery not available for bike"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_urgency_vehicle_conflict",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return """For urgent same-day delivery requirements, we are upgrading your delivery to a faster vehicle (car/motorbike) at no additional cost.
            
Your express delivery will be prioritized and completed within the promised timeframe. We apologize for any initial delays."""

    def handle_speed_requirements(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle urgent delivery requires faster vehicle type"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_speed_requirements",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return """Urgent delivery requests require speed optimization. We are assigning a priority delivery partner with faster vehicle capability.
            
Your delivery will be expedited and completed within 1-2 hours. Express service guarantees will be honored with compensation for any delays."""