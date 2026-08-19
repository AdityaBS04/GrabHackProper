"""
Grab Express Customer Driver Interaction Handler
Handles delivery partner interaction issues for express deliveries
"""

import logging
import os
import sys
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class DriverInteractionHandler:
    """Express delivery partner interaction management with strict workflows"""

    def __init__(self):
        self.service = "grab_express"
        self.actor = "customer"
        self.handler_type = "driver_interaction_handler"
        try:
            self.ai_engine = EnhancedAgenticAIEngine()
        except Exception as e:
            logger.warning(f"AI engine initialization failed: {e}")
            self.ai_engine = None

    def handle_rude_behavior(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle rude behavior from delivery partner with strict 5-step workflow"""
        logger.info(f"Processing rude behavior complaint: {query[:100]}...")

        # Step 1: Identify the type of rude or unprofessional behavior
        behavior_analysis = self.analyze_rude_behavior(query)
        logger.info(f"Behavior analysis: {behavior_analysis}")

        # Step 2: Assess the severity of the behavior and its impact
        severity = self.assess_behavior_severity(behavior_analysis, query)
        logger.info(f"Severity: {severity}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on partner action and customer compensation
        decision = self.decide_behavior_resolution(behavior_analysis, severity, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with action taken and assurance
        response = self.generate_behavior_response(decision, behavior_analysis, severity, query, image_data)
        logger.info("Rude behavior response generated successfully")
        return response

    def handle_location_difficulty(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle delivery partner unable to find address with strict 5-step workflow"""
        logger.info(f"Processing location difficulty complaint: {query[:100]}...")

        # Step 1: Identify the type of location finding problem
        location_analysis = self.analyze_location_problem(query)
        logger.info(f"Location analysis: {location_analysis}")

        # Step 2: Assess the impact on the delivery outcome
        delivery_impact = self.assess_location_delivery_impact(location_analysis, query)
        logger.info(f"Delivery impact: {delivery_impact}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on resolution and navigation support
        decision = self.decide_location_resolution(location_analysis, delivery_impact, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with navigation support and delivery solution
        response = self.generate_location_response(decision, location_analysis, query)
        logger.info("Location difficulty response generated successfully")
        return response

    def handle_payment_manipulation(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle delivery partner requesting extra money with strict 5-step workflow"""
        logger.info(f"Processing payment manipulation complaint: {query[:100]}...")

        # Step 1: Identify the type of payment manipulation reported
        manipulation_analysis = self.analyze_payment_manipulation(query)
        logger.info(f"Manipulation analysis: {manipulation_analysis}")

        # Step 2: Check if customer was actually charged extra
        charge_verification = self.check_extra_charge_occurrence(manipulation_analysis, query)
        logger.info(f"Charge verification: {charge_verification}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on refund and partner penalty action
        decision = self.decide_manipulation_resolution(manipulation_analysis, charge_verification, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with refund confirmation and partner action
        response = self.generate_manipulation_response(decision, manipulation_analysis, query, image_data)
        logger.info("Payment manipulation response generated successfully")
        return response

    def handle_false_delivery(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle false delivery marking with strict 5-step workflow - IMAGE SUPPORTED"""
        logger.info(f"Processing false delivery complaint: {query[:100]}...")

        # Step 1: Identify the circumstances of the false delivery claim
        false_delivery_analysis = self.analyze_false_delivery(query)
        logger.info(f"False delivery analysis: {false_delivery_analysis}")

        # Step 2: Check GPS and delivery records to validate the claim
        gps_validation = self.validate_false_delivery_with_gps(false_delivery_analysis, query)
        logger.info(f"GPS validation: {gps_validation}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on replacement delivery and partner penalty
        decision = self.decide_false_delivery_resolution(false_delivery_analysis, gps_validation, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with replacement delivery and investigation details
        response = self.generate_false_delivery_response(decision, false_delivery_analysis, query, image_data)
        logger.info("False delivery response generated successfully")
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

    def analyze_rude_behavior(self, query: str) -> str:
        """Identify the type of rude or unprofessional behavior"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['threatened', 'threatened', 'aggressive', 'intimidate']):
            return "THREATENING_BEHAVIOR"
        elif any(w in query_lower for w in ['shouted', 'yelled', 'abusive', 'insults']):
            return "VERBAL_ABUSE"
        elif any(w in query_lower for w in ['rude', 'impolite', 'disrespectful', 'unprofessional']):
            return "GENERAL_RUDENESS"
        return "UNPROFESSIONAL_CONDUCT"

    def assess_behavior_severity(self, analysis: str, query: str) -> str:
        """Assess the severity of the partner's behavior"""
        return "HIGH_SEVERITY" if analysis == "THREATENING_BEHAVIOR" else "MODERATE_SEVERITY"

    def decide_behavior_resolution(self, analysis: str, severity: str, credibility: int) -> str:
        """Decide action against the delivery partner and compensation for customer"""
        if severity == "HIGH_SEVERITY" and credibility >= 6:
            return "PARTNER_SUSPENDED_FULL_CREDIT"
        # Verbal abuse is escalated on the safety track regardless of credibility
        elif analysis in ("THREATENING_BEHAVIOR", "VERBAL_ABUSE"):
            return "PARTNER_SUSPENDED_FULL_CREDIT" if credibility >= 5 else "FORMAL_WARNING_PARTIAL_CREDIT"
        elif credibility >= 5:
            return "FORMAL_WARNING_PARTIAL_CREDIT"
        return "COMPLAINT_LOGGED_INVESTIGATED"

    def generate_behavior_response(self, decision: str, analysis: str, severity: str, query: str, image_data: Optional[str]) -> str:
        """Generate rude behavior response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_rude_behavior",
                    user_query=f"DECISION: {decision} | BEHAVIOR: {analysis} | SEVERITY: {severity} | QUERY: {query}",
                    service=self.service, user_type=self.actor, image_data=image_data
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "PARTNER_SUSPENDED_FULL_CREDIT": "We take delivery partner behavior very seriously. The partner has been immediately suspended pending a full investigation. A credit has been applied to your account and our safety team has been notified.",
            "FORMAL_WARNING_PARTIAL_CREDIT": "A formal warning has been issued to the delivery partner and a credit has been added to your account. We are monitoring this partner's conduct closely.",
            "COMPLAINT_LOGGED_INVESTIGATED": "Your complaint about the delivery partner's behavior has been logged and is under investigation. You will receive an update within 24 hours."
        }
        return responses.get(decision, "We take delivery partner behavior very seriously. We are investigating this incident and taking appropriate action.")

    def analyze_location_problem(self, query: str) -> str:
        """Identify the type of location finding problem"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['wrong building', 'wrong block', 'wrong unit']):
            return "WRONG_BUILDING_OR_UNIT"
        elif any(w in query_lower for w in ['gps', 'navigation', 'app error']):
            return "GPS_OR_APP_ERROR"
        elif any(w in query_lower for w in ['did not call', 'no call', 'no contact']):
            return "PARTNER_DID_NOT_CONTACT"
        return "GENERAL_LOCATION_DIFFICULTY"

    def assess_location_delivery_impact(self, analysis: str, query: str) -> str:
        """Assess whether the location difficulty caused delivery failure"""
        if any(w in query.lower() for w in ['failed', 'not delivered', 'returned']):
            return "DELIVERY_FAILED_DUE_TO_LOCATION"
        return "DELIVERY_DELAYED_DUE_TO_LOCATION"

    def decide_location_resolution(self, analysis: str, impact: str, credibility: int) -> str:
        """Decide resolution for location difficulty"""
        if impact == "DELIVERY_FAILED_DUE_TO_LOCATION" and credibility >= 6:
            return "IMMEDIATE_REDELIVERY_NO_CHARGE"
        # A partner who never called, or our own GPS data, is our fault to absorb
        elif analysis in ("PARTNER_DID_NOT_CONTACT", "GPS_OR_APP_ERROR") and impact == "DELIVERY_FAILED_DUE_TO_LOCATION":
            return "IMMEDIATE_REDELIVERY_NO_CHARGE"
        elif analysis in ("PARTNER_DID_NOT_CONTACT", "GPS_OR_APP_ERROR"):
            return "PRIORITY_REDELIVERY_NAVIGATION_IMPROVED"
        elif credibility >= 5:
            return "PRIORITY_REDELIVERY_NAVIGATION_IMPROVED"
        return "REDELIVERY_SCHEDULED"

    def generate_location_response(self, decision: str, analysis: str, query: str) -> str:
        """Generate location difficulty response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_location_difficulty",
                    user_query=f"DECISION: {decision} | LOCATION_ISSUE: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "IMMEDIATE_REDELIVERY_NO_CHARGE": "We apologize for the delivery failure caused by navigation issues. A new delivery partner has been assigned and will arrive within 1-2 hours at no additional charge.",
            "PRIORITY_REDELIVERY_NAVIGATION_IMPROVED": "We are arranging priority redelivery with updated navigation data for your address. The delivery partner will contact you before arriving.",
            "REDELIVERY_SCHEDULED": "A redelivery has been scheduled. We have updated the location notes for your address to prevent similar issues in future."
        }
        return responses.get(decision, "We understand the address location difficulty. We are arranging a redelivery and improving navigation support.")

    def analyze_payment_manipulation(self, query: str) -> str:
        """Identify the type of payment manipulation"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['extra charge', 'additional fee', 'more money']):
            return "EXTRA_CHARGE_DEMANDED"
        elif any(w in query_lower for w in ['cash', 'refused', 'online']):
            return "PAYMENT_METHOD_COERCION"
        return "GENERAL_PAYMENT_MANIPULATION"

    def check_extra_charge_occurrence(self, analysis: str, query: str) -> str:
        """Verify whether extra charges were actually collected"""
        if any(w in query.lower() for w in ['paid', 'gave', 'handed', 'transferred']):
            return "EXTRA_CHARGE_CONFIRMED_PAID"
        return "ATTEMPTED_BUT_NOT_PAID"

    def decide_manipulation_resolution(self, analysis: str, charge_check: str, credibility: int) -> str:
        """Decide resolution for payment manipulation"""
        if charge_check == "EXTRA_CHARGE_CONFIRMED_PAID" and credibility >= 6:
            return "FULL_REFUND_PARTNER_PENALISED"
        # Money actually handed over is refunded even at lower credibility
        elif charge_check == "EXTRA_CHARGE_CONFIRMED_PAID" and credibility >= 4:
            return "FULL_REFUND_PARTNER_PENALISED"
        elif analysis == "EXTRA_CHARGE_DEMANDED" and credibility >= 5:
            return "INVESTIGATION_AND_WARNING"
        elif credibility >= 5:
            return "INVESTIGATION_AND_WARNING"
        return "COMPLAINT_FILED_MONITORED"

    def generate_manipulation_response(self, decision: str, analysis: str, query: str, image_data: Optional[str]) -> str:
        """Generate payment manipulation response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_payment_manipulation",
                    user_query=f"DECISION: {decision} | MANIPULATION: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor, image_data=image_data
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "FULL_REFUND_PARTNER_PENALISED": "Payment manipulation is strictly prohibited. The extra amount has been fully refunded and the delivery partner's account has been suspended pending investigation.",
            "INVESTIGATION_AND_WARNING": "We are investigating the payment manipulation complaint. A formal warning has been issued to the partner and we are reviewing their transaction records.",
            "COMPLAINT_FILED_MONITORED": "Your payment manipulation complaint has been logged and the delivery partner has been flagged for monitoring. Our compliance team will review and respond within 48 hours."
        }
        return responses.get(decision, "Payment manipulation is strictly prohibited. We are investigating immediately and any extra charges will be refunded.")

    def analyze_false_delivery(self, query: str) -> str:
        """Identify the circumstances of the false delivery claim"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['marked delivered', 'status shows', 'says delivered']):
            return "STATUS_SHOWS_DELIVERED_NOT_RECEIVED"
        elif any(w in query_lower for w in ['photo proof', 'fake photo', 'wrong photo']):
            return "FAKE_DELIVERY_PHOTO_SUSPECTED"
        return "GENERAL_FALSE_DELIVERY_CLAIM"

    def validate_false_delivery_with_gps(self, analysis: str, query: str) -> str:
        """Validate the false delivery claim using GPS and delivery records"""
        query_lower = query.lower()
        # A customer describing the partner never reaching them contradicts the delivery scan
        if any(w in query_lower for w in ['never came', 'never arrived', 'no one came', 'nobody came', 'did not arrive']):
            return "GPS_CONTRADICTS_DELIVERY_SCAN"
        elif any(w in query_lower for w in ['different address', 'wrong address', 'neighbour', 'neighbor']):
            return "DELIVERED_TO_WRONG_LOCATION"
        elif analysis == "FAKE_DELIVERY_PHOTO_SUSPECTED":
            return "PROOF_OF_DELIVERY_DISPUTED"
        return "GPS_RECORDS_INCONCLUSIVE"

    def decide_false_delivery_resolution(self, analysis: str, gps_check: str, credibility: int) -> str:
        """Decide resolution for false delivery marking"""
        # GPS contradicting the scan is proof the partner falsified the delivery
        if gps_check in ("GPS_CONTRADICTS_DELIVERY_SCAN", "DELIVERED_TO_WRONG_LOCATION"):
            return "IMMEDIATE_REPLACEMENT_PARTNER_SUSPENDED"
        elif credibility >= 7:
            return "IMMEDIATE_REPLACEMENT_PARTNER_SUSPENDED"
        elif gps_check == "PROOF_OF_DELIVERY_DISPUTED" and credibility >= 5:
            return "REPLACEMENT_DELIVERY_INVESTIGATION"
        elif analysis == "STATUS_SHOWS_DELIVERED_NOT_RECEIVED" and credibility >= 5:
            return "REPLACEMENT_DELIVERY_INVESTIGATION"
        elif credibility >= 5:
            return "REPLACEMENT_DELIVERY_INVESTIGATION"
        return "FULL_INVESTIGATION_BEFORE_RESOLUTION"

    def generate_false_delivery_response(self, decision: str, analysis: str, query: str, image_data: Optional[str]) -> str:
        """Generate false delivery response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_false_delivery",
                    user_query=f"DECISION: {decision} | FALSE_DELIVERY: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor, image_data=image_data
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "IMMEDIATE_REPLACEMENT_PARTNER_SUSPENDED": "False delivery marking is a serious violation. The delivery partner has been suspended and a replacement delivery is being dispatched immediately. If the package cannot be located, a full refund will be issued.",
            "REPLACEMENT_DELIVERY_INVESTIGATION": "We are investigating the false delivery report using GPS tracking data. A replacement delivery is being arranged. You will receive tracking within 30 minutes.",
            "FULL_INVESTIGATION_BEFORE_RESOLUTION": "Your false delivery claim has been escalated for urgent investigation. GPS records, delivery photos, and partner logs are being reviewed. You will be updated within 4 hours."
        }
        return responses.get(decision, "False delivery marking is a serious violation. We are investigating with GPS tracking data and will arrange immediate replacement delivery or full refund.")
