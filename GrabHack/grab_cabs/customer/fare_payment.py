"""
Grab Cabs Customer Fare & Payment Handler
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
    """Customer-focused fare and payment management with real AI"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_cabs"
        self.actor = "customer"
        self.handler_type = "fare_payment_handler"
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_incorrect_multiple_fare_charged(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle incorrect or multiple fare charged complaints - TEXT ONLY"""
        logger.info(f"Processing incorrect/multiple fare charged complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_incorrect_multiple_fare_charged",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_double_payment_cash_online(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle double payment (cash + online) complaints - TEXT ONLY"""
        logger.info(f"Processing double payment cash+online complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_double_payment_cash_online",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_refund_adjustment_issues(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle refund and adjustment issues - TEXT ONLY"""
        logger.info(f"Processing refund/adjustment issues complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_refund_adjustment_issues",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )