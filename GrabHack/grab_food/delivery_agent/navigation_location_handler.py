"""
Navigation & Location Issues Handler
Consolidates: Incorrect address, GPS/app crash, difficulty finding customer location
Enhanced with Google Maps API integration for address verification and navigation assistance
"""

import asyncio
import os
import urllib.parse
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import base64
import json
import requests
from dotenv import load_dotenv

from groq import AsyncGroq

# Load environment variables
load_dotenv()


class NavigationIssueType(Enum):
    INCORRECT_ADDRESS = "incorrect_customer_address"
    GPS_APP_CRASH = "gps_app_technical_failure"
    LOCATION_DIFFICULTY = "customer_location_finding_difficulty"


class AddressIssueType(Enum):
    WRONG_PIN_CODE = "incorrect_pin_code"
    MISSING_DETAILS = "insufficient_address_details"
    INVALID_LOCATION = "non_existent_address"
    OUTDATED_INFO = "address_changed_recently"


class GPSIssueType(Enum):
    GPS_MALFUNCTION = "gps_hardware_failure"
    APP_CRASH = "delivery_app_crash"
    NETWORK_CONNECTIVITY = "poor_internet_connection"
    MAP_DATA_CORRUPT = "corrupted_map_data"


class LocationDifficultyType(Enum):
    GATED_SOCIETY = "restricted_access_community"
    MISSING_LANDMARKS = "inadequate_navigation_markers"
    COMPLEX_BUILDING = "multi_tower_confusion"
    RURAL_AREA = "remote_location_challenges"


@dataclass
class NavigationContext:
    order_id: str
    customer_id: str
    delivery_agent_id: str
    issue_type: NavigationIssueType
    current_location: str
    target_address: str
    customer_phone: str
    gps_coordinates: Optional[Tuple[float, float]]
    time_spent_searching: int  # minutes
    attempts_made: int
    customer_responsive: bool
    weather_conditions: Optional[str] = None
    evidence_image: Optional[bytes] = None
    additional_context: Optional[Dict[str, Any]] = None


class GoogleMapsAPI:
    """Google Maps API integration for navigation assistance"""

    def __init__(self):
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY not found in environment variables")
        self.base_url = "https://maps.googleapis.com/maps/api"

    def geocode_address(self, address: str) -> Dict[str, Any]:
        """Geocode an address to get coordinates and formatted address"""
        try:
            url = f"{self.base_url}/geocode/json"
            params = {
                'address': address,
                'key': self.api_key
            }

            response = requests.get(url, params=params)
            data = response.json()

            if data['status'] == 'OK' and data['results']:
                result = data['results'][0]
                return {
                    'success': True,
                    'formatted_address': result['formatted_address'],
                    'latitude': result['geometry']['location']['lat'],
                    'longitude': result['geometry']['location']['lng'],
                    'place_id': result['place_id'],
                    'types': result.get('types', [])
                }
            else:
                return {
                    'success': False,
                    'error': data.get('error_message', 'Address not found'),
                    'status': data['status']
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status': 'API_ERROR'
            }

    def get_directions(self, origin: str, destination: str, mode: str = 'driving') -> Dict[str, Any]:
        """Get directions between two points"""
        try:
            url = f"{self.base_url}/directions/json"
            params = {
                'origin': origin,
                'destination': destination,
                'mode': mode,
                'key': self.api_key
            }

            response = requests.get(url, params=params)
            data = response.json()

            if data['status'] == 'OK' and data['routes']:
                route = data['routes'][0]
                leg = route['legs'][0]
                return {
                    'success': True,
                    'distance': leg['distance']['text'],
                    'duration': leg['duration']['text'],
                    'start_address': leg['start_address'],
                    'end_address': leg['end_address'],
                    'steps': len(leg['steps']),
                    'overview_polyline': route['overview_polyline']['points']
                }
            else:
                return {
                    'success': False,
                    'error': data.get('error_message', 'Route not found'),
                    'status': data['status']
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status': 'API_ERROR'
            }

    def generate_static_map_url(self, center: str, markers: List[str] = None, zoom: int = 15, size: str = "600x400") -> str:
        """Generate static map URL with markers"""
        try:
            url = f"{self.base_url}/staticmap"
            params = {
                'center': center,
                'zoom': zoom,
                'size': size,
                'key': self.api_key
            }

            if markers:
                for i, marker in enumerate(markers):
                    params[f'markers'] = f"color:red|label:{i+1}|{marker}"

            return f"{url}?" + "&".join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items()])
        except Exception as e:
            return f"Error generating map: {str(e)}"


