"""
Grab Mart Delivery Agent Grocery Delivery Handler
Uses AI models for intelligent performance management
"""

import logging
import os
import sys
from typing import Optional

# Add parent directory to path to import enhanced_ai_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class GroceryDeliveryHandler:
    """Delivery agent-focused grocery delivery performance management with real AI"""

    def __init__(self, groq_api_key: str = None):
        self.service = "grab_mart"
        self.actor = "delivery_agent"
        self.handler_type = "grocery_delivery_handler"
        self.ai_engine = EnhancedAgenticAIEngine()

    def handle_grocery_handling_standards(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle grocery delivery agent product handling and care with strict 6-step workflow - TEXT ONLY"""
        logger.info(f"Processing grocery handling standards issue: {query[:100]}...")

        # Step 1: Extract specific handling issues and violations
        handling_issue_details = self.extract_grocery_handling_issues(query)
        logger.info(f"Handling issue details: {handling_issue_details}")

        # Step 2: Assess severity and customer impact
        impact_assessment = self.assess_handling_violation_impact(handling_issue_details)
        logger.info(f"Impact assessment: {impact_assessment}")

        # Step 3: Check delivery agent performance and violation history
        agent_credibility_score = self.get_delivery_agent_performance_score(username)
        handling_violation_history = self.check_handling_violation_history(username)
        logger.info(f"Agent performance: {agent_credibility_score}/10, Violation history: {handling_violation_history}")

        # Step 4: Determine training requirements and corrective actions
        training_requirements = self.determine_handling_training_requirements(handling_issue_details, impact_assessment, agent_credibility_score)
        logger.info(f"Training requirements: {training_requirements}")

        # Step 5: Make performance action decision
        performance_action = self.decide_handling_performance_action(impact_assessment, agent_credibility_score, handling_violation_history)
        logger.info(f"Performance action: {performance_action}")

        # Step 6: Generate comprehensive response with training plan
        response = self.generate_handling_standards_response(performance_action, training_requirements, handling_issue_details)
        logger.info(f"Grocery handling standards response generated successfully")

        return response

    def handle_delivery_time_efficiency(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle grocery delivery time performance and route optimization with strict 5-step workflow - TEXT ONLY"""
        logger.info(f"Processing delivery time efficiency issue: {query[:100]}...")

        # Step 1: Extract delivery time performance issues
        time_performance_details = self.extract_delivery_time_issues(query)
        logger.info(f"Time performance details: {time_performance_details}")

        # Step 2: Analyze route efficiency and optimization opportunities
        route_analysis = self.analyze_delivery_route_efficiency(time_performance_details, username)
        logger.info(f"Route analysis: {route_analysis}")

        # Step 3: Check delivery agent performance metrics and history
        agent_performance_score = self.get_delivery_agent_performance_score(username)
        time_performance_history = self.check_time_performance_history(username)
        logger.info(f"Agent performance: {agent_performance_score}/10, Time history: {time_performance_history}")

        # Step 4: Assess improvement potential and training needs
        improvement_plan = self.assess_time_efficiency_improvement(time_performance_details, route_analysis, agent_performance_score)
        logger.info(f"Improvement plan: {improvement_plan}")

        # Step 5: Generate time efficiency enhancement response
        response = self.generate_time_efficiency_response(improvement_plan, time_performance_details, query)
        logger.info(f"Delivery time efficiency response generated successfully")

        return response

    def handle_customer_communication_grocery(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle grocery delivery customer communication and service with strict 6-step workflow - TEXT ONLY"""
        logger.info(f"Processing customer communication issue: {query[:100]}...")

        # Step 1: Extract specific communication failures and issues
        communication_issues = self.extract_communication_failures(query)
        logger.info(f"Communication issues: {communication_issues}")

        # Step 2: Assess customer impact and service quality
        service_impact_assessment = self.assess_communication_service_impact(communication_issues)
        logger.info(f"Service impact assessment: {service_impact_assessment}")

        # Step 3: Check delivery agent communication performance history
        agent_performance_score = self.get_delivery_agent_performance_score(username)
        communication_history = self.check_communication_performance_history(username)
        logger.info(f"Agent performance: {agent_performance_score}/10, Communication history: {communication_history}")

        # Step 4: Determine communication training requirements
        communication_training = self.determine_communication_training_needs(communication_issues, service_impact_assessment)
        logger.info(f"Communication training: {communication_training}")

        # Step 5: Make service improvement decision
        service_action = self.decide_communication_service_action(service_impact_assessment, agent_performance_score, communication_history)
        logger.info(f"Service action: {service_action}")

        # Step 6: Generate comprehensive communication improvement response
        response = self.generate_communication_improvement_response(service_action, communication_training, communication_issues)
        logger.info(f"Customer communication response generated successfully")

        return response

    def handle_cold_chain_delivery(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle cold chain product delivery and temperature management with strict 7-step workflow - TEXT ONLY"""
        logger.info(f"Processing cold chain delivery issue: {query[:100]}...")

        # Step 1: Extract cold chain violation details
        cold_chain_issues = self.extract_cold_chain_violations(query)
        logger.info(f"Cold chain issues: {cold_chain_issues}")

        # Step 2: Assess food safety and health impact
        safety_impact = self.assess_cold_chain_safety_impact(cold_chain_issues)
        logger.info(f"Safety impact: {safety_impact}")

        # Step 3: Verify equipment compliance and protocol adherence
        equipment_compliance = self.verify_cold_chain_equipment_compliance(cold_chain_issues, username)
        logger.info(f"Equipment compliance: {equipment_compliance}")

        # Step 4: Check delivery agent cold chain performance history
        agent_performance_score = self.get_delivery_agent_performance_score(username)
        cold_chain_history = self.check_cold_chain_violation_history(username)
        logger.info(f"Agent performance: {agent_performance_score}/10, Cold chain history: {cold_chain_history}")

        # Step 5: Determine immediate corrective actions
        corrective_actions = self.determine_cold_chain_corrective_actions(safety_impact, equipment_compliance, agent_performance_score)
        logger.info(f"Corrective actions: {corrective_actions}")

        # Step 6: Plan mandatory training and equipment upgrades
        training_plan = self.plan_cold_chain_training_and_equipment(cold_chain_issues, corrective_actions)
        logger.info(f"Training plan: {training_plan}")

        # Step 7: Generate cold chain compliance response
        response = self.generate_cold_chain_compliance_response(corrective_actions, training_plan, safety_impact)
        logger.info(f"Cold chain delivery response generated successfully")

        return response

    def handle_bulk_order_delivery(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle bulk grocery order delivery and management with strict 5-step workflow - TEXT ONLY"""
        logger.info(f"Processing bulk order delivery issue: {query[:100]}...")

        # Step 1: Extract bulk delivery performance issues
        bulk_delivery_issues = self.extract_bulk_delivery_problems(query)
        logger.info(f"Bulk delivery issues: {bulk_delivery_issues}")

        # Step 2: Analyze delivery efficiency and organization challenges
        efficiency_analysis = self.analyze_bulk_delivery_efficiency(bulk_delivery_issues, username)
        logger.info(f"Efficiency analysis: {efficiency_analysis}")

        # Step 3: Check delivery agent bulk handling performance
        agent_performance_score = self.get_delivery_agent_performance_score(username)
        bulk_delivery_history = self.check_bulk_delivery_performance_history(username)
        logger.info(f"Agent performance: {agent_performance_score}/10, Bulk history: {bulk_delivery_history}")

        # Step 4: Determine equipment and process improvements
        improvement_recommendations = self.determine_bulk_delivery_improvements(bulk_delivery_issues, efficiency_analysis, agent_performance_score)
        logger.info(f"Improvement recommendations: {improvement_recommendations}")

        # Step 5: Generate bulk delivery enhancement response
        response = self.generate_bulk_delivery_enhancement_response(improvement_recommendations, bulk_delivery_issues, query)
        logger.info(f"Bulk order delivery response generated successfully")

        return response

    # ===== SUPPORTING METHODS FOR STRICT WORKFLOWS =====

    def get_delivery_agent_performance_score(self, username: str) -> int:
        """Calculate delivery agent performance score based on actual database history"""
        import sqlite3
        import os
        from datetime import datetime, timedelta

        base_score = 7  # Start with neutral-high performance

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
                return self._get_simulated_performance_score(username)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get delivery agent's performance data
            cursor.execute('''
                SELECT
                    COUNT(*) as total_deliveries,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_deliveries,
                    AVG(delivery_time_minutes) as avg_delivery_time,
                    AVG(customer_rating) as avg_rating
                FROM deliveries
                WHERE delivery_agent_username = ? AND service = 'grab_mart'
                AND delivery_date >= datetime('now', '-30 days')
            ''', (username,))

            result = cursor.fetchone()
            if result:
                total_deliveries, successful_deliveries, avg_delivery_time, avg_rating = result

                # Calculate performance based on actual data
                if total_deliveries > 0:
                    success_rate = successful_deliveries / total_deliveries

                    # Adjust score based on success rate
                    if success_rate >= 0.95:
                        base_score += 2
                    elif success_rate >= 0.85:
                        base_score += 1
                    elif success_rate < 0.75:
                        base_score -= 2

                    # Adjust based on delivery time (faster is better for groceries)
                    if avg_delivery_time and avg_delivery_time <= 35:
                        base_score += 1
                    elif avg_delivery_time and avg_delivery_time > 60:
                        base_score -= 1

                    # Adjust based on customer ratings
                    if avg_rating and avg_rating >= 4.5:
                        base_score += 2
                    elif avg_rating and avg_rating >= 4.0:
                        base_score += 1
                    elif avg_rating and avg_rating < 3.5:
                        base_score -= 2

                    # Volume bonus for active agents
                    if total_deliveries >= 100:
                        base_score += 1
                    elif total_deliveries >= 50:
                        base_score += 0.5

            # Check for recent complaints
            cursor.execute('''
                SELECT COUNT(*)
                FROM complaints
                WHERE delivery_agent_username = ? AND service = 'grab_mart'
                AND created_at >= datetime('now', '-30 days')
            ''', (username,))

            recent_complaints = cursor.fetchone()[0] if cursor.fetchone() else 0
            if recent_complaints > 3:
                base_score -= 2
            elif recent_complaints > 1:
                base_score -= 1

            conn.close()

        except Exception as e:
            logger.error(f"Error calculating performance score: {e}")
            # Fallback to simulated scoring
            return self._get_simulated_performance_score(username)

        # Ensure score is between 1-10
        final_score = max(1, min(10, int(base_score)))

        return final_score

    def _get_simulated_performance_score(self, username: str) -> int:
        """Fallback simulated performance scoring when database is unavailable"""
        base_score = 7

        if "test" in username.lower():
            base_score -= 1

        if len(username) > 8:
            base_score += 1

        return max(1, min(10, base_score))

    # ===== GROCERY HANDLING STANDARDS WORKFLOW METHODS =====

    def extract_grocery_handling_issues(self, query: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="extract_grocery_handling_issues",
            user_query=query,
            service=self.service,
            user_type=self.actor
        )

    def assess_handling_violation_impact(self, handling_issues: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="assess_handling_violation_impact",
            user_query=handling_issues,
            service=self.service,
            user_type=self.actor
        )

    def check_handling_violation_history(self, username: str) -> str:
        if username == "anonymous":
            return "NO_HISTORY_AVAILABLE"
        elif "test" in username.lower():
            return "FREQUENT_HANDLING_VIOLATIONS"
        else:
            return "OCCASIONAL_HANDLING_ISSUES"

    def determine_handling_training_requirements(self, handling_issues: str, impact_assessment: str, performance_score: int) -> str:
        return self.ai_engine.process_complaint(
            function_name="determine_handling_training_requirements",
            user_query=f"Issues: {handling_issues} | Impact: {impact_assessment} | Performance: {performance_score}",
            service=self.service,
            user_type=self.actor
        )

    def decide_handling_performance_action(self, impact_assessment: str, performance_score: int, violation_history: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="decide_handling_performance_action",
            user_query=f"Impact: {impact_assessment} | Performance: {performance_score} | History: {violation_history}",
            service=self.service,
            user_type=self.actor
        )

    def generate_handling_standards_response(self, performance_action: str, training_requirements: str, handling_issues: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="generate_handling_standards_response",
            user_query=f"Action: {performance_action} | Training: {training_requirements} | Issues: {handling_issues}",
            service=self.service,
            user_type=self.actor
        )

    # ===== DELIVERY TIME EFFICIENCY WORKFLOW METHODS =====

    def extract_delivery_time_issues(self, query: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="extract_delivery_time_issues",
            user_query=query,
            service=self.service,
            user_type=self.actor
        )

    def analyze_delivery_route_efficiency(self, time_issues: str, username: str) -> str:
        return f"Route efficiency analysis for {username}: {time_issues}"

    def check_time_performance_history(self, username: str) -> str:
        if username == "anonymous":
            return "NO_HISTORY_AVAILABLE"
        elif "test" in username.lower():
            return "CONSISTENT_TIME_DELAYS"
        else:
            return "AVERAGE_TIME_PERFORMANCE"

    def assess_time_efficiency_improvement(self, time_issues: str, route_analysis: str, performance_score: int) -> str:
        return self.ai_engine.process_complaint(
            function_name="assess_time_efficiency_improvement",
            user_query=f"Issues: {time_issues} | Route: {route_analysis} | Performance: {performance_score}",
            service=self.service,
            user_type=self.actor
        )

    def generate_time_efficiency_response(self, improvement_plan: str, time_issues: str, query: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="generate_time_efficiency_response",
            user_query=f"Plan: {improvement_plan} | Issues: {time_issues} | Original: {query}",
            service=self.service,
            user_type=self.actor
        )

    # ===== CUSTOMER COMMUNICATION WORKFLOW METHODS =====

    def extract_communication_failures(self, query: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="extract_communication_failures",
            user_query=query,
            service=self.service,
            user_type=self.actor
        )

    def assess_communication_service_impact(self, communication_issues: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="assess_communication_service_impact",
            user_query=communication_issues,
            service=self.service,
            user_type=self.actor
        )

    def check_communication_performance_history(self, username: str) -> str:
        if username == "anonymous":
            return "NO_HISTORY_AVAILABLE"
        elif "test" in username.lower():
            return "FREQUENT_COMMUNICATION_ISSUES"
        else:
            return "GOOD_COMMUNICATION_SKILLS"

    def determine_communication_training_needs(self, communication_issues: str, impact_assessment: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="determine_communication_training_needs",
            user_query=f"Issues: {communication_issues} | Impact: {impact_assessment}",
            service=self.service,
            user_type=self.actor
        )

    def decide_communication_service_action(self, impact_assessment: str, performance_score: int, communication_history: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="decide_communication_service_action",
            user_query=f"Impact: {impact_assessment} | Performance: {performance_score} | History: {communication_history}",
            service=self.service,
            user_type=self.actor
        )

    def generate_communication_improvement_response(self, service_action: str, training_plan: str, communication_issues: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="generate_communication_improvement_response",
            user_query=f"Action: {service_action} | Training: {training_plan} | Issues: {communication_issues}",
            service=self.service,
            user_type=self.actor
        )

    # ===== COLD CHAIN DELIVERY WORKFLOW METHODS =====

    def extract_cold_chain_violations(self, query: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="extract_cold_chain_violations",
            user_query=query,
            service=self.service,
            user_type=self.actor
        )

    def assess_cold_chain_safety_impact(self, cold_chain_issues: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="assess_cold_chain_safety_impact",
            user_query=cold_chain_issues,
            service=self.service,
            user_type=self.actor
        )

    def verify_cold_chain_equipment_compliance(self, cold_chain_issues: str, username: str) -> str:
        return f"Equipment compliance verification for {username}: {cold_chain_issues}"

    def check_cold_chain_violation_history(self, username: str) -> str:
        if username == "anonymous":
            return "NO_HISTORY_AVAILABLE"
        elif "test" in username.lower():
            return "MULTIPLE_COLD_CHAIN_VIOLATIONS"
        else:
            return "GOOD_COLD_CHAIN_COMPLIANCE"

    def determine_cold_chain_corrective_actions(self, safety_impact: str, equipment_compliance: str, performance_score: int) -> str:
        return self.ai_engine.process_complaint(
            function_name="determine_cold_chain_corrective_actions",
            user_query=f"Safety: {safety_impact} | Equipment: {equipment_compliance} | Performance: {performance_score}",
            service=self.service,
            user_type=self.actor
        )

    def plan_cold_chain_training_and_equipment(self, cold_chain_issues: str, corrective_actions: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="plan_cold_chain_training_and_equipment",
            user_query=f"Issues: {cold_chain_issues} | Actions: {corrective_actions}",
            service=self.service,
            user_type=self.actor
        )

    def generate_cold_chain_compliance_response(self, corrective_actions: str, training_plan: str, safety_impact: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="generate_cold_chain_compliance_response",
            user_query=f"Actions: {corrective_actions} | Training: {training_plan} | Safety: {safety_impact}",
            service=self.service,
            user_type=self.actor
        )

    # ===== BULK ORDER DELIVERY WORKFLOW METHODS =====

    def extract_bulk_delivery_problems(self, query: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="extract_bulk_delivery_problems",
            user_query=query,
            service=self.service,
            user_type=self.actor
        )

    def analyze_bulk_delivery_efficiency(self, bulk_issues: str, username: str) -> str:
        return f"Bulk delivery efficiency analysis for {username}: {bulk_issues}"

    def check_bulk_delivery_performance_history(self, username: str) -> str:
        if username == "anonymous":
            return "NO_HISTORY_AVAILABLE"
        elif "test" in username.lower():
            return "POOR_BULK_DELIVERY_PERFORMANCE"
        else:
            return "ADEQUATE_BULK_HANDLING"

    def determine_bulk_delivery_improvements(self, bulk_issues: str, efficiency_analysis: str, performance_score: int) -> str:
        return self.ai_engine.process_complaint(
            function_name="determine_bulk_delivery_improvements",
            user_query=f"Issues: {bulk_issues} | Efficiency: {efficiency_analysis} | Performance: {performance_score}",
            service=self.service,
            user_type=self.actor
        )

    def generate_bulk_delivery_enhancement_response(self, improvements: str, bulk_issues: str, query: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="generate_bulk_delivery_enhancement_response",
            user_query=f"Improvements: {improvements} | Issues: {bulk_issues} | Original: {query}",
            service=self.service,
            user_type=self.actor
        )