"""
Logistics Issues Handler
Consolidates: Traffic delays, Vehicle breakdown, Accident/safety issues, Multiple order batching confusion
Enhanced with Google Maps API and Weather API integration for predictive analysis
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import base64
import json

from groq import AsyncGroq
from ...api_integrations import GoogleMapsAPI, WeatherAPI, PredictiveAnalytics, LocationData


class LogisticsIssueType(Enum):
    TRAFFIC_DELAYS = "traffic_congestion_delays"
    VEHICLE_BREAKDOWN = "vehicle_mechanical_failure"
    SAFETY_ACCIDENT = "accident_safety_incident"
    ORDER_BATCHING_CONFUSION = "multiple_order_management_confusion"


class TrafficSeverity(Enum):
    LIGHT = "minor_delays_5_10_minutes"
    MODERATE = "significant_delays_10_20_minutes"
    HEAVY = "major_delays_20_plus_minutes"
    GRIDLOCK = "severe_standstill_traffic"


class VehicleIssueType(Enum):
    BIKE_PUNCTURE = "motorcycle_tire_puncture"
    FUEL_SHORTAGE = "insufficient_fuel_range"
    ENGINE_MALFUNCTION = "mechanical_engine_failure"
    BATTERY_DEAD = "electrical_system_failure"
    BRAKE_ISSUES = "braking_system_malfunction"


class SafetyIncidentType(Enum):
    MINOR_ACCIDENT = "minor_collision_no_injury"
    MAJOR_ACCIDENT = "serious_collision_injury_possible"
    WEATHER_HAZARD = "dangerous_weather_conditions"
    ROAD_HAZARD = "unsafe_road_conditions"
    PERSONAL_EMERGENCY = "health_safety_emergency"


class BatchingConfusionType(Enum):
    ORDER_MIX_UP = "wrong_order_wrong_customer"
    ROUTE_OPTIMIZATION_FAILURE = "inefficient_delivery_sequence"
    CUSTOMER_CONFUSION = "multiple_customer_interaction_errors"
    TIME_MANAGEMENT = "poor_time_allocation_between_orders"


@dataclass
class LogisticsContext:
    order_ids: List[str]  # Can be multiple for batching issues
    customer_ids: List[str]
    delivery_agent_id: str
    issue_type: LogisticsIssueType
    current_location: str
    estimated_delay: int  # minutes
    safety_level: str  # low, medium, high, critical
    weather_conditions: Optional[str] = None
    traffic_conditions: Optional[str] = None
    vehicle_condition: Optional[str] = None
    orders_remaining: int = 1
    evidence_image: Optional[bytes] = None
    emergency_services_needed: bool = False
    additional_context: Optional[Dict[str, Any]] = None


class LogisticsHandler:
    def __init__(self):
        self.groq_client = AsyncGroq()
        self.emergency_threshold = 30  # minutes
        self.critical_safety_keywords = ["accident", "injury", "emergency", "hospital"]
        
        # Initialize API integrations for predictive analysis
        self.maps_api = GoogleMapsAPI()
        self.weather_api = WeatherAPI()
        self.predictive_analytics = PredictiveAnalytics(self.maps_api, self.weather_api)
        
    async def handle_logistics_issue(self, context: LogisticsContext) -> Dict[str, Any]:
        """Main handler for all logistics issues"""
        
        if context.issue_type == LogisticsIssueType.TRAFFIC_DELAYS:
            return await self._handle_traffic_delays(context)
        elif context.issue_type == LogisticsIssueType.VEHICLE_BREAKDOWN:
            return await self._handle_vehicle_breakdown(context)
        elif context.issue_type == LogisticsIssueType.SAFETY_ACCIDENT:
            return await self._handle_safety_accident(context)
        elif context.issue_type == LogisticsIssueType.ORDER_BATCHING_CONFUSION:
            return await self._handle_order_batching_confusion(context)
        else:
            return {"error": "Unknown logistics issue type"}
    
    async def _handle_traffic_delays(self, context: LogisticsContext) -> Dict[str, Any]:
        """Handle traffic delay situations with real-time API data"""
        
        # Parse location data for API calls
        origin_location = self._parse_location(context.current_location)
        destination_locations = [self._parse_location(order.get('delivery_address', '')) 
                               for order in context.orders_remaining]
        
        # Get real-time predictions and analysis
        api_predictions = []
        for dest in destination_locations:
            if dest:
                prediction = await self.predictive_analytics.predict_delivery_delay(origin_location, dest)
                route_optimization = await self.predictive_analytics.optimize_delivery_route(origin_location, dest)
                api_predictions.append({
                    'destination': dest.address,
                    'prediction': prediction,
                    'route_optimization': route_optimization
                })
        
        # Analyze traffic situation with API data
        traffic_analysis = await self._analyze_traffic_situation_with_api(context, api_predictions)
        
        # Enhanced route optimization using real-time data
        route_optimization = await self._optimize_routes_for_traffic(context, traffic_analysis, api_predictions)
        
        # Customer communication with accurate predictions
        customer_communication = await self._communicate_traffic_delays(context, traffic_analysis)
        
        # Performance protection
        performance_protection = await self._apply_traffic_performance_protection(context, traffic_analysis)
        
        # Alternative solutions with API recommendations
        alternative_solutions = await self._explore_traffic_alternatives(context, traffic_analysis, api_predictions)
        
        return {
            "issue_type": "traffic_delays",
            "traffic_analysis": traffic_analysis,
            "api_predictions": api_predictions,
            "route_optimization": route_optimization,
            "customer_communication": customer_communication,
            "performance_protection": performance_protection,
            "alternative_solutions": alternative_solutions,
            "status": "handled",
            "timestamp": datetime.now().isoformat(),
            "real_time_data_used": True
        }
    
    def _parse_location(self, location_string: str) -> LocationData:
        """Parse location string to LocationData object for API calls"""
        try:
            # Extract coordinates if available (format: "lat,lng,address")
            parts = location_string.split(',')
            if len(parts) >= 3 and parts[0].replace('.','').replace('-','').isdigit():
                lat = float(parts[0].strip())
                lng = float(parts[1].strip())
                address = ','.join(parts[2:]).strip()
                return LocationData(latitude=lat, longitude=lng, address=address)
            else:
                # Use default Singapore coordinates for address-only locations
                return LocationData(latitude=1.3521, longitude=103.8198, address=location_string)
        except (ValueError, IndexError):
            # Fallback to default location
            return LocationData(latitude=1.3521, longitude=103.8198, address=location_string)
    
    async def _analyze_traffic_situation_with_api(self, context: LogisticsContext, api_predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhanced traffic analysis using real-time API data"""
        
        # Calculate average predictions from API data
        total_delay = 0
        total_confidence = 0
        traffic_conditions = []
        weather_conditions = []
        
        for prediction_data in api_predictions:
            prediction = prediction_data['prediction']
            total_delay += prediction['total_predicted_delay']
            total_confidence += prediction['confidence_score']
            traffic_conditions.append(prediction['traffic_condition'])
            weather_conditions.append(prediction['weather_condition'])
        
        if api_predictions:
            avg_delay = total_delay / len(api_predictions)
            avg_confidence = total_confidence / len(api_predictions)
        else:
            avg_delay = context.estimated_delay
            avg_confidence = 0.7
        
        # Determine traffic severity based on API data
        if avg_delay > 30:
            traffic_severity = "GRIDLOCK"
            delay_category = "EXCEPTIONAL"
        elif avg_delay > 20:
            traffic_severity = "HEAVY" 
            delay_category = "UNEXPECTED"
        elif avg_delay > 10:
            traffic_severity = "MODERATE"
            delay_category = "EXPECTED"
        else:
            traffic_severity = "LIGHT"
            delay_category = "EXPECTED"
        
        # Check for route alternatives
        route_alternatives_available = any(
            len(pred['route_optimization']['optimized_routes']) > 1 
            for pred in api_predictions
        )
        
        return {
            "TRAFFIC_SEVERITY": traffic_severity,
            "DELAY_CATEGORY": delay_category,
            "ROUTE_ALTERNATIVES_AVAILABLE": route_alternatives_available,
            "CUSTOMER_IMPACT_LEVEL": "HIGH" if avg_delay > 20 else "MEDIUM" if avg_delay > 10 else "LOW",
            "PERFORMANCE_IMPACT_SCORE": min(1.0, avg_delay / 60),  # Normalize to 0-1 scale
            "AVERAGE_PREDICTED_DELAY": avg_delay,
            "CONFIDENCE_SCORE": avg_confidence,
            "TRAFFIC_CONDITIONS": list(set(traffic_conditions)),
            "WEATHER_CONDITIONS": list(set(weather_conditions)),
            "RECOMMENDED_ACTIONS": self._generate_api_based_recommendations(avg_delay, traffic_conditions, weather_conditions),
            "RESOLUTION_ETA": avg_delay,
            "API_DATA_AVAILABLE": True
        }
    
    def _generate_api_based_recommendations(self, avg_delay: float, traffic_conditions: List[str], weather_conditions: List[str]) -> List[str]:
        """Generate recommendations based on API analysis"""
        recommendations = []
        
        if avg_delay > 25:
            recommendations.extend([
                "use_alternative_routes_immediately",
                "notify_customers_of_significant_delay", 
                "consider_reassigning_orders_to_nearby_agents"
            ])
        elif avg_delay > 15:
            recommendations.extend([
                "explore_alternative_routes",
                "update_customer_eta_notifications",
                "monitor_traffic_conditions_closely"
            ])
        else:
            recommendations.append("continue_with_minor_adjustments")
        
        # Weather-specific recommendations
        if any("rain" in condition or "storm" in condition for condition in weather_conditions):
            recommendations.extend([
                "use_weather_protection_for_orders",
                "reduce_driving_speed_for_safety",
                "prioritize_covered_routes"
            ])
        
        # Traffic-specific recommendations
        if "heavy" in traffic_conditions or "severe" in traffic_conditions:
            recommendations.extend([
                "avoid_main_highways",
                "use_local_roads_alternative",
                "coordinate_with_other_agents_in_area"
            ])
        
        return recommendations
    
    async def _optimize_routes_for_traffic(self, context: LogisticsContext, analysis: Dict[str, Any], api_predictions: List[Dict[str, Any]] = None) -> List[str]:
        """Enhanced route optimization using API data"""
        optimizations = []
        
        if api_predictions:
            # Use API-based route optimizations
            for prediction_data in api_predictions:
                route_opt = prediction_data['route_optimization']
                if route_opt['optimized_routes']:
                    best_route = route_opt['optimized_routes'][0]  # First is usually best scored
                    optimizations.extend([
                        f"route_optimized_for_{prediction_data['destination']}",
                        f"estimated_time_savings_{best_route.get('duration_minutes', 0)}_minutes",
                        f"weather_adjusted_route_selected"
                    ])
            
            optimizations.extend([
                "real_time_traffic_data_integrated",
                "weather_impact_considered",
                "multiple_delivery_routes_optimized"
            ])
        else:
            # Fallback to original optimization logic
            if analysis.get("ROUTE_ALTERNATIVES_AVAILABLE"):
                optimizations.append("alternative_route_calculated")
            
            optimizations.extend([
                "traffic_pattern_analysis_applied",
                "real_time_traffic_monitoring_enabled"
            ])
        
        return optimizations
    
    async def _explore_traffic_alternatives(self, context: LogisticsContext, analysis: Dict[str, Any], api_predictions: List[Dict[str, Any]] = None) -> List[str]:
        """Explore alternative solutions using API recommendations"""
        alternatives = []
        
        if api_predictions:
            # Use API-based alternatives
            avg_delay = analysis.get("AVERAGE_PREDICTED_DELAY", context.estimated_delay)
            
            if avg_delay > 30:
                alternatives.extend([
                    "reassign_orders_to_nearest_available_agents",
                    "implement_dynamic_delivery_time_windows",
                    "activate_emergency_delivery_protocols"
                ])
            elif avg_delay > 15:
                alternatives.extend([
                    "reschedule_non_urgent_deliveries",
                    "offer_delivery_time_flexibility_to_customers",
                    "coordinate_multi_agent_delivery_handoffs"
                ])
            
            # Weather-based alternatives
            weather_conditions = analysis.get("WEATHER_CONDITIONS", [])
            if any("rain" in condition or "storm" in condition for condition in weather_conditions):
                alternatives.extend([
                    "activate_weather_contingency_protocols",
                    "use_covered_delivery_vehicles_if_available",
                    "prioritize_indoor_pickup_points"
                ])
        else:
            # Original alternatives logic
            alternatives.extend([
                "route_recalculation_with_traffic_avoidance",
                "customer_notification_system_activated",
                "delivery_partner_coordination_enhanced"
            ])
        
        return alternatives
    
    async def _analyze_traffic_situation(self, context: LogisticsContext) -> Dict[str, Any]:
        """Analyze traffic delay situation using AI"""
        
        analysis_prompt = f"""
        Analyze this traffic delay situation:
        
        Current Location: {context.current_location}
        Estimated Delay: {context.estimated_delay} minutes
        Orders Remaining: {context.orders_remaining}
        Weather Conditions: {context.weather_conditions or 'normal'}
        Traffic Conditions: {context.traffic_conditions or 'unknown'}
        Time of Day: {datetime.now().strftime('%H:%M')}
        
        Provide analysis in this exact format:
        TRAFFIC_SEVERITY: [LIGHT/MODERATE/HEAVY/GRIDLOCK]
        DELAY_CATEGORY: [EXPECTED/UNEXPECTED/EXCEPTIONAL]
        ROUTE_ALTERNATIVES_AVAILABLE: [true/false]
        CUSTOMER_IMPACT_LEVEL: [LOW/MEDIUM/HIGH]
        PERFORMANCE_IMPACT_SCORE: [0.0-1.0]
        RECOMMENDED_ACTIONS: [comma-separated list]
        RESOLUTION_ETA: [minutes]
        """
        
        try:
            if context.evidence_image:
                image_analysis = await self._analyze_traffic_evidence(context.evidence_image, context)
                analysis_prompt += f"\n\nTraffic Image Evidence: {image_analysis}"
            
            response = await self.groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert in traffic analysis and delivery logistics optimization."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            return self._parse_ai_analysis(response.choices[0].message.content)
            
        except Exception as e:
            return self._create_fallback_traffic_analysis(context)
    
    async def _handle_vehicle_breakdown(self, context: LogisticsContext) -> Dict[str, Any]:
        """Handle vehicle breakdown situations"""
        
        # Diagnose vehicle issue
        vehicle_diagnosis = await self._diagnose_vehicle_issue(context)
        
        # Emergency response if needed
        emergency_response = await self._coordinate_breakdown_emergency_response(context, vehicle_diagnosis)
        
        # Repair/replacement solutions
        repair_solutions = await self._coordinate_vehicle_repair_replacement(context, vehicle_diagnosis)
        
        # Order transfer protocols
        order_transfer = await self._coordinate_order_transfer(context, vehicle_diagnosis)
        
        # Compensation and support
        agent_support = await self._provide_breakdown_agent_support(context, vehicle_diagnosis)
        
        return {
            "issue_type": "vehicle_breakdown",
            "vehicle_diagnosis": vehicle_diagnosis,
            "emergency_response": emergency_response,
            "repair_solutions": repair_solutions,
            "order_transfer": order_transfer,
            "agent_support": agent_support,
            "status": "handled",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _diagnose_vehicle_issue(self, context: LogisticsContext) -> Dict[str, Any]:
        """Diagnose vehicle breakdown using AI"""
        
        diagnosis_prompt = f"""
        Diagnose this vehicle breakdown:
        
        Vehicle Condition Description: {context.vehicle_condition or 'mechanical_issue'}
        Current Location: {context.current_location}
        Safety Level: {context.safety_level}
        Weather: {context.weather_conditions or 'normal'}
        Orders in Transit: {len(context.order_ids)}
        
        Provide diagnosis in this format:
        VEHICLE_ISSUE_TYPE: [BIKE_PUNCTURE/FUEL_SHORTAGE/ENGINE_MALFUNCTION/BATTERY_DEAD/BRAKE_ISSUES]
        SEVERITY: [MINOR/MODERATE/MAJOR/CRITICAL]
        ROADSIDE_REPAIR_POSSIBLE: [true/false]
        SAFETY_RISK_LEVEL: [LOW/MEDIUM/HIGH/CRITICAL]
        REPAIR_TIME_ESTIMATE: [minutes]
        REPLACEMENT_VEHICLE_NEEDED: [true/false]
        EMERGENCY_SERVICES_REQUIRED: [true/false]
        """
        
        try:
            if context.evidence_image:
                image_analysis = await self._analyze_vehicle_evidence(context.evidence_image, context)
                diagnosis_prompt += f"\n\nVehicle Image Evidence: {image_analysis}"
            
            response = await self.groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert in vehicle diagnostics and roadside emergency response."},
                    {"role": "user", "content": diagnosis_prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            return self._parse_ai_analysis(response.choices[0].message.content)
            
        except Exception as e:
            return self._create_fallback_vehicle_diagnosis(context)
    
    async def _handle_safety_accident(self, context: LogisticsContext) -> Dict[str, Any]:
        """Handle safety incidents and accidents - CRITICAL PRIORITY"""
        
        # Immediate safety assessment
        safety_assessment = await self._assess_safety_incident(context)
        
        # Emergency services coordination
        emergency_coordination = await self._coordinate_emergency_services(context, safety_assessment)
        
        # Medical/safety support
        medical_support = await self._provide_medical_safety_support(context, safety_assessment)
        
        # Order management during emergency
        emergency_order_management = await self._manage_orders_during_emergency(context, safety_assessment)
        
        # Insurance and documentation
        incident_documentation = await self._document_safety_incident(context, safety_assessment)
        
        # Agent welfare and support
        agent_welfare = await self._provide_emergency_agent_support(context, safety_assessment)
        
        return {
            "issue_type": "safety_accident",
            "priority": "CRITICAL",
            "safety_assessment": safety_assessment,
            "emergency_coordination": emergency_coordination,
            "medical_support": medical_support,
            "emergency_order_management": emergency_order_management,
            "incident_documentation": incident_documentation,
            "agent_welfare": agent_welfare,
            "status": "emergency_handled",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _assess_safety_incident(self, context: LogisticsContext) -> Dict[str, Any]:
        """Assess safety incident severity and requirements"""
        
        assessment_prompt = f"""
        EMERGENCY SAFETY ASSESSMENT:
        
        Incident Location: {context.current_location}
        Safety Level Reported: {context.safety_level}
        Emergency Services Requested: {context.emergency_services_needed}
        Weather Conditions: {context.weather_conditions or 'unknown'}
        Additional Context: {context.additional_context or 'none'}
        
        CRITICAL ASSESSMENT - Provide in this format:
        INCIDENT_TYPE: [MINOR_ACCIDENT/MAJOR_ACCIDENT/WEATHER_HAZARD/ROAD_HAZARD/PERSONAL_EMERGENCY]
        SEVERITY: [LOW/MEDIUM/HIGH/CRITICAL]
        IMMEDIATE_MEDICAL_ATTENTION: [true/false]
        EMERGENCY_SERVICES_PRIORITY: [LOW/MEDIUM/HIGH/CRITICAL]
        AGENT_MOBILITY_STATUS: [MOBILE/LIMITED/IMMOBILE]
        CONTINUED_DELIVERY_POSSIBLE: [true/false]
        IMMEDIATE_ACTIONS_REQUIRED: [comma-separated critical actions]
        """
        
        try:
            if context.evidence_image:
                image_analysis = await self._analyze_safety_evidence(context.evidence_image, context)
                assessment_prompt += f"\n\nSAFETY IMAGE EVIDENCE: {image_analysis}"
            
            response = await self.groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an emergency response expert. Prioritize safety above all else. Be thorough and cautious in your assessment."},
                    {"role": "user", "content": assessment_prompt}
                ],
                temperature=0.0,  # Maximum precision for safety
                max_tokens=1000
            )
            
            return self._parse_ai_analysis(response.choices[0].message.content)
            
        except Exception as e:
            # Critical fallback - assume worst case for safety
            return self._create_critical_safety_fallback(context)
    
    async def _handle_order_batching_confusion(self, context: LogisticsContext) -> Dict[str, Any]:
        """Handle multiple order batching confusion"""
        
        # Analyze batching issue
        batching_analysis = await self._analyze_batching_confusion(context)
        
        # Order verification and sorting
        order_verification = await self._verify_and_sort_orders(context, batching_analysis)
        
        # Customer communication management
        customer_management = await self._manage_multiple_customer_communications(context, batching_analysis)
        
        # Route re-optimization
        route_reoptimization = await self._reoptimize_delivery_routes(context, batching_analysis)
        
        # Performance protection
        performance_protection = await self._apply_batching_performance_protection(context, batching_analysis)
        
        return {
            "issue_type": "order_batching_confusion",
            "batching_analysis": batching_analysis,
            "order_verification": order_verification,
            "customer_management": customer_management,
            "route_reoptimization": route_reoptimization,
            "performance_protection": performance_protection,
            "status": "handled",
            "timestamp": datetime.now().isoformat()
        }
    
    # Implementation of key methods
    async def _optimize_routes_for_traffic(self, context: LogisticsContext, analysis: Dict[str, Any]) -> List[str]:
        """Optimize routes to avoid traffic"""
        optimizations = []
        
        if analysis.get("ROUTE_ALTERNATIVES_AVAILABLE") == "true":
            optimizations.append("alternative_route_calculated")
            optimizations.append("traffic_pattern_analysis_applied")
        
        if context.orders_remaining > 1:
            optimizations.append("delivery_sequence_reordered")
            optimizations.append("customer_proximity_optimization")
        
        optimizations.append("real_time_traffic_monitoring_enabled")
        return optimizations
    
    async def _communicate_traffic_delays(self, context: LogisticsContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Communicate traffic delays to customers"""
        
        delay_minutes = context.estimated_delay
        communication_result = {
            "customers_notified": len(context.customer_ids),
            "notification_method": "multi_channel_sms_app_call",
            "delay_communicated": f"{delay_minutes}_minutes",
            "alternative_options_provided": delay_minutes > 20
        }
        
        if delay_minutes > 30:
            communication_result["compensation_offered"] = True
            communication_result["rescheduling_option_provided"] = True
        
        return communication_result
    
    async def _coordinate_breakdown_emergency_response(self, context: LogisticsContext, diagnosis: Dict[str, Any]) -> List[str]:
        """Coordinate emergency response for vehicle breakdown"""
        emergency_actions = []
        
        if diagnosis.get("SAFETY_RISK_LEVEL") in ["HIGH", "CRITICAL"]:
            emergency_actions.append("emergency_services_contacted")
            emergency_actions.append("hazard_warning_activated")
        
        if diagnosis.get("ROADSIDE_REPAIR_POSSIBLE") == "false":
            emergency_actions.append("towing_service_requested")
            emergency_actions.append("replacement_vehicle_dispatched")
        
        emergency_actions.append("agent_safety_secured")
        emergency_actions.append("location_monitoring_activated")
        
        return emergency_actions
    
    async def _coordinate_order_transfer(self, context: LogisticsContext, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate transfer of orders to another agent"""
        
        transfer_result = {
            "transfer_required": diagnosis.get("REPLACEMENT_VEHICLE_NEEDED") == "true",
            "orders_affected": len(context.order_ids),
            "transfer_method": "nearest_available_agent"
        }
        
        if transfer_result["transfer_required"]:
            transfer_result.update({
                "backup_agent_dispatched": True,
                "customer_notification_sent": True,
                "order_handoff_coordinated": True,
                "estimated_additional_delay": "15-25 minutes"
            })
        
        return transfer_result
    
    async def _coordinate_emergency_services(self, context: LogisticsContext, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate emergency services for safety incidents"""
        
        services_coordination = {
            "emergency_call_made": assessment.get("EMERGENCY_SERVICES_PRIORITY") != "LOW",
            "location_shared_with_dispatch": True,
            "incident_type_communicated": assessment.get("INCIDENT_TYPE", "UNKNOWN")
        }
        
        priority = assessment.get("EMERGENCY_SERVICES_PRIORITY", "MEDIUM")
        
        if priority in ["HIGH", "CRITICAL"]:
            services_coordination.update({
                "ambulance_requested": assessment.get("IMMEDIATE_MEDICAL_ATTENTION") == "true",
                "police_notified": True,
                "grab_emergency_team_alerted": True,
                "insurance_company_contacted": True
            })
        
        return services_coordination
    
    async def _manage_orders_during_emergency(self, context: LogisticsContext, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Manage orders during emergency situations"""
        
        emergency_management = {
            "orders_secured": True,
            "customer_emergency_notification": True,
            "alternative_delivery_arranged": assessment.get("CONTINUED_DELIVERY_POSSIBLE") == "false"
        }
        
        if not assessment.get("CONTINUED_DELIVERY_POSSIBLE", False):
            emergency_management.update({
                "backup_agent_emergency_dispatch": True,
                "full_refund_processing_initiated": True,
                "priority_reorder_option_provided": True
            })
        
        return emergency_management
    
    async def _verify_and_sort_orders(self, context: LogisticsContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Verify and sort multiple orders"""
        
        verification_result = {
            "orders_verified": len(context.order_ids),
            "customer_order_matching_completed": True,
            "delivery_sequence_optimized": True
        }
        
        confusion_type = analysis.get("CONFUSION_TYPE", "ORDER_MIX_UP")
        
        if confusion_type == "ORDER_MIX_UP":
            verification_result["order_customer_remapping_completed"] = True
        elif confusion_type == "ROUTE_OPTIMIZATION_FAILURE":
            verification_result["route_sequence_recalculated"] = True
        elif confusion_type == "TIME_MANAGEMENT":
            verification_result["delivery_time_windows_adjusted"] = True
        
        return verification_result
    
    async def _manage_multiple_customer_communications(self, context: LogisticsContext, analysis: Dict[str, Any]) -> List[str]:
        """Manage communications with multiple customers"""
        communications = []
        
        for i, customer_id in enumerate(context.customer_ids):
            communications.append(f"customer_{i+1}_updated_with_corrected_eta")
            communications.append(f"customer_{i+1}_delivery_sequence_communicated")
        
        if len(context.customer_ids) > 2:
            communications.append("batch_delivery_explanation_provided")
            communications.append("individual_tracking_links_sent")
        
        return communications
    
    # Performance protection methods
    async def _apply_traffic_performance_protection(self, context: LogisticsContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply performance protection for traffic delays"""
        return {
            "delivery_time_adjustment": True,
            "performance_score_protection": True,
            "incident_classification": "external_traffic_conditions",
            "delay_excluded_from_metrics": context.estimated_delay,
            "compensation_eligible": context.estimated_delay > 20
        }
    
    async def _apply_batching_performance_protection(self, context: LogisticsContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply performance protection for batching confusion"""
        return {
            "delivery_time_adjustment": True,
            "performance_score_protection": True,
            "incident_classification": "system_batching_algorithm_issue",
            "complexity_bonus_applied": len(context.order_ids) > 3,
            "training_support_provided": True
        }
    
    # Evidence analysis methods
    async def _analyze_traffic_evidence(self, image_data: bytes, context: LogisticsContext) -> str:
        """Analyze traffic situation from image"""
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
                                "text": f"Analyze this traffic situation image. Location: {context.current_location}. Describe traffic density, road conditions, alternative routes visible, and estimated delay severity."
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
            return f"Traffic image analysis failed: {str(e)}"
    
    async def _analyze_vehicle_evidence(self, image_data: bytes, context: LogisticsContext) -> str:
        """Analyze vehicle breakdown from image"""
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
                                "text": f"Analyze this vehicle breakdown image. Describe the mechanical issue, safety concerns, repair complexity, and whether roadside repair is feasible."
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
            return f"Vehicle image analysis failed: {str(e)}"
    
    async def _analyze_safety_evidence(self, image_data: bytes, context: LogisticsContext) -> str:
        """Analyze safety incident from image - CRITICAL"""
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
                                "text": "CRITICAL SAFETY ANALYSIS: Analyze this safety incident image. Describe: injury severity (if visible), vehicle damage, road hazards, emergency services needs, immediate safety risks. Prioritize human safety above all else."
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
                temperature=0.0,  # Maximum precision for safety
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"CRITICAL: Safety image analysis failed: {str(e)} - Assume worst case scenario"
    
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
    def _create_fallback_traffic_analysis(self, context: LogisticsContext) -> Dict[str, Any]:
        """Create fallback analysis for traffic delays"""
        severity = "MODERATE" if context.estimated_delay < 20 else "HEAVY"
        return {
            "TRAFFIC_SEVERITY": severity,
            "DELAY_CATEGORY": "UNEXPECTED",
            "ROUTE_ALTERNATIVES_AVAILABLE": "true",
            "CUSTOMER_IMPACT_LEVEL": "MEDIUM",
            "PERFORMANCE_IMPACT_SCORE": "0.0",
            "RECOMMENDED_ACTIONS": ["route_optimization", "customer_notification", "eta_update"],
            "RESOLUTION_ETA": str(context.estimated_delay)
        }
    
    def _create_fallback_vehicle_diagnosis(self, context: LogisticsContext) -> Dict[str, Any]:
        """Create fallback diagnosis for vehicle issues"""
        return {
            "VEHICLE_ISSUE_TYPE": "ENGINE_MALFUNCTION",
            "SEVERITY": "MODERATE",
            "ROADSIDE_REPAIR_POSSIBLE": "false",
            "SAFETY_RISK_LEVEL": context.safety_level.upper(),
            "REPAIR_TIME_ESTIMATE": "30",
            "REPLACEMENT_VEHICLE_NEEDED": "true",
            "EMERGENCY_SERVICES_REQUIRED": str(context.emergency_services_needed).lower()
        }
    
    def _create_critical_safety_fallback(self, context: LogisticsContext) -> Dict[str, Any]:
        """Create critical safety fallback - assume worst case"""
        return {
            "INCIDENT_TYPE": "MAJOR_ACCIDENT",
            "SEVERITY": "CRITICAL",
            "IMMEDIATE_MEDICAL_ATTENTION": "true",
            "EMERGENCY_SERVICES_PRIORITY": "CRITICAL",
            "AGENT_MOBILITY_STATUS": "IMMOBILE",
            "CONTINUED_DELIVERY_POSSIBLE": "false",
            "IMMEDIATE_ACTIONS_REQUIRED": ["emergency_services_contact", "medical_assistance", "scene_securing", "insurance_notification"]
        }


# Example usage
if __name__ == "__main__":
    async def test_logistics_handler():
        handler = LogisticsHandler()
        
        # Test traffic delay
        traffic_context = LogisticsContext(
            order_ids=["ORD001", "ORD002"],
            customer_ids=["CUST001", "CUST002"],
            delivery_agent_id="DA001",
            issue_type=LogisticsIssueType.TRAFFIC_DELAYS,
            current_location="Downtown traffic jam",
            estimated_delay=25,
            safety_level="low",
            traffic_conditions="heavy_congestion",
            orders_remaining=2
        )
        
        result = await handler.handle_logistics_issue(traffic_context)
        print(f"Traffic delay result: {result}")
    
    asyncio.run(test_logistics_handler())