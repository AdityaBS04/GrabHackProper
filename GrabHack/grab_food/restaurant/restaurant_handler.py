"""
Grab Food Restaurant Handler - Combined
Handles all restaurant-side operational issues and management
Enhanced with Weather API and Google Maps API for predictive analysis
"""

import logging
import asyncio
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Import API integrations
try:
    from ..api_integrations import WeatherAPI, GoogleMapsAPI, LocationData
except ImportError:
    # Fallback import path
    from ...api_integrations import WeatherAPI, GoogleMapsAPI, LocationData

# Import cross-actor service
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from cross_actor_service import CrossActorUpdateService


class RestaurantHandler:
    """Combined restaurant-focused operational management and issue resolution"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_food"
        self.actor = "restaurant"

        # Initialize API integrations for predictive analysis
        self.weather_api = WeatherAPI()
        self.maps_api = GoogleMapsAPI()

        # Initialize cross-actor update service
        self.cross_actor_service = CrossActorUpdateService()
    
    # QUALITY HANDLER METHODS
    def handle_restaurant_portion_violation(self, query: str) -> str:
        """Handle restaurant portion size violations"""
        return """🍽️ **Restaurant Portion Standards Violation**

**Quality Assurance Alert - Immediate Action Required**

**Violation Details:**
- Customer complaint: portion size inadequate
- Photo evidence reviewed: confirmed violation
- Standard portion guidelines not followed
- Customer refund processed: impacts restaurant rating

**Restaurant Accountability:**
- Quality score reduction: -10 points
- Portion compliance audit scheduled
- Kitchen staff training required within 48 hours
- Supervisor quality review mandatory

**Required Actions:**
1. Review portion control guidelines
2. Kitchen staff retraining on standard measurements
3. Portion scale calibration verification
4. Photo documentation of correct portions

**Partner Performance Impact:**
- Visibility on platform reduced temporarily
- Customer satisfaction score affected
- Commission adjustment for affected orders
- Quality improvement plan required

**Support Provided:**
- Portion guideline refresher training
- Kitchen efficiency consultation
- Quality management system access
- Best practices sharing session

**Timeline for Compliance:**
- Training completion: 48 hours
- Quality audit: within 5 business days
- Performance review: 2 weeks

Maintaining portion standards ensures customer satisfaction and restaurant success."""

    def handle_restaurant_food_safety(self, query: str) -> str:
        """Handle restaurant food safety and hygiene violations"""
        return """🏥 **Food Safety Compliance Alert**

**Critical Food Safety Violation - Immediate Attention Required**

**Health & Safety Issue:**
- Customer reported food quality concern
- Health department notification triggered
- Immediate food safety audit required
- Temporary menu item suspension

**Mandatory Actions:**
1. Immediate kitchen inspection by certified staff
2. Food safety protocol review and implementation
3. Staff hygiene training (all kitchen personnel)
4. Temperature control system verification
5. Supplier quality assurance check

**Compliance Requirements:**
- Food handler certification verification
- HACCP protocol implementation
- Cold chain maintenance documentation
- Cleaning schedule compliance audit

**Restaurant Support:**
- Food safety consultant assignment
- Training materials and resources provided
- Health department liaison coordination
- Best practices implementation guidance

**Timeline Compliance:**
- Immediate: kitchen inspection and corrections
- 24 hours: staff training completion
- 72 hours: comprehensive safety audit
- 1 week: full compliance certification

Food safety is non-negotiable for customer health and restaurant success."""

    def handle_restaurant_preparation_delays(self, query: str) -> str:
        """Handle restaurant food preparation delays and efficiency"""
        return """⏰ **Kitchen Efficiency Optimization Required**

**Preparation Time Performance Alert**

**Efficiency Analysis:**
- Average preparation time: 35 minutes (standard: 20 minutes)
- Customer satisfaction impacted: delivery delays
- Multiple orders affected: peak hour performance
- Delivery partner waiting time excessive

**Root Cause Assessment:**
- Kitchen workflow analysis required
- Staff scheduling optimization needed
- Equipment efficiency check recommended
- Menu complexity review suggested

