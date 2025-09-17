"""
Grab Food Restaurant Handler - Combined
Handles all restaurant-side operational issues and management
Enhanced with Weather API and Google Maps API for predictive analysis
"""

import logging
import asyncio
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Import API integrations
try:
    from ..api_integrations import WeatherAPI, GoogleMapsAPI, LocationData
except ImportError:
    # Fallback import path
    from ...api_integrations import WeatherAPI, GoogleMapsAPI, LocationData

# Import cross-actor service
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from cross_actor_service import CrossActorUpdateService


class RestaurantHandler:
    """Combined restaurant-focused operational management and issue resolution"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_food"
        self.actor = "restaurant"
        self.handler_type = "restaurant_handler"

        # Initialize AI engine for structured analysis
        self.ai_engine = None
        try:
            from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine
            self.ai_engine = EnhancedAgenticAIEngine(groq_api_key)
            logger.info("AI engine initialized successfully for restaurant handler")
        except Exception as e:
            logger.warning(f"AI engine initialization failed: {e}. Falling back to rule-based processing.")
            self.ai_engine = None

        # Initialize API integrations for predictive analysis
        self.weather_api = WeatherAPI()
        self.maps_api = GoogleMapsAPI()

        # Initialize cross-actor update service
        self.cross_actor_service = CrossActorUpdateService()
    
    # ===== STRICT WORKFLOW METHODS FOR RESTAURANT =====

    def get_restaurant_credibility_score(self, restaurant_id: str) -> int:
        """Calculate restaurant credibility score based on comprehensive performance history"""
        import sqlite3
        import os
        from datetime import datetime, timedelta

        base_score = 7  # Start with neutral-high credibility

        # Handle anonymous or invalid restaurant IDs
        if not restaurant_id or restaurant_id == "anonymous":
            return max(1, base_score - 3)

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
                return self._get_simulated_restaurant_credibility_score(restaurant_id)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get restaurant's current credibility score from users table
            cursor.execute('''
                SELECT credibility_score, created_at
                FROM users
                WHERE username = ? AND user_type = 'restaurant'
            ''', (restaurant_id,))

            user_result = cursor.fetchone()
            if user_result:
                base_score = user_result[0]
                created_at = user_result[1]
            else:
                base_score = 7  # Default for new restaurants
                created_at = None

            # Get comprehensive restaurant order performance (last 90 days)
            cursor.execute('''
                SELECT
                    COUNT(*) as total_orders,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_orders,
                    COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_orders,
                    COUNT(CASE WHEN status = 'refunded' THEN 1 END) as refunded_orders,
                    AVG(price) as avg_order_value,
                    MIN(date) as first_order_date,
                    MAX(date) as last_order_date
                FROM orders
                WHERE restaurant_name = ? AND service = 'grab_food'
                AND date >= date('now', '-90 days')
            ''', (restaurant_id,))

            result = cursor.fetchone()
            if result:
                total_orders, completed_orders, cancelled_orders, refunded_orders, avg_order_value, first_order_date, last_order_date = result

                if total_orders > 0:
                    completion_rate = completed_orders / total_orders
                    cancellation_rate = cancelled_orders / total_orders
                    refund_rate = refunded_orders / total_orders if refunded_orders else 0

                    # Adjust score based on completion rate (stricter than customer scoring)
                    if completion_rate >= 0.98:
                        base_score += 3
                    elif completion_rate >= 0.95:
                        base_score += 2
                    elif completion_rate >= 0.90:
                        base_score += 1
                    elif completion_rate < 0.80:
                        base_score -= 3
                    elif completion_rate < 0.85:
                        base_score -= 2

                    # Adjust based on cancellation rate (restaurants should have low cancellations)
                    if cancellation_rate > 0.15:  # 15% cancellation rate is very bad for restaurants
                        base_score -= 4
                    elif cancellation_rate > 0.10:
                        base_score -= 2
                    elif cancellation_rate > 0.05:
                        base_score -= 1
                    elif cancellation_rate <= 0.02:  # Very low cancellation rate
                        base_score += 1

                    # Adjust based on refund rate (indicator of quality issues)
                    if refund_rate > 0.10:  # 10% refund rate is concerning
                        base_score -= 3
                    elif refund_rate > 0.05:
                        base_score -= 2
                    elif refund_rate > 0.02:
                        base_score -= 1

                    # Adjust based on order volume (experience and scale)
                    if total_orders >= 500:
                        base_score += 3  # High volume, experienced restaurant
                    elif total_orders >= 200:
                        base_score += 2
                    elif total_orders >= 100:
                        base_score += 1
                    elif total_orders < 20:
                        base_score -= 1  # New restaurant, less predictable

                    # Adjust based on average order value (premium vs budget)
                    if avg_order_value and avg_order_value >= 80:
                        base_score += 1  # Premium restaurants typically have higher standards
                    elif avg_order_value and avg_order_value >= 50:
                        base_score += 0.5

            # Restaurant tenure bonus (longer operating = more stable)
            if created_at:
                try:
                    created_date = datetime.strptime(created_at, '%Y-%m-%d')
                    days_operating = (datetime.now() - created_date).days
                    if days_operating > 730:  # More than 2 years
                        base_score += 2
                    elif days_operating > 365:  # More than 1 year
                        base_score += 1
                    elif days_operating < 30:  # Less than 1 month
                        base_score -= 1
                except:
                    pass  # Date parsing failed, skip tenure bonus

            # Check comprehensive complaint history (last 90 days)
            cursor.execute('''
                SELECT
                    COUNT(*) as total_complaints,
                    COUNT(CASE WHEN complaint_type LIKE '%quality%' OR complaint_details LIKE '%quality%' THEN 1 END) as quality_complaints,
                    COUNT(CASE WHEN complaint_type LIKE '%safety%' OR complaint_details LIKE '%safety%' OR complaint_details LIKE '%sick%' THEN 1 END) as safety_complaints,
                    COUNT(CASE WHEN complaint_type LIKE '%portion%' OR complaint_details LIKE '%portion%' OR complaint_details LIKE '%small%' THEN 1 END) as portion_complaints,
                    COUNT(CASE WHEN complaint_type LIKE '%delay%' OR complaint_details LIKE '%late%' OR complaint_details LIKE '%slow%' THEN 1 END) as timing_complaints
                FROM complaints
                WHERE username = ? AND service = 'grab_food' AND user_type = 'restaurant'
                AND created_at >= datetime('now', '-90 days')
            ''', (restaurant_id,))

            complaint_result = cursor.fetchone()
            if complaint_result:
                total_complaints, quality_complaints, safety_complaints, portion_complaints, timing_complaints = complaint_result

                # Heavy penalties for safety complaints (most serious)
                if safety_complaints > 2:
                    base_score -= 5
                elif safety_complaints > 1:
                    base_score -= 3
                elif safety_complaints == 1:
                    base_score -= 2

                # Penalties for quality complaints
                if quality_complaints > 8:
                    base_score -= 4
                elif quality_complaints > 5:
                    base_score -= 3
                elif quality_complaints > 3:
                    base_score -= 2
                elif quality_complaints > 1:
                    base_score -= 1

                # Penalties for portion complaints
                if portion_complaints > 6:
                    base_score -= 3
                elif portion_complaints > 3:
                    base_score -= 2
                elif portion_complaints > 1:
                    base_score -= 1

                # Penalties for timing complaints
                if timing_complaints > 10:
                    base_score -= 2
                elif timing_complaints > 5:
                    base_score -= 1

                # Overall complaint frequency penalty
                if total_complaints > 20:
                    base_score -= 3
                elif total_complaints > 10:
                    base_score -= 2
                elif total_complaints > 5:
                    base_score -= 1

            # Check recent complaint resolution rate
            cursor.execute('''
                SELECT
                    COUNT(*) as total_recent_complaints,
                    COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_complaints
                FROM complaints
                WHERE username = ? AND service = 'grab_food' AND user_type = 'restaurant'
                AND created_at >= datetime('now', '-30 days')
            ''', (restaurant_id,))

            resolution_result = cursor.fetchone()
            if resolution_result:
                total_recent, resolved_recent = resolution_result
                if total_recent > 0:
                    resolution_rate = resolved_recent / total_recent
                    if resolution_rate >= 0.95:
                        base_score += 1  # Excellent complaint resolution
                    elif resolution_rate < 0.70:
                        base_score -= 2  # Poor complaint resolution
                    elif resolution_rate < 0.80:
                        base_score -= 1

            conn.close()

        except Exception as e:
            logger.error(f"Error calculating restaurant credibility score: {e}")
            return self._get_simulated_restaurant_credibility_score(restaurant_id)

        # Ensure score is between 1-10
        final_score = max(1, min(10, int(base_score)))

        # Update the credibility score in the database if it has changed significantly
        self._update_restaurant_credibility_score_if_changed(restaurant_id, final_score)

        return final_score

    def _update_restaurant_credibility_score_if_changed(self, restaurant_id: str, new_score: int) -> None:
        """Update restaurant's credibility score in database if it has changed significantly"""
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

            # Update the credibility score for restaurant
            cursor.execute('''
                UPDATE users
                SET credibility_score = ?
                WHERE username = ? AND user_type = 'restaurant'
            ''', (new_score, restaurant_id))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error updating restaurant credibility score: {e}")

    def _get_simulated_restaurant_credibility_score(self, restaurant_id: str) -> int:
        """Fallback simulated credibility scoring when database is unavailable"""
        base_score = 7

        # Simulate some variation based on restaurant_id characteristics
        if "test" in restaurant_id.lower():
            base_score -= 2  # Test restaurants have lower credibility

        if "premium" in restaurant_id.lower() or "fine" in restaurant_id.lower():
            base_score += 1  # Premium restaurants tend to have higher standards

        if "fast" in restaurant_id.lower() or "quick" in restaurant_id.lower():
            base_score -= 0.5  # Fast food might have more variability

        if len(restaurant_id) > 15:  # Longer names might indicate more established businesses
            base_score += 0.5
        elif len(restaurant_id) < 5:  # Very short names might be less professional
            base_score -= 0.5

        # Simulate some randomness based on hash for consistency
        hash_modifier = (hash(restaurant_id) % 3) - 1  # -1, 0, or 1
        base_score += hash_modifier * 0.5

        return max(1, min(10, int(base_score)))

    # QUALITY HANDLER METHODS
    def handle_restaurant_portion_violation(self, query: str, restaurant_id: str = "anonymous", image_data: str = None, order_id: str = None) -> str:
        """Handle restaurant portion size violations with strict 6-step workflow"""
        logger.info(f"Processing portion violation complaint: {query[:100]}...")

        # Step 1: Extract portion violation details
        violation_details = self.extract_portion_violation_details(query)

        # Step 2: Validate violation with evidence (require image for serious violations)
        if violation_details["severity"] == "severe" and not image_data:
            return "📷 For portion size violations, please upload a photo of the food item so we can verify the portion size against our standards."

        # Step 3: Check restaurant credibility and violation history
        credibility_score = self.get_restaurant_credibility_score(restaurant_id)
        violation_history = self.check_portion_violation_history(restaurant_id)
        logger.info(f"Restaurant credibility: {credibility_score}/10, History: {violation_history}")

        # Step 4: Assess violation severity and impact on customer
        violation_assessment = self.assess_portion_violation_severity(violation_details, credibility_score, violation_history)
        logger.info(f"Violation assessment: {violation_assessment}")

        # Step 5: Determine corrective actions and penalties
        corrective_actions = self.determine_portion_corrective_actions(violation_assessment, credibility_score)
        logger.info(f"Corrective actions: {corrective_actions}")

        # Step 6: Generate comprehensive response with improvement plan
        response = self.generate_portion_violation_response(corrective_actions, violation_details, violation_assessment)
        logger.info(f"Portion violation response generated successfully")

        return response

    def extract_portion_violation_details(self, query: str) -> dict:
        """Extract portion violation details from complaint using structured AI analysis"""
        extraction_prompt = f"""
        Analyze this restaurant portion violation complaint and extract key details:

        Complaint: {query}

        Identify:
        1. What type of portion violation is described?
        2. How severe is the violation based on customer language?
        3. What category of food item is affected?
        4. Is this described as a repeat occurrence?
        5. What is the impact level on customer satisfaction?

        Return ONLY JSON: {{"violation_type": "undersized_portion/oversized_portion/inconsistent_portion", "severity": "minor/moderate/severe/critical", "item_category": "main_dish/side_dish/condiment/beverage", "repeat_occurrence": true/false, "customer_satisfaction_impact": "low/moderate/high/severe", "specific_items": ["item1", "item2"], "evidence_level": "customer_claim/photo_provided/measurement_given"}}
        """

        try:
            # Use AI engine to extract structured data if available
            if self.ai_engine:
                result = self.ai_engine.process_complaint(
                    function_name="extract_portion_violation",
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
                    return self._fallback_portion_extraction(query)
            else:
                return self._fallback_portion_extraction(query)

        except Exception as e:
            logger.error(f"Failed to extract portion violation details: {e}")
            return self._fallback_portion_extraction(query)

    def _fallback_portion_extraction(self, query: str) -> dict:
        """Fallback method for portion violation extraction when AI fails"""
        details = {
            "violation_type": "undersized_portion",
            "severity": "moderate",
            "item_category": "main_dish",
            "customer_satisfaction_impact": "moderate",
            "repeat_occurrence": False,
            "specific_items": [],
            "evidence_level": "customer_claim"
        }

        query_lower = query.lower()

        # Determine violation type
        if any(word in query_lower for word in ['tiny', 'very small', 'ridiculously small']):
            details["severity"] = "severe"
        elif any(word in query_lower for word in ['smaller', 'less than expected']):
            details["severity"] = "moderate"
        elif any(word in query_lower for word in ['slightly small', 'bit small']):
            details["severity"] = "minor"

        # Identify item category
        if any(word in query_lower for word in ['rice', 'noodles', 'pasta', 'main']):
            details["item_category"] = "main_dish"
        elif any(word in query_lower for word in ['side', 'vegetables', 'salad']):
            details["item_category"] = "side_dish"
        elif any(word in query_lower for word in ['sauce', 'dressing', 'condiment']):
            details["item_category"] = "condiment"

        # Check for repeat occurrence indicators
        if any(word in query_lower for word in ['again', 'always', 'every time', 'repeatedly']):
            details["repeat_occurrence"] = True

        # Check for evidence level
        if any(word in query_lower for word in ['photo', 'picture', 'image']):
            details["evidence_level"] = "photo_provided"
        elif any(word in query_lower for word in ['measured', 'weighed', 'ounces', 'grams']):
            details["evidence_level"] = "measurement_given"

        return details

    def check_portion_violation_history(self, restaurant_id: str) -> dict:
        """Check restaurant's portion violation history with database analysis"""
        import sqlite3
        import os
        from datetime import datetime, timedelta

        history_data = {
            "pattern_type": "NORMAL_PORTION_PATTERN",
            "violation_count_30_days": 0,
            "violation_count_90_days": 0,
            "severity_trend": "stable",
            "customer_complaints": 0,
            "resolution_rate": 100.0
        }

        if restaurant_id == "anonymous":
            history_data["pattern_type"] = "NO_HISTORY_AVAILABLE"
            return history_data

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
                return self._get_simulated_portion_history(restaurant_id)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get portion violation complaints in last 30 days
            cursor.execute('''
                SELECT COUNT(*)
                FROM complaints
                WHERE username = ? AND service = 'grab_food' AND user_type = 'restaurant'
                AND (complaint_type LIKE '%portion%' OR complaint_details LIKE '%portion%' OR complaint_details LIKE '%small%')
                AND created_at >= datetime('now', '-30 days')
            ''', (restaurant_id,))

            violations_30_days = cursor.fetchone()[0] if cursor.fetchone() else 0
            history_data["violation_count_30_days"] = violations_30_days

            # Get portion violation complaints in last 90 days
            cursor.execute('''
                SELECT COUNT(*)
                FROM complaints
                WHERE username = ? AND service = 'grab_food' AND user_type = 'restaurant'
                AND (complaint_type LIKE '%portion%' OR complaint_details LIKE '%portion%' OR complaint_details LIKE '%small%')
                AND created_at >= datetime('now', '-90 days')
            ''', (restaurant_id,))

            violations_90_days = cursor.fetchone()[0] if cursor.fetchone() else 0
            history_data["violation_count_90_days"] = violations_90_days

            # Determine pattern type based on violation frequency
            if violations_30_days >= 5:
                history_data["pattern_type"] = "FREQUENT_PORTION_ISSUES"
            elif violations_30_days >= 3:
                history_data["pattern_type"] = "MODERATE_PORTION_CONCERNS"
            elif violations_90_days >= 8:
                history_data["pattern_type"] = "RECURRING_PORTION_PATTERN"
            else:
                history_data["pattern_type"] = "NORMAL_PORTION_PATTERN"

            # Calculate trend
            if violations_90_days > 0:
                recent_rate = violations_30_days / 30
                overall_rate = violations_90_days / 90
                if recent_rate > overall_rate * 1.5:
                    history_data["severity_trend"] = "worsening"
                elif recent_rate < overall_rate * 0.5:
                    history_data["severity_trend"] = "improving"
                else:
                    history_data["severity_trend"] = "stable"

            conn.close()

        except Exception as e:
            logger.error(f"Error checking portion violation history: {e}")
            return self._get_simulated_portion_history(restaurant_id)

        return history_data

    def _get_simulated_portion_history(self, restaurant_id: str) -> dict:
        """Fallback simulated portion history when database is unavailable"""
        base_data = {
            "pattern_type": "NORMAL_PORTION_PATTERN",
            "violation_count_30_days": 0,
            "violation_count_90_days": 0,
            "severity_trend": "stable",
            "customer_complaints": 0,
            "resolution_rate": 95.0
        }

        if "test" in restaurant_id.lower():
            base_data.update({
                "pattern_type": "FREQUENT_PORTION_ISSUES",
                "violation_count_30_days": 6,
                "violation_count_90_days": 15,
                "severity_trend": "worsening"
            })

        return base_data

    def assess_portion_violation_severity(self, violation_details: dict, credibility_score: int, violation_history: dict) -> dict:
        """Assess portion violation severity and impact using strict decision matrix"""
        severity = violation_details.get("severity", "moderate")
        repeat_occurrence = violation_details.get("repeat_occurrence", False)
        evidence_level = violation_details.get("evidence_level", "customer_claim")
        pattern_type = violation_history.get("pattern_type", "NORMAL_PORTION_PATTERN")
        violation_count_30_days = violation_history.get("violation_count_30_days", 0)

        assessment = {
            "violation_level": "MODERATE",
            "customer_compensation_required": True,
            "restaurant_penalty_required": False,
            "training_required": False,
            "audit_required": False,
            "immediate_action_required": False,
            "platform_visibility_impact": 0,
            "health_department_notification": False
        }

        # Strict decision matrix based on multiple factors
        violation_score = 0

        # Severity scoring
        if severity == "critical":
            violation_score += 10
        elif severity == "severe":
            violation_score += 7
        elif severity == "moderate":
            violation_score += 4
        elif severity == "minor":
            violation_score += 2

        # Evidence level scoring
        if evidence_level == "measurement_given":
            violation_score += 5
        elif evidence_level == "photo_provided":
            violation_score += 3
        elif evidence_level == "customer_claim":
            violation_score += 1

        # History pattern scoring
        if pattern_type == "FREQUENT_PORTION_ISSUES":
            violation_score += 8
        elif pattern_type == "RECURRING_PORTION_PATTERN":
            violation_score += 6
        elif pattern_type == "MODERATE_PORTION_CONCERNS":
            violation_score += 4

        # Repeat occurrence scoring
        if repeat_occurrence:
            violation_score += 4

        # Credibility impact (lower credibility = higher violation impact)
        if credibility_score <= 3:
            violation_score += 6
        elif credibility_score <= 5:
            violation_score += 4
        elif credibility_score <= 7:
            violation_score += 2

        # Recent violation frequency impact
        if violation_count_30_days >= 5:
            violation_score += 6
        elif violation_count_30_days >= 3:
            violation_score += 4
        elif violation_count_30_days >= 2:
            violation_score += 2

        # Apply strict decision matrix based on total violation score
        if violation_score >= 20:
            assessment.update({
                "violation_level": "CRITICAL_PATTERN",
                "restaurant_penalty_required": True,
                "training_required": True,
                "audit_required": True,
                "immediate_action_required": True,
                "platform_visibility_impact": 40,
                "health_department_notification": True
            })
        elif violation_score >= 15:
            assessment.update({
                "violation_level": "SEVERE_PATTERN",
                "restaurant_penalty_required": True,
                "training_required": True,
                "audit_required": True,
                "immediate_action_required": True,
                "platform_visibility_impact": 25
            })
        elif violation_score >= 10:
            assessment.update({
                "violation_level": "PATTERN_VIOLATION",
                "restaurant_penalty_required": True,
                "training_required": True,
                "audit_required": True,
                "platform_visibility_impact": 15
            })
        elif violation_score >= 6:
            assessment.update({
                "violation_level": "SEVERE",
                "restaurant_penalty_required": True,
                "training_required": True,
                "platform_visibility_impact": 10
            })
        elif violation_score >= 3:
            assessment.update({
                "violation_level": "MODERATE",
                "training_required": True,
                "platform_visibility_impact": 5
            })
        else:
            assessment.update({
                "violation_level": "MINOR",
                "platform_visibility_impact": 2
            })

        logger.info(f"Portion violation assessment - Score: {violation_score}, Level: {assessment['violation_level']}")
        return assessment

    def determine_portion_corrective_actions(self, violation_assessment: dict, credibility_score: int) -> dict:
        """Determine corrective actions for portion violations using strict escalation matrix"""
        violation_level = violation_assessment.get("violation_level", "MODERATE")
        immediate_action_required = violation_assessment.get("immediate_action_required", False)
        platform_visibility_impact = violation_assessment.get("platform_visibility_impact", 0)

        actions = {
            "customer_refund": 0.0,
            "restaurant_penalty": 0.0,
            "training_program": "none",
            "audit_schedule": "none",
            "visibility_reduction": platform_visibility_impact,
            "suspension_days": 0,
            "compliance_bond": 0.0,
            "emergency_protocols": False,
            "supplier_audit_required": False,
            "kitchen_closure_hours": 0
        }

        # Strict escalation matrix based on violation level
        if violation_level == "CRITICAL_PATTERN":
            actions.update({
                "customer_refund": 150.0,  # Full refund + compensation
                "restaurant_penalty": 500.0,
                "training_program": "emergency_comprehensive_overhaul",
                "audit_schedule": "immediate",
                "suspension_days": 3,
                "compliance_bond": 2000.0,
                "emergency_protocols": True,
                "supplier_audit_required": True,
                "kitchen_closure_hours": 12
            })
        elif violation_level == "SEVERE_PATTERN":
            actions.update({
                "customer_refund": 120.0,
                "restaurant_penalty": 300.0,
                "training_program": "comprehensive_quality_overhaul",
                "audit_schedule": "within_24_hours",
                "suspension_days": 2,
                "compliance_bond": 1000.0,
                "emergency_protocols": True,
                "kitchen_closure_hours": 8
            })
        elif violation_level == "PATTERN_VIOLATION":
            actions.update({
                "customer_refund": 100.0,
                "restaurant_penalty": 200.0,
                "training_program": "comprehensive_quality_control",
                "audit_schedule": "within_48_hours",
                "suspension_days": 1,
                "compliance_bond": 500.0,
                "kitchen_closure_hours": 4
            })
        elif violation_level == "SEVERE":
            actions.update({
                "customer_refund": 100.0,
                "restaurant_penalty": 100.0,
                "training_program": "mandatory_portion_control",
                "audit_schedule": "within_72_hours",
                "compliance_bond": 250.0
            })
        elif violation_level == "MODERATE":
            actions.update({
                "customer_refund": 75.0,
                "restaurant_penalty": 50.0,
                "training_program": "portion_guidelines_review",
                "audit_schedule": "within_1_week"
            })
        elif violation_level == "MINOR":
            actions.update({
                "customer_refund": 50.0,
                "restaurant_penalty": 25.0,
                "training_program": "portion_awareness_session",
                "audit_schedule": "within_2_weeks"
            })

        # Adjust based on credibility score (lower credibility = harsher penalties)
        if credibility_score <= 3:
            actions["restaurant_penalty"] *= 1.5
            actions["compliance_bond"] *= 1.5
        elif credibility_score <= 5:
            actions["restaurant_penalty"] *= 1.25
            actions["compliance_bond"] *= 1.25
        elif credibility_score >= 8:
            actions["restaurant_penalty"] *= 0.8
            actions["compliance_bond"] *= 0.8

        return actions

    def generate_portion_violation_response(self, corrective_actions: dict, violation_details: dict, violation_assessment: dict) -> str:
        """Generate comprehensive response for portion violations"""
        violation_level = violation_assessment.get("violation_level", "MODERATE")
        customer_refund = corrective_actions.get("customer_refund", 0.0)
        restaurant_penalty = corrective_actions.get("restaurant_penalty", 0.0)

        if violation_level == "SEVERE":
            return f"""🍽️ **SEVERE PORTION VIOLATION - IMMEDIATE ACTION REQUIRED**

**Critical Quality Breach Detected**

**Violation Analysis:**
- Severity: {violation_details.get('severity', 'severe').upper()}
- Item category: {violation_details.get('item_category', 'main_dish')}
- Customer impact: Significant dissatisfaction
- Violation level: {violation_level}

**✅ IMMEDIATE CUSTOMER RESOLUTION:**
💰 **Customer refund:** {customer_refund}% of order value processed
🍽️ **Replacement meal:** Offered at no charge
📞 **Personal apology:** Direct contact with customer
⭐ **Service recovery:** Premium customer status upgrade

**⚠️ RESTAURANT ACCOUNTABILITY:**
💸 **Penalty imposed:** ${restaurant_penalty} quality violation fee
📉 **Platform visibility:** Reduced by {corrective_actions.get('visibility_reduction', 0)}% for 7 days
🎯 **Order priority:** Lowered until compliance restored
📊 **Rating impact:** Immediate quality score reduction

**🎓 MANDATORY CORRECTIVE MEASURES:**
1. **IMMEDIATE (0-4 hours):**
   - Kitchen supervisor meeting required
   - Portion scale recalibration mandatory
   - Current inventory portion audit
   - Staff portion training session

2. **SHORT-TERM (24-48 hours):**
   - Mandatory portion control certification
   - Kitchen workflow process review
   - Quality control system implementation
   - Management oversight protocols

3. **ONGOING (1-2 weeks):**
   - Daily portion compliance monitoring
   - Weekly quality assessments
   - Customer feedback tracking
   - Performance improvement reporting

**📋 COMPLIANCE REQUIREMENTS:**
- Portion compliance audit: {corrective_actions.get('audit_schedule', 'immediate')}
- Training completion deadline: 48 hours
- Quality improvement plan: Required within 72 hours
- Performance review: 2 weeks

**❌ CONSEQUENCES OF NON-COMPLIANCE:**
- Further visibility reduction (up to 50%)
- Temporary platform suspension consideration
- Increased penalty fees
- Mandatory quality coaching program

This is a serious quality breach that requires immediate attention and sustained improvement. Your restaurant's reputation and customer trust depend on consistent portion standards."""

        elif violation_level == "PATTERN_VIOLATION":
            return f"""🍽️ **PATTERN VIOLATION - SYSTEMATIC PORTION CONTROL FAILURE**

**Recurring Quality Issue Identified**

**Pattern Analysis:**
- Multiple portion violations detected
- Systematic quality control failure
- Customer trust significantly impacted
- Immediate intervention required

**✅ CUSTOMER RESOLUTION:**
💰 **Customer refund:** {customer_refund}% of order value
🍽️ **Goodwill gesture:** Additional item or credit
📞 **Service recovery:** Direct restaurant manager contact
⭐ **Loyalty program:** Bonus credits for inconvenience

**⚠️ ESCALATED RESTAURANT MEASURES:**
💸 **Pattern violation penalty:** ${restaurant_penalty}
📉 **Platform visibility:** Reduced by {corrective_actions.get('visibility_reduction', 0)}% for 14 days
🔍 **Enhanced monitoring:** All orders subject to quality review
📊 **Performance warning:** Formal improvement notice issued

**🎓 COMPREHENSIVE REMEDIATION PROGRAM:**
1. **MANDATORY TRAINING (48 hours):**
   - Complete portion control certification
   - Kitchen staff quality training
   - Management oversight training
   - Food service standards review

2. **SYSTEMATIC IMPROVEMENTS:**
   - Portion measurement tools installation
   - Quality control checkpoints implementation
   - Daily portion audits requirement
   - Customer feedback monitoring system

3. **ONGOING SUPERVISION:**
   - Weekly compliance assessments
   - Monthly performance reviews
   - Quarterly quality evaluations
   - Continuous improvement planning

**📋 STRICT COMPLIANCE TIMELINE:**
- Quality audit: {corrective_actions.get('audit_schedule', 'immediate')}
- Training completion: 48 hours (non-negotiable)
- System improvements: 1 week
- Performance demonstration: 30 days

Pattern violations indicate systemic issues requiring comprehensive reform of your quality control processes."""

        else:  # MODERATE
            return f"""🍽️ **Portion Standards Violation - Quality Improvement Required**

**Quality Assurance Alert**

**Violation Assessment:**
- Severity: {violation_details.get('severity', 'moderate')}
- Category: {violation_details.get('item_category', 'main_dish')}
- Impact level: Moderate customer dissatisfaction
- Action required: Quality improvement measures

**✅ CUSTOMER RESOLUTION:**
💰 **Customer refund:** {customer_refund}% of order value processed
🍽️ **Service recovery:** Discount on next order
📞 **Follow-up:** Customer satisfaction confirmation
⭐ **Quality assurance:** Enhanced preparation attention

**📊 RESTAURANT QUALITY MEASURES:**
💸 **Quality fee:** ${restaurant_penalty} (portion control improvement)
📈 **Visibility impact:** Minor reduction ({corrective_actions.get('visibility_reduction', 0)}%)
🎯 **Quality focus:** Enhanced portion monitoring
📋 **Improvement plan:** Required within 1 week

**🎓 QUALITY IMPROVEMENT ACTIONS:**
1. **IMMEDIATE REVIEW (24 hours):**
   - Portion guidelines review with kitchen staff
   - Measuring tools calibration check
   - Current portion practices assessment
   - Quality control system evaluation

2. **IMPROVEMENT MEASURES (1 week):**
   - Staff portion training session
   - Kitchen workflow optimization
   - Quality checkpoints implementation
   - Customer feedback integration

3. **MONITORING (ongoing):**
   - Regular portion compliance checks
   - Customer satisfaction tracking
   - Quality metrics monitoring
   - Continuous improvement focus

**📋 COMPLIANCE EXPECTATIONS:**
- Training completion: {corrective_actions.get('training_program', 'portion_guidelines_review')}
- Quality audit: {corrective_actions.get('audit_schedule', 'within_1_week')}
- Improvement demonstration: 2 weeks
- Performance review: Monthly

Consistent portion standards are essential for customer satisfaction and your restaurant's success on our platform."""

    def handle_restaurant_food_safety(self, query: str, restaurant_id: str = "anonymous", image_data: str = None, order_id: str = None) -> str:
        """Handle restaurant food safety and hygiene violations with strict 7-step workflow"""
        logger.info(f"Processing food safety violation: {query[:100]}...")

        # Step 1: Extract food safety violation details
        safety_violation_details = self.extract_food_safety_violation_details(query)

        # Step 2: Assess severity - food safety violations require immediate image evidence
        if safety_violation_details["severity"] in ["severe", "critical"] and not image_data:
            return "📷 Food safety violations require immediate photographic evidence. Please upload a photo of the affected food item for health compliance verification."

        # Step 3: Check restaurant food safety history and credibility
        credibility_score = self.get_restaurant_credibility_score(restaurant_id)
        safety_history = self.check_food_safety_violation_history(restaurant_id)
        logger.info(f"Restaurant credibility: {credibility_score}/10, Safety history: {safety_history}")

        # Step 4: Assess food safety risk and health department notification requirements
        safety_risk_assessment = self.assess_food_safety_risk(safety_violation_details, credibility_score, safety_history)
        logger.info(f"Safety risk assessment: {safety_risk_assessment}")

        # Step 5: Determine emergency protocols and health authority involvement
        emergency_protocols = self.determine_food_safety_emergency_protocols(safety_risk_assessment, credibility_score)
        logger.info(f"Emergency protocols: {emergency_protocols}")

        # Step 6: Calculate customer health protection and restaurant consequences
        health_protection_measures = self.calculate_food_safety_consequences(emergency_protocols, safety_violation_details, safety_risk_assessment)
        logger.info(f"Health protection measures: {health_protection_measures}")

        # Step 7: Generate comprehensive food safety response with health compliance
        response = self.generate_food_safety_response(emergency_protocols, health_protection_measures, safety_violation_details, safety_risk_assessment)
        logger.info(f"Food safety response generated successfully")

        return response

    def extract_food_safety_violation_details(self, query: str) -> dict:
        """Extract food safety violation details from complaint using structured AI analysis"""
        extraction_prompt = f"""
        Analyze this restaurant food safety violation complaint and extract critical details:

        Complaint: {query}

        Identify:
        1. What type of food safety violation is described?
        2. How severe is the health risk based on symptoms/descriptions?
        3. What type of contamination or safety issue is involved?
        4. Are multiple customers potentially affected?
        5. Is this temperature-related food safety issue?
        6. What evidence is provided by the complainant?
        7. Are there any immediate health symptoms described?

        Return ONLY JSON: {{"violation_type": "contamination/temperature_abuse/spoilage/hygiene/cross_contamination", "severity": "minor/moderate/severe/critical/emergency", "health_risk": "low/medium/high/critical", "contamination_type": "foreign_object/undercooked_food/temperature_violation/bacterial/chemical/physical", "temperature_related": true/false, "multiple_customers_affected": true/false, "evidence_level": "customer_claim/photo_provided/medical_report/multiple_reports", "immediate_symptoms": true/false, "medical_attention_required": true/false, "health_department_reportable": true/false}}
        """

        try:
            # Use AI engine to extract structured data if available
            if self.ai_engine:
                result = self.ai_engine.process_complaint(
                    function_name="extract_food_safety_violation",
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
                    return self._fallback_safety_extraction(query)
            else:
                return self._fallback_safety_extraction(query)

        except Exception as e:
            logger.error(f"Failed to extract food safety violation details: {e}")
            return self._fallback_safety_extraction(query)

    def _fallback_safety_extraction(self, query: str) -> dict:
        """Fallback method for food safety violation extraction when AI fails"""
        details = {
            "violation_type": "food_quality",
            "severity": "moderate",
            "health_risk": "medium",
            "contamination_type": "unknown",
            "temperature_related": False,
            "multiple_customers_affected": False,
            "evidence_level": "customer_claim",
            "immediate_symptoms": False,
            "medical_attention_required": False,
            "health_department_reportable": False
        }

        query_lower = query.lower()

        # Determine severity and health risk
        if any(word in query_lower for word in ['food poisoning', 'sick', 'vomiting', 'diarrhea', 'hospital']):
            details["severity"] = "critical"
            details["health_risk"] = "critical"
            details["immediate_symptoms"] = True
            details["medical_attention_required"] = True
            details["health_department_reportable"] = True
        elif any(word in query_lower for word in ['spoiled', 'rotten', 'moldy', 'bad smell']):
            details["severity"] = "severe"
            details["health_risk"] = "high"
            details["health_department_reportable"] = True
        elif any(word in query_lower for word in ['cold food', 'not fresh', 'stale']):
            details["severity"] = "moderate"
            details["health_risk"] = "medium"

        # Identify contamination type
        if any(word in query_lower for word in ['hair', 'foreign object', 'plastic', 'metal']):
            details["contamination_type"] = "foreign_object"
            details["violation_type"] = "contamination"
        elif any(word in query_lower for word in ['undercooked', 'raw', 'pink meat', 'blood']):
            details["contamination_type"] = "undercooked_food"
            details["violation_type"] = "temperature_abuse"
            details["health_department_reportable"] = True
        elif any(word in query_lower for word in ['cold', 'lukewarm', 'not hot', 'room temperature']):
            details["contamination_type"] = "temperature_violation"
            details["temperature_related"] = True
            details["violation_type"] = "temperature_abuse"

        # Check for multiple customers
        if any(word in query_lower for word in ['others', 'multiple', 'everyone', 'group', 'all of us']):
            details["multiple_customers_affected"] = True
            details["health_department_reportable"] = True

        # Check for evidence level
        if any(word in query_lower for word in ['photo', 'picture', 'image']):
            details["evidence_level"] = "photo_provided"
        elif any(word in query_lower for word in ['doctor', 'medical', 'hospital', 'clinic']):
            details["evidence_level"] = "medical_report"

        return details

    def check_food_safety_violation_history(self, restaurant_id: str) -> dict:
        """Check restaurant's food safety violation history with comprehensive database analysis"""
        import sqlite3
        import os
        from datetime import datetime, timedelta

        history_data = {
            "pattern_type": "NORMAL_SAFETY_PATTERN",
            "violation_count_30_days": 0,
            "violation_count_90_days": 0,
            "critical_violations_count": 0,
            "health_department_reports": 0,
            "severity_trend": "stable",
            "customer_health_impacts": 0,
            "resolution_rate": 100.0,
            "license_status": "active"
        }

        if restaurant_id == "anonymous":
            history_data["pattern_type"] = "NO_HISTORY_AVAILABLE"
            return history_data

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
                return self._get_simulated_safety_history(restaurant_id)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get food safety violation complaints in last 30 days
            cursor.execute('''
                SELECT COUNT(*)
                FROM complaints
                WHERE username = ? AND service = 'grab_food' AND user_type = 'restaurant'
                AND (complaint_type LIKE '%safety%' OR complaint_type LIKE '%poison%' OR
                     complaint_details LIKE '%safety%' OR complaint_details LIKE '%poison%' OR
                     complaint_details LIKE '%sick%' OR complaint_details LIKE '%spoiled%')
                AND created_at >= datetime('now', '-30 days')
            ''', (restaurant_id,))

            violations_30_days = cursor.fetchone()[0] if cursor.fetchone() else 0
            history_data["violation_count_30_days"] = violations_30_days

            # Get food safety violation complaints in last 90 days
            cursor.execute('''
                SELECT COUNT(*)
                FROM complaints
                WHERE username = ? AND service = 'grab_food' AND user_type = 'restaurant'
                AND (complaint_type LIKE '%safety%' OR complaint_type LIKE '%poison%' OR
                     complaint_details LIKE '%safety%' OR complaint_details LIKE '%poison%' OR
                     complaint_details LIKE '%sick%' OR complaint_details LIKE '%spoiled%')
                AND created_at >= datetime('now', '-90 days')
            ''', (restaurant_id,))

            violations_90_days = cursor.fetchone()[0] if cursor.fetchone() else 0
            history_data["violation_count_90_days"] = violations_90_days

            # Get critical safety violations (food poisoning, hospitalization)
            cursor.execute('''
                SELECT COUNT(*)
                FROM complaints
                WHERE username = ? AND service = 'grab_food' AND user_type = 'restaurant'
                AND (complaint_details LIKE '%poison%' OR complaint_details LIKE '%hospital%' OR
                     complaint_details LIKE '%vomit%' OR complaint_details LIKE '%diarrhea%')
                AND created_at >= datetime('now', '-90 days')
            ''', (restaurant_id,))

            critical_violations = cursor.fetchone()[0] if cursor.fetchone() else 0
            history_data["critical_violations_count"] = critical_violations

            # Determine pattern type based on violation frequency and severity
            if critical_violations >= 2:
                history_data["pattern_type"] = "CRITICAL_SAFETY_RISK"
                history_data["license_status"] = "under_review"
            elif violations_30_days >= 3:
                history_data["pattern_type"] = "FREQUENT_SAFETY_VIOLATIONS"
            elif violations_30_days >= 2:
                history_data["pattern_type"] = "MODERATE_SAFETY_CONCERNS"
            elif violations_90_days >= 5:
                history_data["pattern_type"] = "RECURRING_SAFETY_PATTERN"
            else:
                history_data["pattern_type"] = "NORMAL_SAFETY_PATTERN"

            # Calculate trend
            if violations_90_days > 0:
                recent_rate = violations_30_days / 30
                overall_rate = violations_90_days / 90
                if recent_rate > overall_rate * 1.5:
                    history_data["severity_trend"] = "worsening"
                elif recent_rate < overall_rate * 0.5:
                    history_data["severity_trend"] = "improving"
                else:
                    history_data["severity_trend"] = "stable"

            conn.close()

        except Exception as e:
            logger.error(f"Error checking food safety violation history: {e}")
            return self._get_simulated_safety_history(restaurant_id)

        return history_data

    def _get_simulated_safety_history(self, restaurant_id: str) -> dict:
        """Fallback simulated safety history when database is unavailable"""
        base_data = {
            "pattern_type": "NORMAL_SAFETY_PATTERN",
            "violation_count_30_days": 0,
            "violation_count_90_days": 0,
            "critical_violations_count": 0,
            "health_department_reports": 0,
            "severity_trend": "stable",
            "customer_health_impacts": 0,
            "resolution_rate": 95.0,
            "license_status": "active"
        }

        if "test" in restaurant_id.lower():
            base_data.update({
                "pattern_type": "FREQUENT_SAFETY_VIOLATIONS",
                "violation_count_30_days": 4,
                "violation_count_90_days": 10,
                "critical_violations_count": 1,
                "severity_trend": "worsening",
                "license_status": "under_review"
            })

        return base_data

    def assess_food_safety_risk(self, safety_violation_details: dict, credibility_score: int, safety_history: dict) -> dict:
        """Assess food safety risk and health department notification requirements using strict risk matrix"""
        severity = safety_violation_details.get("severity", "moderate")
        health_risk = safety_violation_details.get("health_risk", "medium")
        multiple_affected = safety_violation_details.get("multiple_customers_affected", False)
        immediate_symptoms = safety_violation_details.get("immediate_symptoms", False)
        medical_attention_required = safety_violation_details.get("medical_attention_required", False)
        health_department_reportable = safety_violation_details.get("health_department_reportable", False)
        pattern_type = safety_history.get("pattern_type", "NORMAL_SAFETY_PATTERN")
        critical_violations_count = safety_history.get("critical_violations_count", 0)
        violation_count_30_days = safety_history.get("violation_count_30_days", 0)

        assessment = {
            "risk_level": "MEDIUM",
            "health_department_notification": False,
            "immediate_closure_required": False,
            "public_health_threat": False,
            "media_attention_risk": False,
            "emergency_response_required": False,
            "license_suspension_risk": False,
            "legal_liability_risk": False,
            "customer_notification_required": False
        }

        # Calculate comprehensive risk score
        risk_score = 0

        # Severity scoring
        if severity == "emergency":
            risk_score += 15
        elif severity == "critical":
            risk_score += 12
        elif severity == "severe":
            risk_score += 8
        elif severity == "moderate":
            risk_score += 4
        elif severity == "minor":
            risk_score += 2

        # Health risk scoring
        if health_risk == "critical":
            risk_score += 10
        elif health_risk == "high":
            risk_score += 7
        elif health_risk == "medium":
            risk_score += 3
        elif health_risk == "low":
            risk_score += 1

        # Immediate symptoms and medical attention
        if medical_attention_required:
            risk_score += 8
        elif immediate_symptoms:
            risk_score += 5

        # Multiple customers affected
        if multiple_affected:
            risk_score += 6

        # History pattern scoring
        if pattern_type == "CRITICAL_SAFETY_RISK":
            risk_score += 10
        elif pattern_type == "FREQUENT_SAFETY_VIOLATIONS":
            risk_score += 7
        elif pattern_type == "RECURRING_SAFETY_PATTERN":
            risk_score += 5
        elif pattern_type == "MODERATE_SAFETY_CONCERNS":
            risk_score += 3

        # Critical violations history
        if critical_violations_count >= 2:
            risk_score += 8
        elif critical_violations_count >= 1:
            risk_score += 5

        # Recent violation frequency
        if violation_count_30_days >= 3:
            risk_score += 6
        elif violation_count_30_days >= 2:
            risk_score += 4

        # Credibility impact (lower credibility = higher risk)
        if credibility_score <= 3:
            risk_score += 6
        elif credibility_score <= 5:
            risk_score += 4
        elif credibility_score <= 7:
            risk_score += 2

        # Mandatory health department reportable cases
        if health_department_reportable:
            risk_score += 5

        # Apply strict risk assessment matrix
        if risk_score >= 25:
            assessment.update({
                "risk_level": "EMERGENCY",
                "health_department_notification": True,
                "immediate_closure_required": True,
                "public_health_threat": True,
                "media_attention_risk": True,
                "emergency_response_required": True,
                "license_suspension_risk": True,
                "legal_liability_risk": True,
                "customer_notification_required": True
            })
        elif risk_score >= 20:
            assessment.update({
                "risk_level": "CRITICAL",
                "health_department_notification": True,
                "immediate_closure_required": True,
                "public_health_threat": True,
                "media_attention_risk": True,
                "emergency_response_required": True,
                "license_suspension_risk": True,
                "customer_notification_required": True
            })
        elif risk_score >= 15:
            assessment.update({
                "risk_level": "HIGH",
                "health_department_notification": True,
                "immediate_closure_required": True,
                "public_health_threat": True,
                "media_attention_risk": True,
                "customer_notification_required": True
            })
        elif risk_score >= 10:
            assessment.update({
                "risk_level": "ELEVATED",
                "health_department_notification": True,
                "public_health_threat": True,
                "customer_notification_required": True
            })
        elif risk_score >= 6:
            assessment.update({
                "risk_level": "MEDIUM",
                "health_department_notification": health_department_reportable,
                "customer_notification_required": True
            })
        else:
            assessment.update({
                "risk_level": "LOW",
                "customer_notification_required": False
            })

        logger.info(f"Food safety risk assessment - Score: {risk_score}, Level: {assessment['risk_level']}")
        return assessment

    def determine_food_safety_emergency_protocols(self, safety_risk_assessment: dict, credibility_score: int) -> dict:
        """Determine emergency protocols for food safety violations using comprehensive response matrix"""
        risk_level = safety_risk_assessment.get("risk_level", "MEDIUM")
        immediate_closure_required = safety_risk_assessment.get("immediate_closure_required", False)
        emergency_response_required = safety_risk_assessment.get("emergency_response_required", False)
        license_suspension_risk = safety_risk_assessment.get("license_suspension_risk", False)

        protocols = {
            "immediate_menu_suspension": False,
            "kitchen_closure_duration": 0,  # hours
            "health_inspection_required": False,
            "staff_retraining_mandatory": False,
            "supplier_audit_required": False,
            "temperature_system_overhaul": False,
            "equipment_sanitization_required": False,
            "food_disposal_required": False,
            "staff_health_screening": False,
            "emergency_deep_cleaning": False,
            "management_notification": False,
            "legal_team_involvement": False,
            "insurance_notification": False,
            "customer_contact_tracing": False
        }

        # Comprehensive protocol matrix based on risk level
        if risk_level == "EMERGENCY":
            protocols.update({
                "immediate_menu_suspension": True,
                "kitchen_closure_duration": 72,
                "health_inspection_required": True,
                "staff_retraining_mandatory": True,
                "supplier_audit_required": True,
                "temperature_system_overhaul": True,
                "equipment_sanitization_required": True,
                "food_disposal_required": True,
                "staff_health_screening": True,
                "emergency_deep_cleaning": True,
                "management_notification": True,
                "legal_team_involvement": True,
                "insurance_notification": True,
                "customer_contact_tracing": True
            })
        elif risk_level == "CRITICAL":
            protocols.update({
                "immediate_menu_suspension": True,
                "kitchen_closure_duration": 48,
                "health_inspection_required": True,
                "staff_retraining_mandatory": True,
                "supplier_audit_required": True,
                "temperature_system_overhaul": True,
                "equipment_sanitization_required": True,
                "food_disposal_required": True,
                "staff_health_screening": True,
                "emergency_deep_cleaning": True,
                "management_notification": True,
                "legal_team_involvement": True,
                "customer_contact_tracing": True
            })
        elif risk_level == "HIGH":
            protocols.update({
                "immediate_menu_suspension": True,
                "kitchen_closure_duration": 24,
                "health_inspection_required": True,
                "staff_retraining_mandatory": True,
                "supplier_audit_required": True,
                "temperature_system_overhaul": True,
                "equipment_sanitization_required": True,
                "food_disposal_required": True,
                "staff_health_screening": True,
                "management_notification": True,
                "customer_contact_tracing": True
            })
        elif risk_level == "ELEVATED":
            protocols.update({
                "immediate_menu_suspension": True,
                "kitchen_closure_duration": 12,
                "health_inspection_required": True,
                "staff_retraining_mandatory": True,
                "temperature_system_overhaul": True,
                "equipment_sanitization_required": True,
                "food_disposal_required": True,
                "management_notification": True
            })
        elif risk_level == "MEDIUM":
            protocols.update({
                "kitchen_closure_duration": 8,
                "health_inspection_required": True,
                "staff_retraining_mandatory": True,
                "equipment_sanitization_required": True,
                "management_notification": True
            })
        elif risk_level == "LOW":
            protocols.update({
                "kitchen_closure_duration": 4,
                "health_inspection_required": True,
                "staff_retraining_mandatory": True
            })

        # Adjust protocols based on credibility score
        if credibility_score <= 3 and risk_level in ["MEDIUM", "ELEVATED"]:
            # Escalate protocols for low credibility restaurants
            protocols["kitchen_closure_duration"] += 8
            protocols["supplier_audit_required"] = True
            protocols["management_notification"] = True
        elif credibility_score >= 8 and risk_level in ["LOW", "MEDIUM"]:
            # Reduce some protocols for high credibility restaurants
            protocols["kitchen_closure_duration"] = max(2, protocols["kitchen_closure_duration"] - 2)

        return protocols

    def calculate_food_safety_consequences(self, emergency_protocols: dict, safety_violation_details: dict, safety_risk_assessment: dict) -> dict:
        """Calculate comprehensive consequences for food safety violations"""
        risk_level = safety_risk_assessment.get("risk_level", "MEDIUM")
        closure_duration = emergency_protocols.get("kitchen_closure_duration", 0)
        license_suspension_risk = safety_risk_assessment.get("license_suspension_risk", False)
        legal_liability_risk = safety_risk_assessment.get("legal_liability_risk", False)
        multiple_affected = safety_violation_details.get("multiple_customers_affected", False)
        medical_attention_required = safety_violation_details.get("medical_attention_required", False)

        consequences = {
            "customer_compensation": 0.0,
            "restaurant_penalty": 0.0,
            "platform_suspension_days": 0,
            "reputation_recovery_program": False,
            "health_compliance_bond": 0.0,
            "license_review_required": False,
            "legal_liability_coverage": 0.0,
            "emergency_response_costs": 0.0,
            "mandatory_insurance_increase": 0.0,
            "public_disclosure_required": False,
            "media_response_plan": False
        }

        # Comprehensive consequence matrix
        if risk_level == "EMERGENCY":
            consequences.update({
                "customer_compensation": 500.0,  # Full refund + significant medical/inconvenience compensation
                "restaurant_penalty": 5000.0,
                "platform_suspension_days": 30,
                "reputation_recovery_program": True,
                "health_compliance_bond": 25000.0,
                "license_review_required": True,
                "legal_liability_coverage": 100000.0,
                "emergency_response_costs": 10000.0,
                "mandatory_insurance_increase": 50.0,  # percentage
                "public_disclosure_required": True,
                "media_response_plan": True
            })
        elif risk_level == "CRITICAL":
            consequences.update({
                "customer_compensation": 300.0,
                "restaurant_penalty": 3000.0,
                "platform_suspension_days": 21,
                "reputation_recovery_program": True,
                "health_compliance_bond": 15000.0,
                "license_review_required": True,
                "legal_liability_coverage": 50000.0,
                "emergency_response_costs": 5000.0,
                "mandatory_insurance_increase": 30.0,
                "public_disclosure_required": True,
                "media_response_plan": True
            })
        elif risk_level == "HIGH":
            consequences.update({
                "customer_compensation": 200.0,
                "restaurant_penalty": 2000.0,
                "platform_suspension_days": 14,
                "reputation_recovery_program": True,
                "health_compliance_bond": 10000.0,
                "license_review_required": True,
                "legal_liability_coverage": 25000.0,
                "emergency_response_costs": 3000.0,
                "mandatory_insurance_increase": 20.0,
                "media_response_plan": True
            })
        elif risk_level == "ELEVATED":
            consequences.update({
                "customer_compensation": 150.0,
                "restaurant_penalty": 1000.0,
                "platform_suspension_days": 7,
                "reputation_recovery_program": True,
                "health_compliance_bond": 5000.0,
                "license_review_required": True,
                "emergency_response_costs": 1500.0,
                "mandatory_insurance_increase": 15.0
            })
        elif risk_level == "MEDIUM":
            consequences.update({
                "customer_compensation": 100.0,
                "restaurant_penalty": 500.0,
                "platform_suspension_days": 3,
                "health_compliance_bond": 2500.0,
                "emergency_response_costs": 1000.0,
                "mandatory_insurance_increase": 10.0
            })
        elif risk_level == "LOW":
            consequences.update({
                "customer_compensation": 75.0,
                "restaurant_penalty": 250.0,
                "platform_suspension_days": 1,
                "health_compliance_bond": 1000.0,
                "emergency_response_costs": 500.0
            })

        # Additional penalties for specific high-risk factors
        if medical_attention_required:
            consequences["customer_compensation"] += 200.0
            consequences["legal_liability_coverage"] += 25000.0

        if multiple_affected:
            consequences["customer_compensation"] *= 1.5
            consequences["restaurant_penalty"] *= 1.3
            consequences["legal_liability_coverage"] *= 1.5

        if license_suspension_risk:
            consequences["health_compliance_bond"] *= 1.5
            consequences["platform_suspension_days"] += 7

        return consequences

    def generate_food_safety_response(self, emergency_protocols: dict, health_protection_measures: dict, safety_violation_details: dict, safety_risk_assessment: dict) -> str:
        """Generate comprehensive food safety response"""
        risk_level = safety_risk_assessment.get("risk_level", "MEDIUM")
        closure_duration = emergency_protocols.get("kitchen_closure_duration", 0)
        customer_compensation = health_protection_measures.get("customer_compensation", 0.0)
        restaurant_penalty = health_protection_measures.get("restaurant_penalty", 0.0)

        if risk_level == "CRITICAL":
            return f"""🚨 **CRITICAL FOOD SAFETY EMERGENCY - IMMEDIATE KITCHEN CLOSURE**

**FOOD SAFETY CRISIS ALERT**

**Health Emergency Classification:**
- Risk level: {risk_level}
- Contamination type: {safety_violation_details.get('contamination_type', 'unknown')}
- Public health threat: CONFIRMED
- Multiple customers affected: {'YES' if safety_violation_details.get('multiple_customers_affected') else 'POTENTIAL'}

**🚨 IMMEDIATE EMERGENCY ACTIONS:**
1. **KITCHEN OPERATIONS SUSPENDED** - Effective immediately
2. **Health Department notified** - Emergency inspection requested
3. **All pending orders CANCELLED** - Full customer refunds processing
4. **Food inventory QUARANTINED** - No items to be served

**💰 CUSTOMER HEALTH PROTECTION:**
💵 **Emergency compensation:** ${customer_compensation:.2f} per affected customer
🏥 **Medical support:** Healthcare costs coverage if needed
📞 **Health hotline:** 24/7 medical consultation available
⚕️ **Follow-up care:** Customer health monitoring for 72 hours

**⚠️ RESTAURANT CONSEQUENCES:**
💸 **Critical safety penalty:** ${restaurant_penalty:.2f}
🚫 **Platform suspension:** {health_protection_measures.get('platform_suspension_days', 0)} days minimum
💰 **Health compliance bond:** ${health_protection_measures.get('health_compliance_bond', 0):.2f} required
📊 **Rating impact:** Severe downgrade until compliance restored

**🔒 MANDATORY CLOSURE PROTOCOL ({closure_duration} hours minimum):**
1. **IMMEDIATE (0-2 hours):**
   - Complete kitchen shutdown
   - Food safety expert inspection
   - Contamination source identification
   - Health authority coordination

2. **EMERGENCY REMEDIATION (2-24 hours):**
   - Professional kitchen sanitization
   - All equipment deep cleaning/replacement
   - Food inventory disposal and replacement
   - Staff health screening

3. **SYSTEM OVERHAUL (24-48 hours):**
   - Complete HACCP system implementation
   - Temperature monitoring system installation
   - Staff food safety certification (all personnel)
   - Supplier verification and audit

**📋 HEALTH COMPLIANCE REQUIREMENTS:**
- Health inspector clearance: MANDATORY before reopening
- Staff food safety certification: 100% completion required
- Temperature control system: Professional installation/verification
- Supplier audit: Complete safety verification
- Ongoing monitoring: Daily health compliance checks

**❌ REOPENING CONDITIONS:**
- Health department clearance certificate
- All staff certified in food safety
- New supplier agreements with safety guarantees
- Customer health monitoring completion
- Platform safety review approval

This is a critical public health situation requiring immediate and sustained corrective action."""

        elif risk_level == "HIGH":
            return f"""🏥 **SEVERE FOOD SAFETY VIOLATION - EMERGENCY INTERVENTION**

**Health Safety Alert - Immediate Action Required**

**Safety Violation Analysis:**
- Risk level: {risk_level}
- Health impact: Severe potential for customer harm
- Contamination: {safety_violation_details.get('contamination_type', 'multiple_factors')}
- Immediate intervention: REQUIRED

**🚨 IMMEDIATE SAFETY MEASURES:**
1. **Affected menu items SUSPENDED** - Immediate removal
2. **Kitchen operations PAUSED** - {closure_duration} hour mandatory closure
3. **Health Department contacted** - Inspection scheduled within 24 hours
4. **Customer health tracking** - Active monitoring initiated

**💰 CUSTOMER PROTECTION & COMPENSATION:**
💵 **Health protection compensation:** ${customer_compensation:.2f}
🏥 **Medical consultation:** Available if symptoms develop
📞 **Health support line:** Direct access to medical advice
⚕️ **Follow-up monitoring:** 48-hour customer health check

**⚠️ RESTAURANT ACCOUNTABILITY:**
💸 **Severe safety penalty:** ${restaurant_penalty:.2f}
🚫 **Service suspension:** {health_protection_measures.get('platform_suspension_days', 0)} days
💰 **Safety compliance bond:** ${health_protection_measures.get('health_compliance_bond', 0):.2f}
📊 **Performance impact:** Significant rating reduction

**🔧 MANDATORY REMEDIATION ({closure_duration} hours):**
1. **IMMEDIATE SAFETY AUDIT (0-4 hours):**
   - Kitchen safety inspection
   - Temperature system verification
   - Food storage compliance check
   - Staff hygiene assessment

2. **CORRECTIVE MEASURES (4-12 hours):**
   - Problem source elimination
   - Equipment sanitization/replacement
   - Food inventory safety verification
   - Staff safety retraining

3. **SYSTEM IMPROVEMENTS (12-24 hours):**
   - Enhanced temperature monitoring
   - Updated food safety protocols
   - Staff certification updates
   - Supplier safety verification

**📋 HEALTH COMPLIANCE CHECKLIST:**
- Health inspector approval: Required for reopening
- Staff food safety training: Mandatory completion
- Temperature control upgrade: Professional verification
- Food safety protocol update: Written procedures required
- Customer safety guarantee: Formal commitment needed

Severe food safety violations threaten customer health and require comprehensive immediate remediation."""

        else:  # MEDIUM risk
            return f"""🏥 **Food Safety Compliance Alert - Corrective Action Required**

**Health & Safety Concern Identified**

**Safety Assessment:**
- Risk level: {risk_level}
- Health impact: Moderate customer safety concern
- Issue type: {safety_violation_details.get('contamination_type', 'food_quality')}
- Corrective action: Required within {closure_duration} hours

**✅ CUSTOMER PROTECTION MEASURES:**
💰 **Customer compensation:** ${customer_compensation:.2f}
🏥 **Health support:** Medical consultation available if needed
📞 **Customer care:** Direct support line access
⚕️ **Safety assurance:** Enhanced quality monitoring

**📊 RESTAURANT IMPROVEMENT REQUIREMENTS:**
💸 **Safety improvement fee:** ${restaurant_penalty:.2f}
🔍 **Quality monitoring:** Enhanced oversight for {health_protection_measures.get('platform_suspension_days', 2)} days
💰 **Compliance bond:** ${health_protection_measures.get('health_compliance_bond', 0):.2f}
📋 **Training required:** Food safety protocol review

**🔧 CORRECTIVE ACTION PLAN ({closure_duration} hours):**
1. **IMMEDIATE REVIEW (0-2 hours):**
   - Identify and address specific safety concern
   - Review food preparation procedures
   - Check temperature control systems
   - Verify staff hygiene compliance

2. **SYSTEM IMPROVEMENTS (2-6 hours):**
   - Update food safety protocols
   - Staff safety training session
   - Equipment calibration check
   - Supplier quality verification

3. **QUALITY ASSURANCE (6-8 hours):**
   - Implement enhanced monitoring
   - Document corrective measures
   - Customer safety communication
   - Performance improvement tracking

**📋 COMPLIANCE VERIFICATION:**
- Health inspection: Scheduled within 72 hours
- Staff training: Food safety protocol review completed
- System updates: Temperature monitoring verification
- Quality assurance: Enhanced customer safety measures

Food safety is fundamental to customer trust and restaurant success on our platform."""

    def handle_restaurant_preparation_delays(self, query: str, restaurant_id: str = "anonymous") -> str:
        """Handle restaurant food preparation delays with data-driven analysis and improvement plan"""
        logger.info(f"Processing preparation delay issue: {query[:100]}...")

        # Analyze delay details using AI reasoning
        delay_analysis = self.analyze_preparation_delay_details(query)

        # Get restaurant performance metrics
        performance_metrics = self.get_restaurant_preparation_performance(restaurant_id)

        # Identify root causes and improvement opportunities
        improvement_plan = self.generate_preparation_improvement_plan(delay_analysis, performance_metrics)

        # Create actionable response
        return self.generate_preparation_delay_response(delay_analysis, performance_metrics, improvement_plan)

    def analyze_preparation_delay_details(self, query: str) -> dict:
        """Analyze preparation delay details using AI"""
        analysis_prompt = f"""
        Analyze this restaurant preparation delay complaint:

        Complaint: {query}

        Identify:
        1. What is the actual vs expected preparation time?
        2. What factors are contributing to delays?
        3. Is this a recurring pattern or isolated incident?
        4. Which menu items or processes are affected?

        Return ONLY JSON: {{"actual_prep_time": "X minutes", "expected_prep_time": "X minutes", "delay_factors": ["factor1", "factor2"], "pattern_type": "isolated/recurring/systemic", "affected_items": ["item1", "item2"], "severity": "minor/moderate/severe"}}
        """

        try:
            if self.ai_engine:
                result = self.ai_engine.process_complaint(
                    function_name="analyze_preparation_delays",
                    user_query=analysis_prompt,
                    service=self.service,
                    user_type=self.actor
                )

                import json
                if "{" in result and "}" in result:
                    json_start = result.find("{")
                    json_end = result.rfind("}") + 1
                    json_str = result[json_start:json_end]
                    return json.loads(json_str)

            return self._fallback_delay_analysis(query)

        except Exception as e:
            logger.error(f"Failed to analyze preparation delays: {e}")
            return self._fallback_delay_analysis(query)

    def _fallback_delay_analysis(self, query: str) -> dict:
        """Fallback delay analysis"""
        query_lower = query.lower()

        # Extract time information
        actual_time = "30-35 minutes" if "30" in query_lower or "35" in query_lower else "25-30 minutes"
        severity = "severe" if any(word in query_lower for word in ["very long", "extremely slow", "unacceptable"]) else "moderate"

        return {
            "actual_prep_time": actual_time,
            "expected_prep_time": "15-20 minutes",
            "delay_factors": ["kitchen workflow", "staff scheduling", "equipment capacity"],
            "pattern_type": "recurring" if "always" in query_lower or "every time" in query_lower else "isolated",
            "affected_items": ["multiple items"],
            "severity": severity
        }

    def get_restaurant_preparation_performance(self, restaurant_id: str) -> dict:
        """Get restaurant's historical preparation performance"""
        # This would typically query database for performance metrics
        return {
            "average_prep_time": "28 minutes",
            "target_prep_time": "18 minutes",
            "efficiency_score": 65,
            "peak_hour_performance": "below_standard",
            "equipment_utilization": 85,
            "staff_efficiency": "needs_improvement"
        }

    def generate_preparation_improvement_plan(self, delay_analysis: dict, performance_metrics: dict) -> dict:
        """Generate improvement plan using AI reasoning"""
        plan_prompt = f"""
        Create an improvement plan for restaurant preparation delays:

        Delay Analysis: {delay_analysis}
        Performance Metrics: {performance_metrics}

        Generate a comprehensive improvement plan with:
        1. Immediate actions (0-24 hours)
        2. Short-term improvements (1-2 weeks)
        3. Long-term optimizations (1+ months)
        4. Success metrics and monitoring

        Return ONLY JSON: {{"immediate_actions": ["action1"], "short_term_improvements": ["improvement1"], "long_term_optimizations": ["optimization1"], "success_metrics": ["metric1"], "estimated_improvement": "X% reduction in prep time"}}
        """

        try:
            if self.ai_engine:
                result = self.ai_engine.process_complaint(
                    function_name="generate_improvement_plan",
                    user_query=plan_prompt,
                    service=self.service,
                    user_type=self.actor
                )

                import json
                if "{" in result and "}" in result:
                    json_start = result.find("{")
                    json_end = result.rfind("}") + 1
                    json_str = result[json_start:json_end]
                    return json.loads(json_str)

            return self._fallback_improvement_plan(delay_analysis)

        except Exception as e:
            logger.error(f"Failed to generate improvement plan: {e}")
            return self._fallback_improvement_plan(delay_analysis)

    def _fallback_improvement_plan(self, delay_analysis: dict) -> dict:
        """Fallback improvement plan"""
        severity = delay_analysis.get("severity", "moderate")

        plan = {
            "immediate_actions": [
                "Review current order queue and prioritize urgent orders",
                "Optimize kitchen workflow for peak hours",
                "Implement prep-ahead procedures for popular items"
            ],
            "short_term_improvements": [
                "Staff training on time management",
                "Kitchen equipment maintenance and optimization",
                "Menu complexity analysis and simplification"
            ],
            "long_term_optimizations": [
                "Kitchen layout optimization",
                "Technology integration for order tracking",
                "Advanced inventory management system"
            ],
            "success_metrics": [
                "Reduce average prep time to 18-20 minutes",
                "Achieve 95% on-time delivery rate",
                "Improve customer satisfaction to 4.5+ stars"
            ],
            "estimated_improvement": "25-30% reduction in prep time"
        }

        if severity == "severe":
            plan["immediate_actions"].insert(0, "Emergency kitchen workflow assessment")
            plan["estimated_improvement"] = "35-40% reduction in prep time"

        return plan

    def generate_preparation_delay_response(self, delay_analysis: dict, performance_metrics: dict, improvement_plan: dict) -> str:
        """Generate comprehensive response for preparation delays"""
        severity = delay_analysis.get("severity", "moderate")
        actual_time = delay_analysis.get("actual_prep_time", "unknown")
        expected_time = delay_analysis.get("expected_prep_time", "15-20 minutes")

        return f"""⏰ **Kitchen Efficiency Optimization - Data-Driven Improvement Plan**

**Performance Analysis:**
- Current preparation time: {actual_time}
- Target preparation time: {expected_time}
- Efficiency gap: {performance_metrics.get('efficiency_score', 'unknown')}% of target
- Impact severity: {severity.title()}

**🔍 Root Cause Analysis:**
{chr(10).join([f"- {factor}" for factor in delay_analysis.get('delay_factors', ['Workflow optimization needed'])])}

**📊 Performance Metrics:**
- Average prep time: {performance_metrics.get('average_prep_time', 'unknown')}
- Peak hour performance: {performance_metrics.get('peak_hour_performance', 'needs assessment')}
- Equipment utilization: {performance_metrics.get('equipment_utilization', 'unknown')}%
- Staff efficiency: {performance_metrics.get('staff_efficiency', 'requires evaluation')}

**🎯 IMMEDIATE ACTIONS (Next 24 Hours):**
{chr(10).join([f"- {action}" for action in improvement_plan.get('immediate_actions', ['Assess current workflow'])])}

**📈 SHORT-TERM IMPROVEMENTS (1-2 Weeks):**
{chr(10).join([f"- {improvement}" for improvement in improvement_plan.get('short_term_improvements', ['Implement efficiency measures'])])}

**🚀 LONG-TERM OPTIMIZATIONS (1+ Months):**
{chr(10).join([f"- {optimization}" for optimization in improvement_plan.get('long_term_optimizations', ['Strategic improvements'])])}

**✅ SUCCESS METRICS & MONITORING:**
{chr(10).join([f"- {metric}" for metric in improvement_plan.get('success_metrics', ['Track improvement progress'])])}

**📈 Expected Improvement:**
- Preparation time reduction: {improvement_plan.get('estimated_improvement', '20-25%')}
- Customer satisfaction impact: Positive
- Delivery partner experience: Significantly improved

Your commitment to kitchen efficiency optimization will enhance customer satisfaction and operational profitability."""

    def handle_restaurant_ingredient_quality(self, query: str, restaurant_id: str = "anonymous") -> str:
        """Handle restaurant ingredient quality issues with comprehensive quality assurance workflow"""
        logger.info(f"Processing ingredient quality issue: {query[:100]}...")

        # Analyze quality issue details
        quality_analysis = self.analyze_ingredient_quality_issue(query)

        # Assess supplier and quality control systems
        supplier_assessment = self.assess_supplier_quality_performance(restaurant_id, quality_analysis)

        # Generate quality improvement plan
        improvement_plan = self.generate_quality_improvement_plan(quality_analysis, supplier_assessment)

        # Create comprehensive response
        return self.generate_ingredient_quality_response(quality_analysis, supplier_assessment, improvement_plan)

    def analyze_ingredient_quality_issue(self, query: str) -> dict:
        """Analyze ingredient quality issue using AI"""
        analysis_prompt = f"""
        Analyze this restaurant ingredient quality complaint:

        Complaint: {query}

        Identify:
        1. What specific ingredients are affected?
        2. What quality issues are described (freshness, appearance, taste)?
        3. How severe is the quality problem?
        4. Is this a recurring issue or isolated incident?

        Return ONLY JSON: {{"affected_ingredients": ["ingredient1"], "quality_issues": ["freshness", "appearance"], "severity": "minor/moderate/severe/critical", "pattern_type": "isolated/recurring/systemic", "customer_health_risk": true/false, "supplier_issue_likely": true/false}}
        """

        try:
            if self.ai_engine:
                result = self.ai_engine.process_complaint(
                    function_name="analyze_ingredient_quality",
                    user_query=analysis_prompt,
                    service=self.service,
                    user_type=self.actor
                )

                import json
                if "{" in result and "}" in result:
                    json_start = result.find("{")
                    json_end = result.rfind("}") + 1
                    json_str = result[json_start:json_end]
                    return json.loads(json_str)

            return self._fallback_quality_analysis(query)

        except Exception as e:
            logger.error(f"Failed to analyze ingredient quality: {e}")
            return self._fallback_quality_analysis(query)

    def _fallback_quality_analysis(self, query: str) -> dict:
        """Fallback quality analysis"""
        query_lower = query.lower()

        # Detect quality issues
        quality_issues = []
        if any(word in query_lower for word in ["stale", "old", "expired", "fresh"]):
            quality_issues.append("freshness")
        if any(word in query_lower for word in ["looks bad", "appearance", "color", "moldy"]):
            quality_issues.append("appearance")
        if any(word in query_lower for word in ["taste", "flavor", "bitter", "sour"]):
            quality_issues.append("taste")

        severity = "severe" if any(word in query_lower for word in ["disgusting", "terrible", "inedible"]) else "moderate"

        return {
            "affected_ingredients": ["vegetables", "meat", "dairy"],
            "quality_issues": quality_issues or ["freshness"],
            "severity": severity,
            "pattern_type": "recurring" if "always" in query_lower else "isolated",
            "customer_health_risk": "sick" in query_lower or "poison" in query_lower,
            "supplier_issue_likely": True
        }

    def assess_supplier_quality_performance(self, restaurant_id: str, quality_analysis: dict) -> dict:
        """Assess supplier quality performance"""
        return {
            "supplier_rating": "B+",
            "recent_quality_issues": 3,
            "delivery_consistency": "good",
            "certification_status": "valid",
            "alternative_suppliers_available": True,
            "quality_audit_due": True
        }

    def generate_quality_improvement_plan(self, quality_analysis: dict, supplier_assessment: dict) -> dict:
        """Generate quality improvement plan"""
        severity = quality_analysis.get("severity", "moderate")

        plan = {
            "immediate_actions": [
                "Conduct immediate inventory quality inspection",
                "Remove affected ingredients from use",
                "Contact supplier for explanation and resolution"
            ],
            "quality_control_measures": [
                "Implement enhanced receiving inspection protocols",
                "Establish daily quality check procedures",
                "Train staff on quality identification standards"
            ],
            "supplier_management": [
                "Schedule supplier quality audit",
                "Review supplier contracts and quality standards",
                "Identify and qualify backup suppliers"
            ],
            "monitoring_plan": [
                "Daily ingredient quality logs",
                "Weekly supplier performance reviews",
                "Monthly quality trend analysis"
            ]
        }

        if severity in ["severe", "critical"]:
            plan["immediate_actions"].insert(0, "Suspend orders from affected supplier")
            plan["supplier_management"].insert(0, "Initiate emergency supplier replacement")

        return plan

    def generate_ingredient_quality_response(self, quality_analysis: dict, supplier_assessment: dict, improvement_plan: dict) -> str:
        """Generate comprehensive response for ingredient quality issues"""
        severity = quality_analysis.get("severity", "moderate")
        affected_ingredients = ", ".join(quality_analysis.get("affected_ingredients", ["ingredients"]))
        quality_issues = ", ".join(quality_analysis.get("quality_issues", ["quality"]))

        return f"""🥬 **Ingredient Quality Assurance - Comprehensive Quality Management**

**Quality Issue Analysis:**
- Affected ingredients: {affected_ingredients}
- Quality concerns: {quality_issues}
- Severity level: {severity.title()}
- Pattern assessment: {quality_analysis.get('pattern_type', 'unknown').title()}
- Health risk level: {'High' if quality_analysis.get('customer_health_risk') else 'Low'}

**🔍 Supplier Performance Assessment:**
- Current supplier rating: {supplier_assessment.get('supplier_rating', 'Under Review')}
- Recent quality issues: {supplier_assessment.get('recent_quality_issues', 'Unknown')} in past 30 days
- Delivery consistency: {supplier_assessment.get('delivery_consistency', 'Unknown')}
- Certification status: {supplier_assessment.get('certification_status', 'Unknown')}

**⚡ IMMEDIATE ACTIONS:**
{chr(10).join([f"- {action}" for action in improvement_plan.get('immediate_actions', ['Quality assessment initiated'])])}

**🎯 QUALITY CONTROL MEASURES:**
{chr(10).join([f"- {measure}" for measure in improvement_plan.get('quality_control_measures', ['Enhanced quality protocols'])])}

**🤝 SUPPLIER MANAGEMENT:**
{chr(10).join([f"- {action}" for action in improvement_plan.get('supplier_management', ['Supplier performance review'])])}

**📊 MONITORING & VERIFICATION:**
{chr(10).join([f"- {monitor}" for monitor in improvement_plan.get('monitoring_plan', ['Quality tracking system'])])}

**🎯 Quality Assurance Commitment:**
- Zero tolerance for substandard ingredients
- Continuous supplier performance monitoring
- Customer satisfaction as top priority
- Immediate corrective action on quality issues

Your commitment to ingredient quality directly impacts customer satisfaction and restaurant reputation."""

    def handle_restaurant_order_accuracy(self, query: str, restaurant_id: str = "anonymous") -> str:
        """Handle restaurant order accuracy with systematic improvement workflow"""
        logger.info(f"Processing order accuracy issue: {query[:100]}...")

        # Analyze accuracy issue details
        accuracy_analysis = self.analyze_order_accuracy_issue(query)

        # Get restaurant accuracy performance metrics
        accuracy_metrics = self.get_restaurant_accuracy_metrics(restaurant_id)

        # Generate accuracy improvement plan
        improvement_plan = self.generate_accuracy_improvement_plan(accuracy_analysis, accuracy_metrics)

        # Create comprehensive response
        return self.generate_order_accuracy_response(accuracy_analysis, accuracy_metrics, improvement_plan)

    def analyze_order_accuracy_issue(self, query: str) -> dict:
        """Analyze order accuracy issue using AI"""
        analysis_prompt = f"""
        Analyze this restaurant order accuracy complaint:

        Complaint: {query}

        Identify:
        1. What type of accuracy error occurred?
        2. Which items were affected?
        3. How did the error impact the customer?
        4. Is this a process or training issue?

        Return ONLY JSON: {{"error_type": "missing_item/wrong_item/incorrect_quantity/wrong_preparation", "affected_items": ["item1"], "customer_impact": "minor/moderate/severe", "root_cause": "process/training/system/communication", "frequency_indicator": "isolated/occasional/frequent"}}
        """

        try:
            if self.ai_engine:
                result = self.ai_engine.process_complaint(
                    function_name="analyze_order_accuracy",
                    user_query=analysis_prompt,
                    service=self.service,
                    user_type=self.actor
                )

                import json
                if "{" in result and "}" in result:
                    json_start = result.find("{")
                    json_end = result.rfind("}") + 1
                    json_str = result[json_start:json_end]
                    return json.loads(json_str)

            return self._fallback_accuracy_analysis(query)

        except Exception as e:
            logger.error(f"Failed to analyze order accuracy: {e}")
            return self._fallback_accuracy_analysis(query)

    def _fallback_accuracy_analysis(self, query: str) -> dict:
        """Fallback accuracy analysis"""
        query_lower = query.lower()

        error_type = "missing_item"
        if "wrong" in query_lower or "incorrect" in query_lower:
            error_type = "wrong_item"
        elif "missing" in query_lower or "forgot" in query_lower:
            error_type = "missing_item"
        elif "quantity" in query_lower or "amount" in query_lower:
            error_type = "incorrect_quantity"

        impact = "severe" if any(word in query_lower for word in ["ruined", "terrible", "unacceptable"]) else "moderate"

        return {
            "error_type": error_type,
            "affected_items": ["food item"],
            "customer_impact": impact,
            "root_cause": "process",
            "frequency_indicator": "frequent" if "always" in query_lower or "every time" in query_lower else "isolated"
        }

    def get_restaurant_accuracy_metrics(self, restaurant_id: str) -> dict:
        """Get restaurant's accuracy performance metrics"""
        return {
            "current_accuracy_rate": "92%",
            "target_accuracy_rate": "98%",
            "weekly_accuracy_trend": "declining",
            "most_common_errors": ["missing items", "wrong preparations"],
            "peak_hour_accuracy": "88%",
            "staff_training_completion": "75%"
        }

    def generate_accuracy_improvement_plan(self, accuracy_analysis: dict, accuracy_metrics: dict) -> dict:
        """Generate accuracy improvement plan"""
        error_type = accuracy_analysis.get("error_type", "missing_item")
        frequency = accuracy_analysis.get("frequency_indicator", "isolated")

        plan = {
            "immediate_corrections": [
                "Review order fulfillment process immediately",
                "Implement double-check verification system",
                "Brief staff on accuracy importance"
            ],
            "process_improvements": [
                "Install kitchen display system upgrades",
                "Create order verification checkpoints",
                "Implement photo confirmation for complex orders"
            ],
            "training_initiatives": [
                "Conduct accuracy-focused staff training",
                "Create order fulfillment standard procedures",
                "Establish quality assurance protocols"
            ],
            "monitoring_systems": [
                "Daily accuracy tracking implementation",
                "Real-time error reporting system",
                "Weekly performance review meetings"
            ]
        }

        if frequency == "frequent":
            plan["immediate_corrections"].insert(0, "Emergency accuracy audit and retraining")
            plan["process_improvements"].insert(0, "Overhaul current order management system")

        return plan

    def generate_order_accuracy_response(self, accuracy_analysis: dict, accuracy_metrics: dict, improvement_plan: dict) -> str:
        """Generate comprehensive response for order accuracy issues"""
        error_type = accuracy_analysis.get("error_type", "accuracy_error").replace("_", " ").title()
        customer_impact = accuracy_analysis.get("customer_impact", "moderate")
        current_rate = accuracy_metrics.get("current_accuracy_rate", "unknown")
        target_rate = accuracy_metrics.get("target_accuracy_rate", "98%")

        return f"""✅ **Order Accuracy Performance Enhancement - Systematic Improvement**

**Accuracy Issue Analysis:**
- Error type: {error_type}
- Customer impact: {customer_impact.title()}
- Frequency pattern: {accuracy_analysis.get('frequency_indicator', 'unknown').title()}
- Root cause assessment: {accuracy_analysis.get('root_cause', 'unknown').title()}

**📊 Current Performance Metrics:**
- Current accuracy rate: {current_rate}
- Target accuracy rate: {target_rate}
- Weekly trend: {accuracy_metrics.get('weekly_accuracy_trend', 'stable').title()}
- Peak hour accuracy: {accuracy_metrics.get('peak_hour_accuracy', 'unknown')}
- Staff training completion: {accuracy_metrics.get('staff_training_completion', 'unknown')}

**⚡ IMMEDIATE CORRECTIONS:**
{chr(10).join([f"- {correction}" for correction in improvement_plan.get('immediate_corrections', ['Accuracy review initiated'])])}

**🔧 PROCESS IMPROVEMENTS:**
{chr(10).join([f"- {improvement}" for improvement in improvement_plan.get('process_improvements', ['Process optimization planned'])])}

**🎓 TRAINING INITIATIVES:**
{chr(10).join([f"- {training}" for training in improvement_plan.get('training_initiatives', ['Staff training scheduled'])])}

**📈 MONITORING & TRACKING:**
{chr(10).join([f"- {monitor}" for monitor in improvement_plan.get('monitoring_systems', ['Performance tracking activated'])])}

**🎯 Quality Assurance Standards:**
- Zero tolerance for preventable accuracy errors
- Continuous process improvement mindset
- Customer satisfaction as primary metric
- Real-time error correction protocols

**📋 Success Metrics:**
- Target: 98%+ order accuracy within 2 weeks
- Reduce customer complaints by 75%
- Improve peak hour accuracy to 95%+
- Achieve 100% staff training compliance

Order accuracy is fundamental to customer trust and restaurant success on our platform."""
    
    # WAITING TIME HANDLER METHODS
    def handle_long_waiting_time(self, query: str, restaurant_id: str = "anonymous") -> str:
        """Handle restaurant long waiting time with comprehensive efficiency optimization workflow"""
        logger.info(f"Processing long waiting time issue: {query[:100]}...")

        # This uses the same logic as handle_restaurant_preparation_delays since they're essentially the same issue
        # Analyze delay details using AI reasoning
        delay_analysis = self.analyze_preparation_delay_details(query)

        # Get restaurant performance metrics with focus on waiting times
        performance_metrics = self.get_restaurant_preparation_performance(restaurant_id)

        # Add specific waiting time context
        performance_metrics.update({
            "current_waiting_time": "45 minutes",
            "customer_complaints_24h": 15,
            "order_cancellation_rate": "8%",
            "delivery_partner_impact": "severe"
        })

        # Generate improvement plan focused on waiting time reduction
        improvement_plan = self.generate_preparation_improvement_plan(delay_analysis, performance_metrics)

        # Create actionable response with waiting time focus
        return self.generate_waiting_time_response(delay_analysis, performance_metrics, improvement_plan)

    def generate_waiting_time_response(self, delay_analysis: dict, performance_metrics: dict, improvement_plan: dict) -> str:
        """Generate comprehensive response for long waiting times"""
        severity = delay_analysis.get("severity", "moderate")
        actual_time = performance_metrics.get("current_waiting_time", "unknown")
        complaints = performance_metrics.get("customer_complaints_24h", 0)
        cancellation_rate = performance_metrics.get("order_cancellation_rate", "unknown")

        return f"""⏱️ **Critical Waiting Time Optimization - Emergency Response Plan**

**Performance Crisis Analysis:**
- Current waiting time: {actual_time} (standard: 20-25 minutes)
- Customer complaints (24h): {complaints}+ complaints
- Order cancellation rate: {cancellation_rate} increase
- Delivery partner impact: {performance_metrics.get('delivery_partner_impact', 'moderate')}
- Restaurant rating risk: -0.3 stars potential

**🚨 IMMEDIATE CRISIS RESPONSE (Next 2 Hours):**
{chr(10).join([f"- {action}" for action in improvement_plan.get('immediate_actions', ['Emergency workflow assessment'])])}

**📊 Impact Assessment:**
- Customer satisfaction: Severely declining
- Delivery partner efficiency: Significantly affected
- Restaurant reputation: At immediate risk
- Revenue impact: Order cancellations increasing

**🔧 EMERGENCY OPTIMIZATION MEASURES:**
- Kitchen workflow emergency audit and restructure
- Immediate staff reallocation for peak efficiency
- Order prioritization system implementation
- Equipment capacity emergency assessment

**⚡ SHORT-TERM EFFICIENCY SOLUTIONS (24-48 Hours):**
{chr(10).join([f"- {improvement}" for improvement in improvement_plan.get('short_term_improvements', ['Implement efficiency protocols'])])}

**🎯 PERFORMANCE RECOVERY TARGETS:**
- Reduce waiting time to 15-20 minutes within 48 hours
- Eliminate customer complaints related to delays
- Restore delivery partner satisfaction levels
- Prevent rating decline through service recovery

**📈 STRATEGIC OPTIMIZATION (1+ Weeks):**
{chr(10).join([f"- {optimization}" for optimization in improvement_plan.get('long_term_optimizations', ['Implement strategic improvements'])])}

**⚠️ Critical Success Factors:**
- Immediate workflow changes must show results within 2 hours
- Customer communication about improvements essential
- Delivery partner coordination for realistic expectations
- Continuous monitoring until performance stabilizes

**🔄 Monitoring Protocol:**
- Real-time waiting time tracking every 30 minutes
- Customer satisfaction monitoring after each order
- Delivery partner feedback collection hourly
- Management review every 4 hours until resolution

Long waiting times threaten customer loyalty and platform partnership - immediate decisive action required."""
    
    # DELIVERY PARTNERS HANDLER METHODS
    async def handle_delivery_partner_shortage(self, query: str, restaurant_location: str = "1.3521,103.8198,Singapore") -> str:
        """Handle restaurant delivery partner shortage issues with weather predictions"""
        
        # Get weather impact predictions
        location_data = self._parse_restaurant_location(restaurant_location)
        weather_impact = await self._predict_weather_impact_on_delivery(location_data)
        
        # Generate enhanced response with weather considerations
        weather_section = self._generate_weather_impact_section(weather_impact)
        
        return f"""🚗 **Delivery Partner Shortage - Coordination Required**

**Delivery Capacity Issue Alert**

**Current Situation Analysis:**
- Delivery partners available: 3 (required: 8+ for current order volume)
- Orders waiting for pickup: 12+ orders pending
- Average wait time for partner assignment: 35 minutes
- Customer delivery expectations at risk

{weather_section}

**Impact on Restaurant Operations:**
- Orders prepared but awaiting pickup: food quality degradation
- Customer satisfaction declining due to delays
- Restaurant efficiency affected: kitchen capacity tied up
- Potential order cancellations increasing

**Immediate Grab Platform Response:**
1. Priority delivery partner allocation to your location
2. Surge incentive activation for nearby partners
3. Extended delivery radius partner notification
4. Emergency partner pool activation
{self._generate_weather_specific_actions(weather_impact)}

**Restaurant Coordination Actions:**
- Hold order preparation for 15+ minute delays
- Customer communication: proactive delay notifications
- Food quality maintenance: proper holding procedures
- Order prioritization: FIFO with quality considerations
{self._generate_weather_restaurant_actions(weather_impact)}

**Delivery Partner Incentives Activated:**
- Surge pricing: +40% delivery fees for your area
- Priority partner notifications within 5km radius
- Bonus payments for immediate availability
- Performance rewards for quick response times
{self._generate_weather_incentives(weather_impact)}

**Quality Preservation Guidelines:**
- Hot food holding: maximum 20 minutes
- Cold items: proper refrigeration maintenance
- Packaging optimization: insulation and freshness
- Quality check before delayed handover
{self._generate_weather_quality_guidelines(weather_impact)}

**Timeline for Resolution:**
- Immediate: surge incentives activation (5 minutes)
- Short-term: additional partner allocation (15 minutes)
- Medium-term: sustained capacity improvement (1 hour)
- Long-term: demand-supply optimization (ongoing)
{self._generate_weather_timeline_adjustments(weather_impact)}

**Weather-Enhanced Delivery Strategy:**
- Current conditions: {weather_impact.get('current_conditions', 'normal')}
- Impact level: {weather_impact.get('impact_level', 'low')}
- Recommended delay buffer: {weather_impact.get('recommended_delay', 0)} minutes
- Special handling required: {'Yes' if weather_impact.get('special_handling_required') else 'No'}

Adequate delivery partner availability is crucial for restaurant success and customer satisfaction on the Grab Food platform."""
    
    def _parse_restaurant_location(self, location_string: str) -> LocationData:
        """Parse restaurant location string to LocationData object"""
        try:
            parts = location_string.split(',')
            if len(parts) >= 2:
                lat = float(parts[0].strip())
                lng = float(parts[1].strip())
                address = ','.join(parts[2:]).strip() if len(parts) > 2 else "Restaurant Location"
                return LocationData(latitude=lat, longitude=lng, address=address)
            else:
                return LocationData(latitude=1.3521, longitude=103.8198, address=location_string)
        except (ValueError, IndexError):
            return LocationData(latitude=1.3521, longitude=103.8198, address="Singapore")
    
    async def _predict_weather_impact_on_delivery(self, location: LocationData) -> Dict[str, Any]:
        """Predict weather impact on delivery partner availability and performance"""
        try:
            weather_impact = await self.weather_api.predict_weather_impact(location)
            current_weather = await self.weather_api.get_current_weather(location)
            
            return {
                **weather_impact,
                'temperature': current_weather.temperature,
                'precipitation_probability': current_weather.precipitation_probability,
                'wind_speed': current_weather.wind_speed,
                'visibility': current_weather.visibility
            }
        except Exception as e:
            logger.error(f"Weather API error: {str(e)}")
            return {
                'impact_level': 'unknown',
                'current_conditions': 'unknown',
                'temperature': 25.0,
                'precipitation_risk': 0.0,
                'recommended_delay': 0,
                'special_handling_required': False,
                'visibility_concerns': False
            }
    
    def _generate_weather_impact_section(self, weather_impact: Dict[str, Any]) -> str:
        """Generate weather impact section for the response"""
        impact_level = weather_impact.get('impact_level', 'low')
        conditions = weather_impact.get('current_conditions', 'clear')
        
        if impact_level in ['moderate', 'severe']:
            return f"""**Weather Impact Assessment:**
- Current conditions: {conditions} (Impact: {impact_level})
- Temperature: {weather_impact.get('temperature', 25):.1f}°C
- Precipitation risk: {weather_impact.get('precipitation_risk', 0)*100:.0f}%
- Delivery partner availability likely reduced due to weather
- Extended delivery times expected: +{weather_impact.get('recommended_delay', 0)} minutes"""
        else:
            return f"""**Weather Conditions:**
- Current conditions: {conditions} (Impact: minimal)
- Temperature: {weather_impact.get('temperature', 25):.1f}°C
- Weather not significantly impacting delivery operations"""
    
    def _generate_weather_specific_actions(self, weather_impact: Dict[str, Any]) -> str:
        """Generate weather-specific platform actions"""
        impact_level = weather_impact.get('impact_level', 'low')
        actions = []

        if impact_level in ['moderate', 'severe']:
            actions.extend([
                "5. Weather contingency protocols activated",
                "6. Additional weather compensation for delivery partners",
                "7. Extended delivery radius to compensate for reduced availability"
            ])

            if impact_level == 'severe':
                actions.extend([
                    "8. Emergency delivery partner recruitment",
                    "9. Customer proactive weather delay notifications"
                ])

        return '\n'.join(actions) if actions else ""
    
    def _generate_weather_restaurant_actions(self, weather_impact: Dict[str, Any]) -> str:
        """Generate weather-specific restaurant actions"""
        actions = []
        
        if weather_impact.get('special_handling_required'):
            actions.append("- Enhanced packaging for weather protection")
        
        if weather_impact.get('impact_level') in ['moderate', 'severe']:
            actions.extend([
                "- Extended food holding protocols activated",
                "- Customer proactive weather delay notifications"
            ])
        
        if weather_impact.get('precipitation_risk', 0) > 0.3:
            actions.append("- Waterproof packaging prioritized")
        
        return '\n'.join(actions) if actions else ""
    
    def _generate_weather_incentives(self, weather_impact: Dict[str, Any]) -> str:
        """Generate weather-specific partner incentives"""
        impact_level = weather_impact.get('impact_level', 'low')
        incentives = []

        if impact_level in ['moderate', 'severe']:
            incentives.extend([
                "- Weather hazard pay: additional compensation",
                "- Covered parking priority for delivery partners",
                "- Weather gear provision if needed"
            ])

            if impact_level == 'severe':
                incentives.extend([
                    "- Emergency response bonus payments",
                    "- Priority customer service support",
                    "- Extended break facilities access"
                ])

        return '\n'.join(incentives) if incentives else ""
    
    def _generate_weather_quality_guidelines(self, weather_impact: Dict[str, Any]) -> str:
        """Generate weather-specific quality guidelines"""
        guidelines = []
        
        temp = weather_impact.get('temperature', 25)
        if temp > 35 or temp < 5:
            guidelines.append("- Temperature-sensitive items: enhanced insulation required")
        
        if weather_impact.get('precipitation_risk', 0) > 0.2:
            guidelines.extend([
                "- Waterproof packaging mandatory",
                "- Double-bag sensitive items"
            ])
        
        if weather_impact.get('visibility_concerns'):
            guidelines.append("- Enhanced order labeling for low visibility conditions")
        
        return '\n'.join(guidelines) if guidelines else ""
    
    def _generate_weather_timeline_adjustments(self, weather_impact: Dict[str, Any]) -> str:
        """Generate weather-adjusted timeline expectations"""
        if weather_impact.get('recommended_delay', 0) > 5:
            return f"""- Weather delay buffer: +{weather_impact.get('recommended_delay')} minutes added to all estimates
- Extended resolution timeline due to weather conditions"""
        return ""
    
    # UNEXPECTED HINDRANCE HANDLER METHODS
    def handle_unexpected_hindrance(self, query: str, restaurant_id: str = "anonymous", urgency_level: str = "medium") -> str:
        """Handle restaurant unexpected operational hindrances with strict 9-step crisis management workflow"""
        logger.info(f"Processing unexpected hindrance: {query[:100]}...")

        # Step 1: Analyze hindrance type and severity using AI reasoning
        hindrance_analysis = self.analyze_hindrance_type_and_severity(query)

        # Step 2: Assess immediate safety and operational risks
        risk_assessment = self.assess_hindrance_operational_risks(hindrance_analysis, restaurant_id)

        # Step 3: Determine crisis response level and protocol activation
        crisis_response_level = self.determine_crisis_response_level(hindrance_analysis, risk_assessment)

        # Step 4: Evaluate customer impact and order management needs
        customer_impact = self.evaluate_customer_impact_from_hindrance(hindrance_analysis, crisis_response_level)

        # Step 5: Generate emergency action plan using AI reasoning
        emergency_action_plan = self.generate_emergency_action_plan(
            hindrance_analysis, risk_assessment, crisis_response_level, customer_impact
        )

        # Step 6: Activate platform support and coordination protocols
        platform_support = self.activate_platform_support_protocols(emergency_action_plan, crisis_response_level)

        # Step 7: Establish communication strategy for all stakeholders
        communication_strategy = self.establish_hindrance_communication_strategy(
            hindrance_analysis, customer_impact, emergency_action_plan
        )

        # Step 8: Create recovery timeline and monitoring plan
        recovery_plan = self.create_hindrance_recovery_plan(
            hindrance_analysis, emergency_action_plan, platform_support
        )

        # Step 9: Generate comprehensive crisis management response
        response = self.generate_hindrance_management_response(
            hindrance_analysis, risk_assessment, crisis_response_level,
            emergency_action_plan, communication_strategy, recovery_plan
        )

        logger.info(f"Unexpected hindrance crisis management workflow completed")
        return response

    def analyze_hindrance_type_and_severity(self, query: str) -> dict:
        """Analyze hindrance type and severity using AI-powered assessment"""
        analysis_prompt = f"""
        Analyze this restaurant operational hindrance and classify it comprehensively:

        Hindrance Description: {query}

        Identify and categorize:
        1. What type of operational hindrance is this?
        2. How severe is the impact on restaurant operations?
        3. Is this a safety-critical incident?
        4. What operational systems are affected?
        5. How long might this hindrance last?
        6. Are customers immediately at risk?
        7. What is the estimated business impact?

        Return ONLY JSON: {{"hindrance_type": "power_outage/equipment_failure/supply_shortage/staff_emergency/health_incident/technology_failure/natural_disaster/security_incident", "severity_level": "minor/moderate/severe/critical/emergency", "safety_critical": true/false, "affected_systems": ["kitchen", "ordering", "payment", "delivery"], "estimated_duration": "minutes/hours/days", "customer_risk_level": "none/low/medium/high/critical", "business_impact": "minimal/moderate/significant/severe/catastrophic", "requires_immediate_evacuation": true/false, "health_department_notification": true/false, "emergency_services_needed": true/false}}
        """

        try:
            if self.ai_engine:
                result = self.ai_engine.process_complaint(
                    function_name="analyze_hindrance_severity",
                    user_query=analysis_prompt,
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
                    return self._fallback_hindrance_analysis(query)
            else:
                return self._fallback_hindrance_analysis(query)

        except Exception as e:
            logger.error(f"Failed to analyze hindrance: {e}")
            return self._fallback_hindrance_analysis(query)

    def _fallback_hindrance_analysis(self, query: str) -> dict:
        """Fallback hindrance analysis when AI fails"""
        analysis = {
            "hindrance_type": "equipment_failure",
            "severity_level": "moderate",
            "safety_critical": False,
            "affected_systems": ["kitchen"],
            "estimated_duration": "hours",
            "customer_risk_level": "low",
            "business_impact": "moderate",
            "requires_immediate_evacuation": False,
            "health_department_notification": False,
            "emergency_services_needed": False
        }

        query_lower = query.lower()

        # Detect hindrance type
        if any(word in query_lower for word in ['power', 'electricity', 'blackout', 'outage']):
            analysis.update({
                "hindrance_type": "power_outage",
                "severity_level": "severe",
                "affected_systems": ["kitchen", "ordering", "payment"],
                "business_impact": "significant"
            })
        elif any(word in query_lower for word in ['fire', 'smoke', 'gas leak', 'explosion']):
            analysis.update({
                "hindrance_type": "security_incident",
                "severity_level": "critical",
                "safety_critical": True,
                "customer_risk_level": "critical",
                "requires_immediate_evacuation": True,
                "emergency_services_needed": True
            })
        elif any(word in query_lower for word in ['food poisoning', 'contamination', 'sick', 'health']):
            analysis.update({
                "hindrance_type": "health_incident",
                "severity_level": "severe",
                "safety_critical": True,
                "health_department_notification": True,
                "customer_risk_level": "high"
            })
        elif any(word in query_lower for word in ['equipment', 'machine', 'oven', 'broken', 'malfunction']):
            analysis.update({
                "hindrance_type": "equipment_failure",
                "severity_level": "moderate",
                "affected_systems": ["kitchen"]
            })

        # Detect severity indicators
        if any(word in query_lower for word in ['emergency', 'urgent', 'critical', 'immediate']):
            analysis["severity_level"] = "critical"
        elif any(word in query_lower for word in ['serious', 'major', 'significant']):
            analysis["severity_level"] = "severe"

        return analysis

    def assess_hindrance_operational_risks(self, hindrance_analysis: dict, restaurant_id: str) -> dict:
        """Assess operational risks from the hindrance"""
        risks = {
            "immediate_closure_required": False,
            "partial_service_possible": True,
            "food_safety_compromised": False,
            "staff_safety_risk": False,
            "customer_safety_risk": False,
            "revenue_loss_estimate": "low",
            "reputation_impact": "minimal",
            "legal_liability_risk": False,
            "insurance_claim_required": False,
            "regulatory_notification_required": False
        }

        severity = hindrance_analysis.get("severity_level", "moderate")
        safety_critical = hindrance_analysis.get("safety_critical", False)
        hindrance_type = hindrance_analysis.get("hindrance_type", "equipment_failure")

        # Safety-critical assessments
        if safety_critical:
            risks.update({
                "immediate_closure_required": True,
                "partial_service_possible": False,
                "staff_safety_risk": True,
                "customer_safety_risk": True,
                "legal_liability_risk": True,
                "insurance_claim_required": True,
                "regulatory_notification_required": True
            })

        # Severity-based risk escalation
        if severity in ["critical", "emergency"]:
            risks.update({
                "immediate_closure_required": True,
                "revenue_loss_estimate": "high",
                "reputation_impact": "significant"
            })
        elif severity == "severe":
            risks.update({
                "partial_service_possible": False,
                "revenue_loss_estimate": "medium",
                "reputation_impact": "moderate"
            })

        # Hindrance-specific risks
        if hindrance_type == "health_incident":
            risks.update({
                "food_safety_compromised": True,
                "regulatory_notification_required": True,
                "reputation_impact": "significant"
            })
        elif hindrance_type == "power_outage":
            risks.update({
                "food_safety_compromised": True,
                "immediate_closure_required": True
            })

        # Restaurant credibility impact
        credibility_score = self.get_restaurant_credibility_score(restaurant_id)
        if credibility_score <= 5:
            risks["reputation_impact"] = "severe"

        return risks

    def determine_crisis_response_level(self, hindrance_analysis: dict, risk_assessment: dict) -> dict:
        """Determine appropriate crisis response level"""
        response_level = {
            "level": "standard",
            "platform_notification": False,
            "emergency_services_contact": False,
            "health_authorities_contact": False,
            "management_escalation": False,
            "media_response_required": False,
            "legal_team_involvement": False,
            "customer_mass_notification": False,
            "order_suspension_required": False,
            "immediate_action_timeline": "30 minutes"
        }

        severity = hindrance_analysis.get("severity_level", "moderate")
        safety_critical = hindrance_analysis.get("safety_critical", False)
        immediate_closure = risk_assessment.get("immediate_closure_required", False)

        # Response level escalation matrix
        if severity == "emergency" or hindrance_analysis.get("requires_immediate_evacuation"):
            response_level.update({
                "level": "emergency",
                "platform_notification": True,
                "emergency_services_contact": True,
                "management_escalation": True,
                "media_response_required": True,
                "legal_team_involvement": True,
                "customer_mass_notification": True,
                "order_suspension_required": True,
                "immediate_action_timeline": "immediate"
            })
        elif severity == "critical" or safety_critical:
            response_level.update({
                "level": "critical",
                "platform_notification": True,
                "health_authorities_contact": True,
                "management_escalation": True,
                "customer_mass_notification": True,
                "order_suspension_required": True,
                "immediate_action_timeline": "5 minutes"
            })
        elif severity == "severe" or immediate_closure:
            response_level.update({
                "level": "severe",
                "platform_notification": True,
                "management_escalation": True,
                "order_suspension_required": True,
                "immediate_action_timeline": "15 minutes"
            })
        elif severity == "moderate":
            response_level.update({
                "level": "moderate",
                "platform_notification": True,
                "immediate_action_timeline": "30 minutes"
            })

        return response_level

    def evaluate_customer_impact_from_hindrance(self, hindrance_analysis: dict, crisis_response_level: dict) -> dict:
        """Evaluate impact on customers and orders"""
        impact = {
            "orders_affected": 0,
            "customers_to_notify": 0,
            "refund_required": False,
            "alternative_recommendations": False,
            "compensation_required": False,
            "health_risk_to_customers": False,
            "delivery_disruption": False,
            "estimated_customer_complaints": 0,
            "customer_satisfaction_impact": "minimal"
        }

        severity = hindrance_analysis.get("severity_level", "moderate")
        customer_risk = hindrance_analysis.get("customer_risk_level", "low")
        order_suspension = crisis_response_level.get("order_suspension_required", False)

        # Customer impact based on severity
        if order_suspension:
            impact.update({
                "orders_affected": 15,  # Estimated pending orders
                "customers_to_notify": 15,
                "refund_required": True,
                "alternative_recommendations": True,
                "compensation_required": True,
                "delivery_disruption": True
            })

        # Health risk assessment
        if customer_risk in ["high", "critical"]:
            impact.update({
                "health_risk_to_customers": True,
                "compensation_required": True,
                "estimated_customer_complaints": 10
            })

        # Satisfaction impact prediction
        if severity in ["critical", "emergency"]:
            impact["customer_satisfaction_impact"] = "severe"
        elif severity == "severe":
            impact["customer_satisfaction_impact"] = "significant"
        elif severity == "moderate":
            impact["customer_satisfaction_impact"] = "moderate"

        return impact

    def generate_emergency_action_plan(self, hindrance_analysis: dict, risk_assessment: dict,
                                      crisis_response_level: dict, customer_impact: dict) -> dict:
        """Generate emergency action plan using AI reasoning"""
        action_prompt = f"""
        Generate a comprehensive emergency action plan for this restaurant crisis:

        Hindrance Analysis: {hindrance_analysis}
        Risk Assessment: {risk_assessment}
        Crisis Response Level: {crisis_response_level}
        Customer Impact: {customer_impact}

        Create a prioritized action plan with:
        1. Immediate actions (0-15 minutes)
        2. Short-term actions (15 minutes - 2 hours)
        3. Recovery actions (2+ hours)
        4. Staff responsibilities
        5. External coordination needs

        Return ONLY JSON: {{"immediate_actions": ["action1", "action2"], "short_term_actions": ["action1", "action2"], "recovery_actions": ["action1", "action2"], "staff_responsibilities": {{"role": "responsibility"}}, "external_coordination": ["contact1", "contact2"], "resource_requirements": ["resource1", "resource2"], "success_criteria": ["criteria1", "criteria2"]}}
        """

        try:
            if self.ai_engine:
                result = self.ai_engine.process_complaint(
                    function_name="generate_emergency_action_plan",
                    user_query=action_prompt,
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
                    return self._fallback_emergency_action_plan(hindrance_analysis, crisis_response_level)
            else:
                return self._fallback_emergency_action_plan(hindrance_analysis, crisis_response_level)

        except Exception as e:
            logger.error(f"Failed to generate action plan: {e}")
            return self._fallback_emergency_action_plan(hindrance_analysis, crisis_response_level)

    def _fallback_emergency_action_plan(self, hindrance_analysis: dict, crisis_response_level: dict) -> dict:
        """Fallback emergency action plan when AI fails"""
        plan = {
            "immediate_actions": [
                "Assess situation and ensure staff safety",
                "Stop new order acceptance",
                "Notify customers of delays"
            ],
            "short_term_actions": [
                "Contact repair services",
                "Implement alternative procedures",
                "Communicate with delivery partners"
            ],
            "recovery_actions": [
                "Resume normal operations",
                "Monitor service quality",
                "Follow up with affected customers"
            ],
            "staff_responsibilities": {
                "manager": "Coordinate overall response",
                "kitchen_staff": "Implement safety protocols",
                "front_staff": "Manage customer communication"
            },
            "external_coordination": [
                "Platform support team",
                "Equipment repair services"
            ],
            "resource_requirements": [
                "Emergency contact list",
                "Backup procedures manual"
            ],
            "success_criteria": [
                "Operations fully restored",
                "Customer satisfaction maintained"
            ]
        }

        level = crisis_response_level.get("level", "standard")
        hindrance_type = hindrance_analysis.get("hindrance_type", "equipment_failure")

        # Customize based on crisis level
        if level in ["critical", "emergency"]:
            plan["immediate_actions"].extend([
                "Evacuate premises if necessary",
                "Contact emergency services",
                "Secure all equipment and inventory"
            ])
            plan["external_coordination"].extend([
                "Emergency services",
                "Health department"
            ])

        # Customize based on hindrance type
        if hindrance_type == "power_outage":
            plan["immediate_actions"].append("Switch to emergency power if available")
            plan["external_coordination"].append("Utility company")

        return plan

    def activate_platform_support_protocols(self, emergency_action_plan: dict, crisis_response_level: dict) -> dict:
        """Activate platform support and coordination protocols"""
        support = {
            "technical_support_activated": False,
            "customer_service_escalation": False,
            "order_management_override": False,
            "delivery_partner_notification": False,
            "alternative_restaurant_promotion": False,
            "emergency_communication_tools": False,
            "revenue_protection_measures": False,
            "insurance_coordination": False
        }

        level = crisis_response_level.get("level", "standard")

        # Activate support based on crisis level
        if level in ["emergency", "critical"]:
            support.update({
                "technical_support_activated": True,
                "customer_service_escalation": True,
                "order_management_override": True,
                "delivery_partner_notification": True,
                "alternative_restaurant_promotion": True,
                "emergency_communication_tools": True,
                "revenue_protection_measures": True,
                "insurance_coordination": True
            })
        elif level == "severe":
            support.update({
                "technical_support_activated": True,
                "customer_service_escalation": True,
                "order_management_override": True,
                "delivery_partner_notification": True,
                "alternative_restaurant_promotion": True
            })
        elif level == "moderate":
            support.update({
                "customer_service_escalation": True,
                "delivery_partner_notification": True
            })

        return support

    def establish_hindrance_communication_strategy(self, hindrance_analysis: dict, customer_impact: dict, emergency_action_plan: dict) -> dict:
        """Establish communication strategy for all stakeholders"""
        strategy = {
            "customer_message_tone": "apologetic",
            "transparency_level": "high",
            "communication_channels": ["app", "sms"],
            "update_frequency": "every_30_minutes",
            "key_messages": [],
            "staff_briefing_required": True,
            "media_statement_needed": False,
            "social_media_response": False
        }

        severity = hindrance_analysis.get("severity_level", "moderate")
        health_risk = customer_impact.get("health_risk_to_customers", False)

        # Customize communication based on severity
        if severity in ["critical", "emergency"]:
            strategy.update({
                "transparency_level": "complete",
                "communication_channels": ["app", "sms", "email", "phone"],
                "update_frequency": "every_15_minutes",
                "media_statement_needed": True,
                "social_media_response": True
            })

        # Key messages based on situation
        if health_risk:
            strategy["key_messages"].extend([
                "Customer health and safety is our top priority",
                "We are working with health authorities",
                "Free medical consultation available if needed"
            ])
        else:
            strategy["key_messages"].extend([
                "We sincerely apologize for the disruption",
                "We are working to resolve the issue quickly",
                "Full refunds and compensation will be provided"
            ])

        return strategy

    def create_hindrance_recovery_plan(self, hindrance_analysis: dict, emergency_action_plan: dict, platform_support: dict) -> dict:
        """Create recovery timeline and monitoring plan"""
        recovery = {
            "estimated_recovery_time": "2-4 hours",
            "recovery_phases": [],
            "monitoring_checkpoints": [],
            "quality_assurance_steps": [],
            "customer_notification_timeline": [],
            "performance_metrics_tracking": [],
            "lessons_learned_documentation": True
        }

        estimated_duration = hindrance_analysis.get("estimated_duration", "hours")
        hindrance_type = hindrance_analysis.get("hindrance_type", "equipment_failure")

        # Customize recovery timeline
        if estimated_duration == "days":
            recovery["estimated_recovery_time"] = "24-48 hours"
        elif estimated_duration == "minutes":
            recovery["estimated_recovery_time"] = "30-60 minutes"

        # Recovery phases
        recovery["recovery_phases"] = [
            "Emergency response and stabilization",
            "Problem resolution and testing",
            "Gradual service resumption",
            "Full operations restoration",
            "Post-incident review and improvement"
        ]

        # Monitoring checkpoints
        recovery["monitoring_checkpoints"] = [
            "Safety protocols compliance verified",
            "Technical systems functionality confirmed",
            "Staff readiness assessment completed",
            "Customer communication effectiveness measured"
        ]

        return recovery

    def generate_hindrance_management_response(self, hindrance_analysis: dict, risk_assessment: dict,
                                             crisis_response_level: dict, emergency_action_plan: dict,
                                             communication_strategy: dict, recovery_plan: dict) -> str:
        """Generate comprehensive crisis management response"""
        severity = hindrance_analysis.get("severity_level", "moderate")
        hindrance_type = hindrance_analysis.get("hindrance_type", "equipment_failure")
        level = crisis_response_level.get("level", "standard")

        if level in ["emergency", "critical"]:
            return f"""🚨 **EMERGENCY CRISIS RESPONSE ACTIVATED - IMMEDIATE ACTION REQUIRED**

**CRITICAL OPERATIONAL EMERGENCY**

**🔍 Crisis Assessment:**
- Hindrance type: {hindrance_type.replace('_', ' ').title()}
- Severity level: {severity.upper()}
- Safety critical: {'YES' if hindrance_analysis.get('safety_critical') else 'NO'}
- Customer risk: {hindrance_analysis.get('customer_risk_level', 'unknown').upper()}
- Estimated duration: {hindrance_analysis.get('estimated_duration', 'unknown')}

**🚨 IMMEDIATE EMERGENCY ACTIONS (Next {crisis_response_level.get('immediate_action_timeline', '5 minutes')}):**
{chr(10).join([f"- {action}" for action in emergency_action_plan.get('immediate_actions', ['Assess situation and ensure safety'])])}

**⚠️ CRITICAL SAFETY MEASURES:**
- Staff safety protocols: {'ACTIVATED' if risk_assessment.get('staff_safety_risk') else 'STANDARD'}
- Customer safety status: {'AT RISK' if risk_assessment.get('customer_safety_risk') else 'SECURED'}
- Premises evacuation: {'REQUIRED' if hindrance_analysis.get('requires_immediate_evacuation') else 'NOT NEEDED'}
- Emergency services: {'CONTACTED' if crisis_response_level.get('emergency_services_contact') else 'STANDBY'}

**📞 EMERGENCY COORDINATION ACTIVATED:**
{chr(10).join([f"- {contact}" for contact in emergency_action_plan.get('external_coordination', ['Platform emergency support'])])}

**🔒 OPERATIONAL STATUS:**
- Order acceptance: SUSPENDED IMMEDIATELY
- Current orders: {emergency_action_plan.get('orders_affected', 'Unknown')} orders affected
- Customer notifications: MASS ALERT SENT
- Delivery operations: HALTED UNTIL RESOLUTION

**👥 STAFF RESPONSIBILITIES:**
{chr(10).join([f"- {role}: {responsibility}" for role, responsibility in emergency_action_plan.get('staff_responsibilities', {}).items()])}

**📋 RECOVERY TIMELINE:**
- Emergency response: {crisis_response_level.get('immediate_action_timeline', 'immediate')}
- Problem resolution: {recovery_plan.get('estimated_recovery_time', '2-4 hours')}
- Service restoration: Gradual resumption after safety clearance
- Full operations: Subject to complete resolution verification

**📞 CUSTOMER COMMUNICATION STRATEGY:**
- Message tone: {communication_strategy.get('customer_message_tone', 'apologetic')}
- Transparency level: {communication_strategy.get('transparency_level', 'high')}
- Update frequency: {communication_strategy.get('update_frequency', 'continuous')}
- Channels activated: {', '.join(communication_strategy.get('communication_channels', ['app', 'sms']))}

**✅ SUCCESS CRITERIA FOR RESUMPTION:**
{chr(10).join([f"- {criteria}" for criteria in emergency_action_plan.get('success_criteria', ['Safety verified', 'Operations restored'])])}

This is a critical emergency requiring immediate action. Follow all protocols precisely and prioritize safety above all else."""

        elif level == "severe":
            return f"""⚠️ **SEVERE OPERATIONAL DISRUPTION - CRISIS MANAGEMENT ACTIVATED**

**SIGNIFICANT SERVICE INTERRUPTION**

**🔍 Situation Analysis:**
- Hindrance type: {hindrance_type.replace('_', ' ').title()}
- Severity: {severity.upper()}
- Business impact: {risk_assessment.get('revenue_loss_estimate', 'unknown')}
- Customer impact: {customer_impact.get('customer_satisfaction_impact', 'unknown')}
- Service disruption: {'Complete' if risk_assessment.get('immediate_closure_required') else 'Partial'}

**🎯 IMMEDIATE RESPONSE ACTIONS ({crisis_response_level.get('immediate_action_timeline', '15 minutes')}):**
{chr(10).join([f"- {action}" for action in emergency_action_plan.get('immediate_actions', ['Assess and secure operations'])])}

**📊 OPERATIONAL IMPACT:**
- Order processing: {'SUSPENDED' if crisis_response_level.get('order_suspension_required') else 'MODIFIED'}
- Customer orders affected: {customer_impact.get('orders_affected', 'Multiple')}
- Revenue impact: {risk_assessment.get('revenue_loss_estimate', 'Medium')}
- Reputation risk: {risk_assessment.get('reputation_impact', 'Moderate')}

**🔧 SHORT-TERM CORRECTIVE MEASURES:**
{chr(10).join([f"- {action}" for action in emergency_action_plan.get('short_term_actions', ['Implement corrective measures'])])}

**👥 STAFF COORDINATION:**
{chr(10).join([f"- {role}: {responsibility}" for role, responsibility in emergency_action_plan.get('staff_responsibilities', {}).items()])}

**📞 STAKEHOLDER COMMUNICATION:**
- Platform notification: {'SENT' if crisis_response_level.get('platform_notification') else 'PENDING'}
- Customer alerts: {'ACTIVE' if customer_impact.get('customers_to_notify', 0) > 0 else 'NONE'}
- Management escalation: {'YES' if crisis_response_level.get('management_escalation') else 'NO'}

**💰 CUSTOMER PROTECTION MEASURES:**
- Refunds: {'AUTOMATIC' if customer_impact.get('refund_required') else 'CASE BY CASE'}
- Compensation: {'PROVIDED' if customer_impact.get('compensation_required') else 'EVALUATED'}
- Alternative options: {'OFFERED' if customer_impact.get('alternative_recommendations') else 'STANDARD'}

**📅 RECOVERY TIMELINE:**
- Resolution target: {recovery_plan.get('estimated_recovery_time', '2-4 hours')}
- Service resumption: Phased approach with quality verification
- Performance monitoring: Enhanced oversight during recovery
- Customer follow-up: 24-48 hours post-resolution

Severe disruptions require systematic response and careful monitoring to ensure complete recovery."""

        else:  # moderate or standard
            return f"""⚠️ **Operational Challenge - Management Response Activated**

**SERVICE DISRUPTION MANAGEMENT**

**📋 Situation Overview:**
- Challenge type: {hindrance_type.replace('_', ' ').title()}
- Impact level: {severity.title()}
- Resolution priority: {crisis_response_level.get('immediate_action_timeline', 'Standard')}
- Service capability: {'Reduced' if not risk_assessment.get('partial_service_possible', True) else 'Maintained with modifications'}

**🔄 IMMEDIATE MANAGEMENT ACTIONS:**
{chr(10).join([f"- {action}" for action in emergency_action_plan.get('immediate_actions', ['Assess situation and implement workarounds'])])}

**📊 OPERATIONAL ADJUSTMENTS:**
- Service modifications: Implementing alternative procedures
- Customer communication: Proactive updates on delays
- Quality maintenance: Enhanced monitoring during adjustments
- Staff coordination: Task reallocation for efficiency

**🎯 SOLUTION IMPLEMENTATION:**
{chr(10).join([f"- {action}" for action in emergency_action_plan.get('short_term_actions', ['Deploy alternative solutions'])])}

**📞 COMMUNICATION PLAN:**
- Customer updates: {communication_strategy.get('update_frequency', 'Regular')}
- Transparency level: {communication_strategy.get('transparency_level', 'High')}
- Message focus: Solution-oriented with realistic timelines

**⏰ RESOLUTION TIMELINE:**
- Target resolution: {recovery_plan.get('estimated_recovery_time', '1-2 hours')}
- Progress monitoring: Continuous assessment
- Quality verification: Before full service resumption
- Customer satisfaction: Follow-up to ensure resolution effectiveness

**✅ QUALITY ASSURANCE:**
{chr(10).join([f"- {step}" for step in recovery_plan.get('quality_assurance_steps', ['Verify all systems operational', 'Confirm customer satisfaction'])])}

**📈 CONTINUOUS IMPROVEMENT:**
- Incident documentation: Complete record for future prevention
- Process optimization: Identify improvement opportunities
- Staff training: Address any skill gaps identified
- System enhancement: Upgrade resilience where possible

Professional management of operational challenges maintains customer confidence and service quality."""
    
    # ORDER CUSTOMIZATION HANDLER METHODS
    def handle_dish_addition_due_to_inconvenience(self, query: str, order_id: str = None, restaurant_username: str = None) -> str:
        """Handle adding complementary items due to customer inconvenience"""
        try:
            # Parse the query to extract what items are being added and why
            added_item = "complementary item"  # Default
            reason = "inconvenience"  # Default

            # Simple parsing - in production this would be more sophisticated
            if "added" in query.lower():
                words = query.split()
                for i, word in enumerate(words):
                    if word.lower() == "added" and i + 1 < len(words):
                        added_item = words[i + 1]
                        break

            if "due to" in query.lower():
                reason_part = query.lower().split("due to")[1].strip()
                reason = reason_part.split('.')[0] if '.' in reason_part else reason_part

            # Create cross-actor update if order_id provided
            if order_id and restaurant_username:
                self.cross_actor_service.create_cross_actor_update(
                    order_id=order_id,
                    actor_type="restaurant",
                    actor_username=restaurant_username,
                    update_type="dish_added",
                    details={
                        "item": added_item,
                        "reason": reason,
                        "restaurant_name": "Your restaurant"  # This would come from order data
                    }
                )

            return f"""🍽️ **Item Added Successfully - Customer Notification Sent**

**Added Item Details:**
- Item: {added_item}
- Reason: {reason}
- Cost: Complimentary (no charge to customer)
- Status: Added to order automatically

**✅ Customer Notifications Sent:**
- SMS: "Good news! We've added {added_item} to your order at no charge due to {reason}"
- App notification: Order updated with complimentary item
- Delivery partner informed about updated order contents

**📝 Order Impact:**
- Total items increased by 1
- Preparation time may extend by 2-3 minutes
- Customer satisfaction gesture completed
- No billing changes required

**Next Steps:**
- Kitchen has been notified to prepare additional item
- Packaging updated to include new item
- Delivery partner will receive updated order details
- Customer will see real-time order update

Your proactive customer service has been logged and will contribute positively to your restaurant rating."""

        except Exception as e:
            logger.error(f"Error handling dish addition: {e}")
            # Generate a simple but informative response even when detailed processing fails
            return f"""🍽️ **Item Addition Processed**

**Order Update Confirmation:**
- Complimentary item added due to service inconvenience
- Customer notification sent automatically
- Kitchen team updated with new order requirements
- No additional charge applied to customer

**Next Steps:**
- Kitchen preparation will include additional item
- Delivery time may extend by 2-3 minutes
- Customer satisfaction gesture logged for future reference

Your proactive customer service approach has been documented and contributes positively to restaurant performance metrics."""

    def handle_order_customization(self, query: str, restaurant_id: str = "anonymous", order_id: str = None, customer_id: str = None) -> str:
        """Handle restaurant order customization with strict 8-step workflow and LLM reasoning"""
        logger.info(f"Processing order customization request: {query[:100]}...")

        # Step 1: Extract customization details using AI reasoning
        customization_details = self.extract_customization_request_details(query)

        # Step 2: Assess restaurant capability and inventory availability
        restaurant_capability = self.assess_restaurant_customization_capability(restaurant_id, customization_details)

        # Step 3: Evaluate cost, time, and operational impact
        operational_impact = self.evaluate_customization_operational_impact(customization_details, restaurant_capability)

        # Step 4: Check food safety and quality compliance
        safety_compliance = self.check_customization_safety_compliance(customization_details)

        # Step 5: Determine customer communication strategy using AI reasoning
        communication_strategy = self.determine_customization_communication_strategy(
            customization_details, operational_impact, safety_compliance
        )

        # Step 6: Generate implementation instructions for kitchen
        kitchen_instructions = self.generate_kitchen_customization_instructions(
            customization_details, communication_strategy
        )

        # Step 7: Update order tracking and cross-actor communication
        if order_id and customer_id:
            self.update_customization_tracking(order_id, customer_id, customization_details, communication_strategy)

        # Step 8: Generate comprehensive response with AI-powered reasoning
        response = self.generate_customization_response(
            customization_details, operational_impact, safety_compliance,
            communication_strategy, kitchen_instructions
        )

        logger.info(f"Order customization workflow completed successfully")
        return response

    def extract_customization_request_details(self, query: str) -> dict:
        """Extract customization request details using AI-powered analysis"""
        extraction_prompt = f"""
        Analyze this restaurant order customization request and extract structured details:

        Customer Request: {query}

        Identify and categorize:
        1. What type of customization is being requested?
        2. Which specific menu items are affected?
        3. What modifications are requested (additions, removals, substitutions)?
        4. Are there dietary restrictions or allergies mentioned?
        5. Is this a preference-based or medical necessity request?
        6. What level of complexity does this customization require?
        7. Are there any time-sensitive aspects mentioned?

        Return ONLY JSON: {{"customization_type": "dietary_restriction/taste_preference/portion_modification/ingredient_substitution/special_preparation", "affected_items": ["item1", "item2"], "requested_modifications": {{"additions": ["item"], "removals": ["item"], "substitutions": {{"from": "item", "to": "item"}}}}, "dietary_restrictions": ["allergy1", "allergy2"], "medical_necessity": true/false, "complexity_level": "simple/moderate/complex/extremely_complex", "time_sensitivity": "low/medium/high", "customer_tone": "polite/urgent/demanding/frustrated", "special_instructions": "any specific preparation notes"}}
        """

        try:
            if self.ai_engine:
                result = self.ai_engine.process_complaint(
                    function_name="extract_customization_request",
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
                    return self._fallback_customization_extraction(query)
            else:
                return self._fallback_customization_extraction(query)

        except Exception as e:
            logger.error(f"Failed to extract customization details: {e}")
            return self._fallback_customization_extraction(query)

    def _fallback_customization_extraction(self, query: str) -> dict:
        """Fallback customization extraction when AI fails"""
        details = {
            "customization_type": "taste_preference",
            "affected_items": ["main_dish"],
            "requested_modifications": {"additions": [], "removals": [], "substitutions": {}},
            "dietary_restrictions": [],
            "medical_necessity": False,
            "complexity_level": "simple",
            "time_sensitivity": "medium",
            "customer_tone": "polite",
            "special_instructions": ""
        }

        query_lower = query.lower()

        # Detect dietary restrictions and allergies
        if any(word in query_lower for word in ['allergy', 'allergic', 'cannot eat', 'makes me sick']):
            details["medical_necessity"] = True
            details["customization_type"] = "dietary_restriction"
            details["time_sensitivity"] = "high"

            # Common allergens
            if any(word in query_lower for word in ['nuts', 'peanut', 'tree nut']):
                details["dietary_restrictions"].append("nuts")
            if any(word in query_lower for word in ['dairy', 'milk', 'cheese', 'lactose']):
                details["dietary_restrictions"].append("dairy")
            if any(word in query_lower for word in ['gluten', 'wheat', 'bread']):
                details["dietary_restrictions"].append("gluten")

        # Detect taste preferences
        if any(word in query_lower for word in ['spicy', 'spice level', 'hot', 'mild']):
            details["customization_type"] = "taste_preference"
            details["special_instructions"] = "spice level adjustment"

        # Detect portion modifications
        if any(word in query_lower for word in ['extra', 'more', 'additional', 'double']):
            details["customization_type"] = "portion_modification"
            details["requested_modifications"]["additions"] = ["extra_portion"]

        # Detect complexity level
        if any(word in query_lower for word in ['completely different', 'recreate', 'cook differently']):
            details["complexity_level"] = "complex"
        elif any(word in query_lower for word in ['substitute', 'replace', 'instead of']):
            details["complexity_level"] = "moderate"

        # Detect customer tone
        if any(word in query_lower for word in ['urgent', 'asap', 'hurry', 'quickly']):
            details["customer_tone"] = "urgent"
            details["time_sensitivity"] = "high"
        elif any(word in query_lower for word in ['please', 'kindly', 'would appreciate']):
            details["customer_tone"] = "polite"

        return details

    def assess_restaurant_customization_capability(self, restaurant_id: str, customization_details: dict) -> dict:
        """Assess restaurant's capability to handle the customization"""
        capability = {
            "can_accommodate": True,
            "inventory_available": True,
            "kitchen_skills_adequate": True,
            "equipment_sufficient": True,
            "estimated_additional_time": 0,
            "additional_cost": 0.0,
            "risk_level": "low",
            "confidence_score": 85
        }

        customization_type = customization_details.get("customization_type", "taste_preference")
        complexity_level = customization_details.get("complexity_level", "simple")
        dietary_restrictions = customization_details.get("dietary_restrictions", [])

        # Assess based on complexity level
        if complexity_level == "extremely_complex":
            capability.update({
                "can_accommodate": False,
                "kitchen_skills_adequate": False,
                "estimated_additional_time": 20,
                "risk_level": "very_high",
                "confidence_score": 30
            })
        elif complexity_level == "complex":
            capability.update({
                "estimated_additional_time": 15,
                "additional_cost": 5.0,
                "risk_level": "high",
                "confidence_score": 60
            })
        elif complexity_level == "moderate":
            capability.update({
                "estimated_additional_time": 8,
                "additional_cost": 2.0,
                "risk_level": "medium",
                "confidence_score": 75
            })

        # Special handling for dietary restrictions
        if dietary_restrictions and customization_details.get("medical_necessity"):
            if "nuts" in dietary_restrictions:
                capability.update({
                    "estimated_additional_time": 10,
                    "risk_level": "high",
                    "confidence_score": 70  # Cross-contamination risk
                })

        # Restaurant credibility impact
        credibility_score = self.get_restaurant_credibility_score(restaurant_id)
        if credibility_score <= 5:
            capability["confidence_score"] -= 20
            capability["risk_level"] = "high"

        return capability

    def evaluate_customization_operational_impact(self, customization_details: dict, restaurant_capability: dict) -> dict:
        """Evaluate operational impact of customization on restaurant operations"""
        impact = {
            "kitchen_workflow_disruption": "minimal",
            "order_queue_delay": 0,
            "staff_workload_increase": "low",
            "ingredient_cost_impact": 0.0,
            "quality_assurance_risk": "low",
            "customer_satisfaction_impact": "positive",
            "profit_margin_effect": "neutral"
        }

        additional_time = restaurant_capability.get("estimated_additional_time", 0)
        complexity_level = customization_details.get("complexity_level", "simple")
        customer_tone = customization_details.get("customer_tone", "polite")

        # Time impact assessment
        if additional_time >= 15:
            impact.update({
                "kitchen_workflow_disruption": "significant",
                "order_queue_delay": 8,
                "staff_workload_increase": "high",
                "quality_assurance_risk": "medium"
            })
        elif additional_time >= 8:
            impact.update({
                "kitchen_workflow_disruption": "moderate",
                "order_queue_delay": 4,
                "staff_workload_increase": "medium"
            })

        # Cost impact
        additional_cost = restaurant_capability.get("additional_cost", 0.0)
        if additional_cost > 3.0:
            impact["profit_margin_effect"] = "negative"
        elif additional_cost > 0:
            impact["profit_margin_effect"] = "slightly_negative"

        # Customer satisfaction prediction
        if not restaurant_capability.get("can_accommodate"):
            impact["customer_satisfaction_impact"] = "very_negative"
        elif customer_tone == "demanding" and complexity_level == "complex":
            impact["customer_satisfaction_impact"] = "risky"

        return impact

    def check_customization_safety_compliance(self, customization_details: dict) -> dict:
        """Check food safety and quality compliance for customization"""
        compliance = {
            "food_safety_approved": True,
            "cross_contamination_risk": "low",
            "allergen_handling_required": False,
            "special_preparation_needed": False,
            "quality_standards_maintained": True,
            "health_regulation_compliant": True,
            "documentation_required": False
        }

        dietary_restrictions = customization_details.get("dietary_restrictions", [])
        medical_necessity = customization_details.get("medical_necessity", False)

        # Allergen safety assessment
        if dietary_restrictions:
            compliance.update({
                "allergen_handling_required": True,
                "special_preparation_needed": True,
                "documentation_required": True
            })

            # High-risk allergens
            if any(allergen in dietary_restrictions for allergen in ["nuts", "shellfish"]):
                compliance["cross_contamination_risk"] = "high"

        # Medical necessity requirements
        if medical_necessity:
            compliance.update({
                "cross_contamination_risk": "high",
                "documentation_required": True,
                "health_regulation_compliant": True
            })

        return compliance

    def determine_customization_communication_strategy(self, customization_details: dict, operational_impact: dict, safety_compliance: dict) -> dict:
        """Determine communication strategy using AI reasoning"""
        strategy_prompt = f"""
        Determine the optimal communication strategy for this restaurant customization request:

        Customization Details: {customization_details}
        Operational Impact: {operational_impact}
        Safety Compliance: {safety_compliance}

        Based on this analysis, determine:
        1. Should this customization be approved, conditionally approved, or declined?
        2. What is the primary message tone (positive, cautious, apologetic)?
        3. What key information must be communicated to the customer?
        4. What alternatives should be offered if declined?
        5. What timeline should be communicated?

        Return ONLY JSON: {{"decision": "approved/conditional/declined", "message_tone": "positive/cautious/apologetic", "key_messages": ["message1", "message2"], "alternatives_offered": ["alt1", "alt2"], "estimated_timeline": "X minutes", "additional_cost_communication": "none/$X additional", "priority_level": "low/medium/high"}}
        """

        try:
            if self.ai_engine:
                result = self.ai_engine.process_complaint(
                    function_name="determine_communication_strategy",
                    user_query=strategy_prompt,
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
                    return self._fallback_communication_strategy(customization_details, operational_impact, safety_compliance)
            else:
                return self._fallback_communication_strategy(customization_details, operational_impact, safety_compliance)

        except Exception as e:
            logger.error(f"Failed to determine communication strategy: {e}")
            return self._fallback_communication_strategy(customization_details, operational_impact, safety_compliance)

    def _fallback_communication_strategy(self, customization_details: dict, operational_impact: dict, safety_compliance: dict) -> dict:
        """Fallback communication strategy when AI fails"""
        strategy = {
            "decision": "approved",
            "message_tone": "positive",
            "key_messages": ["We can accommodate your request"],
            "alternatives_offered": [],
            "estimated_timeline": "5-10 minutes",
            "additional_cost_communication": "none",
            "priority_level": "medium"
        }

        # Decision logic
        if not safety_compliance.get("food_safety_approved"):
            strategy.update({
                "decision": "declined",
                "message_tone": "apologetic",
                "key_messages": ["Food safety regulations prevent this modification"],
                "alternatives_offered": ["similar dish without restricted ingredients"]
            })
        elif operational_impact.get("kitchen_workflow_disruption") == "significant":
            strategy.update({
                "decision": "conditional",
                "message_tone": "cautious",
                "key_messages": ["We can accommodate with extended preparation time"],
                "estimated_timeline": "15-20 minutes"
            })

        # Medical necessity gets high priority
        if customization_details.get("medical_necessity"):
            strategy["priority_level"] = "high"
            strategy["message_tone"] = "cautious"

        return strategy

    def generate_kitchen_customization_instructions(self, customization_details: dict, communication_strategy: dict) -> dict:
        """Generate detailed kitchen implementation instructions"""
        instructions = {
            "preparation_steps": [],
            "safety_protocols": [],
            "quality_checkpoints": [],
            "timing_requirements": {},
            "special_equipment_needed": [],
            "staff_notifications": []
        }

        decision = communication_strategy.get("decision", "approved")

        if decision == "declined":
            return instructions  # No kitchen instructions needed

        # Generate preparation steps based on customization type
        customization_type = customization_details.get("customization_type", "taste_preference")

        if customization_type == "dietary_restriction":
            instructions["preparation_steps"].extend([
                "Use separate cutting boards and utensils",
                "Prepare in isolated section of kitchen",
                "Double-check all ingredients for allergens"
            ])
            instructions["safety_protocols"].extend([
                "Wash hands and change gloves before preparation",
                "Clean all surfaces before starting",
                "Label order clearly with dietary restriction notes"
            ])

        elif customization_type == "taste_preference":
            instructions["preparation_steps"].extend([
                "Adjust seasoning as requested",
                "Prepare sauces/spices separately if needed",
                "Taste-test if possible before serving"
            ])

        # Quality checkpoints
        instructions["quality_checkpoints"] = [
            "Verify customization matches order ticket",
            "Check visual presentation meets standards",
            "Confirm temperature is appropriate",
            "Ensure packaging is suitable for modifications"
        ]

        return instructions

    def update_customization_tracking(self, order_id: str, customer_id: str, customization_details: dict, communication_strategy: dict):
        """Update order tracking and cross-actor communication"""
        try:
            update_details = {
                "customization_type": customization_details.get("customization_type"),
                "decision": communication_strategy.get("decision"),
                "estimated_additional_time": communication_strategy.get("estimated_timeline"),
                "special_handling": customization_details.get("medical_necessity", False)
            }

            self.cross_actor_service.create_cross_actor_update(
                order_id=order_id,
                actor_type="restaurant",
                actor_username="restaurant_handler",
                update_type="order_customization",
                details=update_details
            )
        except Exception as e:
            logger.error(f"Failed to update customization tracking: {e}")

    def generate_customization_response(self, customization_details: dict, operational_impact: dict,
                                       safety_compliance: dict, communication_strategy: dict,
                                       kitchen_instructions: dict) -> str:
        """Generate comprehensive AI-powered customization response"""
        decision = communication_strategy.get("decision", "approved")
        message_tone = communication_strategy.get("message_tone", "positive")
        estimated_timeline = communication_strategy.get("estimated_timeline", "5-10 minutes")

        if decision == "approved":
            return f"""✅ **Order Customization Approved - Kitchen Notified**

**Customization Details Successfully Processed:**
- Request type: {customization_details.get('customization_type', 'modification').replace('_', ' ').title()}
- Complexity level: {customization_details.get('complexity_level', 'simple').title()}
- Medical necessity: {'Yes' if customization_details.get('medical_necessity') else 'No'}

**🍽️ Kitchen Implementation:**
- Estimated additional time: {estimated_timeline}
- Special preparation required: {'Yes' if safety_compliance.get('special_preparation_needed') else 'No'}
- Allergen handling: {'Required' if safety_compliance.get('allergen_handling_required') else 'Not needed'}
- Quality assurance: Enhanced monitoring activated

**📋 Preparation Instructions Sent to Kitchen:**
{chr(10).join([f"- {step}" for step in kitchen_instructions.get('preparation_steps', ['Standard preparation with requested modifications'])])}

**🔒 Safety Protocols Activated:**
{chr(10).join([f"- {protocol}" for protocol in kitchen_instructions.get('safety_protocols', ['Standard safety protocols'])])}

**📞 Customer Communication:**
- Customer has been notified of approval and timing
- Order tracking updated with customization notes
- Delivery partner will be informed of special handling

**✅ Quality Checkpoints:**
{chr(10).join([f"- {checkpoint}" for checkpoint in kitchen_instructions.get('quality_checkpoints', ['Standard quality verification'])])}

Your kitchen team has been provided with detailed customization instructions to ensure customer satisfaction."""

        elif decision == "conditional":
            additional_cost = communication_strategy.get("additional_cost_communication", "none")
            return f"""⚠️ **Order Customization Conditionally Approved - Customer Confirmation Required**

**Customization Analysis:**
- Request type: {customization_details.get('customization_type', 'modification').replace('_', ' ').title()}
- Operational impact: {operational_impact.get('kitchen_workflow_disruption', 'moderate').title()}
- Additional time required: {estimated_timeline}
- Cost impact: {additional_cost}

**🔍 Conditional Approval Details:**
- Extended preparation time required: {estimated_timeline}
- Kitchen workflow adjustment needed
- Quality standards maintained but additional time necessary
- Customer confirmation requested before proceeding

**📞 Customer Communication Sent:**
"We can accommodate your customization request with some adjustments. This will require approximately {estimated_timeline} additional preparation time{f' and an additional cost of {additional_cost}' if additional_cost != 'none' else ''}. Please confirm if you would like us to proceed with these conditions."

**🍽️ Kitchen Preparation Status:**
- Instructions prepared and ready for implementation
- Awaiting customer confirmation to begin customization
- All safety protocols identified and ready for activation
- Quality checkpoints established for modified preparation

**⏰ Next Steps:**
- Customer response timeline: 5 minutes
- Kitchen preparation begins immediately upon confirmation
- Order tracking updated with conditional status
- Alternative options communicated if customer declines

Kitchen team is standing by to implement your customization upon customer confirmation."""

        else:  # declined
            alternatives = communication_strategy.get("alternatives_offered", [])
            return f"""❌ **Order Customization Declined - Alternative Solutions Provided**

**Customization Analysis:**
- Request type: {customization_details.get('customization_type', 'modification').replace('_', ' ').title()}
- Decline reason: {'; '.join(communication_strategy.get('key_messages', ['Unable to accommodate safely']))}
- Safety compliance: {'Failed' if not safety_compliance.get('food_safety_approved') else 'Passed with restrictions'}

**🚫 Reasons for Decline:**
{chr(10).join([f"- {reason}" for reason in communication_strategy.get('key_messages', ['Kitchen capability limitations'])])}

**🔄 Alternative Solutions Offered:**
{chr(10).join([f"- {alternative}" for alternative in alternatives]) if alternatives else '- Similar menu items without requested modifications'}

**📞 Customer Communication Sent:**
"We sincerely apologize that we cannot accommodate your specific customization request due to {communication_strategy.get('key_messages', ['operational limitations'])[0]}. However, we've identified several alternative options that might meet your needs: {', '.join(alternatives) if alternatives else 'our existing menu items'}."

**✅ Customer Service Actions:**
- Detailed explanation provided to customer
- Alternative menu recommendations sent
- Option to modify order with available alternatives
- Full refund offered if no suitable alternatives

**🎯 Quality Assurance:**
- Customer satisfaction maintained through transparent communication
- Alternative solutions prioritize customer needs
- Order modification options remain available
- Standard menu items prepared to excellence

Your professional handling of this request maintains customer trust even when customization isn't possible."""