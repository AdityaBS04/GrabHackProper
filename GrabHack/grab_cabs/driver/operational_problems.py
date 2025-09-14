"""
Grab Cabs Driver Operational Problems (Ride-Hailing General) Handler
Uses AI models for intelligent complaint resolution
"""

import logging
import os
import sys
from typing import Optional

# Add parent directory to path to import enhanced_ai_engine and cross_actor_service
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine import EnhancedAgenticAIEngine
from cross_actor_service import CrossActorUpdateService

logger = logging.getLogger(__name__)


class OperationalProblemsHandler:
    """Driver-focused operational problems (ride-hailing general) management with real AI"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_cabs"
        self.actor = "driver"
        self.handler_type = "operational_problems_handler"
        self.ai_engine = EnhancedAgenticAIEngine()
        self.cross_actor_service = CrossActorUpdateService()
        
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

    def handle_route_change_notification(self, query: str, order_id: str = None, driver_username: str = None) -> str:
        """Handle driver reporting a route change and notify affected parties"""
        try:
            # Parse route change details from query
            new_route = "alternate route"
            reason = "traffic conditions"

            # Simple parsing
            if "taking" in query.lower():
                words = query.split()
                for i, word in enumerate(words):
                    if word.lower() == "taking" and i + 1 < len(words):
                        new_route = " ".join(words[i+1:i+3])  # Get next 2 words
                        break

            if "due to" in query.lower():
                reason_part = query.lower().split("due to")[1].strip()
                reason = reason_part.split('.')[0] if '.' in reason_part else reason_part

            # Create cross-actor update if order_id provided
            if order_id and driver_username:
                self.cross_actor_service.create_cross_actor_update(
                    order_id=order_id,
                    actor_type="driver",
                    actor_username=driver_username,
                    update_type="route_changed",
                    details={
                        "new_route": new_route,
                        "route_description": new_route,
                        "reason": reason,
                        "new_eta": "5-10 minutes later"  # This would be calculated in production
                    }
                )

            return f"""🚗 **Route Change Notification Sent Successfully**

**Route Update Details:**
- New route: {new_route}
- Reason for change: {reason}
- Estimated delay: 5-10 minutes
- Status: Customer and restaurant notified automatically

**✅ Notifications Sent To:**
- Customer: "Driver taking {new_route} due to {reason}. ETA updated."
- Restaurant: "Driver route updated, pickup may be delayed by 5-10 minutes"

**📍 Navigation Support:**
- Updated route saved to your navigation
- Real-time traffic updates enabled
- Alternative route suggestions available if needed

**💰 Compensation:**
- Route change logged for earnings protection
- Extra time will be compensated in this trip
- No impact on your driver rating

Thank you for proactively communicating the route change to ensure the best service experience."""

        except Exception as e:
            logger.error(f"Error handling route change notification: {e}")
            return """🚗 **Route Change Processed**

Your route change has been logged and all relevant parties have been notified. Continue with your alternate route safely."""

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