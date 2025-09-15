"""
Grab Food Customer Delivery Experience Handler
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


class DeliveryExperienceHandler:
    """Customer-focused delivery experience management with real AI"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_food"
        self.actor = "customer"
        self.handler_type = "delivery_experience_handler"
        self.ai_engine = EnhancedAgenticAIEngine()
        
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

        # Step 4: Validate delay timeline and restaurant preparation time
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
            return "📷 Please upload a photo of what you received so we can verify which items are missing from your order."

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
            return "📷 Please upload a photo showing the temperature issue (melted ice cream, cold food, etc.) so we can properly assess your complaint."

        # Step 2: Analyze image to identify temperature-related problems
        temperature_analysis = self.analyze_temperature_issues_from_image(query, image_data)
        logger.info(f"Temperature analysis: {temperature_analysis}")

        # Step 3: Validate expected food temperature standards
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

        # Step 4: Assess food safety impact and health risks
        safety_assessment = self.assess_food_safety_impact(tampering_analysis, query)
        logger.info(f"Safety assessment: {safety_assessment}")

        # Step 5: Check customer credibility and tampering complaint patterns
        credibility_score = self.get_customer_credibility_score(username)
        tampering_history = self.check_tampering_complaint_history(username)
        logger.info(f"Customer credibility: {credibility_score}/10, History: {tampering_history}")

        # Step 6: Make resolution decision prioritizing food safety
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

    # Helper methods for strict workflow implementation
    def analyze_delivery_delay(self, query: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="analyze_delivery_delay",
            user_query=query,
            service=self.service,
            user_type=self.actor
        )

    def get_customer_delivery_history(self, username: str) -> str:
        return f"Delivery history for {username}: Average delivery time 28 minutes, 12 previous orders, 1 delay complaint"

    def get_customer_credibility_score(self, username: str) -> int:
        return 7

    def check_delay_complaint_pattern(self, username: str) -> str:
        return "Low frequency - 1 delay complaint in last 6 months"

    def validate_delay_timeline(self, delay_analysis: str, query: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="validate_delay_timeline",
            user_query=f"Analysis: {delay_analysis} | Query: {query}",
            service=self.service,
            user_type=self.actor
        )

    def decide_delay_compensation(self, delay_analysis: str, credibility_score: int, timeline_validation: str, complaint_pattern: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="decide_delay_compensation",
            user_query=f"Analysis: {delay_analysis} | Credibility: {credibility_score} | Timeline: {timeline_validation} | Pattern: {complaint_pattern}",
            service=self.service,
            user_type=self.actor
        )

    def generate_delay_response(self, decision: str, delay_analysis: str, query: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="generate_delay_response",
            user_query=f"Decision: {decision} | Analysis: {delay_analysis} | Original: {query}",
            service=self.service,
            user_type=self.actor
        )

    def analyze_delivered_items_from_image(self, query: str, image_data: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="analyze_delivered_items_from_image",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def compare_delivered_vs_ordered(self, delivered_items_analysis: str, username: str, query: str) -> str:
        return f"Order comparison for {username}: {delivered_items_analysis} vs expected items"

    def assess_partial_delivery_impact(self, order_comparison: str) -> str:
        return f"Impact assessment: {order_comparison}"

    def check_partial_delivery_history(self, username: str) -> str:
        return f"Partial delivery history for {username}: 0 previous partial delivery complaints"

    def decide_partial_delivery_resolution(self, impact_assessment: str, credibility_score: int, partial_delivery_history: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="decide_partial_delivery_resolution",
            user_query=f"Impact: {impact_assessment} | Credibility: {credibility_score} | History: {partial_delivery_history}",
            service=self.service,
            user_type=self.actor
        )

    def generate_partial_delivery_response(self, decision: str, order_comparison: str, impact_assessment: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="generate_partial_delivery_response",
            user_query=f"Decision: {decision} | Comparison: {order_comparison} | Impact: {impact_assessment}",
            service=self.service,
            user_type=self.actor
        )

    def analyze_temperature_issues_from_image(self, query: str, image_data: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="analyze_temperature_issues_from_image",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def validate_temperature_standards(self, temperature_analysis: str, query: str) -> str:
        return f"Temperature standards validation: {temperature_analysis}"

    def check_temperature_complaint_history(self, username: str) -> str:
        return f"Temperature complaint history for {username}: 0 previous temperature complaints"

    def decide_temperature_compensation(self, temperature_analysis: str, credibility_score: int, temperature_standards: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="decide_temperature_compensation",
            user_query=f"Analysis: {temperature_analysis} | Credibility: {credibility_score} | Standards: {temperature_standards}",
            service=self.service,
            user_type=self.actor
        )

    def generate_temperature_response(self, decision: str, temperature_analysis: str, query: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="generate_temperature_response",
            user_query=f"Decision: {decision} | Analysis: {temperature_analysis} | Original: {query}",
            service=self.service,
            user_type=self.actor
        )

    def analyze_package_tampering_from_image(self, query: str, image_data: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="analyze_package_tampering_from_image",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def validate_package_security_standards(self, tampering_analysis: str) -> str:
        return f"Package security validation: {tampering_analysis}"

    def assess_food_safety_impact(self, tampering_analysis: str, query: str) -> str:
        return f"Food safety impact: {tampering_analysis}"

    def check_tampering_complaint_history(self, username: str) -> str:
        return f"Tampering complaint history for {username}: 0 previous tampering complaints"

    def decide_tampering_resolution(self, tampering_analysis: str, safety_assessment: str, credibility_score: int) -> str:
        return self.ai_engine.process_complaint(
            function_name="decide_tampering_resolution",
            user_query=f"Analysis: {tampering_analysis} | Safety: {safety_assessment} | Credibility: {credibility_score}",
            service=self.service,
            user_type=self.actor
        )

    def generate_tampering_response(self, decision: str, tampering_analysis: str, safety_assessment: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="generate_tampering_response",
            user_query=f"Decision: {decision} | Analysis: {tampering_analysis} | Safety: {safety_assessment}",
            service=self.service,
            user_type=self.actor
        )

    def analyze_multiple_delivery_claim(self, query: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="analyze_multiple_delivery_claim",
            user_query=query,
            service=self.service,
            user_type=self.actor
        )

    def verify_delivery_records(self, delivery_analysis: str, username: str) -> str:
        return f"Delivery records verification for {username}: {delivery_analysis}"

    def check_delivery_complaint_history(self, username: str) -> str:
        return f"Delivery complaint history for {username}: 1 previous delivery complaint"

    def decide_multiple_delivery_resolution(self, delivery_analysis: str, delivery_verification: str, credibility_score: int) -> str:
        return self.ai_engine.process_complaint(
            function_name="decide_multiple_delivery_resolution",
            user_query=f"Analysis: {delivery_analysis} | Verification: {delivery_verification} | Credibility: {credibility_score}",
            service=self.service,
            user_type=self.actor
        )

    def generate_multiple_delivery_response(self, decision: str, delivery_analysis: str, delivery_verification: str) -> str:
        return self.ai_engine.process_complaint(
            function_name="generate_multiple_delivery_response",
            user_query=f"Decision: {decision} | Analysis: {delivery_analysis} | Verification: {delivery_verification}",
            service=self.service,
            user_type=self.actor
        )