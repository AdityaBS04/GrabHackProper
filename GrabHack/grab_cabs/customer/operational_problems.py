"""
Grab Cabs Customer Operational Problems (Ride-Hailing General) Handler
Uses AI models for intelligent complaint resolution with strict workflows
"""

import logging
import os
import sys
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class OperationalProblemsHandler:
    """Customer-focused operational problems management with strict workflows"""

    def __init__(self, groq_api_key: str = None):
        self.service = "grab_cabs"
        self.actor = "customer"
        self.handler_type = "operational_problems_handler"
        try:
            self.ai_engine = EnhancedAgenticAIEngine()
        except Exception as e:
            logger.warning(f"AI engine initialization failed: {e}")
            self.ai_engine = None

    def handle_driver_availability(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle driver availability issues with strict 5-step workflow - TEXT ONLY"""
        logger.info(f"Processing driver availability complaint: {query[:100]}...")

        # Step 1: Identify the availability problem scenario
        availability_analysis = self.analyze_availability_issue(query)
        logger.info(f"Availability analysis: {availability_analysis}")

        # Step 2: Check time and location context from complaint
        context_check = self.check_time_location_context(query)
        logger.info(f"Context check: {context_check}")

        # Step 3: Assess impact on customer (missed appointment, urgent need, etc.)
        impact_assessment = self.assess_availability_impact(availability_analysis, query)
        logger.info(f"Impact assessment: {impact_assessment}")

        # Step 4: Check customer credibility and decide compensation
        credibility_score = self.get_credibility_score(username)
        decision = self.decide_availability_resolution(availability_analysis, impact_assessment, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with solutions and compensation
        response = self.generate_availability_response(decision, availability_analysis, impact_assessment, query)
        logger.info(f"Driver availability response generated successfully")

        return response

    def handle_driver_cancellations(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle driver cancellations with strict 5-step workflow - TEXT ONLY"""
        logger.info(f"Processing driver cancellations complaint: {query[:100]}...")

        # Step 1: Identify the cancellation pattern from the complaint
        cancellation_analysis = self.analyze_driver_cancellation(query)
        logger.info(f"Cancellation analysis: {cancellation_analysis}")

        # Step 2: Check if cancellation caused significant disruption
        disruption_assessment = self.assess_cancellation_disruption(cancellation_analysis, query)
        logger.info(f"Disruption assessment: {disruption_assessment}")

        # Step 3: Check how many drivers cancelled before getting a ride
        repeat_cancellation_check = self.check_repeat_cancellation_pattern(query)
        logger.info(f"Repeat cancellation check: {repeat_cancellation_check}")

        # Step 4: Check customer credibility and decide compensation
        credibility_score = self.get_credibility_score(username)
        decision = self.decide_cancellation_resolution(cancellation_analysis, disruption_assessment, repeat_cancellation_check, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with compensation and system improvements
        response = self.generate_cancellation_response(decision, cancellation_analysis, disruption_assessment, query)
        logger.info(f"Driver cancellations response generated successfully")

        return response

    def handle_late_arrivals_no_shows(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle late arrivals and no-shows with strict 5-step workflow - TEXT ONLY"""
        logger.info(f"Processing late arrivals/no-shows complaint: {query[:100]}...")

        # Step 1: Identify whether it's a late arrival or a no-show
        incident_analysis = self.analyze_late_arrival_no_show(query)
        logger.info(f"Incident analysis: {incident_analysis}")

        # Step 2: Quantify the delay or wait time from the complaint
        delay_quantification = self.quantify_delay(incident_analysis, query)
        logger.info(f"Delay quantification: {delay_quantification}")

        # Step 3: Assess downstream impact (missed appointment, extra cost, etc.)
        downstream_impact = self.assess_downstream_impact(delay_quantification, query)
        logger.info(f"Downstream impact: {downstream_impact}")

        # Step 4: Check customer credibility and decide compensation
        credibility_score = self.get_credibility_score(username)
        decision = self.decide_late_arrival_resolution(incident_analysis, delay_quantification, downstream_impact, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with compensation and service commitment
        response = self.generate_late_arrival_response(decision, incident_analysis, delay_quantification, query)
        logger.info(f"Late arrivals/no-shows response generated successfully")

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

    def analyze_availability_issue(self, query: str) -> str:
        """Identify the type of availability problem"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['peak', 'rush hour', 'busy']):
            return "PEAK_HOUR_SHORTAGE"
        elif any(w in query_lower for w in ['remote', 'far', 'outskirts', 'no drivers']):
            return "REMOTE_AREA_SHORTAGE"
        elif any(w in query_lower for w in ['surge', 'high price', 'expensive']):
            return "SURGE_PRICING_DETERRENCE"
        return "GENERAL_AVAILABILITY_ISSUE"

    def check_time_location_context(self, query: str) -> str:
        """Extract time and location context from the complaint"""
        query_lower = query.lower()
        # Whether supply was genuinely thin depends on when and where the rider tried
        if any(w in query_lower for w in ['midnight', 'late night', '3 am', 'early morning', 'dawn']):
            return "OFF_PEAK_HOURS_LOW_SUPPLY"
        elif any(w in query_lower for w in ['rush hour', 'peak', 'morning', 'evening', 'office']):
            return "PEAK_HOURS_HIGH_DEMAND"
        elif any(w in query_lower for w in ['outskirts', 'remote', 'village', 'highway', 'far']):
            return "LOW_COVERAGE_AREA"
        elif any(w in query_lower for w in ['airport', 'station', 'mall', 'city centre', 'city center']):
            return "HIGH_COVERAGE_AREA"
        return "CONTEXT_NOT_SPECIFIED"

    def assess_availability_impact(self, analysis: str, query: str) -> str:
        """Assess how the availability issue impacted the customer"""
        if any(w in query.lower() for w in ['missed', 'late', 'appointment', 'flight']):
            return "HIGH_IMPACT_MISSED_COMMITMENT"
        return "MODERATE_INCONVENIENCE"

    def decide_availability_resolution(self, analysis: str, impact: str, credibility: int) -> str:
        """Decide resolution for availability issue"""
        if impact == "HIGH_IMPACT_MISSED_COMMITMENT" and credibility >= 6:
            return "PRIORITY_BOOKING_CREDIT_COMPENSATION"
        # A missed commitment is compensated on its own weight, not on standing alone
        elif impact == "HIGH_IMPACT_MISSED_COMMITMENT" and credibility >= 4:
            return "VOUCHER_CREDIT_ISSUED"
        elif analysis == "REMOTE_AREA_SHORTAGE" and credibility >= 5:
            return "VOUCHER_CREDIT_ISSUED"
        elif credibility >= 5:
            return "VOUCHER_CREDIT_ISSUED"
        return "SERVICE_IMPROVEMENT_ACKNOWLEDGMENT"

    def generate_availability_response(self, decision: str, analysis: str, impact: str, query: str) -> str:
        """Generate availability issue response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_driver_availability",
                    user_query=f"DECISION: {decision} | ISSUE: {analysis} | IMPACT: {impact} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "PRIORITY_BOOKING_CREDIT_COMPENSATION": "We sincerely apologize for the driver unavailability during your critical time. Priority booking status has been activated on your account and compensation credit applied.",
            "VOUCHER_CREDIT_ISSUED": "We're sorry about the lack of available drivers. A voucher credit has been added to your account for future bookings.",
            "SERVICE_IMPROVEMENT_ACKNOWLEDGMENT": "Thank you for reporting the driver availability issue. Your feedback helps us improve service coverage in your area."
        }
        return responses.get(decision, "Your driver availability complaint has been logged for service improvement.")

    def analyze_driver_cancellation(self, query: str) -> str:
        """Identify the cancellation pattern"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['multiple', 'several', 'many times', 'again and again']):
            return "MULTIPLE_DRIVER_CANCELLATIONS"
        elif any(w in query_lower for w in ['just before', 'arrived then', 'after accepting']):
            return "LATE_CANCELLATION_AFTER_ACCEPT"
        return "SINGLE_DRIVER_CANCELLATION"

    def assess_cancellation_disruption(self, analysis: str, query: str) -> str:
        """Assess how disruptive the cancellations were"""
        if analysis == "MULTIPLE_DRIVER_CANCELLATIONS":
            return "HIGHLY_DISRUPTIVE"
        return "MODERATELY_DISRUPTIVE"

    def check_repeat_cancellation_pattern(self, query: str) -> str:
        """Identify if multiple drivers cancelled in succession"""
        if any(w in query.lower() for w in ['3', 'four', 'five', 'multiple', 'several']):
            return "SYSTEMATIC_CANCELLATION_PATTERN"
        return "ISOLATED_CANCELLATION"

    def decide_cancellation_resolution(self, analysis: str, disruption: str, pattern: str, credibility: int) -> str:
        """Decide resolution for driver cancellations"""
        # A systematic pattern is a supply problem on our side, not bad luck for this rider
        if pattern == "SYSTEMATIC_CANCELLATION_PATTERN":
            return "FULL_COMPENSATION_GUARANTEED_RIDE"
        elif disruption == "HIGHLY_DISRUPTIVE" and credibility >= 6:
            return "FULL_COMPENSATION_GUARANTEED_RIDE"
        elif analysis == "MULTIPLE_DRIVER_CANCELLATIONS":
            return "CREDIT_AND_PRIORITY_REBOOKING"
        elif analysis == "LATE_CANCELLATION_AFTER_ACCEPT" and credibility >= 5:
            return "CREDIT_AND_PRIORITY_REBOOKING"
        elif credibility >= 5:
            return "CREDIT_AND_PRIORITY_REBOOKING"
        return "APOLOGY_WITH_REBOOKING_HELP"

    def generate_cancellation_response(self, decision: str, analysis: str, disruption: str, query: str) -> str:
        """Generate driver cancellation response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_driver_cancellations",
                    user_query=f"DECISION: {decision} | CANCELLATION: {analysis} | DISRUPTION: {disruption} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "FULL_COMPENSATION_GUARANTEED_RIDE": "We sincerely apologize for the repeated cancellations. Full compensation has been applied and our team is manually assigning you a guaranteed driver.",
            "CREDIT_AND_PRIORITY_REBOOKING": "We're sorry about the cancellation. Priority rebooking credit has been added to your account to ensure your next booking gets confirmed immediately.",
            "APOLOGY_WITH_REBOOKING_HELP": "We apologize for the cancellation inconvenience. Please try rebooking and our system will prioritize matching you with a reliable driver."
        }
        return responses.get(decision, "Your cancellation complaint is noted and we are working to improve driver reliability.")

    def analyze_late_arrival_no_show(self, query: str) -> str:
        """Determine if this is a late arrival or complete no-show"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['never came', 'never showed', 'no show', "didn't come", 'disappeared']):
            return "DRIVER_NO_SHOW"
        elif any(w in query_lower for w in ['very late', 'extremely late', 'hour late']):
            return "SIGNIFICANTLY_LATE_ARRIVAL"
        return "MODERATELY_LATE_ARRIVAL"

    def quantify_delay(self, analysis: str, query: str) -> str:
        """Estimate the delay duration from the complaint"""
        import re
        time_match = re.search(r'(\d+)\s*(minute|hour|min)', query.lower())
        if time_match:
            return f"DELAY_{time_match.group(1)}_{time_match.group(2).upper()}"
        if analysis == "DRIVER_NO_SHOW":
            return "FULL_WAIT_TIME_WASTED"
        return "UNQUANTIFIED_DELAY"

    def assess_downstream_impact(self, delay: str, query: str) -> str:
        """Assess what was affected by the late arrival or no-show"""
        if any(w in query.lower() for w in ['flight', 'hospital', 'interview', 'meeting', 'appointment']):
            return "CRITICAL_COMMITMENT_MISSED"
        return "GENERAL_INCONVENIENCE"

    def decide_late_arrival_resolution(self, analysis: str, delay: str, impact: str, credibility: int) -> str:
        """Decide compensation for late arrival or no-show"""
        # A no-show wastes the rider's entire wait, so the delay signal itself is enough
        if delay == "FULL_WAIT_TIME_WASTED":
            return "FULL_REFUND_PRIORITY_COMPENSATION"
        elif analysis == "DRIVER_NO_SHOW" and credibility >= 6:
            return "FULL_REFUND_PRIORITY_COMPENSATION"
        elif impact == "CRITICAL_COMMITMENT_MISSED" and credibility >= 5:
            return "SIGNIFICANT_COMPENSATION_ISSUED"
        # A delay the rider could put a number on is concrete enough to credit
        elif delay.startswith("DELAY_") and credibility >= 4:
            return "STANDARD_CREDIT_ISSUED"
        elif credibility >= 5:
            return "STANDARD_CREDIT_ISSUED"
        return "INVESTIGATION_AND_APOLOGY"

    def generate_late_arrival_response(self, decision: str, analysis: str, delay: str, query: str) -> str:
        """Generate late arrival or no-show response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_late_arrivals_no_shows",
                    user_query=f"DECISION: {decision} | INCIDENT: {analysis} | DELAY: {delay} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "FULL_REFUND_PRIORITY_COMPENSATION": "We are extremely sorry for the no-show. This is unacceptable. A full refund and priority compensation credit have been applied. The driver has been flagged for investigation.",
            "SIGNIFICANT_COMPENSATION_ISSUED": "We sincerely apologize for the critical delay to your important commitment. Significant compensation has been issued and a formal complaint lodged against the driver.",
            "STANDARD_CREDIT_ISSUED": "We apologize for the late arrival. A credit has been added to your account as compensation for the wait.",
            "INVESTIGATION_AND_APOLOGY": "We're sorry for the late arrival. Our team is reviewing the driver's performance record and will take appropriate action."
        }
        return responses.get(decision, "Your late arrival complaint has been logged and the driver notified.")