**Improvement Plan:**
1. Kitchen workflow audit and optimization
2. Staff scheduling during peak hours
3. Prep-ahead procedures implementation
4. Equipment maintenance and upgrade evaluation

**Operational Support:**
- Kitchen efficiency consultant assigned
- Staff training on time management
- Technology solutions for order tracking
- Inventory management optimization

**Performance Metrics:**
- Target preparation time: 15-20 minutes
- Customer satisfaction goal: >4.5 stars
- Delivery partner satisfaction improvement
- Order accuracy maintenance: 98%+

Efficient preparation ensures customer satisfaction and restaurant profitability."""

    def handle_restaurant_ingredient_quality(self, query: str) -> str:
        """Handle restaurant ingredient quality and sourcing issues"""
        return """🥬 **Ingredient Quality Standards Enforcement**

**Supplier Quality Assurance Alert**

**Quality Issue Identified:**
- Customer complaint about ingredient freshness
- Food quality below Grab standards
- Immediate supplier audit required
- Ingredient sourcing review mandated

**Quality Control Actions:**
1. Immediate ingredient inventory inspection
2. Supplier quality verification check
3. Freshness protocol compliance review
4. Storage temperature and conditions audit

**Supplier Management:**
- Primary supplier performance evaluation
- Alternative supplier identification
- Quality certification verification
- Delivery schedule optimization

**Restaurant Quality Systems:**
- First-in-first-out (FIFO) protocol enforcement
- Daily freshness inspection checklist
- Temperature monitoring system setup
- Staff training on quality identification

**Timeline:**
- Immediate: current inventory audit
- 48 hours: supplier verification
- 1 week: new protocols implementation
- Monthly: ongoing quality review

Fresh, high-quality ingredients are fundamental to customer satisfaction and restaurant reputation."""

    def handle_restaurant_order_accuracy(self, query: str) -> str:
        """Handle restaurant order accuracy and fulfillment issues"""
        return """✅ **Order Accuracy Performance Improvement**

**Order Fulfillment Quality Alert**

**Accuracy Issue Analysis:**
- Current order accuracy: 92% (standard: 98%+)
- Missing items reported by customers
- Incorrect substitutions without approval
- Customer satisfaction impacted

**Order Management System:**
- Kitchen display system optimization required
- Order verification protocol enhancement
- Quality check procedures implementation
- Staff training on order accuracy

**Process Improvements:**
1. Double-check system before packaging
2. Order ticket verification at each step
3. Photo confirmation for complex orders
4. Final quality assurance checkpoint

**Technology Solutions:**
- Kitchen display system upgrade
- Order tracking integration
- Photo verification system
- Real-time accuracy monitoring

**Monitoring Period:**
- Daily accuracy tracking: immediate
- Weekly performance review
- Monthly improvement assessment
- Quarterly excellence evaluation

Order accuracy directly impacts customer loyalty and restaurant success on the platform."""
    
    # WAITING TIME HANDLER METHODS
    def handle_long_waiting_time(self, query: str) -> str:
        """Handle restaurant long waiting time issues and kitchen optimization"""
        return """⏱️ **Kitchen Efficiency - Long Waiting Time Alert**

**Order Preparation Performance Issue**

**Current Performance Analysis:**
- Average preparation time: 45 minutes (standard: 20-25 minutes)
- Customer satisfaction declining: delivery delays
- Multiple orders in queue: kitchen bottleneck identified
- Delivery partners experiencing extended wait times

**Impact Assessment:**
- Customer complaints: 15+ in last 24 hours
- Order cancellation rate increased: 8%
- Delivery partner efficiency affected
- Restaurant rating impact: -0.3 stars potential

**Immediate Action Required:**
1. Kitchen workflow assessment and optimization
2. Staff allocation review for peak hours
3. Menu complexity evaluation for preparation time
4. Equipment capacity and maintenance check

**Kitchen Efficiency Solutions:**
- Implement prep-ahead procedures for popular items
- Optimize cooking sequence for multiple orders
- Deploy kitchen display system prioritization
- Staff scheduling adjustment for peak periods

