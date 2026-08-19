"""
Grab Cabs Driver Vehicle Issues Handler
Uses AI models for intelligent complaint resolution with strict workflows
"""

import logging
import os
import sys
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class DriverVehicleIssuesHandler:
    """Driver-focused vehicle issues management with strict workflows"""

    def __init__(self, groq_api_key: str = None):
        self.service = "grab_cabs"
        self.actor = "driver"
        self.handler_type = "driver_vehicle_issues_handler"
        try:
            self.ai_engine = EnhancedAgenticAIEngine()
        except Exception as e:
            logger.warning(f"AI engine initialization failed: {e}")
            self.ai_engine = None

    def handle_vehicle_breakdown_during_ride(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle vehicle breakdown during ride with strict 5-step workflow"""
        logger.info(f"Processing vehicle breakdown complaint: {query[:100]}...")

        # Step 1: Identify the type and severity of breakdown
        breakdown_analysis = self.analyze_breakdown_type(query)
        logger.info(f"Breakdown analysis: {breakdown_analysis}")

        # Step 2: Assess safety and passenger impact
        safety_assessment = self.assess_breakdown_safety(breakdown_analysis, query)
        logger.info(f"Safety assessment: {safety_assessment}")

        # Step 3: Check driver credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Driver credibility: {credibility_score}/10")

        # Step 4: Decide on support and earnings protection
        decision = self.decide_breakdown_resolution(breakdown_analysis, safety_assessment, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with roadside support details
        response = self.generate_breakdown_response(decision, breakdown_analysis, safety_assessment, query, image_data)
        logger.info("Vehicle breakdown response generated successfully")
        return response

    def handle_passenger_damage_coverage(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle passenger damage to vehicle with strict 5-step workflow"""
        logger.info(f"Processing passenger damage coverage complaint: {query[:100]}...")

        # Step 1: Identify the type of damage reported
        damage_analysis = self.analyze_damage_type(query)
        logger.info(f"Damage analysis: {damage_analysis}")

        # Step 2: Check whether photo evidence is provided
        evidence_check = self.check_damage_evidence(damage_analysis, image_data)
        logger.info(f"Evidence check: {evidence_check}")

        # Step 3: Check driver credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Driver credibility: {credibility_score}/10")

        # Step 4: Decide on coverage and passenger action
        decision = self.decide_damage_coverage(damage_analysis, evidence_check, credibility_score)
        logger.info(f"Coverage decision: {decision}")

        # Step 5: Generate response with repair support and next steps
        response = self.generate_damage_response(decision, damage_analysis, query, image_data)
        logger.info("Passenger damage response generated successfully")
        return response

    def handle_insurance_fuel_maintenance_support(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle insurance/fuel/maintenance support with strict 5-step workflow"""
        logger.info(f"Processing insurance/fuel/maintenance complaint: {query[:100]}...")

        # Step 1: Identify the support type requested
        support_analysis = self.analyze_support_request(query)
        logger.info(f"Support analysis: {support_analysis}")

        # Step 2: Check eligibility for the requested support
        eligibility_check = self.check_support_eligibility(support_analysis, query)
        logger.info(f"Eligibility check: {eligibility_check}")

        # Step 3: Check driver credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Driver credibility: {credibility_score}/10")

        # Step 4: Decide on support provision level
        decision = self.decide_support_provision(support_analysis, eligibility_check, credibility_score)
        logger.info(f"Support decision: {decision}")

        # Step 5: Generate response with support details and next steps
        response = self.generate_support_response(decision, support_analysis, query)
        logger.info("Insurance/fuel/maintenance response generated successfully")
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

    def analyze_breakdown_type(self, query: str) -> str:
        """Identify the type of vehicle breakdown"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['tyre', 'tire', 'flat', 'puncture']):
            return "TYRE_PUNCTURE"
        elif any(w in query_lower for w in ['engine', 'overheating', 'smoke']):
            return "ENGINE_FAILURE"
        elif any(w in query_lower for w in ['battery', 'dead', 'start', 'electrical']):
            return "BATTERY_ELECTRICAL_FAILURE"
        elif any(w in query_lower for w in ['accident', 'collision', 'crash']):
            return "ACCIDENT_BREAKDOWN"
        return "GENERAL_BREAKDOWN"

    def assess_breakdown_safety(self, analysis: str, query: str) -> str:
        """Assess the safety situation during the breakdown"""
        high_risk = ["ACCIDENT_BREAKDOWN", "ENGINE_FAILURE"]
        if analysis in high_risk:
            return "HIGH_RISK_SITUATION"
        if any(w in query.lower() for w in ['highway', 'expressway', 'dark', 'unsafe']):
            return "HIGH_RISK_SITUATION"
        return "MANAGEABLE_SITUATION"

    def decide_breakdown_resolution(self, analysis: str, safety: str, credibility: int) -> str:
        """Decide resolution for vehicle breakdown"""
        # A breakdown from an accident is an emergency regardless of standing
        if analysis == "ACCIDENT_BREAKDOWN":
            return "EMERGENCY_ROADSIDE_FULL_EARNINGS_PROTECTION"
        elif safety == "HIGH_RISK_SITUATION" and credibility >= 6:
            return "EMERGENCY_ROADSIDE_FULL_EARNINGS_PROTECTION"
        elif analysis in ("ENGINE_FAILURE", "BATTERY_ELECTRICAL_FAILURE") and credibility >= 5:
            return "ROADSIDE_ASSISTANCE_TRIP_COMPENSATION"
        elif credibility >= 5:
            return "ROADSIDE_ASSISTANCE_TRIP_COMPENSATION"
        return "STANDARD_ROADSIDE_SUPPORT"

    def generate_breakdown_response(self, decision: str, analysis: str, safety: str, query: str, image_data: Optional[str]) -> str:
        """Generate vehicle breakdown response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_vehicle_breakdown_during_ride",
                    user_query=f"DECISION: {decision} | BREAKDOWN: {analysis} | SAFETY: {safety} | QUERY: {query}",
                    service=self.service, user_type=self.actor, image_data=image_data
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "EMERGENCY_ROADSIDE_FULL_EARNINGS_PROTECTION": "Emergency! Your safety is our priority. Roadside assistance is being dispatched immediately. The trip has been cancelled without penalty and full earnings protection has been activated for this trip.",
            "ROADSIDE_ASSISTANCE_TRIP_COMPENSATION": "Roadside assistance has been requested. Trip compensation for lost earnings has been applied to your account and the passenger has been reassigned.",
            "STANDARD_ROADSIDE_SUPPORT": "Roadside assistance is on the way. Please stay safe and contact our 24/7 support line if the situation becomes dangerous."
        }
        return responses.get(decision, "Your breakdown has been logged. Roadside assistance is being arranged immediately.")

    def analyze_damage_type(self, query: str) -> str:
        """Identify the type of damage caused by the passenger"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['vomit', 'sick', 'spill', 'stain']):
            return "SOILING_DAMAGE"
        elif any(w in query_lower for w in ['scratch', 'dent', 'door', 'broken']):
            return "PHYSICAL_DAMAGE"
        elif any(w in query_lower for w in ['theft', 'stole', 'missing', 'taken']):
            return "THEFT_OR_MISSING_ITEMS"
        return "GENERAL_PASSENGER_DAMAGE"

    def check_damage_evidence(self, analysis: str, image_data: Optional[str]) -> str:
        """Check if photo evidence is available for the damage claim"""
        if image_data:
            return "PHOTO_EVIDENCE_PROVIDED"
        if analysis in ["PHYSICAL_DAMAGE", "SOILING_DAMAGE"]:
            return "EVIDENCE_REQUIRED_FOR_FULL_CLAIM"
        return "NO_EVIDENCE_TEXT_ONLY"

    def decide_damage_coverage(self, analysis: str, evidence: str, credibility: int) -> str:
        """Decide coverage action for passenger-caused damage"""
        if evidence == "PHOTO_EVIDENCE_PROVIDED" and credibility >= 6:
            return "FULL_REPAIR_COST_COVERED_PASSENGER_CHARGED"
        # Theft is a police matter, not a repair claim, so it is investigated before payout
        elif analysis == "THEFT_OR_MISSING_ITEMS":
            return "INVESTIGATION_REQUIRED_BEFORE_PAYOUT"
        elif analysis == "SOILING_DAMAGE" and evidence == "PHOTO_EVIDENCE_PROVIDED":
            return "FULL_REPAIR_COST_COVERED_PASSENGER_CHARGED"
        elif credibility >= 5:
            return "PARTIAL_COVERAGE_INVESTIGATION_INITIATED"
        return "INVESTIGATION_REQUIRED_BEFORE_PAYOUT"

    def generate_damage_response(self, decision: str, analysis: str, query: str, image_data: Optional[str]) -> str:
        """Generate passenger damage coverage response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_passenger_damage_coverage",
                    user_query=f"DECISION: {decision} | DAMAGE: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor, image_data=image_data
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "FULL_REPAIR_COST_COVERED_PASSENGER_CHARGED": "We have confirmed your damage claim. Full repair costs will be covered and the passenger has been charged accordingly. The amount will reflect in your next payout.",
            "PARTIAL_COVERAGE_INVESTIGATION_INITIATED": "We are investigating your damage claim. Partial coverage has been applied pending full review. The passenger account has been flagged for investigation.",
            "INVESTIGATION_REQUIRED_BEFORE_PAYOUT": "Your damage report has been logged. Please upload photos of the damage to expedite your claim. Our team will contact you within 24 hours."
        }
        return responses.get(decision, "Your damage claim is under review. Please upload photos if you have them to speed up the process.")

    def analyze_support_request(self, query: str) -> str:
        """Identify the type of vehicle support being requested"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['insurance', 'claim', 'cover']):
            return "INSURANCE_SUPPORT"
        elif any(w in query_lower for w in ['fuel', 'petrol', 'gas', 'diesel']):
            return "FUEL_SUPPORT"
        elif any(w in query_lower for w in ['service', 'maintenance', 'repair', 'inspection']):
            return "MAINTENANCE_SUPPORT"
        return "GENERAL_VEHICLE_SUPPORT"

    def check_support_eligibility(self, analysis: str, query: str) -> str:
        """Check driver eligibility for the requested support type"""
        query_lower = query.lower()
        # An active claim or an off-road vehicle is the urgent case; a general enquiry
        # about a scheme is not, and should get guidance rather than a payout
        if any(w in query_lower for w in ['accident', 'claim', 'damaged', 'breakdown', 'not working']):
            return "ACTIVE_INCIDENT_SUPPORT_REQUIRED"
        elif any(w in query_lower for w in ['urgent', 'today', 'stranded', 'cannot drive', "can't drive"]):
            return "URGENT_SUPPORT_REQUIRED"
        elif any(w in query_lower for w in ['how do i', 'what is', 'eligible', 'explain', 'policy']):
            return "INFORMATION_REQUEST_ONLY"
        return "STANDARD_SUPPORT_ELIGIBLE"

    def decide_support_provision(self, analysis: str, eligibility: str, credibility: int) -> str:
        """Decide the level of support to provide"""
        # A driver only asking how a scheme works gets an explanation, not a disbursement
        if eligibility == "INFORMATION_REQUEST_ONLY":
            return "INFORMATION_AND_GUIDANCE_PROVIDED"
        elif eligibility in ("ACTIVE_INCIDENT_SUPPORT_REQUIRED", "URGENT_SUPPORT_REQUIRED") and analysis == "INSURANCE_SUPPORT":
            return "FULL_INSURANCE_CLAIM_ASSISTANCE"
        elif analysis == "INSURANCE_SUPPORT" and credibility >= 6:
            return "FULL_INSURANCE_CLAIM_ASSISTANCE"
        elif analysis == "FUEL_SUPPORT" and credibility >= 5:
            return "FUEL_CREDIT_ISSUED"
        elif analysis == "MAINTENANCE_SUPPORT":
            return "MAINTENANCE_PARTNER_REFERRAL"
        return "INFORMATION_AND_GUIDANCE_PROVIDED"

    def generate_support_response(self, decision: str, analysis: str, query: str) -> str:
        """Generate insurance/fuel/maintenance support response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_insurance_fuel_maintenance_support",
                    user_query=f"DECISION: {decision} | SUPPORT_TYPE: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "FULL_INSURANCE_CLAIM_ASSISTANCE": "Our insurance team will assist you with your claim. A dedicated case manager has been assigned and will contact you within 2 hours with next steps.",
            "FUEL_CREDIT_ISSUED": "A fuel credit has been issued to your GrabPay wallet to cover emergency fuel needs. This will reflect within the hour.",
            "MAINTENANCE_PARTNER_REFERRAL": "We have connected you with our preferred maintenance partner who offers exclusive discounts for Grab drivers. They will contact you shortly.",
            "INFORMATION_AND_GUIDANCE_PROVIDED": "Our driver support team has reviewed your request. Check your driver app inbox for detailed guidance on the next steps."
        }
        return responses.get(decision, "Your vehicle support request has been logged and our team will follow up shortly.")
