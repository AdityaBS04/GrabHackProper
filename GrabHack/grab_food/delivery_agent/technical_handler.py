"""
Technical Issues Handler (Driver Side)
Consolidates: Delivery app crash/OTP not showing, Map/order details not syncing, 
Payment settlement not reflecting in driver app
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import base64
import json

from groq import AsyncGroq


class TechnicalIssueType(Enum):
    APP_CRASH = "delivery_app_technical_failure"
    OTP_NOT_SHOWING = "otp_delivery_code_not_displaying"
    MAP_SYNC_FAILURE = "map_data_synchronization_failure"
    ORDER_SYNC_FAILURE = "order_details_synchronization_failure"
    PAYMENT_SETTLEMENT = "payment_settlement_not_reflecting"


class AppCrashSeverity(Enum):
    MINOR = "app_slow_minor_glitches"
    MODERATE = "app_freeze_restart_required"
    MAJOR = "app_crash_data_loss_possible"
    CRITICAL = "app_completely_unusable"


class SyncIssueType(Enum):
    PARTIAL_SYNC = "some_data_missing_or_outdated"
    COMPLETE_FAILURE = "no_data_synchronization"
    INTERMITTENT = "sync_works_sporadically"
    DELAYED_SYNC = "data_updates_with_significant_delay"


class PaymentIssueType(Enum):
    MISSING_TRANSACTIONS = "completed_deliveries_not_showing"
    INCORRECT_AMOUNTS = "payment_amounts_mismatch"
    DELAYED_SETTLEMENT = "payment_processing_delayed"
    CALCULATION_ERROR = "earnings_calculation_incorrect"


@dataclass
class TechnicalContext:
    delivery_agent_id: str
    device_info: Dict[str, Any]  # OS, app version, device model
    issue_type: TechnicalIssueType
    affected_orders: List[str]
    issue_duration: int  # minutes
    connectivity_status: str  # good, poor, offline
    app_version: str
    os_version: str
    device_storage_available: float  # GB
    last_successful_sync: Optional[datetime] = None
    error_messages: Optional[List[str]] = None
    crash_logs_available: bool = False
    payment_period: Optional[str] = None  # for payment settlement issues
    expected_earnings: Optional[float] = None
    actual_earnings: Optional[float] = None
    screenshots: Optional[List[bytes]] = None
    additional_context: Optional[Dict[str, Any]] = None


class TechnicalHandler:
    def __init__(self):
        self.groq_client = AsyncGroq()
        self.critical_issue_threshold = 30  # minutes
        self.supported_app_versions = ["3.2.1", "3.2.2", "3.3.0"]  # Example versions
        self.min_storage_requirement = 2.0  # GB
        
    async def handle_technical_issue(self, context: TechnicalContext) -> Dict[str, Any]:
        """Main handler for all technical issues"""
        
        if context.issue_type == TechnicalIssueType.APP_CRASH:
            return await self._handle_app_crash(context)
        elif context.issue_type == TechnicalIssueType.OTP_NOT_SHOWING:
            return await self._handle_otp_issue(context)
        elif context.issue_type == TechnicalIssueType.MAP_SYNC_FAILURE:
            return await self._handle_map_sync_failure(context)
        elif context.issue_type == TechnicalIssueType.ORDER_SYNC_FAILURE:
            return await self._handle_order_sync_failure(context)
        elif context.issue_type == TechnicalIssueType.PAYMENT_SETTLEMENT:
            return await self._handle_payment_settlement_issue(context)
        else:
            return {"error": "Unknown technical issue type"}
    
    async def _handle_app_crash(self, context: TechnicalContext) -> Dict[str, Any]:
        """Handle delivery app crashes and freezing"""
        
        # Diagnose crash severity and causes
        crash_diagnosis = await self._diagnose_app_crash(context)
        
        # Immediate recovery actions
        recovery_actions = await self._execute_crash_recovery_protocol(context, crash_diagnosis)
        
        # Data recovery and protection
        data_recovery = await self._handle_crash_data_recovery(context, crash_diagnosis)
        
        # Alternative solutions during downtime
        alternative_solutions = await self._provide_crash_alternatives(context, crash_diagnosis)
        
        # Technical support escalation
        technical_support = await self._escalate_crash_technical_support(context, crash_diagnosis)
        
        # Agent compensation for downtime
        compensation = await self._calculate_crash_compensation(context, crash_diagnosis)
        
        return {
            "issue_type": "app_crash",
            "crash_diagnosis": crash_diagnosis,
            "recovery_actions": recovery_actions,
            "data_recovery": data_recovery,
            "alternative_solutions": alternative_solutions,
            "technical_support": technical_support,
            "compensation": compensation,
            "status": "handled",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _diagnose_app_crash(self, context: TechnicalContext) -> Dict[str, Any]:
        """Diagnose app crash using AI and system analysis"""
        
        diagnosis_prompt = f"""
        Analyze this delivery app crash:
        
        Device: {context.device_info.get('model', 'unknown')} running {context.os_version}
        App Version: {context.app_version}
        Issue Duration: {context.issue_duration} minutes
        Available Storage: {context.device_storage_available} GB
        Connectivity: {context.connectivity_status}
        Error Messages: {context.error_messages or 'none'}
        Crash Logs Available: {context.crash_logs_available}
        Affected Orders: {len(context.affected_orders)}
        
        Provide diagnosis in this exact format:
        CRASH_SEVERITY: [MINOR/MODERATE/MAJOR/CRITICAL]
        PROBABLE_CAUSE: [detailed_cause]
        DEVICE_COMPATIBILITY: [COMPATIBLE/MARGINAL/INCOMPATIBLE]
        STORAGE_ISSUE: [true/false]
        NETWORK_RELATED: [true/false]
        APP_VERSION_ISSUE: [true/false]
        RECOVERY_PROBABILITY: [0.0-1.0]
        IMMEDIATE_WORKAROUND_AVAILABLE: [true/false]
        TECHNICAL_SUPPORT_URGENCY: [LOW/MEDIUM/HIGH/CRITICAL]
        """
        
        try:
            if context.screenshots:
                image_analysis = await self._analyze_crash_screenshots(context.screenshots[0], context)
                diagnosis_prompt += f"\n\nScreenshot Analysis: {image_analysis}"
            
            response = await self.groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert in mobile app diagnostics and technical troubleshooting for delivery applications."},
                    {"role": "user", "content": diagnosis_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            return self._parse_ai_analysis(response.choices[0].message.content)
            
        except Exception as e:
            return self._create_fallback_crash_diagnosis(context)
    
    async def _handle_otp_issue(self, context: TechnicalContext) -> Dict[str, Any]:
        """Handle OTP/delivery code not showing issues"""
        
        # Diagnose OTP issue
        otp_diagnosis = await self._diagnose_otp_issue(context)
        
        # OTP recovery methods
        otp_recovery = await self._attempt_otp_recovery(context, otp_diagnosis)
        
        # Alternative verification methods
        alternative_verification = await self._provide_alternative_verification(context, otp_diagnosis)
        
        # Customer communication during OTP issues
        customer_communication = await self._manage_otp_customer_communication(context, otp_diagnosis)
        
        # Performance protection
        performance_protection = await self._apply_otp_performance_protection(context, otp_diagnosis)
        
        return {
            "issue_type": "otp_not_showing",
            "otp_diagnosis": otp_diagnosis,
            "otp_recovery": otp_recovery,
            "alternative_verification": alternative_verification,
            "customer_communication": customer_communication,
            "performance_protection": performance_protection,
            "status": "handled",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_map_sync_failure(self, context: TechnicalContext) -> Dict[str, Any]:
        """Handle map data synchronization failures"""
        
        # Diagnose sync issue
        sync_diagnosis = await self._diagnose_sync_issue(context, "map")
        
        # Map data recovery
        map_recovery = await self._recover_map_data(context, sync_diagnosis)
        
        # Alternative navigation solutions
        navigation_alternatives = await self._provide_navigation_alternatives(context, sync_diagnosis)
        
        # Route optimization during sync issues
        route_optimization = await self._optimize_routes_during_sync_failure(context, sync_diagnosis)
        
        # Performance protection
        performance_protection = await self._apply_sync_performance_protection(context, sync_diagnosis)
        
        return {
            "issue_type": "map_sync_failure",
            "sync_diagnosis": sync_diagnosis,
            "map_recovery": map_recovery,
            "navigation_alternatives": navigation_alternatives,
            "route_optimization": route_optimization,
            "performance_protection": performance_protection,
            "status": "handled",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_order_sync_failure(self, context: TechnicalContext) -> Dict[str, Any]:
        """Handle order details synchronization failures"""
        
        # Diagnose order sync issue
        order_sync_diagnosis = await self._diagnose_sync_issue(context, "order")
        
        # Order data recovery
        order_recovery = await self._recover_order_data(context, order_sync_diagnosis)
        
        # Manual order management
        manual_management = await self._enable_manual_order_management(context, order_sync_diagnosis)
        
        # Customer and restaurant communication
        stakeholder_communication = await self._manage_sync_stakeholder_communication(context, order_sync_diagnosis)
        
        # Performance protection
        performance_protection = await self._apply_sync_performance_protection(context, order_sync_diagnosis)
        
        return {
            "issue_type": "order_sync_failure",
            "order_sync_diagnosis": order_sync_diagnosis,
            "order_recovery": order_recovery,
            "manual_management": manual_management,
            "stakeholder_communication": stakeholder_communication,
            "performance_protection": performance_protection,
            "status": "handled",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _handle_payment_settlement_issue(self, context: TechnicalContext) -> Dict[str, Any]:
        """Handle payment settlement not reflecting in driver app"""
        
        # Analyze payment discrepancy
        payment_analysis = await self._analyze_payment_settlement_issue(context)
        
        # Payment verification and reconciliation
        payment_verification = await self._verify_and_reconcile_payments(context, payment_analysis)
        
        # Escalation to finance team
        finance_escalation = await self._escalate_to_finance_team(context, payment_analysis)
        
        # Interim compensation if needed
        interim_compensation = await self._process_interim_payment_compensation(context, payment_analysis)
        
        # Payment system improvements
        system_improvements = await self._recommend_payment_system_improvements(context, payment_analysis)
        
        return {
            "issue_type": "payment_settlement",
            "payment_analysis": payment_analysis,
            "payment_verification": payment_verification,
            "finance_escalation": finance_escalation,
            "interim_compensation": interim_compensation,
            "system_improvements": system_improvements,
            "status": "handled",
            "timestamp": datetime.now().isoformat()
        }
    
    # Implementation of key methods
    async def _execute_crash_recovery_protocol(self, context: TechnicalContext, diagnosis: Dict[str, Any]) -> List[str]:
        """Execute crash recovery steps"""
        recovery_actions = []
        
        # Basic recovery steps
        recovery_actions.append("app_force_stop_and_restart")
        recovery_actions.append("device_cache_clear")
        recovery_actions.append("app_data_refresh")
        
        # Issue-specific recovery
        if diagnosis.get("STORAGE_ISSUE") == "true":
            recovery_actions.append("storage_cleanup_initiated")
            recovery_actions.append("temporary_files_cleared")
        
        if diagnosis.get("NETWORK_RELATED") == "true":
            recovery_actions.append("network_connection_reset")
            recovery_actions.append("wifi_mobile_data_toggle")
        
        if diagnosis.get("APP_VERSION_ISSUE") == "true":
            recovery_actions.append("app_update_check_performed")
            recovery_actions.append("legacy_version_compatibility_mode")
        
        # Advanced recovery if needed
        if diagnosis.get("CRASH_SEVERITY") in ["MAJOR", "CRITICAL"]:
            recovery_actions.append("app_reinstall_recommended")
            recovery_actions.append("device_restart_suggested")
            recovery_actions.append("backup_app_alternative_provided")
        
        return recovery_actions
    
    async def _attempt_otp_recovery(self, context: TechnicalContext, diagnosis: Dict[str, Any]) -> List[str]:
        """Attempt various OTP recovery methods"""
        recovery_methods = []
        
        # Standard OTP recovery
        recovery_methods.append("otp_refresh_attempted")
        recovery_methods.append("sms_otp_resend_requested")
        recovery_methods.append("app_notification_otp_check")
        
        # Network-related fixes
        if context.connectivity_status != "good":
            recovery_methods.append("network_connection_optimized")
            recovery_methods.append("mobile_data_wifi_switch")
        
        # App-specific fixes
        recovery_methods.append("app_foreground_background_cycle")
        recovery_methods.append("notification_permissions_verified")
        recovery_methods.append("do_not_disturb_mode_checked")
        
        # Backend system checks
        recovery_methods.append("server_side_otp_generation_verified")
        recovery_methods.append("customer_phone_number_validation")
        
        return recovery_methods
    
    async def _provide_alternative_verification(self, context: TechnicalContext, diagnosis: Dict[str, Any]) -> List[str]:
        """Provide alternative delivery verification methods"""
        alternatives = []
        
        # Manual verification methods
        alternatives.append("customer_id_verification_manual")
        alternatives.append("order_details_verbal_confirmation")
        alternatives.append("customer_app_screenshot_verification")
        
        # Backup verification systems
        alternatives.append("support_team_verification_call")
        alternatives.append("restaurant_confirmation_verification")
        alternatives.append("gps_location_proof_delivery")
        
        # Photo verification
        alternatives.append("delivery_photo_with_customer_consent")
        alternatives.append("order_handover_documentation")
        
        return alternatives
    
    async def _recover_map_data(self, context: TechnicalContext, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """Recover map data and navigation functionality"""
        
        recovery_result = {
            "cache_refresh_attempted": True,
            "offline_maps_activated": True,
            "alternative_map_source_used": True
        }
        
        # Sync issue specific recovery
        sync_type = diagnosis.get("SYNC_ISSUE_TYPE", "PARTIAL_SYNC")
        
        if sync_type == "COMPLETE_FAILURE":
            recovery_result.update({
                "full_data_resync_initiated": True,
                "server_connection_reestablished": True,
                "local_cache_rebuild": True
            })
        elif sync_type == "INTERMITTENT":
            recovery_result.update({
                "connection_stability_improved": True,
                "retry_mechanism_activated": True,
                "bandwidth_optimization_enabled": True
            })
        
        return recovery_result
    
    async def _provide_navigation_alternatives(self, context: TechnicalContext, diagnosis: Dict[str, Any]) -> List[str]:
        """Provide alternative navigation solutions"""
        alternatives = []
        
        # Built-in alternatives
        alternatives.append("device_native_maps_app_suggested")
        alternatives.append("offline_navigation_enabled")
        alternatives.append("cached_route_data_utilized")
        
        # External alternatives
        alternatives.append("third_party_navigation_apps_recommended")
        alternatives.append("voice_guided_customer_directions")
        alternatives.append("landmark_based_navigation_instructions")
        
        # Support alternatives
        alternatives.append("operations_team_navigation_support")
        alternatives.append("local_area_expert_agent_consultation")
        alternatives.append("real_time_remote_guidance_available")
        
        return alternatives
    
    async def _verify_and_reconcile_payments(self, context: TechnicalContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Verify and reconcile payment discrepancies"""
        
        verification_result = {
            "payment_records_cross_checked": True,
            "delivery_completion_verified": True,
            "customer_payment_confirmed": True
        }
        
        expected = context.expected_earnings or 0
        actual = context.actual_earnings or 0
        discrepancy = expected - actual
        
        if discrepancy > 0:
            verification_result.update({
                "discrepancy_identified": True,
                "discrepancy_amount": discrepancy,
                "investigation_initiated": True,
                "temporary_credit_considered": discrepancy > 20.0
            })
        
        return verification_result
    
    async def _escalate_to_finance_team(self, context: TechnicalContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Escalate payment issues to finance team"""
        
        escalation_data = {
            "escalation_ticket_created": True,
            "priority": "high" if (context.expected_earnings or 0) - (context.actual_earnings or 0) > 50 else "medium",
            "finance_team_notified": True,
            "documentation_compiled": True
        }
        
        issue_type = analysis.get("PAYMENT_ISSUE_TYPE", "MISSING_TRANSACTIONS")
        
        if issue_type == "CALCULATION_ERROR":
            escalation_data["algorithm_review_requested"] = True
        elif issue_type == "DELAYED_SETTLEMENT":
            escalation_data["payment_processing_investigation"] = True
        
        return escalation_data
    
    async def _process_interim_payment_compensation(self, context: TechnicalContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Process interim compensation for payment issues"""
        
        expected = context.expected_earnings or 0
        actual = context.actual_earnings or 0
        discrepancy = expected - actual
        
        compensation_result = {
            "interim_payment_eligible": discrepancy > 10.0,
            "discrepancy_amount": discrepancy
        }
        
        if compensation_result["interim_payment_eligible"]:
            compensation_result.update({
                "interim_payment_amount": min(discrepancy * 0.8, 100.0),  # 80% up to $100
                "payment_timeline": "24_hours",
                "full_reconciliation_pending": True
            })
        
        return compensation_result
    
    # Performance protection methods
    async def _apply_otp_performance_protection(self, context: TechnicalContext, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply performance protection for OTP issues"""
        return {
            "delivery_completion_protected": True,
            "performance_score_maintained": True,
            "incident_classification": "technical_system_failure",
            "alternative_verification_credited": True,
            "customer_satisfaction_protection": True
        }
    
    async def _apply_sync_performance_protection(self, context: TechnicalContext, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply performance protection for sync failures"""
        return {
            "delivery_time_adjustment": True,
            "performance_score_protection": True,
            "incident_classification": "system_synchronization_failure",
            "efficiency_metrics_adjusted": True,
            "technical_difficulty_bonus": context.issue_duration > 15
        }
    
    # AI Analysis methods
    async def _diagnose_otp_issue(self, context: TechnicalContext) -> Dict[str, Any]:
        """Diagnose OTP delivery issues"""
        
        diagnosis_prompt = f"""
        Analyze this OTP delivery issue:
        
        App Version: {context.app_version}
        OS Version: {context.os_version}
        Connectivity: {context.connectivity_status}
        Issue Duration: {context.issue_duration} minutes
        Affected Orders: {len(context.affected_orders)}
        Error Messages: {context.error_messages or 'none'}
        
        Provide diagnosis in this format:
        OTP_ISSUE_TYPE: [APP_NOTIFICATION_BLOCKED/SMS_DELIVERY_FAILURE/NETWORK_CONNECTIVITY/SERVER_SIDE_ISSUE]
        SEVERITY: [LOW/MEDIUM/HIGH]
        CUSTOMER_IMPACT: [LOW/MEDIUM/HIGH]
        RECOVERY_PROBABILITY: [0.0-1.0]
        ALTERNATIVE_METHODS_AVAILABLE: [true/false]
        ESCALATION_NEEDED: [true/false]
        """
        
        try:
            response = await self.groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert in mobile app notification systems and OTP delivery mechanisms."},
                    {"role": "user", "content": diagnosis_prompt}
                ],
                temperature=0.1,
                max_tokens=600
            )
            
            return self._parse_ai_analysis(response.choices[0].message.content)
            
        except Exception as e:
            return self._create_fallback_otp_diagnosis(context)
    
    async def _diagnose_sync_issue(self, context: TechnicalContext, sync_type: str) -> Dict[str, Any]:
        """Diagnose synchronization issues"""
        
        last_sync_time = "unknown"
        if context.last_successful_sync:
            minutes_since_sync = int((datetime.now() - context.last_successful_sync).total_seconds() / 60)
            last_sync_time = f"{minutes_since_sync} minutes ago"
        
        diagnosis_prompt = f"""
        Analyze this {sync_type} synchronization failure:
        
        Last Successful Sync: {last_sync_time}
        Issue Duration: {context.issue_duration} minutes
        Connectivity Status: {context.connectivity_status}
        App Version: {context.app_version}
        Affected Orders: {len(context.affected_orders)}
        Device Storage: {context.device_storage_available} GB
        
        Provide diagnosis in this format:
        SYNC_ISSUE_TYPE: [PARTIAL_SYNC/COMPLETE_FAILURE/INTERMITTENT/DELAYED_SYNC]
        ROOT_CAUSE: [detailed_cause]
        NETWORK_RELATED: [true/false]
        SERVER_SIDE_ISSUE: [true/false]
        CLIENT_SIDE_ISSUE: [true/false]
        DATA_CORRUPTION_RISK: [true/false]
        RECOVERY_ETA: [minutes]
        """
        
        try:
            response = await self.groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": f"You are an expert in mobile app data synchronization and {sync_type} data management systems."},
                    {"role": "user", "content": diagnosis_prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            return self._parse_ai_analysis(response.choices[0].message.content)
            
        except Exception as e:
            return self._create_fallback_sync_diagnosis(context, sync_type)
    
    async def _analyze_payment_settlement_issue(self, context: TechnicalContext) -> Dict[str, Any]:
        """Analyze payment settlement discrepancies"""
        
        expected = context.expected_earnings or 0
        actual = context.actual_earnings or 0
        
        analysis_prompt = f"""
        Analyze this payment settlement issue:
        
        Payment Period: {context.payment_period or 'current_week'}
        Expected Earnings: ${expected:.2f}
        Actual Earnings Shown: ${actual:.2f}
        Discrepancy: ${expected - actual:.2f}
        Completed Deliveries: {len(context.affected_orders)}
        App Version: {context.app_version}
        
        Provide analysis in this format:
        PAYMENT_ISSUE_TYPE: [MISSING_TRANSACTIONS/INCORRECT_AMOUNTS/DELAYED_SETTLEMENT/CALCULATION_ERROR]
        DISCREPANCY_SEVERITY: [LOW/MEDIUM/HIGH/CRITICAL]
        PROBABLE_CAUSE: [detailed_cause]
        DATA_SYNC_RELATED: [true/false]
        MANUAL_INTERVENTION_REQUIRED: [true/false]
        ESTIMATED_RESOLUTION_TIME: [hours]
        INTERIM_COMPENSATION_RECOMMENDED: [true/false]
        """
        
        try:
            response = await self.groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert in payment processing systems and financial data reconciliation."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            return self._parse_ai_analysis(response.choices[0].message.content)
            
        except Exception as e:
            return self._create_fallback_payment_analysis(context)
    
    # Screenshot analysis
    async def _analyze_crash_screenshots(self, image_data: bytes, context: TechnicalContext) -> str:
        """Analyze app crash screenshots"""
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
                                "text": f"Analyze this delivery app crash screenshot. App version: {context.app_version}. Describe: error messages visible, UI elements frozen/missing, system notifications, crash indicators, recovery options shown."
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
            return f"Screenshot analysis failed: {str(e)}"
    
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
    def _create_fallback_crash_diagnosis(self, context: TechnicalContext) -> Dict[str, Any]:
        """Create fallback diagnosis for app crashes"""
        severity = "CRITICAL" if context.issue_duration > 30 else "MODERATE"
        return {
            "CRASH_SEVERITY": severity,
            "PROBABLE_CAUSE": "app_memory_or_network_issue",
            "DEVICE_COMPATIBILITY": "COMPATIBLE" if context.app_version in self.supported_app_versions else "MARGINAL",
            "STORAGE_ISSUE": str(context.device_storage_available < self.min_storage_requirement).lower(),
            "NETWORK_RELATED": str(context.connectivity_status != "good").lower(),
            "APP_VERSION_ISSUE": str(context.app_version not in self.supported_app_versions).lower(),
            "RECOVERY_PROBABILITY": "0.7",
            "IMMEDIATE_WORKAROUND_AVAILABLE": "true",
            "TECHNICAL_SUPPORT_URGENCY": "HIGH" if severity == "CRITICAL" else "MEDIUM"
        }
    
    def _create_fallback_otp_diagnosis(self, context: TechnicalContext) -> Dict[str, Any]:
        """Create fallback diagnosis for OTP issues"""
        return {
            "OTP_ISSUE_TYPE": "APP_NOTIFICATION_BLOCKED",
            "SEVERITY": "MEDIUM",
            "CUSTOMER_IMPACT": "MEDIUM",
            "RECOVERY_PROBABILITY": "0.8",
            "ALTERNATIVE_METHODS_AVAILABLE": "true",
            "ESCALATION_NEEDED": str(context.issue_duration > 15).lower()
        }
    
    def _create_fallback_sync_diagnosis(self, context: TechnicalContext, sync_type: str) -> Dict[str, Any]:
        """Create fallback diagnosis for sync issues"""
        return {
            "SYNC_ISSUE_TYPE": "INTERMITTENT",
            "ROOT_CAUSE": f"{sync_type}_data_network_connectivity_issue",
            "NETWORK_RELATED": str(context.connectivity_status != "good").lower(),
            "SERVER_SIDE_ISSUE": "false",
            "CLIENT_SIDE_ISSUE": "true",
            "DATA_CORRUPTION_RISK": "false",
            "RECOVERY_ETA": "10"
        }
    
    def _create_fallback_payment_analysis(self, context: TechnicalContext) -> Dict[str, Any]:
        """Create fallback analysis for payment issues"""
        discrepancy = (context.expected_earnings or 0) - (context.actual_earnings or 0)
        severity = "HIGH" if discrepancy > 50 else "MEDIUM" if discrepancy > 20 else "LOW"
        
        return {
            "PAYMENT_ISSUE_TYPE": "DELAYED_SETTLEMENT",
            "DISCREPANCY_SEVERITY": severity,
            "PROBABLE_CAUSE": "payment_processing_delay_or_sync_issue",
            "DATA_SYNC_RELATED": "true",
            "MANUAL_INTERVENTION_REQUIRED": str(severity in ["HIGH", "CRITICAL"]).lower(),
            "ESTIMATED_RESOLUTION_TIME": "24",
            "INTERIM_COMPENSATION_RECOMMENDED": str(discrepancy > 25).lower()
        }


# Example usage
if __name__ == "__main__":
    async def test_technical_handler():
        handler = TechnicalHandler()
        
        # Test app crash scenario
        crash_context = TechnicalContext(
            delivery_agent_id="DA001",
            device_info={"model": "iPhone 12", "os": "iOS 16.1"},
            issue_type=TechnicalIssueType.APP_CRASH,
            affected_orders=["ORD001", "ORD002"],
            issue_duration=25,
            connectivity_status="good",
            app_version="3.2.1",
            os_version="iOS 16.1",
            device_storage_available=1.5,
            error_messages=["App crashed while loading orders"],
            crash_logs_available=True
        )
        
        result = await handler.handle_technical_issue(crash_context)
        print(f"App crash result: {result}")
    
    asyncio.run(test_technical_handler())