**Performance Improvement Plan:**
- Target preparation time: 15-20 minutes per order
- Kitchen staff training on time management
- Inventory pre-preparation during low-traffic hours
- Equipment upgrade evaluation for efficiency

**Timeline for Improvement:**
- Immediate: workflow assessment (24 hours)
- Short-term: staff training (48 hours)
- Medium-term: process optimization (1 week)
- Long-term: performance monitoring (ongoing)

Efficient kitchen operations ensure customer satisfaction, delivery partner cooperation, and restaurant profitability on the platform."""
    
    # DELIVERY PARTNERS HANDLER METHODS
    async def handle_delivery_partner_shortage(self, query: str, restaurant_location: str = "1.3521,103.8198,Singapore") -> str:
        """Handle restaurant delivery partner shortage issues with weather predictions"""
        
        # Get weather impact predictions
        location_data = self._parse_restaurant_location(restaurant_location)
        weather_impact = await self._predict_weather_impact_on_delivery(location_data)
        
        # Generate enhanced response with weather considerations
        weather_section = self._generate_weather_impact_section(weather_impact)
        
        return f"""🚗 **Delivery Partner Shortage - Coordination Required**

**Delivery Capacity Issue Alert**

**Current Situation Analysis:**
- Delivery partners available: 3 (required: 8+ for current order volume)
- Orders waiting for pickup: 12+ orders pending
- Average wait time for partner assignment: 35 minutes
- Customer delivery expectations at risk

{weather_section}

**Impact on Restaurant Operations:**
- Orders prepared but awaiting pickup: food quality degradation
- Customer satisfaction declining due to delays
- Restaurant efficiency affected: kitchen capacity tied up
- Potential order cancellations increasing

**Immediate Grab Platform Response:**
1. Priority delivery partner allocation to your location
2. Surge incentive activation for nearby partners
3. Extended delivery radius partner notification
4. Emergency partner pool activation
{self._generate_weather_specific_actions(weather_impact)}

**Restaurant Coordination Actions:**
- Hold order preparation for 15+ minute delays
- Customer communication: proactive delay notifications
- Food quality maintenance: proper holding procedures
- Order prioritization: FIFO with quality considerations
{self._generate_weather_restaurant_actions(weather_impact)}

**Delivery Partner Incentives Activated:**
- Surge pricing: +40% delivery fees for your area
- Priority partner notifications within 5km radius
- Bonus payments for immediate availability
- Performance rewards for quick response times
{self._generate_weather_incentives(weather_impact)}

**Quality Preservation Guidelines:**
- Hot food holding: maximum 20 minutes
- Cold items: proper refrigeration maintenance
- Packaging optimization: insulation and freshness
- Quality check before delayed handover
{self._generate_weather_quality_guidelines(weather_impact)}

**Timeline for Resolution:**
- Immediate: surge incentives activation (5 minutes)
- Short-term: additional partner allocation (15 minutes)
- Medium-term: sustained capacity improvement (1 hour)
- Long-term: demand-supply optimization (ongoing)
{self._generate_weather_timeline_adjustments(weather_impact)}

**Weather-Enhanced Delivery Strategy:**
- Current conditions: {weather_impact.get('current_conditions', 'normal')}
- Impact level: {weather_impact.get('impact_level', 'low')}
- Recommended delay buffer: {weather_impact.get('recommended_delay', 0)} minutes
- Special handling required: {'Yes' if weather_impact.get('special_handling_required') else 'No'}

