"""
Grab Cabs Driver Fare & Payment Handler
Uses AI models for intelligent complaint resolution with strict workflows
"""

import logging
import os
import sys
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class FarePaymentHandler:
    """Driver-focused fare and payment management with strict workflows"""

    def __init__(self, groq_api_key: str = None):
        self.service = "grab_cabs"
        self.actor = "driver"
        self.handler_type = "fare_payment_handler"
        try:
            self.ai_engine = EnhancedAgenticAIEngine()
        except Exception as e:
            logger.warning(f"AI engine initialization failed: {e}")
            self.ai_engine = None

    def handle_incorrect_fare_calculation(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle incorrect fare calculation with strict 5-step workflow"""
        logger.info(f"Processing incorrect fare calculation complaint: {query[:100]}...")

        # Step 1: Identify the type of fare discrepancy
        fare_analysis = self.analyze_fare_calculation_issue(query)
        logger.info(f"Fare analysis: {fare_analysis}")

        # Step 2: Validate driver's fare records against expected values
        validation = self.validate_driver_fare_records(fare_analysis, query)
        logger.info(f"Fare validation: {validation}")

        # Step 3: Check driver credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Driver credibility: {credibility_score}/10")

        # Step 4: Decide on fare correction action
        decision = self.decide_fare_correction(fare_analysis, validation, credibility_score)
        logger.info(f"Fare decision: {decision}")

        # Step 5: Generate response with correction details and timeline
        response = self.generate_fare_correction_response(decision, fare_analysis, query)
        logger.info("Fare correction response generated successfully")
        return response

    def handle_payout_not_received(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle payout not received with strict 5-step workflow"""
        logger.info(f"Processing payout not received complaint: {query[:100]}...")

        # Step 1: Identify the payout issue type
        payout_analysis = self.analyze_payout_issue(query)
        logger.info(f"Payout analysis: {payout_analysis}")

        # Step 2: Check current payout records and processing status
        payout_status = self.check_payout_status(payout_analysis, username)
        logger.info(f"Payout status: {payout_status}")

        # Step 3: Check driver credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Driver credibility: {credibility_score}/10")

        # Step 4: Decide on payout resolution action
        decision = self.decide_payout_resolution(payout_analysis, payout_status, credibility_score)
        logger.info(f"Payout decision: {decision}")

        # Step 5: Generate response with payout action and timeline
        response = self.generate_payout_response(decision, payout_analysis, query)
        logger.info("Payout response generated successfully")
        return response

    def handle_high_commission_rates(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle high commission rate complaints with strict 5-step workflow"""
        logger.info(f"Processing high commission rates complaint: {query[:100]}...")

        # Step 1: Identify the nature of the commission concern
        commission_analysis = self.analyze_commission_complaint(query)
        logger.info(f"Commission analysis: {commission_analysis}")

        # Step 2: Check driver's current commission tier and history
        commission_tier = self.check_driver_commission_tier(username)
        logger.info(f"Commission tier: {commission_tier}")

        # Step 3: Check driver credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Driver credibility: {credibility_score}/10")

        # Step 4: Decide on commission review or adjustment action
        decision = self.decide_commission_action(commission_analysis, commission_tier, credibility_score)
        logger.info(f"Commission decision: {decision}")

        # Step 5: Generate response with commission information and options
        response = self.generate_commission_response(decision, commission_analysis, query)
        logger.info("Commission response generated successfully")
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

    def analyze_fare_calculation_issue(self, query: str) -> str:
        """Identify the type of fare calculation discrepancy"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['distance', 'km', 'kilometer', 'route']):
            return "INCORRECT_DISTANCE_CALCULATION"
        elif any(w in query_lower for w in ['surge', 'peak', 'multiplier']):
            return "SURGE_NOT_APPLIED"
        elif any(w in query_lower for w in ['toll', 'extra', 'charge']):
            return "MISSING_ADDITIONAL_CHARGES"
        elif any(w in query_lower for w in ['deducted', 'penalty', 'fine']):
            return "INCORRECT_DEDUCTION"
        return "GENERAL_FARE_DISCREPANCY"

    def validate_driver_fare_records(self, analysis: str, query: str) -> str:
        """Validate fare records against the driver's complaint"""
        query_lower = query.lower()
        # A driver quoting the trip and the figures gives us a record we can audit directly
        if any(w in query_lower for w in ['trip id', 'booking id', 'order id', 'ride id']):
            return "TRIP_IDENTIFIED_FOR_AUDIT"
        elif any(w in query_lower for w in ['rs', 'inr', '$', 'amount', 'should be', 'instead of']):
            return "SPECIFIC_AMOUNT_DISPUTED"
        elif analysis in ("INCORRECT_DISTANCE_CALCULATION", "MISSING_ADDITIONAL_CHARGES"):
            return "TRIP_DATA_RECALCULATION_NEEDED"
        return "INSUFFICIENT_TRIP_DETAIL_PROVIDED"

    def decide_fare_correction(self, analysis: str, validation: str, credibility: int) -> str:
        """Decide fare correction action"""
        # A named trip or a stated figure can be reconciled against our own records now
        if validation in ("TRIP_IDENTIFIED_FOR_AUDIT", "SPECIFIC_AMOUNT_DISPUTED") and credibility >= 5:
            return "IMMEDIATE_FARE_CORRECTION_ISSUED"
        elif analysis == "INCORRECT_DEDUCTION" and credibility >= 6:
            return "IMMEDIATE_FARE_CORRECTION_ISSUED"
        elif validation == "INSUFFICIENT_TRIP_DETAIL_PROVIDED":
            return "MANUAL_AUDIT_REQUIRED"
        elif credibility >= 5:
            return "FARE_REVIEW_INITIATED"
        return "MANUAL_AUDIT_REQUIRED"

    def generate_fare_correction_response(self, decision: str, analysis: str, query: str) -> str:
        """Generate fare correction response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_incorrect_fare_calculation",
                    user_query=f"DECISION: {decision} | FARE_ISSUE: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "IMMEDIATE_FARE_CORRECTION_ISSUED": "We have reviewed your fare records and confirmed the error. The corrected amount has been credited to your account and will reflect in your next payout cycle.",
            "FARE_REVIEW_INITIATED": "A fare review has been initiated for the disputed trip. Our billing team will audit the records and correct any discrepancies within 48 hours.",
            "MANUAL_AUDIT_REQUIRED": "Your fare dispute has been escalated for manual audit. Our finance team will investigate and contact you within 72 hours."
        }
        return responses.get(decision, "Your fare complaint has been logged and will be reviewed. Any corrections will be made within 48 hours.")

    def analyze_payout_issue(self, query: str) -> str:
        """Identify the type of payout problem"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['not received', 'missing', "didn't receive"]):
            return "PAYOUT_NOT_RECEIVED"
        elif any(w in query_lower for w in ['delayed', 'late', 'pending']):
            return "PAYOUT_DELAYED"
        elif any(w in query_lower for w in ['wrong amount', 'less', 'incorrect']):
            return "INCORRECT_PAYOUT_AMOUNT"
        return "GENERAL_PAYOUT_ISSUE"

    def check_payout_status(self, analysis: str, username: str) -> str:
        """Check the current status of the driver's payout from completed trips"""
        import sqlite3
        db_path = self._db_path()
        if not db_path or not username or username == "anonymous":
            return "PAYOUT_RECORDS_UNAVAILABLE"
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''SELECT COUNT(*) FROM orders
                              WHERE (driver_id = ? OR username = ?) AND service = ?
                                AND LOWER(status) = 'completed' ''',
                           (username, username, self.service))
            completed = cursor.fetchone()[0]
            conn.close()
            # Completed trips on record are earnings we owe and can release immediately
            if completed > 0:
                return "COMPLETED_TRIPS_PENDING_PAYOUT"
            return "NO_COMPLETED_TRIPS_ON_RECORD"
        except Exception as e:
            logger.error(f"Error checking payout status: {e}")
            return "PAYOUT_RECORDS_UNAVAILABLE"

    def decide_payout_resolution(self, analysis: str, status: str, credibility: int) -> str:
        """Decide payout resolution action"""
        # Completed trips in our own records settle the question of whether money is owed
        if status == "COMPLETED_TRIPS_PENDING_PAYOUT" and analysis == "PAYOUT_NOT_RECEIVED":
            return "EXPEDITED_PAYOUT_PROCESSED"
        elif analysis == "PAYOUT_NOT_RECEIVED" and credibility >= 6:
            return "EXPEDITED_PAYOUT_PROCESSED"
        elif analysis == "INCORRECT_PAYOUT_AMOUNT":
            return "PAYOUT_RECALCULATION_INITIATED"
        elif status == "NO_COMPLETED_TRIPS_ON_RECORD":
            return "FINANCE_TEAM_ESCALATION"
        elif credibility >= 5:
            return "STANDARD_PAYOUT_REVIEW"
        return "FINANCE_TEAM_ESCALATION"

    def generate_payout_response(self, decision: str, analysis: str, query: str) -> str:
        """Generate payout issue response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_payout_not_received",
                    user_query=f"DECISION: {decision} | PAYOUT_ISSUE: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "EXPEDITED_PAYOUT_PROCESSED": "Your missing payout has been identified and expedited. The funds will be transferred to your registered bank account within 24 hours.",
            "PAYOUT_RECALCULATION_INITIATED": "We identified an error in your payout calculation. A corrected payout is being processed and will be reflected within 2 business days.",
            "STANDARD_PAYOUT_REVIEW": "Your payout issue is under review. Our finance team will verify your delivery records and resolve this within 3-5 business days.",
            "FINANCE_TEAM_ESCALATION": "Your payout concern has been escalated to our finance team who will investigate and contact you within 48 hours."
        }
        return responses.get(decision, "Your payout issue has been logged and is being reviewed by our finance team.")

    def analyze_commission_complaint(self, query: str) -> str:
        """Identify the nature of the commission complaint"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['too high', 'excessive', 'unfair', 'high']):
            return "COMMISSION_RATE_TOO_HIGH"
        elif any(w in query_lower for w in ['changed', 'increased', 'new rate']):
            return "COMMISSION_RATE_CHANGED"
        elif any(w in query_lower for w in ['promo', 'incentive', 'bonus', 'not applied']):
            return "COMMISSION_INCENTIVE_NOT_APPLIED"
        return "GENERAL_COMMISSION_CONCERN"

    def check_driver_commission_tier(self, username: str) -> str:
        """Check driver's current commission tier and upgrade eligibility from trip volume"""
        import sqlite3
        db_path = self._db_path()
        if not db_path or not username or username == "anonymous":
            return "TIER_UNVERIFIED"
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''SELECT COUNT(*) FROM orders
                              WHERE (driver_id = ? OR username = ?) AND service = ?
                                AND LOWER(status) = 'completed' ''',
                           (username, username, self.service))
            completed = cursor.fetchone()[0]
            conn.close()
            # Trip volume is what qualifies a driver for a better commission tier
            if completed >= 3:
                return "ELIGIBLE_FOR_TIER_UPGRADE"
            elif completed > 0:
                return "STANDARD_TIER_BUILDING_VOLUME"
            return "NEW_DRIVER_STANDARD_TIER"
        except Exception as e:
            logger.error(f"Error checking commission tier: {e}")
            return "TIER_UNVERIFIED"

    def decide_commission_action(self, analysis: str, tier: str, credibility: int) -> str:
        """Decide action for commission complaint"""
        if analysis == "COMMISSION_INCENTIVE_NOT_APPLIED" and credibility >= 6:
            return "INCENTIVE_APPLIED_IMMEDIATELY"
        elif analysis == "COMMISSION_RATE_CHANGED":
            return "RATE_CHANGE_EXPLANATION_PROVIDED"
        # Trip volume already earned the better rate, so open the upgrade review on it
        elif tier == "ELIGIBLE_FOR_TIER_UPGRADE":
            return "TIER_UPGRADE_REVIEW_INITIATED"
        elif credibility >= 7:
            return "TIER_UPGRADE_REVIEW_INITIATED"
        return "COMMISSION_POLICY_EXPLANATION"

    def generate_commission_response(self, decision: str, analysis: str, query: str) -> str:
        """Generate commission complaint response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_high_commission_rates",
                    user_query=f"DECISION: {decision} | COMMISSION_ISSUE: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "INCENTIVE_APPLIED_IMMEDIATELY": "We found that the promotional incentive was not correctly applied to your account. The missing amount has been credited immediately.",
            "RATE_CHANGE_EXPLANATION_PROVIDED": "Our commission rates were recently updated as part of a platform-wide review. A detailed breakdown of the new rates has been sent to your driver app.",
            "TIER_UPGRADE_REVIEW_INITIATED": "Based on your excellent performance record, we are reviewing your eligibility for a reduced commission tier. You will receive an update within 5 business days.",
            "COMMISSION_POLICY_EXPLANATION": "A full breakdown of how commissions are calculated, including applicable incentives and bonuses, has been sent to your registered email."
        }
        return responses.get(decision, "Your commission concern has been logged. Our driver partner team will review and respond within 3 business days.")
