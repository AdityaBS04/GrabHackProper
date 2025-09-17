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
    
    # ===== STRICT WORKFLOW METHODS =====

    def get_agent_credibility_score(self, agent_id: str) -> int:
        """Calculate agent credibility score based on performance history"""
        import sqlite3
        import os
        from datetime import datetime, timedelta

        base_score = 7  # Start with neutral-high credibility

        # Handle anonymous or invalid agent IDs
        if not agent_id or agent_id == "anonymous":
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
                return self._get_simulated_agent_credibility_score(agent_id)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get agent's performance from users table
            cursor.execute('''
                SELECT credibility_score
                FROM users
                WHERE username = ? AND user_type = 'delivery_agent'
            ''', (agent_id,))

            user_result = cursor.fetchone()
            if user_result:
                base_score = user_result[0]

            # Get agent's delivery history
            cursor.execute('''
                SELECT
                    COUNT(*) as total_deliveries,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_deliveries,
                    COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_deliveries,
                    AVG(price) as avg_order_value
                FROM orders
                WHERE delivery_agent_id = ? AND service = 'grab_food'
                AND date >= date('now', '-30 days')
            ''', (agent_id,))

            result = cursor.fetchone()
            if result:
                total_deliveries, completed_deliveries, cancelled_deliveries, avg_order_value = result

                if total_deliveries > 0:
                    completion_rate = completed_deliveries / total_deliveries

                    # Adjust score based on completion rate
                    if completion_rate >= 0.95:
                        base_score += 2
                    elif completion_rate >= 0.85:
                        base_score += 1
                    elif completion_rate < 0.70:
                        base_score -= 2

                    # Adjust based on delivery volume (experienced agent)
                    if total_deliveries >= 100:
                        base_score += 2
                    elif total_deliveries >= 50:
                        base_score += 1

            # Check recent technical complaints
            cursor.execute('''
                SELECT COUNT(*)
                FROM complaints
                WHERE username = ? AND service = 'grab_food' AND user_type = 'delivery_agent'
                AND complaint_type LIKE '%technical%'
                AND created_at >= datetime('now', '-30 days')
            ''', (agent_id,))

            recent_tech_complaints = cursor.fetchone()[0] if cursor.fetchone() else 0
            if recent_tech_complaints > 3:
                base_score -= 2
            elif recent_tech_complaints > 1:
                base_score -= 1

            conn.close()

        except Exception as e:
            logger.error(f"Error calculating agent credibility score: {e}")
            return self._get_simulated_agent_credibility_score(agent_id)

        return max(1, min(10, int(base_score)))

    def _get_simulated_agent_credibility_score(self, agent_id: str) -> int:
        """Fallback simulated credibility scoring"""
        base_score = 7

        if "test" in agent_id.lower():
            base_score -= 1

        if len(agent_id) > 8:
            base_score += 1

        return max(1, min(10, base_score))

    def handle_app_crash_strict(self, query: str, agent_id: str, image_data: str = None) -> str:
        """Handle app crashes with strict 6-step workflow"""
        logger.info(f"Processing app crash complaint: {query[:100]}...")

        # Step 1: Extract crash details and device information
        crash_details = self.extract_crash_details(query)
        if not crash_details["device_info"] and not crash_details["error_symptoms"]:
            return "📱 To diagnose the app crash, please provide device information (phone model, Android/iOS version) and describe what was happening when the app crashed."

        # Step 2: Validate crash against system logs and app version
        system_validation = self.validate_crash_against_system_logs(crash_details, agent_id)
        logger.info(f"System validation: {system_validation}")

        # Step 3: Analyze crash severity and impact on deliveries
        crash_analysis = self.analyze_crash_severity_and_impact(crash_details, system_validation)
        logger.info(f"Crash analysis: {crash_analysis}")

        # Step 4: Check agent credibility and technical complaint history
        credibility_score = self.get_agent_credibility_score(agent_id)
        tech_complaint_pattern = self.check_tech_complaint_history(agent_id)
        logger.info(f"Agent credibility: {credibility_score}/10, Tech pattern: {tech_complaint_pattern}")

        # Step 5: Determine resolution priority and compensation eligibility
        resolution_priority = self.determine_crash_resolution_priority(crash_analysis, credibility_score, tech_complaint_pattern)
        logger.info(f"Resolution priority: {resolution_priority}")

        # Step 6: Generate technical support response with next steps
        response = self.generate_crash_support_response(resolution_priority, crash_details, crash_analysis)
        logger.info(f"App crash response generated successfully")

        return response

    def extract_crash_details(self, query: str) -> dict:
        """Extract crash details from agent's report"""
        import re

        details = {
            "device_info": "",
            "error_symptoms": "",
            "crash_frequency": "single",
            "app_version": "",
            "affected_orders": 0,
            "data_loss": False
        }

        # Extract device information
        device_patterns = [
            r'(iphone|android|samsung|apple|ios|pixel)',
            r'(version\s+[\d\.]+)',
            r'(\d+\.\d+\.\d+)'
        ]

        query_lower = query.lower()
        for pattern in device_patterns:
            match = re.search(pattern, query_lower)
            if match:
                details["device_info"] += match.group(1) + " "

        # Extract symptoms
        symptom_keywords = ['crash', 'freeze', 'hang', 'stuck', 'error', 'black screen', 'restart']
        found_symptoms = [keyword for keyword in symptom_keywords if keyword in query_lower]
        details["error_symptoms"] = ", ".join(found_symptoms)

        # Determine frequency
        if any(word in query_lower for word in ['repeatedly', 'multiple times', 'constantly', 'always']):
            details["crash_frequency"] = "frequent"
        elif any(word in query_lower for word in ['sometimes', 'occasionally', 'few times']):
            details["crash_frequency"] = "occasional"

        # Check for data loss indicators
        if any(word in query_lower for word in ['lost', 'missing', 'disappeared', 'deleted']):
            details["data_loss"] = True

        return details

    def validate_crash_against_system_logs(self, crash_details: dict, agent_id: str) -> dict:
        """Validate crash report against system logs and app telemetry"""
        # In real implementation, this would query crash reporting systems

        validation = {
            "crash_logs_found": False,
            "app_version_supported": True,
            "device_compatibility": "compatible",
            "system_outage_correlation": False,
            "agent_specific_issue": False
        }

        # Simulate system validation based on details
        if crash_details["crash_frequency"] == "frequent":
            validation["crash_logs_found"] = True
            validation["agent_specific_issue"] = True

        device_info = crash_details.get("device_info", "").lower()
        if "old" in device_info or any(old_version in device_info for old_version in ["android 6", "ios 12"]):
            validation["device_compatibility"] = "marginal"
            validation["app_version_supported"] = False

        return validation

    def analyze_crash_severity_and_impact(self, crash_details: dict, system_validation: dict) -> dict:
        """Analyze crash severity and impact on delivery operations"""

        severity = "LOW"
        impact_level = "MINIMAL"

        # Determine severity based on frequency and symptoms
        if crash_details["crash_frequency"] == "frequent":
            severity = "HIGH"
            impact_level = "SEVERE"
        elif crash_details["data_loss"]:
            severity = "MEDIUM"
            impact_level = "MODERATE"
        elif "freeze" in crash_details.get("error_symptoms", ""):
            severity = "MEDIUM"
            impact_level = "MODERATE"

        # Factor in system validation
        if not system_validation["app_version_supported"]:
            severity = "HIGH"
        if system_validation["device_compatibility"] == "incompatible":
            severity = "CRITICAL"
            impact_level = "SEVERE"

        return {
            "severity": severity,
            "impact_level": impact_level,
            "delivery_disruption": severity in ["HIGH", "CRITICAL"],
            "immediate_action_required": severity == "CRITICAL",
            "compensation_warranted": impact_level in ["MODERATE", "SEVERE"]
        }

    def check_tech_complaint_history(self, agent_id: str) -> str:
        """Check agent's technical complaint history"""
        if agent_id == "anonymous":
            return "NO_HISTORY_AVAILABLE"
        elif "test" in agent_id.lower():
            return "FREQUENT_TECH_ISSUES"
        else:
            return "NORMAL_TECH_PATTERN"

    def determine_crash_resolution_priority(self, crash_analysis: dict, credibility_score: int, tech_pattern: str) -> str:
        """Determine resolution priority based on analysis"""
        severity = crash_analysis["severity"]
        impact = crash_analysis["impact_level"]

        if severity == "CRITICAL":
            return "EMERGENCY_PRIORITY"
        elif severity == "HIGH" and credibility_score >= 7:
            return "HIGH_PRIORITY"
        elif severity == "HIGH" and credibility_score < 7:
            return "MEDIUM_PRIORITY_VERIFICATION"
        elif tech_pattern == "FREQUENT_TECH_ISSUES":
            return "PATTERN_INVESTIGATION"
        else:
            return "STANDARD_PRIORITY"

    def generate_crash_support_response(self, resolution_priority: str, crash_details: dict, crash_analysis: dict) -> str:
        """Generate comprehensive technical support response"""

        if resolution_priority == "EMERGENCY_PRIORITY":
            return f"""🚨 **EMERGENCY - Critical App Crash Support**

**Issue Classification:** Critical system failure requiring immediate intervention

**✅ Immediate Actions Taken:**
- Emergency technical team notified
- Backup device deployment authorized
- Order reassignment protocols activated
- Performance protection applied to your account

**🔧 Emergency Resolution Steps:**
1. **STOP using the current app immediately**
2. Call Emergency Tech Support: 1800-GRAB-TECH
3. Backup phone/device will be provided within 2 hours
4. Alternative order assignment system activated

**💰 Compensation & Protection:**
- Lost delivery opportunities: Full compensation
- Emergency device provision: No charge
- Performance ratings: Fully protected
- Technical downtime payment: Activated

**⏰ Timeline:**
- Emergency support contact: Within 15 minutes
- Backup device deployment: 2 hours maximum
- Full system restoration: Within 24 hours

Reference ID: TECH-EMRG-{hash(str(crash_details)) % 10000:04d}

Your safety and earning capability are our top priority during this critical technical issue."""

        elif resolution_priority == "HIGH_PRIORITY":
            return f"""🔧 **HIGH PRIORITY - App Crash Technical Support**

**Issue Analysis Complete:**
- Crash severity: {crash_analysis['severity']}
- Delivery impact: {crash_analysis['impact_level']}
- Device compatibility: Verified
- System logs: Under review

**✅ Priority Resolution Plan:**
1. **App Recovery Protocol:**
   - Force stop current app and clear cache
   - Update to latest app version (3.3.2)
   - Reset app data if necessary
   - Re-sync account and order data

2. **Device Optimization:**
   - Storage cleanup: Free up 2GB+ space
   - Background app management
   - Network connectivity optimization
   - Battery optimization settings

**💰 Performance Protection:**
- Delivery completion rates: Protected
- Earnings during downtime: Compensated
- Customer ratings: Technical issue buffer applied
- Order assignment priority: Maintained

**📞 Dedicated Support:**
- Priority tech support line: 1800-GRAB-PRIORITY
- Live chat technical assistance available
- Screen sharing support if needed
- Follow-up within 6 hours guaranteed

**⏰ Expected Resolution:**
- Basic functionality: 30 minutes
- Full app stability: 2-4 hours
- Performance monitoring: 48 hours

Reference ID: TECH-HIGH-{hash(str(crash_details)) % 10000:04d}"""

        elif resolution_priority == "PATTERN_INVESTIGATION":
            return f"""📊 **Technical Pattern Investigation Required**

We notice multiple technical issues on your account requiring specialized analysis.

**Investigation Scope:**
- Device compatibility assessment
- App usage pattern analysis
- Network connectivity evaluation
- Account-specific issue identification

**Next Steps:**
👨‍💼 **Senior Technical Specialist** assigned to your case
📊 Comprehensive device and app performance analysis
📞 Direct consultation within 12 hours
🎯 Customized technical solution development

**Temporary Measures:**
- Alternative order receipt methods activated
- Extended technical issue protection
- Priority support queue placement
- Performance metric adjustments

Reference ID: TECH-INV-{hash(str(crash_details)) % 10000:04d}

We're committed to resolving recurring technical issues permanently."""

        else:  # STANDARD_PRIORITY
            return f"""📱 **Technical Support - App Crash Resolution**

**Issue Assessment:**
- Crash type: {crash_details.get('error_symptoms', 'General app malfunction')}
- Frequency: {crash_details.get('crash_frequency', 'Single occurrence')}
- Device impact: Manageable

**🔧 Resolution Steps:**
1. **Basic Recovery:**
   - Restart your device completely
   - Update app to latest version
   - Clear app cache and data
   - Test with a small order

2. **If Issues Persist:**
   - Check device storage (need 1GB+ free)
   - Verify network connectivity
   - Disable battery optimization for Grab app
   - Restart app after each delivery

**💡 Prevention Tips:**
- Keep app updated automatically
- Maintain 2GB+ free storage space
- Close background apps regularly
- Use WiFi when possible for better stability

**Support Available:**
- Technical help line: 1800-GRAB-HELP
- Live chat support in app
- Video tutorials: grab.com/agent-support

Resolution typically completes within 2-4 hours with these steps."""

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