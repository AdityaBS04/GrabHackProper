"""
Grab Cabs Customer Operational Issues Handler
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


class OperationalIssuesHandler:
    """Customer-focused operational issues management with real AI"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_cabs"
        self.actor = "customer"
        self.handler_type = "operational_issues_handler"
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_pickup_drop_errors(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle pickup & drop errors (wrong location, delayed pickup) complaints - TEXT ONLY"""
        logger.info(f"Processing pickup/drop errors complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_pickup_drop_errors",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_route_problems(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle route problems (wrong route, rerouting issues) complaints - TEXT ONLY"""
        logger.info(f"Processing route problems complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_route_problems",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_communication_issues(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle communication issues (driver not answering, flight details mismanaged) complaints - TEXT ONLY"""
        logger.info(f"Processing communication issues complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_communication_issues",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )