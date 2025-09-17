"""
Grab Mart Customer Technical Handler
Uses AI models for intelligent complaint resolution
"""

import logging
import os
import sys
from typing import Optional

# Add parent directory to path to import enhanced_ai_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class TechnicalHandler:
    """Customer-focused technical issues management with real AI"""

    def __init__(self, groq_api_key: str = None):
        self.service = "grab_mart"
        self.actor = "customer"
        self.handler_type = "technical_handler"
        self.ai_engine = EnhancedAgenticAIEngine()

    def handle_auto_cancellation(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle grocery order auto-cancelled without reason with strict 6-step workflow - TEXT ONLY"""
        logger.info(f"Processing auto cancellation complaint: {query[:100]}...")

        # Step 1: Extract cancellation details and timing information
        cancellation_details = self.extract_auto_cancellation_details(query)
        if not cancellation_details["order_id"] and not cancellation_details["cancellation_timeframe"]:
            return "📋 To investigate the auto-cancellation, please provide your order ID and approximately when the cancellation occurred."

        # Step 2: Verify cancellation against system records and policies
        system_verification = self.verify_auto_cancellation_records(cancellation_details, username)
        logger.info(f"System verification: {system_verification}")

        # Step 3: Analyze cancellation reason and system behavior
        cancellation_analysis = self.analyze_grocery_cancellation_cause(cancellation_details, system_verification)
        logger.info(f"Cancellation analysis: {cancellation_analysis}")

        # Step 4: Check customer credibility and cancellation pattern history
        credibility_score = self.get_customer_credibility_score(username)
        cancellation_pattern = self.check_auto_cancellation_history(username)
        logger.info(f"Customer credibility: {credibility_score}/10, Cancellation pattern: {cancellation_pattern}")

        # Step 5: Assess system fault vs policy compliance
        fault_assessment = self.assess_auto_cancellation_fault(cancellation_analysis, credibility_score, system_verification)
        logger.info(f"Fault assessment: {fault_assessment}")

        # Step 6: Make resolution decision and generate response
        decision = self.decide_auto_cancellation_resolution(fault_assessment, credibility_score, cancellation_pattern)
        response = self.generate_auto_cancellation_response(decision, cancellation_details, query)
        logger.info(f"Auto cancellation resolution: {decision}")

        return response

    def handle_delivery_status_error(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle app shows delivered but groceries not received with strict 7-step workflow - TEXT ONLY"""
        logger.info(f"Processing delivery status error complaint: {query[:100]}...")

        # Step 1: Extract delivery status discrepancy details
        status_details = self.extract_delivery_status_discrepancy(query)
        if not status_details["order_id"] or not status_details["app_status"]:
            return "📋 To investigate the delivery status error, please provide your order ID and confirm what status the app is showing."

        # Step 2: Cross-verify delivery records across multiple systems
        delivery_verification = self.verify_grocery_delivery_across_systems(status_details, username)
        logger.info(f"Delivery verification: {delivery_verification}")

        # Step 3: Check GPS tracking and delivery partner confirmation
        tracking_analysis = self.analyze_grocery_delivery_tracking_data(status_details, delivery_verification)
        logger.info(f"Tracking analysis: {tracking_analysis}")

        # Step 4: Assess customer location and delivery logistics
        location_assessment = self.assess_grocery_delivery_location_factors(status_details, username)
        logger.info(f"Location assessment: {location_assessment}")

        # Step 5: Check customer credibility and delivery dispute history
        credibility_score = self.get_customer_credibility_score(username)
        delivery_dispute_history = self.check_delivery_dispute_patterns(username)
        logger.info(f"Customer credibility: {credibility_score}/10, Dispute history: {delivery_dispute_history}")

        # Step 6: Validate delivery status error legitimacy
        error_validation = self.validate_delivery_status_error(tracking_analysis, location_assessment, credibility_score)
        logger.info(f"Error validation: {error_validation}")

        # Step 7: Make resolution decision and generate response
        decision = self.decide_delivery_status_resolution(error_validation, credibility_score, delivery_dispute_history)
        response = self.generate_grocery_delivery_status_response(decision, status_details, query)
        logger.info(f"Delivery status resolution: {decision}")

        return response

    def handle_tracking_status_error(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle wrong grocery tracking status with strict 5-step workflow - TEXT ONLY"""
        logger.info(f"Processing tracking status error complaint: {query[:100]}...")

        # Step 1: Extract tracking status discrepancy information
        tracking_details = self.extract_tracking_status_discrepancy(query)
        if not tracking_details["order_id"] or not tracking_details["reported_vs_actual_status"]:
            return "📋 To investigate the tracking status error, please provide your order ID and describe what status you're seeing vs. the actual situation."

        # Step 2: Validate tracking system synchronization
        tracking_sync_status = self.validate_grocery_tracking_system_sync(tracking_details, username)
        logger.info(f"Tracking sync status: {tracking_sync_status}")

        # Step 3: Check customer credibility and tracking complaint history
        credibility_score = self.get_customer_credibility_score(username)
        tracking_complaint_pattern = self.check_tracking_complaint_history(username)
        logger.info(f"Customer credibility: {credibility_score}/10, Tracking complaints: {tracking_complaint_pattern}")

        # Step 4: Assess tracking system error vs customer expectation mismatch
        error_assessment = self.assess_grocery_tracking_error_legitimacy(tracking_details, tracking_sync_status, credibility_score)
        logger.info(f"Error assessment: {error_assessment}")

        # Step 5: Make resolution decision and generate response
        decision = self.decide_tracking_status_resolution(error_assessment, credibility_score, tracking_complaint_pattern)
        response = self.generate_grocery_tracking_status_response(decision, tracking_details, query)
        logger.info(f"Tracking status resolution: {decision}")

        return response

    def handle_coupon_offers_error(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle grocery coupons/offers not applied correctly with strict 6-step workflow - TEXT ONLY"""
        logger.info(f"Processing coupon offers error complaint: {query[:100]}...")

        # Step 1: Extract coupon/offer details and application failure information
        coupon_details = self.extract_coupon_application_details(query)
        if not coupon_details["coupon_code"] and not coupon_details["offer_description"]:
            return "📋 To investigate the coupon/offer issue, please provide the coupon code or describe the specific offer that wasn't applied correctly."

        # Step 2: Verify coupon validity and terms & conditions
        coupon_validation = self.verify_grocery_coupon_validity_and_terms(coupon_details, username)
        logger.info(f"Coupon validation: {coupon_validation}")

        # Step 3: Check order eligibility against coupon requirements
        eligibility_check = self.check_grocery_order_coupon_eligibility(coupon_details, username)
        logger.info(f"Eligibility check: {eligibility_check}")

        # Step 4: Assess customer credibility and coupon usage patterns
        credibility_score = self.get_customer_credibility_score(username)
        coupon_usage_pattern = self.analyze_grocery_coupon_usage_patterns(username)
        logger.info(f"Customer credibility: {credibility_score}/10, Coupon patterns: {coupon_usage_pattern}")

        # Step 5: Validate coupon application error legitimacy
        application_error_validation = self.validate_coupon_application_error(coupon_validation, eligibility_check, credibility_score)
        logger.info(f"Application error validation: {application_error_validation}")

        # Step 6: Make resolution decision and generate response
        decision = self.decide_coupon_offers_resolution(application_error_validation, credibility_score, coupon_usage_pattern)
        response = self.generate_grocery_coupon_offers_response(decision, coupon_details, query)
        logger.info(f"Coupon offers resolution: {decision}")

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

            # Get user's grocery order history from the new database schema
            cursor.execute('''
                SELECT
                    COUNT(*) as total_orders,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_orders,
                    COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_orders,
                    AVG(price) as avg_order_value,
                    MIN(date) as first_order_date,
                    MAX(date) as last_order_date
                FROM orders
                WHERE username = ? AND service = 'grab_mart' AND user_type = 'customer'
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

                    # Adjust based on average order value (grocery orders typically higher value)
                    if avg_order_value and avg_order_value >= 80:
                        base_score += 1
                    elif avg_order_value and avg_order_value >= 50:
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
                WHERE username = ? AND service = 'grab_mart'
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

    # ===== AUTO CANCELLATION WORKFLOW METHODS =====

    def extract_auto_cancellation_details(self, query: str) -> dict:
        """Extract auto-cancellation details from complaint using AI"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="extract_auto_cancellation_details",
                user_query=f"Extract grocery order auto-cancellation details from: {query}",
                service=self.service,
                user_type=self.actor
            )

            # Parse AI response for structured data
            import json
            if "{" in result and "}" in result:
                json_start = result.find("{")
                json_end = result.rfind("}") + 1
                json_str = result[json_start:json_end]
                try:
                    return json.loads(json_str)
                except:
                    pass

            # Fallback extraction
            return {
                "order_id": "grocery_order" if "order" in query.lower() else "",
                "cancellation_timeframe": "after ordering" if "after" in query.lower() else "",
                "system_reason": "",
                "customer_expectation": "delivery",
                "error_messages": []
            }

        except Exception as e:
            logger.error(f"Failed to extract auto-cancellation details: {e}")
            return {"order_id": "", "cancellation_timeframe": "", "system_reason": "", "customer_expectation": "", "error_messages": []}

    def verify_auto_cancellation_records(self, cancellation_details: dict, username: str) -> dict:
        """Verify auto-cancellation against system records"""
        order_id = cancellation_details.get("order_id", "")

        # Simulate system record verification for grocery orders
        if order_id and username != "anonymous":
            return {
                "cancellation_found": "yes",
                "cancellation_reason": "store_inventory_unavailable",
                "system_policy_compliant": "yes",
                "notification_sent": "yes",
                "refund_initiated": "pending"
            }
        else:
            return {
                "cancellation_found": "unclear",
                "cancellation_reason": "unknown",
                "system_policy_compliant": "needs_verification",
                "notification_sent": "unknown",
                "refund_initiated": "unknown"
            }

    def analyze_grocery_cancellation_cause(self, cancellation_details: dict, system_verification: dict) -> dict:
        """Analyze the root cause of grocery order auto-cancellation"""
        system_reason = system_verification.get("cancellation_reason", "unknown")
        policy_compliant = system_verification.get("system_policy_compliant", "unknown")

        if system_reason == "store_inventory_unavailable" and policy_compliant == "yes":
            cause_category = "LEGITIMATE_INVENTORY_ISSUE"
        elif system_reason == "payment_failure":
            cause_category = "PAYMENT_RELATED"
        elif system_reason == "delivery_slot_unavailable":
            cause_category = "LOGISTICS_ISSUE"
        elif policy_compliant == "no":
            cause_category = "SYSTEM_ERROR"
        else:
            cause_category = "UNCLEAR_CAUSE"

        return {
            "cause_category": cause_category,
            "system_fault": policy_compliant == "no",
            "customer_impact": "grocery_order_disruption",
            "resolution_required": cause_category in ["SYSTEM_ERROR", "UNCLEAR_CAUSE"]
        }

    def check_auto_cancellation_history(self, username: str) -> str:
        """Check customer's history of auto-cancellation complaints"""
        if username == "anonymous":
            return "NO_HISTORY_AVAILABLE"
        elif "test" in username.lower():
            return "FREQUENT_CANCELLATION_ISSUES"
        else:
            return "OCCASIONAL_CANCELLATIONS"

    def assess_auto_cancellation_fault(self, cancellation_analysis: dict, credibility_score: int, system_verification: dict) -> dict:
        """Assess fault and system error in auto-cancellation"""
        cause_category = cancellation_analysis.get("cause_category", "UNCLEAR")
        system_fault = cancellation_analysis.get("system_fault", False)
        notification_sent = system_verification.get("notification_sent", "unknown")

        if system_fault:
            fault_level = "SYSTEM_ERROR_CONFIRMED"
        elif cause_category == "LEGITIMATE_INVENTORY_ISSUE" and notification_sent == "yes":
            fault_level = "NO_SYSTEM_FAULT"
        elif cause_category == "LEGITIMATE_INVENTORY_ISSUE" and notification_sent != "yes":
            fault_level = "NOTIFICATION_FAULT"
        else:
            fault_level = "UNCLEAR_FAULT"

        return {
            "fault_level": fault_level,
            "compensation_warranted": fault_level in ["SYSTEM_ERROR_CONFIRMED", "NOTIFICATION_FAULT"],
            "apology_required": fault_level != "NO_SYSTEM_FAULT",
            "system_improvement_needed": system_fault
        }

    def decide_auto_cancellation_resolution(self, fault_assessment: dict, credibility_score: int, cancellation_pattern: str) -> str:
        """Decide resolution for auto-cancellation complaint"""
        fault_level = fault_assessment.get("fault_level", "UNCLEAR")
        compensation_warranted = fault_assessment.get("compensation_warranted", False)

        if fault_level == "SYSTEM_ERROR_CONFIRMED":
            return "FULL_COMPENSATION_PLUS_CREDIT"
        elif fault_level == "NOTIFICATION_FAULT" and credibility_score >= 6:
            return "GOODWILL_COMPENSATION"
        elif fault_level == "NO_SYSTEM_FAULT" and credibility_score >= 7:
            return "EXPLANATION_WITH_SMALL_CREDIT"
        elif cancellation_pattern == "FREQUENT_CANCELLATION_ISSUES":
            return "ESCALATE_FOR_PATTERN_REVIEW"
        else:
            return "STANDARD_EXPLANATION"

    def generate_auto_cancellation_response(self, decision: str, cancellation_details: dict, query: str) -> str:
        """Generate response for auto-cancellation complaint"""
        order_id = cancellation_details.get("order_id", "your grocery order")
        timeframe = cancellation_details.get("cancellation_timeframe", "shortly after ordering")

        if decision == "FULL_COMPENSATION_PLUS_CREDIT":
            return f"""🚨 **SYSTEM ERROR: Full Compensation**

We've identified a system error that caused {order_id} to be cancelled improperly.

**✅ Resolution:**
💰 **FULL REFUND** processing immediately
🎁 **ADDITIONAL CREDIT** of 20% for the system error
⚡ **PRIORITY DELIVERY SLOT** for your next grocery order
🔧 System issue being escalated to technical team

This should never have happened. We sincerely apologize for the system malfunction."""

        elif decision == "GOODWILL_COMPENSATION":
            return f"""🤝 **Notification Issue - Goodwill Compensation**

Your grocery order {order_id} was cancelled {timeframe} due to store inventory unavailability, but we failed to notify you properly.

**✅ Resolution:**
💰 **FULL REFUND** confirmed
🎁 **GOODWILL CREDIT** for poor communication
📱 SMS notification system being improved
📞 Reference ID: ATC-{hash(query) % 10000:04d}

We apologize for not keeping you informed during the cancellation process."""

        elif decision == "EXPLANATION_WITH_SMALL_CREDIT":
            return f"""📋 **Auto-Cancellation Explanation**

Your grocery order {order_id} was automatically cancelled {timeframe} due to store inventory unavailability.

**✅ What Happened:**
🏪 Store became unable to fulfill your order after acceptance
💰 **FULL REFUND** processed automatically
🎁 Small goodwill credit added for the inconvenience
📱 Cancellation notification sent (please check SMS/email)

This is our standard policy to ensure you don't wait for unavailable groceries."""

        elif decision == "ESCALATE_FOR_PATTERN_REVIEW":
            return f"""🔍 **Pattern Review Required**

We notice you've experienced multiple auto-cancellations. This requires specialized review.

**Next Steps:**
👨‍💼 **CASE ESCALATED** to customer experience team
📊 Full pattern analysis being conducted
📞 Direct contact within 24 hours with findings
🎯 Personalized solution to prevent future issues

Reference ID: PAT-{hash(query) % 10000:04d}"""

        else:  # STANDARD_EXPLANATION
            return f"""📱 **Auto-Cancellation Information**

Your grocery order {order_id} was cancelled {timeframe} following our automatic policies.

**Standard Process:**
💰 **FULL REFUND** processed (if payment was taken)
📱 Notification sent to registered contact details
🔄 You can place a new grocery order immediately
📞 Contact support if refund doesn't appear within 3-5 business days

Auto-cancellations help ensure you don't wait unnecessarily for unavailable groceries."""

    # ===== DELIVERY STATUS ERROR WORKFLOW METHODS =====

    def extract_delivery_status_discrepancy(self, query: str) -> dict:
        """Extract delivery status error details from complaint"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="extract_delivery_status_discrepancy",
                user_query=f"Extract grocery delivery status discrepancy details from: {query}",
                service=self.service,
                user_type=self.actor
            )

            # Parse AI response for structured data
            import json
            if "{" in result and "}" in result:
                json_start = result.find("{")
                json_end = result.rfind("}") + 1
                json_str = result[json_start:json_end]
                try:
                    return json.loads(json_str)
                except:
                    pass

            # Fallback extraction
            return {
                "order_id": "grocery_order" if "order" in query.lower() else "",
                "app_status": "delivered" if "delivered" in query.lower() else "",
                "actual_situation": "not received",
                "discrepancy_noticed": "today",
                "partner_interaction": ""
            }

        except Exception as e:
            logger.error(f"Failed to extract delivery status discrepancy: {e}")
            return {"order_id": "", "app_status": "", "actual_situation": "", "discrepancy_noticed": "", "partner_interaction": ""}

    def verify_grocery_delivery_across_systems(self, status_details: dict, username: str) -> dict:
        """Verify grocery delivery status across multiple systems"""
        order_id = status_details.get("order_id", "")

        # Simulate cross-system verification for grocery delivery
        if order_id and username != "anonymous":
            return {
                "app_system_status": "delivered",
                "partner_system_status": "delivered",
                "gps_confirmation": "location_match",
                "photo_proof": "uploaded",
                "customer_confirmation": "not_received",
                "delivery_window": "within_scheduled_time"
            }
        else:
            return {
                "app_system_status": "unknown",
                "partner_system_status": "unknown",
                "gps_confirmation": "unavailable",
                "photo_proof": "unavailable",
                "customer_confirmation": "unknown",
                "delivery_window": "unknown"
            }

    def analyze_grocery_delivery_tracking_data(self, status_details: dict, delivery_verification: dict) -> dict:
        """Analyze grocery delivery tracking and GPS data"""
        gps_confirmation = delivery_verification.get("gps_confirmation", "unavailable")
        photo_proof = delivery_verification.get("photo_proof", "unavailable")
        delivery_window = delivery_verification.get("delivery_window", "unknown")

        if gps_confirmation == "location_match" and photo_proof == "uploaded" and delivery_window == "within_scheduled_time":
            tracking_confidence = "HIGH_CONFIDENCE_DELIVERED"
        elif gps_confirmation == "location_match" and photo_proof == "uploaded":
            tracking_confidence = "LIKELY_DELIVERED"
        elif photo_proof == "uploaded":
            tracking_confidence = "PHOTO_EVIDENCE_DELIVERED"
        else:
            tracking_confidence = "INSUFFICIENT_TRACKING_DATA"

        return {
            "tracking_confidence": tracking_confidence,
            "evidence_strength": "strong" if tracking_confidence == "HIGH_CONFIDENCE_DELIVERED" else "moderate",
            "gps_accuracy": gps_confirmation,
            "delivery_proof": photo_proof,
            "timing_compliance": delivery_window
        }

    def assess_grocery_delivery_location_factors(self, status_details: dict, username: str) -> dict:
        """Assess grocery delivery location and accessibility factors"""
        # Simulate location assessment for grocery delivery
        return {
            "address_accuracy": "verified",
            "delivery_accessibility": "normal",
            "building_type": "residential",
            "delivery_instructions": "available",
            "location_challenges": "none_reported",
            "grocery_specific_requirements": "refrigeration_noted"
        }

    def check_delivery_dispute_patterns(self, username: str) -> str:
        """Check customer's delivery dispute pattern history"""
        if username == "anonymous":
            return "NO_HISTORY_AVAILABLE"
        elif "test" in username.lower():
            return "FREQUENT_DELIVERY_DISPUTES"
        else:
            return "OCCASIONAL_DELIVERY_ISSUES"

    def validate_delivery_status_error(self, tracking_analysis: dict, location_assessment: dict, credibility_score: int) -> dict:
        """Validate delivery status error legitimacy"""
        tracking_confidence = tracking_analysis.get("tracking_confidence", "UNKNOWN")
        evidence_strength = tracking_analysis.get("evidence_strength", "weak")

        if tracking_confidence == "HIGH_CONFIDENCE_DELIVERED" and credibility_score <= 4:
            validation = "LIKELY_FALSE_CLAIM"
        elif tracking_confidence == "INSUFFICIENT_TRACKING_DATA" and credibility_score >= 7:
            validation = "LIKELY_LEGITIMATE_COMPLAINT"
        elif evidence_strength == "strong" and credibility_score >= 6:
            validation = "DELIVERY_PROOF_VS_CUSTOMER_CLAIM"
        else:
            validation = "REQUIRES_INVESTIGATION"

        return {
            "validation": validation,
            "investigation_needed": validation == "REQUIRES_INVESTIGATION",
            "evidence_conflicts": tracking_confidence == "HIGH_CONFIDENCE_DELIVERED",
            "customer_benefit_of_doubt": credibility_score >= 7
        }

    def decide_delivery_status_resolution(self, error_validation: dict, credibility_score: int, delivery_dispute_history: str) -> str:
        """Decide resolution for delivery status error"""
        validation = error_validation.get("validation", "UNKNOWN")
        evidence_conflicts = error_validation.get("evidence_conflicts", False)

        if validation == "LIKELY_LEGITIMATE_COMPLAINT":
            return "FULL_REDELIVERY_OR_REFUND"
        elif validation == "DELIVERY_PROOF_VS_CUSTOMER_CLAIM" and credibility_score >= 7:
            return "INVESTIGATE_WITH_PARTNER"
        elif validation == "LIKELY_FALSE_CLAIM":
            return "PRESENT_DELIVERY_EVIDENCE"
        elif delivery_dispute_history == "FREQUENT_DELIVERY_DISPUTES":
            return "ESCALATE_PATTERN_INVESTIGATION"
        else:
            return "DETAILED_INVESTIGATION_REQUIRED"

    def generate_grocery_delivery_status_response(self, decision: str, status_details: dict, query: str) -> str:
        """Generate response for grocery delivery status error"""
        order_id = status_details.get("order_id", "your grocery order")
        app_status = status_details.get("app_status", "delivered")

        if decision == "FULL_REDELIVERY_OR_REFUND":
            return f"""🚚 **Grocery Delivery Issue Confirmed - Immediate Resolution**

We understand your grocery order {order_id} shows as {app_status} but you haven't received it.

**✅ Immediate Resolution:**
🔄 **REDELIVERY** scheduled within 2 hours OR
💰 **FULL REFUND** if you prefer
📞 Direct contact with delivery partner
🎁 Goodwill credit for the inconvenience

Please choose your preferred resolution and we'll process it immediately."""

        elif decision == "INVESTIGATE_WITH_PARTNER":
            return f"""🔍 **Partner Investigation - Delivery Verification**

Your grocery order {order_id} shows conflicting delivery status. We're investigating immediately.

**✅ Investigation Process:**
📞 **CONTACTING DELIVERY PARTNER** now for clarification
🗺️ GPS and photo evidence being reviewed
⏰ Resolution within 2-4 hours
📱 SMS updates on progress

If not delivered, we'll arrange immediate redelivery or full refund."""

        elif decision == "PRESENT_DELIVERY_EVIDENCE":
            return f"""📋 **Delivery Evidence Review**

Our records show {order_id} was delivered with the following evidence:

**📊 Delivery Confirmation:**
🗺️ GPS location matched your delivery address
📷 Photo proof uploaded by delivery partner
⏰ Delivered within scheduled time window

If you believe this is incorrect, please provide:
- Details about who might have received the groceries
- Any building/location access issues
- Preferred resolution (investigation/redelivery)"""

        elif decision == "ESCALATE_PATTERN_INVESTIGATION":
            return f"""⚠️ **Pattern Investigation Required**

We notice multiple delivery disputes on your account requiring specialized review.

**Next Steps:**
👨‍💼 **SENIOR SPECIALIST** assigned to your case
📊 Comprehensive delivery pattern analysis
📞 Direct contact within 6 hours
🎯 Customized delivery solution development

Reference ID: DEL-{hash(query) % 10000:04d}"""

        else:  # DETAILED_INVESTIGATION_REQUIRED
            return f"""🔍 **Detailed Investigation Initiated**

Your delivery status discrepancy for {order_id} requires thorough investigation.

**Investigation Timeline:**
📋 **CASE REVIEW** begins immediately
🕐 Investigation completion: 12-24 hours
📞 Direct contact with findings
💰 Appropriate resolution guaranteed

Reference ID: INV-{hash(query) % 10000:04d}

We'll resolve this thoroughly and fairly."""

    # ===== TRACKING STATUS ERROR WORKFLOW METHODS =====

    def extract_tracking_status_discrepancy(self, query: str) -> dict:
        """Extract tracking status error details from complaint"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="extract_tracking_status_discrepancy",
                user_query=f"Extract grocery tracking status discrepancy details from: {query}",
                service=self.service,
                user_type=self.actor
            )

            # Parse AI response for structured data
            import json
            if "{" in result and "}" in result:
                json_start = result.find("{")
                json_end = result.rfind("}") + 1
                json_str = result[json_start:json_end]
                try:
                    return json.loads(json_str)
                except:
                    pass

            # Fallback extraction
            return {
                "order_id": "grocery_order" if "order" in query.lower() else "",
                "incorrect_status": "wrong status",
                "expected_status": "correct status",
                "reported_vs_actual_status": query[:100],
                "timeline": "today",
                "tracking_stages": ["order_placed", "preparing", "out_for_delivery"]
            }

        except Exception as e:
            logger.error(f"Failed to extract tracking status discrepancy: {e}")
            return {"order_id": "", "incorrect_status": "", "expected_status": "", "reported_vs_actual_status": "", "timeline": "", "tracking_stages": []}

    def validate_grocery_tracking_system_sync(self, tracking_details: dict, username: str) -> dict:
        """Validate grocery tracking system synchronization"""
        order_id = tracking_details.get("order_id", "")

        # Simulate tracking system validation for grocery orders
        if order_id and username != "anonymous":
            return {
                "system_sync_status": "synced",
                "last_update_time": "2 minutes ago",
                "tracking_accuracy": "accurate",
                "system_delays": "none",
                "partner_system_alignment": "aligned",
                "grocery_tracking_stages": "properly_configured"
            }
        else:
            return {
                "system_sync_status": "unknown",
                "last_update_time": "unavailable",
                "tracking_accuracy": "unclear",
                "system_delays": "unknown",
                "partner_system_alignment": "unknown",
                "grocery_tracking_stages": "unknown"
            }

    def check_tracking_complaint_history(self, username: str) -> str:
        """Check customer's tracking complaint history"""
        if username == "anonymous":
            return "NO_HISTORY_AVAILABLE"
        elif "test" in username.lower():
            return "FREQUENT_TRACKING_COMPLAINTS"
        else:
            return "MINIMAL_TRACKING_ISSUES"

    def assess_grocery_tracking_error_legitimacy(self, tracking_details: dict, tracking_sync_status: dict, credibility_score: int) -> dict:
        """Assess grocery tracking error legitimacy"""
        system_sync = tracking_sync_status.get("system_sync_status", "unknown")
        tracking_accuracy = tracking_sync_status.get("tracking_accuracy", "unknown")

        if system_sync == "synced" and tracking_accuracy == "accurate" and credibility_score <= 4:
            legitimacy = "LIKELY_CUSTOMER_MISUNDERSTANDING"
        elif system_sync != "synced" and credibility_score >= 6:
            legitimacy = "LIKELY_SYSTEM_ERROR"
        elif tracking_accuracy != "accurate":
            legitimacy = "CONFIRMED_TRACKING_ERROR"
        else:
            legitimacy = "REQUIRES_CLARIFICATION"

        return {
            "legitimacy": legitimacy,
            "system_error_confirmed": legitimacy == "CONFIRMED_TRACKING_ERROR",
            "customer_education_needed": legitimacy == "LIKELY_CUSTOMER_MISUNDERSTANDING",
            "technical_fix_required": system_sync != "synced"
        }

    def decide_tracking_status_resolution(self, error_assessment: dict, credibility_score: int, tracking_complaint_pattern: str) -> str:
        """Decide resolution for tracking status error"""
        legitimacy = error_assessment.get("legitimacy", "UNKNOWN")
        system_error_confirmed = error_assessment.get("system_error_confirmed", False)

        if system_error_confirmed:
            return "FIX_TRACKING_WITH_CREDIT"
        elif legitimacy == "LIKELY_SYSTEM_ERROR":
            return "INVESTIGATE_AND_CORRECT"
        elif legitimacy == "LIKELY_CUSTOMER_MISUNDERSTANDING" and credibility_score >= 6:
            return "EXPLAIN_WITH_GOODWILL"
        elif tracking_complaint_pattern == "FREQUENT_TRACKING_COMPLAINTS":
            return "ESCALATE_FREQUENT_COMPLAINTS"
        else:
            return "STANDARD_TRACKING_EXPLANATION"

    def generate_grocery_tracking_status_response(self, decision: str, tracking_details: dict, query: str) -> str:
        """Generate response for grocery tracking status error"""
        order_id = tracking_details.get("order_id", "your grocery order")
        incorrect_status = tracking_details.get("incorrect_status", "the incorrect status")

        if decision == "FIX_TRACKING_WITH_CREDIT":
            return f"""🔧 **Tracking System Error - Fixed + Compensation**

We've identified and fixed the tracking error for {order_id} showing {incorrect_status}.

**✅ Resolution:**
📱 **TRACKING CORRECTED** - refresh your app
🎁 **GOODWILL CREDIT** for the confusion
⚡ Real-time tracking now functioning properly
📞 Reference ID: TRK-{hash(query) % 10000:04d}

Thank you for reporting this system error."""

        elif decision == "INVESTIGATE_AND_CORRECT":
            return f"""🔍 **Tracking Investigation & Correction**

We're investigating the tracking status issue for {order_id}.

**✅ Immediate Actions:**
🔄 **SYSTEM REFRESH** initiated
📊 Tracking data being synchronized
⏰ Correction within 15-30 minutes
📱 App notification when tracking is accurate

Please check your tracking in 30 minutes for updated status."""

        elif decision == "EXPLAIN_WITH_GOODWILL":
            return f"""📚 **Tracking Status Clarification**

Let me explain the tracking status for {order_id}:

**📱 Tracking Information:**
✅ Current status is accurate based on our systems
🕐 Updates occur at key milestones (store preparation, pickup, delivery)
📍 Status changes when delivery partner confirms each stage
🎁 Small goodwill credit added for the confusion

Tracking will update to "Out for Delivery" when your groceries are picked up."""

        elif decision == "ESCALATE_FREQUENT_COMPLAINTS":
            return f"""📈 **Tracking Experience Review Required**

We notice multiple tracking concerns and want to improve your experience.

**Next Steps:**
👨‍💼 **TRACKING SPECIALIST** assigned to review your case
📊 Account-specific tracking analysis
📞 Direct contact within 12 hours
🎯 Personalized tracking solution

Reference ID: TRK-{hash(query) % 10000:04d}"""

        else:  # STANDARD_TRACKING_EXPLANATION
            return f"""📱 **Tracking Status Information**

Regarding the tracking status for {order_id}:

**How Grocery Tracking Works:**
📍 Updates at major milestones only (store prep, pickup, delivery)
🕐 Real-time updates not always available
✅ Status shown reflects last confirmed checkpoint
🔄 Refresh app if status seems outdated

If tracking doesn't update within expected timeframes, please contact us again."""

    # ===== COUPON OFFERS ERROR WORKFLOW METHODS =====

    def extract_coupon_application_details(self, query: str) -> dict:
        """Extract coupon/offer application failure details"""
        try:
            result = self.ai_engine.process_complaint(
                function_name="extract_coupon_application_details",
                user_query=f"Extract grocery coupon application error details from: {query}",
                service=self.service,
                user_type=self.actor
            )

            # Parse AI response for structured data
            import json
            if "{" in result and "}" in result:
                json_start = result.find("{")
                json_end = result.rfind("}") + 1
                json_str = result[json_start:json_end]
                try:
                    return json.loads(json_str)
                except:
                    pass

            # Fallback extraction
            return {
                "coupon_code": "",
                "offer_description": "grocery discount" if "discount" in query.lower() else "",
                "expected_benefit": "discount",
                "actual_result": "not applied",
                "order_amount": "",
                "expected_discount": "",
                "error_messages": []
            }

        except Exception as e:
            logger.error(f"Failed to extract coupon application details: {e}")
            return {"coupon_code": "", "offer_description": "", "expected_benefit": "", "actual_result": "", "order_amount": "", "expected_discount": "", "error_messages": []}

    def verify_grocery_coupon_validity_and_terms(self, coupon_details: dict, username: str) -> dict:
        """Verify grocery coupon validity and terms & conditions"""
        coupon_code = coupon_details.get("coupon_code", "")

        # Simulate coupon validation for grocery orders
        if coupon_code and username != "anonymous":
            return {
                "coupon_validity": "valid",
                "expiry_status": "not_expired",
                "usage_limit_reached": "no",
                "terms_compliance": "eligible",
                "minimum_order_met": "yes",
                "grocery_category_eligible": "yes"
            }
        else:
            return {
                "coupon_validity": "unknown",
                "expiry_status": "unknown",
                "usage_limit_reached": "unknown",
                "terms_compliance": "unknown",
                "minimum_order_met": "unknown",
                "grocery_category_eligible": "unknown"
            }

    def check_grocery_order_coupon_eligibility(self, coupon_details: dict, username: str) -> dict:
        """Check grocery order eligibility against coupon requirements"""
        order_amount = coupon_details.get("order_amount", "0")

        # Simulate order eligibility check for grocery orders
        try:
            amount = float(order_amount.replace("$", "").replace(",", ""))
            minimum_met = amount >= 40  # Higher minimum for grocery orders
        except:
            amount = 0
            minimum_met = False

        return {
            "minimum_order_requirement": "40",
            "order_amount": amount,
            "minimum_requirement_met": minimum_met,
            "store_eligible": "yes",
            "user_category_eligible": "yes",
            "grocery_categories_included": "all_categories"
        }

    def analyze_grocery_coupon_usage_patterns(self, username: str) -> dict:
        """Analyze customer's grocery coupon usage patterns"""
        if username == "anonymous":
            return {"usage_frequency": "unknown", "success_rate": "unknown", "complaint_pattern": "unknown"}
        elif "test" in username.lower():
            return {"usage_frequency": "frequent", "success_rate": "variable", "complaint_pattern": "frequent_complaints"}
        else:
            return {"usage_frequency": "occasional", "success_rate": "normal", "complaint_pattern": "rare_complaints"}

    def validate_coupon_application_error(self, coupon_validation: dict, eligibility_check: dict, credibility_score: int) -> dict:
        """Validate coupon application error legitimacy"""
        coupon_validity = coupon_validation.get("coupon_validity", "unknown")
        minimum_met = eligibility_check.get("minimum_requirement_met", False)
        terms_compliance = coupon_validation.get("terms_compliance", "unknown")

        if coupon_validity == "valid" and minimum_met and terms_compliance == "eligible":
            if credibility_score >= 6:
                validation = "LEGITIMATE_APPLICATION_ERROR"
            else:
                validation = "LIKELY_USER_ERROR"
        elif not minimum_met:
            validation = "MINIMUM_ORDER_NOT_MET"
        elif coupon_validity != "valid":
            validation = "INVALID_COUPON"
        else:
            validation = "TERMS_NOT_MET"

        return {
            "validation": validation,
            "system_error": validation == "LEGITIMATE_APPLICATION_ERROR",
            "user_education_needed": validation in ["MINIMUM_ORDER_NOT_MET", "TERMS_NOT_MET"],
            "compensation_warranted": validation == "LEGITIMATE_APPLICATION_ERROR"
        }

    def decide_coupon_offers_resolution(self, application_error_validation: dict, credibility_score: int, coupon_usage_pattern: dict) -> str:
        """Decide resolution for coupon/offers error"""
        validation = application_error_validation.get("validation", "UNKNOWN")
        system_error = application_error_validation.get("system_error", False)
        complaint_pattern = coupon_usage_pattern.get("complaint_pattern", "unknown")

        if system_error:
            return "APPLY_COUPON_WITH_COMPENSATION"
        elif validation == "MINIMUM_ORDER_NOT_MET" and credibility_score >= 7:
            return "EXPLAIN_WITH_ALTERNATIVE_OFFER"
        elif validation == "INVALID_COUPON":
            return "EXPLAIN_COUPON_STATUS"
        elif complaint_pattern == "frequent_complaints":
            return "ESCALATE_COUPON_ABUSE_REVIEW"
        else:
            return "STANDARD_COUPON_EXPLANATION"

    def generate_grocery_coupon_offers_response(self, decision: str, coupon_details: dict, query: str) -> str:
        """Generate response for grocery coupon/offers error"""
        coupon_code = coupon_details.get("coupon_code", "your coupon")
        expected_benefit = coupon_details.get("expected_benefit", "the discount")

        if decision == "APPLY_COUPON_WITH_COMPENSATION":
            return f"""🎁 **Coupon Error - Applied + Compensation**

We've identified a system error with coupon {coupon_code} not applying correctly to your grocery order.

**✅ Resolution:**
💰 **COUPON DISCOUNT APPLIED** retroactively to your order
🎁 **ADDITIONAL CREDIT** for the system error
✅ Coupon system error being fixed
📞 Reference ID: CPN-{hash(query) % 10000:04d}

Your discount of {expected_benefit} has been processed as credit to your account."""

        elif decision == "EXPLAIN_WITH_ALTERNATIVE_OFFER":
            return f"""📋 **Coupon Requirements + Alternative Offer**

The coupon {coupon_code} requires a minimum grocery order amount that wasn't met.

**💡 Alternative Solutions:**
📈 Add items to reach minimum order requirement ($40)
🎁 **ALTERNATIVE DISCOUNT** - 15% off your current grocery order
🔄 Save the coupon for a future larger order
💳 Small goodwill credit for the confusion

Would you like to apply the alternative 15% discount to this grocery order?"""

        elif decision == "EXPLAIN_COUPON_STATUS":
            return f"""🔍 **Coupon Status Information**

Regarding coupon {coupon_code} for your grocery order:

**📋 Coupon Status Check:**
⏰ Expiry date verification
📊 Usage limit status
📋 Terms and conditions review
🎯 Grocery order eligibility check

Based on our records, this coupon [specific status reason]. For valid alternative offers, please check the 'Offers' section in your app."""

        elif decision == "ESCALATE_COUPON_ABUSE_REVIEW":
            return f"""⚠️ **Coupon Usage Review Required**

Multiple coupon-related complaints require specialized review for account optimization.

**Next Steps:**
👨‍💼 **PROMOTIONS SPECIALIST** assigned
📊 Coupon usage pattern analysis
📞 Direct contact within 8 hours
🎯 Personalized offers solution

Reference ID: COU-{hash(query) % 10000:04d}"""

        else:  # STANDARD_COUPON_EXPLANATION
            return f"""📱 **Coupon Application Information**

Regarding {coupon_code} and the expected {expected_benefit} on your grocery order:

**How Grocery Coupons Work:**
✅ Must meet all terms and conditions
📊 Applied automatically when eligible
🕐 Some offers have time/usage limits
💡 Alternative offers always available in app

Please check the 'My Offers' section for currently available grocery discounts."""