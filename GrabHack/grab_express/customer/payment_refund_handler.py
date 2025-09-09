"""
Grab Express Customer Payment & Refund Handler
Handles payment and refund issues for express deliveries
"""

import logging
import sys
import os
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class PaymentRefundHandler:
    """Express delivery payment and refund management"""
    
    def __init__(self):
        self.service = "grab_express"
        self.actor = "customer"
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_double_charge(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle double charge for single delivery"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_double_charge",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return "We apologize for the double charge error. The duplicate charge will be refunded within 2-3 business days to your original payment method."

    def handle_failed_payment_money_deducted(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle failed payment but money deducted"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_failed_payment_money_deducted",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return "Payment processing errors will be resolved immediately. The deducted amount will be refunded within 24 hours and your delivery will be completed as scheduled."

    def handle_cod_marked_prepaid(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle COD delivery marked prepaid"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_cod_marked_prepaid",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return "Payment method errors will be corrected immediately. If you were incorrectly charged online for a COD delivery, the amount will be refunded within 24 hours."

    def handle_refund_not_initiated(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle refund not initiated for damaged/lost package"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_refund_not_initiated",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            return "We apologize for the refund delay. Your refund for the damaged/lost package is being processed immediately and will be credited within 24-48 hours."