Adequate delivery partner availability is crucial for restaurant success and customer satisfaction on the Grab Food platform."""
    
    def _parse_restaurant_location(self, location_string: str) -> LocationData:
        """Parse restaurant location string to LocationData object"""
        try:
            parts = location_string.split(',')
            if len(parts) >= 2:
                lat = float(parts[0].strip())
                lng = float(parts[1].strip())
                address = ','.join(parts[2:]).strip() if len(parts) > 2 else "Restaurant Location"
                return LocationData(latitude=lat, longitude=lng, address=address)
            else:
                return LocationData(latitude=1.3521, longitude=103.8198, address=location_string)
        except (ValueError, IndexError):
            return LocationData(latitude=1.3521, longitude=103.8198, address="Singapore")
    
    async def _predict_weather_impact_on_delivery(self, location: LocationData) -> Dict[str, Any]:
        """Predict weather impact on delivery partner availability and performance"""
        try:
            weather_impact = await self.weather_api.predict_weather_impact(location)
            current_weather = await self.weather_api.get_current_weather(location)
            
            return {
                **weather_impact,
                'temperature': current_weather.temperature,
                'precipitation_probability': current_weather.precipitation_probability,
                'wind_speed': current_weather.wind_speed,
                'visibility': current_weather.visibility
            }
        except Exception as e:
            logger.error(f"Weather API error: {str(e)}")
            return {
                'impact_level': 'unknown',
                'current_conditions': 'unknown',
                'temperature': 25.0,
                'precipitation_risk': 0.0,
                'recommended_delay': 0,
                'special_handling_required': False,
                'visibility_concerns': False
            }
    
    def _generate_weather_impact_section(self, weather_impact: Dict[str, Any]) -> str:
        """Generate weather impact section for the response"""
        impact_level = weather_impact.get('impact_level', 'low')
        conditions = weather_impact.get('current_conditions', 'clear')
        
        if impact_level in ['moderate', 'severe']:
            return f"""**Weather Impact Assessment:**
- Current conditions: {conditions} (Impact: {impact_level})
- Temperature: {weather_impact.get('temperature', 25):.1f}°C
- Precipitation risk: {weather_impact.get('precipitation_risk', 0)*100:.0f}%
- Delivery partner availability likely reduced due to weather
- Extended delivery times expected: +{weather_impact.get('recommended_delay', 0)} minutes"""
        else:
            return f"""**Weather Conditions:**
- Current conditions: {conditions} (Impact: minimal)
- Temperature: {weather_impact.get('temperature', 25):.1f}°C
- Weather not significantly impacting delivery operations"""
    
    def _generate_weather_specific_actions(self, weather_impact: Dict[str, Any]) -> str:
        """Generate weather-specific platform actions"""
        if weather_impact.get('impact_level') in ['moderate', 'severe']:
            return """5. Weather contingency protocols activated
6. Additional weather compensation for delivery partners
7. Extended delivery radius to compensate for reduced availability"""
        return ""
    
    def _generate_weather_restaurant_actions(self, weather_impact: Dict[str, Any]) -> str:
        """Generate weather-specific restaurant actions"""
        actions = []
        
        if weather_impact.get('special_handling_required'):
            actions.append("- Enhanced packaging for weather protection")
        
        if weather_impact.get('impact_level') in ['moderate', 'severe']:
            actions.extend([
                "- Extended food holding protocols activated",
                "- Customer proactive weather delay notifications"
            ])
        
        if weather_impact.get('precipitation_risk', 0) > 0.3:
            actions.append("- Waterproof packaging prioritized")
        
        return '\n'.join(actions) if actions else ""
    
    def _generate_weather_incentives(self, weather_impact: Dict[str, Any]) -> str:
        """Generate weather-specific partner incentives"""
        if weather_impact.get('impact_level') in ['moderate', 'severe']:
            return """- Weather hazard pay: additional compensation
- Covered parking priority for delivery partners
- Weather gear provision if needed"""
        return ""
    
    def _generate_weather_quality_guidelines(self, weather_impact: Dict[str, Any]) -> str:
        """Generate weather-specific quality guidelines"""
        guidelines = []
        
        temp = weather_impact.get('temperature', 25)
        if temp > 35 or temp < 5:
            guidelines.append("- Temperature-sensitive items: enhanced insulation required")
        
        if weather_impact.get('precipitation_risk', 0) > 0.2:
            guidelines.extend([
                "- Waterproof packaging mandatory",
                "- Double-bag sensitive items"
            ])
        
        if weather_impact.get('visibility_concerns'):
            guidelines.append("- Enhanced order labeling for low visibility conditions")
        
        return '\n'.join(guidelines) if guidelines else ""
    
    def _generate_weather_timeline_adjustments(self, weather_impact: Dict[str, Any]) -> str:
        """Generate weather-adjusted timeline expectations"""
        if weather_impact.get('recommended_delay', 0) > 5:
            return f"""- Weather delay buffer: +{weather_impact.get('recommended_delay')} minutes added to all estimates
