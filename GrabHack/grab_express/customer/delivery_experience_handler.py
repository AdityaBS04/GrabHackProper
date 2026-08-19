"""
Grab Express Customer Delivery Experience Handler
Handles express delivery experience and timing issues
"""

import logging
import os
import sys
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class DeliveryExperienceHandler:
    """Express delivery experience management with strict workflows"""

    def __init__(self):
        self.service = "grab_express"
        self.actor = "customer"
        self.handler_type = "delivery_experience_handler"
        try:
            self.ai_engine = EnhancedAgenticAIEngine()
        except Exception as e:
            logger.warning(f"AI engine initialization failed: {e}")
            self.ai_engine = None

    def handle_delivery_delay(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle express delivery delays with strict 5-step workflow"""
        logger.info(f"Processing delivery delay complaint: {query[:100]}...")

        # Step 1: Identify the delay type and duration from the complaint
        delay_analysis = self.analyze_express_delay(query)
        logger.info(f"Delay analysis: {delay_analysis}")

        # Step 2: Assess the urgency and downstream impact of the delay
        impact_assessment = self.assess_delay_impact(delay_analysis, query)
        logger.info(f"Impact assessment: {impact_assessment}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on compensation and priority escalation
        decision = self.decide_delay_resolution(delay_analysis, impact_assessment, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with compensation and updated ETA
        response = self.generate_delay_response(decision, delay_analysis, impact_assessment, query)
        logger.info("Delivery delay response generated successfully")
        return response

    def handle_partial_delivery(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle package not delivered to correct recipient with strict 5-step workflow"""
        logger.info(f"Processing partial delivery complaint: {query[:100]}...")

        # Step 1: Identify the delivery failure type
        delivery_analysis = self.analyze_delivery_failure(query)
        logger.info(f"Delivery analysis: {delivery_analysis}")

        # Step 2: Assess the impact on the recipient
        impact_assessment = self.assess_delivery_failure_impact(delivery_analysis, query)
        logger.info(f"Impact assessment: {impact_assessment}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on re-delivery or refund action
        decision = self.decide_delivery_failure_resolution(delivery_analysis, impact_assessment, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with re-delivery or refund details
        response = self.generate_delivery_failure_response(decision, delivery_analysis, query)
        logger.info("Partial delivery response generated successfully")
        return response

    def handle_temperature_issues(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle package damaged or temperature-compromised during transit with strict 5-step workflow"""
        logger.info(f"Processing temperature/damage issue complaint: {query[:100]}...")

        # Step 1: Identify the type of temperature or damage issue
        damage_analysis = self.analyze_transit_damage(query)
        logger.info(f"Damage analysis: {damage_analysis}")

        # Step 2: Check if photo evidence is provided
        evidence_check = self.check_transit_damage_evidence(damage_analysis, image_data)
        logger.info(f"Evidence check: {evidence_check}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on refund and carrier accountability action
        decision = self.decide_transit_damage_resolution(damage_analysis, evidence_check, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with compensation and process improvement
        response = self.generate_transit_damage_response(decision, damage_analysis, query, image_data)
        logger.info("Temperature/damage response generated successfully")
        return response

    def handle_package_tampering(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle package tampering with strict 5-step workflow - IMAGE SUPPORTED"""
        logger.info(f"Processing package tampering complaint: {query[:100]}...")

        # Step 1: Identify evidence of tampering from the complaint
        tampering_analysis = self.analyze_tampering_evidence(query)
        logger.info(f"Tampering analysis: {tampering_analysis}")

        # Step 2: Check if photo evidence documents the tampering
        evidence_check = self.check_tampering_photo_evidence(tampering_analysis, image_data)
        logger.info(f"Evidence check: {evidence_check}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on investigation and compensation action
        decision = self.decide_tampering_resolution(tampering_analysis, evidence_check, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with investigation and full compensation details
        response = self.generate_tampering_response(decision, tampering_analysis, query, image_data)
        logger.info("Package tampering response generated successfully")
        return response

    def handle_multiple_deliveries(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle multiple failed delivery attempts with strict 5-step workflow"""
        logger.info(f"Processing multiple delivery attempts complaint: {query[:100]}...")

        # Step 1: Identify how many attempts were made and why they failed
        attempt_analysis = self.analyze_delivery_attempts(query)
        logger.info(f"Attempt analysis: {attempt_analysis}")

        # Step 2: Assess the impact of repeated failed attempts
        impact_assessment = self.assess_repeated_attempt_impact(attempt_analysis, query)
        logger.info(f"Impact assessment: {impact_assessment}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on priority delivery and compensation
        decision = self.decide_repeated_attempt_resolution(attempt_analysis, impact_assessment, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with guaranteed delivery plan
        response = self.generate_repeated_attempt_response(decision, attempt_analysis, query)
        logger.info("Multiple deliveries response generated successfully")
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

    def analyze_express_delay(self, query: str) -> str:
        """Identify the type and duration of the express delivery delay"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['same day', 'today', 'urgent']):
            return "SAME_DAY_DELIVERY_MISSED"
        elif any(w in query_lower for w in ['hour', 'hours', 'late by']):
            return "HOURS_BEYOND_PROMISED_TIME"
        return "GENERAL_EXPRESS_DELAY"

    def assess_delay_impact(self, analysis: str, query: str) -> str:
        """Assess the urgency and downstream impact of the delay"""
        if analysis == "SAME_DAY_DELIVERY_MISSED" or any(w in query.lower() for w in ['urgent', 'critical', 'important']):
            return "HIGH_URGENCY_IMPACT"
        return "MODERATE_INCONVENIENCE"

    def decide_delay_resolution(self, analysis: str, impact: str, credibility: int) -> str:
        """Decide compensation and escalation for the delay"""
        if impact == "HIGH_URGENCY_IMPACT" and credibility >= 6:
            return "PRIORITY_REDELIVERY_FULL_COMPENSATION"
        # A missed same-day window is a breach of the express guarantee we sold,
        # so it compensates without a credibility bar
        elif analysis == "SAME_DAY_DELIVERY_MISSED":
            return "PRIORITY_REDELIVERY_FULL_COMPENSATION"
        elif analysis == "HOURS_BEYOND_PROMISED_TIME" and credibility >= 4:
            return "VOUCHER_CREDIT_EXPEDITED_DELIVERY"
        elif credibility >= 5:
            return "VOUCHER_CREDIT_EXPEDITED_DELIVERY"
        return "APOLOGY_AND_STANDARD_REDELIVERY"

    def generate_delay_response(self, decision: str, analysis: str, impact: str, query: str) -> str:
        """Generate delivery delay response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_delivery_delay",
                    user_query=f"DECISION: {decision} | DELAY: {analysis} | IMPACT: {impact} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "PRIORITY_REDELIVERY_FULL_COMPENSATION": "We sincerely apologize for the express delivery delay. Your delivery has been escalated to priority status and full compensation has been applied to your account.",
            "VOUCHER_CREDIT_EXPEDITED_DELIVERY": "We apologize for the delay. Your delivery has been expedited and a voucher credit has been added to your account as compensation.",
            "APOLOGY_AND_STANDARD_REDELIVERY": "We are sorry for the express delivery delay. Your delivery is being prioritized and we expect it to arrive within the next 2 hours."
        }
        return responses.get(decision, "We apologize for the express delivery delay. We are working to complete your delivery as soon as possible.")

    def analyze_delivery_failure(self, query: str) -> str:
        """Identify the type of partial delivery failure"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['wrong person', 'neighbour', 'someone else']):
            return "DELIVERED_TO_WRONG_PERSON"
        elif any(w in query_lower for w in ['left outside', 'unattended', 'no signature']):
            return "UNATTENDED_DELIVERY"
        return "GENERAL_DELIVERY_FAILURE"

    def assess_delivery_failure_impact(self, analysis: str, query: str) -> str:
        """Assess impact of the delivery failure"""
        return "HIGH_IMPACT" if analysis == "DELIVERED_TO_WRONG_PERSON" else "MODERATE_IMPACT"

    def decide_delivery_failure_resolution(self, analysis: str, impact: str, credibility: int) -> str:
        """Decide resolution for delivery failure"""
        if impact == "HIGH_IMPACT" and credibility >= 6:
            return "IMMEDIATE_RECOVERY_FULL_REFUND"
        # Handing a package to the wrong person means it is already out of our custody
        elif analysis == "DELIVERED_TO_WRONG_PERSON":
            return "IMMEDIATE_RECOVERY_FULL_REFUND"
        elif analysis == "UNATTENDED_DELIVERY" and credibility >= 4:
            return "REDELIVERY_WITH_INVESTIGATION"
        elif credibility >= 5:
            return "REDELIVERY_WITH_INVESTIGATION"
        return "STANDARD_INVESTIGATION"

    def generate_delivery_failure_response(self, decision: str, analysis: str, query: str) -> str:
        """Generate delivery failure response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_partial_delivery",
                    user_query=f"DECISION: {decision} | FAILURE: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "IMMEDIATE_RECOVERY_FULL_REFUND": "We are immediately escalating this delivery failure. Our team is working to recover your package and a full refund has been processed as a precaution.",
            "REDELIVERY_WITH_INVESTIGATION": "We are arranging immediate redelivery and investigating how the delivery failure occurred. You will receive tracking for the redelivery within 30 minutes.",
            "STANDARD_INVESTIGATION": "Your delivery failure report has been logged. We are investigating with the delivery partner and will update you within 24 hours."
        }
        return responses.get(decision, "We are investigating the delivery issue and will arrange redelivery or a refund as appropriate.")

    def analyze_transit_damage(self, query: str) -> str:
        """Identify the type of transit damage or temperature issue"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['temperature', 'melted', 'hot', 'cold', 'spoiled']):
            return "TEMPERATURE_COMPROMISE"
        elif any(w in query_lower for w in ['wet', 'water', 'rain']):
            return "WATER_DAMAGE"
        elif any(w in query_lower for w in ['crushed', 'broken', 'damaged']):
            return "PHYSICAL_TRANSIT_DAMAGE"
        return "GENERAL_TRANSIT_DAMAGE"

    def check_transit_damage_evidence(self, analysis: str, image_data: Optional[str]) -> str:
        """Check for photo evidence of transit damage"""
        return "PHOTO_EVIDENCE_PROVIDED" if image_data else "TEXT_CLAIM_ONLY"

    def decide_transit_damage_resolution(self, analysis: str, evidence: str, credibility: int) -> str:
        """Decide resolution for transit damage"""
        if evidence == "PHOTO_EVIDENCE_PROVIDED" and credibility >= 6:
            return "FULL_REFUND_CARRIER_PENALISED"
        # A broken cold chain writes off the contents entirely, photo or not
        elif analysis == "TEMPERATURE_COMPROMISE" and credibility >= 5:
            return "FULL_REFUND_CARRIER_PENALISED"
        elif analysis in ("WATER_DAMAGE", "PHYSICAL_TRANSIT_DAMAGE") and evidence == "PHOTO_EVIDENCE_PROVIDED":
            return "COMPENSATION_ISSUED_INVESTIGATION"
        elif credibility >= 5:
            return "COMPENSATION_ISSUED_INVESTIGATION"
        return "INVESTIGATION_REQUIRED"

    def generate_transit_damage_response(self, decision: str, analysis: str, query: str, image_data: Optional[str]) -> str:
        """Generate transit damage response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_temperature_issues",
                    user_query=f"DECISION: {decision} | DAMAGE: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor, image_data=image_data
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "FULL_REFUND_CARRIER_PENALISED": "We take package integrity very seriously. A full refund has been processed and the delivery partner has been flagged for a safety review.",
            "COMPENSATION_ISSUED_INVESTIGATION": "Compensation has been issued for the transit damage and an investigation into the delivery partner's handling has been opened.",
            "INVESTIGATION_REQUIRED": "Your damage report has been logged. Please share photos if available. Our team will investigate and process compensation within 24 hours."
        }
        return responses.get(decision, "We take package integrity very seriously. We are processing your refund and implementing additional security measures.")

    def analyze_tampering_evidence(self, query: str) -> str:
        """Identify evidence of package tampering"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['opened', 'resealed', 'tape removed']):
            return "OPENED_AND_RESEALED"
        elif any(w in query_lower for w in ['content missing', 'items removed', 'lighter']):
            return "CONTENTS_REMOVED"
        return "GENERAL_TAMPERING_SUSPECTED"

    def check_tampering_photo_evidence(self, analysis: str, image_data: Optional[str]) -> str:
        """Check if photo evidence documents tampering"""
        return "PHOTO_EVIDENCE_PROVIDED" if image_data else "TEXT_CLAIM_ONLY"

    def decide_tampering_resolution(self, analysis: str, evidence: str, credibility: int) -> str:
        """Decide resolution for package tampering"""
        if analysis == "CONTENTS_REMOVED" and credibility >= 6:
            return "FULL_REFUND_URGENT_INVESTIGATION"
        elif evidence == "PHOTO_EVIDENCE_PROVIDED" and credibility >= 5:
            return "COMPENSATION_AND_CARRIER_INVESTIGATION"
        return "INVESTIGATION_INITIATED"

    def generate_tampering_response(self, decision: str, analysis: str, query: str, image_data: Optional[str]) -> str:
        """Generate package tampering response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_package_tampering",
                    user_query=f"DECISION: {decision} | TAMPERING: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor, image_data=image_data
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "FULL_REFUND_URGENT_INVESTIGATION": "Package tampering is a serious offence. A full refund has been processed and an urgent investigation has been opened. The delivery partner's account has been suspended pending review.",
            "COMPENSATION_AND_CARRIER_INVESTIGATION": "We are treating your tampering report with the highest priority. Compensation has been issued and a formal investigation into the delivery partner is underway.",
            "INVESTIGATION_INITIATED": "Your tampering report has been escalated. Please preserve the package as evidence. Our team will contact you within 4 hours regarding investigation findings."
        }
        return responses.get(decision, "Package tampering is a serious concern. We are investigating immediately and will provide full compensation for any losses.")

    def analyze_delivery_attempts(self, query: str) -> str:
        """Identify how many delivery attempts were made and why they failed"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['3', 'three', 'multiple', 'several']):
            return "THREE_OR_MORE_FAILED_ATTEMPTS"
        elif any(w in query_lower for w in ['twice', 'two', '2']):
            return "TWO_FAILED_ATTEMPTS"
        return "REPEATED_FAILED_ATTEMPTS_UNSPECIFIED"

    def assess_repeated_attempt_impact(self, analysis: str, query: str) -> str:
        """Assess the impact of repeated failed delivery attempts"""
        return "HIGH_IMPACT" if analysis == "THREE_OR_MORE_FAILED_ATTEMPTS" else "MODERATE_IMPACT"

    def decide_repeated_attempt_resolution(self, analysis: str, impact: str, credibility: int) -> str:
        """Decide resolution for repeated failed attempts"""
        if impact == "HIGH_IMPACT" and credibility >= 6:
            return "GUARANTEED_PRIORITY_DELIVERY_COMPENSATION"
        # Three failed attempts means our routing is the problem, not the customer
        elif analysis == "THREE_OR_MORE_FAILED_ATTEMPTS":
            return "GUARANTEED_PRIORITY_DELIVERY_COMPENSATION"
        elif analysis == "TWO_FAILED_ATTEMPTS" and credibility >= 4:
            return "SCHEDULED_DELIVERY_VOUCHER"
        elif credibility >= 5:
            return "SCHEDULED_DELIVERY_VOUCHER"
        return "REDELIVERY_COORDINATION"

    def generate_repeated_attempt_response(self, decision: str, analysis: str, query: str) -> str:
        """Generate multiple delivery attempts response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_multiple_deliveries",
                    user_query=f"DECISION: {decision} | ATTEMPTS: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "GUARANTEED_PRIORITY_DELIVERY_COMPENSATION": "We sincerely apologize for the repeated delivery failures. A priority delivery partner has been assigned and a guaranteed delivery slot has been booked for you. Compensation for the inconvenience has been credited to your account.",
            "SCHEDULED_DELIVERY_VOUCHER": "We are scheduling a confirmed delivery appointment with you. A voucher credit has been applied. Our delivery partner will coordinate a specific time slot directly with you.",
            "REDELIVERY_COORDINATION": "We are arranging a fresh delivery attempt. Our team will coordinate with you to ensure the next attempt is successful."
        }
        return responses.get(decision, "We understand the inconvenience of multiple delivery attempts. A priority redelivery has been arranged.")
