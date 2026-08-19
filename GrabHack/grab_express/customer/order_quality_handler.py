"""
Grab Express Customer Order Quality Handler
Handles package quality and accuracy issues for express deliveries
"""

import logging
import os
import sys
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class OrderQualityHandler:
    """Express delivery package quality and accuracy management with strict workflows"""

    def __init__(self):
        self.service = "grab_express"
        self.actor = "customer"
        self.handler_type = "order_quality_handler"
        try:
            self.ai_engine = EnhancedAgenticAIEngine()
        except Exception as e:
            logger.warning(f"AI engine initialization failed: {e}")
            self.ai_engine = None

    def handle_missing_items(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle missing packages in express delivery with strict 5-step workflow"""
        logger.info(f"Processing missing package complaint: {query[:100]}...")

        # Step 1: Identify what is reported as missing
        missing_analysis = self.analyze_missing_package(query)
        logger.info(f"Missing analysis: {missing_analysis}")

        # Step 2: Check if photo evidence is provided
        evidence_check = self.check_missing_evidence(missing_analysis, image_data)
        logger.info(f"Evidence check: {evidence_check}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on replacement or refund action
        decision = self.decide_missing_resolution(missing_analysis, evidence_check, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with replacement or refund details
        response = self.generate_missing_response(decision, missing_analysis, query, image_data)
        logger.info("Missing package response generated successfully")
        return response

    def handle_wrong_item(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle wrong package delivered with strict 5-step workflow"""
        logger.info(f"Processing wrong package complaint: {query[:100]}...")

        # Step 1: Identify the nature of the wrong delivery
        wrong_item_analysis = self.analyze_wrong_delivery(query)
        logger.info(f"Wrong item analysis: {wrong_item_analysis}")

        # Step 2: Check if image evidence is provided for verification
        evidence_check = self.check_wrong_item_evidence(wrong_item_analysis, image_data)
        logger.info(f"Evidence check: {evidence_check}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on collection and redelivery action
        decision = self.decide_wrong_item_resolution(wrong_item_analysis, evidence_check, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with swap and redelivery details
        response = self.generate_wrong_item_response(decision, wrong_item_analysis, query, image_data)
        logger.info("Wrong package response generated successfully")
        return response

    def handle_quality_issues(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle damaged packages during transit with strict 5-step workflow - IMAGE SUPPORTED"""
        logger.info(f"Processing package damage complaint: {query[:100]}...")

        # Step 1: Identify the type and extent of damage
        damage_analysis = self.analyze_package_damage(query)
        logger.info(f"Damage analysis: {damage_analysis}")

        # Step 2: Check if image evidence documents the damage
        evidence_check = self.check_damage_photo_evidence(damage_analysis, image_data)
        logger.info(f"Evidence check: {evidence_check}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on compensation or replacement action
        decision = self.decide_damage_resolution(damage_analysis, evidence_check, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with compensation and liability details
        response = self.generate_damage_response(decision, damage_analysis, query, image_data)
        logger.info("Package damage response generated successfully")
        return response

    def handle_substitution_issues(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle incomplete package contents with strict 5-step workflow"""
        logger.info(f"Processing incomplete package complaint: {query[:100]}...")

        # Step 1: Identify what content is reported as missing or substituted
        substitution_analysis = self.analyze_substitution_issue(query)
        logger.info(f"Substitution analysis: {substitution_analysis}")

        # Step 2: Assess sender vs carrier responsibility
        responsibility_check = self.assess_substitution_responsibility(substitution_analysis, query)
        logger.info(f"Responsibility check: {responsibility_check}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on compensation and sender notification action
        decision = self.decide_substitution_resolution(substitution_analysis, responsibility_check, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with resolution and sender escalation details
        response = self.generate_substitution_response(decision, substitution_analysis, query, image_data)
        logger.info("Substitution issue response generated successfully")
        return response

    def handle_quantity_mismatch(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle package size or quantity mismatch with strict 5-step workflow"""
        logger.info(f"Processing package size mismatch complaint: {query[:100]}...")

        # Step 1: Identify the mismatch type and magnitude
        mismatch_analysis = self.analyze_quantity_mismatch(query)
        logger.info(f"Mismatch analysis: {mismatch_analysis}")

        # Step 2: Assess whether the mismatch is a sender or system error
        error_source = self.assess_mismatch_source(mismatch_analysis, query)
        logger.info(f"Error source: {error_source}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on reconciliation and compensation action
        decision = self.decide_mismatch_resolution(mismatch_analysis, error_source, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with correction and compensation details
        response = self.generate_mismatch_response(decision, mismatch_analysis, query, image_data)
        logger.info("Quantity mismatch response generated successfully")
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

    def analyze_missing_package(self, query: str) -> str:
        """Identify what is missing from the delivery"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['entire', 'whole', 'nothing', 'not received']):
            return "ENTIRE_PACKAGE_MISSING"
        elif any(w in query_lower for w in ['partial', 'some', 'part']):
            return "PARTIAL_PACKAGE_MISSING"
        return "UNSPECIFIED_MISSING_CONTENT"

    def check_missing_evidence(self, analysis: str, image_data: Optional[str]) -> str:
        """Check if evidence is provided for the missing package claim"""
        return "PHOTO_EVIDENCE_PROVIDED" if image_data else "CLAIM_WITHOUT_EVIDENCE"

    def decide_missing_resolution(self, analysis: str, evidence: str, credibility: int) -> str:
        """Decide resolution for missing package"""
        has_evidence = evidence == "PHOTO_EVIDENCE_PROVIDED"
        if analysis == "ENTIRE_PACKAGE_MISSING" and credibility >= 6:
            return "FULL_REFUND_OR_REPLACEMENT"
        elif has_evidence and credibility >= 5:
            return "FULL_REFUND_OR_REPLACEMENT"
        elif credibility >= 5:
            return "INVESTIGATION_AND_REPLACEMENT"
        elif has_evidence:
            return "INVESTIGATION_AND_REPLACEMENT"
        return "INVESTIGATION_REQUIRED"

    def generate_missing_response(self, decision: str, analysis: str, query: str, image_data: Optional[str]) -> str:
        """Generate missing package response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_missing_items",
                    user_query=f"DECISION: {decision} | MISSING: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor, image_data=image_data
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "FULL_REFUND_OR_REPLACEMENT": "We are extremely sorry for the missing package. A full refund has been processed and an immediate replacement delivery has been arranged.",
            "INVESTIGATION_AND_REPLACEMENT": "We are investigating the missing package. A replacement delivery has been dispatched and you will receive tracking details shortly.",
            "INVESTIGATION_REQUIRED": "Your missing package report has been logged. Our team is investigating with the delivery partner and will update you within 24 hours."
        }
        return responses.get(decision, "We apologize for the missing package. We are investigating this issue immediately.")

    def analyze_wrong_delivery(self, query: str) -> str:
        """Identify the nature of the wrong package delivery"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['completely different', 'wrong person', 'wrong address']):
            return "DELIVERED_TO_WRONG_RECIPIENT"
        elif any(w in query_lower for w in ['wrong item', 'different package']):
            return "WRONG_PACKAGE_DELIVERED"
        return "GENERAL_WRONG_DELIVERY"

    def check_wrong_item_evidence(self, analysis: str, image_data: Optional[str]) -> str:
        """Check evidence for wrong delivery claim"""
        return "PHOTO_EVIDENCE_PROVIDED" if image_data else "TEXT_CLAIM_ONLY"

    def decide_wrong_item_resolution(self, analysis: str, evidence: str, credibility: int) -> str:
        """Decide resolution for wrong delivery"""
        has_evidence = evidence == "PHOTO_EVIDENCE_PROVIDED"
        # Wrong-recipient delivery is a carrier fault confirmed from delivery logs, so it
        # never waits on customer evidence
        if analysis == "DELIVERED_TO_WRONG_RECIPIENT" and credibility >= 5:
            return "IMMEDIATE_SWAP_AND_REDELIVERY"
        elif has_evidence and credibility >= 6:
            return "IMMEDIATE_SWAP_AND_REDELIVERY"
        elif has_evidence or credibility >= 6:
            return "COLLECTION_AND_REDELIVERY_ARRANGED"
        elif credibility >= 4:
            return "COLLECTION_AND_REDELIVERY_ARRANGED"
        return "INVESTIGATION_BEFORE_REDELIVERY"

    def generate_wrong_item_response(self, decision: str, analysis: str, query: str, image_data: Optional[str]) -> str:
        """Generate wrong item response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_wrong_item",
                    user_query=f"DECISION: {decision} | WRONG_DELIVERY: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor, image_data=image_data
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "IMMEDIATE_SWAP_AND_REDELIVERY": "We sincerely apologize for delivering the wrong package. A delivery partner is being dispatched immediately to collect the incorrect package and deliver the correct one within 2 hours.",
            "COLLECTION_AND_REDELIVERY_ARRANGED": "We are arranging collection of the wrong package and redelivery of the correct one. You will receive a tracking update within the hour.",
            "INVESTIGATION_BEFORE_REDELIVERY": "Your wrong delivery report has been logged. We are coordinating with the delivery partner to locate your correct package and arrange redelivery."
        }
        return responses.get(decision, "We apologize for the wrong delivery. We will collect the incorrect package and deliver the correct one as soon as possible.")

    def analyze_package_damage(self, query: str) -> str:
        """Identify the type and severity of package damage"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['broken', 'shattered', 'destroyed', 'completely']):
            return "SEVERE_DAMAGE"
        elif any(w in query_lower for w in ['dented', 'scratched', 'wet', 'torn']):
            return "MODERATE_DAMAGE"
        return "MINOR_DAMAGE"

    def check_damage_photo_evidence(self, analysis: str, image_data: Optional[str]) -> str:
        """Check if photo evidence documents the damage"""
        if image_data:
            return "PHOTO_EVIDENCE_AVAILABLE"
        if analysis == "SEVERE_DAMAGE":
            return "PHOTO_REQUIRED_FOR_FULL_CLAIM"
        return "TEXT_CLAIM_ONLY"

    def decide_damage_resolution(self, analysis: str, evidence: str, credibility: int) -> str:
        """Decide compensation for package damage"""
        if analysis == "SEVERE_DAMAGE" and credibility >= 6:
            return "FULL_REFUND_CARRIER_LIABILITY"
        elif evidence == "PHOTO_EVIDENCE_AVAILABLE" and credibility >= 5:
            return "COMPENSATION_BASED_ON_EVIDENCE"
        return "INVESTIGATION_AND_PARTIAL_COMPENSATION"

    def generate_damage_response(self, decision: str, analysis: str, query: str, image_data: Optional[str]) -> str:
        """Generate package damage response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_quality_issues",
                    user_query=f"DECISION: {decision} | DAMAGE: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor, image_data=image_data
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "FULL_REFUND_CARRIER_LIABILITY": "We confirm the carrier is liable for the damage. A full refund has been processed and the delivery partner has been flagged for a package handling review.",
            "COMPENSATION_BASED_ON_EVIDENCE": "Based on the evidence provided, compensation has been issued for the damaged package. The amount will appear in your account within 24 hours.",
            "INVESTIGATION_AND_PARTIAL_COMPENSATION": "We are investigating the damage incident. A partial compensation has been applied and our team will contact you within 24 hours with full resolution."
        }
        return responses.get(decision, "We apologize for the package damage. Please share photos for immediate refund processing.")

    def analyze_substitution_issue(self, query: str) -> str:
        """Identify what was substituted or is incomplete"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['substituted', 'replaced', 'different item']):
            return "UNAUTHORIZED_SUBSTITUTION"
        elif any(w in query_lower for w in ['incomplete', 'missing contents', 'partial']):
            return "INCOMPLETE_PACKAGE_CONTENTS"
        return "GENERAL_SUBSTITUTION_ISSUE"

    def assess_substitution_responsibility(self, analysis: str, query: str) -> str:
        """Assess whether issue stems from sender or carrier"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['opened', 'tampered', 'resealed', 'seal broken', 'torn open']):
            return "CARRIER_TAMPERING_SUSPECTED"
        elif analysis == "UNAUTHORIZED_SUBSTITUTION":
            return "CARRIER_TAMPERING_SUSPECTED"
        return "SENDER_OR_SYSTEM_ERROR"

    def decide_substitution_resolution(self, analysis: str, responsibility: str, credibility: int) -> str:
        """Decide resolution for substitution or incomplete contents"""
        if responsibility == "CARRIER_TAMPERING_SUSPECTED" and credibility >= 6:
            return "FULL_REFUND_CARRIER_INVESTIGATION"
        elif analysis == "INCOMPLETE_PACKAGE_CONTENTS" and credibility >= 5:
            return "SENDER_CONTACTED_REPLACEMENT_ARRANGED"
        elif credibility >= 5:
            return "SENDER_CONTACTED_REPLACEMENT_ARRANGED"
        return "INVESTIGATION_INITIATED"

    def generate_substitution_response(self, decision: str, analysis: str, query: str, image_data: Optional[str]) -> str:
        """Generate substitution issue response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_substitution_issues",
                    user_query=f"DECISION: {decision} | SUBSTITUTION: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor, image_data=image_data
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "FULL_REFUND_CARRIER_INVESTIGATION": "We have flagged this as a potential tampering incident. A full refund has been processed and an urgent investigation into the delivery partner has been opened.",
            "SENDER_CONTACTED_REPLACEMENT_ARRANGED": "We have contacted the sender to arrange replacement of the missing or substituted items. You will receive an update within 2 hours.",
            "INVESTIGATION_INITIATED": "Your report of substituted or incomplete contents has been logged. Our team will verify with the sender and delivery partner and update you within 24 hours."
        }
        return responses.get(decision, "We understand your concern about the package contents. We will verify with the sender and provide appropriate compensation.")

    def analyze_quantity_mismatch(self, query: str) -> str:
        """Identify the type and extent of quantity mismatch"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['size', 'too small', 'too large', 'wrong size']):
            return "SIZE_MISMATCH"
        elif any(w in query_lower for w in ['quantity', 'count', 'number', 'pieces']):
            return "QUANTITY_MISMATCH"
        return "GENERAL_CONTENT_MISMATCH"

    def assess_mismatch_source(self, analysis: str, query: str) -> str:
        """Determine if mismatch is from sender or system error"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['app showed', 'booking said', 'listed as', 'system', 'invoice']):
            return "SYSTEM_RECORD_ERROR"
        elif any(w in query_lower for w in ['sender', 'shipper', 'they sent', 'packed']):
            return "SENDER_PACKING_ERROR"
        elif analysis == "SIZE_MISMATCH":
            return "BOOKING_DECLARATION_MISMATCH"
        return "SOURCE_UNDETERMINED"

    def decide_mismatch_resolution(self, analysis: str, source: str, credibility: int) -> str:
        """Decide reconciliation action for quantity mismatch"""
        # A system record error is verifiable on our side, so it refunds without sender involvement
        if source == "SYSTEM_RECORD_ERROR" and credibility >= 5:
            return "IMMEDIATE_DIFFERENCE_REFUND"
        elif analysis == "QUANTITY_MISMATCH" and credibility >= 6:
            return "IMMEDIATE_DIFFERENCE_REFUND"
        elif source == "SENDER_PACKING_ERROR" and credibility >= 4:
            return "SENDER_COORDINATION_REQUIRED"
        elif credibility >= 6:
            return "IMMEDIATE_DIFFERENCE_REFUND"
        elif credibility >= 4:
            return "SENDER_COORDINATION_REQUIRED"
        return "FULL_INVESTIGATION_REQUIRED"

    def generate_mismatch_response(self, decision: str, analysis: str, query: str, image_data: Optional[str]) -> str:
        """Generate quantity mismatch response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_quantity_mismatch",
                    user_query=f"DECISION: {decision} | MISMATCH: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor, image_data=image_data
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "IMMEDIATE_DIFFERENCE_REFUND": "We have confirmed the mismatch. A refund for the difference has been processed and will appear in your account within 24 hours.",
            "SENDER_COORDINATION_REQUIRED": "We are coordinating with the sender to resolve the quantity discrepancy. You will receive confirmation of the corrected delivery within 24 hours.",
            "FULL_INVESTIGATION_REQUIRED": "Your quantity mismatch report requires full investigation. Our team will review sender records and delivery logs to resolve this within 48 hours."
        }
        return responses.get(decision, "We apologize for the quantity discrepancy. We will coordinate with the sender to resolve and provide appropriate compensation.")
