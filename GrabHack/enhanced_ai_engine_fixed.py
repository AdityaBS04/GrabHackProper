"""
Enhanced Agentic AI Engine for GrabHack Customer Service
Uses different Groq models based on function requirements:
- Llama-4-Maverick for image processing functions
- Llama-Prompt-Guard for security screening
- GPT-4O-Mini for text-only functions
"""

import os
import json
import logging
import base64
import re
import unicodedata
from groq import Groq
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class EnhancedAgenticAIEngine:
    """Enhanced AI Engine with image processing and security screening"""
    
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.text_model = "openai/gpt-oss-120b"  # For resolving issues
        self.image_model = "meta-llama/llama-4-maverick-17b-128e-instruct"  # For image processing 
        self.security_model = "meta-llama/llama-prompt-guard-2-86m"  # For security screening
        self.orchestrator_model = "llama-3.3-70b-versatile"  # For orchestration
        
        # Define which functions require images
        self.image_required_functions = {
            # Grab Food Customer functions that need image proof
            'handle_missing_items': True,  # Photo of received items
            'handle_wrong_item': True,    # Photo of wrong item
            'handle_quality_issues': True, # Photo of poor quality food
            'handle_spillage': True,      # Photo of spilled/damaged items
            'handle_package_tampering': True, # Photo of tampered package
            'handle_driver_misconduct': True,  # Photo of evidence
            
            # Grab Food Delivery Agent functions that need image proof
            'handle_navigation_issues': False,  # Navigation issues don't require images - use Google Maps links
            'handle_vehicle_breakdown': True,   # Photo of vehicle issue
            'handle_safety_incident': True,     # Photo of safety concern
            'handle_traffic_violation': True,   # Photo of traffic issue
            
            # Grab Food Restaurant functions that need image proof
            'handle_wrong_order_prep': True,    # Photo of wrong prepared order
            'handle_food_safety_violation': True, # Photo of safety violations
            
            # Grab Cabs Customer functions that need image proof
            'handle_driver_behavior_issues': True,  # Photo of misconduct
            'handle_vehicle_condition': True,       # Photo of dirty/damaged vehicle
            'handle_safety_concerns': True,         # Photo of safety issues
            
            # Grab Cabs Driver functions that need image proof
            'handle_passenger_misconduct': True,    # Photo of passenger issues
            'handle_vehicle_damage': True,         # Photo of damage caused by passenger
            
            # Grab Mart Customer functions that need image proof
            'handle_quality_issues': True,    # Photo of poor quality products
            'handle_missing_items': True,     # Photo of received items vs ordered
            'handle_wrong_items': True,       # Photo of wrong items received
            'handle_expired_damaged_items': True, # Photo of expired/damaged items
            
            # Grab Mart Dark House functions that need image proof
            'handle_product_quality_control': True, # Photo of quality issues
            'handle_temperature_control': True,     # Photo of temperature violations
            
            # Functions that don't require images (text-only)
            'handle_substitution_issues': False,  # Text-only - preference issues
            'handle_double_charge': False,
            'handle_failed_payment_money_deducted': False, 
            'handle_refund_delays': False,
            'handle_payment_method_issues': False,
            'handle_app_technical_issues': False,
            'handle_long_wait_times': False,
            'handle_delivery_delays': False,
            'handle_communication_issues': False,
            'handle_promo_discount_issues': False,
            'handle_account_issues': False,
            'handle_service_availability': False,
            'handle_booking_cancellation': False,
            'handle_surge_pricing': False,
            'handle_eta_accuracy': False,
            'handle_route_optimization': False,
            'handle_order_modification': False,
            'handle_customer_preferences': False,
            
            # Add image-required functions
            'handle_partial_delivery': True,  # Photo of partial delivery
            'handle_temperature_issues': True  # Photo of temperature damage
        }
        
    def _clean_unicode_response(self, text: str) -> str:
        """Clean Unicode characters that may cause encoding issues"""
        if not text:
            return text
        
        # Remove problematic Unicode characters
        text = text.replace('\u202f', ' ')  # Narrow no-break space
        text = text.replace('\u2060', '')   # Word joiner
        text = text.replace('\u00a0', ' ')  # Non-breaking space
        
        # Remove emojis and special symbols
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        
        # Normalize remaining Unicode
        text = unicodedata.normalize('NFKD', text)
        text = text.encode('ascii', 'ignore').decode('ascii')
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _handle_navigation_with_maps(self, user_query: str) -> str:
        """Handle navigation issues using practical navigation handler with Google Maps"""
        # For now, use the fallback method which works reliably
        return self._generate_enhanced_navigation_response(user_query)
    
    def _generate_enhanced_navigation_response(self, user_query: str) -> str:
        """Generate enhanced navigation response with intelligent routing"""
        
        # Extract locations from query or use defaults
        current_location = self._extract_location_from_query(user_query, "current") or "Sapna Book Stores, Jayanagar, Bangalore"
        destination = self._extract_location_from_query(user_query, "destination") or "South End Circle Metro, Bangalore"
        
        # Generate navigation links
        import urllib.parse
        current_encoded = urllib.parse.quote(current_location)
        dest_encoded = urllib.parse.quote(destination)
        maps_url = f"https://www.google.com/maps/dir/{current_encoded}/{dest_encoded}/"
        waze_url = f"https://waze.com/ul?q={dest_encoded}&navigate=yes"
        
        # Determine response type based on query
        query_lower = user_query.lower()
        
        if any(word in query_lower for word in ['stuck', 'traffic', 'reroute', 'alternative']):
            response_type = "Traffic Rerouting"
            icon = "🚦"
            specific_help = """**Traffic Solutions:**
- Click Google Maps link for real-time traffic avoidance
- Waze often finds faster routes during traffic jams
- Inform customer about delay and new ETA
- Consider motorcycle/bicycle lanes if available"""
        
        elif any(word in query_lower for word in ['address', 'find', 'location', 'lost']):
            response_type = "Address & Location Help"  
            icon = "🏠"
            specific_help = """**Address Resolution:**
- Use Google Maps link to verify exact location
- Call customer to confirm complete address
- Ask for nearby landmarks or building details
- Request customer to share live location if needed"""
        
        elif any(word in query_lower for word in ['gps', 'navigation', 'maps', 'crash']):
            response_type = "GPS & Navigation Fix"
            icon = "📱"
            specific_help = """**Technical Solutions:**
- Navigation links work even if your GPS app crashed
- Restart your phone to fix most GPS issues
- Use browser-based navigation as backup
- Download offline maps for poor network areas"""
        
        else:
            response_type = "General Navigation"
            icon = "🧭"
            specific_help = """**Navigation Tips:**
- Click Google Maps for turn-by-turn directions
- Save customer number for easy communication  
- Check traffic conditions before leaving
- Keep phone charged with power bank backup"""
        
        return f"""{icon} **{response_type}**

**📍 Navigation Links (Click to Open):**

🗺️ **Google Maps:** https://www.google.com/maps/dir/{current_encoded}/{dest_encoded}/

🚗 **Waze Alternative:** https://waze.com/ul?q={dest_encoded}&navigate=yes

**🎯 Route Information:**
- **From:** {current_location}
- **To:** {destination}

{specific_help}

**📞 Customer Communication:**
"Hi! I'm navigating to your location now. Your delivery is on the way!"

**⚡ Emergency Options:**
- Call customer for real-time directions
- Ask local shopkeepers for help
- Contact delivery support: Available 24/7

**Issue Details:** {user_query}"""
    
    def _extract_location_from_query(self, query: str, location_type: str) -> str:
        """Extract current location or destination from user query"""
        import re
        
        if location_type == "current":
            patterns = [
                r'(?:from|currently at|at|starting from|i am at)\s+([^,\n]+(?:,\s*[^,\n]+)*)',
                r'(?:my location is|im at)\s+([^,\n]+(?:,\s*[^,\n]+)*)'
            ]
        else:  # destination
            patterns = [
                r'(?:to|going to|destination|deliver to)\s+([^,\n]+(?:,\s*[^,\n]+)*)',
                r'(?:customer at|address is|location is)\s+([^,\n]+(?:,\s*[^,\n]+)*)'
            ]
        
        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_order_id_from_query(self, user_query: str) -> Optional[str]:
        """Extract order ID from user query if mentioned"""
        import re
        
        # Look for patterns like "order GF001", "GF002", "order #GF001", etc.
        patterns = [
            r'\b(GF\d{3})\b',  # GF followed by 3 digits
            r'\b(GM\d{3})\b',  # GM followed by 3 digits  
            r'\b(GC\d{3})\b',  # GC followed by 3 digits
            r'order\s*#?\s*([A-Z]{2}\d{3})',  # "order GF001" or "order #GF001"
            r'#([A-Z]{2}\d{3})',  # "#GF001"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, user_query, re.IGNORECASE)
            if match:
                order_id = match.group(1).upper()
                print(f"DEBUG: Extracted order ID '{order_id}' from query: '{user_query}'")
                return order_id
        
        print(f"DEBUG: No order ID found in query: '{user_query}'")
        return None
    
    def _is_food_quality_issue(self, function_name: str, service: str) -> bool:
        """Check if this is a food quality related complaint that requires order status validation"""
        if service != 'grab_food':
            return False
            
        food_quality_issues = {
            'handle_quality_issues',  # Main food quality issue
            'handle_wrong_item',      # Wrong item received
            'handle_missing_items',   # Missing items
            'handle_spillage',        # Spilled/damaged food
            'handle_temperature_issues'  # Temperature problems
        }
        
        return function_name in food_quality_issues
    
    def _check_order_status_for_food_quality(self, username: str, service: str, function_name: str, user_query: str = "", specific_order_id: str = None) -> Optional[str]:
        """Check order status before accepting quality complaints for all services"""
        import sqlite3
        import os
        import re
        
        try:
            # Use the correct database path - try multiple possible paths
            current_dir = os.getcwd()
            database_paths = [
                'grabhack.db',                    # If running from GrabHack directory
                '../grabhack.db',                 # If running from test directory  
                'GrabHack/grabhack.db',          # If running from parent directory
                os.path.join(os.path.dirname(__file__), 'grabhack.db'),  # Relative to this file
                'grab_service.db',               # Fallback
                'GrabHack/grab_service.db'       # Fallback
            ]
            DATABASE_PATH = None
            
            for path in database_paths:
                if os.path.exists(path):
                    DATABASE_PATH = path
                    print(f"DEBUG: Using database at {path}")
                    break
            
            if not DATABASE_PATH:
                print("DEBUG: No database found, allowing complaint to proceed")
                return None
            
            # Skip validation if no username provided (anonymous users)
            if not username or username == 'anonymous':
                return None
                
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # First, check if a specific order ID was passed from the session context
            if not specific_order_id:
                # If no specific order ID provided, try to extract from the user query
                specific_order_id = self._extract_order_id_from_query(user_query)
                print(f"DEBUG: Extracted order ID from query: {specific_order_id}")
            else:
                print(f"DEBUG: Using specific order ID from session: {specific_order_id}")
            
            if specific_order_id:
                # Check the specific order mentioned by the user
                cursor.execute('''
                    SELECT id, status, details FROM orders 
                    WHERE id = ? AND service = ? AND username = ? AND user_type = 'customer'
                ''', (specific_order_id, service, username))
                
                order = cursor.fetchone()
                if order:
                    order_id, status, details = order
                    print(f"DEBUG: Checking specific order {order_id} with status {status}")
                else:
                    print(f"DEBUG: Specific order {specific_order_id} not found for user {username}")
                    print(f"DEBUG: Query was: SELECT id, status, details FROM orders WHERE id = {specific_order_id} AND service = {service} AND username = {username} AND user_type = 'customer'")
                    conn.close()
                    return None
            else:
                # No specific order mentioned - get the most recent order for this service
                print(f"DEBUG: No specific order ID found, checking most recent {service} order")
                cursor.execute('''
                    SELECT id, status, details FROM orders 
                    WHERE service = ? AND username = ? AND user_type = 'customer'
                    ORDER BY date DESC 
                    LIMIT 1
                ''', (service, username))
                
                order = cursor.fetchone()
                if not order:
                    # No orders found for this service - allow complaint to proceed
                    print(f"DEBUG: No {service} orders found for {username}")
                    conn.close()
                    return None
                
                order_id, status, details = order
                print(f"DEBUG: Most recent {service} order {order_id} has status {status}")
            
            conn.close()
            
            # Check if this specific order is still in progress (not delivered yet)
            in_progress_statuses = {'in_progress', 'preparing', 'assigned', 'picking', 'on_the_way', 'active'}
            
            if status in in_progress_statuses:
                issue_type = function_name.replace('handle_', '').replace('_', ' ')
                service_name = service.replace('_', ' ').title()
                
                return self._clean_unicode_response(f"""
I understand you're concerned about the {issue_type}, but I can see that your {service_name} order (#{order_id}) is still {status} and hasn't been completed yet.

Since your order is still being processed and on its way to you, I recommend waiting until you receive your order to assess the quality. 

If you have other concerns about your current order (like delivery time, location issues, or payment problems), I'd be happy to help with those instead.

Once your order is completed, if there are any quality issues, please don't hesitate to reach out and I'll make sure to resolve them immediately with appropriate compensation.

Is there anything else I can help you with regarding your current order?
                """.strip())
            
            # Order is completed or delivered, allow quality complaint to proceed
            print(f"DEBUG: Order {order_id} is {status}, allowing quality complaint to proceed")
            return None
            
        except Exception as e:
            logger.error(f"Error checking order status: {e}")
            # If there's an error, allow complaint to proceed rather than block it
            return None
        
    
    def process_complaint(self, function_name: str, user_query: str, service: str, 
                         user_type: str, image_data: Optional[str] = None, username: Optional[str] = None) -> str:
        """Main method to process complaint using appropriate AI model"""
        
        try:
            print(f"DEBUG: process_complaint called with function_name={function_name}, service={service}, user_type={user_type}, username={username}")
            
            # Step 1: Check order status for quality issues (for grab_food) or any post-delivery complaints (for all services)
            if user_type == 'customer':
                # Check for grab_food quality issues OR any quality-related complaint for other services
                should_check_order_status = (
                    self._is_food_quality_issue(function_name, service) or  # Grab Food quality issues
                    (service in ['grab_cabs', 'grab_mart'] and 'quality' in function_name.lower()) or  # Other service quality issues
                    'missing' in function_name.lower() or 'wrong' in function_name.lower()  # Missing/wrong items for any service
                )
                
                if should_check_order_status:
                    print(f"DEBUG: This is a quality/post-delivery issue for customer, checking order status...")
                    order_status_response = self._check_order_status_for_food_quality(username, service, function_name, user_query)
                    if order_status_response:
                        print(f"DEBUG: Order status validation blocked the request")
                        return order_status_response
                    print(f"DEBUG: Order status validation passed, proceeding with complaint")
            
            # Step 2: Security screening if image is provided
            if image_data:
                if not self._screen_image_security(image_data):
                    return self._clean_unicode_response("Content Security Alert - The uploaded image contains inappropriate content and cannot be processed. Please upload a relevant image related to your service issue.")
            
            # Step 3: Determine if function requires image
            requires_image = self.image_required_functions.get(function_name, False)
            
            if requires_image and not image_data:
                return self._request_image_upload(function_name, service, user_type)
            
            # Step 4: Process with appropriate model
            if requires_image and image_data:
                return self._process_with_image_model(function_name, user_query, service, user_type, image_data)
            else:
                return self._process_with_text_model(function_name, user_query, service, user_type)
                
        except Exception as e:
            logger.error(f"Error processing complaint: {e}")
            return self._generate_fallback_response(function_name, user_query, service, user_type)
    
    def _screen_image_security(self, image_data: str) -> bool:
        """Screen image for inappropriate content using Llama-Prompt-Guard"""
        try:
            prompt = f"""
            Analyze this image for appropriateness in a customer service context. 
            Determine if the image contains:
            1. Relevant service-related content (food, vehicles, packages, etc.)
            2. Any inappropriate, explicit, or harmful content
            3. Personal information that should be protected
            
            Respond with only: SAFE or UNSAFE
            """
            
            response = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                            }
                        ]
                    }
                ],
                model=self.security_model,
                temperature=0.0,
                max_tokens=10
            )
            
            result = response.choices[0].message.content.strip().upper()
            return result == "SAFE"
            
        except Exception as e:
            logger.error(f"Security screening error: {e}")
            # Default to safe if screening fails
            return True
    
    def _process_with_image_model(self, function_name: str, user_query: str, 
                                 service: str, user_type: str, image_data: str) -> str:
        """Process complaint with image using conversational approach with fraud detection"""
        
        context = self._get_function_context(function_name, service, user_type)
        
        prompt = f"""
        You are a conversational {service.replace('_', ' ').title()} customer service agent. 
        You need to analyze the customer's image and have a conversation with them to verify their complaint.

        CUSTOMER ISSUE: {function_name.replace('_', ' ').title()}
        CUSTOMER COMPLAINT: {user_query}
        
        IMPORTANT INSTRUCTIONS:
        1. First, describe what you see in the image in a friendly conversational tone
        2. Ask the customer to clarify or confirm details if something seems unclear
        3. If the image matches their complaint and seems genuine, proceed to help them
        4. If the image doesn't match their complaint or seems suspicious, ask more questions
        5. If you suspect fraud or the complaint seems invalid, politely suggest connecting with human support
        6. Be conversational, not formal - talk like a helpful customer service person
        
        CONVERSATION FLOW:
        - "I can see in your image that [describe what you see]..."
        - If genuine: "I understand your frustration. Let me help you resolve this..."
        - If suspicious: "I notice [concern]. Could you please clarify [specific question]?"
        - If fraud suspected: "I'd like to connect you with our specialized support team who can better assist you with this."
        
        Respond as if you're talking directly to the customer. Be helpful but also protective of the company's interests.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                            }
                        ]
                    }
                ],
                model=self.image_model,
                temperature=0.3,
                max_tokens=1000
            )
            
            return self._clean_unicode_response(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Image processing error: {e}")
            return self._process_with_text_model(function_name, user_query, service, user_type)
    
    def _process_with_text_model(self, function_name: str, user_query: str,
                                service: str, user_type: str) -> str:
        """Process text-only complaint using GPT-4O-Mini"""
        
        # Special handling for navigation issues - use practical navigation handler
        if function_name == 'handle_navigation_issues' and service == 'grab_food' and user_type == 'delivery_agent':
            return self._handle_navigation_with_maps(user_query)
        
        context = self._get_function_context(function_name, service, user_type)
        
        prompt = f"""
        You are an expert {service.replace('_', ' ').title()} customer service agent.

        FUNCTION: {function_name.replace('_', ' ').title()}
        SERVICE: {service.replace('_', ' ').title()}
        USER TYPE: {user_type.replace('_', ' ').title()}
        
        CONTEXT: {context}
        
        USER COMPLAINT: {user_query}
        
        Provide a comprehensive, personalized resolution that:
        
        1. **Acknowledgment**: Show empathy and understanding
        2. **Immediate Actions**: Specific steps being taken now
        3. **Compensation**: Appropriate compensation for this specific issue
        4. **Prevention**: Measures to prevent recurrence  
        5. **Timeline**: Clear expectations for resolution
        
        Make it specific to this exact situation, not generic.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.text_model,
                temperature=0.3,
                max_tokens=800
            )
            
            return self._clean_unicode_response(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Text processing error: {e}")
            return self._generate_fallback_response(function_name, user_query, service, user_type)
    
    def _request_image_upload(self, function_name: str, service: str, user_type: str) -> str:
        """Request image upload for functions that require visual evidence"""
        
        image_requests = {
            'handle_missing_items': "Please upload a photo of the items you received so we can verify what's missing and process your refund accordingly.",
            'handle_wrong_item': "Please upload a photo of the incorrect item you received so we can arrange an immediate exchange and investigate with the restaurant.",
            'handle_quality_issues': "Please upload a photo of the food quality issue so we can assess the severity and provide appropriate compensation while ensuring food safety standards.",
            'handle_spillage': "Please upload a photo of the spilled/damaged items so we can document the issue and provide full compensation plus quality assurance measures.",
            'handle_package_tampering': "Please upload a photo of the tampered package so we can investigate this security concern and ensure your safety.",
            'handle_vehicle_breakdown': "Please upload a photo of the vehicle issue so we can provide immediate roadside assistance and document for maintenance support.",
            'handle_safety_accident_enroute': "Please upload a photo of the incident (if safe to do so) so we can provide immediate support and document for safety review.",
            'handle_vehicle_condition': "Please upload a photo of the vehicle condition issue so we can review with the driver partner and ensure your safety standards.",
            'handle_safety_incident': "Please upload a photo of the safety concern (if safe to do so) so we can take immediate action and prevent future incidents.",
            'handle_vehicle_standards': "Please upload a photo of the vehicle maintenance issue so we can provide guidance and ensure compliance with safety standards.",
            'handle_expired_damaged_items': "Please upload a photo of the expired/damaged products so we can process immediate replacement and investigate with our suppliers.",
            'handle_product_quality_control': "Please upload a photo of the quality issue so we can enhance our inspection procedures and provide appropriate compensation.",
            'handle_temperature_control': "Please upload a photo showing the temperature control issue so we can address this critical food safety concern immediately."
        }
        
        specific_request = image_requests.get(function_name, 
            "Please upload a photo related to your issue so we can provide the best possible resolution.")
        
        return f"""📸 **Image Required for Resolution**

**To provide you with the most accurate and comprehensive solution, we need visual evidence of your {service.replace('_', ' ').title()} issue.**

**Why we need this:**
{specific_request}

**What to include in your photo:**
- Clear view of the issue you're reporting
- Any relevant details that support your complaint
- Ensure the image is well-lit and focused

**Your privacy is protected:**
- Images are securely processed and used only for resolution
- No personal information will be stored or shared
- All images are deleted after issue resolution

Please upload your image and resubmit your complaint for immediate processing."""

    def _get_function_context(self, function_name: str, service: str, user_type: str) -> str:
        """Get specific context for each function to guide AI reasoning"""
        
        function_contexts = {
            # Grab Food Customer Image Functions
            'handle_missing_items': f"Missing items from {service} orders require visual verification for accurate refund processing. Standard compensation: full refund + redelivery + $3-15 credit based on order value. Restaurant accountability measures apply.",
            
            'handle_wrong_item': f"Wrong item delivery requires photo evidence for exchange processing. Policy: customer keeps wrong item + receives correct item + $5-20 compensation. Restaurant training implications considered.",
            
            'handle_quality_issues': f"Food quality issues require visual assessment for health and safety protocols. Full refund + health safety compensation ($10-50) + restaurant quality audit trigger. Health department notification if severe.",
            
            'handle_spillage': f"Spilled/damaged food requires photo documentation for full compensation. Temperature control assessment + delivery partner review + customer protection guarantee activation.",
            
            'handle_package_tampering': f"Package tampering is a serious security issue requiring immediate documentation. Full refund + security investigation + customer safety prioritization + delivery verification protocol enhancement.",
            
            # Text-only Functions  
            'handle_double_charge': f"Payment system errors require immediate refund processing (2-5 business days) + transaction investigation + account protection measures + payment system audit.",
            
            'handle_rude_behavior': f"Professional conduct violations require driver/partner performance review + customer service recovery + behavior coaching + satisfaction guarantee.",
            
            'handle_delivery_delay': f"Delivery delays require compensation based on time exceeded + route optimization review + customer priority status + service improvement measures.",
            
            # Add more function contexts as needed...
        }
        
        return function_contexts.get(function_name, 
            f"Provide comprehensive {service} customer service resolution for {user_type} with appropriate compensation and follow-up measures.")
    
    def _generate_fallback_response(self, function_name: str, user_query: str, 
                                   service: str, user_type: str) -> str:
        """Generate fallback response when AI models fail"""
        
        service_name = service.replace('_', ' ').title()
        function_display = function_name.replace('handle_', '').replace('_', ' ').title()
        
        response = f"""{service_name} Issue Resolution

{function_display} - Processing Your Request

We acknowledge your {service_name} concern and are committed to resolving it promptly. While our AI system is temporarily unavailable, our team is processing your issue manually.

Immediate Actions:
- Issue logged and prioritized for manual review
- Appropriate compensation will be determined based on case specifics
- Investigation initiated with relevant service partners
- Customer satisfaction follow-up scheduled

Next Steps:
- Manual review: 2-4 hours  
- Resolution processing: 4-24 hours
- Compensation application: Within 24 hours
- Follow-up contact: Within 48 hours

Reference ID: {service.upper()}-{function_name.upper()}-{hash(user_query) % 10000}

Thank you for your patience as we ensure you receive the best possible resolution."""
        
        return self._clean_unicode_response(response)
    
    def process_conversation(self, message: str, service: str, user_type: str, 
                           conversation_history: List[Dict], session_context: Dict) -> Dict[str, Any]:
        """Process conversation messages and determine appropriate response"""
        
        try:
            # Check if we already have a specific issue selected
            selected_issue = session_context.get('sub_issue')
            conversation_context = session_context.get('conversation_context', '')
            username = session_context.get('username', 'anonymous')
            user_orders = session_context.get('user_orders', '')
            specific_order_id = session_context.get('specific_order_id')
            
            print(f"DEBUG: process_conversation called with selected_issue={selected_issue}, username={username}, specific_order_id={specific_order_id}")
            
            # Check for order status validation if this is a food quality issue
            if selected_issue and self._is_food_quality_issue(selected_issue, service) and user_type == 'customer':
                print(f"DEBUG: Checking order status for food quality issue in conversation...")
                order_status_response = self._check_order_status_for_food_quality(username, service, selected_issue, message, specific_order_id)
                if order_status_response:
                    print(f"DEBUG: Order status blocked conversation request")
                    return {
                        'text': order_status_response,
                        'requires_image': False,
                        'issue_type': selected_issue
                    }
                print(f"DEBUG: Order status validation passed in conversation")
            
            if selected_issue:
                # We have a specific issue, use conversational fraud-detection approach
                prompt = f"""
                You are a conversational {service.replace('_', ' ').title()} customer service agent handling: {selected_issue.replace('_', ' ').title()}
                
                CUSTOMER ORDER DATA:
                {user_orders}
                
                CONVERSATION SO FAR:
                {conversation_context}
                
                Current customer message: "{message}"
                
                Your job is to:
                1. Use the customer's order data to provide personalized assistance
                2. Reference specific orders when relevant to their complaint
                3. Have a natural conversation with the customer
                4. Ask clarifying questions if needed (but check order data first)
                5. Detect if their complaint seems genuine or suspicious based on order history
                6. Request images when you need visual evidence
                7. If something seems fishy, ask more questions or escalate to human support
                
                Respond naturally and conversationally. Examples:
                - "I see you ordered [specific item] from [restaurant] on [date]. Can you tell me more about what exactly happened?"
                - "Looking at your order [order_id], I'd like to see a photo of the issue to help you better"
                - "I can see from your order history that you ordered [details]. Based on what you're describing, let me check what we can do for you"
                - "I notice something doesn't quite match up with your order [order_id] - could you clarify [specific concern]?"
                - "I see this is about your recent order from [restaurant]. Let me help you resolve this issue."
                
                Respond with a JSON object:
                {{
                    "response_text": "your conversational response to the customer",
                    "needs_image": true/false,
                    "escalate_to_human": true/false,
                    "image_request": "specific image request if needed"
                }}
                """
                
                response = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.orchestrator_model,
                    temperature=0.7,
                    max_tokens=300
                )
                
                try:
                    import json
                    result = json.loads(response.choices[0].message.content.strip())
                    
                    return {
                        'text': result.get('response_text', 'How can I help you further?'),
                        'requires_image': result.get('needs_image', False),
                        'escalate_to_human': result.get('escalate_to_human', False),
                        'image_request': result.get('image_request'),
                        'issue_type': selected_issue
                    }
                    
                except json.JSONDecodeError:
                    return {
                        'text': "I understand you're having an issue. Could you please provide more details about what happened?",
                        'requires_image': False,
                        'issue_type': selected_issue
                    }
            
            else:
                # No specific issue selected yet, use original logic
                analysis_prompt = f"""
                You are an AI customer service agent for {service.replace('_', ' ').title()}.
                
                Analyze this customer message and conversation history to determine:
                1. What specific issue or problem they are describing
                2. Whether you need more information to help them
                3. Whether you need to see an image to properly resolve their issue
                4. What specific function/issue type this relates to
                
                Current message: "{message}"
                
                Conversation history: {conversation_history[-3:] if len(conversation_history) > 3 else conversation_history}
                
                Based on the message, respond with a JSON object containing:
                {{
                    "issue_type": "specific_issue_function_name_if_identified_or_null",
                    "needs_image": true/false,
                    "needs_more_info": true/false,
                    "response_text": "your helpful response to the customer",
                    "image_request": "specific request for what image they should upload, if needs_image is true"
                }}
                
                Common issues that require images:
                - Food quality problems, wrong items, missing items, damaged packages
                - Vehicle condition issues, safety concerns, damaged items
                - Any physical evidence of problems
                
                Respond ONLY with the JSON object, no additional text.
                """
            
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": analysis_prompt}],
                model=self.orchestrator_model,
                temperature=0.3,
                max_tokens=500
            )
            
            try:
                import json
                analysis = json.loads(response.choices[0].message.content.strip())
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                analysis = {
                    "issue_type": None,
                    "needs_image": False,
                    "needs_more_info": True,
                    "response_text": "I understand you have an issue. Could you please provide more details about what happened so I can better assist you?",
                    "image_request": None
                }
            
            # If we identified a specific issue and it requires an image, check our function mapping
            if analysis.get('issue_type') and analysis.get('needs_image'):
                requires_image = self.image_required_functions.get(analysis['issue_type'], False)
                if requires_image:
                    return {
                        'text': analysis['response_text'],
                        'requires_image': True,
                        'image_request': analysis.get('image_request', "Please upload a photo of the issue to help me provide the best solution."),
                        'issue_type': analysis['issue_type']
                    }
            
            # If we have enough information, try to resolve directly
            if analysis.get('issue_type') and not analysis.get('needs_more_info'):
                resolution = self._process_with_text_model(
                    function_name=analysis['issue_type'],
                    user_query=message,
                    service=service,
                    user_type=user_type
                )
                
                return {
                    'text': resolution,
                    'requires_image': False,
                    'issue_type': analysis['issue_type']
                }
            
            # Otherwise, continue the conversation to gather more info
            return {
                'text': analysis['response_text'],
                'requires_image': analysis.get('needs_image', False),
                'issue_type': analysis.get('issue_type')
            }
            
        except Exception as e:
            logger.error(f"Conversation processing error: {e}")
            return {
                'text': "I'm here to help you with your issue. Could you please tell me more about what problem you're experiencing?",
                'requires_image': False,
                'issue_type': None
            }
    
    def process_conversation_image(self, image_data: str, service: str, user_type: str,
                                 conversation_history: List[Dict], current_issue: Optional[str],
                                 session_context: Dict) -> Dict[str, Any]:
        """Process image uploaded during conversation with fraud detection"""
        
        try:
            # First, screen the image for security
            if not self._screen_image_security(image_data):
                return {
                    'text': "I'm sorry, but I cannot process this image. Please upload a clear photo related to your service issue.",
                    'requires_image': True
                }
            
            # Get conversation context
            conversation_context = session_context.get('conversation_context', '')
            current_issue = current_issue or session_context.get('sub_issue')
            
            # Use conversational fraud detection approach
            # Get user orders from session context
            user_orders = session_context.get('user_orders', '')
            
            prompt = f"""
            You are a conversational {service.replace('_', ' ').title()} customer service agent analyzing an image for: {current_issue.replace('_', ' ').title() if current_issue else 'customer issue'}
            
            CUSTOMER ORDER DATA:
            {user_orders}
            
            CONVERSATION SO FAR:
            {conversation_context}
            
            The customer has uploaded an image. Your job is to:
            1. Use the customer's order data to verify the complaint
            2. Describe what you see in the image conversationally
            3. Check if the image matches their complaint and order details
            4. If it matches and seems genuine, help them resolve it
            5. If it doesn't match or seems suspicious, ask questions or escalate
            6. Be conversational and natural, not formal
            
            Examples of responses:
            - "I can see [description] in your photo from your order [order_id] at [restaurant]. This definitely looks like [issue]. Let me help you resolve this..."
            - "Looking at your image and your order details, I notice [observation]. However, this doesn't quite match what you described. Could you clarify [question]?"
            - "I see [description], but comparing this to your order [order_id] for [items], I'm having trouble understanding how this relates to your complaint. Can you help me understand?"
            - "Based on what I see and your order history, I think it's best to connect you with our specialized team who can look into this more thoroughly."
            
            Respond with JSON:
            {{
                "response_text": "your conversational response to the customer",
                "genuine_complaint": true/false,
                "escalate_to_human": true/false,
                "provide_resolution": true/false
            }}
            """
            
            response = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url", 
                                "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                            }
                        ]
                    }
                ],
                model=self.image_model,
                temperature=0.3,
                max_tokens=400
            )
            
            try:
                import json
                result = json.loads(response.choices[0].message.content.strip())
                
                response_text = result.get('response_text', 'Thank you for the image. Let me review this.')
                
                # If escalation needed, add escalation message
                if result.get('escalate_to_human', False):
                    response_text += "\n\nI'm going to connect you with our specialized support team who can better assist you with this specific case."
                
                return {
                    'text': self._clean_unicode_response(response_text),
                    'requires_image': False,
                    'escalate_to_human': result.get('escalate_to_human', False),
                    'genuine_complaint': result.get('genuine_complaint', True)
                }
                
            except json.JSONDecodeError:
                # Fallback to direct processing
                return {
                    'text': self._process_with_image_model(
                        function_name=current_issue or 'handle_general_complaint',
                        user_query=" ".join([msg.get('content', '') for msg in conversation_history[-3:] if msg.get('role') == 'user']),
                        service=service,
                        user_type=user_type,
                        image_data=image_data
                    ),
                    'requires_image': False
                }
            
        except Exception as e:
            logger.error(f"Conversation image processing error: {e}")
            return {
                'text': "Thank you for the image. I'm analyzing what you've shown me and will get back to you with the next steps.",
                'requires_image': False
            }