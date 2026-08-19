"""
Grab Express Customer Vehicle Matching Handler
Handles vehicle type and capacity matching issues specific to express delivery
"""

import logging
import os
import sys
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class VehicleMatchingHandler:
    """Vehicle type and capacity matching for express packages with strict workflows"""

    def __init__(self):
        self.service = "grab_express"
        self.actor = "customer"
        self.handler_type = "vehicle_matching_handler"
        try:
            self.ai_engine = EnhancedAgenticAIEngine()
        except Exception as e:
            logger.warning(f"AI engine initialization failed: {e}")
            self.ai_engine = None

    def handle_vehicle_size_mismatch(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle package too large for assigned vehicle with strict 5-step workflow"""
        logger.info(f"Processing vehicle size mismatch complaint: {query[:100]}...")

        # Step 1: Identify the mismatch between package size and vehicle
        mismatch_analysis = self.analyze_size_mismatch(query)
        logger.info(f"Mismatch analysis: {mismatch_analysis}")

        # Step 2: Determine the correct vehicle type needed
        vehicle_requirement = self.determine_required_vehicle(mismatch_analysis, query)
        logger.info(f"Vehicle requirement: {vehicle_requirement}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on vehicle upgrade and cost adjustment
        decision = self.decide_vehicle_upgrade_resolution(mismatch_analysis, vehicle_requirement, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with vehicle upgrade details and timeline
        response = self.generate_size_mismatch_response(decision, mismatch_analysis, vehicle_requirement, query)
        logger.info("Vehicle size mismatch response generated successfully")
        return response

    def handle_vehicle_upgrade_needed(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle package requiring truck but bike/car assigned with strict 5-step workflow"""
        logger.info(f"Processing vehicle upgrade needed complaint: {query[:100]}...")

        # Step 1: Identify why an upgrade is required
        upgrade_analysis = self.analyze_upgrade_requirement(query)
        logger.info(f"Upgrade analysis: {upgrade_analysis}")

        # Step 2: Assess urgency and check truck availability
        availability_check = self.check_truck_availability(upgrade_analysis, query)
        logger.info(f"Truck availability: {availability_check}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on upgrade execution and compensation
        decision = self.decide_upgrade_execution(upgrade_analysis, availability_check, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with upgrade confirmation and new timeline
        response = self.generate_upgrade_response(decision, upgrade_analysis, query)
        logger.info("Vehicle upgrade response generated successfully")
        return response

    def handle_weight_vehicle_mismatch(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle heavy package assigned to underweight vehicle with strict 5-step workflow"""
        logger.info(f"Processing weight vehicle mismatch complaint: {query[:100]}...")

        # Step 1: Identify the weight versus vehicle capacity mismatch
        weight_analysis = self.analyze_weight_mismatch(query)
        logger.info(f"Weight analysis: {weight_analysis}")

        # Step 2: Determine the correct vehicle capacity needed
        capacity_requirement = self.determine_required_capacity(weight_analysis, query)
        logger.info(f"Capacity requirement: {capacity_requirement}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on vehicle reassignment and handling support
        decision = self.decide_weight_mismatch_resolution(weight_analysis, capacity_requirement, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with safe handling reassignment details
        response = self.generate_weight_mismatch_response(decision, weight_analysis, capacity_requirement, query)
        logger.info("Weight vehicle mismatch response generated successfully")
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

    def analyze_size_mismatch(self, query: str) -> str:
        """Identify the package size vs vehicle size mismatch"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['too big', 'too large', "doesn't fit", 'cannot fit']):
            return "PACKAGE_TOO_LARGE_FOR_BIKE"
        elif any(w in query_lower for w in ['oversized', 'bulky', 'wide']):
            return "OVERSIZED_PACKAGE_WRONG_VEHICLE"
        return "GENERAL_SIZE_MISMATCH"

    def determine_required_vehicle(self, analysis: str, query: str) -> str:
        """Determine what vehicle type is actually needed"""
        if any(w in query.lower() for w in ['car', 'sedan', 'medium']):
            return "CAR_REQUIRED"
        elif any(w in query.lower() for w in ['truck', 'van', 'large']):
            return "TRUCK_OR_VAN_REQUIRED"
        return "CAR_OR_LARGER_REQUIRED"

    def decide_vehicle_upgrade_resolution(self, analysis: str, vehicle: str, credibility: int) -> str:
        """Decide vehicle upgrade action and cost handling"""
        # Assigning a bike to a package that cannot fit is our booking error, so the
        # upgrade is free regardless of how large the correct vehicle needs to be
        if analysis == "PACKAGE_TOO_LARGE_FOR_BIKE":
            return "FREE_UPGRADE_PRIORITY_REASSIGNMENT"
        elif credibility >= 6:
            return "FREE_UPGRADE_PRIORITY_REASSIGNMENT"
        elif vehicle == "TRUCK_OR_VAN_REQUIRED" and credibility >= 4:
            return "UPGRADE_WITH_MINIMAL_SURCHARGE"
        elif credibility >= 4:
            return "UPGRADE_WITH_MINIMAL_SURCHARGE"
        return "STANDARD_UPGRADE_PROCESS"

    def generate_size_mismatch_response(self, decision: str, analysis: str, vehicle: str, query: str) -> str:
        """Generate vehicle size mismatch response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_vehicle_size_mismatch",
                    user_query=f"DECISION: {decision} | MISMATCH: {analysis} | REQUIRED: {vehicle} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "FREE_UPGRADE_PRIORITY_REASSIGNMENT": "We apologize for the vehicle mismatch. Your package has been immediately reassigned to an appropriate larger vehicle at no additional cost. The upgraded delivery will be completed within 2 hours.",
            "UPGRADE_WITH_MINIMAL_SURCHARGE": "We are upgrading your delivery to a suitable vehicle. A minimal surcharge applies for the vehicle upgrade and will be communicated to you before confirmation.",
            "STANDARD_UPGRADE_PROCESS": "Your delivery is being reassigned to a vehicle with appropriate capacity. You will receive updated tracking details shortly."
        }
        return responses.get(decision, "We apologize for the vehicle capacity mismatch. Your package has been reassigned to a car/truck delivery partner at no additional cost.")

    def analyze_upgrade_requirement(self, query: str) -> str:
        """Identify the reason why a vehicle upgrade is needed"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['furniture', 'sofa', 'appliance', 'heavy']):
            return "HEAVY_OR_LARGE_ITEM_REQUIRES_TRUCK"
        elif any(w in query_lower for w in ['multiple', 'many', 'bulk']):
            return "MULTIPLE_PACKAGES_REQUIRE_TRUCK"
        return "GENERAL_TRUCK_REQUIRED"

    def check_truck_availability(self, analysis: str, query: str) -> str:
        """Check availability of truck in the customer's area"""
        query_lower = query.lower()
        # Remote pickup points and out-of-hours requests are where truck supply runs short
        if any(w in query_lower for w in ['remote', 'outskirts', 'village', 'far from city']):
            return "NO_TRUCK_NEARBY"
        elif any(w in query_lower for w in ['night', 'midnight', 'late', 'early morning']):
            return "LIMITED_TRUCK_AVAILABILITY"
        elif analysis == "MULTIPLE_PACKAGES_REQUIRE_TRUCK":
            return "LIMITED_TRUCK_AVAILABILITY"
        return "TRUCK_AVAILABLE_NEARBY"

    def decide_upgrade_execution(self, analysis: str, availability: str, credibility: int) -> str:
        """Decide how to execute the vehicle upgrade"""
        if availability == "NO_TRUCK_NEARBY":
            return "UPGRADE_PENDING_VEHICLE_AVAILABILITY"
        elif availability == "TRUCK_AVAILABLE_NEARBY" and credibility >= 6:
            return "IMMEDIATE_TRUCK_DISPATCH_FREE_UPGRADE"
        elif analysis == "HEAVY_OR_LARGE_ITEM_REQUIRES_TRUCK" and credibility >= 6:
            return "IMMEDIATE_TRUCK_DISPATCH_FREE_UPGRADE"
        elif credibility >= 4:
            return "TRUCK_DISPATCHED_STANDARD_RATE"
        return "UPGRADE_PENDING_VEHICLE_AVAILABILITY"

    def generate_upgrade_response(self, decision: str, analysis: str, query: str) -> str:
        """Generate vehicle upgrade needed response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_vehicle_upgrade_needed",
                    user_query=f"DECISION: {decision} | UPGRADE_REASON: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "IMMEDIATE_TRUCK_DISPATCH_FREE_UPGRADE": "We understand your package requires truck capacity. A truck has been immediately assigned at no extra cost. Your package will be picked up and delivered within 3 hours.",
            "TRUCK_DISPATCHED_STANDARD_RATE": "A truck with appropriate capacity has been dispatched. Standard truck delivery rates apply and your delivery will be completed within 3-4 hours.",
            "UPGRADE_PENDING_VEHICLE_AVAILABILITY": "We are locating the nearest available truck for your delivery. You will receive confirmation and a new ETA within 30 minutes."
        }
        return responses.get(decision, "We understand your package requires truck capacity. We are immediately upgrading your delivery and arranging the correct vehicle.")

    def analyze_weight_mismatch(self, query: str) -> str:
        """Identify the weight versus vehicle capacity issue"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['kg', 'kilos', 'kilograms', 'heavy']):
            return "HEAVY_PACKAGE_WRONG_VEHICLE"
        elif any(w in query_lower for w in ['too heavy', 'overweight', 'excess weight']):
            return "PACKAGE_EXCEEDS_VEHICLE_WEIGHT_LIMIT"
        return "GENERAL_WEIGHT_MISMATCH"

    def determine_required_capacity(self, analysis: str, query: str) -> str:
        """Determine the vehicle capacity needed for the package weight"""
        if any(w in query.lower() for w in ['100', '200', 'ton']):
            return "HEAVY_DUTY_TRUCK_REQUIRED"
        elif any(w in query.lower() for w in ['50', '30', 'cargo']):
            return "CARGO_VAN_OR_TRUCK_REQUIRED"
        return "STANDARD_TRUCK_REQUIRED"

    def decide_weight_mismatch_resolution(self, analysis: str, capacity: str, credibility: int) -> str:
        """Decide resolution for weight vehicle mismatch"""
        # Exceeding a vehicle's rated weight limit is a safety issue, so the correct
        # vehicle goes out free rather than waiting on a credibility check
        if analysis == "PACKAGE_EXCEEDS_VEHICLE_WEIGHT_LIMIT":
            return "SAFE_VEHICLE_DISPATCHED_FREE_UPGRADE"
        elif capacity == "HEAVY_DUTY_TRUCK_REQUIRED" and credibility >= 5:
            return "SAFE_VEHICLE_DISPATCHED_FREE_UPGRADE"
        elif credibility >= 6:
            return "SAFE_VEHICLE_DISPATCHED_FREE_UPGRADE"
        elif credibility >= 4:
            return "APPROPRIATE_VEHICLE_DISPATCHED_RATE_ADJUSTED"
        return "VEHICLE_REASSIGNMENT_IN_PROGRESS"

    def generate_weight_mismatch_response(self, decision: str, analysis: str, capacity: str, query: str) -> str:
        """Generate weight vehicle mismatch response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_weight_vehicle_mismatch",
                    user_query=f"DECISION: {decision} | WEIGHT: {analysis} | CAPACITY: {capacity} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "SAFE_VEHICLE_DISPATCHED_FREE_UPGRADE": "Heavy packages require appropriate vehicle capacity. A vehicle with proper weight handling has been dispatched at no additional charge. Safe delivery with professional handling will be completed within 2-3 hours.",
            "APPROPRIATE_VEHICLE_DISPATCHED_RATE_ADJUSTED": "We have reassigned your delivery to a vehicle with correct weight capacity. The rate has been adjusted accordingly and delivery will be completed within 3 hours.",
            "VEHICLE_REASSIGNMENT_IN_PROGRESS": "We are reassigning your delivery to a vehicle with appropriate weight capacity. You will receive updated tracking and ETA within 30 minutes."
        }
        return responses.get(decision, "Heavy packages require appropriate vehicle capacity. We are upgrading your delivery to a truck with proper weight handling capability.")
