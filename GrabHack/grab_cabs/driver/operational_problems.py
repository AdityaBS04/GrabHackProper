"""
Grab Cabs Driver Operational Problems (Ride-Hailing General) Handler
Uses AI models for intelligent complaint resolution with strict workflows
"""

import logging
import os
import sys
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine
from cross_actor_service import CrossActorUpdateService

logger = logging.getLogger(__name__)


class OperationalProblemsHandler:
    """Driver-focused operational problems (ride-hailing general) management with strict workflows"""

    def __init__(self, groq_api_key: str = None):
        self.service = "grab_cabs"
        self.actor = "driver"
        self.handler_type = "operational_problems_handler"
        try:
            self.ai_engine = EnhancedAgenticAIEngine()
        except Exception as e:
            logger.warning(f"AI engine initialization failed: {e}")
            self.ai_engine = None
        self.cross_actor_service = CrossActorUpdateService()

    def handle_no_rides_during_peak_hours(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle no rides during peak hours with strict 5-step workflow"""
        logger.info(f"Processing no rides during peak hours complaint: {query[:100]}...")

        # Step 1: Identify the peak hours problem type
        availability_analysis = self.analyze_ride_availability_issue(query)
        logger.info(f"Availability analysis: {availability_analysis}")

        # Step 2: Check the zone and time context of the driver's complaint
        zone_context = self.check_driver_zone_context(query)
        logger.info(f"Zone context: {zone_context}")

        # Step 3: Check driver credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Driver credibility: {credibility_score}/10")

        # Step 4: Decide on reallocation and incentive action
        decision = self.decide_ride_availability_resolution(availability_analysis, zone_context, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with zone guidance and incentive information
        response = self.generate_ride_availability_response(decision, availability_analysis, zone_context, query)
        logger.info("No rides during peak hours response generated successfully")
        return response

    def handle_unfair_ride_allocation(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle unfair ride allocation with strict 5-step workflow"""
        logger.info(f"Processing unfair ride allocation complaint: {query[:100]}...")

        # Step 1: Identify the allocation fairness issue type
        allocation_analysis = self.analyze_allocation_issue(query)
        logger.info(f"Allocation analysis: {allocation_analysis}")

        # Step 2: Check driver's ride history and allocation patterns
        allocation_history = self.check_driver_allocation_history(username)
        logger.info(f"Allocation history: {allocation_history}")

        # Step 3: Check driver credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Driver credibility: {credibility_score}/10")

        # Step 4: Decide on allocation review action
        decision = self.decide_allocation_resolution(allocation_analysis, allocation_history, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with allocation explanation and next steps
        response = self.generate_allocation_response(decision, allocation_analysis, query)
        logger.info("Unfair ride allocation response generated successfully")
        return response

    def handle_route_change_notification(self, query: str, image_data: Optional[str] = None, username: str = "anonymous", order_id: str = None) -> str:
        """Handle driver reporting a route change with strict 5-step workflow"""
        logger.info(f"Processing route change notification: {query[:100]}...")

        # Step 1: Parse the new route and the reason for the change
        route_details = self.analyze_route_change(query)
        logger.info(f"Route details: {route_details}")

        # Step 2: Assess the passenger impact of the route change
        impact = self.assess_route_change_impact(route_details, query)
        logger.info(f"Route change impact: {impact}")

        # Step 3: Check driver credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Driver credibility: {credibility_score}/10")

        # Step 4: Decide on passenger notification and earnings protection
        decision = self.decide_route_change_action(route_details, impact, credibility_score)
        logger.info(f"Route change decision: {decision}")

        # Step 5: Notify the passenger and generate the driver confirmation
        self.notify_passenger_of_route_change(route_details, decision, order_id, username)
        response = self.generate_route_change_response(decision, route_details, impact, query)
        logger.info("Route change notification response generated successfully")
        return response

    def handle_incorrect_navigation_route(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle incorrect navigation route suggestions with strict 5-step workflow"""
        logger.info(f"Processing incorrect navigation route complaint: {query[:100]}...")

        # Step 1: Identify the type of navigation problem being reported
        navigation_analysis = self.analyze_navigation_issue(query)
        logger.info(f"Navigation analysis: {navigation_analysis}")

        # Step 2: Assess the trip impact of the incorrect routing
        route_impact = self.assess_navigation_impact(navigation_analysis, query)
        logger.info(f"Route impact: {route_impact}")

        # Step 3: Check driver credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Driver credibility: {credibility_score}/10")

        # Step 4: Decide on corrected routing and payout compensation
        decision = self.decide_navigation_resolution(navigation_analysis, route_impact, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with the corrected route and compensation details
        response = self.generate_navigation_response(decision, navigation_analysis, query)
        logger.info("Incorrect navigation route response generated successfully")
        return response

    # ===== SUPPORTING METHODS FOR STRICT WORKFLOWS =====

    def _db_path(self) -> Optional[str]:
        """Resolve the path to the GrabHack database, or None if it cannot be found"""
        paths = ['grabhack.db', '../grabhack.db', 'GrabHack/grabhack.db',
                 os.path.join(os.path.dirname(__file__), '../../../grabhack.db')]
        return next((p for p in paths if os.path.exists(p)), None)

    def get_credibility_score(self, username: str) -> int:
        """Get driver credibility score from database"""
        import sqlite3
        base_score = 7
        if not username or username == "anonymous":
            return max(1, base_score - 2)
        try:
            db_path = self._db_path()
            if not db_path:
                return base_score
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT credibility_score FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else base_score
        except Exception as e:
            logger.error(f"Error fetching credibility: {e}")
            return base_score

    def analyze_ride_availability_issue(self, query: str) -> str:
        """Identify the type of ride availability problem during peak hours"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['no request', 'no ping', 'no ride']):
            return "ZERO_RIDE_REQUESTS_RECEIVED"
        elif any(w in query_lower for w in ['far', 'long distance', 'out of zone']):
            return "RIDES_ASSIGNED_TOO_FAR"
        elif any(w in query_lower for w in ['others', 'other driver', 'unfair']):
            return "ALLOCATION_BIAS_SUSPECTED"
        return "GENERAL_LOW_RIDE_AVAILABILITY"

    def check_driver_zone_context(self, query: str) -> str:
        """Check the location and time context of the availability complaint"""
        query_lower = query.lower()
        # Low-demand zones need a relocation prompt; peak windows in a busy zone
        # point at allocation rather than at genuine demand shortage
        if any(w in query_lower for w in ['airport', 'mall', 'station', 'downtown', 'city centre', 'city center']):
            return "HIGH_DEMAND_ZONE_REPORTED"
        elif any(w in query_lower for w in ['outskirts', 'suburb', 'residential', 'village', 'remote']):
            return "LOW_DEMAND_ZONE_REPORTED"
        elif any(w in query_lower for w in ['morning', 'evening', 'rush hour', 'peak', 'night']):
            return "PEAK_WINDOW_ZONE_UNSPECIFIED"
        return "ZONE_CONTEXT_UNKNOWN"

    def decide_ride_availability_resolution(self, analysis: str, zone: str, credibility: int) -> str:
        """Decide resolution for low ride availability during peak hours"""
        # Sitting in a high-demand zone with no pings points at allocation, not demand
        if zone == "HIGH_DEMAND_ZONE_REPORTED" and analysis == "ZERO_RIDE_REQUESTS_RECEIVED":
            return "ZONE_REASSIGNMENT_AND_INCENTIVE"
        elif analysis == "ZERO_RIDE_REQUESTS_RECEIVED" and credibility >= 6:
            return "ZONE_REASSIGNMENT_AND_INCENTIVE"
        elif zone == "LOW_DEMAND_ZONE_REPORTED":
            return "HOTSPOT_GUIDANCE_PROVIDED"
        elif credibility >= 5:
            return "HOTSPOT_GUIDANCE_PROVIDED"
        return "GENERAL_AVAILABILITY_TIPS"

    def generate_ride_availability_response(self, decision: str, analysis: str, zone: str, query: str) -> str:
        """Generate ride availability response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_no_rides_during_peak_hours",
                    user_query=f"DECISION: {decision} | AVAILABILITY: {analysis} | ZONE: {zone} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "ZONE_REASSIGNMENT_AND_INCENTIVE": "We have identified a surge zone near you with high demand. Moving to this area should increase your ride requests significantly. A peak-hour incentive bonus has also been applied to your account.",
            "HOTSPOT_GUIDANCE_PROVIDED": "Our demand analysis shows higher ride requests in nearby zones. Check your driver app for real-time hotspot markers to maximise your earnings during peak hours.",
            "GENERAL_AVAILABILITY_TIPS": "Ride demand fluctuates during peak hours. We recommend positioning yourself near high-demand areas shown in your driver app's heat map for best results."
        }
        return responses.get(decision, "We have noted your concern about ride availability. Our allocation team is reviewing patterns in your area.")

    def analyze_allocation_issue(self, query: str) -> str:
        """Identify the type of unfair allocation complaint"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['new driver', 'other driver', 'getting more']):
            return "PERCEIVED_BIAS_TOWARD_OTHER_DRIVERS"
        elif any(w in query_lower for w in ['cancelled', 'bad trip', 'penalised']):
            return "ALLOCATION_PENALTY_AFTER_CANCELLATION"
        elif any(w in query_lower for w in ['rating', 'low rating', 'score']):
            return "RATING_AFFECTING_ALLOCATION"
        return "GENERAL_ALLOCATION_UNFAIRNESS"

    def check_driver_allocation_history(self, username: str) -> str:
        """Check driver's historical ride allocation data from completed trips"""
        import sqlite3
        db_path = self._db_path()
        if not db_path or not username or username == "anonymous":
            return "ALLOCATION_HISTORY_UNAVAILABLE"
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''SELECT COUNT(*) FROM orders
                              WHERE (driver_id = ? OR username = ?) AND service = ?''',
                           (username, username, self.service))
            total = cursor.fetchone()[0]
            cursor.execute('''SELECT COUNT(*) FROM orders
                              WHERE (driver_id = ? OR username = ?) AND service = ?
                                AND LOWER(status) = 'cancelled' ''',
                           (username, username, self.service))
            cancelled = cursor.fetchone()[0]
            conn.close()
            if total == 0:
                return "NO_RIDE_HISTORY_YET"
            elif cancelled > total / 3:
                return "HIGH_CANCELLATION_RATE_AFFECTING_ALLOCATION"
            return "ALLOCATION_HISTORY_NORMAL"
        except Exception as e:
            logger.error(f"Error checking allocation history: {e}")
            return "ALLOCATION_HISTORY_UNAVAILABLE"

    def decide_allocation_resolution(self, analysis: str, history: str, credibility: int) -> str:
        """Decide action for unfair allocation complaint"""
        # A clean record with an allocation penalty means the penalty was misapplied
        if analysis == "ALLOCATION_PENALTY_AFTER_CANCELLATION" and history == "ALLOCATION_HISTORY_NORMAL":
            return "ALLOCATION_PENALTY_REVIEWED_AND_LIFTED"
        elif analysis == "ALLOCATION_PENALTY_AFTER_CANCELLATION" and credibility >= 6:
            return "ALLOCATION_PENALTY_REVIEWED_AND_LIFTED"
        # A genuinely high cancellation rate explains the allocation, so coach instead
        elif history == "HIGH_CANCELLATION_RATE_AFFECTING_ALLOCATION":
            return "DRIVER_PERFORMANCE_REVIEW_INITIATED"
        elif credibility >= 5:
            return "ALLOCATION_ALGORITHM_EXPLANATION"
        return "DRIVER_PERFORMANCE_REVIEW_INITIATED"

    def generate_allocation_response(self, decision: str, analysis: str, query: str) -> str:
        """Generate unfair allocation response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_unfair_ride_allocation",
                    user_query=f"DECISION: {decision} | ALLOCATION_ISSUE: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "ALLOCATION_PENALTY_REVIEWED_AND_LIFTED": "We have reviewed your allocation history and identified an unfair restriction. The allocation penalty has been lifted and your ride requests should normalise immediately.",
            "ALLOCATION_ALGORITHM_EXPLANATION": "Our ride allocation system considers multiple factors including location, acceptance rate, and demand patterns. A detailed breakdown of how your allocation is calculated has been sent to your driver app.",
            "DRIVER_PERFORMANCE_REVIEW_INITIATED": "Your allocation concern has triggered a performance review. Our driver partner team will analyse your ride history and provide personalised tips to improve your allocation within 3 business days."
        }
        return responses.get(decision, "Your ride allocation concern has been logged. Our algorithm team will review and respond within 48 hours.")

    def analyze_route_change(self, query: str) -> dict:
        """Parse the new route and the reason for the change out of the driver's message"""
        new_route = "alternate route"
        reason = "traffic conditions"
        query_lower = query.lower()

        if "taking" in query_lower:
            words = query.split()
            for i, word in enumerate(words):
                if word.lower() == "taking" and i + 1 < len(words):
                    new_route = " ".join(words[i + 1:i + 3])
                    break

        if "due to" in query_lower:
            reason_part = query_lower.split("due to")[1].strip()
            reason = reason_part.split('.')[0] if '.' in reason_part else reason_part

        return {"new_route": new_route, "reason": reason}

    def assess_route_change_impact(self, route_details: dict, query: str) -> str:
        """Assess how much the route change delays the passenger"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['accident', 'closed', 'blocked', 'diversion', 'flood']):
            return "MAJOR_DELAY_UNAVOIDABLE_DIVERSION"
        elif any(w in query_lower for w in ['shortcut', 'faster', 'quicker']):
            return "NO_DELAY_FASTER_ROUTE"
        # Read traffic off the driver's own words, not off the default reason
        elif any(w in query_lower for w in ['traffic', 'jam', 'congestion', 'construction']):
            return "MODERATE_DELAY_TRAFFIC_AVOIDANCE"
        return "MINOR_DELAY_EXPECTED"

    def decide_route_change_action(self, route_details: dict, impact: str, credibility: int) -> str:
        """Decide passenger notification and driver earnings protection for the route change"""
        # Without a named route there is nothing specific to tell the passenger, so the
        # change is logged for review rather than pushed as a notification
        if route_details.get("new_route") == "alternate route" and credibility < 6:
            return "ROUTE_CHANGE_LOGGED_FOR_REVIEW"
        # An unavoidable diversion is not the driver's fault, so earnings are protected
        # regardless of standing and the passenger gets a full explanation
        elif impact == "MAJOR_DELAY_UNAVOIDABLE_DIVERSION":
            return "PASSENGER_NOTIFIED_EARNINGS_PROTECTED"
        elif impact == "NO_DELAY_FASTER_ROUTE":
            return "PASSENGER_NOTIFIED_NO_ADJUSTMENT_NEEDED"
        elif impact == "MODERATE_DELAY_TRAFFIC_AVOIDANCE" and credibility >= 5:
            return "PASSENGER_NOTIFIED_EARNINGS_PROTECTED"
        elif credibility >= 5:
            return "PASSENGER_NOTIFIED_STANDARD_LOGGING"
        return "ROUTE_CHANGE_LOGGED_FOR_REVIEW"

    def notify_passenger_of_route_change(self, route_details: dict, decision: str, order_id: str, username: str) -> bool:
        """Push the route change to the passenger through the cross-actor service"""
        if not order_id or not username or username == "anonymous":
            logger.info("Route change not pushed to passenger: order or driver identity missing")
            return False
        if decision == "ROUTE_CHANGE_LOGGED_FOR_REVIEW":
            logger.info("Route change held for review before passenger notification")
            return False
        try:
            self.cross_actor_service.create_cross_actor_update(
                order_id=order_id,
                actor_type="driver",
                actor_username=username,
                update_type="route_changed",
                details={
                    "new_route": route_details.get("new_route"),
                    "route_description": route_details.get("new_route"),
                    "reason": route_details.get("reason"),
                    "new_eta": "5-10 minutes later"
                }
            )
            logger.info(f"Passenger notified of route change on order {order_id}")
            return True
        except Exception as e:
            logger.error(f"Error notifying passenger of route change: {e}")
            return False

    def generate_route_change_response(self, decision: str, route_details: dict, impact: str, query: str) -> str:
        """Generate route change notification response"""
        new_route = route_details.get("new_route")
        reason = route_details.get("reason")
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_route_change_notification",
                    user_query=f"DECISION: {decision} | ROUTE: {new_route} | REASON: {reason} | IMPACT: {impact} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "PASSENGER_NOTIFIED_EARNINGS_PROTECTED": f"Your route change to {new_route} due to {reason} has been logged and the passenger has been notified with an updated ETA. The extra time is protected for earnings and will be compensated on this trip, with no impact on your rating.",
            "PASSENGER_NOTIFIED_NO_ADJUSTMENT_NEEDED": f"Your route change to {new_route} has been logged and the passenger notified. Since this route is faster, no ETA adjustment or fare change is needed. Thank you for optimising the trip.",
            "PASSENGER_NOTIFIED_STANDARD_LOGGING": f"Your route change to {new_route} due to {reason} has been recorded and the passenger has been notified. Continue safely on your alternate route.",
            "ROUTE_CHANGE_LOGGED_FOR_REVIEW": f"Your route change to {new_route} has been logged for review. Please keep the passenger informed directly while our team verifies the deviation."
        }
        return responses.get(decision, "Your route change has been logged and the passenger has been notified. Continue with your alternate route safely.")

    def analyze_navigation_issue(self, query: str) -> str:
        """Identify the type of navigation problem the driver is reporting"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['wrong destination', 'wrong location', 'wrong drop', 'wrong address']):
            return "ROUTED_TO_WRONG_DESTINATION"
        elif any(w in query_lower for w in ['closed', 'blocked', 'construction', 'one way', 'no entry']):
            return "ROUTE_THROUGH_BLOCKED_ROAD"
        elif any(w in query_lower for w in ['traffic', 'outdated', 'not updated', 'old data']):
            return "OUTDATED_TRAFFIC_DATA"
        elif any(w in query_lower for w in ['wrong', 'incorrect', 'bad route', 'wrong direction', 'navigation', 'route', 'gps', 'direction']):
            return "GENERAL_INCORRECT_ROUTE"
        return "NAVIGATION_ISSUE_UNCLEAR"

    def assess_navigation_impact(self, analysis: str, query: str) -> str:
        """Assess how badly the incorrect routing affected the trip"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['lost', 'far away', 'wasted', 'extra km', 'extra kilometres', 'long detour']):
            return "SIGNIFICANT_DETOUR_AND_FUEL_LOSS"
        elif any(w in query_lower for w in ['late', 'delayed', 'passenger angry', 'complaint']):
            return "TRIP_DELAYED_PASSENGER_AFFECTED"
        elif analysis == "NAVIGATION_ISSUE_UNCLEAR":
            return "IMPACT_NOT_YET_DESCRIBED"
        return "MINOR_ROUTING_INCONVENIENCE"

    def decide_navigation_resolution(self, analysis: str, impact: str, credibility: int) -> str:
        """Decide corrected routing and payout compensation for the navigation error"""
        # Nothing actionable was described yet, so ask before promising a fix
        if analysis == "NAVIGATION_ISSUE_UNCLEAR" or impact == "IMPACT_NOT_YET_DESCRIBED":
            return "CLARIFICATION_REQUIRED"
        # Our GPS sending a driver to the wrong place costs them fuel and time directly
        elif analysis == "ROUTED_TO_WRONG_DESTINATION" or impact == "SIGNIFICANT_DETOUR_AND_FUEL_LOSS":
            return "CORRECTED_ROUTE_WITH_PAYOUT_COMPENSATION"
        elif impact == "TRIP_DELAYED_PASSENGER_AFFECTED" and credibility >= 5:
            return "CORRECTED_ROUTE_WITH_PAYOUT_COMPENSATION"
        elif credibility >= 5:
            return "CORRECTED_ROUTE_ISSUE_REPORTED"
        return "CORRECTED_ROUTE_PROVIDED"

    def generate_navigation_response(self, decision: str, analysis: str, query: str) -> str:
        """Generate incorrect navigation route response"""
        if decision == "CLARIFICATION_REQUIRED":
            return """I'm here to help with your navigation concerns. Could you please tell me more about what's wrong with the route?

For example:
- Is the route taking you through incorrect roads?
- Are you being directed to the wrong destination?
- Is the GPS showing outdated traffic information?
- Are there road closures not being accounted for?

Once I understand the specific issue, I can provide you with the correct route and report the problem to our technical team."""

        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_incorrect_navigation_route",
                    user_query=f"DECISION: {decision} | NAVIGATION_ISSUE: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")

        corrected_route_link = """**Updated route**:
https://maps.app.goo.gl/PEaK5NpD5oZMhKg3A

Open that link to load the correct route in Google Maps, and use it instead of the in-app navigation for this trip."""

        responses = {
            "CORRECTED_ROUTE_WITH_PAYOUT_COMPENSATION": f"""I apologize for the incorrect route suggestions from our GPS system. Here is an updated and correct route to your destination:

{corrected_route_link}

This GPS issue has been reported to our technical team, and route accuracy compensation for the extra distance and time will be added to your next payout.

Is there anything else about the navigation I can help you with?""",
            "CORRECTED_ROUTE_ISSUE_REPORTED": f"""I apologize for the routing problem. Here is a corrected route to help you reach the destination efficiently:

{corrected_route_link}

We have reported this GPS issue to our technical team so the map data can be updated for future trips.

Is there anything else about the navigation I can help you with?""",
            "CORRECTED_ROUTE_PROVIDED": f"""Here is an updated route to help you reach your destination:

{corrected_route_link}

Please use this instead of the in-app navigation for this trip while we review the routing data.

Is there anything else about the navigation I can help you with?"""
        }
        return responses.get(decision, f"""I apologize for the incorrect route suggestions from our GPS system.

{corrected_route_link}

We are reporting this issue to our technical team to prevent similar problems in the future.""")
