"""
Grab Mart Dark Store Handler - Combined
Handles all dark store warehouse operational issues and management
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


class DarkStoreHandler:
    """Combined dark store warehouse operational management and issue resolution"""

    def __init__(self, groq_api_key: str = None):
        self.service = "grab_mart"
        self.actor = "dark_house"
        self.handler_type = "dark_store_handler"

        # Initialize AI engine for structured analysis
        self.ai_engine = None
        try:
            from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine
            self.ai_engine = EnhancedAgenticAIEngine(groq_api_key)
            logger.info("AI engine initialized successfully for dark store handler")
        except Exception as e:
            logger.warning(f"AI engine initialization failed: {e}. Falling back to rule-based processing.")
            self.ai_engine = None

        # Initialize API integrations for predictive analysis
        self.weather_api = WeatherAPI()
        self.maps_api = GoogleMapsAPI()

        # Initialize cross-actor update service
        self.cross_actor_service = CrossActorUpdateService()

    # ===== STRICT WORKFLOW METHODS FOR DARK STORE =====

    def get_dark_store_credibility_score(self, store_id: str) -> int:
        """Calculate dark store credibility score based on warehouse performance history"""
        import sqlite3
        import os
        from datetime import datetime, timedelta

        base_score = 7  # Start with neutral-high credibility

        # Handle anonymous or invalid store IDs
        if not store_id or store_id == "anonymous":
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
                return self._get_simulated_dark_store_credibility_score(store_id)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get dark store's current credibility score from users table
            cursor.execute('''
                SELECT credibility_score, created_at
                FROM users
                WHERE username = ? AND user_type = 'dark_house'
            ''', (store_id,))

            user_result = cursor.fetchone()
            if user_result:
                base_score = user_result[0]
                created_at = user_result[1]
            else:
                base_score = 7  # Default for new dark stores
                created_at = None

            # Get comprehensive dark store order performance (last 90 days)
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
                WHERE restaurant_name = ? AND service = 'grab_mart'
                AND date >= date('now', '-90 days')
            ''', (f"Dark Store {store_id}",))

            result = cursor.fetchone()
            if result:
                total_orders, completed_orders, cancelled_orders, refunded_orders, avg_order_value, first_order_date, last_order_date = result

                if total_orders > 0:
                    completion_rate = completed_orders / total_orders
                    cancellation_rate = cancelled_orders / total_orders
                    refund_rate = refunded_orders / total_orders if refunded_orders else 0

                    # Adjust score based on completion rate (stricter for warehouses)
                    if completion_rate >= 0.99:
                        base_score += 3
                    elif completion_rate >= 0.97:
                        base_score += 2
                    elif completion_rate >= 0.95:
                        base_score += 1
                    elif completion_rate < 0.85:
                        base_score -= 3
                    elif completion_rate < 0.90:
                        base_score -= 2

                    # Adjust based on cancellation rate (warehouses should have very low cancellations)
                    if cancellation_rate > 0.10:  # 10% cancellation rate is bad for warehouses
                        base_score -= 4
                    elif cancellation_rate > 0.05:
                        base_score -= 2
                    elif cancellation_rate > 0.02:
                        base_score -= 1
                    elif cancellation_rate <= 0.01:  # Very low cancellation rate
                        base_score += 1

                    # Adjust based on refund rate (indicator of picking accuracy)
                    if refund_rate > 0.08:  # 8% refund rate is concerning for warehouses
                        base_score -= 3
                    elif refund_rate > 0.04:
                        base_score -= 2
                    elif refund_rate > 0.02:
                        base_score -= 1

                    # Adjust based on order volume (warehouse efficiency)
                    if total_orders >= 800:
                        base_score += 3  # High volume, efficient warehouse
                    elif total_orders >= 400:
                        base_score += 2
                    elif total_orders >= 200:
                        base_score += 1
                    elif total_orders < 50:
                        base_score -= 1  # New warehouse, less predictable

                    # Adjust based on average order value
                    if avg_order_value and avg_order_value >= 120:
                        base_score += 1  # Higher value orders typically have higher standards
                    elif avg_order_value and avg_order_value >= 80:
                        base_score += 0.5

            # Warehouse tenure bonus (longer operating = more stable)
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
                    COUNT(CASE WHEN complaint_type LIKE '%damage%' OR complaint_details LIKE '%damage%' OR complaint_details LIKE '%broken%' THEN 1 END) as damage_complaints,
                    COUNT(CASE WHEN complaint_type LIKE '%missing%' OR complaint_details LIKE '%missing%' OR complaint_details LIKE '%wrong%' THEN 1 END) as picking_complaints,
                    COUNT(CASE WHEN complaint_type LIKE '%delay%' OR complaint_details LIKE '%late%' OR complaint_details LIKE '%slow%' THEN 1 END) as timing_complaints
                FROM complaints
                WHERE username = ? AND service = 'grab_mart' AND user_type = 'dark_house'
                AND created_at >= datetime('now', '-90 days')
            ''', (store_id,))

            complaint_result = cursor.fetchone()
            if complaint_result:
                total_complaints, quality_complaints, damage_complaints, picking_complaints, timing_complaints = complaint_result

                # Heavy penalties for damage complaints (warehouse handling issues)
                if damage_complaints > 3:
                    base_score -= 5
                elif damage_complaints > 2:
                    base_score -= 3
                elif damage_complaints == 1:
                    base_score -= 2

                # Penalties for quality complaints (expiry, freshness)
                if quality_complaints > 10:
                    base_score -= 4
                elif quality_complaints > 6:
                    base_score -= 3
                elif quality_complaints > 3:
                    base_score -= 2
                elif quality_complaints > 1:
                    base_score -= 1

                # Penalties for picking complaints (accuracy issues)
                if picking_complaints > 8:
                    base_score -= 3
                elif picking_complaints > 5:
                    base_score -= 2
                elif picking_complaints > 2:
                    base_score -= 1

                # Penalties for timing complaints (warehouse efficiency)
                if timing_complaints > 12:
                    base_score -= 2
                elif timing_complaints > 6:
                    base_score -= 1

                # Overall complaint frequency penalty
                if total_complaints > 25:
                    base_score -= 3
                elif total_complaints > 15:
                    base_score -= 2
                elif total_complaints > 8:
                    base_score -= 1

            # Check recent complaint resolution rate
            cursor.execute('''
                SELECT
                    COUNT(*) as total_recent_complaints,
                    COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_complaints
                FROM complaints
                WHERE username = ? AND service = 'grab_mart' AND user_type = 'dark_house'
                AND created_at >= datetime('now', '-30 days')
            ''', (store_id,))

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
            logger.error(f"Error calculating dark store credibility score: {e}")
            return self._get_simulated_dark_store_credibility_score(store_id)

        # Ensure score is between 1-10
        final_score = max(1, min(10, int(base_score)))

        # Update the credibility score in the database if it has changed significantly
        self._update_dark_store_credibility_score_if_changed(store_id, final_score)

        return final_score

    def _update_dark_store_credibility_score_if_changed(self, store_id: str, new_score: int) -> None:
        """Update dark store's credibility score in database if it has changed significantly"""
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

            # Update the credibility score for dark store
            cursor.execute('''
                UPDATE users
                SET credibility_score = ?
                WHERE username = ? AND user_type = 'dark_house'
            ''', (new_score, store_id))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error updating dark store credibility score: {e}")

    def _get_simulated_dark_store_credibility_score(self, store_id: str) -> int:
        """Fallback simulated credibility scoring when database is unavailable"""
        base_score = 7

        # Simulate some variation based on store_id characteristics
        if "test" in store_id.lower():
            base_score -= 2  # Test stores have lower credibility

        # Simulate based on store number (if extractable)
        try:
            if any(char.isdigit() for char in store_id):
                store_num = int(''.join(filter(str.isdigit, store_id)))
                if store_num <= 5:  # Lower numbered stores are more established
                    base_score += 1
                elif store_num > 20:  # Higher numbers might be newer
                    base_score -= 0.5
        except:
            pass

        # Simulate some randomness based on hash for consistency
        hash_modifier = (hash(store_id) % 3) - 1  # -1, 0, or 1
        base_score += hash_modifier * 0.5

        return max(1, min(10, int(base_score)))

    # PRODUCT QUALITY HANDLER METHODS
    def handle_product_quality_violation(self, query: str, store_id: str = "anonymous", image_data: str = None, order_id: str = None) -> str:
        """Handle dark store product quality violations with strict 6-step workflow"""
        logger.info(f"Processing product quality violation: {query[:100]}...")

        # Step 1: Extract product quality violation details
        violation_details = self.extract_product_quality_violation_details(query)

        # Step 2: Validate violation with evidence (require image for serious violations)
        if violation_details["severity"] == "severe" and not image_data:
            return "📷 For product quality violations, please upload a photo of the product so we can verify the quality against our standards."

        # Step 3: Check dark store credibility and violation history
        credibility_score = self.get_dark_store_credibility_score(store_id)
        violation_history = self.check_product_quality_violation_history(store_id)
        logger.info(f"Dark store credibility: {credibility_score}/10, History: {violation_history}")

        # Step 4: Assess violation severity and impact on customer
        violation_assessment = self.assess_product_quality_violation_severity(violation_details, credibility_score, violation_history)
        logger.info(f"Violation assessment: {violation_assessment}")

        # Step 5: Determine corrective actions and penalties
        corrective_actions = self.determine_product_quality_corrective_actions(violation_assessment, credibility_score)
        logger.info(f"Corrective actions: {corrective_actions}")

        # Step 6: Generate comprehensive response with improvement plan
        response = self.generate_product_quality_violation_response(corrective_actions, violation_details, violation_assessment)
        logger.info(f"Product quality violation response generated successfully")

        return response

    def extract_product_quality_violation_details(self, query: str) -> dict:
        """Extract product quality violation details from complaint using structured AI analysis"""
        extraction_prompt = f"""
        Analyze this dark store product quality violation complaint and extract key details:

        Complaint: {query}

        Identify:
        1. What type of product quality violation is described?
        2. How severe is the violation based on customer language?
        3. What category of product is affected?
        4. Is this described as a repeat occurrence?
        5. What is the impact level on customer satisfaction?

        Return ONLY JSON: {{"violation_type": "expired_product/damaged_product/wrong_product/missing_product/poor_quality", "severity": "minor/moderate/severe/critical", "product_category": "fresh_produce/dairy/frozen/packaged_goods/household_items", "repeat_occurrence": true/false, "customer_satisfaction_impact": "low/moderate/high/severe", "specific_products": ["product1", "product2"], "evidence_level": "customer_claim/photo_provided/receipt_provided"}}
        """

        try:
            # Use AI engine to extract structured data if available
            if self.ai_engine:
                result = self.ai_engine.process_complaint(
                    function_name="extract_product_quality_violation",
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
                    return self._fallback_product_quality_extraction(query)
            else:
                return self._fallback_product_quality_extraction(query)

        except Exception as e:
            logger.error(f"Failed to extract product quality violation details: {e}")
            return self._fallback_product_quality_extraction(query)

    def _fallback_product_quality_extraction(self, query: str) -> dict:
        """Fallback method for product quality violation extraction when AI fails"""
        details = {
            "violation_type": "poor_quality",
            "severity": "moderate",
            "product_category": "packaged_goods",
            "customer_satisfaction_impact": "moderate",
            "repeat_occurrence": False,
            "specific_products": [],
            "evidence_level": "customer_claim"
        }

        query_lower = query.lower()

        # Determine violation type
        if any(word in query_lower for word in ['expired', 'expiry', 'out of date', 'old']):
            details["violation_type"] = "expired_product"
            details["severity"] = "severe"
        elif any(word in query_lower for word in ['damaged', 'broken', 'crushed', 'leaking']):
            details["violation_type"] = "damaged_product"
            details["severity"] = "moderate"
        elif any(word in query_lower for word in ['wrong', 'different', 'not what I ordered']):
            details["violation_type"] = "wrong_product"
        elif any(word in query_lower for word in ['missing', 'forgot', 'not included']):
            details["violation_type"] = "missing_product"

        # Severity assessment
        if any(word in query_lower for word in ['terrible', 'disgusting', 'unusable', 'inedible']):
            details["severity"] = "severe"
        elif any(word in query_lower for word in ['poor', 'bad', 'not good']):
            details["severity"] = "moderate"
        elif any(word in query_lower for word in ['slightly', 'minor', 'small issue']):
            details["severity"] = "minor"

        # Identify product category
        if any(word in query_lower for word in ['vegetables', 'fruits', 'fresh', 'produce']):
            details["product_category"] = "fresh_produce"
        elif any(word in query_lower for word in ['milk', 'cheese', 'yogurt', 'dairy']):
            details["product_category"] = "dairy"
        elif any(word in query_lower for word in ['frozen', 'ice cream', 'freezer']):
            details["product_category"] = "frozen"
        elif any(word in query_lower for word in ['cleaning', 'detergent', 'household']):
            details["product_category"] = "household_items"

        # Check for repeat occurrence indicators
        if any(word in query_lower for word in ['again', 'always', 'every time', 'repeatedly']):
            details["repeat_occurrence"] = True

        # Check for evidence level
        if any(word in query_lower for word in ['photo', 'picture', 'image']):
            details["evidence_level"] = "photo_provided"
        elif any(word in query_lower for word in ['receipt', 'bill', 'invoice']):
            details["evidence_level"] = "receipt_provided"

        return details

    def check_product_quality_violation_history(self, store_id: str) -> dict:
        """Check dark store's product quality violation history with database analysis"""
        import sqlite3
        import os
        from datetime import datetime, timedelta

        history_data = {
            "pattern_type": "NORMAL_QUALITY_PATTERN",
            "violation_count_30_days": 0,
            "violation_count_90_days": 0,
            "severity_trend": "stable",
            "customer_complaints": 0,
            "resolution_rate": 100.0
        }

        if store_id == "anonymous":
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
                return self._get_simulated_quality_history(store_id)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get product quality violation complaints in last 30 days
            cursor.execute('''
                SELECT COUNT(*)
                FROM complaints
                WHERE username = ? AND service = 'grab_mart' AND user_type = 'dark_house'
                AND (complaint_type LIKE '%quality%' OR complaint_details LIKE '%quality%' OR
                     complaint_details LIKE '%expired%' OR complaint_details LIKE '%damaged%')
                AND created_at >= datetime('now', '-30 days')
            ''', (store_id,))

            violations_30_days = cursor.fetchone()[0] if cursor.fetchone() else 0
            history_data["violation_count_30_days"] = violations_30_days

            # Get product quality violation complaints in last 90 days
            cursor.execute('''
                SELECT COUNT(*)
                FROM complaints
                WHERE username = ? AND service = 'grab_mart' AND user_type = 'dark_house'
                AND (complaint_type LIKE '%quality%' OR complaint_details LIKE '%quality%' OR
                     complaint_details LIKE '%expired%' OR complaint_details LIKE '%damaged%')
                AND created_at >= datetime('now', '-90 days')
            ''', (store_id,))

            violations_90_days = cursor.fetchone()[0] if cursor.fetchone() else 0
            history_data["violation_count_90_days"] = violations_90_days

            # Determine pattern type based on violation frequency
            if violations_30_days >= 6:
                history_data["pattern_type"] = "FREQUENT_QUALITY_ISSUES"
            elif violations_30_days >= 4:
                history_data["pattern_type"] = "MODERATE_QUALITY_CONCERNS"
            elif violations_90_days >= 12:
                history_data["pattern_type"] = "RECURRING_QUALITY_PATTERN"
            else:
                history_data["pattern_type"] = "NORMAL_QUALITY_PATTERN"

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
            logger.error(f"Error checking product quality violation history: {e}")
            return self._get_simulated_quality_history(store_id)

        return history_data

    def _get_simulated_quality_history(self, store_id: str) -> dict:
        """Fallback simulated quality history when database is unavailable"""
        base_data = {
            "pattern_type": "NORMAL_QUALITY_PATTERN",
            "violation_count_30_days": 0,
            "violation_count_90_days": 0,
            "severity_trend": "stable",
            "customer_complaints": 0,
            "resolution_rate": 95.0
        }

        if "test" in store_id.lower():
            base_data.update({
                "pattern_type": "FREQUENT_QUALITY_ISSUES",
                "violation_count_30_days": 8,
                "violation_count_90_days": 20,
                "severity_trend": "worsening"
            })

        return base_data

    def assess_product_quality_violation_severity(self, violation_details: dict, credibility_score: int, violation_history: dict) -> dict:
        """Assess product quality violation severity and impact using strict decision matrix"""
        severity = violation_details.get("severity", "moderate")
        repeat_occurrence = violation_details.get("repeat_occurrence", False)
        evidence_level = violation_details.get("evidence_level", "customer_claim")
        pattern_type = violation_history.get("pattern_type", "NORMAL_QUALITY_PATTERN")
        violation_count_30_days = violation_history.get("violation_count_30_days", 0)

        assessment = {
            "violation_level": "MODERATE",
            "customer_compensation_required": True,
            "dark_store_penalty_required": False,
            "training_required": False,
            "audit_required": False,
            "immediate_action_required": False,
            "platform_visibility_impact": 0,
            "supplier_notification": False
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
        if evidence_level == "receipt_provided":
            violation_score += 4
        elif evidence_level == "photo_provided":
            violation_score += 3
        elif evidence_level == "customer_claim":
            violation_score += 1

        # History pattern scoring
        if pattern_type == "FREQUENT_QUALITY_ISSUES":
            violation_score += 8
        elif pattern_type == "RECURRING_QUALITY_PATTERN":
            violation_score += 6
        elif pattern_type == "MODERATE_QUALITY_CONCERNS":
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
        if violation_count_30_days >= 6:
            violation_score += 6
        elif violation_count_30_days >= 4:
            violation_score += 4
        elif violation_count_30_days >= 2:
            violation_score += 2

        # Apply strict decision matrix based on total violation score
        if violation_score >= 20:
            assessment.update({
                "violation_level": "CRITICAL_PATTERN",
                "dark_store_penalty_required": True,
                "training_required": True,
                "audit_required": True,
                "immediate_action_required": True,
                "platform_visibility_impact": 40,
                "supplier_notification": True
            })
        elif violation_score >= 15:
            assessment.update({
                "violation_level": "SEVERE_PATTERN",
                "dark_store_penalty_required": True,
                "training_required": True,
                "audit_required": True,
                "immediate_action_required": True,
                "platform_visibility_impact": 25
            })
        elif violation_score >= 10:
            assessment.update({
                "violation_level": "PATTERN_VIOLATION",
                "dark_store_penalty_required": True,
                "training_required": True,
                "audit_required": True,
                "platform_visibility_impact": 15
            })
        elif violation_score >= 6:
            assessment.update({
                "violation_level": "SEVERE",
                "dark_store_penalty_required": True,
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

        logger.info(f"Product quality violation assessment - Score: {violation_score}, Level: {assessment['violation_level']}")
        return assessment

    def determine_product_quality_corrective_actions(self, violation_assessment: dict, credibility_score: int) -> dict:
        """Determine corrective actions for product quality violations using strict escalation matrix"""
        violation_level = violation_assessment.get("violation_level", "MODERATE")
        immediate_action_required = violation_assessment.get("immediate_action_required", False)
        platform_visibility_impact = violation_assessment.get("platform_visibility_impact", 0)

        actions = {
            "customer_refund": 0.0,
            "dark_store_penalty": 0.0,
            "training_program": "none",
            "audit_schedule": "none",
            "visibility_reduction": platform_visibility_impact,
            "suspension_days": 0,
            "compliance_bond": 0.0,
            "emergency_protocols": False,
            "supplier_audit_required": False,
            "inventory_removal_hours": 0
        }

        # Strict escalation matrix based on violation level
        if violation_level == "CRITICAL_PATTERN":
            actions.update({
                "customer_refund": 150.0,  # Full refund + compensation
                "dark_store_penalty": 800.0,
                "training_program": "emergency_comprehensive_overhaul",
                "audit_schedule": "immediate",
                "suspension_days": 3,
                "compliance_bond": 3000.0,
                "emergency_protocols": True,
                "supplier_audit_required": True,
                "inventory_removal_hours": 6
            })
        elif violation_level == "SEVERE_PATTERN":
            actions.update({
                "customer_refund": 120.0,
                "dark_store_penalty": 500.0,
                "training_program": "comprehensive_quality_overhaul",
                "audit_schedule": "within_24_hours",
                "suspension_days": 2,
                "compliance_bond": 1500.0,
                "emergency_protocols": True,
                "inventory_removal_hours": 4
            })
        elif violation_level == "PATTERN_VIOLATION":
            actions.update({
                "customer_refund": 100.0,
                "dark_store_penalty": 300.0,
                "training_program": "comprehensive_quality_control",
                "audit_schedule": "within_48_hours",
                "suspension_days": 1,
                "compliance_bond": 800.0,
                "inventory_removal_hours": 2
            })
        elif violation_level == "SEVERE":
            actions.update({
                "customer_refund": 100.0,
                "dark_store_penalty": 200.0,
                "training_program": "mandatory_quality_control",
                "audit_schedule": "within_72_hours",
                "compliance_bond": 400.0
            })
        elif violation_level == "MODERATE":
            actions.update({
                "customer_refund": 75.0,
                "dark_store_penalty": 100.0,
                "training_program": "quality_guidelines_review",
                "audit_schedule": "within_1_week"
            })
        elif violation_level == "MINOR":
            actions.update({
                "customer_refund": 50.0,
                "dark_store_penalty": 50.0,
                "training_program": "quality_awareness_session",
                "audit_schedule": "within_2_weeks"
            })

        # Adjust based on credibility score (lower credibility = harsher penalties)
        if credibility_score <= 3:
            actions["dark_store_penalty"] *= 1.5
            actions["compliance_bond"] *= 1.5
        elif credibility_score <= 5:
            actions["dark_store_penalty"] *= 1.25
            actions["compliance_bond"] *= 1.25
        elif credibility_score >= 8:
            actions["dark_store_penalty"] *= 0.8
            actions["compliance_bond"] *= 0.8

        return actions

    def generate_product_quality_violation_response(self, corrective_actions: dict, violation_details: dict, violation_assessment: dict) -> str:
        """Generate comprehensive response for product quality violations"""
        violation_level = violation_assessment.get("violation_level", "MODERATE")
        customer_refund = corrective_actions.get("customer_refund", 0.0)
        dark_store_penalty = corrective_actions.get("dark_store_penalty", 0.0)

        if violation_level == "SEVERE":
            return f"""📦 **SEVERE PRODUCT QUALITY VIOLATION - IMMEDIATE ACTION REQUIRED**

**Critical Quality Breach Detected**

**Violation Analysis:**
- Severity: {violation_details.get('severity', 'severe').upper()}
- Product category: {violation_details.get('product_category', 'packaged_goods')}
- Customer impact: Significant dissatisfaction
- Violation level: {violation_level}

**✅ IMMEDIATE CUSTOMER RESOLUTION:**
💰 **Customer refund:** {customer_refund}% of order value processed
📦 **Replacement products:** Offered at no charge
📞 **Personal apology:** Direct contact with customer
⭐ **Service recovery:** Premium customer status upgrade

**⚠️ DARK STORE ACCOUNTABILITY:**
💸 **Penalty imposed:** ${dark_store_penalty} quality violation fee
📉 **Platform visibility:** Reduced by {corrective_actions.get('visibility_reduction', 0)}% for 7 days
🎯 **Order priority:** Lowered until compliance restored
📊 **Rating impact:** Immediate quality score reduction

**🎓 MANDATORY CORRECTIVE MEASURES:**
1. **IMMEDIATE (0-4 hours):**
   - Warehouse supervisor meeting required
   - Product batch inspection mandatory
   - Current inventory quality audit
   - Staff quality training session

2. **SHORT-TERM (24-48 hours):**
   - Mandatory quality control certification
   - Warehouse workflow process review
   - Quality control system implementation
   - Management oversight protocols

3. **ONGOING (1-2 weeks):**
   - Daily quality compliance monitoring
   - Weekly quality assessments
   - Customer feedback tracking
   - Performance improvement reporting

**📋 COMPLIANCE REQUIREMENTS:**
- Quality compliance audit: {corrective_actions.get('audit_schedule', 'immediate')}
- Training completion deadline: 48 hours
- Quality improvement plan: Required within 72 hours
- Performance review: 2 weeks

**❌ CONSEQUENCES OF NON-COMPLIANCE:**
- Further visibility reduction (up to 50%)
- Temporary platform suspension consideration
- Increased penalty fees
- Mandatory quality coaching program

This is a serious quality breach that requires immediate attention and sustained improvement. Your dark store's reputation and customer trust depend on consistent product quality standards."""

        elif violation_level == "PATTERN_VIOLATION":
            return f"""📦 **PATTERN VIOLATION - SYSTEMATIC QUALITY CONTROL FAILURE**

**Recurring Quality Issue Identified**

**Pattern Analysis:**
- Multiple product quality violations detected
- Systematic quality control failure
- Customer trust significantly impacted
- Immediate intervention required

**✅ CUSTOMER RESOLUTION:**
💰 **Customer refund:** {customer_refund}% of order value
📦 **Goodwill gesture:** Additional products or credit
📞 **Service recovery:** Direct warehouse manager contact
⭐ **Loyalty program:** Bonus credits for inconvenience

**⚠️ ESCALATED DARK STORE MEASURES:**
💸 **Pattern violation penalty:** ${dark_store_penalty}
📉 **Platform visibility:** Reduced by {corrective_actions.get('visibility_reduction', 0)}% for 14 days
🔍 **Enhanced monitoring:** All orders subject to quality review
📊 **Performance warning:** Formal improvement notice issued

**🎓 COMPREHENSIVE REMEDIATION PROGRAM:**
1. **MANDATORY TRAINING (48 hours):**
   - Complete quality control certification
   - Warehouse staff quality training
   - Management oversight training
   - Product standards review

2. **SYSTEMATIC IMPROVEMENTS:**
   - Quality measurement tools installation
   - Quality control checkpoints implementation
   - Daily product audits requirement
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
            return f"""📦 **Product Quality Standards Violation - Quality Improvement Required**

**Quality Assurance Alert**

**Violation Assessment:**
- Severity: {violation_details.get('severity', 'moderate')}
- Category: {violation_details.get('product_category', 'packaged_goods')}
- Impact level: Moderate customer dissatisfaction
- Action required: Quality improvement measures

**✅ CUSTOMER RESOLUTION:**
💰 **Customer refund:** {customer_refund}% of order value processed
📦 **Service recovery:** Discount on next order
📞 **Follow-up:** Customer satisfaction confirmation
⭐ **Quality assurance:** Enhanced picking attention

**📊 DARK STORE QUALITY MEASURES:**
💸 **Quality fee:** ${dark_store_penalty} (quality control improvement)
📈 **Visibility impact:** Minor reduction ({corrective_actions.get('visibility_reduction', 0)}%)
🎯 **Quality focus:** Enhanced product monitoring
📋 **Improvement plan:** Required within 1 week

**🎓 QUALITY IMPROVEMENT ACTIONS:**
1. **IMMEDIATE REVIEW (24 hours):**
   - Product quality guidelines review with warehouse staff
   - Quality checking tools calibration check
   - Current quality practices assessment
   - Quality control system evaluation

2. **IMPROVEMENT MEASURES (1 week):**
   - Staff quality training session
   - Warehouse workflow optimization
   - Quality checkpoints implementation
   - Customer feedback integration

3. **MONITORING (ongoing):**
   - Regular quality compliance checks
   - Customer satisfaction tracking
   - Quality metrics monitoring
   - Continuous improvement focus

**📋 COMPLIANCE EXPECTATIONS:**
- Training completion: {corrective_actions.get('training_program', 'quality_guidelines_review')}
- Quality audit: {corrective_actions.get('audit_schedule', 'within_1_week')}
- Improvement demonstration: 2 weeks
- Performance review: Monthly

Consistent product quality standards are essential for customer satisfaction and your dark store's success on our platform."""

    # PICKING AND PACKING EFFICIENCY HANDLER METHODS
    def handle_dark_store_picking_delays(self, query: str, store_id: str = "anonymous") -> str:
        """Handle dark store picking delays with data-driven analysis and improvement plan"""
        logger.info(f"Processing picking delay issue: {query[:100]}...")

        # Analyze delay details using AI reasoning
        delay_analysis = self.analyze_picking_delay_details(query)

        # Get dark store performance metrics
        performance_metrics = self.get_dark_store_picking_performance(store_id)

        # Identify root causes and improvement opportunities
        improvement_plan = self.generate_picking_improvement_plan(delay_analysis, performance_metrics)

        # Create actionable response
        return self.generate_picking_delay_response(delay_analysis, performance_metrics, improvement_plan)

    def analyze_picking_delay_details(self, query: str) -> dict:
        """Analyze picking delay details using AI"""
        analysis_prompt = f"""
        Analyze this dark store picking delay complaint:

        Complaint: {query}

        Identify:
        1. What is the actual vs expected picking time?
        2. What factors are contributing to delays?
        3. Is this a recurring pattern or isolated incident?
        4. Which products or processes are affected?

        Return ONLY JSON: {{"actual_picking_time": "X minutes", "expected_picking_time": "X minutes", "delay_factors": ["factor1", "factor2"], "pattern_type": "isolated/recurring/systemic", "affected_products": ["product1", "product2"], "severity": "minor/moderate/severe"}}
        """

        try:
            if self.ai_engine:
                result = self.ai_engine.process_complaint(
                    function_name="analyze_picking_delays",
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

            return self._fallback_picking_delay_analysis(query)

        except Exception as e:
            logger.error(f"Failed to analyze picking delays: {e}")
            return self._fallback_picking_delay_analysis(query)

    def _fallback_picking_delay_analysis(self, query: str) -> dict:
        """Fallback delay analysis"""
        query_lower = query.lower()

        # Extract time information
        actual_time = "25-30 minutes" if "25" in query_lower or "30" in query_lower else "20-25 minutes"
        severity = "severe" if any(word in query_lower for word in ["very long", "extremely slow", "unacceptable"]) else "moderate"

        return {
            "actual_picking_time": actual_time,
            "expected_picking_time": "10-15 minutes",
            "delay_factors": ["warehouse layout", "staff allocation", "inventory organization"],
            "pattern_type": "recurring" if "always" in query_lower or "every time" in query_lower else "isolated",
            "affected_products": ["multiple products"],
            "severity": severity
        }

    def get_dark_store_picking_performance(self, store_id: str) -> dict:
        """Get dark store's historical picking performance"""
        # This would typically query database for performance metrics
        return {
            "average_picking_time": "22 minutes",
            "target_picking_time": "12 minutes",
            "efficiency_score": 60,
            "peak_hour_performance": "below_standard",
            "equipment_utilization": 80,
            "staff_efficiency": "needs_improvement"
        }

    def generate_picking_improvement_plan(self, delay_analysis: dict, performance_metrics: dict) -> dict:
        """Generate improvement plan using AI reasoning"""
        plan_prompt = f"""
        Create an improvement plan for dark store picking delays:

        Delay Analysis: {delay_analysis}
        Performance Metrics: {performance_metrics}

        Generate a comprehensive improvement plan with:
        1. Immediate actions (0-24 hours)
        2. Short-term improvements (1-2 weeks)
        3. Long-term optimizations (1+ months)
        4. Success metrics and monitoring

        Return ONLY JSON: {{"immediate_actions": ["action1"], "short_term_improvements": ["improvement1"], "long_term_optimizations": ["optimization1"], "success_metrics": ["metric1"], "estimated_improvement": "X% reduction in picking time"}}
        """

        try:
            if self.ai_engine:
                result = self.ai_engine.process_complaint(
                    function_name="generate_picking_improvement_plan",
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

            return self._fallback_picking_improvement_plan(delay_analysis)

        except Exception as e:
            logger.error(f"Failed to generate improvement plan: {e}")
            return self._fallback_picking_improvement_plan(delay_analysis)

    def _fallback_picking_improvement_plan(self, delay_analysis: dict) -> dict:
        """Fallback improvement plan"""
        severity = delay_analysis.get("severity", "moderate")

        plan = {
            "immediate_actions": [
                "Review current order queue and prioritize urgent orders",
                "Optimize warehouse workflow for peak hours",
                "Implement batch picking procedures for similar products"
            ],
            "short_term_improvements": [
                "Staff training on efficient picking techniques",
                "Warehouse equipment maintenance and optimization",
                "Inventory organization and layout optimization"
            ],
            "long_term_optimizations": [
                "Warehouse layout redesign for optimal flow",
                "Technology integration for order tracking and routing",
                "Advanced inventory management system implementation"
            ],
            "success_metrics": [
                "Reduce average picking time to 12-15 minutes",
                "Achieve 95% on-time fulfillment rate",
                "Improve customer satisfaction to 4.5+ stars"
            ],
            "estimated_improvement": "30-35% reduction in picking time"
        }

        if severity == "severe":
            plan["immediate_actions"].insert(0, "Emergency warehouse workflow assessment")
            plan["estimated_improvement"] = "40-45% reduction in picking time"

        return plan

    def generate_picking_delay_response(self, delay_analysis: dict, performance_metrics: dict, improvement_plan: dict) -> str:
        """Generate comprehensive response for picking delays"""
        severity = delay_analysis.get("severity", "moderate")
        actual_time = delay_analysis.get("actual_picking_time", "unknown")
        expected_time = delay_analysis.get("expected_picking_time", "10-15 minutes")

        return f"""📦 **Warehouse Efficiency Optimization - Data-Driven Improvement Plan**

**Performance Analysis:**
- Current picking time: {actual_time}
- Target picking time: {expected_time}
- Efficiency gap: {performance_metrics.get('efficiency_score', 'unknown')}% of target
- Impact severity: {severity.title()}

**🔍 Root Cause Analysis:**
{chr(10).join([f"- {factor}" for factor in delay_analysis.get('delay_factors', ['Workflow optimization needed'])])}

**📊 Performance Metrics:**
- Average picking time: {performance_metrics.get('average_picking_time', 'unknown')}
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
- Picking time reduction: {improvement_plan.get('estimated_improvement', '25-30%')}
- Customer satisfaction impact: Positive
- Delivery partner experience: Significantly improved

Your commitment to warehouse efficiency optimization will enhance customer satisfaction and operational profitability."""

    # INVENTORY MANAGEMENT HANDLER METHODS
    def handle_inventory_shortage(self, query: str, store_id: str = "anonymous") -> str:
        """Handle dark store inventory shortage issues with systematic approach"""
        logger.info(f"Processing inventory shortage issue: {query[:100]}...")

        # Analyze shortage details
        shortage_analysis = self.analyze_inventory_shortage_details(query)

        # Get current inventory status
        inventory_status = self.get_dark_store_inventory_status(store_id, shortage_analysis)

        # Generate restocking plan
        restocking_plan = self.generate_inventory_restocking_plan(shortage_analysis, inventory_status)

        # Create comprehensive response
        return self.generate_inventory_shortage_response(shortage_analysis, inventory_status, restocking_plan)

    def analyze_inventory_shortage_details(self, query: str) -> dict:
        """Analyze inventory shortage details using AI"""
        analysis_prompt = f"""
        Analyze this dark store inventory shortage complaint:

        Complaint: {query}

        Identify:
        1. Which specific products are out of stock?
        2. What product categories are affected?
        3. Is this affecting order fulfillment?
        4. How urgent is the restocking need?

        Return ONLY JSON: {{"affected_products": ["product1"], "product_categories": ["category1"], "fulfillment_impact": "minor/moderate/severe", "urgency_level": "low/medium/high/critical", "customer_requests": 5, "alternative_available": true/false}}
        """

        try:
            if self.ai_engine:
                result = self.ai_engine.process_complaint(
                    function_name="analyze_inventory_shortage",
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

            return self._fallback_shortage_analysis(query)

        except Exception as e:
            logger.error(f"Failed to analyze inventory shortage: {e}")
            return self._fallback_shortage_analysis(query)

    def _fallback_shortage_analysis(self, query: str) -> dict:
        """Fallback shortage analysis"""
        query_lower = query.lower()

        # Determine urgency based on language
        urgency = "high" if any(word in query_lower for word in ["urgent", "immediately", "asap"]) else "medium"

        # Estimate fulfillment impact
        impact = "severe" if any(word in query_lower for word in ["many customers", "all orders", "completely out"]) else "moderate"

        return {
            "affected_products": ["grocery items"],
            "product_categories": ["packaged_goods", "fresh_produce"],
            "fulfillment_impact": impact,
            "urgency_level": urgency,
            "customer_requests": 8,
            "alternative_available": True
        }

    def get_dark_store_inventory_status(self, store_id: str, shortage_analysis: dict) -> dict:
        """Get current inventory status for dark store"""
        return {
            "overall_stock_level": "75%",
            "critical_items_count": 12,
            "pending_deliveries": "3 deliveries scheduled today",
            "supplier_lead_time": "24-48 hours",
            "backup_supplier_available": True,
            "affected_categories_status": {
                "fresh_produce": "60% stocked",
                "dairy": "85% stocked",
                "packaged_goods": "70% stocked"
            }
        }

    def generate_inventory_restocking_plan(self, shortage_analysis: dict, inventory_status: dict) -> dict:
        """Generate comprehensive restocking plan"""
        urgency = shortage_analysis.get("urgency_level", "medium")

        plan = {
            "immediate_actions": [
                "Contact primary supplier for emergency restocking",
                "Check inter-store transfer possibilities",
                "Update customer-facing inventory status"
            ],
            "restocking_timeline": "24-48 hours",
            "alternative_solutions": [
                "Offer substitute products to customers",
                "Provide rain checks for out-of-stock items",
                "Coordinate with nearby Dark Store locations"
            ],
            "prevention_measures": [
                "Implement automated low-stock alerts",
                "Review and adjust safety stock levels",
                "Improve demand forecasting accuracy"
            ]
        }

        if urgency == "critical":
            plan["immediate_actions"].insert(0, "Activate emergency supplier protocols")
            plan["restocking_timeline"] = "6-12 hours"

        return plan

    def generate_inventory_shortage_response(self, shortage_analysis: dict, inventory_status: dict, restocking_plan: dict) -> str:
        """Generate comprehensive response for inventory shortages"""
        urgency = shortage_analysis.get("urgency_level", "medium")
        impact = shortage_analysis.get("fulfillment_impact", "moderate")
        affected_products = ", ".join(shortage_analysis.get("affected_products", ["various items"]))

        return f"""📦 **Inventory Management - Stock Shortage Resolution**

**Shortage Analysis:**
- Affected products: {affected_products}
- Fulfillment impact: {impact.title()}
- Urgency level: {urgency.title()}
- Customer requests affected: {shortage_analysis.get('customer_requests', 'Multiple')}

**📊 Current Inventory Status:**
- Overall stock level: {inventory_status.get('overall_stock_level', 'Under Review')}
- Critical items count: {inventory_status.get('critical_items_count', 'Unknown')}
- Pending deliveries: {inventory_status.get('pending_deliveries', 'Checking status')}
- Supplier lead time: {inventory_status.get('supplier_lead_time', '24-48 hours')}

**⚡ IMMEDIATE RESOLUTION ACTIONS:**
{chr(10).join([f"- {action}" for action in restocking_plan.get('immediate_actions', ['Initiating restocking procedures'])])}

**🔄 ALTERNATIVE CUSTOMER SOLUTIONS:**
{chr(10).join([f"- {solution}" for solution in restocking_plan.get('alternative_solutions', ['Exploring alternatives'])])}

**📅 RESTOCKING TIMELINE:**
- Expected restock completion: {restocking_plan.get('restocking_timeline', '24-48 hours')}
- Customer notification: Automatic updates when items available
- Order fulfillment: Resumed immediately upon restock

**🛡️ PREVENTION MEASURES:**
{chr(10).join([f"- {measure}" for measure in restocking_plan.get('prevention_measures', ['Improving inventory management'])])}

**📈 Quality Assurance:**
- Automated stock level monitoring implementation
- Supplier performance review and optimization
- Customer satisfaction priority during shortage periods
- Real-time inventory accuracy improvements

Efficient inventory management ensures consistent product availability and customer satisfaction."""

    # COLD CHAIN AND PRODUCT HANDLING METHODS
    def handle_cold_chain_violation(self, query: str, store_id: str = "anonymous", image_data: str = None, order_id: str = None) -> str:
        """Handle cold chain violations with strict temperature control protocols"""
        logger.info(f"Processing cold chain violation: {query[:100]}...")

        # Step 1: Extract cold chain violation details
        violation_details = self.extract_cold_chain_violation_details(query)

        # Step 2: Assess temperature control systems
        if violation_details["severity"] in ["severe", "critical"] and not image_data:
            return "🌡️ For cold chain violations, please upload a photo showing the product condition for temperature control verification."

        # Step 3: Check dark store credibility and cold chain history
        credibility_score = self.get_dark_store_credibility_score(store_id)
        cold_chain_history = self.check_cold_chain_violation_history(store_id)
        logger.info(f"Dark store credibility: {credibility_score}/10, Cold chain history: {cold_chain_history}")

        # Step 4: Assess temperature risk and food safety implications
        temperature_risk_assessment = self.assess_cold_chain_risk(violation_details, credibility_score, cold_chain_history)
        logger.info(f"Temperature risk assessment: {temperature_risk_assessment}")

        # Step 5: Determine cold chain emergency protocols
        emergency_protocols = self.determine_cold_chain_emergency_protocols(temperature_risk_assessment, credibility_score)
        logger.info(f"Emergency protocols: {emergency_protocols}")

        # Step 6: Generate comprehensive cold chain response
        response = self.generate_cold_chain_response(emergency_protocols, violation_details, temperature_risk_assessment)
        logger.info(f"Cold chain violation response generated successfully")

        return response

    def extract_cold_chain_violation_details(self, query: str) -> dict:
        """Extract cold chain violation details from complaint using structured AI analysis"""
        extraction_prompt = f"""
        Analyze this cold chain violation complaint and extract critical details:

        Complaint: {query}

        Identify:
        1. What type of temperature control issue is described?
        2. Which products were affected (frozen, chilled, ambient)?
        3. How severe is the temperature violation?
        4. Are there visible signs of temperature damage?
        5. What is the customer health risk level?

        Return ONLY JSON: {{"violation_type": "frozen_thawed/chilled_warm/condensation/ice_crystals/temperature_abuse", "affected_product_types": ["frozen", "chilled", "ambient"], "severity": "minor/moderate/severe/critical", "visible_damage": true/false, "customer_health_risk": "none/low/medium/high/critical", "temperature_duration": "short/extended/unknown", "evidence_level": "customer_claim/photo_provided/temperature_log"}}
        """

        try:
            # Use AI engine to extract structured data if available
            if self.ai_engine:
                result = self.ai_engine.process_complaint(
                    function_name="extract_cold_chain_violation",
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
                    return self._fallback_cold_chain_extraction(query)
            else:
                return self._fallback_cold_chain_extraction(query)

        except Exception as e:
            logger.error(f"Failed to extract cold chain violation details: {e}")
            return self._fallback_cold_chain_extraction(query)

    def _fallback_cold_chain_extraction(self, query: str) -> dict:
        """Fallback method for cold chain violation extraction when AI fails"""
        details = {
            "violation_type": "temperature_abuse",
            "affected_product_types": ["chilled"],
            "severity": "moderate",
            "visible_damage": False,
            "customer_health_risk": "low",
            "temperature_duration": "unknown",
            "evidence_level": "customer_claim"
        }

        query_lower = query.lower()

        # Determine violation type and severity
        if any(word in query_lower for word in ['melted', 'thawed', 'soft', 'liquid']):
            details.update({
                "violation_type": "frozen_thawed",
                "affected_product_types": ["frozen"],
                "severity": "severe",
                "visible_damage": True
            })
        elif any(word in query_lower for word in ['warm', 'not cold', 'room temperature']):
            details.update({
                "violation_type": "chilled_warm",
                "affected_product_types": ["chilled"],
                "severity": "moderate"
            })
        elif any(word in query_lower for word in ['ice crystals', 'freezer burn', 'frost']):
            details.update({
                "violation_type": "ice_crystals",
                "affected_product_types": ["frozen"],
                "severity": "moderate"
            })

        # Assess health risk
        if any(word in query_lower for word in ['spoiled', 'bad smell', 'unsafe']):
            details["customer_health_risk"] = "high"
            details["severity"] = "severe"

        # Check for evidence
        if any(word in query_lower for word in ['photo', 'picture', 'image']):
            details["evidence_level"] = "photo_provided"

        return details

    def check_cold_chain_violation_history(self, store_id: str) -> dict:
        """Check dark store's cold chain violation history"""
        # This would query the database for historical violations
        # For now, return simulated data
        return {
            "pattern_type": "NORMAL_TEMPERATURE_PATTERN",
            "violation_count_30_days": 1,
            "violation_count_90_days": 3,
            "severity_trend": "stable",
            "equipment_maintenance_due": False,
            "resolution_rate": 95.0
        }

    def assess_cold_chain_risk(self, violation_details: dict, credibility_score: int, cold_chain_history: dict) -> dict:
        """Assess cold chain risk and implications"""
        severity = violation_details.get("severity", "moderate")
        health_risk = violation_details.get("customer_health_risk", "low")
        visible_damage = violation_details.get("visible_damage", False)

        assessment = {
            "risk_level": "MEDIUM",
            "equipment_inspection_required": True,
            "inventory_review_required": True,
            "temperature_log_audit": True,
            "customer_health_priority": False,
            "supplier_notification": False
        }

        if severity in ["severe", "critical"] or health_risk in ["high", "critical"]:
            assessment.update({
                "risk_level": "HIGH",
                "customer_health_priority": True,
                "supplier_notification": True
            })

        if visible_damage:
            assessment["inventory_review_required"] = True

        return assessment

    def determine_cold_chain_emergency_protocols(self, temperature_risk_assessment: dict, credibility_score: int) -> dict:
        """Determine emergency protocols for cold chain violations"""
        risk_level = temperature_risk_assessment.get("risk_level", "MEDIUM")

        protocols = {
            "immediate_temperature_check": True,
            "equipment_inspection": True,
            "affected_inventory_quarantine": False,
            "temperature_log_review": True,
            "staff_retraining": False,
            "equipment_maintenance": False,
            "supplier_contact": False
        }

        if risk_level == "HIGH":
            protocols.update({
                "affected_inventory_quarantine": True,
                "staff_retraining": True,
                "equipment_maintenance": True,
                "supplier_contact": True
            })

        return protocols

    def generate_cold_chain_response(self, emergency_protocols: dict, violation_details: dict, temperature_risk_assessment: dict) -> str:
        """Generate comprehensive cold chain response"""
        risk_level = temperature_risk_assessment.get("risk_level", "MEDIUM")
        violation_type = violation_details.get("violation_type", "temperature_abuse").replace("_", " ").title()
        health_risk = violation_details.get("customer_health_risk", "low")

        if risk_level == "HIGH":
            return f"""🌡️ **CRITICAL COLD CHAIN VIOLATION - IMMEDIATE TEMPERATURE CONTROL REQUIRED**

**Cold Chain Emergency Alert**

**Violation Analysis:**
- Violation type: {violation_type}
- Customer health risk: {health_risk.upper()}
- Product safety: COMPROMISED
- Temperature control: IMMEDIATE ATTENTION REQUIRED

**❄️ IMMEDIATE EMERGENCY ACTIONS:**
- Temperature equipment inspection: MANDATORY
- Affected inventory quarantine: ACTIVATED
- Temperature logs audit: IN PROGRESS
- Equipment maintenance: EMERGENCY CALL SCHEDULED

**🥶 CUSTOMER PROTECTION MEASURES:**
- Immediate full refund: 100% order value
- Replacement products: Fresh cold chain verified items
- Health priority support: Medical consultation if needed
- Quality guarantee: Enhanced cold chain monitoring

**⚡ COLD CHAIN RESTORATION PROTOCOL:**
1. **IMMEDIATE (0-2 hours):**
   - Emergency temperature equipment inspection
   - Affected product batch quarantine
   - Cold storage system verification
   - Staff cold chain training refresh

2. **CORRECTIVE MEASURES (2-8 hours):**
   - Equipment calibration and maintenance
   - Temperature monitoring system upgrade
   - Inventory quality verification
   - Cold chain process review

3. **PREVENTION (8+ hours):**
   - Enhanced temperature monitoring alerts
   - Staff certification in cold chain management
   - Supplier cold chain verification
   - Customer quality assurance communication

**📊 COMPLIANCE REQUIREMENTS:**
- Temperature equipment certification: Required before operations resume
- Staff cold chain training: 100% completion mandatory
- Supplier verification: Cold chain compliance confirmation
- Quality monitoring: Continuous temperature tracking

Cold chain integrity is fundamental to product safety and customer health protection."""

        else:  # MEDIUM risk
            return f"""🌡️ **Cold Chain Quality Alert - Temperature Control Improvement Required**

**Temperature Management Issue Identified**

**Situation Assessment:**
- Violation type: {violation_type}
- Customer health risk: {health_risk.title()}
- Temperature control: Requires attention and improvement
- Product quality: Enhanced monitoring needed

**❄️ IMMEDIATE QUALITY MEASURES:**
- Temperature equipment check: Scheduled within 4 hours
- Affected inventory review: Quality verification in progress
- Temperature logs analysis: System performance evaluation
- Cold chain protocols review: Staff procedure confirmation

**🛡️ CUSTOMER CARE ACTIONS:**
- Customer refund: 75% of order value processed
- Replacement offer: Quality-verified products available
- Quality assurance: Enhanced cold chain attention
- Follow-up confirmation: Customer satisfaction priority

**🔧 TEMPERATURE CONTROL IMPROVEMENTS:**
1. **ASSESSMENT (0-4 hours):**
   - Temperature equipment functionality check
   - Cold storage performance verification
   - Staff cold chain procedure review
   - Product quality assessment

2. **OPTIMIZATION (4-24 hours):**
   - Temperature monitoring calibration
   - Cold chain workflow optimization
   - Staff refresher training session
   - Quality control enhancement

3. **MONITORING (24+ hours):**
   - Continuous temperature tracking
   - Regular equipment maintenance
   - Staff performance monitoring
   - Customer feedback integration

**📈 QUALITY ASSURANCE COMMITMENT:**
- Consistent temperature maintenance across all products
- Regular equipment maintenance and calibration
- Staff training on cold chain best practices
- Customer satisfaction through product quality excellence

Proper cold chain management ensures product freshness and customer confidence in your Dark Store operations."""

    # ORDER CUSTOMIZATION AND PRODUCT SUBSTITUTION HANDLER METHODS
    def handle_product_substitution_request(self, query: str, store_id: str = "anonymous", order_id: str = None, customer_id: str = None) -> str:
        """Handle product substitution requests with strict 8-step workflow and AI reasoning"""
        logger.info(f"Processing product substitution request: {query[:100]}...")

        # Step 1: Extract substitution details using AI reasoning
        substitution_details = self.extract_substitution_request_details(query)

        # Step 2: Assess dark store inventory availability
        inventory_availability = self.assess_substitution_inventory_capability(store_id, substitution_details)

        # Step 3: Evaluate customer preferences and dietary restrictions
        preference_analysis = self.evaluate_substitution_preferences(substitution_details, inventory_availability)

        # Step 4: Check price impact and customer approval requirements
        pricing_impact = self.check_substitution_pricing_impact(substitution_details, preference_analysis)

        # Step 5: Determine substitution communication strategy using AI reasoning
        communication_strategy = self.determine_substitution_communication_strategy(
            substitution_details, preference_analysis, pricing_impact
        )

        # Step 6: Generate implementation instructions for warehouse staff
        warehouse_instructions = self.generate_warehouse_substitution_instructions(
            substitution_details, communication_strategy
        )

        # Step 7: Update order tracking and cross-actor communication
        if order_id and customer_id:
            self.update_substitution_tracking(order_id, customer_id, substitution_details, communication_strategy)

        # Step 8: Generate comprehensive response with AI-powered reasoning
        response = self.generate_substitution_response(
            substitution_details, preference_analysis, pricing_impact,
            communication_strategy, warehouse_instructions
        )

        logger.info(f"Product substitution workflow completed successfully")
        return response

    def extract_substitution_request_details(self, query: str) -> dict:
        """Extract substitution request details using AI-powered analysis"""
        extraction_prompt = f"""
        Analyze this product substitution request and extract structured details:

        Customer Request: {query}

        Identify and categorize:
        1. What type of substitution is being requested?
        2. Which specific products need substitution?
        3. What are the reasons for substitution (unavailable, dietary, preference)?
        4. Are there specific requirements or restrictions mentioned?
        5. Is this a preference-based or necessity-based request?
        6. What level of flexibility does the customer show?
        7. Are there any time-sensitive aspects mentioned?

        Return ONLY JSON: {{"substitution_type": "unavailable_item/dietary_restriction/brand_preference/size_preference/quality_upgrade", "affected_products": ["product1", "product2"], "substitution_reasons": ["out_of_stock", "dietary_need", "brand_preference"], "dietary_restrictions": ["allergy1", "allergy2"], "necessity_level": "optional/preferred/required/critical", "flexibility_level": "very_flexible/flexible/specific/very_specific", "time_sensitivity": "low/medium/high", "customer_tone": "polite/urgent/demanding/frustrated", "special_instructions": "any specific notes"}}
        """

        try:
            if self.ai_engine:
                result = self.ai_engine.process_complaint(
                    function_name="extract_substitution_request",
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
                    return self._fallback_substitution_extraction(query)
            else:
                return self._fallback_substitution_extraction(query)

        except Exception as e:
            logger.error(f"Failed to extract substitution details: {e}")
            return self._fallback_substitution_extraction(query)

    def _fallback_substitution_extraction(self, query: str) -> dict:
        """Fallback substitution extraction when AI fails"""
        details = {
            "substitution_type": "unavailable_item",
            "affected_products": ["grocery_item"],
            "substitution_reasons": ["out_of_stock"],
            "dietary_restrictions": [],
            "necessity_level": "preferred",
            "flexibility_level": "flexible",
            "time_sensitivity": "medium",
            "customer_tone": "polite",
            "special_instructions": ""
        }

        query_lower = query.lower()

        # Detect dietary restrictions and allergies
        if any(word in query_lower for word in ['allergy', 'allergic', 'cannot have', 'intolerant']):
            details["necessity_level"] = "critical"
            details["substitution_type"] = "dietary_restriction"
            details["time_sensitivity"] = "high"

            # Common allergens
            if any(word in query_lower for word in ['nuts', 'peanut', 'tree nut']):
                details["dietary_restrictions"].append("nuts")
            if any(word in query_lower for word in ['dairy', 'milk', 'lactose']):
                details["dietary_restrictions"].append("dairy")
            if any(word in query_lower for word in ['gluten', 'wheat']):
                details["dietary_restrictions"].append("gluten")

        # Detect brand preferences
        if any(word in query_lower for word in ['brand', 'specific brand', 'only this brand']):
            details["substitution_type"] = "brand_preference"
            details["flexibility_level"] = "specific"

        # Detect size preferences
        if any(word in query_lower for word in ['size', 'larger', 'smaller', 'different size']):
            details["substitution_type"] = "size_preference"

        # Detect flexibility level
        if any(word in query_lower for word in ['any', 'anything', 'whatever', 'dont care']):
            details["flexibility_level"] = "very_flexible"
        elif any(word in query_lower for word in ['exactly', 'only', 'must be', 'specifically']):
            details["flexibility_level"] = "very_specific"

        # Detect customer tone
        if any(word in query_lower for word in ['urgent', 'asap', 'hurry', 'quickly']):
            details["customer_tone"] = "urgent"
            details["time_sensitivity"] = "high"
        elif any(word in query_lower for word in ['please', 'kindly', 'would appreciate']):
            details["customer_tone"] = "polite"

        return details

    def assess_substitution_inventory_capability(self, store_id: str, substitution_details: dict) -> dict:
        """Assess dark store's capability to provide suitable substitutions"""
        capability = {
            "suitable_alternatives": True,
            "inventory_available": True,
            "brand_alternatives": True,
            "size_alternatives": True,
            "price_range_alternatives": True,
            "dietary_compliant_options": True,
            "estimated_additional_time": 0,
            "additional_cost_impact": 0.0,
            "risk_level": "low",
            "confidence_score": 85
        }

        substitution_type = substitution_details.get("substitution_type", "unavailable_item")
        flexibility_level = substitution_details.get("flexibility_level", "flexible")
        dietary_restrictions = substitution_details.get("dietary_restrictions", [])

        # Assess based on substitution type
        if substitution_type == "dietary_restriction":
            capability.update({
                "estimated_additional_time": 5,
                "risk_level": "medium",
                "confidence_score": 75
            })

            # Check for complex dietary restrictions
            if len(dietary_restrictions) > 2:
                capability.update({
                    "dietary_compliant_options": False,
                    "risk_level": "high",
                    "confidence_score": 60
                })

        elif substitution_type == "brand_preference" and flexibility_level == "very_specific":
            capability.update({
                "brand_alternatives": False,
                "estimated_additional_time": 3,
                "risk_level": "medium",
                "confidence_score": 65
            })

        # Dark store credibility impact
        credibility_score = self.get_dark_store_credibility_score(store_id)
        if credibility_score <= 5:
            capability["confidence_score"] -= 15
            capability["risk_level"] = "high"

        return capability

    def evaluate_substitution_preferences(self, substitution_details: dict, inventory_availability: dict) -> dict:
        """Evaluate customer preferences and match with available options"""
        analysis = {
            "preference_match_level": "good",
            "dietary_compliance": "full",
            "price_range_match": "exact",
            "quality_level_match": "equivalent",
            "brand_satisfaction": "high",
            "overall_satisfaction_prediction": "positive",
            "recommendation_confidence": "high"
        }

        flexibility = substitution_details.get("flexibility_level", "flexible")
        necessity_level = substitution_details.get("necessity_level", "preferred")

        # Adjust based on customer flexibility
        if flexibility == "very_specific":
            if not inventory_availability.get("brand_alternatives", True):
                analysis.update({
                    "preference_match_level": "poor",
                    "brand_satisfaction": "low",
                    "overall_satisfaction_prediction": "negative",
                    "recommendation_confidence": "low"
                })

        # Critical dietary restrictions
        if necessity_level == "critical":
            if not inventory_availability.get("dietary_compliant_options", True):
                analysis.update({
                    "dietary_compliance": "none",
                    "overall_satisfaction_prediction": "very_negative",
                    "recommendation_confidence": "very_low"
                })

        return analysis

    def check_substitution_pricing_impact(self, substitution_details: dict, preference_analysis: dict) -> dict:
        """Check pricing impact of substitutions"""
        pricing = {
            "price_difference": 0.0,
            "customer_approval_required": False,
            "automatic_substitution_allowed": True,
            "refund_price_difference": False,
            "upgrade_cost": 0.0,
            "customer_benefit": "none"
        }

        # Simulate pricing logic based on substitution type
        substitution_type = substitution_details.get("substitution_type", "unavailable_item")

        if substitution_type == "quality_upgrade":
            pricing.update({
                "price_difference": 2.50,
                "customer_approval_required": True,
                "automatic_substitution_allowed": False,
                "upgrade_cost": 2.50
            })
        elif substitution_type == "size_preference":
            pricing.update({
                "price_difference": 1.00,
                "customer_approval_required": True,
                "automatic_substitution_allowed": False
            })

        # Check if substitution results in savings
        if pricing["price_difference"] < 0:
            pricing.update({
                "refund_price_difference": True,
                "customer_benefit": "savings"
            })

        return pricing

    def determine_substitution_communication_strategy(self, substitution_details: dict, preference_analysis: dict, pricing_impact: dict) -> dict:
        """Determine communication strategy using AI reasoning"""
        strategy_prompt = f"""
        Determine the optimal communication strategy for this product substitution request:

        Substitution Details: {substitution_details}
        Preference Analysis: {preference_analysis}
        Pricing Impact: {pricing_impact}

        Based on this analysis, determine:
        1. Should this substitution be approved automatically, require approval, or be declined?
        2. What is the primary message tone (positive, informative, apologetic)?
        3. What key information must be communicated to the customer?
        4. What alternatives should be offered if primary substitution isn't suitable?
        5. What timeline should be communicated?

        Return ONLY JSON: {{"decision": "auto_approved/approval_required/declined", "message_tone": "positive/informative/apologetic", "key_messages": ["message1", "message2"], "alternatives_offered": ["alt1", "alt2"], "estimated_timeline": "X minutes", "price_communication": "no_change/upgrade_cost/savings", "priority_level": "low/medium/high"}}
        """

        try:
            if self.ai_engine:
                result = self.ai_engine.process_complaint(
                    function_name="determine_substitution_strategy",
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
                    return self._fallback_substitution_strategy(substitution_details, preference_analysis, pricing_impact)
            else:
                return self._fallback_substitution_strategy(substitution_details, preference_analysis, pricing_impact)

        except Exception as e:
            logger.error(f"Failed to determine substitution strategy: {e}")
            return self._fallback_substitution_strategy(substitution_details, preference_analysis, pricing_impact)

    def _fallback_substitution_strategy(self, substitution_details: dict, preference_analysis: dict, pricing_impact: dict) -> dict:
        """Fallback substitution strategy when AI fails"""
        strategy = {
            "decision": "auto_approved",
            "message_tone": "positive",
            "key_messages": ["We found a suitable substitution"],
            "alternatives_offered": [],
            "estimated_timeline": "3-5 minutes",
            "price_communication": "no_change",
            "priority_level": "medium"
        }

        # Decision logic
        if not preference_analysis.get("dietary_compliance") == "full":
            strategy.update({
                "decision": "declined",
                "message_tone": "apologetic",
                "key_messages": ["Unable to find suitable dietary-compliant substitution"],
                "alternatives_offered": ["Full refund for unavailable items"]
            })
        elif pricing_impact.get("customer_approval_required"):
            strategy.update({
                "decision": "approval_required",
                "message_tone": "informative",
                "key_messages": ["Substitution available with price adjustment"],
                "price_communication": "upgrade_cost"
            })

        # Medical necessity gets high priority
        if substitution_details.get("necessity_level") == "critical":
            strategy["priority_level"] = "high"

        return strategy

    def generate_warehouse_substitution_instructions(self, substitution_details: dict, communication_strategy: dict) -> dict:
        """Generate detailed warehouse implementation instructions"""
        instructions = {
            "picking_steps": [],
            "quality_protocols": [],
            "verification_checkpoints": [],
            "customer_communication": [],
            "special_handling_needed": [],
            "staff_notifications": []
        }

        decision = communication_strategy.get("decision", "auto_approved")

        if decision == "declined":
            return instructions  # No warehouse instructions needed

        # Generate picking steps based on substitution type
        substitution_type = substitution_details.get("substitution_type", "unavailable_item")

        if substitution_type == "dietary_restriction":
            instructions["picking_steps"].extend([
                "Verify product labels for allergen information",
                "Use separate picking tools to avoid cross-contamination",
                "Double-check dietary compliance before adding to order"
            ])
            instructions["quality_protocols"].extend([
                "Clean hands and equipment before handling",
                "Verify no cross-contamination risk",
                "Label order with dietary substitution notes"
            ])

        elif substitution_type == "brand_preference":
            instructions["picking_steps"].extend([
                "Select closest brand alternative based on customer preference",
                "Verify product specifications match requirements",
                "Check expiry dates and product condition"
            ])

        # Quality checkpoints
        instructions["verification_checkpoints"] = [
            "Verify substitution matches customer requirements",
            "Check product quality and expiry dates",
            "Confirm pricing is correct",
            "Ensure proper packaging for substituted items"
        ]

        return instructions

    def update_substitution_tracking(self, order_id: str, customer_id: str, substitution_details: dict, communication_strategy: dict):
        """Update order tracking and cross-actor communication"""
        try:
            update_details = {
                "substitution_type": substitution_details.get("substitution_type"),
                "decision": communication_strategy.get("decision"),
                "estimated_additional_time": communication_strategy.get("estimated_timeline"),
                "special_handling": substitution_details.get("necessity_level") == "critical"
            }

            self.cross_actor_service.create_cross_actor_update(
                order_id=order_id,
                actor_type="dark_house",
                actor_username="dark_store_handler",
                update_type="product_substitution",
                details=update_details
            )
        except Exception as e:
            logger.error(f"Failed to update substitution tracking: {e}")

    def generate_substitution_response(self, substitution_details: dict, preference_analysis: dict,
                                     pricing_impact: dict, communication_strategy: dict,
                                     warehouse_instructions: dict) -> str:
        """Generate comprehensive AI-powered substitution response"""
        decision = communication_strategy.get("decision", "auto_approved")
        message_tone = communication_strategy.get("message_tone", "positive")
        estimated_timeline = communication_strategy.get("estimated_timeline", "3-5 minutes")

        if decision == "auto_approved":
            return f"""✅ **Product Substitution Approved - Warehouse Notified**

**Substitution Details Successfully Processed:**
- Request type: {substitution_details.get('substitution_type', 'substitution').replace('_', ' ').title()}
- Necessity level: {substitution_details.get('necessity_level', 'preferred').title()}
- Dietary compliance: {'Required' if substitution_details.get('dietary_restrictions') else 'Standard'}

**📦 Warehouse Implementation:**
- Estimated additional time: {estimated_timeline}
- Special handling required: {'Yes' if preference_analysis.get('dietary_compliance') != 'full' else 'No'}
- Quality verification: Enhanced checking protocols
- Price impact: {pricing_impact.get('price_difference', 0.0)} difference

**📋 Picking Instructions Sent to Warehouse:**
{chr(10).join([f"- {step}" for step in warehouse_instructions.get('picking_steps', ['Standard substitution procedures'])])}

**🔒 Quality Protocols Activated:**
{chr(10).join([f"- {protocol}" for protocol in warehouse_instructions.get('quality_protocols', ['Standard quality protocols'])])}

**📞 Customer Communication:**
- Customer will be notified of approved substitution
- Order tracking updated with substitution details
- Delivery partner informed of any special handling requirements

**✅ Verification Checkpoints:**
{chr(10).join([f"- {checkpoint}" for checkpoint in warehouse_instructions.get('verification_checkpoints', ['Standard verification'])])}

Your warehouse team has been provided with detailed substitution instructions to ensure customer satisfaction."""

        elif decision == "approval_required":
            price_diff = pricing_impact.get("price_difference", 0.0)
            return f"""⚠️ **Product Substitution Pending Customer Approval**

**Substitution Analysis:**
- Request type: {substitution_details.get('substitution_type', 'substitution').replace('_', ' ').title()}
- Price impact: ${abs(price_diff):.2f} {'additional cost' if price_diff > 0 else 'savings'}
- Quality match: {preference_analysis.get('quality_level_match', 'equivalent').title()}
- Estimated time: {estimated_timeline}

**💰 Pricing Information:**
- Original item: Unavailable
- Substitute item: Available with price adjustment
- Price difference: ${price_diff:.2f}
- Customer approval: Required before proceeding

**📞 Customer Communication Sent:**
"We found a suitable substitute for your unavailable item. The substitute costs ${abs(price_diff):.2f} {'more' if price_diff > 0 else 'less'} than the original item. Please confirm if you would like us to proceed with this substitution."

**📦 Warehouse Preparation Status:**
- Substitution item located and quality verified
- Awaiting customer confirmation to add to order
- Picking instructions prepared and ready
- Alternative options identified if customer declines

**⏰ Next Steps:**
- Customer response timeline: 5 minutes
- Warehouse picking begins immediately upon approval
- Order tracking updated with substitution status
- Alternative options available if declined

Warehouse team is prepared to implement substitution upon customer confirmation."""

        else:  # declined
            alternatives = communication_strategy.get("alternatives_offered", [])
            return f"""❌ **Product Substitution Unavailable - Alternative Solutions Provided**

**Substitution Analysis:**
- Request type: {substitution_details.get('substitution_type', 'substitution').replace('_', ' ').title()}
- Decline reason: {'; '.join(communication_strategy.get('key_messages', ['No suitable alternatives available']))}
- Dietary compliance: {'Failed' if preference_analysis.get('dietary_compliance') != 'full' else 'Reviewed'}

**🚫 Reasons for Unavailability:**
{chr(10).join([f"- {reason}" for reason in communication_strategy.get('key_messages', ['Suitable alternatives not available'])])}

**🔄 Alternative Solutions Offered:**
{chr(10).join([f"- {alternative}" for alternative in alternatives]) if alternatives else '- Full refund for unavailable items'}

**📞 Customer Communication Sent:**
"We apologize that we cannot provide a suitable substitution for your requested item due to {communication_strategy.get('key_messages', ['inventory limitations'])[0]}. We have processed a full refund for the unavailable item and offer the following alternatives for future orders."

**✅ Customer Service Actions:**
- Full refund processed for unavailable items
- Alternative product recommendations provided
- Future order modification assistance offered
- Quality standards maintained over forced substitutions

**🎯 Quality Assurance:**
- Customer satisfaction prioritized over incomplete substitutions
- Product quality standards maintained
- Future inventory planning improved
- Alternative sourcing options explored

Professional handling ensures customer trust is maintained even when perfect substitutions aren't available."""

    # WAREHOUSE OPERATIONAL HINDRANCE HANDLER METHODS
    def handle_warehouse_operational_hindrance(self, query: str, store_id: str = "anonymous", urgency_level: str = "medium") -> str:
        """Handle warehouse operational hindrances with strict 9-step crisis management workflow"""
        logger.info(f"Processing warehouse operational hindrance: {query[:100]}...")

        # Step 1: Analyze hindrance type and severity using AI reasoning
        hindrance_analysis = self.analyze_warehouse_hindrance_type_and_severity(query)

        # Step 2: Assess immediate operational and inventory risks
        risk_assessment = self.assess_warehouse_operational_risks(hindrance_analysis, store_id)

        # Step 3: Determine crisis response level and protocol activation
        crisis_response_level = self.determine_warehouse_crisis_response_level(hindrance_analysis, risk_assessment)

        # Step 4: Evaluate customer impact and order fulfillment needs
        customer_impact = self.evaluate_customer_impact_from_warehouse_hindrance(hindrance_analysis, crisis_response_level)

        # Step 5: Generate emergency action plan using AI reasoning
        emergency_action_plan = self.generate_warehouse_emergency_action_plan(
            hindrance_analysis, risk_assessment, crisis_response_level, customer_impact
        )

        # Step 6: Activate platform support and coordination protocols
        platform_support = self.activate_warehouse_platform_support_protocols(emergency_action_plan, crisis_response_level)

        # Step 7: Establish communication strategy for all stakeholders
        communication_strategy = self.establish_warehouse_hindrance_communication_strategy(
            hindrance_analysis, customer_impact, emergency_action_plan
        )

        # Step 8: Create recovery timeline and monitoring plan
        recovery_plan = self.create_warehouse_hindrance_recovery_plan(
            hindrance_analysis, emergency_action_plan, platform_support
        )

        # Step 9: Generate comprehensive crisis management response
        response = self.generate_warehouse_hindrance_management_response(
            hindrance_analysis, risk_assessment, crisis_response_level,
            emergency_action_plan, communication_strategy, recovery_plan
        )

        logger.info(f"Warehouse operational hindrance crisis management workflow completed")
        return response

    def analyze_warehouse_hindrance_type_and_severity(self, query: str) -> dict:
        """Analyze warehouse hindrance using AI-powered assessment adapted for warehouse operations"""
        analysis_prompt = f"""
        Analyze this warehouse operational hindrance and classify it comprehensively:

        Hindrance Description: {query}

        Identify and categorize:
        1. What type of warehouse operational hindrance is this?
        2. How severe is the impact on warehouse operations?
        3. Is this affecting inventory or customer orders?
        4. What warehouse systems are affected?
        5. How long might this hindrance last?
        6. Are customer orders immediately at risk?
        7. What is the estimated business impact?

        Return ONLY JSON: {{"hindrance_type": "power_outage/equipment_failure/inventory_system_failure/staff_shortage/temperature_control_failure/warehouse_damage/supplier_delay/technology_failure", "severity_level": "minor/moderate/severe/critical/emergency", "inventory_affected": true/false, "affected_systems": ["picking", "packing", "inventory", "temperature_control"], "estimated_duration": "minutes/hours/days", "customer_order_risk": "none/low/medium/high/critical", "business_impact": "minimal/moderate/significant/severe/catastrophic", "requires_immediate_evacuation": true/false, "supplier_notification_needed": true/false, "alternative_sourcing_required": true/false}}
        """

        try:
            if self.ai_engine:
                result = self.ai_engine.process_complaint(
                    function_name="analyze_warehouse_hindrance_severity",
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
                    return self._fallback_warehouse_hindrance_analysis(query)
            else:
                return self._fallback_warehouse_hindrance_analysis(query)

        except Exception as e:
            logger.error(f"Failed to analyze warehouse hindrance: {e}")
            return self._fallback_warehouse_hindrance_analysis(query)

    def _fallback_warehouse_hindrance_analysis(self, query: str) -> dict:
        """Fallback warehouse hindrance analysis when AI fails"""
        analysis = {
            "hindrance_type": "equipment_failure",
            "severity_level": "moderate",
            "inventory_affected": False,
            "affected_systems": ["picking"],
            "estimated_duration": "hours",
            "customer_order_risk": "low",
            "business_impact": "moderate",
            "requires_immediate_evacuation": False,
            "supplier_notification_needed": False,
            "alternative_sourcing_required": False
        }

        query_lower = query.lower()

        # Detect hindrance type
        if any(word in query_lower for word in ['power', 'electricity', 'blackout', 'outage']):
            analysis.update({
                "hindrance_type": "power_outage",
                "severity_level": "severe",
                "affected_systems": ["picking", "packing", "inventory", "temperature_control"],
                "business_impact": "significant",
                "inventory_affected": True
            })
        elif any(word in query_lower for word in ['temperature', 'freezer', 'cooling', 'cold']):
            analysis.update({
                "hindrance_type": "temperature_control_failure",
                "severity_level": "severe",
                "inventory_affected": True,
                "customer_order_risk": "high",
                "affected_systems": ["temperature_control"]
            })
        elif any(word in query_lower for word in ['inventory', 'system', 'computer', 'software']):
            analysis.update({
                "hindrance_type": "inventory_system_failure",
                "severity_level": "moderate",
                "affected_systems": ["inventory", "picking"]
            })
        elif any(word in query_lower for word in ['staff', 'workers', 'employees', 'shortage']):
            analysis.update({
                "hindrance_type": "staff_shortage",
                "severity_level": "moderate",
                "affected_systems": ["picking", "packing"]
            })

        # Detect severity indicators
        if any(word in query_lower for word in ['emergency', 'urgent', 'critical', 'immediate']):
            analysis["severity_level"] = "critical"
        elif any(word in query_lower for word in ['serious', 'major', 'significant']):
            analysis["severity_level"] = "severe"

        return analysis

    def assess_warehouse_operational_risks(self, hindrance_analysis: dict, store_id: str) -> dict:
        """Assess operational risks from warehouse hindrance"""
        risks = {
            "immediate_closure_required": False,
            "partial_operations_possible": True,
            "inventory_safety_compromised": False,
            "staff_safety_risk": False,
            "customer_order_risk": False,
            "revenue_loss_estimate": "low",
            "reputation_impact": "minimal",
            "supplier_relationship_risk": False,
            "inventory_loss_risk": False,
            "temperature_sensitive_products_risk": False
        }

        severity = hindrance_analysis.get("severity_level", "moderate")
        inventory_affected = hindrance_analysis.get("inventory_affected", False)
        hindrance_type = hindrance_analysis.get("hindrance_type", "equipment_failure")

        # Inventory-specific assessments
        if inventory_affected:
            risks.update({
                "immediate_closure_required": True,
                "partial_operations_possible": False,
                "customer_order_risk": True,
                "revenue_loss_estimate": "high",
                "reputation_impact": "significant"
            })

        # Temperature control failures are critical for grocery operations
        if hindrance_type == "temperature_control_failure":
            risks.update({
                "inventory_safety_compromised": True,
                "temperature_sensitive_products_risk": True,
                "inventory_loss_risk": True,
                "immediate_closure_required": True
            })

        # Severity-based risk escalation
        if severity in ["critical", "emergency"]:
            risks.update({
                "immediate_closure_required": True,
                "revenue_loss_estimate": "high",
                "reputation_impact": "significant"
            })

        # Dark store credibility impact
        credibility_score = self.get_dark_store_credibility_score(store_id)
        if credibility_score <= 5:
            risks["reputation_impact"] = "severe"

        return risks

    def determine_warehouse_crisis_response_level(self, hindrance_analysis: dict, risk_assessment: dict) -> dict:
        """Determine appropriate crisis response level for warehouse operations"""
        response_level = {
            "level": "standard",
            "platform_notification": False,
            "emergency_services_contact": False,
            "supplier_notification": False,
            "management_escalation": False,
            "customer_mass_notification": False,
            "order_suspension_required": False,
            "inventory_preservation_protocols": False,
            "immediate_action_timeline": "30 minutes"
        }

        severity = hindrance_analysis.get("severity_level", "moderate")
        inventory_affected = hindrance_analysis.get("inventory_affected", False)
        immediate_closure = risk_assessment.get("immediate_closure_required", False)

        # Response level escalation matrix for warehouse
        if severity == "emergency" or hindrance_analysis.get("requires_immediate_evacuation"):
            response_level.update({
                "level": "emergency",
                "platform_notification": True,
                "emergency_services_contact": True,
                "management_escalation": True,
                "customer_mass_notification": True,
                "order_suspension_required": True,
                "inventory_preservation_protocols": True,
                "immediate_action_timeline": "immediate"
            })
        elif severity == "critical" or inventory_affected:
            response_level.update({
                "level": "critical",
                "platform_notification": True,
                "supplier_notification": True,
                "management_escalation": True,
                "customer_mass_notification": True,
                "order_suspension_required": True,
                "inventory_preservation_protocols": True,
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

        return response_level

    def evaluate_customer_impact_from_warehouse_hindrance(self, hindrance_analysis: dict, crisis_response_level: dict) -> dict:
        """Evaluate impact on customers and orders from warehouse hindrance"""
        impact = {
            "orders_affected": 0,
            "customers_to_notify": 0,
            "refund_required": False,
            "alternative_sourcing": False,
            "compensation_required": False,
            "inventory_shortage_risk": False,
            "delivery_disruption": False,
            "estimated_customer_complaints": 0,
            "customer_satisfaction_impact": "minimal"
        }

        severity = hindrance_analysis.get("severity_level", "moderate")
        customer_order_risk = hindrance_analysis.get("customer_order_risk", "low")
        order_suspension = crisis_response_level.get("order_suspension_required", False)

        # Customer impact based on severity
        if order_suspension:
            impact.update({
                "orders_affected": 20,  # Estimated pending orders for warehouse
                "customers_to_notify": 20,
                "refund_required": True,
                "alternative_sourcing": True,
                "compensation_required": True,
                "delivery_disruption": True
            })

        # Inventory risk assessment
        if customer_order_risk in ["high", "critical"]:
            impact.update({
                "inventory_shortage_risk": True,
                "compensation_required": True,
                "estimated_customer_complaints": 12
            })

        # Satisfaction impact prediction
        if severity in ["critical", "emergency"]:
            impact["customer_satisfaction_impact"] = "severe"
        elif severity == "severe":
            impact["customer_satisfaction_impact"] = "significant"
        elif severity == "moderate":
            impact["customer_satisfaction_impact"] = "moderate"

        return impact

    def generate_warehouse_emergency_action_plan(self, hindrance_analysis: dict, risk_assessment: dict,
                                                crisis_response_level: dict, customer_impact: dict) -> dict:
        """Generate warehouse emergency action plan using AI reasoning"""
        action_prompt = f"""
        Generate a comprehensive emergency action plan for this warehouse crisis:

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
                    function_name="generate_warehouse_emergency_action_plan",
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
                    return self._fallback_warehouse_emergency_action_plan(hindrance_analysis, crisis_response_level)
            else:
                return self._fallback_warehouse_emergency_action_plan(hindrance_analysis, crisis_response_level)

        except Exception as e:
            logger.error(f"Failed to generate warehouse action plan: {e}")
            return self._fallback_warehouse_emergency_action_plan(hindrance_analysis, crisis_response_level)

    def _fallback_warehouse_emergency_action_plan(self, hindrance_analysis: dict, crisis_response_level: dict) -> dict:
        """Fallback warehouse emergency action plan when AI fails"""
        plan = {
            "immediate_actions": [
                "Assess situation and ensure staff safety",
                "Stop new order processing",
                "Secure temperature-sensitive inventory"
            ],
            "short_term_actions": [
                "Contact equipment repair services",
                "Implement alternative warehouse procedures",
                "Coordinate with supplier for emergency restocking"
            ],
            "recovery_actions": [
                "Resume normal warehouse operations",
                "Monitor inventory quality and systems",
                "Follow up with affected customers"
            ],
            "staff_responsibilities": {
                "warehouse_manager": "Coordinate overall response",
                "picking_staff": "Implement safety protocols",
                "inventory_staff": "Secure and monitor stock"
            },
            "external_coordination": [
                "Platform support team",
                "Equipment maintenance services"
            ],
            "resource_requirements": [
                "Emergency contact list",
                "Backup warehouse procedures manual"
            ],
            "success_criteria": [
                "Warehouse operations fully restored",
                "Inventory integrity maintained"
            ]
        }

        level = crisis_response_level.get("level", "standard")
        hindrance_type = hindrance_analysis.get("hindrance_type", "equipment_failure")

        # Customize based on crisis level
        if level in ["critical", "emergency"]:
            plan["immediate_actions"].extend([
                "Activate emergency inventory preservation protocols",
                "Contact emergency services if required",
                "Secure all perishable inventory immediately"
            ])
            plan["external_coordination"].extend([
                "Emergency services",
                "Supplier emergency contacts"
            ])

        # Customize based on hindrance type
        if hindrance_type == "temperature_control_failure":
            plan["immediate_actions"].append("Move temperature-sensitive products to backup cooling")
            plan["external_coordination"].append("Emergency refrigeration services")

        return plan

    def activate_warehouse_platform_support_protocols(self, emergency_action_plan: dict, crisis_response_level: dict) -> dict:
        """Activate platform support for warehouse operations"""
        support = {
            "technical_support_activated": False,
            "customer_service_escalation": False,
            "order_management_override": False,
            "delivery_partner_notification": False,
            "alternative_warehouse_coordination": False,
            "emergency_communication_tools": False,
            "revenue_protection_measures": False,
            "supplier_coordination": False
        }

        level = crisis_response_level.get("level", "standard")

        # Activate support based on crisis level
        if level in ["emergency", "critical"]:
            support.update({
                "technical_support_activated": True,
                "customer_service_escalation": True,
                "order_management_override": True,
                "delivery_partner_notification": True,
                "alternative_warehouse_coordination": True,
                "emergency_communication_tools": True,
                "revenue_protection_measures": True,
                "supplier_coordination": True
            })
        elif level == "severe":
            support.update({
                "technical_support_activated": True,
                "customer_service_escalation": True,
                "order_management_override": True,
                "delivery_partner_notification": True,
                "alternative_warehouse_coordination": True
            })

        return support

    def establish_warehouse_hindrance_communication_strategy(self, hindrance_analysis: dict, customer_impact: dict, emergency_action_plan: dict) -> dict:
        """Establish communication strategy for warehouse stakeholders"""
        strategy = {
            "customer_message_tone": "apologetic",
            "transparency_level": "high",
            "communication_channels": ["app", "sms"],
            "update_frequency": "every_30_minutes",
            "key_messages": [],
            "staff_briefing_required": True,
            "supplier_communication": False,
            "delivery_partner_updates": False
        }

        severity = hindrance_analysis.get("severity_level", "moderate")
        inventory_risk = customer_impact.get("inventory_shortage_risk", False)

        # Customize communication based on severity
        if severity in ["critical", "emergency"]:
            strategy.update({
                "transparency_level": "complete",
                "communication_channels": ["app", "sms", "email"],
                "update_frequency": "every_15_minutes",
                "supplier_communication": True,
                "delivery_partner_updates": True
            })

        # Key messages based on situation
        if inventory_risk:
            strategy["key_messages"].extend([
                "Product availability temporarily affected",
                "Working to restore full inventory access",
                "Alternative products and refunds available"
            ])
        else:
            strategy["key_messages"].extend([
                "We are addressing a temporary operational issue",
                "Working to restore normal service quickly",
                "Customer orders are our top priority"
            ])

        return strategy

    def create_warehouse_hindrance_recovery_plan(self, hindrance_analysis: dict, emergency_action_plan: dict, platform_support: dict) -> dict:
        """Create recovery timeline and monitoring plan for warehouse"""
        recovery = {
            "estimated_recovery_time": "2-4 hours",
            "recovery_phases": [],
            "monitoring_checkpoints": [],
            "quality_assurance_steps": [],
            "customer_notification_timeline": [],
            "performance_metrics_tracking": [],
            "inventory_verification_required": True
        }

        estimated_duration = hindrance_analysis.get("estimated_duration", "hours")
        hindrance_type = hindrance_analysis.get("hindrance_type", "equipment_failure")

        # Customize recovery timeline
        if estimated_duration == "days":
            recovery["estimated_recovery_time"] = "24-48 hours"
        elif estimated_duration == "minutes":
            recovery["estimated_recovery_time"] = "30-60 minutes"

        # Recovery phases for warehouse
        recovery["recovery_phases"] = [
            "Emergency response and inventory securing",
            "System restoration and testing",
            "Gradual order fulfillment resumption",
            "Full warehouse operations restoration",
            "Performance monitoring and improvement"
        ]

        # Warehouse-specific monitoring checkpoints
        recovery["monitoring_checkpoints"] = [
            "Inventory integrity verified",
            "Temperature control systems functional",
            "Picking and packing systems operational",
            "Customer order processing accuracy confirmed"
        ]

        return recovery

    def generate_warehouse_hindrance_management_response(self, hindrance_analysis: dict, risk_assessment: dict,
                                                        crisis_response_level: dict, emergency_action_plan: dict,
                                                        communication_strategy: dict, recovery_plan: dict) -> str:
        """Generate comprehensive warehouse crisis management response"""
        severity = hindrance_analysis.get("severity_level", "moderate")
        hindrance_type = hindrance_analysis.get("hindrance_type", "equipment_failure")
        level = crisis_response_level.get("level", "standard")

        if level in ["emergency", "critical"]:
            return f"""🏪 **CRITICAL WAREHOUSE EMERGENCY - IMMEDIATE ACTION REQUIRED**

**WAREHOUSE OPERATIONAL CRISIS**

**🔍 Crisis Assessment:**
- Hindrance type: {hindrance_type.replace('_', ' ').title()}
- Severity level: {severity.upper()}
- Inventory affected: {'YES' if hindrance_analysis.get('inventory_affected') else 'NO'}
- Customer order risk: {hindrance_analysis.get('customer_order_risk', 'unknown').upper()}
- Estimated duration: {hindrance_analysis.get('estimated_duration', 'unknown')}

**🚨 IMMEDIATE EMERGENCY ACTIONS (Next {crisis_response_level.get('immediate_action_timeline', '5 minutes')}):**
{chr(10).join([f"- {action}" for action in emergency_action_plan.get('immediate_actions', ['Assess situation and ensure safety'])])}

**⚠️ CRITICAL WAREHOUSE MEASURES:**
- Staff safety protocols: {'ACTIVATED' if risk_assessment.get('staff_safety_risk') else 'STANDARD'}
- Inventory safety status: {'AT RISK' if risk_assessment.get('inventory_safety_compromised') else 'SECURED'}
- Temperature control: {'CRITICAL' if hindrance_type == 'temperature_control_failure' else 'MONITORING'}
- Emergency protocols: {'ACTIVATED' if crisis_response_level.get('inventory_preservation_protocols') else 'STANDBY'}

**📞 EMERGENCY COORDINATION ACTIVATED:**
{chr(10).join([f"- {contact}" for contact in emergency_action_plan.get('external_coordination', ['Platform emergency support'])])}

**🔒 OPERATIONAL STATUS:**
- Order processing: SUSPENDED IMMEDIATELY
- Current orders: {customer_impact.get('orders_affected', 'Unknown')} orders affected
- Customer notifications: MASS ALERT SENT
- Inventory protection: MAXIMUM PRIORITY

**👥 WAREHOUSE STAFF RESPONSIBILITIES:**
{chr(10).join([f"- {role}: {responsibility}" for role, responsibility in emergency_action_plan.get('staff_responsibilities', {}).items()])}

**📋 RECOVERY TIMELINE:**
- Emergency response: {crisis_response_level.get('immediate_action_timeline', 'immediate')}
- System restoration: {recovery_plan.get('estimated_recovery_time', '2-4 hours')}
- Service restoration: Gradual resumption after full system verification
- Full operations: Subject to complete safety and inventory verification

**📞 STAKEHOLDER COMMUNICATION STRATEGY:**
- Message tone: {communication_strategy.get('customer_message_tone', 'apologetic')}
- Transparency level: {communication_strategy.get('transparency_level', 'high')}
- Update frequency: {communication_strategy.get('update_frequency', 'continuous')}
- Channels activated: {', '.join(communication_strategy.get('communication_channels', ['app', 'sms']))}

**✅ SUCCESS CRITERIA FOR RESUMPTION:**
{chr(10).join([f"- {criteria}" for criteria in emergency_action_plan.get('success_criteria', ['Systems verified', 'Inventory secured'])])}

This is a critical warehouse emergency requiring immediate action. Follow all protocols precisely and prioritize inventory protection and customer service."""

        else:  # moderate or standard
            return f"""🏪 **Warehouse Operational Challenge - Management Response Activated**

**WAREHOUSE DISRUPTION MANAGEMENT**

**📋 Situation Overview:**
- Challenge type: {hindrance_type.replace('_', ' ').title()}
- Impact level: {severity.title()}
- Resolution priority: {crisis_response_level.get('immediate_action_timeline', 'Standard')}
- Service capability: {'Reduced' if not risk_assessment.get('partial_operations_possible', True) else 'Maintained with modifications'}

**🔄 IMMEDIATE MANAGEMENT ACTIONS:**
{chr(10).join([f"- {action}" for action in emergency_action_plan.get('immediate_actions', ['Assess situation and implement workarounds'])])}

**📊 OPERATIONAL ADJUSTMENTS:**
- Service modifications: Implementing alternative warehouse procedures
- Customer communication: Proactive updates on any delays
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
{chr(10).join([f"- {step}" for step in recovery_plan.get('quality_assurance_steps', ['Verify all systems operational', 'Confirm inventory integrity'])])}

**📈 CONTINUOUS IMPROVEMENT:**
- Incident documentation: Complete record for future prevention
- Process optimization: Identify improvement opportunities
- Staff training: Address any skill gaps identified
- System enhancement: Upgrade resilience where possible

Professional management of warehouse challenges maintains customer confidence and operational excellence."""