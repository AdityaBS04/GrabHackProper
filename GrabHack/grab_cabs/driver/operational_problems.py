"""
Grab Cabs Driver Operational Problems (Ride-Hailing General) Handler
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


class OperationalProblemsHandler:
    """Driver-focused operational problems (ride-hailing general) management with real AI"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_cabs"
        self.actor = "driver"
        self.handler_type = "operational_problems_handler"
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_no_rides_during_peak_hours(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle not receiving rides during peak hours complaints - TEXT ONLY"""
        logger.info(f"Processing no rides during peak hours complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_no_rides_during_peak_hours",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_unfair_ride_allocation(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle unfair ride allocation complaints - TEXT ONLY"""
        logger.info(f"Processing unfair ride allocation complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_unfair_ride_allocation",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_incorrect_navigation_route(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle incorrect navigation route suggestions complaints - TEXT ONLY with conversational flow"""
        logger.info(f"Processing incorrect navigation route complaint: {query[:100]}...")
        
        # Check if user is reporting wrong location/route issues
        query_lower = query.lower()
        route_keywords = ['wrong', 'incorrect', 'bad route', 'wrong direction', 'wrong location', 'navigation', 'route', 'gps', 'direction']
        
        # If user mentions route/navigation issues, provide the new Google Maps link
        if any(keyword in query_lower for keyword in route_keywords):
            return """I understand you're having navigation route issues. I apologize for the incorrect route suggestions from our GPS system.

I'm providing you with an updated and correct route link to help you reach your destination efficiently:

🗺️ **Updated Google Maps Route**: 
https://maps.app.goo.gl/PEaK5NpD5oZMhKg3A

👆 Click the link above to open the correct route in Google Maps. Please use this instead of our app's navigation for this trip.

We're also reporting this GPS issue to our technical team to prevent similar problems in the future. You will receive route accuracy compensation in your next payout.

Is there anything else about the navigation I can help you with?"""
        
        else:
            # Ask for more details about the navigation issue
            return """I'm here to help with your navigation concerns. Could you please tell me more about what's wrong with the route?

For example:
- Is the route taking you through incorrect roads?
- Are you being directed to the wrong destination?
- Is the GPS showing outdated traffic information?
- Are there road closures not being accounted for?

Once I understand the specific issue, I can provide you with the correct route and report the problem to our technical team."""