"""
Grab Cabs Customer Operational Issues Handler
Uses AI models for intelligent complaint resolution with strict workflows
"""

import logging
import os
import sys
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class OperationalIssuesHandler:
    """Customer-focused operational issues management with strict workflows"""

    def __init__(self, groq_api_key: str = None):
        self.service = "grab_cabs"
        self.actor = "customer"
        self.handler_type = "operational_issues_handler"
        try:
            self.ai_engine = EnhancedAgenticAIEngine()
        except Exception as e:
            logger.warning(f"AI engine initialization failed: {e}")
            self.ai_engine = None

    def handle_pickup_drop_errors(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle pickup & drop location errors with strict 5-step workflow - TEXT ONLY"""
        logger.info(f"Processing pickup/drop errors complaint: {query[:100]}...")

        # Step 1: Identify the type of pickup/drop error from the complaint
        error_analysis = self.analyze_pickup_drop_error(query)
        logger.info(f"Error analysis: {error_analysis}")

        # Step 2: Assess the impact on the customer's journey
        journey_impact = self.assess_journey_impact(error_analysis, query)
        logger.info(f"Journey impact: {journey_impact}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on compensation and corrective action
        decision = self.decide_pickup_drop_resolution(error_analysis, journey_impact, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with compensation and prevention measures
        response = self.generate_pickup_drop_response(decision, error_analysis, journey_impact, query)
        logger.info(f"Pickup/drop errors response generated successfully")

        return response

    def handle_route_problems(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle route problems with strict 5-step workflow - TEXT ONLY"""
        logger.info(f"Processing route problems complaint: {query[:100]}...")

        # Step 1: Identify the specific route problem from the complaint
        route_analysis = self.analyze_route_problem(query)
        logger.info(f"Route analysis: {route_analysis}")

        # Step 2: Validate if the route deviated from the optimal path
        route_validation = self.validate_route_deviation(route_analysis, query)
        logger.info(f"Route validation: {route_validation}")

        # Step 3: Check if extra fare was charged due to the route issue
        fare_impact = self.check_fare_impact_from_route(route_analysis)
        logger.info(f"Fare impact check: {fare_impact}")

        # Step 4: Check customer credibility and decide compensation
        credibility_score = self.get_credibility_score(username)
        decision = self.decide_route_resolution(route_analysis, route_validation, fare_impact, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with route correction and fare adjustment
        response = self.generate_route_response(decision, route_analysis, fare_impact, query)
        logger.info(f"Route problems response generated successfully")

        return response

    def handle_communication_issues(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle driver communication issues with strict 5-step workflow - TEXT ONLY"""
        logger.info(f"Processing communication issues complaint: {query[:100]}...")

        # Step 1: Identify the type of communication failure from the complaint
        comm_analysis = self.analyze_communication_failure(query)
        logger.info(f"Communication analysis: {comm_analysis}")

        # Step 2: Assess the severity and impact of the communication breakdown
        impact_assessment = self.assess_communication_impact(comm_analysis, query)
        logger.info(f"Impact assessment: {impact_assessment}")

        # Step 3: Check if it led to trip failure or significant inconvenience
        trip_outcome = self.check_trip_outcome_from_comm_issue(comm_analysis, query)
        logger.info(f"Trip outcome check: {trip_outcome}")

        # Step 4: Check customer credibility and decide action
        credibility_score = self.get_credibility_score(username)
        decision = self.decide_communication_resolution(comm_analysis, impact_assessment, trip_outcome, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with resolution and driver action
        response = self.generate_communication_response(decision, comm_analysis, impact_assessment, query)
        logger.info(f"Communication issues response generated successfully")

        return response

    # ===== SUPPORTING METHODS FOR STRICT WORKFLOWS =====

    def _db_path(self) -> Optional[str]:
        """Resolve the path to the GrabHack database, or None if it cannot be found"""
        paths = ['grabhack.db', '../grabhack.db', 'GrabHack/grabhack.db',
                 os.path.join(os.path.dirname(__file__), '../../../grabhack.db')]
        return next((p for p in paths if os.path.exists(p)), None)

    def get_credibility_score(self, username: str) -> int:
        """Get customer credibility score from database"""
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

    def analyze_pickup_drop_error(self, query: str) -> str:
        """Identify the type of pickup/drop location error"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['wrong pickup', 'wrong location', 'pickup point']):
            return "WRONG_PICKUP_LOCATION"
        elif any(w in query_lower for w in ['wrong drop', 'wrong destination', 'dropped wrong']):
            return "WRONG_DROP_LOCATION"
        elif any(w in query_lower for w in ['delayed pickup', 'late pickup', 'waiting long']):
            return "DELAYED_PICKUP"
        return "GENERAL_LOCATION_ERROR"

    def assess_journey_impact(self, analysis: str, query: str) -> str:
        """Assess the impact on the customer's journey"""
        high_impact = ["WRONG_DROP_LOCATION"]
        return "HIGH_IMPACT" if analysis in high_impact else "MODERATE_IMPACT"

    def decide_pickup_drop_resolution(self, analysis: str, impact: str, credibility: int) -> str:
        """Decide resolution for pickup/drop error"""
        # Being left at the wrong destination is a failure to deliver the ride at all
        if analysis == "WRONG_DROP_LOCATION":
            return "FULL_REFUND_CORRECTION"
        elif impact == "HIGH_IMPACT" and credibility >= 6:
            return "FULL_REFUND_CORRECTION"
        elif analysis == "WRONG_PICKUP_LOCATION" and credibility >= 5:
            return "PARTIAL_REFUND_APOLOGY"
        elif credibility >= 5:
            return "PARTIAL_REFUND_APOLOGY"
        return "GOODWILL_CREDIT"

    def generate_pickup_drop_response(self, decision: str, analysis: str, impact: str, query: str) -> str:
        """Generate pickup/drop error response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_pickup_drop_errors",
                    user_query=f"DECISION: {decision} | ERROR: {analysis} | IMPACT: {impact} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "FULL_REFUND_CORRECTION": "We sincerely apologize for the location error. A full refund has been processed and we've flagged the driver for location accuracy training.",
            "PARTIAL_REFUND_APOLOGY": "We apologize for the pickup/drop location issue. A partial refund has been issued and the driver notified.",
            "GOODWILL_CREDIT": "Thank you for reporting the location issue. A goodwill credit has been added to your account."
        }
        return responses.get(decision, "Your location complaint has been logged and will be resolved within 24 hours.")

    def analyze_route_problem(self, query: str) -> str:
        """Identify the specific type of route problem"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['longer route', 'longer way', 'extra distance']):
            return "LONGER_ROUTE_TAKEN"
        elif any(w in query_lower for w in ['wrong route', 'wrong direction', 'wrong road']):
            return "WRONG_ROUTE_TAKEN"
        elif any(w in query_lower for w in ['reroute', 'detour', 'unexpected']):
            return "UNAUTHORIZED_DETOUR"
        return "GENERAL_ROUTE_ISSUE"

    def validate_route_deviation(self, analysis: str, query: str) -> str:
        """Validate whether the route deviation was justified"""
        if analysis in ["WRONG_ROUTE_TAKEN", "UNAUTHORIZED_DETOUR"]:
            return "DEVIATION_NOT_JUSTIFIED"
        return "DEVIATION_NEEDS_REVIEW"

    def check_fare_impact_from_route(self, analysis: str) -> str:
        """Check if the route issue resulted in extra fare"""
        if analysis in ["LONGER_ROUTE_TAKEN", "UNAUTHORIZED_DETOUR"]:
            return "EXTRA_FARE_CHARGED"
        return "FARE_IMPACT_UNCLEAR"

    def decide_route_resolution(self, analysis: str, validation: str, fare_impact: str, credibility: int) -> str:
        """Decide resolution for route problem"""
        # A detour the rider never agreed to, with an unjustified deviation on record,
        # is a driver fault that refunds without needing a credibility score
        if analysis == "UNAUTHORIZED_DETOUR" and validation == "DEVIATION_NOT_JUSTIFIED":
            return "REFUND_EXTRA_FARE_DRIVER_WARNING"
        elif validation == "DEVIATION_NOT_JUSTIFIED" and credibility >= 6:
            return "REFUND_EXTRA_FARE_DRIVER_WARNING"
        elif analysis in ("WRONG_ROUTE_TAKEN", "LONGER_ROUTE_TAKEN") and fare_impact == "EXTRA_FARE_CHARGED":
            return "REFUND_EXTRA_FARE_DRIVER_WARNING"
        elif fare_impact == "EXTRA_FARE_CHARGED" and credibility >= 5:
            return "PARTIAL_REFUND_REVIEW"
        return "INVESTIGATION_INITIATED"

    def generate_route_response(self, decision: str, analysis: str, fare_impact: str, query: str) -> str:
        """Generate route problem response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_route_problems",
                    user_query=f"DECISION: {decision} | ROUTE_ISSUE: {analysis} | FARE_IMPACT: {fare_impact} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "REFUND_EXTRA_FARE_DRIVER_WARNING": "We've confirmed the unauthorized route deviation. The extra fare has been refunded and the driver issued a formal warning.",
            "PARTIAL_REFUND_REVIEW": "We're reviewing the route data. A partial refund has been issued pending final investigation results.",
            "INVESTIGATION_INITIATED": "Our route analytics team is reviewing your trip data and will resolve this within 24 hours."
        }
        return responses.get(decision, "Your route complaint is under investigation.")

    def analyze_communication_failure(self, query: str) -> str:
        """Identify the type of communication failure"""
        query_lower = query.lower()
        if any(w in query_lower for w in ["not answering", "not picking up", "not responding"]):
            return "DRIVER_NOT_RESPONDING"
        elif any(w in query_lower for w in ['language', 'understand', 'barrier']):
            return "LANGUAGE_BARRIER"
        elif any(w in query_lower for w in ['rude', 'impolite', 'disrespectful']):
            return "RUDE_COMMUNICATION"
        return "GENERAL_COMMUNICATION_FAILURE"

    def assess_communication_impact(self, analysis: str, query: str) -> str:
        """Assess impact of communication failure"""
        return "HIGH_IMPACT" if analysis == "DRIVER_NOT_RESPONDING" else "MODERATE_IMPACT"

    def check_trip_outcome_from_comm_issue(self, analysis: str, query: str) -> str:
        """Check if communication issue caused trip cancellation or failure"""
        if 'cancel' in query.lower() or 'missed' in query.lower():
            return "TRIP_FAILED_DUE_TO_COMM"
        return "TRIP_COMPLETED_WITH_DIFFICULTY"

    def decide_communication_resolution(self, analysis: str, impact: str, trip_outcome: str, credibility: int) -> str:
        """Decide resolution for communication failure"""
        # A trip that never happened because the driver went silent is a full failure
        if trip_outcome == "TRIP_FAILED_DUE_TO_COMM":
            return "FULL_REFUND_DRIVER_REVIEW"
        elif analysis == "RUDE_COMMUNICATION" and credibility >= 5:
            return "PARTIAL_CREDIT_WARNING"
        elif impact == "HIGH_IMPACT" and credibility >= 5:
            return "PARTIAL_CREDIT_WARNING"
        elif credibility >= 5:
            return "PARTIAL_CREDIT_WARNING"
        return "GOODWILL_GESTURE"

    def generate_communication_response(self, decision: str, analysis: str, impact: str, query: str) -> str:
        """Generate communication issue response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_communication_issues",
                    user_query=f"DECISION: {decision} | COMM_ISSUE: {analysis} | IMPACT: {impact} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "FULL_REFUND_DRIVER_REVIEW": "We apologize for the communication failure that disrupted your trip. A full refund has been processed and the driver flagged for communication standards review.",
            "PARTIAL_CREDIT_WARNING": "We're sorry about the communication difficulties. A credit has been added to your account and the driver notified about professional communication standards.",
            "GOODWILL_GESTURE": "Thank you for your feedback on the communication issue. A goodwill gesture has been added to your account."
        }
        return responses.get(decision, "Your communication complaint has been forwarded to the driver's supervisor.")
