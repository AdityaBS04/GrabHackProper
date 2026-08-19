"""
Grab Express Customer Payment & Refund Handler
Handles payment and refund issues for express deliveries
"""

import logging
import os
import sys
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class PaymentRefundHandler:
    """Express delivery payment and refund management with strict workflows"""

    def __init__(self):
        self.service = "grab_express"
        self.actor = "customer"
        self.handler_type = "payment_refund_handler"
        try:
            self.ai_engine = EnhancedAgenticAIEngine()
        except Exception as e:
            logger.warning(f"AI engine initialization failed: {e}")
            self.ai_engine = None

    def handle_double_charge(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle double charge for single delivery with strict 5-step workflow"""
        logger.info(f"Processing double charge complaint: {query[:100]}...")

        # Step 1: Identify the double charge scenario
        charge_analysis = self.analyze_double_charge_scenario(query)
        logger.info(f"Charge analysis: {charge_analysis}")

        # Step 2: Validate against payment records
        payment_validation = self.validate_double_charge_records(charge_analysis, username)
        logger.info(f"Payment validation: {payment_validation}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on refund action
        decision = self.decide_double_charge_refund(charge_analysis, payment_validation, credibility_score)
        logger.info(f"Refund decision: {decision}")

        # Step 5: Generate response with refund confirmation and timeline
        response = self.generate_double_charge_response(decision, charge_analysis, query)
        logger.info("Double charge response generated successfully")
        return response

    def handle_failed_payment_money_deducted(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle failed payment but money deducted with strict 5-step workflow"""
        logger.info(f"Processing failed payment complaint: {query[:100]}...")

        # Step 1: Identify the payment failure scenario
        payment_analysis = self.analyze_failed_payment_scenario(query)
        logger.info(f"Payment analysis: {payment_analysis}")

        # Step 2: Check payment gateway and transaction records
        transaction_check = self.check_transaction_status(payment_analysis, username)
        logger.info(f"Transaction check: {transaction_check}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on refund and delivery continuation action
        decision = self.decide_failed_payment_resolution(payment_analysis, transaction_check, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with refund and delivery status
        response = self.generate_failed_payment_response(decision, payment_analysis, query)
        logger.info("Failed payment response generated successfully")
        return response

    def handle_cod_marked_prepaid(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle COD delivery incorrectly marked as prepaid with strict 5-step workflow"""
        logger.info(f"Processing COD/prepaid mismatch complaint: {query[:100]}...")

        # Step 1: Identify the payment method error type
        payment_error_analysis = self.analyze_payment_method_error(query)
        logger.info(f"Payment error analysis: {payment_error_analysis}")

        # Step 2: Verify the original booking payment method
        booking_verification = self.verify_original_payment_method(payment_error_analysis, username)
        logger.info(f"Booking verification: {booking_verification}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on correction and refund action
        decision = self.decide_payment_method_correction(payment_error_analysis, booking_verification, credibility_score)
        logger.info(f"Correction decision: {decision}")

        # Step 5: Generate response with correction and refund details
        response = self.generate_cod_correction_response(decision, payment_error_analysis, query)
        logger.info("COD/prepaid correction response generated successfully")
        return response

    def handle_refund_not_initiated(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle refund not initiated for damaged/lost package with strict 5-step workflow"""
        logger.info(f"Processing refund not initiated complaint: {query[:100]}...")

        # Step 1: Identify the refund issue type
        refund_analysis = self.analyze_refund_issue(query)
        logger.info(f"Refund analysis: {refund_analysis}")

        # Step 2: Check the status of any existing refund request
        refund_status = self.check_existing_refund_status(refund_analysis, username)
        logger.info(f"Refund status: {refund_status}")

        # Step 3: Check customer credibility and refund history
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on expedite or initiate refund action
        decision = self.decide_refund_action(refund_analysis, refund_status, credibility_score)
        logger.info(f"Refund decision: {decision}")

        # Step 5: Generate response with refund processing confirmation
        response = self.generate_refund_response(decision, refund_analysis, query)
        logger.info("Refund not initiated response generated successfully")
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

    def analyze_double_charge_scenario(self, query: str) -> str:
        """Identify the double charge scenario"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['twice', 'two times', 'same order']):
            return "DUPLICATE_TRANSACTION"
        elif any(w in query_lower for w in ['cash and online', 'cash and card']):
            return "CASH_AND_ONLINE_DOUBLE_CHARGE"
        return "GENERAL_DOUBLE_CHARGE"

    def validate_double_charge_records(self, analysis: str, username: str) -> str:
        """Validate payment records for double charge against the customer's order history"""
        import sqlite3
        db_path = self._db_path()
        if not db_path or not username or username == "anonymous":
            return "RECORDS_UNAVAILABLE"
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            # Two orders at the same price on the same day is the signature of a duplicate charge
            cursor.execute('''SELECT COUNT(*) FROM orders
                              WHERE username = ? AND service = ?
                              GROUP BY price, date(date) HAVING COUNT(*) > 1''',
                           (username, self.service))
            duplicate_found = cursor.fetchone() is not None
            conn.close()
            return "DUPLICATE_CONFIRMED_IN_RECORDS" if duplicate_found else "NO_DUPLICATE_IN_RECORDS"
        except Exception as e:
            logger.error(f"Error validating double charge records: {e}")
            return "RECORDS_UNAVAILABLE"

    def decide_double_charge_refund(self, analysis: str, validation: str, credibility: int) -> str:
        """Decide refund action for double charge"""
        # A duplicate confirmed in our own records refunds regardless of credibility
        if validation == "DUPLICATE_CONFIRMED_IN_RECORDS":
            return "IMMEDIATE_DUPLICATE_REFUND"
        elif analysis == "DUPLICATE_TRANSACTION" and credibility >= 6:
            return "IMMEDIATE_DUPLICATE_REFUND"
        elif validation == "NO_DUPLICATE_IN_RECORDS" and credibility < 5:
            return "INVESTIGATION_REQUIRED"
        elif credibility >= 5:
            return "REFUND_AFTER_VERIFICATION"
        return "INVESTIGATION_REQUIRED"

    def generate_double_charge_response(self, decision: str, analysis: str, query: str) -> str:
        """Generate double charge response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_double_charge",
                    user_query=f"DECISION: {decision} | CHARGE: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "IMMEDIATE_DUPLICATE_REFUND": "We have confirmed the duplicate charge. The extra amount has been immediately refunded and will appear in your account within 2-3 business days.",
            "REFUND_AFTER_VERIFICATION": "Your double charge claim is being verified against our payment records. If confirmed, a full refund will be processed within 24 hours.",
            "INVESTIGATION_REQUIRED": "Your double charge report is under investigation. Our finance team will review transaction records and respond within 48 hours."
        }
        return responses.get(decision, "We apologize for the double charge. The duplicate charge will be refunded within 2-3 business days.")

    def analyze_failed_payment_scenario(self, query: str) -> str:
        """Identify the failed payment scenario"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['deducted', 'debited', 'charged']):
            return "MONEY_DEDUCTED_ORDER_FAILED"
        elif any(w in query_lower for w in ['pending', 'processing', 'stuck']):
            return "PAYMENT_STUCK_IN_PROCESSING"
        return "GENERAL_FAILED_PAYMENT"

    def check_transaction_status(self, analysis: str, username: str) -> str:
        """Check payment gateway transaction status from the customer's recent orders"""
        import sqlite3
        db_path = self._db_path()
        if not db_path or not username or username == "anonymous":
            return "TRANSACTION_STATUS_UNKNOWN"
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''SELECT status FROM orders
                              WHERE username = ? AND service = ?
                              ORDER BY date DESC LIMIT 1''',
                           (username, self.service))
            row = cursor.fetchone()
            conn.close()
            if not row:
                return "TRANSACTION_STATUS_UNKNOWN"
            status = (row[0] or "").lower()
            if status in ('cancelled', 'failed'):
                return "ORDER_FAILED_PAYMENT_CAPTURED"
            elif status in ('pending', 'in_progress'):
                return "TRANSACTION_STILL_PROCESSING"
            return "ORDER_COMPLETED_PAYMENT_VALID"
        except Exception as e:
            logger.error(f"Error checking transaction status: {e}")
            return "TRANSACTION_STATUS_UNKNOWN"

    def decide_failed_payment_resolution(self, analysis: str, transaction_check: str, credibility: int) -> str:
        """Decide resolution for failed payment with money deducted"""
        # A failed order with a captured payment is an unambiguous refund case
        if transaction_check == "ORDER_FAILED_PAYMENT_CAPTURED":
            return "IMMEDIATE_REFUND_ORDER_REINSTATED"
        elif analysis == "MONEY_DEDUCTED_ORDER_FAILED" and credibility >= 6:
            return "IMMEDIATE_REFUND_ORDER_REINSTATED"
        elif transaction_check == "TRANSACTION_STILL_PROCESSING":
            return "PAYMENT_GATEWAY_INVESTIGATION"
        elif credibility >= 5:
            return "REFUND_PROCESSED_24_HOURS"
        return "PAYMENT_GATEWAY_INVESTIGATION"

    def generate_failed_payment_response(self, decision: str, analysis: str, query: str) -> str:
        """Generate failed payment response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_failed_payment_money_deducted",
                    user_query=f"DECISION: {decision} | PAYMENT: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "IMMEDIATE_REFUND_ORDER_REINSTATED": "We have confirmed the payment failure. Your money has been fully refunded and the order has been reinstated at no extra cost. The delivery will proceed as scheduled.",
            "REFUND_PROCESSED_24_HOURS": "The deducted amount is being refunded and will appear in your account within 24 hours. Your delivery has been confirmed as paid and is proceeding normally.",
            "PAYMENT_GATEWAY_INVESTIGATION": "We are investigating the payment processing issue with our payment gateway. A refund will be initiated once confirmed, within 48 hours."
        }
        return responses.get(decision, "Payment processing errors will be resolved immediately. The deducted amount will be refunded within 24 hours.")

    def analyze_payment_method_error(self, query: str) -> str:
        """Identify the payment method discrepancy"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['cod', 'cash on delivery', 'should be cash']):
            return "COD_CHARGED_ONLINE"
        elif any(w in query_lower for w in ['prepaid', 'online', 'already paid']):
            return "PREPAID_ASKED_FOR_CASH"
        return "GENERAL_PAYMENT_METHOD_ERROR"

    def verify_original_payment_method(self, analysis: str, username: str) -> str:
        """Verify the original booking payment method from records"""
        import sqlite3
        db_path = self._db_path()
        if not db_path or not username or username == "anonymous":
            return "PAYMENT_METHOD_UNVERIFIED"
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''SELECT payment_method FROM orders
                              WHERE username = ? AND service = ?
                              ORDER BY date DESC LIMIT 1''',
                           (username, self.service))
            row = cursor.fetchone()
            conn.close()
            if not row or not row[0]:
                return "PAYMENT_METHOD_UNVERIFIED"
            method = row[0].lower()
            if 'cod' in method or 'cash' in method:
                return "COD_CONFIRMED_IN_RECORDS"
            return "PREPAID_CONFIRMED_IN_RECORDS"
        except Exception as e:
            logger.error(f"Error verifying payment method: {e}")
            return "PAYMENT_METHOD_UNVERIFIED"

    def decide_payment_method_correction(self, analysis: str, verification: str, credibility: int) -> str:
        """Decide correction action for payment method error"""
        # If booking records contradict how the customer was charged, correct it right away
        booking_contradicts_charge = (
            (analysis == "COD_CHARGED_ONLINE" and verification == "COD_CONFIRMED_IN_RECORDS") or
            (analysis == "PREPAID_ASKED_FOR_CASH" and verification == "PREPAID_CONFIRMED_IN_RECORDS")
        )
        if booking_contradicts_charge:
            return "IMMEDIATE_CORRECTION_REFUND_IF_APPLICABLE"
        elif verification == "PAYMENT_METHOD_UNVERIFIED" and credibility < 6:
            return "MANUAL_REVIEW_REQUIRED"
        elif credibility >= 6:
            return "IMMEDIATE_CORRECTION_REFUND_IF_APPLICABLE"
        elif credibility >= 4:
            return "CORRECTION_AFTER_VERIFICATION"
        return "MANUAL_REVIEW_REQUIRED"

    def generate_cod_correction_response(self, decision: str, analysis: str, query: str) -> str:
        """Generate COD/prepaid correction response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_cod_marked_prepaid",
                    user_query=f"DECISION: {decision} | PAYMENT_ERROR: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "IMMEDIATE_CORRECTION_REFUND_IF_APPLICABLE": "We have corrected the payment method error. If you were incorrectly charged online for a COD delivery, the amount has been refunded immediately.",
            "CORRECTION_AFTER_VERIFICATION": "Your payment method discrepancy is being verified. The correction will be applied and any applicable refund processed within 24 hours.",
            "MANUAL_REVIEW_REQUIRED": "Your payment method error requires manual review. Our billing team will investigate and contact you within 48 hours."
        }
        return responses.get(decision, "Payment method errors will be corrected immediately. Any incorrect charges will be refunded within 24 hours.")

    def analyze_refund_issue(self, query: str) -> str:
        """Identify the type of refund issue"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['not received', 'not processed', "haven't received"]):
            return "REFUND_NOT_RECEIVED"
        elif any(w in query_lower for w in ['delayed', 'late', 'taking long']):
            return "REFUND_DELAYED"
        elif any(w in query_lower for w in ['wrong amount', 'partial', 'less']):
            return "INCORRECT_REFUND_AMOUNT"
        return "GENERAL_REFUND_ISSUE"

    def check_existing_refund_status(self, analysis: str, username: str) -> str:
        """Check the status of any existing refund request in the complaint log"""
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
            logger.error(f"Error checking refund status: {e}")
            return "NO_PRIOR_REFUND_REQUEST"

    def decide_refund_action(self, analysis: str, status: str, credibility: int) -> str:
        """Decide the refund action to take"""
        # A refund logged earlier and still pending is already overdue, so it jumps the queue
        if status == "PRIOR_REFUND_STILL_PENDING":
            return "EXPEDITE_REFUND_PROCESSING"
        elif analysis == "REFUND_NOT_RECEIVED" and credibility >= 6:
            return "EXPEDITE_REFUND_PROCESSING"
        elif analysis == "INCORRECT_REFUND_AMOUNT":
            return "RECALCULATE_AND_REPROCESS"
        elif analysis == "REFUND_DELAYED" and credibility >= 5:
            return "EXPEDITE_REFUND_PROCESSING"
        elif credibility >= 5:
            return "STANDARD_REFUND_REVIEW"
        return "MANUAL_REVIEW_REQUIRED"

    def generate_refund_response(self, decision: str, analysis: str, query: str) -> str:
        """Generate refund resolution response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_refund_not_initiated",
                    user_query=f"DECISION: {decision} | REFUND_ISSUE: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "EXPEDITE_REFUND_PROCESSING": "Your refund has been expedited and will appear in your account within 24 hours. We sincerely apologize for the delay.",
            "RECALCULATE_AND_REPROCESS": "We identified an error in the refund amount. The correct amount has been recalculated and the difference will be processed within 2 business days.",
            "STANDARD_REFUND_REVIEW": "Your refund request is being processed and should appear within 3-5 business days.",
            "MANUAL_REVIEW_REQUIRED": "Your refund requires manual review due to the complexity of the issue. Our billing team will contact you within 48 hours."
        }
        return responses.get(decision, "We apologize for the refund delay. Your refund is being processed immediately and will be credited within 24-48 hours.")
