"""
Grab Food Customer Order Quality Handler
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


class OrderQualityHandler:
    """Customer-focused order accuracy and quality management with real AI"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_food"
        self.actor = "customer"
        self.handler_type = "order_quality_handler"
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_missing_items(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle missing items - REQUIRES IMAGE for verification"""
        logger.info(f"Processing missing items complaint: {query[:100]}...")
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_missing_items",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            logger.info(f"AI response generated successfully")
            return result
        except Exception as e:
            logger.error(f"Error in handle_missing_items: {e}")
            return f"🚨 Processing Error: {str(e)}"

    def handle_wrong_item(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle wrong item delivered - REQUIRES IMAGE for verification"""
        logger.info(f"Processing wrong item complaint: {query[:100]}...")
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_wrong_item",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            logger.info(f"AI response generated successfully")
            return result
        except Exception as e:
            logger.error(f"Error in handle_wrong_item: {e}")
            return f"🚨 Processing Error: {str(e)}"

    def handle_quality_issues(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle expired/damaged/poor quality items - REQUIRES IMAGE for assessment"""
        logger.info(f"Processing quality issues complaint: {query[:100]}...")
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_quality_issues",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            logger.info(f"AI response generated successfully")
            return result
        except Exception as e:
            logger.error(f"Error in handle_quality_issues: {e}")
            return f"🚨 Processing Error: {str(e)}"

    def handle_substitution_issues(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle substituted item not acceptable - TEXT ONLY (no image required)"""
        logger.info(f"Processing substitution issues complaint: {query[:100]}...")
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_substitution_issues",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            logger.info(f"AI response generated successfully")
            return result
        except Exception as e:
            logger.error(f"Error in handle_substitution_issues: {e}")
            return f"🚨 Processing Error: {str(e)}"

    def handle_quantity_mismatch(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle quantity mismatch - REQUIRES IMAGE to verify portions"""
        logger.info(f"Processing quantity mismatch complaint: {query[:100]}...")
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_quantity_mismatch",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            logger.info(f"AI response generated successfully")
            return result
        except Exception as e:
            logger.error(f"Error in handle_quantity_mismatch: {e}")
            return f"🚨 Processing Error: {str(e)}"