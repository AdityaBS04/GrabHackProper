"""
Grab Express Customer Special Handling Handler
Handles special package requirements (fragile, temperature-sensitive, bulk)
"""

import logging
import os
import sys
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class SpecialHandlingHandler:
    """Special package handling requirements management with strict workflows"""

    def __init__(self):
        self.service = "grab_express"
        self.actor = "customer"
        self.handler_type = "special_handling_handler"
        try:
            self.ai_engine = EnhancedAgenticAIEngine()
        except Exception as e:
            logger.warning(f"AI engine initialization failed: {e}")
            self.ai_engine = None

    def handle_fragile_vehicle_requirements(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle fragile items needing car instead of bike with strict 5-step workflow"""
        logger.info(f"Processing fragile vehicle requirements complaint: {query[:100]}...")

        # Step 1: Identify what fragile item is at risk and the current vehicle issue
        fragile_analysis = self.analyze_fragile_item_risk(query)
        logger.info(f"Fragile analysis: {fragile_analysis}")

        # Step 2: Assess whether damage has occurred or is at risk
        damage_risk = self.assess_fragile_damage_risk(fragile_analysis, query)
        logger.info(f"Damage risk: {damage_risk}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on vehicle upgrade and special handling protocol
        decision = self.decide_fragile_handling_resolution(fragile_analysis, damage_risk, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with safe vehicle upgrade and handling confirmation
        response = self.generate_fragile_response(decision, fragile_analysis, damage_risk, query)
        logger.info("Fragile vehicle requirements response generated successfully")
        return response

    def handle_temperature_vehicle_requirements(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle temperature-sensitive delivery needing refrigerated truck with strict 5-step workflow"""
        logger.info(f"Processing temperature vehicle requirements complaint: {query[:100]}...")

        # Step 1: Identify the temperature sensitivity requirement
        temp_analysis = self.analyze_temperature_requirement(query)
        logger.info(f"Temperature analysis: {temp_analysis}")

        # Step 2: Check if cold chain integrity has been or may be compromised
        cold_chain_status = self.assess_cold_chain_status(temp_analysis, query)
        logger.info(f"Cold chain status: {cold_chain_status}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on refrigerated vehicle dispatch and compensation
        decision = self.decide_temperature_resolution(temp_analysis, cold_chain_status, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with cold chain delivery confirmation
        response = self.generate_temperature_response(decision, temp_analysis, cold_chain_status, query)
        logger.info("Temperature vehicle requirements response generated successfully")
        return response

    def handle_bulk_delivery_requirements(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle bulk delivery requiring truck capacity with strict 5-step workflow"""
        logger.info(f"Processing bulk delivery requirements complaint: {query[:100]}...")

        # Step 1: Identify the bulk delivery scale and vehicle mismatch
        bulk_analysis = self.analyze_bulk_requirement(query)
        logger.info(f"Bulk analysis: {bulk_analysis}")

        # Step 2: Assess the complexity of the bulk delivery
        complexity_assessment = self.assess_bulk_complexity(bulk_analysis, query)
        logger.info(f"Complexity assessment: {complexity_assessment}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on truck dispatch and professional handling arrangement
        decision = self.decide_bulk_resolution(bulk_analysis, complexity_assessment, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with truck and handling team confirmation
        response = self.generate_bulk_response(decision, bulk_analysis, complexity_assessment, query)
        logger.info("Bulk delivery requirements response generated successfully")
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

    def analyze_fragile_item_risk(self, query: str) -> str:
        """Identify the fragile item and current vehicle risk"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['glass', 'glassware', 'mirror', 'crystal']):
            return "GLASS_OR_CRYSTAL_ITEM"
        elif any(w in query_lower for w in ['electronics', 'laptop', 'screen', 'monitor']):
            return "ELECTRONICS_ITEM"
        elif any(w in query_lower for w in ['artwork', 'painting', 'antique']):
            return "ARTWORK_OR_ANTIQUE"
        return "GENERAL_FRAGILE_ITEM"

    def assess_fragile_damage_risk(self, analysis: str, query: str) -> str:
        """Assess whether damage has occurred or is imminent"""
        high_risk = ["GLASS_OR_CRYSTAL_ITEM", "ELECTRONICS_ITEM"]
        if analysis in high_risk or any(w in query.lower() for w in ['bike', 'motorcycle', 'bumpy']):
            return "HIGH_DAMAGE_RISK"
        return "MODERATE_DAMAGE_RISK"

    def decide_fragile_handling_resolution(self, analysis: str, risk: str, credibility: int) -> str:
        """Decide vehicle upgrade and handling protocol for fragile item"""
        if risk == "HIGH_DAMAGE_RISK" and credibility >= 6:
            return "IMMEDIATE_CAR_UPGRADE_PADDED_HANDLING"
        # Irreplaceable and high-value categories get padded transport up front,
        # since damage in transit cannot be undone by compensation
        elif analysis in ("ARTWORK_OR_ANTIQUE", "GLASS_OR_CRYSTAL_ITEM"):
            return "IMMEDIATE_CAR_UPGRADE_PADDED_HANDLING"
        elif analysis == "ELECTRONICS_ITEM" and credibility >= 4:
            return "CAR_UPGRADE_CAREFUL_HANDLING"
        elif credibility >= 5:
            return "CAR_UPGRADE_CAREFUL_HANDLING"
        return "VEHICLE_UPGRADE_STANDARD_CARE"

    def generate_fragile_response(self, decision: str, analysis: str, risk: str, query: str) -> str:
        """Generate fragile item handling response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_fragile_vehicle_requirements",
                    user_query=f"DECISION: {decision} | FRAGILE: {analysis} | RISK: {risk} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "IMMEDIATE_CAR_UPGRADE_PADDED_HANDLING": "Fragile items require special care. A car has been immediately assigned with padded transport and careful handling protocols. Your fragile package will be delivered safely within 2 hours. If any damage occurs, full compensation is guaranteed.",
            "CAR_UPGRADE_CAREFUL_HANDLING": "We have upgraded your delivery to a car with strict fragile item handling instructions given to the partner. Your package will be delivered with the utmost care within 2-3 hours.",
            "VEHICLE_UPGRADE_STANDARD_CARE": "Your delivery has been upgraded to an appropriate vehicle for fragile items. The delivery partner has been briefed on careful handling requirements."
        }
        return responses.get(decision, "Fragile items require special care. We are upgrading your delivery to a car with proper cushioning and careful handling protocols.")

    def analyze_temperature_requirement(self, query: str) -> str:
        """Identify the temperature sensitivity requirement"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['frozen', 'freeze', 'ice cream', 'ice']):
            return "FROZEN_GOODS_REQUIRED"
        elif any(w in query_lower for w in ['chilled', 'refrigerated', 'cold', 'dairy']):
            return "CHILLED_GOODS_REQUIRED"
        elif any(w in query_lower for w in ['medicine', 'medication', 'pharmaceutical', 'vaccine']):
            return "MEDICAL_TEMPERATURE_SENSITIVE"
        return "GENERAL_TEMPERATURE_SENSITIVE"

    def assess_cold_chain_status(self, analysis: str, query: str) -> str:
        """Assess whether cold chain has been compromised"""
        if any(w in query.lower() for w in ['melted', 'spoiled', 'warm', 'thawed']):
            return "COLD_CHAIN_COMPROMISED"
        return "COLD_CHAIN_AT_RISK"

    def decide_temperature_resolution(self, analysis: str, cold_chain: str, credibility: int) -> str:
        """Decide resolution for temperature-sensitive delivery"""
        if cold_chain == "COLD_CHAIN_COMPROMISED" and credibility >= 6:
            return "FULL_REFUND_REFRIGERATED_REDELIVERY"
        # Medical goods are unusable once the chain breaks and cannot be risked further
        elif analysis == "MEDICAL_TEMPERATURE_SENSITIVE" and cold_chain == "COLD_CHAIN_COMPROMISED":
            return "FULL_REFUND_REFRIGERATED_REDELIVERY"
        elif analysis in ("FROZEN_GOODS_REQUIRED", "MEDICAL_TEMPERATURE_SENSITIVE"):
            return "REFRIGERATED_VEHICLE_DISPATCHED"
        elif credibility >= 5:
            return "REFRIGERATED_VEHICLE_DISPATCHED"
        return "TEMPERATURE_VEHICLE_UPGRADE"

    def generate_temperature_response(self, decision: str, analysis: str, cold_chain: str, query: str) -> str:
        """Generate temperature-sensitive delivery response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_temperature_vehicle_requirements",
                    user_query=f"DECISION: {decision} | TEMP_TYPE: {analysis} | COLD_CHAIN: {cold_chain} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "FULL_REFUND_REFRIGERATED_REDELIVERY": "We apologize that the cold chain was compromised. A full refund has been processed and a refrigerated vehicle redelivery has been arranged. Cold chain integrity will be maintained throughout the new delivery.",
            "REFRIGERATED_VEHICLE_DISPATCHED": "A specialized refrigerated vehicle has been dispatched for your temperature-sensitive delivery. Cold chain integrity will be fully maintained and your delivery will arrive within the expected timeframe.",
            "TEMPERATURE_VEHICLE_UPGRADE": "Your delivery has been upgraded to a vehicle with appropriate temperature control. The delivery partner has been briefed on cold chain protocols."
        }
        return responses.get(decision, "Temperature-sensitive packages require refrigerated transport. We are arranging a specialized refrigerated vehicle for your delivery.")

    def analyze_bulk_requirement(self, query: str) -> str:
        """Identify the bulk delivery scale and requirements"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['pallet', 'pallets', 'warehouse']):
            return "PALLET_LEVEL_BULK_DELIVERY"
        elif any(w in query_lower for w in ['boxes', 'cartons', 'multiple']):
            return "MULTI_BOX_BULK_DELIVERY"
        return "GENERAL_BULK_DELIVERY"

    def assess_bulk_complexity(self, analysis: str, query: str) -> str:
        """Assess the complexity of the bulk delivery"""
        high_complexity = ["PALLET_LEVEL_BULK_DELIVERY"]
        return "HIGH_COMPLEXITY" if analysis in high_complexity else "STANDARD_COMPLEXITY"

    def decide_bulk_resolution(self, analysis: str, complexity: str, credibility: int) -> str:
        """Decide truck and handling team arrangement for bulk delivery"""
        if complexity == "HIGH_COMPLEXITY" and credibility >= 6:
            return "LARGE_TRUCK_LOADING_TEAM_DISPATCHED"
        # Pallet freight physically cannot be moved without a loading crew
        elif analysis == "PALLET_LEVEL_BULK_DELIVERY":
            return "LARGE_TRUCK_LOADING_TEAM_DISPATCHED"
        elif analysis == "MULTI_BOX_BULK_DELIVERY" and credibility >= 4:
            return "TRUCK_WITH_HANDLING_SUPPORT"
        elif credibility >= 5:
            return "TRUCK_WITH_HANDLING_SUPPORT"
        return "APPROPRIATE_TRUCK_ASSIGNED"

    def generate_bulk_response(self, decision: str, analysis: str, complexity: str, query: str) -> str:
        """Generate bulk delivery requirements response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_bulk_delivery_requirements",
                    user_query=f"DECISION: {decision} | BULK: {analysis} | COMPLEXITY: {complexity} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "LARGE_TRUCK_LOADING_TEAM_DISPATCHED": "A large truck with a professional loading and unloading team has been arranged for your bulk delivery. All equipment for safe handling is included. Delivery will be completed within 3-4 hours.",
            "TRUCK_WITH_HANDLING_SUPPORT": "A truck with adequate capacity and basic handling support has been assigned. Professional loading assistance will be provided. Your bulk delivery will arrive within 3-4 hours.",
            "APPROPRIATE_TRUCK_ASSIGNED": "An appropriate truck has been assigned for your bulk delivery. The driver has been briefed on the delivery requirements and will contact you 30 minutes before arrival."
        }
        return responses.get(decision, "Bulk deliveries require adequate vehicle capacity. We are assigning a truck with proper loading equipment for your bulk package delivery.")
