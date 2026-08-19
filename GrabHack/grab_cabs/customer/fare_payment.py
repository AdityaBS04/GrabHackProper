"""
Grab Cabs Customer Fare & Payment Handler
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
    """Customer-focused fare and payment management with strict workflows"""

    def __init__(self, groq_api_key: str = None):
        self.service = "grab_cabs"
        self.actor = "customer"
        self.handler_type = "fare_payment_handler"
        try:
            self.ai_engine = EnhancedAgenticAIEngine()
        except Exception as e:
            logger.warning(f"AI engine initialization failed: {e}")
            self.ai_engine = None

    def handle_incorrect_multiple_fare_charged(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle incorrect or multiple fare charged with strict 5-step workflow - TEXT ONLY"""
        logger.info(f"Processing incorrect/multiple fare complaint: {query[:100]}...")

        # Step 1: Analyze the fare discrepancy from the complaint
        fare_analysis = self.analyze_fare_discrepancy(query)
        logger.info(f"Fare analysis: {fare_analysis}")

        # Step 2: Validate the payment records and expected fare
        payment_validation = self.validate_payment_records(fare_analysis, query)
        logger.info(f"Payment validation: {payment_validation}")

        # Step 3: Check customer credibility and complaint history
        credibility_score = self.get_credibility_score(username)
        payment_history = self.check_payment_complaint_history(username)
        logger.info(f"Credibility: {credibility_score}/10, History: {payment_history}")

        # Step 4: Calculate refund amount based on discrepancy analysis
        refund_decision = self.calculate_fare_refund(fare_analysis, payment_validation, credibility_score)
        logger.info(f"Refund decision: {refund_decision}")

        # Step 5: Generate response with refund details and timeline
        response = self.generate_fare_response(refund_decision, fare_analysis, query)
        logger.info(f"Fare correction response generated successfully")

        return response

    def handle_double_payment_cash_online(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle double payment (cash + online) with strict 5-step workflow - TEXT ONLY"""
        logger.info(f"Processing double payment complaint: {query[:100]}...")

        # Step 1: Identify the double payment scenario from description
        payment_analysis = self.analyze_double_payment(query)
        logger.info(f"Double payment analysis: {payment_analysis}")

        # Step 2: Verify if both cash and online payment were collected
        payment_verification = self.verify_double_payment_occurrence(payment_analysis, query)
        logger.info(f"Payment verification: {payment_verification}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide refund amount for the duplicate payment
        refund_decision = self.decide_double_payment_refund(payment_analysis, payment_verification, credibility_score)
        logger.info(f"Refund decision: {refund_decision}")

        # Step 5: Generate response with refund confirmation and driver action
        response = self.generate_double_payment_response(refund_decision, payment_analysis, query)
        logger.info(f"Double payment response generated successfully")

        return response

    def handle_refund_adjustment_issues(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle refund and adjustment issues with strict 5-step workflow - TEXT ONLY"""
        logger.info(f"Processing refund/adjustment issues: {query[:100]}...")

        # Step 1: Identify the type of refund or adjustment issue
        refund_analysis = self.analyze_refund_issue(query)
        logger.info(f"Refund issue analysis: {refund_analysis}")

        # Step 2: Check the status of any existing refund request
        refund_status = self.check_existing_refund_status(refund_analysis, username)
        logger.info(f"Existing refund status: {refund_status}")

        # Step 3: Check customer credibility and refund history
        credibility_score = self.get_credibility_score(username)
        refund_history = self.check_refund_history(username)
        logger.info(f"Credibility: {credibility_score}/10, Refund history: {refund_history}")

        # Step 4: Determine appropriate refund action
        refund_decision = self.decide_refund_action(refund_analysis, refund_status, credibility_score, refund_history)
        logger.info(f"Refund action decision: {refund_decision}")

        # Step 5: Generate response with resolution and timeline
        response = self.generate_refund_response(refund_decision, refund_analysis, query)
        logger.info(f"Refund adjustment response generated successfully")

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

    def analyze_fare_discrepancy(self, query: str) -> str:
        """Identify the nature of the fare discrepancy"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['surge', 'dynamic', 'peak']):
            return "SURGE_PRICING_DISPUTE"
        elif any(w in query_lower for w in ['wrong fare', 'incorrect fare', 'overcharged']):
            return "OVERCHARGE_DETECTED"
        elif any(w in query_lower for w in ['multiple charge', 'charged twice', 'double charge']):
            return "DUPLICATE_CHARGE"
        return "GENERAL_FARE_DISCREPANCY"

    def validate_payment_records(self, analysis: str, query: str) -> str:
        """Validate payment records against the complaint"""
        query_lower = query.lower()
        # A rider quoting a receipt or a specific amount gives us something to reconcile against
        if any(w in query_lower for w in ['receipt', 'statement', 'screenshot', 'invoice', 'transaction id']):
            return "SUPPORTING_RECORD_REFERENCED"
        elif any(w in query_lower for w in ['rs', 'inr', '$', 'amount', 'charged me']):
            return "SPECIFIC_AMOUNT_DISPUTED"
        elif analysis == "SURGE_PRICING_DISPUTE":
            return "SURGE_APPLIED_PER_BOOKING_TERMS"
        return "NO_SUPPORTING_RECORD_PROVIDED"

    def check_payment_complaint_history(self, username: str) -> str:
        """Check customer's payment complaint history"""
        import sqlite3
        db_path = self._db_path()
        if not db_path or not username or username == "anonymous":
            return "COMPLAINT_HISTORY_UNAVAILABLE"
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''SELECT COUNT(*) FROM complaints
                              WHERE username = ? AND service = ?
                                AND (category LIKE '%fare%' OR category LIKE '%payment%'
                                     OR sub_issue LIKE '%fare%' OR sub_issue LIKE '%payment%')''',
                           (username, self.service))
            count = cursor.fetchone()[0]
            conn.close()
            # Repeated fare disputes warrant a closer look before an automatic refund
            if count >= 3:
                return "FREQUENT_PAYMENT_COMPLAINTS"
            elif count == 0:
                return "FIRST_PAYMENT_COMPLAINT"
            return "OCCASIONAL_PAYMENT_COMPLAINTS"
        except Exception as e:
            logger.error(f"Error checking payment complaint history: {e}")
            return "COMPLAINT_HISTORY_UNAVAILABLE"

    def calculate_fare_refund(self, analysis: str, validation: str, credibility: int) -> str:
        """Calculate appropriate refund amount"""
        # Surge charged per the terms the rider accepted at booking is explained, not refunded
        if validation == "SURGE_APPLIED_PER_BOOKING_TERMS" and credibility < 7:
            return "INVESTIGATION_REQUIRED"
        elif analysis == "DUPLICATE_CHARGE" and credibility >= 6:
            return "FULL_DUPLICATE_REFUND"
        elif analysis == "DUPLICATE_CHARGE" and validation == "SUPPORTING_RECORD_REFERENCED":
            return "FULL_DUPLICATE_REFUND"
        elif analysis == "OVERCHARGE_DETECTED" and credibility >= 5:
            return "DIFFERENCE_REFUND"
        elif validation == "SUPPORTING_RECORD_REFERENCED" and credibility >= 4:
            return "DIFFERENCE_REFUND"
        elif credibility >= 5:
            return "GOODWILL_CREDIT"
        return "INVESTIGATION_REQUIRED"

    def generate_fare_response(self, decision: str, analysis: str, query: str) -> str:
        """Generate fare correction response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_incorrect_multiple_fare_charged",
                    user_query=f"DECISION: {decision} | ANALYSIS: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "FULL_DUPLICATE_REFUND": "We confirmed the duplicate charge. A full refund of the extra amount has been initiated and will appear within 2-3 business days.",
            "DIFFERENCE_REFUND": "We identified the fare discrepancy and have refunded the difference. Our fare calculation team has been notified.",
            "GOODWILL_CREDIT": "We have reviewed your fare concern and added a goodwill credit to your account as a gesture of goodwill.",
            "INVESTIGATION_REQUIRED": "Your fare dispute has been logged for detailed review. Our billing team will contact you within 48 hours."
        }
        return responses.get(decision, "Your fare complaint is being reviewed. We'll resolve this within 24 hours.")

    def analyze_double_payment(self, query: str) -> str:
        """Analyze the double payment scenario"""
        query_lower = query.lower()
        if 'cash' in query_lower and 'online' in query_lower:
            return "CASH_AND_ONLINE_DOUBLE_CHARGE"
        elif 'twice' in query_lower or 'double' in query_lower:
            return "GENERAL_DOUBLE_CHARGE"
        return "SUSPECTED_DOUBLE_PAYMENT"

    def verify_double_payment_occurrence(self, analysis: str, query: str) -> str:
        """Verify whether a double payment actually occurred"""
        query_lower = query.lower()
        # A driver demanding cash on an already-paid digital booking is the clearest case
        if any(w in query_lower for w in ['driver asked', 'driver demanded', 'forced', 'insisted']):
            return "DRIVER_COLLECTED_CASH_ON_PAID_RIDE"
        elif any(w in query_lower for w in ['receipt', 'statement', 'screenshot', 'both charges']):
            return "DOUBLE_PAYMENT_EVIDENCED"
        elif analysis == "CASH_AND_ONLINE_DOUBLE_CHARGE":
            return "DOUBLE_PAYMENT_LIKELY"
        return "DOUBLE_PAYMENT_UNCONFIRMED"

    def decide_double_payment_refund(self, analysis: str, verification: str, credibility: int) -> str:
        """Decide the refund for double payment"""
        # Cash taken on a prepaid ride is a driver violation, refunded on its own merits
        if verification == "DRIVER_COLLECTED_CASH_ON_PAID_RIDE":
            return "IMMEDIATE_REFUND_DRIVER_PENALIZED"
        elif verification == "DOUBLE_PAYMENT_EVIDENCED" and credibility >= 4:
            return "IMMEDIATE_REFUND_DRIVER_PENALIZED"
        elif credibility >= 6:
            return "IMMEDIATE_REFUND_DRIVER_PENALIZED"
        # Cash plus an online charge on one ride is a concrete, checkable claim
        elif analysis == "CASH_AND_ONLINE_DOUBLE_CHARGE" and credibility >= 4:
            return "REFUND_AFTER_VERIFICATION"
        elif verification == "DOUBLE_PAYMENT_UNCONFIRMED" and credibility < 6:
            return "INVESTIGATION_REQUIRED"
        elif credibility >= 4:
            return "REFUND_AFTER_VERIFICATION"
        return "INVESTIGATION_REQUIRED"

    def generate_double_payment_response(self, decision: str, analysis: str, query: str) -> str:
        """Generate double payment response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_double_payment_cash_online",
                    user_query=f"DECISION: {decision} | ANALYSIS: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "IMMEDIATE_REFUND_DRIVER_PENALIZED": "We have confirmed the double payment. The duplicate amount has been immediately refunded and the driver issued a warning for collecting cash on a digital-only booking.",
            "REFUND_AFTER_VERIFICATION": "Your double payment claim is being verified against transaction records. If confirmed, a full refund will be processed within 24 hours.",
            "INVESTIGATION_REQUIRED": "Your double payment report is under review. Our finance team will investigate and contact you within 48 hours."
        }
        return responses.get(decision, "Your double payment complaint is being processed.")

    def analyze_refund_issue(self, query: str) -> str:
        """Identify the type of refund issue"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['not received', 'not processed', "haven't received"]):
            return "REFUND_NOT_RECEIVED"
        elif any(w in query_lower for w in ['wrong amount', 'partial', 'less']):
            return "INCORRECT_REFUND_AMOUNT"
        elif any(w in query_lower for w in ['delayed', 'late', 'taking long']):
            return "REFUND_DELAYED"
        return "GENERAL_REFUND_ISSUE"

    def check_existing_refund_status(self, analysis: str, username: str) -> str:
        """Check status of any pending refund"""
        import sqlite3
        db_path = self._db_path()
        if not db_path or not username or username == "anonymous":
            return "NO_PRIOR_REFUND_REQUEST"
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''SELECT status FROM complaints
                              WHERE username = ? AND service = ?
                                AND (sub_issue LIKE '%refund%' OR sub_issue LIKE '%payment%')
                              ORDER BY created_at DESC LIMIT 1''',
                           (username, self.service))
            row = cursor.fetchone()
            conn.close()
            if not row:
                return "NO_PRIOR_REFUND_REQUEST"
            return "PRIOR_REFUND_RESOLVED" if (row[0] or "").lower() == 'resolved' else "PRIOR_REFUND_STILL_PENDING"
        except Exception as e:
            logger.error(f"Error checking existing refund status: {e}")
            return "NO_PRIOR_REFUND_REQUEST"

    def check_refund_history(self, username: str) -> str:
        """Check customer's refund request history"""
        import sqlite3
        db_path = self._db_path()
        if not db_path or not username or username == "anonymous":
            return "REFUND_HISTORY_UNAVAILABLE"
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''SELECT COUNT(*) FROM complaints
                              WHERE username = ? AND sub_issue LIKE '%refund%' ''',
                           (username,))
            count = cursor.fetchone()[0]
            conn.close()
            if count >= 4:
                return "HIGH_REFUND_REQUEST_FREQUENCY"
            elif count == 0:
                return "NO_REFUND_HISTORY"
            return "NORMAL_REFUND_FREQUENCY"
        except Exception as e:
            logger.error(f"Error checking refund history: {e}")
            return "REFUND_HISTORY_UNAVAILABLE"

    def decide_refund_action(self, analysis: str, status: str, credibility: int, history: str) -> str:
        """Determine refund action"""
        # An unusual volume of refund claims goes to a person before any money moves
        if history == "HIGH_REFUND_REQUEST_FREQUENCY" and credibility < 7:
            return "MANUAL_REVIEW_REQUIRED"
        # A refund already logged and still pending is overdue, so it jumps the queue
        elif status == "PRIOR_REFUND_STILL_PENDING":
            return "EXPEDITE_REFUND_PROCESSING"
        elif analysis == "REFUND_NOT_RECEIVED" and credibility >= 6:
            return "EXPEDITE_REFUND_PROCESSING"
        elif analysis == "INCORRECT_REFUND_AMOUNT":
            return "RECALCULATE_AND_REPROCESS"
        elif analysis == "REFUND_DELAYED" and credibility >= 5:
            return "EXPEDITE_REFUND_PROCESSING"
        elif credibility >= 5:
            return "STANDARD_REFUND_PROCESSING"
        return "MANUAL_REVIEW_REQUIRED"

    def generate_refund_response(self, decision: str, analysis: str, query: str) -> str:
        """Generate refund resolution response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_refund_adjustment_issues",
                    user_query=f"DECISION: {decision} | ANALYSIS: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "EXPEDITE_REFUND_PROCESSING": "Your refund has been expedited and will appear in your account within 24 hours. We apologize for the delay.",
            "RECALCULATE_AND_REPROCESS": "We identified an incorrect refund amount and are reprocessing the correct amount. You will receive the difference within 2 business days.",
            "STANDARD_REFUND_PROCESSING": "Your refund is being processed and should appear within 3-5 business days.",
            "MANUAL_REVIEW_REQUIRED": "Your refund request requires manual review. Our billing team will contact you within 48 hours."
        }
        return responses.get(decision, "Your refund request has been received and is being processed.")
