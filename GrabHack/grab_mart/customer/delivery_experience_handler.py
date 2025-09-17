"""
Grab Mart Customer Delivery Experience Handler
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


class DeliveryExperienceHandler:
    """Customer-focused delivery experience management for grocery delivery with strict workflows"""

    def __init__(self, groq_api_key: str = None):
        self.service = "grab_mart"
        self.actor = "customer"
        self.handler_type = "delivery_experience_handler"

        # Initialize AI engine for structured analysis
        try:
            self.ai_engine = EnhancedAgenticAIEngine(groq_api_key)
            logger.info("AI engine initialized successfully for delivery experience handler")
        except Exception as e:
            logger.warning(f"AI engine initialization failed: {e}. Falling back to basic processing.")
            self.ai_engine = None

    def handle_delivery_delay(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle delay beyond promised time with strict 6-step workflow - TEXT ONLY"""
        logger.info(f"Processing delivery delay complaint: {query[:100]}...")

        # Step 1: Extract delay specifics from customer complaint
        delay_analysis = self.analyze_delivery_delay(query)
        logger.info(f"Delay analysis: {delay_analysis}")

        # Step 2: Get customer's order history and delivery patterns
        customer_history = self.get_customer_delivery_history(username)
        logger.info(f"Customer delivery history: {customer_history}")

        # Step 3: Check customer credibility and complaint frequency
        credibility_score = self.get_customer_credibility_score(username)
        complaint_pattern = self.check_delay_complaint_pattern(username)
        logger.info(f"Customer credibility: {credibility_score}/10, Complaint pattern: {complaint_pattern}")

        # Step 4: Validate delay timeline and store preparation time
        timeline_validation = self.validate_delay_timeline(delay_analysis, query)
        logger.info(f"Timeline validation: {timeline_validation}")

        # Step 5: Make compensation decision based on analysis
        decision = self.decide_delay_compensation(delay_analysis, credibility_score, timeline_validation, complaint_pattern)
        logger.info(f"Compensation decision: {decision}")

        # Step 6: Generate appropriate response with clear resolution
        response = self.generate_delay_response(decision, delay_analysis, query)
        logger.info(f"Delivery delay response generated successfully")

        return response

    def handle_partial_delivery(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle partial order delivered with strict 7-step workflow - REQUIRES IMAGE for verification"""
        logger.info(f"Processing partial delivery complaint: {query[:100]}...")

        # Step 1: Validate image requirement for partial delivery claims
        if not image_data:
            return "📷 Please upload a photo of what you received so we can verify which grocery items are missing from your order."

        # Step 2: Analyze image to identify what was actually delivered
        delivered_items_analysis = self.analyze_delivered_items_from_image(query, image_data)
        logger.info(f"Delivered items analysis: {delivered_items_analysis}")

        # Step 3: Compare delivered items against actual order
        order_comparison = self.compare_delivered_vs_ordered(delivered_items_analysis, username, query)
        logger.info(f"Order comparison: {order_comparison}")

        # Step 4: Assess value impact of missing items
        impact_assessment = self.assess_partial_delivery_impact(order_comparison)
        logger.info(f"Impact assessment: {impact_assessment}")

        # Step 5: Check customer credibility and delivery patterns
        credibility_score = self.get_customer_credibility_score(username)
        partial_delivery_history = self.check_partial_delivery_history(username)
        logger.info(f"Customer credibility: {credibility_score}/10, History: {partial_delivery_history}")

        # Step 6: Make resolution decision based on verified missing items
        decision = self.decide_partial_delivery_resolution(impact_assessment, credibility_score, partial_delivery_history)
        logger.info(f"Resolution decision: {decision}")

        # Step 7: Generate comprehensive response with next steps
        response = self.generate_partial_delivery_response(decision, order_comparison, impact_assessment)
        logger.info(f"Partial delivery response generated successfully")

        return response

    def handle_temperature_issues(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle cold/frozen items melted or leaked with strict 6-step workflow - REQUIRES IMAGE"""
        logger.info(f"Processing temperature issues complaint: {query[:100]}...")

        # Step 1: Validate image requirement for temperature issue claims
        if not image_data:
            return "📷 Please upload a photo showing the temperature issue (melted ice cream, warm dairy, cold fresh items, etc.) so we can properly assess your complaint."

        # Step 2: Analyze image to identify temperature-related problems
        temperature_analysis = self.analyze_temperature_issues_from_image(query, image_data)
        logger.info(f"Temperature analysis: {temperature_analysis}")

        # Step 3: Validate expected product temperature standards for groceries
        temperature_standards = self.validate_temperature_standards(temperature_analysis, query)
        logger.info(f"Temperature standards check: {temperature_standards}")

        # Step 4: Check customer credibility and temperature complaint history
        credibility_score = self.get_customer_credibility_score(username)
        temperature_complaint_history = self.check_temperature_complaint_history(username)
        logger.info(f"Customer credibility: {credibility_score}/10, History: {temperature_complaint_history}")

        # Step 5: Make compensation decision based on verified temperature issues
        decision = self.decide_temperature_compensation(temperature_analysis, credibility_score, temperature_standards)
        logger.info(f"Temperature compensation decision: {decision}")

        # Step 6: Generate appropriate response with resolution
        response = self.generate_temperature_response(decision, temperature_analysis, query)
        logger.info(f"Temperature issues response generated successfully")

        return response

    def handle_package_tampering(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle package tampered or unsealed with strict 7-step workflow - REQUIRES IMAGE"""
        logger.info(f"Processing package tampering complaint: {query[:100]}...")

        # Step 1: Validate image requirement for tampering claims
        if not image_data:
            return "📷 Please upload a photo showing the tampered or unsealed package so we can verify the security breach."

        # Step 2: Analyze image for signs of tampering or security compromise
        tampering_analysis = self.analyze_package_tampering_from_image(query, image_data)
        logger.info(f"Tampering analysis: {tampering_analysis}")

        # Step 3: Check package security standards and delivery protocols
        security_validation = self.validate_package_security_standards(tampering_analysis)
        logger.info(f"Security validation: {security_validation}")

        # Step 4: Assess product safety impact and health risks (especially for perishables)
        safety_assessment = self.assess_product_safety_impact(tampering_analysis, query)
        logger.info(f"Safety assessment: {safety_assessment}")

        # Step 5: Check customer credibility and tampering complaint patterns
        credibility_score = self.get_customer_credibility_score(username)
        tampering_history = self.check_tampering_complaint_history(username)
        logger.info(f"Customer credibility: {credibility_score}/10, History: {tampering_history}")

        # Step 6: Make resolution decision prioritizing product safety
        decision = self.decide_tampering_resolution(tampering_analysis, safety_assessment, credibility_score)
        logger.info(f"Tampering resolution decision: {decision}")

        # Step 7: Generate comprehensive response with safety measures
        response = self.generate_tampering_response(decision, tampering_analysis, safety_assessment)
        logger.info(f"Package tampering response generated successfully")

        return response

    def handle_multiple_deliveries(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle multiple deliveries for same order with strict 5-step workflow - TEXT ONLY"""
        logger.info(f"Processing multiple deliveries complaint: {query[:100]}...")

        # Step 1: Extract multiple delivery details from complaint
        delivery_analysis = self.analyze_multiple_delivery_claim(query)
        logger.info(f"Multiple delivery analysis: {delivery_analysis}")

        # Step 2: Verify delivery records and driver assignments
        delivery_verification = self.verify_delivery_records(delivery_analysis, username)
        logger.info(f"Delivery verification: {delivery_verification}")

        # Step 3: Check customer credibility and delivery complaint patterns
        credibility_score = self.get_customer_credibility_score(username)
        delivery_complaint_history = self.check_delivery_complaint_history(username)
        logger.info(f"Customer credibility: {credibility_score}/10, History: {delivery_complaint_history}")

        # Step 4: Make resolution decision based on verified delivery data
        decision = self.decide_multiple_delivery_resolution(delivery_analysis, delivery_verification, credibility_score)
        logger.info(f"Multiple delivery resolution decision: {decision}")

        # Step 5: Generate appropriate response with next steps
        response = self.generate_multiple_delivery_response(decision, delivery_analysis, delivery_verification)
        logger.info(f"Multiple deliveries response generated successfully")

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
                    cancellation_rate = cancelled_orders / total_orders

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

    def analyze_delivery_delay(self, query: str) -> str:
        """Analyze delivery delay details from customer complaint"""
        if not self.ai_engine:
            # Fallback analysis
            if "hour" in query.lower():
                return "SIGNIFICANT_DELAY_HOURS"
            elif "late" in query.lower():
                return "MODERATE_DELAY_MINUTES"
            else:
                return "UNCLEAR_DELAY"

        return self.ai_engine.process_complaint(
            function_name="analyze_delivery_delay",
            user_query=query,
            service=self.service,
            user_type=self.actor
        )

    def get_customer_delivery_history(self, username: str) -> str:
        """Get customer's delivery history from database"""
        # Simplified implementation - would query actual delivery data in real system
        if username == "anonymous":
            return "No delivery history available"
        else:
            return f"Delivery history for {username}: Average delivery time 32 minutes, 8 previous grocery orders, 0 delay complaints"

    def check_delay_complaint_pattern(self, username: str) -> str:
        """Check customer's pattern of delay complaints"""
        # Simplified implementation - would query database in real system
        if username == "anonymous":
            return "Unknown complaint pattern"
        elif "test" in username.lower():
            return "High frequency - 3+ delay complaints in last 3 months"
        else:
            return "Low frequency - 0-1 delay complaints in last 6 months"

    def validate_delay_timeline(self, delay_analysis: str, query: str) -> str:
        """Validate delivery delay timeline"""
        if not self.ai_engine:
            return "Timeline validation unavailable - AI engine not initialized"

        return self.ai_engine.process_complaint(
            function_name="validate_delay_timeline",
            user_query=f"Analysis: {delay_analysis} | Query: {query}",
            service=self.service,
            user_type=self.actor
        )

    def decide_delay_compensation(self, delay_analysis: str, credibility_score: int, timeline_validation: str, complaint_pattern: str) -> str:
        """Decide compensation for delivery delay"""
        if not self.ai_engine:
            # Simple fallback decision logic
            if credibility_score >= 7 and "SIGNIFICANT" in delay_analysis:
                return "FULL_COMPENSATION"
            elif credibility_score >= 5:
                return "PARTIAL_COMPENSATION"
            else:
                return "GOODWILL_GESTURE"

        return self.ai_engine.process_complaint(
            function_name="decide_delay_compensation",
            user_query=f"Analysis: {delay_analysis} | Credibility: {credibility_score} | Timeline: {timeline_validation} | Pattern: {complaint_pattern}",
            service=self.service,
            user_type=self.actor
        )

    def generate_delay_response(self, decision: str, delay_analysis: str, query: str) -> str:
        """Generate response for delivery delay"""
        if not self.ai_engine:
            # Fallback response generation
            if decision == "FULL_COMPENSATION":
                return "We sincerely apologize for the significant delivery delay. We're processing a full refund and providing store credit for the inconvenience."
            elif decision == "PARTIAL_COMPENSATION":
                return "We apologize for the delivery delay. We're providing partial compensation and have escalated this to improve our delivery times."
            else:
                return "We understand your concern about the delivery timing. We're providing a goodwill gesture and will work to improve our service."

        return self.ai_engine.process_complaint(
            function_name="generate_delay_response",
            user_query=f"Decision: {decision} | Analysis: {delay_analysis} | Original: {query}",
            service=self.service,
            user_type=self.actor
        )

    def analyze_delivered_items_from_image(self, query: str, image_data: str) -> str:
        """Analyze delivered items from image"""
        if not self.ai_engine:
            return "Image analysis unavailable - AI engine not initialized"

        return self.ai_engine.process_complaint(
            function_name="analyze_delivered_items_from_image",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def compare_delivered_vs_ordered(self, delivered_items_analysis: str, username: str, query: str) -> str:
        """Compare delivered items against customer's order"""
        return f"Order comparison for {username}: {delivered_items_analysis} vs expected grocery items"

    def assess_partial_delivery_impact(self, order_comparison: str) -> str:
        """Assess impact of partial delivery"""
        return f"Impact assessment: {order_comparison}"

    def check_partial_delivery_history(self, username: str) -> str:
        """Check customer's partial delivery complaint history"""
        return f"Partial delivery history for {username}: 0 previous partial delivery complaints"

    def decide_partial_delivery_resolution(self, impact_assessment: str, credibility_score: int, partial_delivery_history: str) -> str:
        """Decide resolution for partial delivery"""
        if not self.ai_engine:
            if credibility_score >= 7:
                return "REPLACEMENT_ORDER"
            elif credibility_score >= 5:
                return "PARTIAL_REFUND"
            else:
                return "STORE_CREDIT"

        return self.ai_engine.process_complaint(
            function_name="decide_partial_delivery_resolution",
            user_query=f"Impact: {impact_assessment} | Credibility: {credibility_score} | History: {partial_delivery_history}",
            service=self.service,
            user_type=self.actor
        )

    def generate_partial_delivery_response(self, decision: str, order_comparison: str, impact_assessment: str) -> str:
        """Generate response for partial delivery"""
        if not self.ai_engine:
            if decision == "REPLACEMENT_ORDER":
                return "We apologize for the missing items in your grocery delivery. We're sending the missing items immediately at no charge."
            elif decision == "PARTIAL_REFUND":
                return "We understand some items were missing from your delivery. We're processing a partial refund for the missing items."
            else:
                return "We're sorry about the incomplete delivery. We're providing store credit for the missing items."

        return self.ai_engine.process_complaint(
            function_name="generate_partial_delivery_response",
            user_query=f"Decision: {decision} | Comparison: {order_comparison} | Impact: {impact_assessment}",
            service=self.service,
            user_type=self.actor
        )

    def analyze_temperature_issues_from_image(self, query: str, image_data: str) -> str:
        """Analyze temperature issues from image"""
        if not self.ai_engine:
            return "Temperature analysis unavailable - AI engine not initialized"

        return self.ai_engine.process_complaint(
            function_name="analyze_temperature_issues_from_image",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def validate_temperature_standards(self, temperature_analysis: str, query: str) -> str:
        """Validate temperature standards for grocery products"""
        return f"Temperature standards validation for grocery products: {temperature_analysis}"

    def check_temperature_complaint_history(self, username: str) -> str:
        """Check customer's temperature complaint history"""
        return f"Temperature complaint history for {username}: 0 previous temperature complaints"

    def decide_temperature_compensation(self, temperature_analysis: str, credibility_score: int, temperature_standards: str) -> str:
        """Decide compensation for temperature issues"""
        if not self.ai_engine:
            if credibility_score >= 7:
                return "FULL_REPLACEMENT"
            elif credibility_score >= 5:
                return "PARTIAL_COMPENSATION"
            else:
                return "STORE_CREDIT"

        return self.ai_engine.process_complaint(
            function_name="decide_temperature_compensation",
            user_query=f"Analysis: {temperature_analysis} | Credibility: {credibility_score} | Standards: {temperature_standards}",
            service=self.service,
            user_type=self.actor
        )

    def generate_temperature_response(self, decision: str, temperature_analysis: str, query: str) -> str:
        """Generate response for temperature issues"""
        if not self.ai_engine:
            if decision == "FULL_REPLACEMENT":
                return "We're very sorry about the temperature issues with your grocery items. We're sending fresh replacements immediately."
            elif decision == "PARTIAL_COMPENSATION":
                return "We apologize for the temperature problems. We're providing compensation for the affected items."
            else:
                return "We understand your concern about product temperatures. We're providing store credit and will improve our cold chain."

        return self.ai_engine.process_complaint(
            function_name="generate_temperature_response",
            user_query=f"Decision: {decision} | Analysis: {temperature_analysis} | Original: {query}",
            service=self.service,
            user_type=self.actor
        )

    def analyze_package_tampering_from_image(self, query: str, image_data: str) -> str:
        """Analyze package tampering from image"""
        if not self.ai_engine:
            return "Tampering analysis unavailable - AI engine not initialized"

        return self.ai_engine.process_complaint(
            function_name="analyze_package_tampering_from_image",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def validate_package_security_standards(self, tampering_analysis: str) -> str:
        """Validate package security standards"""
        return f"Package security validation: {tampering_analysis}"

    def assess_product_safety_impact(self, tampering_analysis: str, query: str) -> str:
        """Assess product safety impact of tampering"""
        return f"Product safety impact assessment: {tampering_analysis}"

    def check_tampering_complaint_history(self, username: str) -> str:
        """Check customer's tampering complaint history"""
        return f"Tampering complaint history for {username}: 0 previous tampering complaints"

    def decide_tampering_resolution(self, tampering_analysis: str, safety_assessment: str, credibility_score: int) -> str:
        """Decide resolution for tampering complaints"""
        if not self.ai_engine:
            # Safety first approach for tampering
            return "FULL_REFUND_SAFETY_PRIORITY"

        return self.ai_engine.process_complaint(
            function_name="decide_tampering_resolution",
            user_query=f"Analysis: {tampering_analysis} | Safety: {safety_assessment} | Credibility: {credibility_score}",
            service=self.service,
            user_type=self.actor
        )

    def generate_tampering_response(self, decision: str, tampering_analysis: str, safety_assessment: str) -> str:
        """Generate response for tampering complaints"""
        if not self.ai_engine:
            return "We take package security very seriously. We're processing a full refund and investigating this incident to ensure product safety."

        return self.ai_engine.process_complaint(
            function_name="generate_tampering_response",
            user_query=f"Decision: {decision} | Analysis: {tampering_analysis} | Safety: {safety_assessment}",
            service=self.service,
            user_type=self.actor
        )

    def analyze_multiple_delivery_claim(self, query: str) -> str:
        """Analyze multiple delivery claim"""
        if not self.ai_engine:
            return "Multiple delivery analysis unavailable"

        return self.ai_engine.process_complaint(
            function_name="analyze_multiple_delivery_claim",
            user_query=query,
            service=self.service,
            user_type=self.actor
        )

    def verify_delivery_records(self, delivery_analysis: str, username: str) -> str:
        """Verify delivery records"""
        return f"Delivery records verification for {username}: {delivery_analysis}"

    def check_delivery_complaint_history(self, username: str) -> str:
        """Check customer's delivery complaint history"""
        return f"Delivery complaint history for {username}: 0 previous delivery complaints"

    def decide_multiple_delivery_resolution(self, delivery_analysis: str, delivery_verification: str, credibility_score: int) -> str:
        """Decide resolution for multiple delivery complaints"""
        if not self.ai_engine:
            if credibility_score >= 7:
                return "COMPENSATION_PROVIDED"
            else:
                return "INVESTIGATION_REQUIRED"

        return self.ai_engine.process_complaint(
            function_name="decide_multiple_delivery_resolution",
            user_query=f"Analysis: {delivery_analysis} | Verification: {delivery_verification} | Credibility: {credibility_score}",
            service=self.service,
            user_type=self.actor
        )

    def generate_multiple_delivery_response(self, decision: str, delivery_analysis: str, delivery_verification: str) -> str:
        """Generate response for multiple delivery complaints"""
        if not self.ai_engine:
            if decision == "COMPENSATION_PROVIDED":
                return "We apologize for the multiple delivery inconvenience. We're providing compensation and optimizing our delivery process."
            else:
                return "We're investigating the multiple delivery issue and will respond with our findings and resolution."

        return self.ai_engine.process_complaint(
            function_name="generate_multiple_delivery_response",
            user_query=f"Decision: {decision} | Analysis: {delivery_analysis} | Verification: {delivery_verification}",
            service=self.service,
            user_type=self.actor
        )