class NavigationLocationHandler:
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_food"
        self.actor = "delivery_agent"
        self.max_search_time = 20  # minutes
        self.escalation_threshold = 15  # minutes
        # Default testing locations
        self.default_current_location = "Sapna Book Stores, Jayanagar, Bangalore"
        self.default_destination = "South End Circle Metro, Bangalore"
        self.maps_api = GoogleMapsAPI()

    def handle_navigation_issues(self, query: str, image_data: Optional[str] = None) -> str:
        """Main handler for navigation issues - simple interface for AI engine"""

        query_lower = query.lower()

        # Try to extract order details for better navigation assistance
        order_details = self._get_order_details_from_query(query)

        if any(word in query_lower for word in ['stuck', 'traffic', 'reroute', 'alternative route']):
            return self.handle_traffic_rerouting(query, image_data, order_details)
        elif any(word in query_lower for word in ['address', 'wrong address', 'find location']):
            return self.handle_address_issues(query, image_data, order_details)
        elif any(word in query_lower for word in ['gps', 'maps', 'navigation not working']):
            return self.handle_gps_issues(query, image_data, order_details)
        else:
            return self.handle_general_navigation(query, image_data, order_details)

    def handle_traffic_rerouting(self, query: str, image_data: Optional[str] = None, order_details: Optional[Dict] = None) -> str:
        """Handle traffic issues and provide rerouting with Google Maps API"""

        # Extract locations from query, order details, or use defaults
        current_location = self._extract_current_location(query)
        destination = self._extract_destination(query)

        # Use order details if available and locations not found in query
        if order_details:
            if not current_location:
                current_location = order_details.get('start_location') or order_details.get('restaurant_name')
            if not destination:
                destination = order_details.get('end_location')

        # Fall back to defaults if still not found
        current_location = current_location or self.default_current_location
        destination = destination or self.default_destination

        # Get real-time directions using Google Maps API
        directions_result = self.maps_api.get_directions(current_location, destination)

        # Generate navigation links
        maps_link = self._generate_google_maps_navigation_link(current_location, destination)
        waze_link = self._generate_waze_navigation_link(current_location, destination)

        # Include real-time route information if available
        route_info = ""
        if directions_result['success']:
            route_info = f"""
**📊 Real-time Route Information:**
- **Distance:** {directions_result['distance']}
- **Estimated Time:** {directions_result['duration']}
- **Route Steps:** {directions_result['steps']} navigation points
"""

        return f"""🚦 **Traffic Rerouting Solution**

**Current Route Issue:** Traffic detected on your current path

**📍 Navigation Links (Click to Open):**

🗺️ **Google Maps Navigation:**
{maps_link}

🚗 **Waze Alternative Route:**
{waze_link}

**📱 Quick Actions:**
1. **Click the Google Maps link above** - Opens turn-by-turn navigation with real-time traffic
2. **Alternative: Use Waze link** - Often finds faster routes during traffic
3. **Call Customer:** Inform about delay and new ETA

**⏱️ Route Information:**
- **From:** {current_location}
- **To:** {destination}
{route_info}

**🔄 Additional Options:**
- **Re-route automatically** using the navigation apps
- **Avoid toll roads** if selected in app settings
- **Motorcycle/bicycle lanes** available if applicable

**📞 Customer Communication:**
"Hi! I'm rerouting due to traffic to ensure fastest delivery. Your new ETA will be updated in the app. Thank you for your patience!"

**💡 Pro Tip:** Save both links for easy access during delivery!"""

    def handle_address_issues(self, query: str, image_data: Optional[str] = None, order_details: Optional[Dict] = None) -> str:
        """Handle incorrect or unclear addresses with Google Maps API verification"""

        # Extract locations from query, order details, or use defaults
        current_location = self._extract_current_location(query)
        destination = self._extract_destination(query)

        # Use order details if available
        order_info = ""
        if order_details:
            if not current_location:
                current_location = order_details.get('start_location') or order_details.get('restaurant_name')
            if not destination:
                destination = order_details.get('end_location')
            order_info = f"\n**📋 Order Info:**\n- Order ID: {order_details.get('order_id', 'N/A')}\n- Restaurant: {order_details.get('restaurant_name', 'N/A')}\n- Payment: {order_details.get('payment_method', 'N/A')}\n"

        # Fall back to defaults if still not found
        current_location = current_location or self.default_current_location
        destination = destination or self.default_destination

        # Verify address using Google Maps API
        address_verification = self.maps_api.geocode_address(destination)

        maps_link = self._generate_google_maps_navigation_link(current_location, destination)

        # Address verification information
        verification_info = ""
        if address_verification['success']:
            verification_info = f"""
**✅ Address Verification:**
- **Verified Address:** {address_verification['formatted_address']}
- **Coordinates:** {address_verification['latitude']:.4f}, {address_verification['longitude']:.4f}
- **Status:** Address found in Google Maps database
"""
        else:
            verification_info = f"""
**⚠️ Address Verification:**
- **Status:** Address not found in Google Maps
- **Issue:** {address_verification.get('error', 'Unknown error')}
- **Action Required:** Customer verification needed
"""

        return f"""🏠 **Address Resolution Assistant**

{verification_info}

**📍 Current Navigation Link:**
{maps_link}

**🔍 Address Verification Steps:**
1. **Click the Google Maps link above** for navigation assistance
2. **Cross-check with customer address** in your delivery app
3. **Call customer** to confirm exact location
4. **Request landmark references** (nearby shops, buildings)

**📞 Customer Questions to Ask:**
- "Can you confirm your complete address with building/flat number?"
- "What landmarks are nearby your location?"
- "Can you share your live location via WhatsApp?"
- "Should I look for any specific building color or sign?"

**🎯 Location Details:**
- **Your Location:** {current_location}
- **Customer Address:** {destination}
- **Backup Apps:** Use Waze or Apple Maps if Google Maps fails

**⚡ Quick Solutions:**
- **Meet at landmark:** Ask customer to meet at nearby recognizable place
- **Building entrance:** For complexes, meet at main gate
- **Live location:** Request customer to share exact pin location

**🆘 Escalation:** If address cannot be resolved in 15 minutes, contact customer support for assistance."""

    def handle_gps_issues(self, query: str, image_data: Optional[str] = None, order_details: Optional[Dict] = None) -> str:
        """Handle GPS and navigation app technical problems"""

        current_location = self._extract_current_location(query) or self.default_current_location
        destination = self._extract_destination(query) or self.default_destination

        maps_link = self._generate_google_maps_navigation_link(current_location, destination)
        waze_link = self._generate_waze_navigation_link(current_location, destination)

        # Generate static map for offline reference
        static_map_url = self.maps_api.generate_static_map_url(
            center=destination,
            markers=[current_location, destination],
            zoom=14
        )

        return f"""📱 **GPS & Navigation Fix**

**🔧 Immediate Solutions:**

**Primary Navigation Links:**
🗺️ **Google Maps:** {maps_link}
🚗 **Waze Backup:** {waze_link}

**📍 Static Map Reference:**
{static_map_url}

**📱 Troubleshooting Steps:**
1. **Click navigation links above** - Works even if your GPS app crashed
2. **Restart your phone** - Fixes most GPS issues quickly
3. **Check location services** - Ensure GPS is enabled
4. **Clear app cache** - Go to Settings > Apps > Maps > Clear Cache

**🌐 Alternative Navigation:**
- **Use phone browser** - Navigation links work in any browser
- **Download offline maps** - Google Maps offline mode
- **Ask for directions** - Call customer for turn-by-turn guidance

**📍 Current Route:**
- **From:** {current_location}
- **To:** {destination}

**⚡ Emergency Options:**
- **Customer guidance:** Call customer for real-time directions
- **Local help:** Ask nearby shopkeepers for directions
- **Voice navigation:** Use hands-free calling with customer

**🔄 Performance Protection:**
- GPS failures are technical issues (no penalty)
- Time spent troubleshooting is protected
- Device replacement available for persistent problems"""

    def handle_general_navigation(self, query: str, image_data: Optional[str] = None, order_details: Optional[Dict] = None) -> str:
        """General navigation assistance"""

        current_location = self._extract_current_location(query) or self.default_current_location
        destination = self._extract_destination(query) or self.default_destination

        maps_link = self._generate_google_maps_navigation_link(current_location, destination)

        # Get route information if possible
        directions_result = self.maps_api.get_directions(current_location, destination)
        route_summary = ""
        if directions_result['success']:
            route_summary = f"""
**📊 Route Summary:**
- **Distance:** {directions_result['distance']}
- **Estimated Time:** {directions_result['duration']}
- **Navigation Steps:** {directions_result['steps']} turns/instructions
"""

        return f"""🧭 **Navigation Assistant**

**📍 Your Navigation Link:**
{maps_link}

**🎯 Current Journey:**
- **From:** {current_location}
- **To:** {destination}
{route_summary}

**💡 Navigation Tips:**
1. **Click the link above** - Opens Google Maps with turn-by-turn directions
2. **Save customer's number** - For easy communication during delivery
3. **Check traffic before leaving** - Plan your route ahead
4. **Keep phone charged** - Carry power bank for longer deliveries

**📱 Multi-App Strategy:**
- **Primary:** Google Maps (most accurate with real-time traffic)
- **Backup:** Waze (better community-based updates)
- **Offline:** Download area maps for poor network zones

**🔄 If Navigation Fails:**
1. Call customer for directions
2. Ask local shopkeepers
3. Use voice calls for real-time guidance
4. Contact delivery support for assistance

**⭐ Pro Tips:**
- Learn major landmarks in your delivery area
- Build relationships with local businesses for directions
- Keep multiple navigation apps installed
- Always inform customer about any delays immediately"""

    def _extract_current_location(self, query: str) -> Optional[str]:
        """Extract current location from query if mentioned"""
        # Look for patterns like "from [location]" or "currently at [location]"
        import re

        patterns = [
            r'(?:from|currently at|at|starting from)\s+([^,]+(?:,\s*[^,]+)*)',
            r'(?:my location is|i am at|im at)\s+([^,]+(?:,\s*[^,]+)*)'
        ]

        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                return match.group(1).strip()

        return None

    def _extract_destination(self, query: str) -> Optional[str]:
        """Extract destination from query if mentioned"""
        import re

        patterns = [
            r'(?:to|going to|destination|deliver to)\s+([^,]+(?:,\s*[^,]+)*)',
            r'(?:customer at|address is|location is)\s+([^,]+(?:,\s*[^,]+)*)'
        ]

        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                return match.group(1).strip()

        return None

    def _generate_google_maps_navigation_link(self, origin: str, destination: str) -> str:
        """Generate Google Maps navigation link"""
        # URL encode the locations
        origin_encoded = urllib.parse.quote(origin)
        destination_encoded = urllib.parse.quote(destination)

        # Google Maps navigation URL format
        maps_url = f"https://www.google.com/maps/dir/{origin_encoded}/{destination_encoded}/"

        return f"[🗺️ Open Google Maps Navigation]({maps_url})"

    def _generate_waze_navigation_link(self, origin: str, destination: str) -> str:
        """Generate Waze navigation link"""
        destination_encoded = urllib.parse.quote(destination)

        # Waze navigation URL format
        waze_url = f"https://waze.com/ul?q={destination_encoded}&navigate=yes"

        return f"[🚗 Open Waze Navigation]({waze_url})"

    def _get_order_details_from_query(self, query: str) -> Optional[Dict]:
        """Extract order details from database for better navigation assistance"""
        import sqlite3
        import os
        import json
        import re

        try:
            # Try to extract order ID from query
            order_id_match = re.search(r'order[\s#]*([A-Z]{1,2}\d{3,4})', query, re.IGNORECASE)
            order_id = order_id_match.group(1) if order_id_match else None

            if not order_id:
                return None

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
                return None

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get order details
            cursor.execute('''
                SELECT
                    id, start_location, end_location, restaurant_name,
                    customer_id, status, payment_method, details
                FROM orders
                WHERE id = ? AND service = 'grab_food'
            ''', (order_id,))

            result = cursor.fetchone()
            conn.close()

            if result:
                order_id, start_loc, end_loc, restaurant, customer_id, status, payment_method, details = result

                order_details = {
                    'order_id': order_id,
                    'start_location': start_loc or 'Restaurant Area',
                    'end_location': end_loc or 'Customer Location',
                    'restaurant_name': restaurant or 'Restaurant',
                    'customer_id': customer_id,
                    'status': status,
                    'payment_method': payment_method
                }

                # Add details from JSON if available
                if details:
                    try:
                        details_json = json.loads(details)
                        order_details.update(details_json)
                    except:
                        pass

                return order_details

        except Exception as e:
            return None

        return None

    async def handle_navigation_issue(self, context: NavigationContext) -> Dict[str, Any]:
        """Main handler for all navigation and location issues"""

        if context.issue_type == NavigationIssueType.INCORRECT_ADDRESS:
            return await self._handle_incorrect_address(context)
        elif context.issue_type == NavigationIssueType.GPS_APP_CRASH:
            return await self._handle_gps_app_crash(context)
        elif context.issue_type == NavigationIssueType.LOCATION_DIFFICULTY:
            return await self._handle_location_difficulty(context)
        else:
            return {"error": "Unknown navigation issue type"}

    async def _handle_incorrect_address(self, context: NavigationContext) -> Dict[str, Any]:
        """Handle incorrect customer address issues with Google Maps verification"""

        # Verify address using Google Maps API
        address_verification = self.maps_api.geocode_address(context.target_address)

        # Analyze address issue using AI and API results
        address_analysis = await self._analyze_address_issue_with_api(context, address_verification)

        # Execute enhanced address verification protocol
        verification_result = await self._execute_address_verification(context, address_analysis, address_verification)

        # Customer communication for address correction
        customer_communication = await self._initiate_address_correction_communication(context, address_analysis)

        # Alternative location strategies using Maps API
        alternative_solutions = await self._explore_address_alternatives_with_maps(context, address_analysis, address_verification)

        # Performance protection
        performance_protection = await self._apply_address_performance_protection(context, address_analysis)

        return {
            "issue_type": "incorrect_address",
            "address_verification": address_verification,
            "address_analysis": address_analysis,
            "verification_result": verification_result,
            "customer_communication": customer_communication,
            "alternative_solutions": alternative_solutions,
            "performance_protection": performance_protection,
            "status": "handled",
            "timestamp": datetime.now().isoformat(),
            "maps_api_used": True
        }

    async def _analyze_address_issue_with_api(self, context: NavigationContext, address_verification: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced address analysis using Google Maps API results"""

        # Determine issue type based on API verification
        if not address_verification["success"]:
            if "coordinates" in context.target_address.lower():
                issue_type = "INVALID_LOCATION"
            elif len(context.target_address.split()) < 3:
                issue_type = "MISSING_DETAILS"
            else:
                issue_type = "WRONG_PIN_CODE"
        else:
            issue_type = "OUTDATED_INFO"  # Valid address but still can't find

        # Calculate confidence based on API results
        verification_confidence = 0.9 if address_verification["success"] else 0.1

        # Determine correction probability
        if address_verification["success"]:
            correction_probability = 0.8
        elif context.customer_responsive:
            correction_probability = 0.7
        else:
            correction_probability = 0.4

        return {
            "ADDRESS_ISSUE_TYPE": issue_type,
            "VERIFICATION_CONFIDENCE": verification_confidence,
            "CORRECTION_PROBABILITY": correction_probability,
            "CUSTOMER_CONTACT_REQUIRED": not address_verification["success"],
            "GPS_NAVIGATION_POSSIBLE": address_verification["success"],
            "ALTERNATIVE_PICKUP_SUGGESTED": verification_confidence < 0.5,
            "ESTIMATED_RESOLUTION_TIME": self._estimate_resolution_time(issue_type, context.customer_responsive, verification_confidence),
            "MAPS_API_DATA": address_verification,
            "RECOMMENDED_ACTIONS": self._generate_address_recommendations(issue_type, address_verification, context)
        }

    def _estimate_resolution_time(self, issue_type: str, customer_responsive: bool, confidence: float) -> int:
        """Estimate time to resolve address issue in minutes"""
        base_time = {
            "WRONG_PIN_CODE": 5,
            "MISSING_DETAILS": 8,
            "INVALID_LOCATION": 15,
            "OUTDATED_INFO": 10
        }.get(issue_type, 10)

        if not customer_responsive:
            base_time += 10

        if confidence < 0.3:
            base_time += 15

        return min(base_time, 30)  # Cap at 30 minutes

    def _generate_address_recommendations(self, issue_type: str, verification: Dict[str, Any], context: NavigationContext) -> List[str]:
        """Generate specific recommendations based on address analysis"""
        recommendations = []

        if verification["success"]:
            recommendations.extend([
                "use_verified_coordinates_for_navigation",
                "share_precise_location_with_customer",
                "enable_gps_guided_navigation"
            ])
        else:
            recommendations.extend([
                "contact_customer_for_address_clarification",
                "request_nearby_landmarks_or_reference_points",
                "suggest_alternative_pickup_location"
            ])

        if issue_type == "MISSING_DETAILS":
            recommendations.extend([
                "request_complete_address_with_building_details",
                "ask_for_floor_number_and_apartment_details",
                "get_contact_person_information"
            ])
        elif issue_type == "INVALID_LOCATION":
            recommendations.extend([
                "verify_address_exists_in_maps",
                "suggest_nearest_valid_address",
                "coordinate_with_customer_service"
            ])

        return recommendations

    async def _explore_address_alternatives_with_maps(self, context: NavigationContext, analysis: Dict[str, Any], verification: Dict[str, Any]) -> List[str]:
        """Explore alternative solutions using Maps API data"""
        alternatives = []

        if verification["success"]:
            # Valid address found - use GPS navigation
            alternatives.extend([
                "navigate_to_verified_coordinates",
                "enable_turn_by_turn_navigation",
                "share_live_location_with_customer"
            ])
        else:
            # Invalid address - need alternatives
            alternatives.extend([
                "suggest_nearest_landmark_pickup",
                "coordinate_alternative_meeting_point",
                "escalate_to_customer_service_support"
            ])

        # Time-based alternatives
        resolution_time = analysis.get("ESTIMATED_RESOLUTION_TIME", 15)
        if resolution_time > 20:
            alternatives.extend([
                "consider_order_reassignment_to_nearby_agent",
                "offer_customer_pickup_from_restaurant",
                "implement_partial_refund_with_future_credit"
            ])

        return alternatives

    async def _execute_address_verification(self, context: NavigationContext, analysis: Dict[str, Any], verification: Dict[str, Any]) -> Dict[str, Any]:
        """Execute enhanced address verification using Maps API"""
        verification_steps = []

        if verification["success"]:
            verification_steps.extend([
                "google_maps_address_verified",
                "coordinates_extracted_successfully",
                "navigation_route_calculated"
            ])

            # Get navigation directions if coordinates available
            if context.current_location:
                try:
                    directions = self.maps_api.get_directions(context.current_location, verification['formatted_address'])
                    if directions['success']:
                        verification_steps.extend([
                            f"navigation_route_duration_{directions['duration']}",
                            f"distance_to_target_{directions['distance']}",
                            f"route_calculated_successfully"
                        ])
                except:
                    verification_steps.append("navigation_route_calculation_failed")
        else:
            verification_steps.extend([
                "google_maps_verification_failed",
                "address_not_found_in_maps_database",
                "customer_contact_required_for_clarification"
            ])

        return {
            "verification_completed": True,
            "steps_executed": verification_steps,
            "maps_api_integration": True,
            "next_action_required": not verification["success"]
        }

    # ... [Keep all other existing methods unchanged] ...

    # Common helper methods
    async def _execute_address_verification(self, context: NavigationContext, analysis: Dict[str, Any]) -> List[str]:
        """Execute address verification steps"""
        actions = []

        if analysis.get("CUSTOMER_COOPERATION_NEEDED") == "true":
            customer_verification = await self._contact_customer_for_verification(context)
            actions.append(f"customer_verification: {customer_verification}")

        # Cross-reference with mapping services
        mapping_verification = await self._verify_with_mapping_services(context)
        actions.append(f"mapping_verification: {mapping_verification}")

        # GPS coordinate validation
        if context.gps_coordinates:
            gps_validation = await self._validate_gps_coordinates(context.gps_coordinates, context.target_address)
            actions.append(f"gps_validation: {gps_validation}")

        return actions

    async def _contact_customer_for_verification(self, context: NavigationContext) -> str:
        """Contact customer for address verification"""
        try:
            # Multi-channel communication
            communication_methods = ["call", "sms", "app_message"]

            verification_message = f"""
            Hello! I'm your delivery agent for order {context.order_id}.
            I'm having difficulty locating your address: {context.target_address}

            Could you please:
            1. Confirm your complete address
            2. Provide nearby landmarks
            3. Share your live location if possible

            I've been searching for {context.time_spent_searching} minutes.
            """

            await asyncio.sleep(0.1)  # Simulate communication
            return f"customer_contacted_via_{'+'.join(communication_methods)}"

        except Exception as e:
            return f"customer_contact_failed: {str(e)}"

    async def _verify_with_mapping_services(self, context: NavigationContext) -> str:
        """Verify address with multiple mapping services"""
        try:
            mapping_services = ["google_maps", "apple_maps", "openstreetmap"]
            verification_results = []

            for service in mapping_services:
                # Simulate mapping service verification
                await asyncio.sleep(0.05)
                verification_results.append(f"{service}_verified")

            return f"verified_with_{'+'.join(verification_results)}"

        except Exception as e:
            return f"mapping_verification_failed: {str(e)}"

    async def _validate_gps_coordinates(self, coordinates: Tuple[float, float], address: str) -> str:
        """Validate GPS coordinates against address"""
        try:
            lat, lon = coordinates
            # Simulate coordinate validation
            await asyncio.sleep(0.1)

            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return f"coordinates_valid_lat_{lat}_lon_{lon}"
            else:
                return "coordinates_invalid_out_of_range"

        except Exception as e:
            return f"coordinate_validation_failed: {str(e)}"

    # Performance protection methods
    async def _apply_address_performance_protection(self, context: NavigationContext, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply performance protection for address issues"""
        return {
            "delivery_time_adjustment": True,
            "performance_score_protection": True,
            "incident_classification": "customer_provided_incorrect_address",
            "compensation_eligible": context.time_spent_searching > 15,
            "time_spent_excluded_from_metrics": context.time_spent_searching
        }


# Example usage
if __name__ == "__main__":
    async def test_navigation_handler():
        handler = NavigationLocationHandler()

        # Test address issue
        address_context = NavigationContext(
            order_id="ORD001",
            customer_id="CUST001",
            delivery_agent_id="DA001",
            issue_type=NavigationIssueType.INCORRECT_ADDRESS,
            current_location="Near target area",
            target_address="123 Main St, Apt 4B",
            customer_phone="+1234567890",
            gps_coordinates=(12.9716, 77.5946),
            time_spent_searching=12,
            attempts_made=3,
            customer_responsive=True
        )

        result = await handler.handle_navigation_issue(address_context)
        print(f"Address issue result: {result}")

    asyncio.run(test_navigation_handler())