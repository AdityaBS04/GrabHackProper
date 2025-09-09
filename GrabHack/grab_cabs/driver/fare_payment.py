"""
Grab Cabs Driver Fare & Payment Handler
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


class FarePaymentHandler:
    """Driver-focused fare and payment management with real AI"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_cabs"
        self.actor = "driver"
        self.handler_type = "fare_payment_handler"
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_incorrect_fare_calculation(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle incorrect fare calculation complaints - TEXT ONLY"""
        logger.info(f"Processing incorrect fare calculation complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_incorrect_fare_calculation",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_payout_not_received(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle payout not received for recent rides complaints - TEXT ONLY"""
        logger.info(f"Processing payout not received complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_payout_not_received",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_high_commission_rates(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle high commission rates complaints - TEXT ONLY"""
        logger.info(f"Processing high commission rates complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_high_commission_rates",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )