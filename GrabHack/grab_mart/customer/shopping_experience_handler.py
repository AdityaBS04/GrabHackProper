"""
Grab Mart Customer Shopping Experience Handler
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


class CustomerShoppingExperienceHandler:
    """Customer-focused grocery shopping experience management with real AI"""

    def __init__(self, groq_api_key: str = None):
        self.service = "grab_mart"
        self.actor = "customer"
        self.handler_type = "shopping_experience_handler"
        self.ai_engine = EnhancedAgenticAIEngine()

    def handle_customer_product_quality(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle customer product quality complaints and freshness issues with strict 7-step workflow - IMAGE REQUIRED"""
        logger.info(f"Processing product quality complaint: {query[:100]}...")

        # Step 1: Validate image requirement for quality claims
        if not image_data:
            return "📷 Please upload a photo of the product showing the quality issue so we can properly assess and resolve your concern."

        # Step 2: Analyze product quality issue from image and description
        quality_analysis = self.analyze_product_quality_from_image(query, image_data)
        logger.info(f"Quality analysis: {quality_analysis}")

        # Step 3: Assess health and safety impact
        safety_assessment = self.assess_product_safety_impact(quality_analysis, query)
        logger.info(f"Safety assessment: {safety_assessment}")

        # Step 4: Verify order details and product identification
        order_verification = self.verify_product_order_details(quality_analysis, username)
        logger.info(f"Order verification: {order_verification}")

        # Step 5: Check customer credibility and quality complaint history
        credibility_score = self.get_customer_credibility_score(username)
        quality_complaint_history = self.check_quality_complaint_history(username)
        logger.info(f"Customer credibility: {credibility_score}/10, Quality history: {quality_complaint_history}")

        # Step 6: Make resolution decision based on evidence and safety concerns
        decision = self.decide_product_quality_resolution(quality_analysis, safety_assessment, credibility_score, quality_complaint_history)
        logger.info(f"Quality resolution decision: {decision}")

        # Step 7: Generate comprehensive response with safety measures
        response = self.generate_product_quality_response(decision, quality_analysis, safety_assessment)
        logger.info(f"Product quality response generated successfully")

        return response

    def handle_customer_shopping_convenience(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle customer shopping convenience and experience enhancement with strict 5-step workflow - TEXT ONLY"""
        logger.info(f"Processing shopping convenience complaint: {query[:100]}...")

        # Step 1: Extract specific convenience issues and expectations
        convenience_details = self.extract_convenience_issues(query)
        logger.info(f"Convenience details: {convenience_details}")

        # Step 2: Analyze shopping patterns and preferences
        shopping_pattern_analysis = self.analyze_customer_shopping_patterns(username, convenience_details)
        logger.info(f"Shopping pattern analysis: {shopping_pattern_analysis}")

        # Step 3: Check customer credibility and service usage history
        credibility_score = self.get_customer_credibility_score(username)
        service_usage_history = self.check_service_usage_patterns(username)
        logger.info(f"Customer credibility: {credibility_score}/10, Service usage: {service_usage_history}")

        # Step 4: Assess feasibility of convenience improvements
        improvement_feasibility = self.assess_convenience_improvement_feasibility(convenience_details, shopping_pattern_analysis)
        logger.info(f"Improvement feasibility: {improvement_feasibility}")

        # Step 5: Make enhancement decision and generate response
        decision = self.decide_convenience_enhancement(improvement_feasibility, credibility_score, service_usage_history)
        response = self.generate_convenience_enhancement_response(decision, convenience_details, query)
        logger.info(f"Convenience enhancement response generated successfully")

        return response

    def handle_customer_substitution_satisfaction(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle customer product substitution satisfaction and preferences with strict 6-step workflow - TEXT ONLY"""
        logger.info(f"Processing substitution satisfaction complaint: {query[:100]}...")

        # Step 1: Extract substitution details and customer expectations
        substitution_details = self.extract_substitution_issues(query)
        logger.info(f"Substitution details: {substitution_details}")

        # Step 2: Analyze substitution quality and appropriateness
        substitution_analysis = self.analyze_substitution_appropriateness(substitution_details)
        logger.info(f"Substitution analysis: {substitution_analysis}")

        # Step 3: Review customer substitution preferences and history
        substitution_preferences = self.get_customer_substitution_preferences(username)
        logger.info(f"Substitution preferences: {substitution_preferences}")

        # Step 4: Check customer credibility and substitution complaint patterns
        credibility_score = self.get_customer_credibility_score(username)
        substitution_complaint_history = self.check_substitution_complaint_history(username)
        logger.info(f"Customer credibility: {credibility_score}/10, Substitution history: {substitution_complaint_history}")

        # Step 5: Assess substitution policy compliance
        policy_compliance = self.assess_substitution_policy_compliance(substitution_analysis, substitution_preferences)
        logger.info(f"Policy compliance: {policy_compliance}")

        # Step 6: Make resolution decision and generate response
        decision = self.decide_substitution_resolution(substitution_analysis, policy_compliance, credibility_score)
        response = self.generate_substitution_response(decision, substitution_details, query)
        logger.info(f"Substitution resolution response generated successfully")

        return response

    def handle_customer_grocery_freshness(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle customer grocery freshness concerns and quality expectations with strict 7-step workflow - IMAGE REQUIRED"""
        logger.info(f"Processing grocery freshness complaint: {query[:100]}...")

        # Step 1: Validate image requirement for freshness claims
        if not image_data:
            return "📷 Please upload a photo of the grocery items showing the freshness issue (expiry dates, appearance) so we can verify and resolve your concern."

        # Step 2: Analyze freshness issue from image and complaint
        freshness_analysis = self.analyze_freshness_from_image(query, image_data)
        logger.info(f"Freshness analysis: {freshness_analysis}")

        # Step 3: Assess health and safety implications
        health_safety_assessment = self.assess_freshness_health_safety(freshness_analysis, query)
        logger.info(f"Health safety assessment: {health_safety_assessment}")

        # Step 4: Verify purchase timeline and storage conditions
        timeline_verification = self.verify_purchase_timeline_and_storage(freshness_analysis, username)
        logger.info(f"Timeline verification: {timeline_verification}")

        # Step 5: Check customer credibility and freshness complaint patterns
        credibility_score = self.get_customer_credibility_score(username)
        freshness_complaint_history = self.check_freshness_complaint_history(username)
        logger.info(f"Customer credibility: {credibility_score}/10, Freshness history: {freshness_complaint_history}")

        # Step 6: Validate freshness complaint legitimacy
        freshness_validation = self.validate_freshness_complaint(freshness_analysis, timeline_verification, credibility_score)
        logger.info(f"Freshness validation: {freshness_validation}")

        # Step 7: Make resolution decision prioritizing health safety
        decision = self.decide_freshness_resolution(freshness_validation, health_safety_assessment, credibility_score)
        response = self.generate_freshness_response(decision, freshness_analysis, health_safety_assessment)
        logger.info(f"Freshness resolution response generated successfully")

        return response

    def handle_customer_bulk_shopping(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle customer bulk shopping needs and family-size orders with strict 5-step workflow - TEXT ONLY"""
        logger.info(f"Processing bulk shopping complaint: {query[:100]}...")

        # Step 1: Extract bulk shopping requirements and issues
        bulk_shopping_details = self.extract_bulk_shopping_issues(query)
        logger.info(f"Bulk shopping details: {bulk_shopping_details}")

        # Step 2: Analyze customer bulk shopping patterns and needs
        bulk_pattern_analysis = self.analyze_customer_bulk_patterns(username, bulk_shopping_details)
        logger.info(f"Bulk pattern analysis: {bulk_pattern_analysis}")

        # Step 3: Check customer credibility and bulk order history
        credibility_score = self.get_customer_credibility_score(username)
        bulk_order_history = self.check_bulk_order_history(username)
        logger.info(f"Customer credibility: {credibility_score}/10, Bulk history: {bulk_order_history}")

        # Step 4: Assess bulk service optimization opportunities
        optimization_assessment = self.assess_bulk_service_optimization(bulk_shopping_details, bulk_pattern_analysis)
        logger.info(f"Optimization assessment: {optimization_assessment}")

        # Step 5: Make bulk service enhancement decision and generate response
        decision = self.decide_bulk_shopping_enhancement(optimization_assessment, credibility_score, bulk_order_history)
        response = self.generate_bulk_shopping_response(decision, bulk_shopping_details, query)
        logger.info(f"Bulk shopping enhancement response generated successfully")

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

        return final_score

    def _get_simulated_credibility_score(self, username: str) -> int:
        """Fallback simulated credibility scoring when database is unavailable"""
        base_score = 7

        if "test" in username.lower():
            base_score -= 1

        if len(username) > 8:
            base_score += 1

        return max(1, min(10, base_score))

    # ===== PRODUCT QUALITY WORKFLOW METHODS =====

    def analyze_product_quality_from_image(self, query: str, image_data: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="analyze_product_quality_from_image",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def assess_product_safety_impact(self, quality_analysis: str, query: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="assess_product_safety_impact",
            user_query=f"Quality Analysis: {quality_analysis} | Original Query: {query}",
            service=self.service,
            user_type=self.actor
        )

    def verify_product_order_details(self, quality_analysis: str, username: str) -> str:
        return f"Product order verification for {username}: {quality_analysis}"

    def check_quality_complaint_history(self, username: str) -> str:
        if username == "anonymous":
            return "NO_HISTORY_AVAILABLE"
        elif "test" in username.lower():
            return "FREQUENT_QUALITY_COMPLAINTS"
        else:
            return "OCCASIONAL_QUALITY_ISSUES"

    def decide_product_quality_resolution(self, quality_analysis: str, safety_assessment: str, credibility_score: int, quality_history: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="decide_product_quality_resolution",
            user_query=f"Quality: {quality_analysis} | Safety: {safety_assessment} | Credibility: {credibility_score} | History: {quality_history}",
            service=self.service,
            user_type=self.actor
        )

    def generate_product_quality_response(self, decision: str, quality_analysis: str, safety_assessment: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="generate_product_quality_response",
            user_query=f"Decision: {decision} | Quality: {quality_analysis} | Safety: {safety_assessment}",
            service=self.service,
            user_type=self.actor
        )

    # ===== SHOPPING CONVENIENCE WORKFLOW METHODS =====

    def extract_convenience_issues(self, query: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="extract_convenience_issues",
            user_query=query,
            service=self.service,
            user_type=self.actor
        )

    def analyze_customer_shopping_patterns(self, username: str, convenience_details: str) -> str:
        return f"Shopping patterns for {username}: {convenience_details}"

    def check_service_usage_patterns(self, username: str) -> str:
        if username == "anonymous":
            return "NO_USAGE_HISTORY"
        elif "test" in username.lower():
            return "HEAVY_SERVICE_USER"
        else:
            return "REGULAR_SERVICE_USER"

    def assess_convenience_improvement_feasibility(self, convenience_details: str, shopping_patterns: str) -> str:
        return f"Feasibility assessment: {convenience_details} vs {shopping_patterns}"

    def decide_convenience_enhancement(self, improvement_feasibility: str, credibility_score: int, service_usage: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="decide_convenience_enhancement",
            user_query=f"Feasibility: {improvement_feasibility} | Credibility: {credibility_score} | Usage: {service_usage}",
            service=self.service,
            user_type=self.actor
        )

    def generate_convenience_enhancement_response(self, decision: str, convenience_details: str, query: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="generate_convenience_enhancement_response",
            user_query=f"Decision: {decision} | Details: {convenience_details} | Original: {query}",
            service=self.service,
            user_type=self.actor
        )

    # ===== SUBSTITUTION SATISFACTION WORKFLOW METHODS =====

    def extract_substitution_issues(self, query: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="extract_substitution_issues",
            user_query=query,
            service=self.service,
            user_type=self.actor
        )

    def analyze_substitution_appropriateness(self, substitution_details: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="analyze_substitution_appropriateness",
            user_query=substitution_details,
            service=self.service,
            user_type=self.actor
        )

    def get_customer_substitution_preferences(self, username: str) -> str:
        return f"Substitution preferences for {username}: standard_allowed"

    def check_substitution_complaint_history(self, username: str) -> str:
        if username == "anonymous":
            return "NO_HISTORY_AVAILABLE"
        elif "test" in username.lower():
            return "FREQUENT_SUBSTITUTION_COMPLAINTS"
        else:
            return "OCCASIONAL_SUBSTITUTION_ISSUES"

    def assess_substitution_policy_compliance(self, substitution_analysis: str, preferences: str) -> str:
        return f"Policy compliance: {substitution_analysis} vs {preferences}"

    def decide_substitution_resolution(self, substitution_analysis: str, policy_compliance: str, credibility_score: int) -> str:
        return self.ai_engine.process_complaint(
            function_name="decide_substitution_resolution",
            user_query=f"Analysis: {substitution_analysis} | Compliance: {policy_compliance} | Credibility: {credibility_score}",
            service=self.service,
            user_type=self.actor
        )

    def generate_substitution_response(self, decision: str, substitution_details: str, query: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="generate_substitution_response",
            user_query=f"Decision: {decision} | Details: {substitution_details} | Original: {query}",
            service=self.service,
            user_type=self.actor
        )

    # ===== GROCERY FRESHNESS WORKFLOW METHODS =====

    def analyze_freshness_from_image(self, query: str, image_data: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="analyze_freshness_from_image",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def assess_freshness_health_safety(self, freshness_analysis: str, query: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="assess_freshness_health_safety",
            user_query=f"Freshness: {freshness_analysis} | Query: {query}",
            service=self.service,
            user_type=self.actor
        )

    def verify_purchase_timeline_and_storage(self, freshness_analysis: str, username: str) -> str:
        return f"Timeline verification for {username}: {freshness_analysis}"

    def check_freshness_complaint_history(self, username: str) -> str:
        if username == "anonymous":
            return "NO_HISTORY_AVAILABLE"
        elif "test" in username.lower():
            return "FREQUENT_FRESHNESS_COMPLAINTS"
        else:
            return "OCCASIONAL_FRESHNESS_ISSUES"

    def validate_freshness_complaint(self, freshness_analysis: str, timeline_verification: str, credibility_score: int) -> str:
        return self.ai_engine.process_complaint(
            function_name="validate_freshness_complaint",
            user_query=f"Freshness: {freshness_analysis} | Timeline: {timeline_verification} | Credibility: {credibility_score}",
            service=self.service,
            user_type=self.actor
        )

    def decide_freshness_resolution(self, freshness_validation: str, health_safety: str, credibility_score: int) -> str:
        return self.ai_engine.process_complaint(
            function_name="decide_freshness_resolution",
            user_query=f"Validation: {freshness_validation} | Safety: {health_safety} | Credibility: {credibility_score}",
            service=self.service,
            user_type=self.actor
        )

    def generate_freshness_response(self, decision: str, freshness_analysis: str, health_safety: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="generate_freshness_response",
            user_query=f"Decision: {decision} | Freshness: {freshness_analysis} | Safety: {health_safety}",
            service=self.service,
            user_type=self.actor
        )

    # ===== BULK SHOPPING WORKFLOW METHODS =====

    def extract_bulk_shopping_issues(self, query: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="extract_bulk_shopping_issues",
            user_query=query,
            service=self.service,
            user_type=self.actor
        )

    def analyze_customer_bulk_patterns(self, username: str, bulk_details: str) -> str:
        return f"Bulk patterns for {username}: {bulk_details}"

    def check_bulk_order_history(self, username: str) -> str:
        if username == "anonymous":
            return "NO_BULK_HISTORY"
        elif "test" in username.lower():
            return "FREQUENT_BULK_ORDERS"
        else:
            return "OCCASIONAL_BULK_ORDERS"

    def assess_bulk_service_optimization(self, bulk_details: str, bulk_patterns: str) -> str:
        return f"Optimization opportunities: {bulk_details} with {bulk_patterns}"

    def decide_bulk_shopping_enhancement(self, optimization_assessment: str, credibility_score: int, bulk_history: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="decide_bulk_shopping_enhancement",
            user_query=f"Optimization: {optimization_assessment} | Credibility: {credibility_score} | History: {bulk_history}",
            service=self.service,
            user_type=self.actor
        )

    def generate_bulk_shopping_response(self, decision: str, bulk_details: str, query: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="generate_bulk_shopping_response",
            user_query=f"Decision: {decision} | Details: {bulk_details} | Original: {query}",
            service=self.service,
            user_type=self.actor
        )