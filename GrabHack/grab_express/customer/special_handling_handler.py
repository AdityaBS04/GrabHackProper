"""
Grab Express Customer Special Handling Handler
Handles special package requirements (fragile, temperature-sensitive, bulk)
"""

import logging
import sys
import os
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class SpecialHandlingHandler:
    """Special package handling requirements management"""
    
    def __init__(self):
        self.service = "grab_express"
        self.actor = "customer"
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_fragile_vehicle_requirements(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle fragile items need car instead of bike"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_fragile_vehicle_requirements",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return """Fragile items require special care and appropriate vehicle selection. We are upgrading your delivery to a car with proper cushioning and careful handling protocols.
            
Your fragile package will be delivered safely within 2 hours. If any damage occurred, full compensation will be provided immediately."""

    def handle_temperature_vehicle_requirements(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle temperature sensitive delivery needs refrigerated truck"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_temperature_vehicle_requirements",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return """Temperature-sensitive packages require refrigerated transport. We are arranging a specialized refrigerated vehicle for your delivery.
            
Cold chain integrity will be maintained throughout delivery. Any temperature compromise will result in immediate replacement or full refund."""

    def handle_bulk_delivery_requirements(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle bulk delivery requires truck capacity"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_bulk_delivery_requirements",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return """Bulk deliveries require adequate vehicle capacity. We are assigning a truck with proper loading equipment for your bulk package delivery.
            
Professional loading/unloading assistance will be provided. Delivery will be completed within 3-4 hours with proper handling."""