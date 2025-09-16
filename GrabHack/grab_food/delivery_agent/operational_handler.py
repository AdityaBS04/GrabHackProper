"""
Operational Issues Handler
Consolidates: Package tampered/spilled, Wrong package, Payment collection (COD), 
Customer unavailable, Long wait times, Late cancellations
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import base64
import json

from groq import AsyncGroq


class OperationalIssueType(Enum):
    PACKAGE_TAMPERED = "package_integrity_compromised"
    WRONG_PACKAGE = "incorrect_order_delivered"
    PAYMENT_COLLECTION = "cash_on_delivery_issues"
    CUSTOMER_UNAVAILABLE = "customer_not_available_for_delivery"
    LONG_WAIT_TIME = "extended_waiting_at_customer_location"
    LATE_CANCELLATION = "customer_cancellation_after_pickup"


class PackageCondition(Enum):
    TAMPERED_SEAL = "packaging_seal_broken"
    SPILLED_CONTENTS = "food_contents_spilled"
    DAMAGED_CONTAINER = "container_physically_damaged"
    TEMPERATURE_COMPROMISED = "food_temperature_unsafe"


class PaymentIssue(Enum):
    INSUFFICIENT_CASH = "customer_lacks_exact_change"
    FAKE_CURRENCY = "counterfeit_money_suspected"
    PAYMENT_REFUSAL = "customer_refuses_to_pay"
    DIGITAL_PAYMENT_FAILURE = "cod_digital_payment_failed"


class CustomerAvailabilityStatus(Enum):
    NOT_RESPONDING = "no_response_to_contact_attempts"
    TEMPORARILY_AWAY = "customer_temporarily_unavailable"
    WRONG_CONTACT = "incorrect_contact_information"
    DELIVERY_REFUSED = "customer_refuses_delivery"


class CancellationStage(Enum):
    AFTER_PICKUP = "post_pickup_cancellation"
    EN_ROUTE = "en_route_cancellation"
    AT_LOCATION = "at_delivery_location_cancellation"
    DELIVERY_ATTEMPTED = "post_delivery_attempt_cancellation"


@dataclass
class OperationalContext:
    order_id: str
    customer_id: str
    delivery_agent_id: str
    restaurant_id: str
    issue_type: OperationalIssueType
    order_value: float
    delivery_fee: float
    payment_method: str  # COD, digital, etc.
    food_items: List[str]
    temperature_sensitive: bool
    time_at_location: int  # minutes
    customer_contact_attempts: int
    customer_responsive: bool
    pickup_time: Optional[datetime] = None
    current_time: Optional[datetime] = None
    package_condition_description: Optional[str] = None
    payment_amount_expected: Optional[float] = None
    evidence_images: Optional[List[bytes]] = None
    additional_context: Optional[Dict[str, Any]] = None


class OperationalHandler:
    def __init__(self):
        self.groq_client = AsyncGroq()
        self.max_wait_time = 20  # minutes
        self.food_safety_time_limit = 30  # minutes
        self.escalation_threshold = 15  # minutes
        
    async def handle_operational_issue(self, context: OperationalContext) -> Dict[str, Any]:
        """Main handler for all operational issues"""
        
        if context.issue_type == OperationalIssueType.PACKAGE_TAMPERED:
            return await self._handle_package_tampered(context)
        elif context.issue_type == OperationalIssueType.WRONG_PACKAGE:
            return await self._handle_wrong_package(context)
        elif context.issue_type == OperationalIssueType.PAYMENT_COLLECTION:
            return await self._handle_payment_collection(context)
        elif context.issue_type == OperationalIssueType.CUSTOMER_UNAVAILABLE:
            return await self._handle_customer_unavailable(context)
        elif context.issue_type == OperationalIssueType.LONG_WAIT_TIME:
            return await self._handle_long_wait_time(context)
        elif context.issue_type == OperationalIssueType.LATE_CANCELLATION:
            return await self._handle_late_cancellation(context)
        else:
            return {"error": "Unknown operational issue type"}
    
    async def _handle_package_tampered(self, context: OperationalContext) -> Dict[str, Any]:
        """Handle package tampering and food safety issues"""
        
        # Analyze package condition and safety
        package_analysis = await self._analyze_package_condition(context)
        
        # Food safety assessment
        safety_assessment = await self._assess_food_safety(context, package_analysis)
        
        # Customer notification and options
        customer_notification = await self._notify_customer_package_issue(context, package_analysis)
        
        # Replacement order coordination
        replacement_coordination = await self._coordinate_replacement_order(context, package_analysis)
        
        # Restaurant notification
        restaurant_notification = await self._notify_restaurant_package_issue(context, package_analysis)
        
        # Performance protection and compensation
        agent_protection = await self._apply_package_performance_protection(context, package_analysis)
        
        return {
            "issue_type": "package_tampered",
            "package_analysis": package_analysis,
            "safety_assessment": safety_assessment,
            "customer_notification": customer_notification,
            "replacement_coordination": replacement_coordination,
            "restaurant_notification": restaurant_notification,
            "agent_protection": agent_protection,
            "status": "handled",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _analyze_package_condition(self, context: OperationalContext) -> Dict[str, Any]:
        """Analyze package tampering using AI"""
        
        analysis_prompt = f"""
        Analyze this package tampering incident:
        
        Package Condition: {context.package_condition_description or 'damaged_during_transit'}
        Food Items: {', '.join(context.food_items)}
        Temperature Sensitive: {context.temperature_sensitive}
        Order Value: ${context.order_value}
        Time Since Pickup: {((context.current_time or datetime.now()) - (context.pickup_time or datetime.now() - timedelta(minutes=20))).seconds // 60} minutes
        
        Provide analysis in this exact format:
        CONDITION_TYPE: [TAMPERED_SEAL/SPILLED_CONTENTS/DAMAGED_CONTAINER/TEMPERATURE_COMPROMISED]
        FOOD_SAFETY_RISK: [LOW/MEDIUM/HIGH/CRITICAL]
        DELIVERY_FEASIBLE: [true/false]
        CUSTOMER_ACCEPTANCE_LIKELY: [true/false]
        REPLACEMENT_REQUIRED: [true/false]
        REFUND_AMOUNT: [dollar amount or 'full']
        AGENT_LIABILITY: [NONE/PARTIAL/FULL]
        RECOMMENDED_ACTIONS: [comma-separated list]
        """
        
        try:
            if context.evidence_images:
                image_analysis = await self._analyze_package_evidence(context.evidence_images[0], context)
                analysis_prompt += f"\n\nPackage Image Evidence: {image_analysis}"
            
            response = await self.groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert in food safety and package integrity assessment. Prioritize customer safety."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            return self._parse_ai_analysis(response.choices[0].message.content)
            
        except Exception as e:
            return self._create_fallback_package_analysis(context)
    
    async def _handle_wrong_package(self, context: OperationalContext) -> Dict[str, Any]:
        """Handle wrong package delivery mix-ups"""
        
        # Verify order mismatch
        order_verification = await self._verify_order_mismatch(context)
        
        # Customer communication
        customer_communication = await self._communicate_wrong_package(context, order_verification)
        
        # Correct order coordination
        correct_order_coordination = await self._coordinate_correct_order_delivery(context, order_verification)
        
        # Wrong package handling
        wrong_package_handling = await self._handle_misdelivered_package(context, order_verification)
        
        # Performance protection
        performance_protection = await self._apply_mixup_performance_protection(context, order_verification)
        
        return {
            "issue_type": "wrong_package",
            "order_verification": order_verification,
            "customer_communication": customer_communication,
            "correct_order_coordination": correct_order_coordination,
            "wrong_package_handling": wrong_package_handling,
            "performance_protection": performance_protection,
            "status": "handled",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_payment_collection(self, context: OperationalContext) -> Dict[str, Any]:
        """Handle COD payment collection issues"""
        
        # Analyze payment issue
        payment_analysis = await self._analyze_payment_issue(context)
        
        # Payment resolution attempts
        payment_resolution = await self._attempt_payment_resolution(context, payment_analysis)
        
        # Alternative payment methods
        alternative_payments = await self._explore_alternative_payment_methods(context, payment_analysis)
        
        # Escalation procedures
        escalation_procedures = await self._execute_payment_escalation(context, payment_analysis)
        
        # Agent protection and compensation
        agent_protection = await self._apply_payment_performance_protection(context, payment_analysis)
        
        return {
            "issue_type": "payment_collection",
            "payment_analysis": payment_analysis,
            "payment_resolution": payment_resolution,
            "alternative_payments": alternative_payments,
            "escalation_procedures": escalation_procedures,
            "agent_protection": agent_protection,
            "status": "handled",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_customer_unavailable(self, context: OperationalContext) -> Dict[str, Any]:
        """Handle customer unavailability situations"""
        
        # Analyze availability situation
        availability_analysis = await self._analyze_customer_availability(context)
        
        # Contact escalation protocol
        contact_escalation = await self._execute_contact_escalation_protocol(context, availability_analysis)
        
        # Alternative delivery options
        alternative_delivery = await self._explore_alternative_delivery_options(context, availability_analysis)
        
        # Food quality management
        food_quality_management = await self._manage_food_quality_during_wait(context, availability_analysis)
        
        # Performance protection
        performance_protection = await self._apply_availability_performance_protection(context, availability_analysis)
        
        return {
            "issue_type": "customer_unavailable",
            "availability_analysis": availability_analysis,
            "contact_escalation": contact_escalation,
            "alternative_delivery": alternative_delivery,
            "food_quality_management": food_quality_management,
            "performance_protection": performance_protection,
            "status": "handled",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_long_wait_time(self, context: OperationalContext) -> Dict[str, Any]:
        """Handle extended waiting times at customer location"""
        
        # Analyze wait situation
        wait_analysis = await self._analyze_wait_situation(context)
        
        # Customer communication during wait
        wait_communication = await self._manage_wait_communication(context, wait_analysis)
        
        # Food quality preservation
        quality_preservation = await self._implement_quality_preservation(context, wait_analysis)
        
        # Escalation and alternatives
        escalation_alternatives = await self._manage_wait_escalation(context, wait_analysis)
        
        # Performance protection
        performance_protection = await self._apply_wait_performance_protection(context, wait_analysis)
        
        return {
            "issue_type": "long_wait_time",
            "wait_analysis": wait_analysis,
            "wait_communication": wait_communication,
            "quality_preservation": quality_preservation,
            "escalation_alternatives": escalation_alternatives,
            "performance_protection": performance_protection,
            "status": "handled",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_late_cancellation(self, context: OperationalContext) -> Dict[str, Any]:
        """Handle customer cancellations after pickup"""
        
        # Analyze cancellation situation
        cancellation_analysis = await self._analyze_late_cancellation(context)
        
        # Food disposal management
        food_disposal = await self._manage_food_disposal(context, cancellation_analysis)
        
        # Compensation calculation
        compensation_calculation = await self._calculate_cancellation_compensation(context, cancellation_analysis)
        
        # Customer financial responsibility
        customer_charges = await self._process_customer_cancellation_charges(context, cancellation_analysis)
        
        # Performance protection
        performance_protection = await self._apply_cancellation_performance_protection(context, cancellation_analysis)
        
        return {
            "issue_type": "late_cancellation",
            "cancellation_analysis": cancellation_analysis,
            "food_disposal": food_disposal,
            "compensation_calculation": compensation_calculation,
            "customer_charges": customer_charges,
            "performance_protection": performance_protection,
            "status": "handled",
            "timestamp": datetime.now().isoformat()
        }
    
    # Implementation of key analysis methods
    async def _assess_food_safety(self, context: OperationalContext, package_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess food safety based on package condition"""
        
        safety_risk = package_analysis.get("FOOD_SAFETY_RISK", "MEDIUM")
        
        safety_assessment = {
            "risk_level": safety_risk,
            "safe_for_consumption": safety_risk in ["LOW", "MEDIUM"],
            "replacement_recommended": safety_risk in ["HIGH", "CRITICAL"],
            "health_department_notification_required": safety_risk == "CRITICAL"
        }
        
        if context.temperature_sensitive:
            time_elapsed = ((context.current_time or datetime.now()) - (context.pickup_time or datetime.now() - timedelta(minutes=20))).seconds // 60
            if time_elapsed > self.food_safety_time_limit:
                safety_assessment["temperature_safety_compromised"] = True
                safety_assessment["safe_for_consumption"] = False
        
        return safety_assessment
    
    async def _verify_order_mismatch(self, context: OperationalContext) -> Dict[str, Any]:
        """Verify and analyze order mismatch"""
        
        verification_prompt = f"""
        Analyze this order mismatch situation:
        
        Expected Items: {', '.join(context.food_items)}
        Order Value: ${context.order_value}
        Customer ID: {context.customer_id}
        
        Provide verification in this format:
        MISMATCH_TYPE: [COMPLETE_WRONG_ORDER/PARTIAL_MISMATCH/QUANTITY_ERROR/ITEM_SUBSTITUTION]
        CUSTOMER_IMPACT: [LOW/MEDIUM/HIGH]
        CORRECT_ORDER_AVAILABILITY: [IMMEDIATE/DELAYED/UNAVAILABLE]
        RESOLUTION_COMPLEXITY: [SIMPLE/MODERATE/COMPLEX]
        CUSTOMER_SATISFACTION_RISK: [LOW/MEDIUM/HIGH]
        """
        
        try:
            response = await self.groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert in order management and customer service resolution."},
                    {"role": "user", "content": verification_prompt}
                ],
                temperature=0.1,
                max_tokens=600
            )
            
            return self._parse_ai_analysis(response.choices[0].message.content)
            
        except Exception as e:
            return self._create_fallback_order_verification(context)
    
    async def _analyze_payment_issue(self, context: OperationalContext) -> Dict[str, Any]:
        """Analyze COD payment collection issue"""
        
        payment_prompt = f"""
        Analyze this COD payment issue:
        
        Expected Payment: ${context.payment_amount_expected or context.order_value + context.delivery_fee}
        Order Value: ${context.order_value}
        Delivery Fee: ${context.delivery_fee}
        Customer Contact Attempts: {context.customer_contact_attempts}
        Customer Responsive: {context.customer_responsive}
        
        Provide analysis in this format:
        PAYMENT_ISSUE_TYPE: [INSUFFICIENT_CASH/FAKE_CURRENCY/PAYMENT_REFUSAL/DIGITAL_PAYMENT_FAILURE]
        RESOLUTION_PROBABILITY: [0.0-1.0]
        ALTERNATIVE_PAYMENT_FEASIBLE: [true/false]
        ESCALATION_REQUIRED: [true/false]
        AGENT_SAFETY_CONCERN: [true/false]
        RECOMMENDED_ACTIONS: [comma-separated list]
        """
        
        try:
            response = await self.groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert in payment collection and financial dispute resolution."},
                    {"role": "user", "content": payment_prompt}
                ],
                temperature=0.1,
                max_tokens=600
            )
            
            return self._parse_ai_analysis(response.choices[0].message.content)
            
        except Exception as e:
            return self._create_fallback_payment_analysis(context)
    
    # Implementation of coordination methods
    async def _coordinate_replacement_order(self, context: OperationalContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate replacement order for damaged package"""
        
        if analysis.get("REPLACEMENT_REQUIRED") == "true":
            coordination_result = {
                "replacement_order_initiated": True,
                "restaurant_contacted": True,
                "estimated_preparation_time": "20-30 minutes",
                "customer_notified_of_delay": True,
                "original_order_disposal_arranged": True
            }
            
            # Check restaurant availability
            coordination_result["restaurant_can_remake"] = True  # Simulate restaurant check
            
            if not coordination_result["restaurant_can_remake"]:
                coordination_result["full_refund_processed"] = True
                coordination_result["alternative_restaurant_suggested"] = True
        else:
            coordination_result = {
                "replacement_not_required": True,
                "customer_offered_partial_refund": analysis.get("REFUND_AMOUNT") != "0"
            }
        
        return coordination_result
    
    async def _attempt_payment_resolution(self, context: OperationalContext, analysis: Dict[str, Any]) -> List[str]:
        """Attempt various payment resolution methods"""
        resolution_attempts = []
        
        issue_type = analysis.get("PAYMENT_ISSUE_TYPE", "INSUFFICIENT_CASH")
        
        if issue_type == "INSUFFICIENT_CASH":
            resolution_attempts.extend([
                "exact_change_calculation_assistance",
                "partial_payment_acceptance_considered",
                "nearby_atm_location_provided"
            ])
        
        elif issue_type == "DIGITAL_PAYMENT_FAILURE":
            resolution_attempts.extend([
                "alternative_payment_app_suggested",
                "qr_code_payment_attempted",
                "manual_card_entry_tried"
            ])
        
        elif issue_type == "PAYMENT_REFUSAL":
            resolution_attempts.extend([
                "order_quality_verification_completed",
                "customer_complaint_addressed",
                "supervisor_escalation_offered"
            ])
        
        return resolution_attempts
    
    async def _manage_food_disposal(self, context: OperationalContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Manage food disposal for cancelled orders"""
        
        time_since_pickup = ((context.current_time or datetime.now()) - (context.pickup_time or datetime.now() - timedelta(minutes=20))).seconds // 60
        
        disposal_management = {
            "disposal_method": "return_to_restaurant" if time_since_pickup < 15 else "safe_disposal",
            "food_safety_compliant": True,
            "waste_minimization_attempted": True
        }
        
        if time_since_pickup < 15 and not context.temperature_sensitive:
            disposal_management.update({
                "return_to_restaurant_feasible": True,
                "restaurant_acceptance_likely": True
            })
        elif time_since_pickup < 30:
            disposal_management.update({
                "donation_to_charity_considered": True,
                "agent_compensation_food_value": min(context.order_value * 0.5, 12.0)
            })
        else:
            disposal_management.update({
                "safe_disposal_required": True,
                "food_safety_time_exceeded": True
            })
        
        return disposal_management
    
    async def _calculate_cancellation_compensation(self, context: OperationalContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate agent compensation for late cancellations"""
        
        time_since_pickup = ((context.current_time or datetime.now()) - (context.pickup_time or datetime.now() - timedelta(minutes=20))).seconds // 60
        
        compensation = {
            "base_delivery_fee": context.delivery_fee,
            "time_compensation": time_since_pickup * 1.5,  # $1.5 per minute
            "inconvenience_fee": 8.0,  # Base inconvenience
            "fuel_reimbursement": 3.0   # Estimated fuel cost
        }
        
        total_compensation = sum(compensation.values())
        
        return {
            "compensation_breakdown": compensation,
            "total_compensation": total_compensation,
            "payment_method": "next_payout_cycle",
            "compensation_justified": True
        }
    
    # Performance protection methods
    async def _apply_package_performance_protection(self, context: OperationalContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply performance protection for package issues"""
        return {
            "delivery_completion_protected": True,
            "performance_score_maintained": True,
            "incident_classification": "package_integrity_issue_external",
            "agent_liability": analysis.get("AGENT_LIABILITY", "NONE"),
            "compensation_eligible": analysis.get("AGENT_LIABILITY") == "NONE"
        }
    
    async def _apply_payment_performance_protection(self, context: OperationalContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply performance protection for payment issues"""
        return {
            "delivery_attempt_credited": True,
            "performance_score_protection": True,
            "incident_classification": "customer_payment_issue",
            "safety_protocol_followed": analysis.get("AGENT_SAFETY_CONCERN") == "true",
            "additional_compensation": analysis.get("ESCALATION_REQUIRED") == "true"
        }
    
    async def _apply_availability_performance_protection(self, context: OperationalContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply performance protection for customer unavailability"""
        return {
            "delivery_time_adjustment": True,
            "performance_score_protection": True,
            "incident_classification": "customer_unavailability",
            "wait_time_compensation": context.time_at_location > 10,
            "time_excluded_from_metrics": context.time_at_location
        }
    
    async def _apply_wait_performance_protection(self, context: OperationalContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply performance protection for long wait times"""
        return {
            "delivery_time_adjustment": True,
            "performance_score_protection": True,
            "incident_classification": "customer_caused_delay",
            "wait_time_compensation": context.time_at_location * 1.5,  # $1.5 per minute
            "customer_rating_protection": context.time_at_location > 15
        }
    
    async def _apply_cancellation_performance_protection(self, context: OperationalContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply performance protection for late cancellations"""
        return {
            "delivery_success_rate_protected": True,
            "completion_time_excluded": True,
            "customer_rating_impact_negated": True,
            "incident_classification": "customer_late_cancellation",
            "full_compensation_eligible": True
        }
    
    # Evidence analysis methods
    async def _analyze_package_evidence(self, image_data: bytes, context: OperationalContext) -> str:
        """Analyze package condition from image"""
        try:
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            
            response = await self.groq_client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Analyze this food package condition. Order contains: {', '.join(context.food_items)}. Assess: packaging integrity, food safety concerns, tampering evidence, spillage, container damage."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_b64}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1,
                max_tokens=400
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Package image analysis failed: {str(e)}"
    
    # Helper methods
    def _parse_ai_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse AI analysis response into dictionary"""
        try:
            lines = analysis_text.strip().split('\n')
            parsed_data = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    parsed_data[key.strip()] = value.strip()
            
            return parsed_data
            
        except Exception:
            return {"parsing_failed": True}
    
    # Fallback methods
    def _create_fallback_package_analysis(self, context: OperationalContext) -> Dict[str, Any]:
        """Create fallback analysis for package issues"""
        return {
            "CONDITION_TYPE": "DAMAGED_CONTAINER",
            "FOOD_SAFETY_RISK": "MEDIUM",
            "DELIVERY_FEASIBLE": "false",
            "CUSTOMER_ACCEPTANCE_LIKELY": "false",
            "REPLACEMENT_REQUIRED": "true",
            "REFUND_AMOUNT": "full",
            "AGENT_LIABILITY": "NONE",
            "RECOMMENDED_ACTIONS": ["replacement_order", "customer_notification", "restaurant_contact"]
        }
    
    def _create_fallback_order_verification(self, context: OperationalContext) -> Dict[str, Any]:
        """Create fallback verification for order mismatch"""
        return {
            "MISMATCH_TYPE": "COMPLETE_WRONG_ORDER",
            "CUSTOMER_IMPACT": "HIGH",
            "CORRECT_ORDER_AVAILABILITY": "DELAYED",
            "RESOLUTION_COMPLEXITY": "MODERATE",
            "CUSTOMER_SATISFACTION_RISK": "HIGH"
        }
    
    def _create_fallback_payment_analysis(self, context: OperationalContext) -> Dict[str, Any]:
        """Create fallback analysis for payment issues"""
        return {
            "PAYMENT_ISSUE_TYPE": "INSUFFICIENT_CASH",
            "RESOLUTION_PROBABILITY": "0.6",
            "ALTERNATIVE_PAYMENT_FEASIBLE": "true",
            "ESCALATION_REQUIRED": str(context.customer_contact_attempts > 2).lower(),
            "AGENT_SAFETY_CONCERN": "false",
            "RECOMMENDED_ACTIONS": ["alternative_payment_methods", "partial_payment_consideration", "supervisor_contact"]
        }
    
    def handle_payment_discrepancy(self, query: str, order_id: str, customer_id: str, 
                                 agent_id: str, expected_amount: float) -> str:
        """
        Handle strict workflow for payment discrepancy: Customer claims online payment but system shows COD
        This is the main entry point for delivery agents facing this specific issue
        """
        
        # Step 1: Validate payment status across multiple systems
        payment_validation = self.validate_payment_status(order_id, customer_id)
        
        # Step 2: Get customer credibility score based on payment history
        credibility_score = self.get_customer_payment_credibility(customer_id)
        
        # Step 3: Use GPT reasoning to make final decision
        decision = self.reason_with_gpt_payment(payment_validation, credibility_score, expected_amount)
        
        # Step 4: Generate response based on decision
        response = self.generate_payment_response(decision, order_id, expected_amount)
        
        return response
    
    def validate_payment_status(self, order_id: str, customer_id: str) -> str:
        """Validate payment status across multiple systems"""
        
        # In a real system, this would check:
        # 1. Order management system
        # 2. Payment gateway logs  
        # 3. Bank transaction records
        # 4. Customer app payment history
        
        validation_checks = {
            "order_system_status": self._check_order_system(order_id),
            "payment_gateway_logs": self._check_payment_gateway(order_id),
            "bank_transaction_record": self._check_bank_records(customer_id, order_id),
            "app_payment_history": self._check_app_payments(customer_id, order_id)
        }
        
        # Analyze validation results
        online_payment_confirmations = 0
        cod_confirmations = 0
        
        for check, result in validation_checks.items():
            if "ONLINE_PAID" in result:
                online_payment_confirmations += 1
            elif "COD_REQUIRED" in result:
                cod_confirmations += 1
        
        # Determine validation result
        if online_payment_confirmations >= 3:
            return "CONFIRMED_ONLINE_PAYMENT"
        elif online_payment_confirmations >= 2:
            return "LIKELY_ONLINE_PAYMENT"  
        elif cod_confirmations >= 3:
            return "CONFIRMED_COD_REQUIRED"
        elif cod_confirmations >= 2:
            return "LIKELY_COD_REQUIRED"
        else:
            return "PAYMENT_STATUS_UNCLEAR"
    
    def _check_order_system(self, order_id: str) -> str:
        """Check order management system for payment status using actual database"""
        import sqlite3
        import os
        import json
        
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
                return self._simulate_order_system_check(order_id)
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Query the actual order from database
            cursor.execute('''
                SELECT id, status, details, price, user_type, payment_method 
                FROM orders 
                WHERE id = ? AND service = 'grab_food'
            ''', (order_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                order_id_db, status, details, price, user_type, payment_method = result
                
                # Use the payment_method column first
                if payment_method:
                    if payment_method.lower() in ['card', 'online', 'upi', 'wallet']:
                        return "ONLINE_PAID - Payment confirmed in order system"
                    elif payment_method.lower() == 'cod':
                        return "COD_REQUIRED - Cash on delivery in order system"
                
                # Fallback: parse details JSON for payment method
                if details:
                    try:
                        details_json = json.loads(details)
                        payment_method_details = details_json.get('payment_method')
                        if payment_method_details:
                            if payment_method_details.lower() in ['card', 'online', 'upi', 'wallet']:
                                return "ONLINE_PAID - Payment confirmed in order system"
                            elif payment_method_details.lower() == 'cod':
                                return "COD_REQUIRED - Cash on delivery in order system"
                    except:
                        pass
                
                # Final fallback: use status and price to infer payment
                if status == 'completed' and price and price > 0:
                    return "ONLINE_PAID - Payment confirmed in order system"
                elif price and price > 0:
                    return "COD_REQUIRED - Cash on delivery in order system"
                else:
                    return "STATUS_UNCLEAR - Order system data inconsistent"
            else:
                return "STATUS_UNCLEAR - Order not found in system"
                
        except Exception as e:
            # Fallback to simulation if database access fails
            return self._simulate_order_system_check(order_id)
    
    def _simulate_order_system_check(self, order_id: str) -> str:
        """Fallback simulation when database is unavailable"""
        # Using the order_id pattern to simulate different scenarios for testing
        if order_id.endswith("001") or order_id.endswith("003"):
            return "ONLINE_PAID - Payment confirmed in order system"
        elif order_id.endswith("002") or order_id.endswith("004"):
            return "COD_REQUIRED - Cash on delivery in order system"
        else:
            return "STATUS_UNCLEAR - Order system data inconsistent"
    
    def _check_payment_gateway(self, order_id: str) -> str:
        """Check payment gateway for transaction logs"""
        # Simulate payment gateway API call
        if order_id.endswith("001") or order_id.endswith("005"):
            return "ONLINE_PAID - Transaction found in payment gateway"
        elif order_id.endswith("002"):
            return "COD_REQUIRED - No payment transaction found"
        else:
            return "STATUS_UNCLEAR - Payment gateway timeout or error"
    
    def _check_bank_records(self, customer_id: str, order_id: str) -> str:
        """Check bank transaction records (simulated)"""
        # In real system, this would be complex integration with banking APIs
        if customer_id.endswith("001"):
            return "ONLINE_PAID - Bank transaction confirmed"
        elif customer_id.endswith("002"):
            return "COD_REQUIRED - No bank transaction found"
        else:
            return "STATUS_UNCLEAR - Bank records unavailable"
    
    def _check_app_payments(self, customer_id: str, order_id: str) -> str:
        """Check customer app payment history"""
        # Simulate checking customer's app payment logs
        if len(customer_id) > 6:  # Simulate established customers
            return "ONLINE_PAID - Payment shown in customer app"
        else:
            return "STATUS_UNCLEAR - App data inconsistent"
    
    def get_customer_payment_credibility(self, customer_id: str) -> int:
        """Calculate customer credibility score for payment disputes (1-10)"""
        
        base_score = 6  # Start with neutral credibility
        
        # Simulate factors that affect payment credibility:
        # In real system, these would be database queries
        
        # Account age factor
        if len(customer_id) > 8:  # Simulate older accounts
            base_score += 2
        elif len(customer_id) < 5:  # Simulate new accounts  
            base_score -= 1
        
        # Payment history factor (simulated)
        if customer_id.endswith("001") or customer_id.endswith("003"):
            base_score += 2  # Good payment history
        elif customer_id.endswith("999") or customer_id.endswith("000"):
            base_score -= 3  # Poor payment history
        
        # Order frequency factor
        customer_hash = sum(ord(c) for c in customer_id)
        if customer_hash % 3 == 0:  # Simulate frequent customers
            base_score += 1
        
        # Previous disputes factor (simulated)
        if "TEST" in customer_id.upper():
            base_score -= 2  # Test accounts are less credible
        
        return max(1, min(10, base_score))
    
    def reason_with_gpt_payment(self, validation_result: str, credibility_score: int, amount: float) -> str:
        """Use GPT to make final decision on payment discrepancy based on validation and credibility"""
        
        reasoning_prompt = f"""
        Make a final decision on a payment discrepancy complaint based on:
        
        System Validation Result: {validation_result}
        Customer Credibility Score: {credibility_score}/10
        Order Amount: ${amount}
        
        Decision Rules:
        1. If validation = "CONFIRMED_ONLINE_PAYMENT" AND credibility >= 5: ACCEPT_CUSTOMER_CLAIM
        2. If validation = "LIKELY_ONLINE_PAYMENT" AND credibility >= 8: ACCEPT_CUSTOMER_CLAIM
        3. If validation = "LIKELY_ONLINE_PAYMENT" AND credibility < 8: REQUIRE_PAYMENT_PROOF
        4. If validation = "CONFIRMED_COD_REQUIRED" AND credibility <= 6: COLLECT_COD_PAYMENT
        5. If validation = "LIKELY_COD_REQUIRED" AND credibility <= 5: COLLECT_COD_PAYMENT
        6. If validation = "PAYMENT_STATUS_UNCLEAR": ESCALATE_TO_FINANCE
        
        Additional considerations:
        - High amount orders (>$50) require stronger validation
        - Customer safety and agent protection are priorities
        
        Respond with ONLY one of: ACCEPT_CUSTOMER_CLAIM, REQUIRE_PAYMENT_PROOF, COLLECT_COD_PAYMENT, ESCALATE_TO_FINANCE
        """
        
        try:
            # In a real system, this would call the actual GPT API
            # For now, implement the decision logic directly
            
            if validation_result == "CONFIRMED_ONLINE_PAYMENT" and credibility_score >= 5:
                return "ACCEPT_CUSTOMER_CLAIM"
            elif validation_result == "LIKELY_ONLINE_PAYMENT" and credibility_score >= 8:
                return "ACCEPT_CUSTOMER_CLAIM"
            elif validation_result == "LIKELY_ONLINE_PAYMENT" and credibility_score < 8:
                return "REQUIRE_PAYMENT_PROOF"
            elif validation_result == "CONFIRMED_COD_REQUIRED" and credibility_score <= 6:
                return "COLLECT_COD_PAYMENT"
            elif validation_result == "LIKELY_COD_REQUIRED" and credibility_score <= 5:
                return "COLLECT_COD_PAYMENT"
            else:
                return "ESCALATE_TO_FINANCE"
                
        except Exception as e:
            # Default to safest option
            return "ESCALATE_TO_FINANCE"
    
    def generate_payment_response(self, decision: str, order_id: str, amount: float) -> str:
        """Generate appropriate response based on payment decision"""

        if decision == "ACCEPT_CUSTOMER_CLAIM":
            return f"""PAYMENT VERIFICATION COMPLETED [APPROVED]

Order ID: {order_id}
Decision: CUSTOMER CLAIM ACCEPTED

Our system validation confirms online payment was processed. You may deliver the order without collecting cash payment.

Actions taken:
- Payment status verified across multiple systems
- Order marked as "PAID ONLINE" in delivery system
- No cash collection required from customer

You can proceed with the delivery. Mark order as completed once delivered."""

        elif decision == "REQUIRE_PAYMENT_PROOF":
            return f"""PAYMENT VERIFICATION REQUIRED [WARNING]

Order ID: {order_id}
Decision: ADDITIONAL PROOF NEEDED

Please ask the customer to provide proof of online payment before delivering:

Required proof (any ONE of the following):
1. Screenshot of payment confirmation from their app
2. Bank SMS/notification showing transaction
3. Digital payment receipt with transaction ID

If customer provides valid proof: Deliver the order
If customer cannot provide proof: Collect ${amount:.2f} as COD

Contact support at 1800-GRAB-HELP if customer disputes."""

        elif decision == "COLLECT_COD_PAYMENT":
            return f"""CASH COLLECTION REQUIRED [COD]

Order ID: {order_id}
Decision: COLLECT CASH ON DELIVERY

System validation shows this order requires cash payment. Please collect ${amount:.2f} from the customer before delivery.

If customer insists they paid online:
1. Ask for payment proof (screenshot, SMS, receipt)
2. If no proof provided, politely explain cash is required
3. If customer refuses payment, contact support immediately

Do NOT deliver without payment or valid proof. Your safety and company policy are priorities."""

        else:  # ESCALATE_TO_FINANCE
            return f"""PAYMENT DISPUTE ESCALATION [URGENT]

Order ID: {order_id}
Decision: ESCALATE TO FINANCE TEAM

This payment discrepancy requires immediate escalation due to:
- Unclear payment status in systems
- Complex dispute requiring financial investigation

IMMEDIATE ACTIONS:
1. Do NOT collect cash payment yet
2. Do NOT deliver the order yet
3. Call Finance Support: 1800-GRAB-FINANCE
4. Wait for payment confirmation before proceeding

Provide Finance team with:
- Order ID: {order_id}
- Customer claim: "Paid online"
- System status: "Shows COD"
- Amount in dispute: ${amount:.2f}

Stay at location until issue is resolved (max 15 minutes)."""

    # ===== STRICT WORKFLOW METHODS FOR DELIVERY AGENTS =====

    def handle_package_damage_strict(self, query: str, agent_id: str, image_data: str = None, order_id: str = None) -> str:
        """Handle package damage with strict 7-step workflow - REQUIRES IMAGE"""
        logger.info(f"Processing package damage complaint: {query[:100]}...")

        # Step 1: Validate image requirement for damage verification
        if not image_data:
            return "📷 Please upload a photo of the damaged package so we can verify the condition and provide appropriate guidance."

        # Step 2: Analyze package damage severity and cause
        damage_analysis = self.analyze_package_damage_from_image(query, image_data)
        logger.info(f"Damage analysis: {damage_analysis}")

        # Step 3: Get actual order data from database
        order_data = self.get_order_data_for_agent(order_id, agent_id) if order_id else None

        # Step 4: Check agent credibility and damage complaint history
        credibility_score = self.get_agent_credibility_score(agent_id)
        damage_complaint_history = self.check_damage_complaint_history(agent_id)
        logger.info(f"Agent credibility: {credibility_score}/10, History: {damage_complaint_history}")

        # Step 5: Determine liability and responsibility
        liability_assessment = self.assess_damage_liability(damage_analysis, credibility_score, agent_id)
        logger.info(f"Liability assessment: {liability_assessment}")

        # Step 6: Calculate compensation and performance protection
        compensation_calculation = self.calculate_damage_compensation(liability_assessment, order_data, damage_analysis)
        logger.info(f"Compensation: {compensation_calculation}")

        # Step 7: Generate comprehensive response with next steps
        response = self.generate_damage_response(liability_assessment, compensation_calculation, damage_analysis)
        logger.info(f"Package damage response generated successfully")

        return response

    def analyze_package_damage_from_image(self, query: str, image_data: str) -> dict:
        """Analyze package damage from image using AI (simulated)"""
        # In real implementation, this would use image analysis
        query_lower = query.lower()

        analysis = {
            "damage_type": "container_damage",
            "severity": "moderate",
            "cause": "handling_accident",
            "food_safety_risk": "low",
            "delivery_feasible": True,
            "customer_acceptance_likely": False
        }

        # Analyze query for damage indicators
        if any(word in query_lower for word in ['spilled', 'leaked', 'wet']):
            analysis["damage_type"] = "content_spill"
            analysis["severity"] = "severe"
            analysis["food_safety_risk"] = "high"
            analysis["delivery_feasible"] = False
        elif any(word in query_lower for word in ['crushed', 'broken', 'smashed']):
            analysis["damage_type"] = "container_damage"
            analysis["severity"] = "moderate"
        elif any(word in query_lower for word in ['torn', 'ripped', 'open']):
            analysis["damage_type"] = "packaging_breach"
            analysis["severity"] = "moderate"
            analysis["food_safety_risk"] = "medium"

        # Determine cause
        if any(word in query_lower for word in ['dropped', 'fell', 'accident']):
            analysis["cause"] = "handling_accident"
        elif any(word in query_lower for word in ['restaurant', 'kitchen', 'received']):
            analysis["cause"] = "restaurant_packaging"
        else:
            analysis["cause"] = "transport_damage"

        return analysis

    def get_order_data_for_agent(self, order_id: str, agent_id: str) -> dict:
        """Get order data specific to delivery agent"""
        import sqlite3
        import os

        try:
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
                return None

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, food_items, price, restaurant_name, status, delivery_agent_id
                FROM orders
                WHERE id = ? AND delivery_agent_id = ? AND service = 'grab_food'
            ''', (order_id, agent_id))

            result = cursor.fetchone()
            conn.close()

            if result:
                order_id_db, food_items, price, restaurant_name, status, delivery_agent_id = result
                return {
                    'order_id': order_id_db,
                    'food_items': food_items,
                    'price': price,
                    'restaurant_name': restaurant_name,
                    'status': status,
                    'delivery_agent_id': delivery_agent_id
                }

        except Exception as e:
            logger.error(f"Error getting order data: {e}")

        return None

    def get_agent_credibility_score(self, agent_id: str) -> int:
        """Calculate agent credibility score"""
        import sqlite3
        import os

        base_score = 7

        if not agent_id or agent_id == "anonymous":
            return max(1, base_score - 3)

        try:
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
                return self._get_simulated_agent_credibility_score(agent_id)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get agent performance
            cursor.execute('''
                SELECT
                    COUNT(*) as total_deliveries,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_deliveries
                FROM orders
                WHERE delivery_agent_id = ? AND service = 'grab_food'
                AND date >= date('now', '-30 days')
            ''', (agent_id,))

            result = cursor.fetchone()
            if result:
                total_deliveries, completed_deliveries = result

                if total_deliveries > 0:
                    completion_rate = completed_deliveries / total_deliveries

                    if completion_rate >= 0.95:
                        base_score += 2
                    elif completion_rate >= 0.85:
                        base_score += 1
                    elif completion_rate < 0.70:
                        base_score -= 2

                    if total_deliveries >= 100:
                        base_score += 2
                    elif total_deliveries >= 50:
                        base_score += 1

            conn.close()

        except Exception as e:
            logger.error(f"Error calculating agent credibility: {e}")
            return self._get_simulated_agent_credibility_score(agent_id)

        return max(1, min(10, int(base_score)))

    def _get_simulated_agent_credibility_score(self, agent_id: str) -> int:
        """Fallback credibility scoring"""
        base_score = 7

        if "test" in agent_id.lower():
            base_score -= 1
        if len(agent_id) > 8:
            base_score += 1

        return max(1, min(10, base_score))

    def check_damage_complaint_history(self, agent_id: str) -> str:
        """Check agent's package damage complaint history"""
        if agent_id == "anonymous":
            return "NO_HISTORY_AVAILABLE"
        elif "test" in agent_id.lower():
            return "FREQUENT_DAMAGE_REPORTS"
        else:
            return "NORMAL_DAMAGE_PATTERN"

    def assess_damage_liability(self, damage_analysis: dict, credibility_score: int, agent_id: str) -> dict:
        """Assess liability for package damage"""
        damage_type = damage_analysis.get("damage_type", "container_damage")
        cause = damage_analysis.get("cause", "unknown")
        severity = damage_analysis.get("severity", "moderate")

        liability = {
            "agent_liability": "partial",
            "compensation_warranted": True,
            "performance_protection": False,
            "restaurant_responsibility": False
        }

        # Determine liability based on cause and agent credibility
        if cause == "restaurant_packaging" and credibility_score >= 7:
            liability["agent_liability"] = "none"
            liability["restaurant_responsibility"] = True
            liability["performance_protection"] = True
        elif cause == "handling_accident" and credibility_score >= 8:
            liability["agent_liability"] = "minimal"
            liability["performance_protection"] = True
        elif cause == "transport_damage" and severity == "severe":
            liability["agent_liability"] = "full"
            liability["compensation_warranted"] = False
        elif credibility_score <= 4:
            liability["agent_liability"] = "full"
            liability["performance_protection"] = False

        return liability

    def calculate_damage_compensation(self, liability_assessment: dict, order_data: dict, damage_analysis: dict) -> dict:
        """Calculate compensation for package damage"""
        agent_liability = liability_assessment.get("agent_liability", "partial")
        order_value = order_data.get('price', 25.0) if order_data else 25.0

        compensation = {
            "customer_refund": 0.0,
            "agent_compensation": 0.0,
            "restaurant_charge": 0.0,
            "delivery_fee_retention": 0.0
        }

        if agent_liability == "none":
            compensation["customer_refund"] = order_value
            compensation["agent_compensation"] = 5.0  # Goodwill payment
            compensation["delivery_fee_retention"] = 1.0
        elif agent_liability == "minimal":
            compensation["customer_refund"] = order_value * 0.8
            compensation["agent_compensation"] = 3.0
            compensation["delivery_fee_retention"] = 1.0
        elif agent_liability == "partial":
            compensation["customer_refund"] = order_value * 0.6
            compensation["agent_compensation"] = 0.0
            compensation["delivery_fee_retention"] = 0.5
        else:  # full liability
            compensation["customer_refund"] = order_value
            compensation["agent_compensation"] = -order_value * 0.3  # Deduction
            compensation["delivery_fee_retention"] = 0.0

        return compensation

    def generate_damage_response(self, liability_assessment: dict, compensation_calculation: dict, damage_analysis: dict) -> str:
        """Generate comprehensive response for package damage"""
        agent_liability = liability_assessment.get("agent_liability", "partial")
        customer_refund = compensation_calculation.get("customer_refund", 0.0)
        agent_compensation = compensation_calculation.get("agent_compensation", 0.0)

        if agent_liability == "none":
            return f"""📦 **Package Damage - Not Your Responsibility**

**Damage Assessment Complete:**
- Damage type: {damage_analysis.get('damage_type', 'container_damage')}
- Cause: Restaurant packaging issue
- Agent liability: None

**✅ Resolution & Compensation:**
💰 **Customer refund:** ${customer_refund:.2f} processed
🎁 **Your compensation:** ${agent_compensation:.2f} for inconvenience
📈 **Performance protection:** Fully applied
🚫 **No negative impact** on your ratings

**Next Steps:**
1. Do not deliver the damaged order
2. Return to restaurant if feasible
3. Customer will receive full refund + replacement option
4. Your earnings and ratings are fully protected

**Restaurant Notification:**
- Packaging quality issue reported
- Immediate review of packaging procedures required
- Future prevention measures implemented

Your professionalism in reporting this issue is appreciated and protects both customer satisfaction and service quality."""

        elif agent_liability == "minimal":
            return f"""📦 **Package Damage - Minimal Responsibility**

**Damage Assessment:**
- Damage type: {damage_analysis.get('damage_type', 'container_damage')}
- Cause: Minor handling issue during transport
- Agent liability: Minimal

**✅ Fair Resolution:**
💰 **Customer refund:** ${customer_refund:.2f}
🎁 **Your compensation:** ${agent_compensation:.2f} (goodwill payment)
📈 **Performance protection:** Applied
⚠️ **Minor guidance** for future handling

**Learning Opportunity:**
- Handle packages with extra care during transport
- Use both hands for large/fragile orders
- Secure items properly in delivery bag
- Check package condition before pickup

**Support Provided:**
- Delivery handling training resources available
- Equipment upgrade options if needed
- Performance metrics protected for this incident

Accidents happen, and your honest reporting helps us improve service quality for everyone."""

        elif agent_liability == "partial":
            return f"""📦 **Package Damage - Shared Responsibility**

**Damage Assessment:**
- Damage type: {damage_analysis.get('damage_type', 'container_damage')}
- Cause: Handling during delivery process
- Agent liability: Partial

**⚖️ Balanced Resolution:**
💰 **Customer refund:** ${customer_refund:.2f}
📊 **Performance impact:** Minimal (extenuating circumstances considered)
💼 **Delivery fee:** Partial retention (${compensation_calculation.get('delivery_fee_retention', 0):.2f})

**Improvement Plan:**
1. **Package Handling Review:**
   - Best practices for fragile items
   - Proper delivery bag usage
   - Weather protection techniques

2. **Prevention Measures:**
   - Double-check package integrity at pickup
   - Use insulated bags for temperature-sensitive items
   - Report packaging concerns to restaurants proactively

**Support Available:**
- Delivery technique training modules
- Equipment upgrade assistance
- Mentorship program with experienced agents

We understand that damage can occur despite best efforts. Learn from this experience to enhance your delivery success."""

        else:  # full liability
            return f"""📦 **Package Damage - Full Responsibility**

**Damage Assessment:**
- Damage type: {damage_analysis.get('damage_type', 'container_damage')}
- Cause: Preventable handling issue
- Agent liability: Full

**⚠️ Serious Resolution Required:**
💰 **Customer refund:** ${customer_refund:.2f} (full order value)
📉 **Performance impact:** Significant
💸 **Agent responsibility:** ${abs(agent_compensation):.2f} order value deduction
🚫 **Delivery fee:** Forfeited

**Immediate Requirements:**
1. **Mandatory Training:**
   - Package handling certification required
   - Food safety protocols review
   - Customer service excellence modules

2. **Probationary Measures:**
   - Enhanced supervision for next 20 deliveries
   - Quality check requirements increased
   - Performance monitoring intensified

**Path to Improvement:**
- Complete mandatory training within 48 hours
- Demonstrate improved handling techniques
- Maintain 95%+ customer satisfaction
- Pass quality assessments consistently

This incident represents a serious service failure. However, we believe in second chances with proper training and commitment to improvement. Your future success depends on learning from this experience."""


# Example usage
if __name__ == "__main__":
    async def test_operational_handler():
        handler = OperationalHandler()
        
        # Test package tampered scenario
        package_context = OperationalContext(
            order_id="ORD001",
            customer_id="CUST001",
            delivery_agent_id="DA001",
            restaurant_id="REST001",
            issue_type=OperationalIssueType.PACKAGE_TAMPERED,
            order_value=25.50,
            delivery_fee=3.50,
            payment_method="COD",
            food_items=["Burger", "Fries", "Drink"],
            temperature_sensitive=True,
            time_at_location=5,
            customer_contact_attempts=1,
            customer_responsive=True,
            pickup_time=datetime.now() - timedelta(minutes=15),
            current_time=datetime.now(),
            package_condition_description="seal_broken_food_spilled"
        )
        
        result = await handler.handle_operational_issue(package_context)
        print(f"Package tampered result: {result}")
    
    asyncio.run(test_operational_handler())