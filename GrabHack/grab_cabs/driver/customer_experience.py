"""
Grab Cabs Driver Customer Experience Handler (Driver's POV)
Uses AI models for intelligent complaint resolution
"""

import logging
import os
import sys
from typing import Optional

# Add parent directory to path to import enhanced_ai_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class CustomerExperienceHandler:
    """Driver-focused customer experience management with real AI (Driver's POV)"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_cabs"
        self.actor = "driver"
        self.handler_type = "customer_experience_handler"
        try:
            self.ai_engine = EnhancedAgenticAIEngine()
        except Exception as e:
            logger.warning(f"AI engine initialization failed: {e}")
            self.ai_engine = None
        
    def handle_passenger_harassment_complaint(self, query: str, harassment_type: str = None, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle passenger harassment complaints with flat 5-step workflow"""
        logger.info(f"Processing passenger harassment complaint - Type: {harassment_type}")

        # Step 1: Identify harassment type and severity from query and explicit type param
        harassment_analysis = self.analyze_harassment_type(query, harassment_type)

        # Step 2: Check incident context and evidence availability
        incident_context = self.check_harassment_incident_context(harassment_analysis, query)

        # Step 3: Check driver credibility score
        credibility_score = self.get_credibility_score(username)

        # Step 4: Decide escalation and response action based on severity and credibility
        decision = self.decide_harassment_resolution(harassment_analysis, incident_context, credibility_score)

        # Step 5: Generate empathetic response with safety info, actions, and next steps
        response = self.generate_harassment_response(decision, harassment_analysis, query, image_data)
        return response

    def handle_false_complaint_rating_reduction(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle false complaints that reduced driver rating with strict 5-step workflow"""
        logger.info(f"Processing false complaint rating reduction complaint: {query[:100]}...")

        # Step 1: Identify the type of false complaint reported
        complaint_analysis = self.analyze_false_complaint_type(query)
        logger.info(f"False complaint analysis: {complaint_analysis}")

        # Step 2: Check whether counter-evidence or trip data supports the driver
        evidence_check = self.check_driver_counter_evidence(complaint_analysis, query)
        logger.info(f"Evidence check: {evidence_check}")

        # Step 3: Check driver credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Driver credibility: {credibility_score}/10")

        # Step 4: Decide on rating review and complaint flagging action
        decision = self.decide_false_complaint_resolution(complaint_analysis, evidence_check, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with rating protection and investigation details
        response = self.generate_false_complaint_response(decision, complaint_analysis, query, image_data)
        logger.info("False complaint rating reduction response generated successfully")
        return response

    def handle_unresolved_passenger_disputes(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle escalation of unresolved passenger disputes with strict 5-step workflow"""
        logger.info(f"Processing unresolved passenger disputes complaint: {query[:100]}...")

        # Step 1: Identify the nature of the unresolved dispute
        dispute_analysis = self.analyze_dispute_type(query)
        logger.info(f"Dispute analysis: {dispute_analysis}")

        # Step 2: Assess the severity and financial impact of the dispute
        dispute_severity = self.assess_dispute_severity(dispute_analysis, query)
        logger.info(f"Dispute severity: {dispute_severity}")

        # Step 3: Check driver credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Driver credibility: {credibility_score}/10")

        # Step 4: Decide on escalation and resolution path
        decision = self.decide_dispute_resolution(dispute_analysis, dispute_severity, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with escalation confirmation and next steps
        response = self.generate_dispute_response(decision, dispute_analysis, query, image_data)
        logger.info("Unresolved passenger disputes response generated successfully")
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
        import os
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

    def analyze_harassment_type(self, query: str, harassment_type: str = None) -> str:
        """Identify harassment type from explicit param or query text"""
        if harassment_type:
            return harassment_type.upper().replace(" ", "_")
        query_lower = query.lower()
        if any(w in query_lower for w in ['threat', 'threaten', 'kill', 'harm']):
            return "THREATS"
        elif any(w in query_lower for w in ['physical', 'hit', 'assault', 'punch', 'attack']):
            return "PHYSICAL_ABUSE"
        elif any(w in query_lower for w in ['stalk', 'follow', 'track']):
            return "STALKING"
        elif any(w in query_lower for w in ['inappropriate', 'sexual', 'touch', 'grope']):
            return "INAPPROPRIATE_BEHAVIOUR"
        return "VERBAL_ABUSE"

    def check_harassment_incident_context(self, harassment_type: str, query: str) -> dict:
        """Check incident context: severity, whether evidence is present, safety status"""
        high_severity_types = {"THREATS", "PHYSICAL_ABUSE", "STALKING"}
        return {
            "severity": "HIGH" if harassment_type in high_severity_types else "MODERATE",
            "has_evidence": bool(query and len(query) > 20),
            "immediate_danger": harassment_type in {"THREATS", "PHYSICAL_ABUSE"},
        }

    def decide_harassment_resolution(self, harassment_type: str, context: dict, credibility: int) -> str:
        """Decide escalation tier based on harassment severity and driver credibility"""
        if context.get("immediate_danger"):
            return "EMERGENCY_ESCALATION"
        # Stalking is an ongoing safety risk to the driver even once the trip is over
        if harassment_type == "STALKING":
            return "PRIORITY_CASE_OPENED"
        if context.get("severity") == "HIGH" and credibility >= 6:
            return "PRIORITY_CASE_OPENED"
        if harassment_type in ("VERBAL_ABUSE", "INAPPROPRIATE_BEHAVIOUR") and credibility >= 5:
            return "STANDARD_INVESTIGATION"
        if credibility >= 5:
            return "STANDARD_INVESTIGATION"
        return "CASE_LOGGED_REVIEW"

    def generate_harassment_response(self, decision: str, harassment_type: str, query: str, image_data: Optional[str]) -> str:
        """Generate empathetic harassment response with AI or fallback template"""
        display_type = harassment_type.replace("_", " ").title()
        case_ref = f"GC-DRIVER-HARASSMENT-{harassment_type}-001"

        if self.ai_engine:
            try:
                ai_context = (
                    f"HARASSMENT TYPE: {display_type}\n"
                    f"DECISION: {decision}\n"
                    f"DRIVER DESCRIPTION: {query}\n"
                    f"IMAGE PROVIDED: {'Yes - analyze for evidence' if image_data else 'No'}\n\n"
                    "Generate a personalized, empathetic response for a driver-partner that: "
                    "acknowledges their specific situation, validates their experience, "
                    "provides relevant safety advice, and gives specific next steps. "
                    "Address income protection concerns and provide driver support resources."
                )
                ai_response = self.ai_engine.process_complaint(
                    function_name="handle_passenger_harassment_complaint",
                    user_query=ai_context,
                    service=self.service,
                    user_type=self.actor,
                    image_data=image_data,
                )
                return (
                    f"{ai_response}\n\n"
                    f"**Case Reference:** {case_ref}\n"
                    "**Emergency Support:** Grab Driver Safety: 1-800-GRAB-DRIVER | Crisis Support: 1-800-273-8255"
                )
            except Exception as e:
                logger.error(f"AI failed for harassment response: {e}")

        templates = {
            "EMERGENCY_ESCALATION": (
                f"We are treating your {display_type} report as an emergency. "
                "Driver safety team has been notified immediately. "
                "The passenger has been suspended pending investigation. "
                "If you are in immediate danger, please call emergency services (911). "
                f"Income protection is activated. Case Reference: {case_ref}"
            ),
            "PRIORITY_CASE_OPENED": (
                f"We are deeply sorry you experienced {display_type}. "
                "A priority case has been opened and you will receive a response within 2 hours. "
                "The passenger has been temporarily suspended. "
                f"Your earnings are protected during the investigation. Case Reference: {case_ref}"
            ),
            "STANDARD_INVESTIGATION": (
                f"Your {display_type} report has been received and an investigation has been opened. "
                "Our driver relations team will review trip data and respond within 24 hours. "
                f"Case Reference: {case_ref}"
            ),
            "CASE_LOGGED_REVIEW": (
                f"Your {display_type} report has been logged. "
                "Our team will review and contact you within 48 hours. "
                f"Case Reference: {case_ref}"
            ),
        }
        return templates.get(decision, f"Your harassment report has been received. Case Reference: {case_ref}")

    def analyze_false_complaint_type(self, query: str) -> str:
        """Identify what type of false complaint was filed against the driver"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['rude', 'behaviour', 'attitude']):
            return "FALSE_RUDE_BEHAVIOUR_COMPLAINT"
        elif any(w in query_lower for w in ['route', 'overcharge', 'fare']):
            return "FALSE_OVERCHARGING_COMPLAINT"
        elif any(w in query_lower for w in ['late', 'delay', 'slow']):
            return "FALSE_DELAY_COMPLAINT"
        return "GENERAL_FALSE_COMPLAINT"

    def check_driver_counter_evidence(self, analysis: str, query: str) -> str:
        """Check if trip data or evidence supports the driver's counter-claim"""
        query_lower = query.lower()
        # Dashcam or trip data the driver can point to is what makes a counter-claim checkable
        if any(w in query_lower for w in ['dashcam', 'dash cam', 'recording', 'video', 'camera']):
            return "RECORDED_EVIDENCE_AVAILABLE"
        elif any(w in query_lower for w in ['gps', 'trip id', 'booking id', 'route log', 'tracking']):
            return "TRIP_DATA_SUPPORTS_DRIVER"
        elif any(w in query_lower for w in ['passenger', 'witness', 'co-passenger', 'another rider']):
            return "WITNESS_ACCOUNT_OFFERED"
        return "DRIVER_STATEMENT_ONLY"

    def decide_false_complaint_resolution(self, analysis: str, evidence: str, credibility: int) -> str:
        """Decide rating review and complaint flagging action"""
        # Recorded evidence or trip data settles the dispute without waiting on standing
        if evidence in ("RECORDED_EVIDENCE_AVAILABLE", "TRIP_DATA_SUPPORTS_DRIVER") and credibility >= 5:
            return "RATING_RESTORED_COMPLAINT_FLAGGED"
        elif credibility >= 7:
            return "RATING_RESTORED_COMPLAINT_FLAGGED"
        elif evidence == "WITNESS_ACCOUNT_OFFERED" and credibility >= 4:
            return "INVESTIGATION_INITIATED_TEMPORARY_PROTECTION"
        elif analysis == "FALSE_OVERCHARGING_COMPLAINT" and credibility >= 5:
            # Fare claims are checkable against our own billing records
            return "RATING_RESTORED_COMPLAINT_FLAGGED"
        elif credibility >= 5:
            return "INVESTIGATION_INITIATED_TEMPORARY_PROTECTION"
        return "COMPLAINT_LOGGED_UNDER_REVIEW"

    def generate_false_complaint_response(self, decision: str, analysis: str, query: str, image_data: Optional[str]) -> str:
        """Generate false complaint response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_false_complaint_rating_reduction",
                    user_query=f"DECISION: {decision} | COMPLAINT_TYPE: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor, image_data=image_data
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "RATING_RESTORED_COMPLAINT_FLAGGED": "We have reviewed the trip data and found the complaint to be unsubstantiated. Your rating has been restored and the false complaint has been flagged on the passenger's account.",
            "INVESTIGATION_INITIATED_TEMPORARY_PROTECTION": "A full investigation has been initiated. Your rating is temporarily protected during the review period and you will not be penalised while we investigate.",
            "COMPLAINT_LOGGED_UNDER_REVIEW": "Your counter-complaint has been logged. Our driver relations team will review the trip records and respond within 48 hours."
        }
        return responses.get(decision, "Your false complaint appeal has been received and is under review. We will update you within 48 hours.")

    def analyze_dispute_type(self, query: str) -> str:
        """Identify the nature of the unresolved passenger dispute"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['fare', 'payment', 'money', 'charge']):
            return "FARE_PAYMENT_DISPUTE"
        elif any(w in query_lower for w in ['rating', 'review', 'feedback']):
            return "RATING_REVIEW_DISPUTE"
        elif any(w in query_lower for w in ['behaviour', 'harassment', 'rude']):
            return "PASSENGER_BEHAVIOUR_DISPUTE"
        return "GENERAL_PASSENGER_DISPUTE"

    def assess_dispute_severity(self, analysis: str, query: str) -> str:
        """Assess the severity and impact of the unresolved dispute"""
        high_severity = ["PASSENGER_BEHAVIOUR_DISPUTE", "FARE_PAYMENT_DISPUTE"]
        return "HIGH_SEVERITY" if analysis in high_severity else "MODERATE_SEVERITY"

    def decide_dispute_resolution(self, analysis: str, severity: str, credibility: int) -> str:
        """Decide escalation path for the unresolved dispute"""
        if severity == "HIGH_SEVERITY" and credibility >= 6:
            return "SENIOR_CASE_MANAGER_ASSIGNED"
        # A passenger-behaviour dispute affects the driver's safety record, so it gets
        # a named owner rather than sitting in the general queue
        elif analysis == "PASSENGER_BEHAVIOUR_DISPUTE" and credibility >= 5:
            return "SENIOR_CASE_MANAGER_ASSIGNED"
        elif analysis in ("FARE_PAYMENT_DISPUTE", "RATING_REVIEW_DISPUTE") and credibility >= 4:
            return "FORMAL_INVESTIGATION_OPENED"
        elif credibility >= 5:
            return "FORMAL_INVESTIGATION_OPENED"
        return "STANDARD_DISPUTE_REVIEW"

    def generate_dispute_response(self, decision: str, analysis: str, query: str, image_data: Optional[str]) -> str:
        """Generate unresolved dispute response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_unresolved_passenger_disputes",
                    user_query=f"DECISION: {decision} | DISPUTE: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor, image_data=image_data
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "SENIOR_CASE_MANAGER_ASSIGNED": "Given the severity of this dispute, a senior case manager has been assigned to your case. They will contact you within 2 hours with a full resolution plan.",
            "FORMAL_INVESTIGATION_OPENED": "A formal investigation has been opened for your dispute. All trip data, GPS records, and communication logs are being reviewed. You will receive an update within 24 hours.",
            "STANDARD_DISPUTE_REVIEW": "Your dispute has been escalated to our driver relations team. They will review all available evidence and provide a resolution within 3 business days."
        }
        return responses.get(decision, "Your dispute escalation has been received. Our team will review and contact you within 48 hours.")