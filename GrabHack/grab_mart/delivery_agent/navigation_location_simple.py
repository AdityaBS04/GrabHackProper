"""
Simple, Practical Navigation & Location Handler for Grab Mart Delivery Agents
Handles location issues, rerouting, traffic problems, and address corrections
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class NavigationLocationHandler:
    """Simple and practical navigation handler for Grab Mart delivery agents"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_mart"
        self.actor = "delivery_agent"
        
    def handle_navigation_location(self, query: str, image_data: Optional[str] = None) -> str:
        """Main handler for all navigation and location issues"""
        
        query_lower = query.lower()
        
        # Determine issue type based on keywords
        if any(word in query_lower for word in ['address', 'wrong address', 'incorrect address', 'can\'t find address']):
            return self.handle_incorrect_address(query, image_data)
        elif any(word in query_lower for word in ['gps', 'app crash', 'navigation not working', 'maps']):
            return self.handle_gps_app_issues(query, image_data)
        elif any(word in query_lower for word in ['can\'t find', 'location', 'house', 'building']):
            return self.handle_location_difficulty(query, image_data)
        elif any(word in query_lower for word in ['traffic', 'stuck', 'jam', 'route', 'reroute']):
            return self.handle_traffic_rerouting(query, image_data)
        else:
            # Default to location assistance
            return self.handle_general_navigation_help(query, image_data)
    
    def handle_incorrect_address(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle incorrect customer address with practical solutions"""
        
        return """🏠 **Address Issue Resolution**

**Immediate Actions:**
1. **Contact Customer** - Call/text customer to verify correct address
2. **Check Order Details** - Verify address in your delivery app
3. **Use Alternative Apps** - Try Google Maps, Waze, or Apple Maps for address verification

**Address Verification Steps:**
✅ Ask customer for:
- Complete address with building/apartment number  
- Nearby landmarks (shops, hospitals, schools)
- Pin location share if possible
- Contact person if different location

**Alternative Solutions:**
🔄 **Meet at Nearby Landmark** - Suggest meeting at a recognizable location
🏢 **Building Main Gate** - If complex/gated community, meet at main entrance  
📍 **Pin Location** - Request customer to share live location pin
🆘 **Customer Pickup** - Offer customer to collect from a convenient nearby location

**Performance Protection:**
- Time spent on address verification is excused
- No delivery time penalty for incorrect addresses  
- Full support for order completion or customer refund

**Next Steps:**
1. Document the address issue in your app
2. Contact customer service if address cannot be resolved in 15 minutes
3. Keep customer informed of progress

**Support:** Call delivery support at any time for address verification assistance."""

    def handle_gps_app_issues(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle GPS and navigation app technical problems"""
        
        return """📱 **GPS & Navigation App Fix**

**Immediate Troubleshooting:**
1. **Restart Navigation** - Close and reopen your navigation app
2. **Check Internet** - Ensure strong mobile data/WiFi connection
3. **Restart Phone** - Force restart if app keeps crashing
4. **Clear App Cache** - Go to Settings > Apps > [Navigation App] > Clear Cache

**Alternative Navigation:**
🗺️ **Backup Apps** - Use Waze, Apple Maps, or offline maps as backup
📞 **Customer Guidance** - Call customer for turn-by-turn directions
🧭 **Manual Navigation** - Use road signs and ask locals for directions
📍 **Live Location** - Request customer to share live location via WhatsApp/SMS

**Technical Solutions:**
⚡ **Power Save Mode** - Turn off power saving to improve GPS accuracy
🛰️ **Location Services** - Ensure location services are enabled for navigation apps
📶 **Network Reset** - Reset network settings if GPS keeps failing
💾 **Update Apps** - Ensure navigation apps are updated to latest version

**Emergency Navigation:**
- Use customer's phone number to call for directions
- Ask nearby shops/residents for landmark-based directions
- Take photos of confusing areas to share with customer
- Use voice calls with customer for real-time guidance

**Performance Protection:**
- GPS/app failures are documented as technical issues
- No penalty for delays due to technical problems
- Immediate technical support available 24/7
- Device replacement available for persistent issues

**Support Contact:**
📞 Technical Support: Available 24/7 in your delivery app
🔧 Report app crashes immediately for faster resolution"""

    def handle_location_difficulty(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle difficulty finding customer's specific location"""
        
        return """🔍 **Location Finding Assistance**

**Smart Search Strategy:**
1. **Call Customer First** - Get real-time directions from customer
2. **Use Landmarks** - Ask customer about nearby shops, buildings, or unique features  
3. **Building Details** - Get specific floor, wing, apartment number
4. **Visual Cues** - Ask customer to describe what you should see (gate color, signboard, etc.)

**Navigation Techniques:**
🏢 **Complex Buildings** - Start from main entrance, check directory/security
🏘️ **Residential Areas** - Look for house number sequence and ask neighbors
🏪 **Commercial Areas** - Use shop names and building signage as reference
🌳 **Rural/Remote Areas** - Use natural landmarks and ask local residents

**Customer Assistance:**
📱 **Live Location** - Request customer to share exact location pin
👋 **Meet Outside** - Ask customer to wait outside/at building entrance  
💡 **Lighting** - Ask customer to turn on lights or flashlight if evening/night
📸 **Photo Share** - Ask customer to send photo of their building/house front

**Local Help:**
🛒 **Ask Shop Owners** - Local businesses usually know the area well
🏘️ **Community Guards** - Security guards can guide you to specific addresses  
🚗 **Other Delivery Agents** - Check if other delivery partners know the location
📞 **Building Manager** - For offices/apartments, contact building management

**Time Management:**
⏱️ **15-Minute Rule** - If location not found in 15 minutes, escalate to support
🔄 **Alternative Meeting** - Suggest meeting at the nearest main road/landmark
📞 **Constant Communication** - Keep customer updated every 5 minutes
🆘 **Support Escalation** - Contact customer service for location assistance

**Performance Protection:**
- Complex location finding time is protected
- No delivery rating impact for difficult addresses  
- Full support for challenging delivery locations
- Area marking for future delivery reference"""

    def handle_traffic_rerouting(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle traffic delays and provide rerouting solutions"""
        
        return """🚦 **Traffic & Rerouting Solutions**

**Immediate Rerouting:**
1. **Open Alternative Route** - Use Waze/Google Maps "Avoid Traffic" option
2. **Check Traffic Updates** - Look for real-time traffic conditions
3. **Ask Locals** - Get local knowledge about best alternate routes
4. **Customer Communication** - Inform customer about delay and new ETA

**Smart Route Planning:**
🛣️ **Main Road Alternatives** - Use parallel roads or inner lanes when available
🚲 **Bike/Scooter Shortcuts** - Take advantage of smaller vehicle access roads
🕐 **Time-Based Routes** - Avoid peak hour main roads, use residential routes
📍 **Landmark Navigation** - Use known landmarks to create alternative paths

**Traffic Solutions:**
⛽ **Fuel-Efficient Routes** - Choose routes that save fuel during traffic
🚥 **Signal Timing** - Learn local traffic light patterns for better timing  
🏍️ **Lane Selection** - Use appropriate lanes for two-wheelers/cars
📱 **Traffic Apps** - Use multiple navigation apps to compare routes

**Customer Communication:**
📞 **Proactive Updates** - Call/message customer about traffic delays immediately
⏰ **Realistic ETA** - Provide updated delivery time considering traffic
🗺️ **Route Explanation** - Explain why taking alternative route (faster/safer)
🎁 **Goodwill Gesture** - Offer discount/future credit for significant delays

**Emergency Options:**
🚇 **Public Transport** - In extreme cases, use metro/bus for faster delivery
🏃 **Walking** - For short distances in heavy traffic, consider walking  
🤝 **Partner Assistance** - Coordinate with nearby delivery partners for help
📞 **Customer Pickup** - Offer customer to collect from nearby accessible location

**Performance Protection:**
- Traffic delays are automatically documented
- GPS tracking shows route taken for verification
- No penalty for delays due to traffic conditions  
- Peak hour bonus consideration for difficult routes

**Pro Tips:**
🔄 Route Learning: Remember good alternative routes for future deliveries
⏰ Peak Hour Strategy: Plan deliveries to avoid worst traffic times
🛣️ Area Expertise: Build knowledge of your delivery area's traffic patterns
📱 Multi-App Strategy: Use 2-3 navigation apps to compare routes"""

    def handle_general_navigation_help(self, query: str, image_data: Optional[str] = None) -> str:
        """General navigation assistance and tips"""
        
        return """🧭 **General Navigation Support**

**Navigation Best Practices:**
1. **Pre-Delivery Check** - Review delivery address before leaving store
2. **Route Planning** - Check traffic conditions and plan optimal route
3. **Backup Plans** - Always have 2-3 route options in mind
4. **Customer Contact** - Save customer number for easy communication

**Essential Tools:**
📱 **Primary Navigation** - Google Maps, Waze, or preferred navigation app
🗺️ **Offline Maps** - Download offline maps for network coverage issues  
📞 **Customer Communication** - WhatsApp, SMS, or calling capability
🔋 **Power Management** - Ensure phone is charged with power bank backup

**Area Knowledge Building:**
🏘️ **Landmark Mapping** - Learn major landmarks, hospitals, schools, malls
🛣️ **Route Alternatives** - Identify 2-3 routes for each common delivery area
🚦 **Traffic Patterns** - Understand peak hours and congestion points  
🏪 **Local Contacts** - Build relationships with local shop owners for directions

**Problem-Solving Approach:**
1. **Stay Calm** - Navigation issues are common and solvable
2. **Communicate Early** - Inform customer about any delays immediately  
3. **Use Multiple Resources** - Combine GPS, local knowledge, and customer help
4. **Document Issues** - Report persistent area problems to support team

**Emergency Contacts:**
📞 **Delivery Support** - 24/7 support for navigation emergencies
🆘 **Technical Help** - App and GPS technical support
👥 **Local Partner Network** - Connect with other delivery agents in area
🏢 **Customer Service** - Escalation support for complex delivery issues

**Performance Optimization:**
⭐ **Delivery Rating** - Good navigation leads to better customer ratings
⏱️ **Time Management** - Efficient routes increase daily delivery capacity  
💰 **Earnings Boost** - Faster deliveries mean more orders per day
🎯 **Area Expertise** - Specialized area knowledge leads to premium assignments

**Remember:** Every delivery is a learning opportunity to improve your navigation skills!"""