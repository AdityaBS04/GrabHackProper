"""
Grab Cabs Customer Driver & Vehicle Issues Handler
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
    """Customer-focused driver and vehicle issues management with strict workflows"""

    def __init__(self, groq_api_key: str = None):
        self.service = "grab_cabs"
        self.actor = "customer"
        self.handler_type = "driver_vehicle_issues_handler"
        try:
            self.ai_engine = EnhancedAgenticAIEngine()
        except Exception as e:
            logger.warning(f"AI engine initialization failed: {e}")
            self.ai_engine = None

    def handle_unsafe_driving_behavior(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle unsafe driving behavior with strict 6-step workflow - IMAGE SUPPORTED"""
        logger.info(f"Processing unsafe driving behavior complaint: {query[:100]}...")

        # Step 1: Analyze the safety incident from customer description
        safety_analysis = self.analyze_safety_incident(query)
        logger.info(f"Safety analysis: {safety_analysis}")

        # Step 2: Extract driver and trip details from the complaint
        trip_details = self.extract_trip_details(query)
        logger.info(f"Trip details extracted: {trip_details}")

        # Step 3: Assess severity of the unsafe behavior reported
        severity = self.assess_driving_severity(safety_analysis, query)
        logger.info(f"Severity assessment: {severity}")

        # Step 4: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 5: Make resolution decision based on severity and credibility
        decision = self.decide_safety_resolution(severity, credibility_score, safety_analysis)
        logger.info(f"Resolution decision: {decision}")

        # Step 6: Generate response with appropriate actions and compensation
        response = self.generate_safety_response(decision, severity, safety_analysis, query, image_data)
        logger.info(f"Unsafe driving response generated successfully")

        return response

    def handle_vehicle_problems(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle vehicle condition problems with strict 6-step workflow - IMAGE SUPPORTED"""
        logger.info(f"Processing vehicle problems complaint: {query[:100]}...")

        # Step 1: Identify the type and nature of vehicle problem
        problem_analysis = self.analyze_vehicle_problem(query)
        logger.info(f"Vehicle problem analysis: {problem_analysis}")

        # Step 2: Check if problem affected ride safety or comfort
        impact_assessment = self.assess_vehicle_problem_impact(problem_analysis, query)
        logger.info(f"Impact assessment: {impact_assessment}")

        # Step 3: Validate standards violation based on reported condition
        standards_check = self.validate_vehicle_standards(problem_analysis)
        logger.info(f"Standards validation: {standards_check}")

        # Step 4: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 5: Decide compensation and action against driver
        decision = self.decide_vehicle_resolution(problem_analysis, impact_assessment, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 6: Generate comprehensive response with next steps
        response = self.generate_vehicle_response(decision, problem_analysis, impact_assessment, query, image_data)
        logger.info(f"Vehicle problems response generated successfully")

        return response

    def handle_accidents_during_ride(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle accidents during ride with strict 7-step workflow - IMAGE REQUIRED for claims"""
        logger.info(f"Processing accident during ride complaint: {query[:100]}...")

        # Step 1: Assess the accident type and immediate safety situation
        accident_analysis = self.analyze_accident_details(query)
        logger.info(f"Accident analysis: {accident_analysis}")

        # Step 2: Check if medical attention or emergency services were needed
        emergency_assessment = self.assess_emergency_level(accident_analysis, query)
        logger.info(f"Emergency assessment: {emergency_assessment}")

        # Step 3: Validate injury or damage claims
        if not image_data and "damage" in query.lower():
            return "📷 Please upload a photo of the damage or injury so we can process your accident claim with appropriate priority and compensation."

        damage_validation = self.validate_accident_claims(accident_analysis, image_data)
        logger.info(f"Damage validation: {damage_validation}")

        # Step 4: Check insurance coverage applicability
        insurance_check = self.check_insurance_coverage(accident_analysis)
        logger.info(f"Insurance coverage check: {insurance_check}")

        # Step 5: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 6: Make liability and compensation decision
        decision = self.decide_accident_resolution(accident_analysis, emergency_assessment, damage_validation, insurance_check, credibility_score)
        logger.info(f"Accident resolution decision: {decision}")

        # Step 7: Generate comprehensive response with full support package
        response = self.generate_accident_response(decision, accident_analysis, emergency_assessment, query)
        logger.info(f"Accident during ride response generated successfully")

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

    def analyze_safety_incident(self, query: str) -> str:
        """Identify the type of unsafe driving behavior from the complaint"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['rash', 'speeding', 'speed', 'fast']):
            return "SPEEDING_RASH_DRIVING"
        elif any(w in query_lower for w in ['drunk', 'influence', 'alcohol', 'intoxicated']):
            return "DRIVING_UNDER_INFLUENCE"
        elif any(w in query_lower for w in ['phone', 'distracted', 'texting']):
            return "DISTRACTED_DRIVING"
        elif any(w in query_lower for w in ['aggressive', 'road rage', 'threat']):
            return "AGGRESSIVE_DRIVING"
        return "GENERAL_UNSAFE_BEHAVIOR"

    def extract_trip_details(self, query: str) -> str:
        """Extract relevant trip details mentioned in the complaint"""
        query_lower = query.lower()
        # What the rider names about the trip decides how far we can investigate it
        if any(w in query_lower for w in ['trip id', 'booking id', 'ride id', 'order id']):
            return "TRIP_IDENTIFIED_BY_REFERENCE"
        elif any(w in query_lower for w in ['highway', 'road', 'street', 'airport', 'flyover', 'junction']):
            return "ROUTE_LOCATION_DESCRIBED"
        elif any(w in query_lower for w in ['today', 'yesterday', 'last night', 'this morning', 'just now']):
            return "TRIP_TIMEFRAME_DESCRIBED"
        return "NO_SPECIFIC_TRIP_DETAILS"

    def assess_driving_severity(self, safety_analysis: str, query: str) -> str:
        """Assess how severe the unsafe driving behavior was"""
        high_severity = ["DRIVING_UNDER_INFLUENCE", "AGGRESSIVE_DRIVING"]
        if safety_analysis in high_severity:
            return "HIGH_SEVERITY"
        return "MODERATE_SEVERITY"

    def decide_safety_resolution(self, severity: str, credibility_score: int, analysis: str) -> str:
        """Decide the resolution based on severity and customer credibility"""
        # Driving under the influence is a zero-tolerance offence: the driver comes off
        # the road on the report alone, before any credibility weighting
        if analysis == "DRIVING_UNDER_INFLUENCE":
            return "DRIVER_SUSPENDED_FULL_REFUND"
        elif severity == "HIGH_SEVERITY" and credibility_score >= 6:
            return "DRIVER_SUSPENDED_FULL_REFUND"
        elif analysis == "AGGRESSIVE_DRIVING" and credibility_score >= 5:
            return "DRIVER_SUSPENDED_FULL_REFUND"
        elif credibility_score >= 5:
            return "DRIVER_WARNING_PARTIAL_REFUND"
        return "INVESTIGATION_INITIATED"

    def generate_safety_response(self, decision: str, severity: str, analysis: str, query: str, image_data: Optional[str]) -> str:
        """Generate appropriate safety response"""
        if self.ai_engine:
            try:
                context = f"DECISION: {decision} | SEVERITY: {severity} | ANALYSIS: {analysis} | QUERY: {query}"
                return self.ai_engine.process_complaint(
                    function_name="handle_unsafe_driving_behavior",
                    user_query=context,
                    service=self.service,
                    user_type=self.actor,
                    image_data=image_data
                )
            except Exception as e:
                logger.error(f"AI generation failed: {e}")

        if decision == "DRIVER_SUSPENDED_FULL_REFUND":
            return f"Your safety report has been escalated with HIGH priority. The driver has been immediately suspended pending investigation. Full refund processed and safety team notified. Case Reference: GC-SAFETY-{hash(query) % 9999}"
        elif decision == "DRIVER_WARNING_PARTIAL_REFUND":
            return f"We take unsafe driving very seriously. A formal warning has been issued to the driver and a partial refund has been processed. Your feedback helps us maintain safety standards."
        return f"We have received your safety complaint. Our team is investigating the incident and will take appropriate action. You'll receive an update within 24 hours."

    def analyze_vehicle_problem(self, query: str) -> str:
        """Identify the type of vehicle problem"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['dirty', 'smell', 'smelly', 'unclean', 'hygiene']):
            return "CLEANLINESS_ISSUE"
        elif any(w in query_lower for w in ['ac', 'air condition', 'hot', 'cold']):
            return "AC_MALFUNCTION"
        elif any(w in query_lower for w in ['break', 'brake', 'broke down', 'breakdown', 'engine']):
            return "MECHANICAL_BREAKDOWN"
        elif any(w in query_lower for w in ['seatbelt', 'seat belt', 'unsafe']):
            return "SAFETY_EQUIPMENT_MISSING"
        return "GENERAL_VEHICLE_CONDITION"

    def assess_vehicle_problem_impact(self, analysis: str, query: str) -> str:
        """Assess how the vehicle problem impacted the ride"""
        high_impact = ["MECHANICAL_BREAKDOWN", "SAFETY_EQUIPMENT_MISSING"]
        return "HIGH_IMPACT" if analysis in high_impact else "MODERATE_IMPACT"

    def validate_vehicle_standards(self, analysis: str) -> str:
        """Validate against Grab vehicle standards"""
        violations = {
            "CLEANLINESS_ISSUE": "Grab vehicle hygiene standards violated",
            "AC_MALFUNCTION": "Grab comfort standards violated",
            "MECHANICAL_BREAKDOWN": "Grab safety inspection standards violated",
            "SAFETY_EQUIPMENT_MISSING": "Grab mandatory safety equipment standards violated"
        }
        return violations.get(analysis, "Grab general service standards violated")

    def decide_vehicle_resolution(self, analysis: str, impact: str, credibility_score: int) -> str:
        """Decide resolution for vehicle problem"""
        # Missing safety equipment or a mechanical fault makes the vehicle unfit to carry
        # passengers at all, which is a compliance matter rather than a comfort complaint
        if analysis in ("SAFETY_EQUIPMENT_MISSING", "MECHANICAL_BREAKDOWN"):
            return "FULL_REFUND_DRIVER_REVIEW"
        elif impact == "HIGH_IMPACT" and credibility_score >= 6:
            return "FULL_REFUND_DRIVER_REVIEW"
        elif analysis in ("CLEANLINESS_ISSUE", "AC_MALFUNCTION") and credibility_score >= 5:
            return "PARTIAL_REFUND_WARNING"
        elif credibility_score >= 5:
            return "PARTIAL_REFUND_WARNING"
        return "GOODWILL_CREDIT"

    def generate_vehicle_response(self, decision: str, analysis: str, impact: str, query: str, image_data: Optional[str]) -> str:
        """Generate vehicle problem response"""
        if self.ai_engine:
            try:
                context = f"DECISION: {decision} | VEHICLE_ISSUE: {analysis} | IMPACT: {impact} | QUERY: {query}"
                return self.ai_engine.process_complaint(
                    function_name="handle_vehicle_problems",
                    user_query=context,
                    service=self.service,
                    user_type=self.actor,
                    image_data=image_data
                )
            except Exception as e:
                logger.error(f"AI generation failed: {e}")

        resolutions = {
            "FULL_REFUND_DRIVER_REVIEW": "We sincerely apologize for the vehicle condition. A full refund has been processed and the driver has been flagged for mandatory vehicle inspection.",
            "PARTIAL_REFUND_WARNING": "We apologize for the vehicle issue. A partial refund has been provided and a formal warning issued to the driver.",
            "GOODWILL_CREDIT": "Thank you for reporting the vehicle condition. A goodwill credit has been added to your account and the feedback forwarded to the driver."
        }
        return resolutions.get(decision, "Your vehicle complaint has been received and will be addressed within 24 hours.")

    def analyze_accident_details(self, query: str) -> str:
        """Analyze the type and severity of the accident"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['injury', 'injured', 'hurt', 'hospital']):
            return "ACCIDENT_WITH_INJURY"
        elif any(w in query_lower for w in ['major', 'serious', 'severe']):
            return "MAJOR_ACCIDENT"
        return "MINOR_ACCIDENT"

    def assess_emergency_level(self, analysis: str, query: str) -> str:
        """Assess whether emergency services were or should be involved"""
        return "EMERGENCY_SERVICES_NEEDED" if analysis == "ACCIDENT_WITH_INJURY" else "NO_EMERGENCY_SERVICES"

    def validate_accident_claims(self, analysis: str, image_data: Optional[str]) -> str:
        """Validate accident claims with or without image evidence"""
        if image_data:
            return "CLAIMS_VERIFIED_WITH_IMAGE"
        return "CLAIMS_ACCEPTED_PENDING_VERIFICATION"

    def check_insurance_coverage(self, analysis: str) -> str:
        """Check applicable insurance coverage for the accident type"""
        if analysis == "ACCIDENT_WITH_INJURY":
            return "FULL_INSURANCE_APPLICABLE"
        return "STANDARD_COVERAGE_APPLICABLE"

    def decide_accident_resolution(self, analysis: str, emergency: str, validation: str, insurance: str, credibility: int) -> str:
        """Decide comprehensive accident resolution"""
        # Anything with an injury or an active emergency goes straight to the medical
        # track — no credibility or evidence gate is appropriate on a safety incident
        if analysis == "ACCIDENT_WITH_INJURY" or emergency == "EMERGENCY_SERVICES_NEEDED":
            return "PRIORITY_MEDICAL_FULL_COMPENSATION"
        elif insurance == "FULL_INSURANCE_APPLICABLE":
            return "FULL_REFUND_INSURANCE_CLAIM"
        elif validation == "CLAIMS_VERIFIED_WITH_IMAGE" and credibility >= 5:
            return "FULL_REFUND_INSURANCE_CLAIM"
        elif credibility >= 6:
            return "FULL_REFUND_INSURANCE_CLAIM"
        return "PARTIAL_COMPENSATION_INVESTIGATION"

    def generate_accident_response(self, decision: str, analysis: str, emergency: str, query: str) -> str:
        """Generate comprehensive accident response"""
        if self.ai_engine:
            try:
                context = f"DECISION: {decision} | ACCIDENT_TYPE: {analysis} | EMERGENCY: {emergency} | QUERY: {query}"
                return self.ai_engine.process_complaint(
                    function_name="handle_accidents_during_ride",
                    user_query=context,
                    service=self.service,
                    user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI generation failed: {e}")

        if decision == "PRIORITY_MEDICAL_FULL_COMPENSATION":
            return "Your safety is our absolute priority. We have escalated this to our emergency response team. Full medical expense coverage and ride refund have been initiated. Please seek medical attention immediately if needed. Case Reference: GC-ACCIDENT-PRIORITY"
        elif decision == "FULL_REFUND_INSURANCE_CLAIM":
            return "We sincerely apologize for the accident. A full refund has been processed and an insurance claim initiated on your behalf. Our team will contact you within 2 hours."
        return "We have received your accident report and initiated an investigation. Compensation will be determined after review. You'll be contacted within 24 hours."
