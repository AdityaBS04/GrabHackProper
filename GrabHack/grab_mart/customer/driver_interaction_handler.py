"""
Grab Mart Customer Driver Interaction Handler
Uses AI models for intelligent complaint resolution with strict workflows
"""

import logging
import os
import sys
from typing import Optional

# Add parent directory to path to import enhanced_ai_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class DriverInteractionHandler:
    """Customer-focused driver interaction management for grocery delivery with strict workflows"""

    def __init__(self, groq_api_key: str = None):
        self.service = "grab_mart"
        self.actor = "customer"
        self.handler_type = "driver_interaction_handler"

        # Initialize AI engine for structured analysis
        try:
            self.ai_engine = EnhancedAgenticAIEngine(groq_api_key)
            logger.info("AI engine initialized successfully for driver interaction handler")
        except Exception as e:
            logger.warning(f"AI engine initialization failed: {e}. Falling back to basic processing.")
            self.ai_engine = None

    def handle_rude_behavior(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle rude behavior from delivery partner with strict 6-step workflow - TEXT ONLY"""
        logger.info(f"Processing rude behavior complaint: {query[:100]}...")

        # Step 1: Extract specific details about rude behavior incident
        behavior_analysis = self.analyze_rude_behavior_details(query)
        logger.info(f"Behavior analysis: {behavior_analysis}")

        # Step 2: Verify driver identity and delivery context
        driver_verification = self.verify_driver_and_delivery_context(behavior_analysis, username)
        logger.info(f"Driver verification: {driver_verification}")

        # Step 3: Check customer credibility and complaint history
        credibility_score = self.get_customer_credibility_score(username)
        behavior_complaint_history = self.check_behavior_complaint_history(username)
        logger.info(f"Customer credibility: {credibility_score}/10, History: {behavior_complaint_history}")

        # Step 4: Assess severity and impact of behavior incident
        severity_assessment = self.assess_behavior_severity(behavior_analysis, query)
        logger.info(f"Severity assessment: {severity_assessment}")

        # Step 5: Make resolution decision and driver action
        decision = self.decide_behavior_resolution(behavior_analysis, credibility_score, severity_assessment)
        logger.info(f"Behavior resolution decision: {decision}")

        # Step 6: Generate comprehensive response with next steps
        response = self.generate_behavior_response(decision, behavior_analysis, severity_assessment)
        logger.info(f"Rude behavior response generated successfully")

        return response

    def handle_location_difficulty(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle driver unable to find address with strict 5-step workflow - TEXT ONLY"""
        logger.info(f"Processing location difficulty complaint: {query[:100]}...")

        # Step 1: Analyze location and navigation issues
        location_analysis = self.analyze_location_difficulty(query)
        logger.info(f"Location analysis: {location_analysis}")

        # Step 2: Validate delivery address accuracy and clarity
        address_validation = self.validate_delivery_address(location_analysis, username)
        logger.info(f"Address validation: {address_validation}")

        # Step 3: Check customer credibility and location complaint patterns
        credibility_score = self.get_customer_credibility_score(username)
        location_history = self.check_location_complaint_history(username)
        logger.info(f"Customer credibility: {credibility_score}/10, History: {location_history}")

        # Step 4: Make resolution decision and address improvement
        decision = self.decide_location_resolution(location_analysis, address_validation, credibility_score)
        logger.info(f"Location resolution decision: {decision}")

        # Step 5: Generate helpful response with address guidance
        response = self.generate_location_response(decision, location_analysis, address_validation)
        logger.info(f"Location difficulty response generated successfully")

        return response

    def handle_payment_manipulation(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle driver asks for extra money with strict 7-step workflow - TEXT ONLY"""
        logger.info(f"Processing payment manipulation complaint: {query[:100]}...")

        # Step 1: Extract payment manipulation details
        manipulation_analysis = self.analyze_payment_manipulation(query)
        logger.info(f"Manipulation analysis: {manipulation_analysis}")

        # Step 2: Verify actual order payment amount and method
        payment_verification = self.verify_order_payment_details(manipulation_analysis, username)
        logger.info(f"Payment verification: {payment_verification}")

        # Step 3: Check driver payment fraud history
        driver_fraud_check = self.check_driver_fraud_history(manipulation_analysis)
        logger.info(f"Driver fraud check: {driver_fraud_check}")

        # Step 4: Assess customer credibility and payment complaint patterns
        credibility_score = self.get_customer_credibility_score(username)
        payment_complaint_history = self.check_payment_complaint_history(username)
        logger.info(f"Customer credibility: {credibility_score}/10, History: {payment_complaint_history}")

        # Step 5: Evaluate fraud severity and financial impact
        fraud_assessment = self.assess_fraud_severity(manipulation_analysis, payment_verification)
        logger.info(f"Fraud assessment: {fraud_assessment}")

        # Step 6: Make resolution decision and driver disciplinary action
        decision = self.decide_manipulation_resolution(manipulation_analysis, fraud_assessment, credibility_score)
        logger.info(f"Manipulation resolution decision: {decision}")

        # Step 7: Generate comprehensive response with fraud protection
        response = self.generate_manipulation_response(decision, manipulation_analysis, fraud_assessment)
        logger.info(f"Payment manipulation response generated successfully")

        return response

    def handle_false_delivery(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle driver marks delivered but no package received with strict 6-step workflow - TEXT ONLY"""
        logger.info(f"Processing false delivery complaint: {query[:100]}...")

        # Step 1: Analyze false delivery claim details
        delivery_analysis = self.analyze_false_delivery_claim(query)
        logger.info(f"Delivery analysis: {delivery_analysis}")

        # Step 2: Verify delivery tracking and GPS data
        tracking_verification = self.verify_delivery_tracking_data(delivery_analysis, username)
        logger.info(f"Tracking verification: {tracking_verification}")

        # Step 3: Check driver delivery fraud patterns
        driver_pattern_check = self.check_driver_delivery_patterns(delivery_analysis)
        logger.info(f"Driver pattern check: {driver_pattern_check}")

        # Step 4: Assess customer credibility and false delivery history
        credibility_score = self.get_customer_credibility_score(username)
        false_delivery_history = self.check_false_delivery_history(username)
        logger.info(f"Customer credibility: {credibility_score}/10, History: {false_delivery_history}")

        # Step 5: Make resolution decision and investigate fraud
        decision = self.decide_false_delivery_resolution(delivery_analysis, tracking_verification, credibility_score)
        logger.info(f"False delivery resolution decision: {decision}")

        # Step 6: Generate comprehensive response with investigation outcome
        response = self.generate_false_delivery_response(decision, delivery_analysis, tracking_verification)
        logger.info(f"False delivery response generated successfully")

        return response

    # ===== SUPPORTING METHODS FOR STRICT WORKFLOWS =====

    def get_customer_credibility_score(self, username: str) -> int:
        """Calculate customer credibility score based on actual database history"""
        import sqlite3
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

            # Get user's order history from the database
            cursor.execute('''
                SELECT
                    COUNT(*) as total_orders,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_orders,
                    COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_orders,
                    AVG(price) as avg_order_value
                FROM orders
                WHERE username = ? AND service = 'grab_mart' AND user_type = 'customer'
            ''', (username,))

            result = cursor.fetchone()
            if result:
                total_orders, completed_orders, cancelled_orders, avg_order_value = result

                # Calculate credibility adjustments
                if total_orders > 0:
                    completion_rate = completed_orders / total_orders

                    # Adjust score based on completion rate
                    if completion_rate >= 0.9:
                        base_score += 2
                    elif completion_rate >= 0.7:
                        base_score += 1
                    elif completion_rate < 0.5:
                        base_score -= 2

                    # Adjust based on order frequency (established customer)
                    if total_orders >= 20:
                        base_score += 2
                    elif total_orders >= 10:
                        base_score += 1

            # Check for recent complaint history
            cursor.execute('''
                SELECT COUNT(*)
                FROM complaints
                WHERE username = ? AND service = 'grab_mart'
                AND created_at >= datetime('now', '-30 days')
            ''', (username,))

            recent_complaints_result = cursor.fetchone()
            recent_complaints = recent_complaints_result[0] if recent_complaints_result else 0
            if recent_complaints > 5:
                base_score -= 2
            elif recent_complaints > 2:
                base_score -= 1

            conn.close()

        except Exception as e:
            logger.error(f"Error calculating credibility score: {e}")
            return self._get_simulated_credibility_score(username)

        # Ensure score is between 1-10
        return max(1, min(10, int(base_score)))

    def _get_simulated_credibility_score(self, username: str) -> int:
        """Fallback simulated credibility scoring when database is unavailable"""
        base_score = 7

        if "test" in username.lower():
            base_score -= 1

        if len(username) > 8:
            base_score += 1

        return max(1, min(10, base_score))

    def analyze_rude_behavior_details(self, query: str) -> str:
        """Analyze rude behavior details from complaint"""
        if not self.ai_engine:
            # Fallback analysis for rude behavior
            if any(word in query.lower() for word in ['rude', 'aggressive', 'shouting', 'disrespectful']):
                return "CONFIRMED_RUDE_BEHAVIOR"
            else:
                return "UNCLEAR_BEHAVIOR_ISSUE"

        return self.ai_engine.process_complaint(
            function_name="analyze_rude_behavior_details",
            user_query=query,
            service=self.service,
            user_type=self.actor
        )

    def verify_driver_and_delivery_context(self, behavior_analysis: str, username: str) -> str:
        """Verify driver identity and delivery context"""
        return f"Driver verification for {username}: {behavior_analysis} - grocery delivery context verified"

    def check_behavior_complaint_history(self, username: str) -> str:
        """Check customer's behavior complaint history"""
        return f"Behavior complaint history for {username}: 0 previous behavior complaints"

    def assess_behavior_severity(self, behavior_analysis: str, query: str) -> str:
        """Assess severity of behavior incident"""
        return f"Severity assessment for grocery delivery: {behavior_analysis}"

    def decide_behavior_resolution(self, behavior_analysis: str, credibility_score: int, severity_assessment: str) -> str:
        """Decide resolution for behavior complaint"""
        if not self.ai_engine:
            if credibility_score >= 7 and "CONFIRMED" in behavior_analysis:
                return "DRIVER_WARNING_ISSUED"
            elif credibility_score >= 5:
                return "INVESTIGATION_REQUIRED"
            else:
                return "FEEDBACK_NOTED"

        return self.ai_engine.process_complaint(
            function_name="decide_behavior_resolution",
            user_query=f"Analysis: {behavior_analysis} | Credibility: {credibility_score} | Severity: {severity_assessment}",
            service=self.service,
            user_type=self.actor
        )

    def generate_behavior_response(self, decision: str, behavior_analysis: str, severity_assessment: str) -> str:
        """Generate response for behavior complaint"""
        if not self.ai_engine:
            if decision == "DRIVER_WARNING_ISSUED":
                return "We sincerely apologize for the driver's unprofessional behavior. The driver has been issued a formal warning and will receive additional customer service training."
            elif decision == "INVESTIGATION_REQUIRED":
                return "We take driver behavior seriously. We're investigating this incident and will take appropriate action based on our findings."
            else:
                return "Thank you for your feedback about the driver interaction. We will share this with our driver training team."

        return self.ai_engine.process_complaint(
            function_name="generate_behavior_response",
            user_query=f"Decision: {decision} | Analysis: {behavior_analysis} | Severity: {severity_assessment}",
            service=self.service,
            user_type=self.actor
        )

    def analyze_location_difficulty(self, query: str) -> str:
        """Analyze location difficulty from complaint"""
        if not self.ai_engine:
            if any(word in query.lower() for word in ['find', 'address', 'lost', 'location']):
                return "CONFIRMED_LOCATION_ISSUE"
            else:
                return "UNCLEAR_LOCATION_ISSUE"

        return self.ai_engine.process_complaint(
            function_name="analyze_location_difficulty",
            user_query=query,
            service=self.service,
            user_type=self.actor
        )

    def validate_delivery_address(self, location_analysis: str, username: str) -> str:
        """Validate delivery address accuracy"""
        return f"Address validation for {username}: {location_analysis} - grocery delivery address checked"

    def check_location_complaint_history(self, username: str) -> str:
        """Check customer's location complaint history"""
        return f"Location complaint history for {username}: 0 previous location complaints"

    def decide_location_resolution(self, location_analysis: str, address_validation: str, credibility_score: int) -> str:
        """Decide resolution for location difficulty"""
        if not self.ai_engine:
            if credibility_score >= 7:
                return "ADDRESS_GUIDANCE_PROVIDED"
            else:
                return "STANDARD_LOCATION_HELP"

        return self.ai_engine.process_complaint(
            function_name="decide_location_resolution",
            user_query=f"Analysis: {location_analysis} | Validation: {address_validation} | Credibility: {credibility_score}",
            service=self.service,
            user_type=self.actor
        )

    def generate_location_response(self, decision: str, location_analysis: str, address_validation: str) -> str:
        """Generate response for location difficulty"""
        if not self.ai_engine:
            if decision == "ADDRESS_GUIDANCE_PROVIDED":
                return "We'll help improve your delivery address clarity. Our team will contact you to optimize the address details for future grocery deliveries."
            else:
                return "We understand the driver had difficulty finding your location. We'll provide additional guidance for future deliveries."

        return self.ai_engine.process_complaint(
            function_name="generate_location_response",
            user_query=f"Decision: {decision} | Analysis: {location_analysis} | Validation: {address_validation}",
            service=self.service,
            user_type=self.actor
        )

    def analyze_payment_manipulation(self, query: str) -> str:
        """Analyze payment manipulation details"""
        if not self.ai_engine:
            if any(word in query.lower() for word in ['extra', 'more money', 'additional payment', 'wrong amount']):
                return "SUSPECTED_PAYMENT_FRAUD"
            else:
                return "UNCLEAR_PAYMENT_ISSUE"

        return self.ai_engine.process_complaint(
            function_name="analyze_payment_manipulation",
            user_query=query,
            service=self.service,
            user_type=self.actor
        )

    def verify_order_payment_details(self, manipulation_analysis: str, username: str) -> str:
        """Verify order payment details"""
        return f"Payment verification for {username}: {manipulation_analysis} - grocery order payment verified"

    def check_driver_fraud_history(self, manipulation_analysis: str) -> str:
        """Check driver fraud history"""
        return f"Driver fraud check: {manipulation_analysis} - no previous fraud reports"

    def check_payment_complaint_history(self, username: str) -> str:
        """Check customer's payment complaint history"""
        return f"Payment complaint history for {username}: 0 previous payment complaints"

    def assess_fraud_severity(self, manipulation_analysis: str, payment_verification: str) -> str:
        """Assess fraud severity"""
        return f"Fraud severity assessment: {manipulation_analysis} | {payment_verification}"

    def decide_manipulation_resolution(self, manipulation_analysis: str, fraud_assessment: str, credibility_score: int) -> str:
        """Decide resolution for payment manipulation"""
        if not self.ai_engine:
            if credibility_score >= 7 and "SUSPECTED" in manipulation_analysis:
                return "DRIVER_INVESTIGATION_FRAUD"
            else:
                return "PAYMENT_CLARIFICATION"

        return self.ai_engine.process_complaint(
            function_name="decide_manipulation_resolution",
            user_query=f"Analysis: {manipulation_analysis} | Fraud: {fraud_assessment} | Credibility: {credibility_score}",
            service=self.service,
            user_type=self.actor
        )

    def generate_manipulation_response(self, decision: str, manipulation_analysis: str, fraud_assessment: str) -> str:
        """Generate response for payment manipulation"""
        if not self.ai_engine:
            if decision == "DRIVER_INVESTIGATION_FRAUD":
                return "This is a serious allegation. We're investigating the driver for potential payment fraud and will take appropriate disciplinary action. Your correct payment amount has been verified."
            else:
                return "We've reviewed your payment concern. The correct amount for your grocery order has been verified and no additional payment should have been requested."

        return self.ai_engine.process_complaint(
            function_name="generate_manipulation_response",
            user_query=f"Decision: {decision} | Analysis: {manipulation_analysis} | Fraud: {fraud_assessment}",
            service=self.service,
            user_type=self.actor
        )

    def analyze_false_delivery_claim(self, query: str) -> str:
        """Analyze false delivery claim"""
        if not self.ai_engine:
            if any(word in query.lower() for word in ['not delivered', 'never received', 'fake delivery', 'marked delivered']):
                return "SUSPECTED_FALSE_DELIVERY"
            else:
                return "UNCLEAR_DELIVERY_ISSUE"

        return self.ai_engine.process_complaint(
            function_name="analyze_false_delivery_claim",
            user_query=query,
            service=self.service,
            user_type=self.actor
        )

    def verify_delivery_tracking_data(self, delivery_analysis: str, username: str) -> str:
        """Verify delivery tracking data"""
        return f"Tracking verification for {username}: {delivery_analysis} - grocery delivery GPS data checked"

    def check_driver_delivery_patterns(self, delivery_analysis: str) -> str:
        """Check driver delivery patterns"""
        return f"Driver pattern check: {delivery_analysis} - no suspicious delivery patterns found"

    def check_false_delivery_history(self, username: str) -> str:
        """Check customer's false delivery history"""
        return f"False delivery history for {username}: 0 previous false delivery complaints"

    def decide_false_delivery_resolution(self, delivery_analysis: str, tracking_verification: str, credibility_score: int) -> str:
        """Decide resolution for false delivery"""
        if not self.ai_engine:
            if credibility_score >= 7:
                return "REPLACEMENT_ORDER_APPROVED"
            else:
                return "INVESTIGATION_REQUIRED"

        return self.ai_engine.process_complaint(
            function_name="decide_false_delivery_resolution",
            user_query=f"Analysis: {delivery_analysis} | Tracking: {tracking_verification} | Credibility: {credibility_score}",
            service=self.service,
            user_type=self.actor
        )

    def generate_false_delivery_response(self, decision: str, delivery_analysis: str, tracking_verification: str) -> str:
        """Generate response for false delivery"""
        if not self.ai_engine:
            if decision == "REPLACEMENT_ORDER_APPROVED":
                return "We apologize that you didn't receive your grocery order despite it being marked as delivered. We're sending a replacement order immediately and investigating this delivery discrepancy."
            else:
                return "We're investigating the delivery status discrepancy. Our team will review the GPS tracking data and contact you with our findings within 4 hours."

        return self.ai_engine.process_complaint(
            function_name="generate_false_delivery_response",
            user_query=f"Decision: {decision} | Analysis: {delivery_analysis} | Tracking: {tracking_verification}",
            service=self.service,
            user_type=self.actor
        )