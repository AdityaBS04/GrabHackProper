"""
Grab Mart Customer Payment Refund Handler
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


class PaymentRefundHandler:
    """Customer-focused payment and refund management with real AI"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_mart"
        self.actor = "customer"
        self.handler_type = "payment_refund_handler"
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_double_charge(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle double charge for single order - TEXT ONLY"""
        logger.info(f"Processing double charge complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_double_charge",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_failed_payment_money_deducted(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle failed payment but money deducted - TEXT ONLY"""
        logger.info(f"Processing failed payment money deducted complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_failed_payment_money_deducted",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_cod_marked_prepaid(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle COD order marked prepaid - TEXT ONLY"""
        logger.info(f"Processing COD marked prepaid complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_cod_marked_prepaid",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_refund_not_initiated(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle refund not initiated for missing/damaged items - TEXT ONLY"""
        logger.info(f"Processing refund not initiated complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_refund_not_initiated",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )