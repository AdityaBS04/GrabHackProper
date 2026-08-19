"""
Grab Cabs Driver Operational Issues Handler
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
    """Driver-focused operational issues management with strict workflows"""

    def __init__(self, groq_api_key: str = None):
        self.service = "grab_cabs"
        self.actor = "driver"
        self.handler_type = "operational_issues_handler"
        try:
            self.ai_engine = EnhancedAgenticAIEngine()
        except Exception as e:
            logger.warning(f"AI engine initialization failed: {e}")
            self.ai_engine = None

    def handle_passenger_cancellation_after_arrival(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle passenger cancellation after driver arrival with strict 5-step workflow"""
        logger.info(f"Processing passenger cancellation after arrival complaint: {query[:100]}...")

        # Step 1: Identify the cancellation scenario and wait time
        cancellation_analysis = self.analyze_late_cancellation(query)
        logger.info(f"Cancellation analysis: {cancellation_analysis}")

        # Step 2: Assess the financial impact on the driver
        financial_impact = self.assess_cancellation_financial_impact(cancellation_analysis, query)
        logger.info(f"Financial impact: {financial_impact}")

        # Step 3: Check driver credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Driver credibility: {credibility_score}/10")

        # Step 4: Decide on cancellation fee and compensation
        decision = self.decide_cancellation_compensation(cancellation_analysis, financial_impact, credibility_score)
        logger.info(f"Compensation decision: {decision}")

        # Step 5: Generate response with compensation details
        response = self.generate_cancellation_response(decision, cancellation_analysis, financial_impact, query)
        logger.info("Passenger cancellation response generated successfully")
        return response

    def handle_wrong_pickup_drop_details(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle wrong pickup/drop details from app with strict 5-step workflow"""
        logger.info(f"Processing wrong pickup/drop details complaint: {query[:100]}...")

        # Step 1: Identify the type of location error from the complaint
        location_analysis = self.analyze_location_error(query)
        logger.info(f"Location analysis: {location_analysis}")

        # Step 2: Assess the time and fuel wasted due to the error
        impact_assessment = self.assess_location_error_impact(location_analysis, query)
        logger.info(f"Impact assessment: {impact_assessment}")

        # Step 3: Check driver credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Driver credibility: {credibility_score}/10")

        # Step 4: Decide on compensation for wasted time and fuel
        decision = self.decide_location_error_resolution(location_analysis, impact_assessment, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with compensation and technical correction
        response = self.generate_location_error_response(decision, location_analysis, impact_assessment, query)
        logger.info("Wrong location response generated successfully")
        return response

    def handle_long_waiting_time_compensation(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle long waiting time compensation requests with strict 5-step workflow"""
        logger.info(f"Processing long waiting time compensation complaint: {query[:100]}...")

        # Step 1: Quantify the waiting time from the complaint
        wait_analysis = self.analyze_waiting_time(query)
        logger.info(f"Wait analysis: {wait_analysis}")

        # Step 2: Determine if the wait was due to passenger or system fault
        fault_assessment = self.assess_waiting_fault(wait_analysis, query)
        logger.info(f"Fault assessment: {fault_assessment}")

        # Step 3: Check driver credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Driver credibility: {credibility_score}/10")

        # Step 4: Decide on waiting time compensation amount
        decision = self.decide_waiting_compensation(wait_analysis, fault_assessment, credibility_score)
        logger.info(f"Compensation decision: {decision}")

        # Step 5: Generate response with compensation confirmation
        response = self.generate_waiting_response(decision, wait_analysis, fault_assessment, query)
        logger.info("Waiting time compensation response generated successfully")
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

    def analyze_late_cancellation(self, query: str) -> str:
        """Identify the circumstances of the late cancellation"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['already arrived', 'at pickup', 'waiting outside']):
            return "CANCELLATION_AFTER_ARRIVAL_AT_PICKUP"
        elif any(w in query_lower for w in ['10 minute', '15 minute', 'long wait']):
            return "CANCELLATION_AFTER_EXTENDED_WAIT"
        elif any(w in query_lower for w in ['no show', 'not there', 'not found']):
            return "PASSENGER_NO_SHOW_THEN_CANCEL"
        return "GENERAL_LATE_CANCELLATION"

    def assess_cancellation_financial_impact(self, analysis: str, query: str) -> str:
        """Assess the financial loss to the driver from the cancellation"""
        high_impact = ["CANCELLATION_AFTER_EXTENDED_WAIT", "PASSENGER_NO_SHOW_THEN_CANCEL"]
        return "HIGH_FINANCIAL_IMPACT" if analysis in high_impact else "MODERATE_FINANCIAL_IMPACT"

    def decide_cancellation_compensation(self, analysis: str, impact: str, credibility: int) -> str:
        """Decide cancellation fee and driver compensation"""
        # Once the driver has reached the pickup point the trip cost is already incurred,
        # so the full cancellation fee is owed by policy rather than by discretion
        if analysis in ("CANCELLATION_AFTER_ARRIVAL_AT_PICKUP", "PASSENGER_NO_SHOW_THEN_CANCEL"):
            return "FULL_CANCELLATION_FEE_COLLECTED"
        elif impact == "HIGH_FINANCIAL_IMPACT" and credibility >= 6:
            return "FULL_CANCELLATION_FEE_COLLECTED"
        elif analysis == "CANCELLATION_AFTER_EXTENDED_WAIT" and credibility >= 4:
            return "PARTIAL_CANCELLATION_FEE_APPLIED"
        elif credibility >= 5:
            return "PARTIAL_CANCELLATION_FEE_APPLIED"
        return "STANDARD_CANCELLATION_POLICY_APPLIED"

    def generate_cancellation_response(self, decision: str, analysis: str, impact: str, query: str) -> str:
        """Generate passenger cancellation response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_passenger_cancellation_after_arrival",
                    user_query=f"DECISION: {decision} | CANCELLATION: {analysis} | IMPACT: {impact} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "FULL_CANCELLATION_FEE_COLLECTED": "The cancellation fee has been charged to the passenger and credited to your account. Your waiting time has been fully compensated and this incident will not affect your driver rating.",
            "PARTIAL_CANCELLATION_FEE_APPLIED": "A partial cancellation fee has been applied. Your account has been credited and the passenger has been flagged for late cancellation behaviour.",
            "STANDARD_CANCELLATION_POLICY_APPLIED": "Standard cancellation policy has been applied. The applicable fee will appear in your next earnings statement."
        }
        return responses.get(decision, "Your cancellation complaint has been logged. Compensation will be reviewed and applied within 24 hours.")

    def analyze_location_error(self, query: str) -> str:
        """Identify the type of location error in the app"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['wrong pickup', 'wrong address', 'different location']):
            return "WRONG_PICKUP_LOCATION_IN_APP"
        elif any(w in query_lower for w in ['wrong drop', 'wrong destination']):
            return "WRONG_DROP_LOCATION_IN_APP"
        elif any(w in query_lower for w in ['pin', 'marker', 'map error']):
            return "MAP_PIN_ERROR"
        return "GENERAL_LOCATION_DATA_ERROR"

    def assess_location_error_impact(self, analysis: str, query: str) -> str:
        """Assess the time and resource waste from the location error"""
        if analysis in ["WRONG_PICKUP_LOCATION_IN_APP", "MAP_PIN_ERROR"]:
            return "SIGNIFICANT_TIME_AND_FUEL_WASTED"
        return "MINOR_INCONVENIENCE"

    def decide_location_error_resolution(self, analysis: str, impact: str, credibility: int) -> str:
        """Decide compensation for the location data error"""
        # Wrong coordinates in our own app sent the driver to the wrong place — that is
        # our data error to compensate, not something for them to prove
        if analysis in ("WRONG_PICKUP_LOCATION_IN_APP", "WRONG_DROP_LOCATION_IN_APP") and impact == "SIGNIFICANT_TIME_AND_FUEL_WASTED":
            return "FUEL_TIME_COMPENSATION_ISSUED"
        elif impact == "SIGNIFICANT_TIME_AND_FUEL_WASTED" and credibility >= 6:
            return "FUEL_TIME_COMPENSATION_ISSUED"
        elif analysis == "MAP_PIN_ERROR" and credibility >= 4:
            return "PARTIAL_COMPENSATION_TECHNICAL_TICKET"
        elif credibility >= 5:
            return "PARTIAL_COMPENSATION_TECHNICAL_TICKET"
        return "TECHNICAL_TICKET_FILED"

    def generate_location_error_response(self, decision: str, analysis: str, impact: str, query: str) -> str:
        """Generate wrong location error response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_wrong_pickup_drop_details",
                    user_query=f"DECISION: {decision} | LOCATION_ERROR: {analysis} | IMPACT: {impact} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "FUEL_TIME_COMPENSATION_ISSUED": "We confirmed the app provided incorrect location data. Compensation for your extra time and fuel has been credited to your account. A technical ticket has been raised to fix the app error.",
            "PARTIAL_COMPENSATION_TECHNICAL_TICKET": "A technical ticket has been filed for the location error. Partial compensation has been applied and our tech team will review the mapping data.",
            "TECHNICAL_TICKET_FILED": "Your report of incorrect location data has been forwarded to our technical team for investigation and correction."
        }
        return responses.get(decision, "Your location error report has been logged. We will investigate and improve map accuracy in your area.")

    def analyze_waiting_time(self, query: str) -> str:
        """Quantify the waiting time from the driver's complaint"""
        import re
        time_match = re.search(r'(\d+)\s*(minute|min|hour)', query.lower())
        if time_match:
            return f"WAITED_{time_match.group(1)}_{time_match.group(2).upper()}"
        if any(w in query.lower() for w in ['long', 'forever', 'ages']):
            return "EXTENDED_WAIT_UNQUANTIFIED"
        return "WAIT_TIME_NOT_SPECIFIED"

    def assess_waiting_fault(self, analysis: str, query: str) -> str:
        """Determine who is responsible for the extended wait"""
        if any(w in query.lower() for w in ['passenger', 'customer', 'not ready']):
            return "PASSENGER_FAULT"
        if any(w in query.lower() for w in ['airport', 'traffic', 'queue']):
            return "EXTERNAL_CIRCUMSTANCE"
        return "CAUSE_UNCLEAR"

    def decide_waiting_compensation(self, analysis: str, fault: str, credibility: int) -> str:
        """Decide waiting time compensation amount"""
        if fault == "PASSENGER_FAULT" and credibility >= 6:
            return "FULL_WAITING_FEE_CREDITED"
        # A wait the driver could quantify is billable against the passenger's account
        elif analysis.startswith("WAITED_") and fault == "PASSENGER_FAULT":
            return "FULL_WAITING_FEE_CREDITED"
        elif analysis.startswith("WAITED_") and credibility >= 4:
            return "PARTIAL_WAITING_COMPENSATION"
        # Nothing quantified and no clear cause leaves only a policy explanation
        elif analysis == "WAIT_TIME_NOT_SPECIFIED" and fault == "CAUSE_UNCLEAR":
            return "WAITING_POLICY_REVIEWED"
        elif credibility >= 5:
            return "PARTIAL_WAITING_COMPENSATION"
        return "WAITING_POLICY_REVIEWED"

    def generate_waiting_response(self, decision: str, analysis: str, fault: str, query: str) -> str:
        """Generate waiting time compensation response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_long_waiting_time_compensation",
                    user_query=f"DECISION: {decision} | WAIT: {analysis} | FAULT: {fault} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "FULL_WAITING_FEE_CREDITED": "Your waiting fee has been fully calculated and credited to your account. The passenger has also been flagged for keeping drivers waiting excessively.",
            "PARTIAL_WAITING_COMPENSATION": "A partial waiting time compensation has been credited to your account. We are reviewing the full circumstances of the delay.",
            "WAITING_POLICY_REVIEWED": "Your waiting time report has been logged. Our team will review the trip details and apply appropriate compensation per our driver waiting policy."
        }
        return responses.get(decision, "Your waiting time complaint has been noted. Compensation will be calculated and applied within 24 hours.")