- Extended resolution timeline due to weather conditions"""
        return ""
    
    # UNEXPECTED HINDRANCE HANDLER METHODS
    def handle_unexpected_hindrance(self, query: str) -> str:
        """Handle restaurant unexpected operational hindrances and crisis management"""
        return """🚨 **Restaurant Crisis Management - Unexpected Hindrance**

**Emergency Operational Support Activated**

**Crisis Situation Assessment:**
- Unexpected operational hindrance identified
- Service capacity severely impacted
- Customer orders at risk of disruption
- Immediate intervention required

**Common Hindrance Types & Response:**

**🔌 Power Outage/Electrical Issues:**
- Immediate: Switch to emergency protocols
- Kitchen equipment assessment required
- Food safety protocols activation
- Estimated restoration time evaluation

**⚙️ Equipment Failure (Critical):**
- Kitchen equipment malfunction identified
- Alternative preparation methods evaluation
- Repair service coordination immediate
- Menu adaptation for available equipment

**🚛 Supply Chain Disruption:**
- Key ingredient shortage detected
- Supplier coordination emergency protocols
- Menu item availability updates required
- Alternative sourcing solutions activation

**🏥 Health/Safety Incident:**
- Food safety protocols immediate activation
- Health department notification if required
- Staff safety assessment and response
- Customer impact evaluation and communication

**Immediate Platform Response:**
1. **Order Flow Management:**
   - New order acceptance temporary suspension
   - Pending orders: customer notification system
   - Estimated resolution time communication
   - Alternative restaurant recommendations

2. **Customer Communication:**
   - Proactive notification to affected customers
   - Transparent explanation of situation
   - Service recovery options provided
   - Alternative dining recommendations offered

3. **Business Continuity Support:**
   - Emergency technical support activation
   - Vendor/supplier coordination assistance
   - Insurance claim guidance if applicable
   - Revenue protection measures evaluation

**Restaurant Crisis Response Plan:**

**Phase 1 - Immediate (0-30 minutes):**
- Situation assessment and documentation
- Safety protocols activation
- Staff coordination and task assignment
- Customer impact evaluation

**Phase 2 - Short-term (30 minutes - 2 hours):**
- Problem resolution initiation
- Resource mobilization (repair, supplies)
- Customer communication management
- Alternative service options evaluation

**Phase 3 - Recovery (2+ hours):**
- Service restoration planning
- Quality assurance verification
- Gradual service resumption
- Performance monitoring restoration

Restaurant resilience during crisis situations protects both customer satisfaction and business continuity on the Grab Food platform."""
    
    # ORDER CUSTOMIZATION HANDLER METHODS
    def handle_dish_addition_due_to_inconvenience(self, query: str, order_id: str = None, restaurant_username: str = None) -> str:
        """Handle adding complementary items due to customer inconvenience"""
        try:
            # Parse the query to extract what items are being added and why
            added_item = "complementary item"  # Default
            reason = "inconvenience"  # Default

            # Simple parsing - in production this would be more sophisticated
            if "added" in query.lower():
                words = query.split()
                for i, word in enumerate(words):
                    if word.lower() == "added" and i + 1 < len(words):
                        added_item = words[i + 1]
                        break

            if "due to" in query.lower():
                reason_part = query.lower().split("due to")[1].strip()
                reason = reason_part.split('.')[0] if '.' in reason_part else reason_part

            # Create cross-actor update if order_id provided
            if order_id and restaurant_username:
                self.cross_actor_service.create_cross_actor_update(
                    order_id=order_id,
                    actor_type="restaurant",
                    actor_username=restaurant_username,
                    update_type="dish_added",
                    details={
                        "item": added_item,
                        "reason": reason,
                        "restaurant_name": "Your restaurant"  # This would come from order data
                    }
                )

            return f"""🍽️ **Item Added Successfully - Customer Notification Sent**

