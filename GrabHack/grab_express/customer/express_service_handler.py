"""
Grab Express Customer Express Service Handler
Handles express delivery urgency and speed requirements
"""

import logging
import os
import sys
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class ExpressServiceHandler:
    """Express delivery urgency and speed management with strict workflows"""

    def __init__(self):
        self.service = "grab_express"
        self.actor = "customer"
        self.handler_type = "express_service_handler"
        try:
            self.ai_engine = EnhancedAgenticAIEngine()
        except Exception as e:
            logger.warning(f"AI engine initialization failed: {e}")
            self.ai_engine = None

    def handle_urgency_vehicle_conflict(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle same-day delivery not available for assigned vehicle with strict 5-step workflow"""
        logger.info(f"Processing urgency vehicle conflict complaint: {query[:100]}...")

        # Step 1: Identify the urgency and vehicle conflict type
        conflict_analysis = self.analyze_urgency_conflict(query)
        logger.info(f"Conflict analysis: {conflict_analysis}")

        # Step 2: Check same-day delivery availability and alternatives
        availability_check = self.check_same_day_availability(conflict_analysis, query)
        logger.info(f"Availability check: {availability_check}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on express upgrade and delivery guarantee
        decision = self.decide_urgency_resolution(conflict_analysis, availability_check, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with express delivery confirmation
        response = self.generate_urgency_response(decision, conflict_analysis, query)
        logger.info("Urgency vehicle conflict response generated successfully")
        return response

    def handle_speed_requirements(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle urgent delivery requiring faster vehicle with strict 5-step workflow"""
        logger.info(f"Processing speed requirements complaint: {query[:100]}...")

        # Step 1: Identify the speed and urgency requirement
        speed_analysis = self.analyze_speed_requirement(query)
        logger.info(f"Speed analysis: {speed_analysis}")

        # Step 2: Assess feasibility of meeting the speed requirement
        feasibility_check = self.assess_speed_feasibility(speed_analysis, query)
        logger.info(f"Feasibility check: {feasibility_check}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on priority partner assignment and guarantee
        decision = self.decide_speed_resolution(speed_analysis, feasibility_check, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with priority delivery confirmation
        response = self.generate_speed_response(decision, speed_analysis, query)
        logger.info("Speed requirements response generated successfully")
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

    def analyze_urgency_conflict(self, query: str) -> str:
        """Identify the urgency vs vehicle type conflict"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['same day', 'today', 'urgent', 'asap']):
            return "SAME_DAY_DELIVERY_REQUIRED"
        elif any(w in query_lower for w in ['few hours', '2 hours', '3 hours']):
            return "VERY_FAST_DELIVERY_REQUIRED"
        return "GENERAL_URGENCY_CONFLICT"

    def check_same_day_availability(self, analysis: str, query: str) -> str:
        """Check availability of express vehicles for same-day delivery"""
        query_lower = query.lower()
        # A bike-assigned booking can always be upgraded; truck/refrigerated capacity is limited
        if any(w in query_lower for w in ['truck', 'refrigerated', 'oversized', 'bulk']):
            return "UPGRADE_CAPACITY_CONSTRAINED"
        elif analysis == "VERY_FAST_DELIVERY_REQUIRED":
            return "EXPRESS_PARTNER_AVAILABLE_LIMITED"
        return "EXPRESS_PARTNER_AVAILABLE"

    def decide_urgency_resolution(self, analysis: str, availability: str, credibility: int) -> str:
        """Decide resolution for urgency vehicle conflict"""
        if availability == "UPGRADE_CAPACITY_CONSTRAINED":
            return "BEST_EFFORT_SAME_DAY_DELIVERY"
        elif analysis == "SAME_DAY_DELIVERY_REQUIRED" and availability == "EXPRESS_PARTNER_AVAILABLE" and credibility >= 6:
            return "PRIORITY_EXPRESS_UPGRADE_GUARANTEED"
        elif credibility >= 5:
            return "EXPRESS_UPGRADE_APPLIED_NO_EXTRA_COST"
        return "BEST_EFFORT_SAME_DAY_DELIVERY"

    def generate_urgency_response(self, decision: str, analysis: str, query: str) -> str:
        """Generate urgency vehicle conflict response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_urgency_vehicle_conflict",
                    user_query=f"DECISION: {decision} | URGENCY: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "PRIORITY_EXPRESS_UPGRADE_GUARANTEED": "For your urgent same-day delivery requirement, we have upgraded your delivery to a priority express partner with a faster vehicle at no additional cost. Guaranteed delivery within the same day.",
            "EXPRESS_UPGRADE_APPLIED_NO_EXTRA_COST": "We have upgraded your delivery to an express vehicle to meet your urgency requirements. Your delivery is now prioritized and will arrive within the promised timeframe at no extra charge.",
            "BEST_EFFORT_SAME_DAY_DELIVERY": "We are doing our best to complete your delivery today. A faster vehicle option has been assigned and our team will keep you updated on progress every 30 minutes."
        }
        return responses.get(decision, "For urgent same-day delivery requirements, we are upgrading your delivery to a faster vehicle at no additional cost.")

    def analyze_speed_requirement(self, query: str) -> str:
        """Identify the specific speed and delivery time requirement"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['1 hour', 'one hour', 'within hour']):
            return "ONE_HOUR_DELIVERY_REQUIRED"
        elif any(w in query_lower for w in ['2 hour', 'two hours', 'within 2']):
            return "TWO_HOUR_DELIVERY_REQUIRED"
        elif any(w in query_lower for w in ['fastest', 'quickest', 'asap']):
            return "FASTEST_POSSIBLE_DELIVERY"
        return "GENERAL_SPEED_REQUIREMENT"

    def assess_speed_feasibility(self, analysis: str, query: str) -> str:
        """Assess whether the speed requirement can be met"""
        if analysis == "ONE_HOUR_DELIVERY_REQUIRED":
            return "FEASIBLE_WITH_PRIORITY_PARTNER"
        elif analysis == "TWO_HOUR_DELIVERY_REQUIRED":
            return "HIGHLY_FEASIBLE"
        return "FEASIBLE_WITH_OPTIMIZATION"

    def decide_speed_resolution(self, analysis: str, feasibility: str, credibility: int) -> str:
        """Decide resolution for speed requirement"""
        # The one-hour guarantee carries an auto-refund commitment, so it needs both
        # a feasible window and an established customer
        if analysis == "ONE_HOUR_DELIVERY_REQUIRED" and feasibility == "FEASIBLE_WITH_PRIORITY_PARTNER" and credibility >= 6:
            return "PRIORITY_PARTNER_ASSIGNED_GUARANTEED"
        elif feasibility == "HIGHLY_FEASIBLE" and credibility >= 5:
            return "EXPRESS_PARTNER_ASSIGNED_BEST_ETA"
        elif analysis == "FASTEST_POSSIBLE_DELIVERY" and credibility >= 5:
            return "EXPRESS_PARTNER_ASSIGNED_BEST_ETA"
        elif credibility >= 5:
            return "EXPRESS_PARTNER_ASSIGNED_BEST_ETA"
        return "FASTEST_AVAILABLE_PARTNER_ASSIGNED"

    def generate_speed_response(self, decision: str, analysis: str, query: str) -> str:
        """Generate speed requirements response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_speed_requirements",
                    user_query=f"DECISION: {decision} | SPEED: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "PRIORITY_PARTNER_ASSIGNED_GUARANTEED": "We have assigned our fastest priority delivery partner for your urgent requirement. Guaranteed delivery within 1 hour. If we miss this commitment, a full refund will be processed automatically.",
            "EXPRESS_PARTNER_ASSIGNED_BEST_ETA": "An express delivery partner has been assigned with the fastest available route. Your delivery is being prioritized and you will receive live tracking updates.",
            "FASTEST_AVAILABLE_PARTNER_ASSIGNED": "We have assigned the fastest available delivery partner for your request. Express service guarantees will be honored with compensation for any delays beyond the promised timeframe."
        }
        return responses.get(decision, "Urgent delivery requests are being prioritized. We have assigned a priority delivery partner and your package will arrive as soon as possible.")
