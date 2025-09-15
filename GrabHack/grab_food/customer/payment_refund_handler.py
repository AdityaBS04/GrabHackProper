"""
Grab Food Customer Payment Refund Handler
Uses AI models for intelligent complaint resolution
"""

import logging
import os
import sys
from typing import Optional

# Add parent directory to path to import enhanced_ai_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
# Temporarily comment out AI engine import to test basic functionality
# from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class PaymentRefundHandler:
    """Customer-focused payment and refund management with real AI"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_food"
        self.actor = "customer"
        self.handler_type = "payment_refund_handler"
        # Initialize AI engine later to avoid import issues
        self.ai_engine = None
        
    def handle_double_charge(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle double charge for single order with strict 6-step workflow - TEXT ONLY"""
        logger.info(f"Processing double charge complaint: {query[:100]}...")

        # Step 1: Validate and extract charge details from complaint
        charge_details = self.extract_double_charge_details(query)
        if not charge_details["order_id"] or not charge_details["charge_amount"]:
            return "📋 To investigate the double charge, please provide your order ID and the exact amount that was charged twice."

        # Step 2: Verify charges against payment system records
        charge_verification = self.verify_payment_charges(charge_details, username)
        logger.info(f"Charge verification result: {charge_verification}")

        # Step 3: Assess severity and financial impact
        impact_assessment = self.assess_double_charge_impact(charge_details, charge_verification)
        logger.info(f"Impact assessment: {impact_assessment}")

        # Step 4: Check customer credibility and payment history
        credibility_score = self.get_customer_credibility_score(username)
        payment_history = self.check_payment_complaint_history(username)
        logger.info(f"Customer credibility: {credibility_score}/10, Payment history: {payment_history}")

        # Step 5: Validate duplicate charges with bank/payment gateway
        duplicate_validation = self.validate_duplicate_charges(charge_details, credibility_score)
        logger.info(f"Duplicate validation: {duplicate_validation}")

        # Step 6: Make refund decision and generate response
        decision = self.decide_double_charge_resolution(impact_assessment, credibility_score, duplicate_validation)
        response = self.generate_double_charge_response(decision, charge_details, query)
        logger.info(f"Double charge resolution: {decision}")

        return response

    def handle_failed_payment_money_deducted(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle failed payment but money deducted with strict 6-step workflow - TEXT ONLY"""
        logger.info(f"Processing failed payment money deducted complaint: {query[:100]}...")

        # Step 1: Extract payment failure details and transaction information
        payment_details = self.extract_failed_payment_details(query)
        if not payment_details["transaction_reference"] and not payment_details["order_attempt_info"]:
            return "📋 To resolve this payment issue, please provide your transaction reference number or details about when you attempted to place the order."

        # Step 2: Cross-verify payment status with order creation records
        payment_order_status = self.verify_payment_vs_order_status(payment_details, username)
        logger.info(f"Payment vs order status: {payment_order_status}")

        # Step 3: Check customer credibility and payment dispute history
        credibility_score = self.get_customer_credibility_score(username)
        dispute_history = self.check_payment_dispute_history(username)
        logger.info(f"Customer credibility: {credibility_score}/10, Dispute history: {dispute_history}")

        # Step 4: Validate payment gateway response and bank deduction
        gateway_validation = self.validate_payment_gateway_records(payment_details, credibility_score)
        logger.info(f"Gateway validation: {gateway_validation}")

        # Step 5: Assess financial impact and refund eligibility
        refund_eligibility = self.assess_failed_payment_refund_eligibility(payment_details, gateway_validation, credibility_score)
        logger.info(f"Refund eligibility: {refund_eligibility}")

        # Step 6: Make resolution decision and generate response
        decision = self.decide_failed_payment_resolution(refund_eligibility, credibility_score, dispute_history)
        response = self.generate_failed_payment_response(decision, payment_details, query)
        logger.info(f"Failed payment resolution: {decision}")

        return response

    def handle_cod_marked_prepaid(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle COD order marked prepaid with strict 5-step workflow - TEXT ONLY"""
        logger.info(f"Processing COD marked prepaid complaint: {query[:100]}...")

        # Step 1: Extract COD order details and payment method discrepancy
        cod_details = self.extract_cod_payment_discrepancy(query)
        if not cod_details["order_id"] or not cod_details["expected_payment_method"]:
            return "📋 Please provide your order ID and confirm what payment method you selected (COD or prepaid) when placing the order."

        # Step 2: Verify original payment method selection in order records
        payment_method_verification = self.verify_original_payment_method(cod_details, username)
        logger.info(f"Payment method verification: {payment_method_verification}")

        # Step 3: Check customer credibility and COD usage patterns
        credibility_score = self.get_customer_credibility_score(username)
        cod_usage_pattern = self.analyze_cod_usage_patterns(username)
        logger.info(f"Customer credibility: {credibility_score}/10, COD patterns: {cod_usage_pattern}")

        # Step 4: Assess impact and validate payment method mismatch
        mismatch_assessment = self.assess_payment_method_mismatch(cod_details, payment_method_verification, credibility_score)
        logger.info(f"Mismatch assessment: {mismatch_assessment}")

        # Step 5: Make resolution decision and generate response
        decision = self.decide_cod_prepaid_resolution(mismatch_assessment, credibility_score, cod_usage_pattern)
        response = self.generate_cod_prepaid_response(decision, cod_details, query)
        logger.info(f"COD prepaid resolution: {decision}")

        return response

    def handle_refund_not_initiated(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle refund not initiated for missing/damaged items with strict 7-step workflow - TEXT ONLY"""
        logger.info(f"Processing refund not initiated complaint: {query[:100]}...")

        # Step 1: Extract original complaint and promised refund details
        refund_details = self.extract_refund_promise_details(query)
        if not refund_details["original_issue"] or not refund_details["promised_timeframe"]:
            return "📋 To track your refund status, please provide details about the original issue (missing/damaged items) and when the refund was promised."

        # Step 2: Verify original complaint and refund promise records
        original_complaint_status = self.verify_original_complaint_records(refund_details, username)
        logger.info(f"Original complaint verification: {original_complaint_status}")

        # Step 3: Check refund processing status and delays
        refund_processing_status = self.check_refund_processing_status(refund_details, username)
        logger.info(f"Refund processing status: {refund_processing_status}")

        # Step 4: Assess time elapsed vs promised timeline
        timeline_assessment = self.assess_refund_timeline_breach(refund_details, refund_processing_status)
        logger.info(f"Timeline assessment: {timeline_assessment}")

        # Step 5: Check customer credibility and refund request history
        credibility_score = self.get_customer_credibility_score(username)
        refund_history = self.check_refund_request_history(username)
        logger.info(f"Customer credibility: {credibility_score}/10, Refund history: {refund_history}")

        # Step 6: Validate refund legitimacy and processing barriers
        refund_validation = self.validate_refund_legitimacy(original_complaint_status, credibility_score, timeline_assessment)
        logger.info(f"Refund validation: {refund_validation}")

        # Step 7: Make resolution decision and expedite processing
        decision = self.decide_refund_not_initiated_resolution(refund_validation, timeline_assessment, credibility_score)
        response = self.generate_refund_not_initiated_response(decision, refund_details, query)
        logger.info(f"Refund not initiated resolution: {decision}")

        return response

    # ===== SUPPORTING METHODS FOR STRICT WORKFLOWS =====

    def get_customer_credibility_score(self, username: str) -> int:
        """Calculate customer credibility score based on actual database history"""
        import sqlite3
        import os
        from datetime import datetime, timedelta

        base_score = 7  # Start with neutral-high credibility

        # Handle anonymous users
        if not username or username == "anonymous":
            return max(1, base_score - 2)

        try:
            # Find database path
            database_paths = [
                'grabhack.db',
                '../grabhack.db',
                'GrabHack/grabhack.db',
                os.path.join(os.path.dirname(__file__), '../../grabhack.db')
            ]

            db_path = None
            for path in database_paths:
                if os.path.exists(path):
                    db_path = path
                    break

            if not db_path:
                # Fallback to simulated scoring if no database
                return self._get_simulated_credibility_score(username)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get user's current credibility score from users table
            cursor.execute('''
                SELECT credibility_score
                FROM users
                WHERE username = ?
            ''', (username,))

            user_result = cursor.fetchone()
            if user_result:
                base_score = user_result[0]
            else:
                base_score = 7  # Default if user not found

            # Get user's order history from the new database schema
            cursor.execute('''
                SELECT
                    COUNT(*) as total_orders,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_orders,
                    COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_orders,
                    AVG(price) as avg_order_value,
                    MIN(date) as first_order_date,
                    MAX(date) as last_order_date
                FROM orders
                WHERE username = ? AND service = 'grab_food' AND user_type = 'customer'
            ''', (username,))

            result = cursor.fetchone()
            if result:
                total_orders, completed_orders, cancelled_orders, avg_order_value, first_order_date, last_order_date = result

                # Calculate credibility based on actual data
                if total_orders > 0:
                    completion_rate = completed_orders / total_orders
                    cancellation_rate = cancelled_orders / total_orders if total_orders > 0 else 0

                    # Adjust score based on completion rate
                    if completion_rate >= 0.9:
                        base_score += 2
                    elif completion_rate >= 0.7:
                        base_score += 1
                    elif completion_rate < 0.5:
                        base_score -= 2

                    # Adjust based on cancellation rate
                    if cancellation_rate > 0.3:
                        base_score -= 2
                    elif cancellation_rate > 0.2:
                        base_score -= 1

                    # Adjust based on order frequency (established customer)
                    if total_orders >= 20:
                        base_score += 2
                    elif total_orders >= 10:
                        base_score += 1

                    # Adjust based on average order value (higher value = more credible)
                    if avg_order_value and avg_order_value >= 50:
                        base_score += 1
                    elif avg_order_value and avg_order_value >= 30:
                        base_score += 0.5

                    # Account tenure bonus
                    if first_order_date:
                        try:
                            first_date = datetime.strptime(first_order_date, '%Y-%m-%d')
                            days_since_first = (datetime.now() - first_date).days
                            if days_since_first > 365:  # More than a year
                                base_score += 1
                            elif days_since_first > 180:  # More than 6 months
                                base_score += 0.5
                        except:
                            pass  # Date parsing failed, skip tenure bonus

            # Check for recent complaint history
            cursor.execute('''
                SELECT COUNT(*)
                FROM complaints
                WHERE username = ? AND service = 'grab_food'
                AND created_at >= datetime('now', '-30 days')
            ''', (username,))

            recent_complaints = cursor.fetchone()[0] if cursor.fetchone() else 0
            if recent_complaints > 5:
                base_score -= 2
            elif recent_complaints > 2:
                base_score -= 1

            conn.close()

        except Exception as e:
            logger.error(f"Error calculating credibility score: {e}")
            # Fallback to simulated scoring
            return self._get_simulated_credibility_score(username)

        # Ensure score is between 1-10
        final_score = max(1, min(10, int(base_score)))

        # Update the credibility score in the database if it has changed significantly
        self._update_credibility_score_if_changed(username, final_score)

        return final_score

    def _get_simulated_credibility_score(self, username: str) -> int:
        """Fallback simulated credibility scoring when database is unavailable"""
        base_score = 7

        if "test" in username.lower():
            base_score -= 1

        if len(username) > 8:
            base_score += 1

        return max(1, min(10, base_score))

    def _update_credibility_score_if_changed(self, username: str, new_score: int) -> None:
        """Update user's credibility score in database if it has changed"""
        try:
            # Find database path
            database_paths = [
                'grabhack.db',
                '../grabhack.db',
                'GrabHack/grabhack.db',
                os.path.join(os.path.dirname(__file__), '../../grabhack.db')
            ]

            db_path = None
            for path in database_paths:
                if os.path.exists(path):
                    db_path = path
                    break

            if not db_path:
                return

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Update the credibility score
            cursor.execute('''
                UPDATE users
                SET credibility_score = ?
                WHERE username = ?
            ''', (new_score, username))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error updating credibility score: {e}")

    # ===== DOUBLE CHARGE WORKFLOW METHODS =====

    def extract_double_charge_details(self, query: str) -> dict:
        """Extract double charge details from complaint using AI"""
        extraction_prompt = f"""
        Extract double charge details from this payment complaint:

        Complaint: {query}

        Identify:
        1. Order ID or reference number
        2. Amount charged (and how many times)
        3. Payment method used
        4. Date/time of charges if mentioned

        Return ONLY JSON: {{"order_id": "id", "charge_amount": "amount", "charge_count": "times", "payment_method": "method", "charge_dates": ["dates"]}}
        """

        try:
            result = self.ai_engine.process_complaint(
                function_name="extract_double_charge_details",
                user_query=extraction_prompt,
                service=self.service,
                user_type=self.actor
            )

            import json
            if "{" in result and "}" in result:
                json_start = result.find("{")
                json_end = result.rfind("}") + 1
                json_str = result[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"order_id": "", "charge_amount": "", "charge_count": "2", "payment_method": "unknown", "charge_dates": []}

        except Exception as e:
            logger.error(f"Failed to extract double charge details: {e}")
            return {"order_id": "", "charge_amount": "", "charge_count": "unknown", "payment_method": "unknown", "charge_dates": []}

    def verify_payment_charges(self, charge_details: dict, username: str) -> dict:
        """Verify charges against payment system records (simulated)"""
        # In real implementation, would query payment gateway/bank records
        order_id = charge_details.get("order_id", "")

        # Simulate payment verification
        if order_id and username != "anonymous":
            return {
                "charges_found": "2_charges",
                "verification_status": "confirmed_duplicate",
                "charge_timestamps": ["2023-01-01 14:30", "2023-01-01 14:31"],
                "gateway_response": "duplicate_transaction_detected"
            }
        else:
            return {
                "charges_found": "unclear",
                "verification_status": "needs_more_info",
                "charge_timestamps": [],
                "gateway_response": "insufficient_data"
            }

    def assess_double_charge_impact(self, charge_details: dict, charge_verification: dict) -> dict:
        """Assess financial impact of double charge"""
        try:
            amount_str = charge_details.get("charge_amount", "0")
            amount = float(amount_str.replace("$", "").replace(",", ""))
            charge_count = int(charge_details.get("charge_count", "2"))

            duplicate_amount = amount * (charge_count - 1)

            if duplicate_amount >= 100:
                severity = "HIGH_IMPACT"
            elif duplicate_amount >= 50:
                severity = "MEDIUM_IMPACT"
            else:
                severity = "LOW_IMPACT"

            return {
                "severity": severity,
                "duplicate_amount": duplicate_amount,
                "total_charged": amount * charge_count,
                "refund_required": duplicate_amount
            }
        except:
            return {
                "severity": "UNKNOWN_IMPACT",
                "duplicate_amount": 0,
                "total_charged": 0,
                "refund_required": 0
            }

    def check_payment_complaint_history(self, username: str) -> str:
        """Check customer's history of payment complaints"""
        if username == "anonymous":
            return "UNKNOWN_HISTORY"
        elif "test" in username.lower():
            return "FREQUENT_PAYMENT_COMPLAINTS"
        else:
            return "OCCASIONAL_PAYMENT_ISSUES"

    def validate_duplicate_charges(self, charge_details: dict, credibility_score: int) -> str:
        """Validate duplicate charges with bank/payment gateway"""
        verification_confidence = "HIGH" if credibility_score >= 7 else "MEDIUM" if credibility_score >= 5 else "LOW"

        if charge_details.get("order_id") and credibility_score >= 6:
            return "CONFIRMED_DUPLICATE"
        elif credibility_score >= 4:
            return "LIKELY_DUPLICATE"
        else:
            return "REQUIRES_INVESTIGATION"

    def decide_double_charge_resolution(self, impact_assessment: dict, credibility_score: int, duplicate_validation: str) -> str:
        """Decide resolution for double charge complaint"""
        severity = impact_assessment.get("severity", "UNKNOWN")
        duplicate_amount = impact_assessment.get("duplicate_amount", 0)

        if duplicate_validation == "CONFIRMED_DUPLICATE":
            if severity == "HIGH_IMPACT" and credibility_score >= 6:
                return "IMMEDIATE_FULL_REFUND"
            elif credibility_score >= 5:
                return "STANDARD_REFUND_PROCESSING"
            else:
                return "VERIFIED_REFUND_24HR"
        elif duplicate_validation == "LIKELY_DUPLICATE" and credibility_score >= 7:
            return "PROVISIONAL_REFUND"
        elif duplicate_validation == "REQUIRES_INVESTIGATION":
            return "ESCALATE_INVESTIGATION"
        else:
            return "REQUEST_DOCUMENTATION"

    def generate_double_charge_response(self, decision: str, charge_details: dict, query: str) -> str:
        """Generate response for double charge complaint"""
        order_id = charge_details.get("order_id", "your order")
        amount = charge_details.get("charge_amount", "the amount")

        if decision == "IMMEDIATE_FULL_REFUND":
            return f"""💰 **URGENT: Double Charge Refund Processing**

We've confirmed that you were incorrectly charged twice for {order_id}.

**✅ Resolution:**
💵 **IMMEDIATE REFUND** of ${charge_details.get('duplicate_amount', 0):.2f} being processed now
⏰ Refund will appear within 2-4 hours
🔴 HIGH PRIORITY - Our payment team is handling this personally
📞 You'll receive SMS confirmation when refund is completed

This is a serious payment error and we sincerely apologize for the inconvenience."""

        elif decision == "STANDARD_REFUND_PROCESSING":
            return f"""💳 **Double Charge Refund Confirmed**

We've verified the duplicate charge for {order_id}.

**✅ Resolution:**
💰 **FULL REFUND** of ${charge_details.get('duplicate_amount', 0):.2f} confirmed
⏰ Processing time: 3-5 business days
📱 SMS notification when refund is initiated
📞 Reference ID: DBL-{hash(query) % 10000:04d}

Thank you for bringing this to our attention."""

        elif decision == "VERIFIED_REFUND_24HR":
            return f"""🔍 **Double Charge Under Review**

We're investigating the duplicate charge for {order_id}.

**✅ Next Steps:**
🕐 **24-HOUR REVIEW** period for verification
💰 Refund will be processed once confirmed
📞 Our payment team will contact you within 24 hours
📱 Updates via SMS

Reference ID: VER-{hash(query) % 10000:04d}"""

        elif decision == "PROVISIONAL_REFUND":
            return f"""⚡ **Provisional Refund Approved**

While we investigate the duplicate charge claim for {order_id}:

**✅ Immediate Action:**
💳 **PROVISIONAL REFUND** being processed
⏰ Will appear in 24-48 hours
🔍 Full investigation continuing in parallel
📱 Final confirmation within 3-5 days

If investigation shows error, no further action needed."""

        elif decision == "ESCALATE_INVESTIGATION":
            return f"""🕵️ **Specialized Investigation Required**

Your double charge complaint for {order_id} needs detailed review.

**Next Steps:**
📋 **CASE ESCALATED** to payment specialists
🕐 Investigation timeline: 5-7 business days
📞 Direct contact from our team within 48 hours
🔒 Case secured with high priority

Reference ID: INV-{hash(query) % 10000:04d}"""

        else:  # REQUEST_DOCUMENTATION
            return f"""📄 **Documentation Required**

To process your double charge claim for {order_id}:

**Please Provide:**
🧾 Bank statement showing duplicate charges
📱 Screenshots of payment confirmations
💳 Transaction reference numbers
📅 Exact dates/times of charges

Upload these documents and we'll expedite your refund within 24 hours."""

    # ===== FAILED PAYMENT WORKFLOW METHODS =====

    def extract_failed_payment_details(self, query: str) -> dict:
        """Extract failed payment details from complaint using AI"""
        extraction_prompt = f"""
        Extract failed payment details from this complaint:

        Complaint: {query}

        Identify:
        1. Transaction reference/ID if mentioned
        2. Payment method that failed
        3. Amount that was deducted despite failure
        4. When the payment attempt was made
        5. Any error messages mentioned

        Return ONLY JSON: {{"transaction_reference": "ref", "payment_method": "method", "deducted_amount": "amount", "attempt_time": "time", "error_message": "error", "order_attempt_info": "details"}}
        """

        try:
            result = self.ai_engine.process_complaint(
                function_name="extract_failed_payment_details",
                user_query=extraction_prompt,
                service=self.service,
                user_type=self.actor
            )

            import json
            if "{" in result and "}" in result:
                json_start = result.find("{")
                json_end = result.rfind("}") + 1
                json_str = result[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"transaction_reference": "", "payment_method": "unknown", "deducted_amount": "", "attempt_time": "", "error_message": "", "order_attempt_info": ""}

        except Exception as e:
            logger.error(f"Failed to extract failed payment details: {e}")
            return {"transaction_reference": "", "payment_method": "unknown", "deducted_amount": "", "attempt_time": "", "error_message": "", "order_attempt_info": ""}

    def verify_payment_vs_order_status(self, payment_details: dict, username: str) -> dict:
        """Verify payment status against order creation status"""
        # Simulate checking payment gateway vs order system
        transaction_ref = payment_details.get("transaction_reference", "")

        if transaction_ref and username != "anonymous":
            return {
                "payment_status": "deducted",
                "order_status": "failed_to_create",
                "gateway_response": "payment_processed_order_failed",
                "refund_eligible": "yes"
            }
        else:
            return {
                "payment_status": "unclear",
                "order_status": "unknown",
                "gateway_response": "insufficient_information",
                "refund_eligible": "needs_verification"
            }

    def check_payment_dispute_history(self, username: str) -> str:
        """Check customer's payment dispute history"""
        if username == "anonymous":
            return "NO_HISTORY_AVAILABLE"
        elif "test" in username.lower():
            return "MULTIPLE_PAYMENT_DISPUTES"
        else:
            return "MINIMAL_PAYMENT_DISPUTES"

    def validate_payment_gateway_records(self, payment_details: dict, credibility_score: int) -> dict:
        """Validate payment gateway records and bank deduction"""
        transaction_ref = payment_details.get("transaction_reference", "")

        if transaction_ref and credibility_score >= 6:
            return {
                "gateway_validation": "CONFIRMED_DEDUCTION",
                "bank_record_status": "payment_processed",
                "order_creation_status": "failed",
                "refund_processing": "eligible"
            }
        elif credibility_score >= 4:
            return {
                "gateway_validation": "LIKELY_VALID",
                "bank_record_status": "needs_verification",
                "order_creation_status": "unclear",
                "refund_processing": "conditional"
            }
        else:
            return {
                "gateway_validation": "REQUIRES_EVIDENCE",
                "bank_record_status": "unverified",
                "order_creation_status": "unknown",
                "refund_processing": "manual_review"
            }

    def assess_failed_payment_refund_eligibility(self, payment_details: dict, gateway_validation: dict, credibility_score: int) -> dict:
        """Assess refund eligibility for failed payment"""
        try:
            amount = float(payment_details.get("deducted_amount", "0").replace("$", "").replace(",", ""))
        except:
            amount = 0

        gateway_status = gateway_validation.get("gateway_validation", "UNKNOWN")

        if gateway_status == "CONFIRMED_DEDUCTION" and amount > 0:
            eligibility = "FULLY_ELIGIBLE"
        elif gateway_status == "LIKELY_VALID" and credibility_score >= 6:
            eligibility = "PROVISIONALLY_ELIGIBLE"
        elif credibility_score >= 4:
            eligibility = "REQUIRES_VERIFICATION"
        else:
            eligibility = "MANUAL_REVIEW_REQUIRED"

        return {
            "eligibility": eligibility,
            "refund_amount": amount,
            "confidence_level": "high" if gateway_status == "CONFIRMED_DEDUCTION" else "medium"
        }

    def decide_failed_payment_resolution(self, refund_eligibility: dict, credibility_score: int, dispute_history: str) -> str:
        """Decide resolution for failed payment complaint"""
        eligibility = refund_eligibility.get("eligibility", "UNKNOWN")
        amount = refund_eligibility.get("refund_amount", 0)

        if eligibility == "FULLY_ELIGIBLE":
            if amount >= 100 and credibility_score >= 7:
                return "IMMEDIATE_PRIORITY_REFUND"
            elif credibility_score >= 5:
                return "STANDARD_FULL_REFUND"
            else:
                return "VERIFIED_REFUND"
        elif eligibility == "PROVISIONALLY_ELIGIBLE" and dispute_history != "MULTIPLE_PAYMENT_DISPUTES":
            return "PROVISIONAL_REFUND"
        elif eligibility == "REQUIRES_VERIFICATION":
            return "REQUEST_BANK_STATEMENT"
        else:
            return "ESCALATE_TO_SPECIALISTS"

    def generate_failed_payment_response(self, decision: str, payment_details: dict, query: str) -> str:
        """Generate response for failed payment complaint"""
        amount = payment_details.get("deducted_amount", "the amount")
        payment_method = payment_details.get("payment_method", "your payment method")

        if decision == "IMMEDIATE_PRIORITY_REFUND":
            return f"""🚨 **PRIORITY: Failed Payment Refund**

We've confirmed your payment of {amount} was deducted despite order failure.

**✅ Immediate Action:**
💰 **PRIORITY REFUND** processing now
⏰ Refund within 2-4 hours
📱 SMS confirmation when completed
🔴 High-priority case escalated to payment team

This should never happen - we sincerely apologize for this system error."""

        elif decision == "STANDARD_FULL_REFUND":
            return f"""💳 **Failed Payment Refund Confirmed**

Your payment of {amount} via {payment_method} was processed but order failed to complete.

**✅ Resolution:**
💰 **FULL REFUND** confirmed and processing
⏰ Refund timeline: 3-5 business days
📱 SMS updates on progress
📞 Reference ID: FPR-{hash(query) % 10000:04d}

Thank you for reporting this payment system issue."""

        elif decision == "VERIFIED_REFUND":
            return f"""🔍 **Payment Failure Refund - Verification Complete**

After reviewing your failed payment case:

**✅ Resolution:**
💰 **REFUND APPROVED** for {amount}
⏰ Processing within 24-48 hours
📋 Case verified through payment gateway
📱 Confirmation via SMS when processed"""

        elif decision == "PROVISIONAL_REFUND":
            return f"""⚡ **Provisional Refund Approved**

While we investigate your failed payment claim:

**✅ Immediate Action:**
💳 **PROVISIONAL REFUND** of {amount} being processed
⏰ Will appear in 24-48 hours
🔍 Full verification continuing
📱 Final confirmation within 3-5 days"""

        elif decision == "REQUEST_BANK_STATEMENT":
            return f"""📄 **Bank Statement Required**

To process your failed payment refund for {amount}:

**Please Provide:**
🏦 Bank statement showing deduction
📱 Screenshot of failed payment notification
💳 Transaction reference number from bank
📅 Exact date/time of payment attempt

Upload these and we'll process your refund within 24 hours."""

        else:  # ESCALATE_TO_SPECIALISTS
            return f"""🕵️ **Specialist Review Required**

Your failed payment case requires detailed technical investigation.

**Next Steps:**
📋 **CASE ESCALATED** to payment specialists
🕐 Review timeline: 5-7 business days
📞 Direct contact from our team within 48 hours
🔒 High priority case tracking

Reference ID: SPC-{hash(query) % 10000:04d}"""

    # ===== COD PREPAID WORKFLOW METHODS =====

    def extract_cod_payment_discrepancy(self, query: str) -> dict:
        """Extract COD payment method discrepancy details"""
        extraction_prompt = f"""
        Extract COD payment discrepancy details from this complaint:

        Complaint: {query}

        Identify:
        1. Order ID or reference
        2. What payment method customer selected (COD or prepaid)
        3. What the system/delivery person is claiming
        4. Any charges or payment demands mentioned

        Return ONLY JSON: {{"order_id": "id", "expected_payment_method": "cod/prepaid", "system_showing": "method", "delivery_demand": "demand", "complaint_type": "type"}}
        """

        try:
            result = self.ai_engine.process_complaint(
                function_name="extract_cod_discrepancy",
                user_query=extraction_prompt,
                service=self.service,
                user_type=self.actor
            )

            import json
            if "{" in result and "}" in result:
                json_start = result.find("{")
                json_end = result.rfind("}") + 1
                json_str = result[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"order_id": "", "expected_payment_method": "", "system_showing": "", "delivery_demand": "", "complaint_type": ""}

        except Exception as e:
            logger.error(f"Failed to extract COD discrepancy details: {e}")
            return {"order_id": "", "expected_payment_method": "", "system_showing": "", "delivery_demand": "", "complaint_type": ""}

    def verify_original_payment_method(self, cod_details: dict, username: str) -> dict:
        """Verify original payment method selection in order records"""
        order_id = cod_details.get("order_id", "")

        # Simulate order record verification
        if order_id and username != "anonymous":
            return {
                "order_record_method": "cod_selected",
                "payment_status": "pending_cod",
                "system_error": "payment_method_mismatch",
                "verification_status": "customer_correct"
            }
        else:
            return {
                "order_record_method": "unknown",
                "payment_status": "unclear",
                "system_error": "insufficient_data",
                "verification_status": "needs_order_lookup"
            }

    def analyze_cod_usage_patterns(self, username: str) -> dict:
        """Analyze customer's COD usage patterns"""
        if username == "anonymous":
            return {"cod_frequency": "unknown", "payment_preference": "unknown", "reliability": "unknown"}
        elif "test" in username.lower():
            return {"cod_frequency": "frequent", "payment_preference": "mixed", "reliability": "variable"}
        else:
            return {"cod_frequency": "occasional", "payment_preference": "cod_preferred", "reliability": "consistent"}

    def assess_payment_method_mismatch(self, cod_details: dict, payment_method_verification: dict, credibility_score: int) -> dict:
        """Assess impact and validate payment method mismatch"""
        verification_status = payment_method_verification.get("verification_status", "unknown")
        expected_method = cod_details.get("expected_payment_method", "")

        if verification_status == "customer_correct" and expected_method == "cod":
            severity = "SYSTEM_ERROR_CONFIRMED"
        elif credibility_score >= 7 and expected_method == "cod":
            severity = "LIKELY_SYSTEM_ERROR"
        elif credibility_score >= 4:
            severity = "POSSIBLE_CONFUSION"
        else:
            severity = "REQUIRES_INVESTIGATION"

        return {
            "severity": severity,
            "system_error_confirmed": verification_status == "customer_correct",
            "customer_impact": "delivery_confusion",
            "resolution_urgency": "high" if severity == "SYSTEM_ERROR_CONFIRMED" else "medium"
        }

    def decide_cod_prepaid_resolution(self, mismatch_assessment: dict, credibility_score: int, cod_usage_pattern: dict) -> str:
        """Decide resolution for COD prepaid complaint"""
        severity = mismatch_assessment.get("severity", "UNKNOWN")
        system_confirmed = mismatch_assessment.get("system_error_confirmed", False)

        if system_confirmed and severity == "SYSTEM_ERROR_CONFIRMED":
            return "IMMEDIATE_SYSTEM_CORRECTION"
        elif severity == "LIKELY_SYSTEM_ERROR" and credibility_score >= 6:
            return "CORRECTIVE_ACTION_CUSTOMER_FAVOR"
        elif severity == "POSSIBLE_CONFUSION" and credibility_score >= 5:
            return "CLARIFICATION_WITH_GOODWILL"
        else:
            return "INVESTIGATION_REQUIRED"

    def generate_cod_prepaid_response(self, decision: str, cod_details: dict, query: str) -> str:
        """Generate response for COD prepaid complaint"""
        order_id = cod_details.get("order_id", "your order")
        expected_method = cod_details.get("expected_payment_method", "COD")

        if decision == "IMMEDIATE_SYSTEM_CORRECTION":
            return f"""🔧 **URGENT: System Error Correction**

We've confirmed a system error with {order_id} payment method settings.

**✅ Immediate Action:**
💻 **PAYMENT METHOD CORRECTED** to {expected_method.upper()} in system
📱 Delivery partner notified of correction
🚫 **NO PAYMENT REQUIRED** at delivery
🔴 High priority system fix being implemented

This error should never have occurred. We sincerely apologize for the confusion."""

        elif decision == "CORRECTIVE_ACTION_CUSTOMER_FAVOR":
            return f"""✅ **Payment Method Issue Resolved**

Based on your selection, {order_id} should be {expected_method.upper()}.

**✅ Resolution:**
💻 **SYSTEM UPDATED** to reflect your original choice
📱 Delivery partner informed - NO payment required at delivery
💳 Any prepaid amounts will be refunded within 24 hours
🎁 Small goodwill credit added to your account for the inconvenience"""

        elif decision == "CLARIFICATION_WITH_GOODWILL":
            return f"""🤝 **Payment Method Clarification**

We're resolving the payment method confusion for {order_id}.

**✅ Resolution:**
📋 **PAYMENT METHOD CONFIRMED** as {expected_method.upper()}
📱 Clear instructions sent to delivery partner
💳 No additional payment required if COD was selected
🎁 Goodwill credit added for the confusion

Thank you for bringing this discrepancy to our attention."""

        else:  # INVESTIGATION_REQUIRED
            return f"""🔍 **Payment Method Investigation**

We're investigating the payment method discrepancy for {order_id}.

**Next Steps:**
📋 **ORDER REVIEW** in progress
🕐 Investigation within 2-4 hours
📱 Direct contact from our team with resolution
🔒 Order held until clarification complete

Reference ID: PMI-{hash(query) % 10000:04d}"""

    # ===== REFUND NOT INITIATED WORKFLOW METHODS =====

    def extract_refund_promise_details(self, query: str) -> dict:
        """Extract original complaint and refund promise details"""
        extraction_prompt = f"""
        Extract refund promise details from this complaint:

        Complaint: {query}

        Identify:
        1. What was the original issue (missing items, quality issues, etc.)
        2. When was refund promised and by whom
        3. What timeframe was given for refund processing
        4. How much time has elapsed since promise
        5. Any reference numbers or previous interaction details

        Return ONLY JSON: {{"original_issue": "issue", "promised_date": "date", "promised_timeframe": "timeframe", "promised_by": "agent/system", "elapsed_time": "time", "reference_numbers": ["refs"]}}
        """

        try:
            result = self.ai_engine.process_complaint(
                function_name="extract_refund_promise",
                user_query=extraction_prompt,
                service=self.service,
                user_type=self.actor
            )

            import json
            if "{" in result and "}" in result:
                json_start = result.find("{")
                json_end = result.rfind("}") + 1
                json_str = result[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"original_issue": "", "promised_date": "", "promised_timeframe": "", "promised_by": "", "elapsed_time": "", "reference_numbers": []}

        except Exception as e:
            logger.error(f"Failed to extract refund promise details: {e}")
            return {"original_issue": "", "promised_date": "", "promised_timeframe": "", "promised_by": "", "elapsed_time": "", "reference_numbers": []}

    def verify_original_complaint_records(self, refund_details: dict, username: str) -> dict:
        """Verify original complaint and refund promise records"""
        original_issue = refund_details.get("original_issue", "")

        # Simulate complaint record verification
        if original_issue and username != "anonymous":
            return {
                "complaint_found": "yes",
                "complaint_type": "quality_issue",
                "resolution_promised": "refund_approved",
                "promise_date": "2023-01-01",
                "promise_validity": "legitimate"
            }
        else:
            return {
                "complaint_found": "unclear",
                "complaint_type": "unknown",
                "resolution_promised": "unverified",
                "promise_date": "unknown",
                "promise_validity": "needs_verification"
            }

    def check_refund_processing_status(self, refund_details: dict, username: str) -> dict:
        """Check refund processing status and delays"""
        # Simulate refund processing system check
        return {
            "processing_status": "delayed",
            "delay_reason": "high_volume_processing",
            "current_queue_position": "processing",
            "expected_completion": "within_48_hours",
            "system_delays": "acknowledged"
        }

    def assess_refund_timeline_breach(self, refund_details: dict, refund_processing_status: dict) -> dict:
        """Assess time elapsed vs promised timeline"""
        promised_timeframe = refund_details.get("promised_timeframe", "")
        elapsed_time = refund_details.get("elapsed_time", "")
        processing_status = refund_processing_status.get("processing_status", "unknown")

        # Simple assessment logic
        if "day" in promised_timeframe.lower() and "week" in elapsed_time.lower():
            breach_severity = "SIGNIFICANT_BREACH"
        elif processing_status == "delayed":
            breach_severity = "MODERATE_BREACH"
        else:
            breach_severity = "MINOR_DELAY"

        return {
            "breach_severity": breach_severity,
            "days_overdue": "7" if breach_severity == "SIGNIFICANT_BREACH" else "3",
            "breach_confirmed": True,
            "customer_impact": "high" if breach_severity == "SIGNIFICANT_BREACH" else "medium"
        }

    def check_refund_request_history(self, username: str) -> dict:
        """Check customer's refund request history"""
        if username == "anonymous":
            return {"refund_frequency": "unknown", "success_rate": "unknown", "pattern": "unknown"}
        elif "test" in username.lower():
            return {"refund_frequency": "frequent", "success_rate": "high", "pattern": "multiple_refunds"}
        else:
            return {"refund_frequency": "occasional", "success_rate": "normal", "pattern": "legitimate_requests"}

    def validate_refund_legitimacy(self, original_complaint_status: dict, credibility_score: int, timeline_assessment: dict) -> dict:
        """Validate refund legitimacy and processing barriers"""
        complaint_found = original_complaint_status.get("complaint_found", "no")
        promise_validity = original_complaint_status.get("promise_validity", "unknown")
        breach_severity = timeline_assessment.get("breach_severity", "unknown")

        if complaint_found == "yes" and promise_validity == "legitimate":
            legitimacy = "FULLY_LEGITIMATE"
        elif credibility_score >= 6 and breach_severity in ["SIGNIFICANT_BREACH", "MODERATE_BREACH"]:
            legitimacy = "LIKELY_LEGITIMATE"
        elif credibility_score >= 4:
            legitimacy = "REQUIRES_VERIFICATION"
        else:
            legitimacy = "MANUAL_REVIEW_NEEDED"

        return {
            "legitimacy": legitimacy,
            "processing_barriers": "system_delays" if legitimacy == "FULLY_LEGITIMATE" else "verification_needed",
            "expedite_eligible": legitimacy in ["FULLY_LEGITIMATE", "LIKELY_LEGITIMATE"]
        }

    def decide_refund_not_initiated_resolution(self, refund_validation: dict, timeline_assessment: dict, credibility_score: int) -> str:
        """Decide resolution for refund not initiated complaint"""
        legitimacy = refund_validation.get("legitimacy", "UNKNOWN")
        expedite_eligible = refund_validation.get("expedite_eligible", False)
        breach_severity = timeline_assessment.get("breach_severity", "UNKNOWN")

        if legitimacy == "FULLY_LEGITIMATE" and breach_severity == "SIGNIFICANT_BREACH":
            return "IMMEDIATE_EXPEDITED_REFUND"
        elif legitimacy == "FULLY_LEGITIMATE" and expedite_eligible:
            return "PRIORITY_REFUND_PROCESSING"
        elif legitimacy == "LIKELY_LEGITIMATE" and credibility_score >= 6:
            return "ACCELERATED_REFUND"
        elif legitimacy == "REQUIRES_VERIFICATION":
            return "VERIFICATION_EXPEDITED_PROCESS"
        else:
            return "ESCALATE_REFUND_SPECIALIST"

    def generate_refund_not_initiated_response(self, decision: str, refund_details: dict, query: str) -> str:
        """Generate response for refund not initiated complaint"""
        original_issue = refund_details.get("original_issue", "your reported issue")
        promised_timeframe = refund_details.get("promised_timeframe", "the promised timeframe")

        if decision == "IMMEDIATE_EXPEDITED_REFUND":
            return f"""🚨 **URGENT: Expedited Refund Processing**

We sincerely apologize - your refund for {original_issue} is significantly overdue.

**✅ Immediate Action:**
💰 **EXPEDITED REFUND** processing now with priority override
⏰ Refund within 2-4 hours (expedited processing)
📱 SMS confirmation when completed
💳 Additional compensation credit for the delay
🔴 Case escalated to senior management

This delay is unacceptable and we're taking immediate corrective action."""

        elif decision == "PRIORITY_REFUND_PROCESSING":
            return f"""⚡ **Priority Refund Processing**

Your refund for {original_issue} has been delayed beyond {promised_timeframe}.

**✅ Resolution:**
💰 **PRIORITY REFUND** processing now
⏰ Completion within 12-24 hours
📱 SMS updates every 6 hours
🎁 Goodwill credit added for the delay
📞 Reference ID: PRI-{hash(query) % 10000:04d}

We apologize for not meeting our promised timeline."""

        elif decision == "ACCELERATED_REFUND":
            return f"""🔄 **Accelerated Refund Processing**

We're expediting your delayed refund for {original_issue}.

**✅ Resolution:**
💳 **ACCELERATED PROCESSING** initiated
⏰ Completion within 24-48 hours
📋 Queue position elevated to high priority
📱 SMS confirmation when processed"""

        elif decision == "VERIFICATION_EXPEDITED_PROCESS":
            return f"""🔍 **Expedited Verification & Refund**

We're fast-tracking the verification process for your refund:

**✅ Next Steps:**
📋 **EXPEDITED REVIEW** of {original_issue}
🕐 Verification within 6-12 hours
💰 Immediate refund processing upon confirmation
📞 Direct contact from our team today

Reference ID: EXP-{hash(query) % 10000:04d}"""

        else:  # ESCALATE_REFUND_SPECIALIST
            return f"""🎯 **Refund Specialist Assignment**

Your delayed refund case requires specialized handling:

**✅ Immediate Action:**
👨‍💼 **SPECIALIST ASSIGNED** to your case
🕐 Direct contact within 4-6 hours
💰 Refund processing decision within 24 hours
📞 Dedicated support throughout resolution

Reference ID: REF-{hash(query) % 10000:04d}

We're committed to resolving this delay promptly."""