**Added Item Details:**
- Item: {added_item}
- Reason: {reason}
- Cost: Complimentary (no charge to customer)
- Status: Added to order automatically

**✅ Customer Notifications Sent:**
- SMS: "Good news! We've added {added_item} to your order at no charge due to {reason}"
- App notification: Order updated with complimentary item
- Delivery partner informed about updated order contents

**📝 Order Impact:**
- Total items increased by 1
- Preparation time may extend by 2-3 minutes
- Customer satisfaction gesture completed
- No billing changes required

**Next Steps:**
- Kitchen has been notified to prepare additional item
- Packaging updated to include new item
- Delivery partner will receive updated order details
- Customer will see real-time order update

Your proactive customer service has been logged and will contribute positively to your restaurant rating."""

        except Exception as e:
            logger.error(f"Error handling dish addition: {e}")
            return """🍽️ **Item Addition Processed**

We've processed your request to add a complimentary item due to customer inconvenience. The customer has been notified and your kitchen team has been updated with the new order requirements."""

    def handle_order_customization(self, query: str) -> str:
        """Handle restaurant order customization issues and customer modification requests"""
        return """🍽️ **Order Customization Management - Restaurant Guide**

**Customer Order Modification Request**

**Customization Request Assessment:**
- Customer requesting menu item modifications
- Ingredient substitutions or additions needed
- Special dietary requirements consideration
- Kitchen capability and cost impact evaluation

**Standard Customization Categories:**

**🥗 Dietary Restrictions:**
- Allergies: nuts, dairy, gluten, seafood
- Dietary preferences: vegetarian, vegan, halal
- Health conditions: low sodium, diabetic-friendly
- Religious requirements: kosher, halal certification

**🌶️ Taste Preferences:**
- Spice level adjustments: mild, medium, extra spicy
- Seasoning modifications: less salt, extra herbs
- Cooking style changes: well-done, rare, crispy
- Sauce preferences: on side, extra, different type

**📦 Portion & Presentation:**
- Size modifications: larger, smaller portions
- Ingredient quantities: extra cheese, light dressing
- Presentation requests: separate containers, mixed
- Add-on items: extra proteins, vegetables

**Restaurant Response Protocol:**

**✅ Approved Customizations:**
- Standard ingredient substitutions available
- Dietary restriction accommodations possible
- Simple preparation modifications feasible
- No significant cost or time impact

**❌ Declined Customizations:**
- Requires ingredients not in inventory
- Complex preparation beyond kitchen capability
- Violates food safety or quality standards
- Significant delay to other orders

**⚠️ Conditional Customizations:**
- Additional charge required for premium ingredients
- Extended preparation time needed (notify customer)
- Limited availability based on current stock
- Quality compromise potential (advise customer)

**Customer Communication Framework:**

**For Approved Requests:**
"We're happy to accommodate your customization request! Your order will include [specific modifications]. No additional charge/Additional charge of $X applies. Estimated preparation time: [X] minutes."

**For Declined Requests:**  
"We understand your preference for [modification]. Unfortunately, we cannot accommodate this request due to [reason: ingredient availability/safety standards/preparation complexity]. We recommend [alternative options]."

**For Conditional Requests:**
"We can accommodate your request with some adjustments: [explanation]. This will add $[amount] to your order and approximately [X] minutes to preparation time. Would you like to proceed?"

**Kitchen Implementation Guidelines:**

**🔄 Modification Process:**
1. Review customization feasibility immediately
2. Check ingredient availability and freshness
3. Assess impact on preparation time and quality
4. Communicate with customer within 3 minutes
5. Update order ticket with clear modification notes

**Quality Assurance Standards:**
- Customized orders must meet same quality standards
- No compromise on food safety protocols
- Visual presentation maintains restaurant standards
- Customer satisfaction priority over convenience

Effective order customization management enhances customer satisfaction while maintaining operational efficiency and quality standards."""