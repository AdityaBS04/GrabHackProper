"""
Grab Express Customer Order Quality Handler
Handles package quality and accuracy issues for express deliveries
"""

import logging
import os
import sys
from typing import Optional

# Add parent directory to path to import enhanced_ai_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class OrderQualityHandler:
    """Express delivery package quality and accuracy management"""
    
    def __init__(self):
        self.service = "grab_express"
        self.actor = "customer"
        self.handler_type = "order_quality_handler"
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_missing_items(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle missing packages in express delivery"""
        logger.info(f"Processing missing package complaint: {query[:100]}...")
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_missing_items",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in handle_missing_items: {e}")
            return "We apologize for the missing package. We are investigating this issue and will arrange immediate replacement delivery."

    def handle_wrong_item(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle wrong package delivered"""
        logger.info(f"Processing wrong package complaint: {query[:100]}...")
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_wrong_item",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in handle_wrong_item: {e}")
            return "We sincerely apologize for delivering the wrong package. We will collect the incorrect package and deliver the correct one within 2 hours."

    def handle_quality_issues(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle damaged packages during transit"""
        logger.info(f"Processing package damage complaint: {query[:100]}...")
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_quality_issues",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in handle_quality_issues: {e}")
            return "We apologize for the package damage. Please share photos of the damaged items for immediate refund processing."

    def handle_substitution_issues(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle package contents incomplete"""
        logger.info(f"Processing incomplete package complaint: {query[:100]}...")
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_substitution_issues",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in handle_substitution_issues: {e}")
            return "We understand your concern about incomplete package contents. We will verify with the sender and provide appropriate compensation."

    def handle_quantity_mismatch(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle package size mismatch"""
        logger.info(f"Processing package size mismatch complaint: {query[:100]}...")
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_quantity_mismatch",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            return result
        except Exception as e:
            logger.error(f"Error in handle_quantity_mismatch: {e}")
            return "We apologize for the package size discrepancy. We will coordinate with the sender to resolve this issue and ensure proper compensation."