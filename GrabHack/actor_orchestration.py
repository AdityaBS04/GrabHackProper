"""
Actor-Aware Grab Service Orchestration System
Routes queries to appropriate actor-specific handlers within each Grab service
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from models import GrabService, Actor, IssueCategory, ACTOR_ISSUE_MAPPING, SERVICE_ACTORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ActorAwareOrchestrator:
    """Actor-aware orchestration system that routes by service and actor"""
    
    def __init__(self):
        self.current_service = None
        self.current_actor = None
        self.current_category = None
        self.conversation_history = []
        
    def process_message(self, user_input: str) -> str:
        """Process user message and route to appropriate actor-specific handler"""
        try:
            # Add to conversation history
            self.conversation_history.append({"role": "user", "message": user_input})
            
            # Enhanced intent detection with actor awareness
            if self._is_service_selection(user_input):
                response = self._handle_service_selection(user_input)
            elif self._is_actor_selection(user_input):
                response = self._handle_actor_selection(user_input)
            elif self._is_category_selection(user_input):
                response = self._handle_category_selection(user_input)
            elif self._is_issue_description(user_input):
                response = self._handle_issue_resolution(user_input)
            else:
                response = self._show_services()
            
            # Add response to history
            self.conversation_history.append({"role": "assistant", "message": response})
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return "I apologize for the technical difficulty. Please try again."
    
    def _is_service_selection(self, text: str) -> bool:
        """Check if user is selecting a service"""
        service_keywords = {
            'food': GrabService.GRAB_FOOD,
            'delivery': GrabService.GRAB_FOOD,
            'restaurant': GrabService.GRAB_FOOD,
            'mart': GrabService.GRAB_MART,
            'grocery': GrabService.GRAB_MART,
            'shopping': GrabService.GRAB_MART,
            'cab': GrabService.GRAB_CABS,
            'ride': GrabService.GRAB_CABS,
            'driver': GrabService.GRAB_CABS,
            'taxi': GrabService.GRAB_CABS
        }
        
        text_lower = text.lower()
        for keyword, service in service_keywords.items():
            if keyword in text_lower:
                self.current_service = service
                return True
        return False
    
    def _is_actor_selection(self, text: str) -> bool:
        """Check if user is selecting an actor type"""
        if not self.current_service:
            return False
            
        actor_keywords = {
            'customer': Actor.CUSTOMER,
            'client': Actor.CUSTOMER,
            'user': Actor.CUSTOMER,
            'restaurant': Actor.RESTAURANT,
            'partner': Actor.RESTAURANT,
            'delivery': Actor.DELIVERY_AGENT,
            'driver': Actor.DRIVER,
            'warehouse': Actor.DARK_HOUSE,
            'dark house': Actor.DARK_HOUSE,
            'inventory': Actor.DARK_HOUSE
        }
        
        text_lower = text.lower()
        for keyword, actor in actor_keywords.items():
            if keyword in text_lower:
                # Check if actor is valid for current service
                if actor in SERVICE_ACTORS.get(self.current_service, []):
                    self.current_actor = actor
                    return True
        return False
    
    def _is_category_selection(self, text: str) -> bool:
        """Check if user is selecting an issue category"""
        return (self.current_service is not None and 
                self.current_actor is not None and 
                any(char.isdigit() for char in text))
    
    def _is_issue_description(self, text: str) -> bool:
        """Check if user is describing their issue"""
        return (self.current_service is not None and 
                self.current_actor is not None and 
                len(text.split()) > 5)
    
    def _handle_service_selection(self, text: str) -> str:
        """Handle service selection and show available actors"""
        service_name = self.current_service.value.replace('_', ' ').title()
        return f"Great! You've selected **{service_name}**. Now please tell me who you are:\n\n{self._show_actors()}"
    
    def _handle_actor_selection(self, text: str) -> str:
        """Handle actor selection and show categories"""
        actor_name = self._get_actor_display_name(self.current_actor)
        service_name = self.current_service.value.replace('_', ' ').title()
        return f"Perfect! You are a **{actor_name}** with **{service_name}**. Let me show you relevant issue categories:\n\n{self._show_categories()}"
    
    def _handle_category_selection(self, text: str) -> str:
        """Handle category selection"""
        try:
            # Extract number from text
            category_num = int(''.join(filter(str.isdigit, text)))
            
            service_actor_key = (self.current_service, self.current_actor)
            if service_actor_key not in ACTOR_ISSUE_MAPPING:
                return "No categories available for this service and actor combination."
            
            actor_issues = ACTOR_ISSUE_MAPPING[service_actor_key]
            categories = list(actor_issues.keys())
            
            if 1 <= category_num <= len(categories):
                self.current_category = categories[category_num - 1]
                return self._show_sub_issues()
            else:
                return "Invalid category number. Please select a valid option."
                
        except ValueError:
            return "Please enter a valid category number."
    
    def _handle_issue_resolution(self, text: str) -> str:
        """Handle issue resolution with actor-specific responses"""
        if not self.current_service or not self.current_actor or not self.current_category:
            return "Please select a service, actor type, and category first."
        
        # Get actor-specific response based on issue type
        return self._get_actor_response(text)
    
    def _get_actor_response(self, issue_description: str) -> str:
        """Get actor-specific response based on the issue"""
        service = self.current_service
        actor = self.current_actor
        category = self.current_category
        
        # Actor-specific responses
        if service == GrabService.GRAB_FOOD:
            return self._get_food_actor_response(actor, category, issue_description)
        elif service == GrabService.GRAB_MART:
            return self._get_mart_actor_response(actor, category, issue_description)
        elif service == GrabService.GRAB_CABS:
            return self._get_cabs_actor_response(actor, category, issue_description)
        else:
            return "Service handler not available. Please contact support."
    
    def _get_food_actor_response(self, actor: Actor, category: IssueCategory, description: str) -> str:
        """Grab Food actor-specific responses"""
        if actor == Actor.CUSTOMER:
            return """🍽️ **Customer Food Quality Resolution**
            
**We Sincerely Apologize for Your Experience**

**Immediate Actions:**
- Full refund processed for your order
- $10 Grab Food credits added to account
- Quality investigation with restaurant initiated
- VIP customer status activated

**Your Satisfaction Guarantee:**
- Priority restaurant selection
- Quality guarantee for next 5 orders
- Direct customer service hotline
- Personal satisfaction manager assigned

Your trust in Grab Food is our priority."""

        elif actor == Actor.RESTAURANT:
            return """🏪 **Restaurant Quality Standards Alert**
            
**Quality Compliance Action Required**

**Performance Issue Identified:**
- Customer complaint received and verified
- Quality standards violation documented
- Immediate corrective action required

**Required Actions:**
1. Kitchen staff quality training (48 hours)
2. Portion control verification and calibration
3. Food safety audit and compliance check
4. Customer service recovery training

**Performance Impact:**
- Quality score reduction applied
- Temporary platform visibility reduction
- Mandatory quality improvement plan
- Supervisor review scheduled

**Support Resources:**
- Quality management consultant assigned
- Training materials and resources provided
- Best practices sharing session
- Performance monitoring and guidance

Restaurant success depends on consistent quality standards."""

        elif actor == Actor.DELIVERY_AGENT:
            return """🚴 **Delivery Performance Enhancement**
            
**Performance Improvement Plan**

**Delivery Issue Identified:**
- Customer experience below standards
- Performance accountability measures applied
- Training and improvement required

**Mandatory Training:**
1. Delivery time optimization (30 minutes)
2. Customer communication excellence
3. Food handling and safety protocols
4. Professional service standards

**Performance Monitoring:**
- Next 20 deliveries tracked for improvement
- Customer satisfaction verification
- Route efficiency analysis
- Quality assurance checkpoints

**Support and Recovery:**
- Performance coaching available
- Equipment upgrade assistance
- Best practices sharing
- Earnings recovery plan

Professional delivery service ensures customer satisfaction and your success."""

    def _get_mart_actor_response(self, actor: Actor, category: IssueCategory, description: str) -> str:
        """Grab Mart actor-specific responses"""
        if actor == Actor.CUSTOMER:
            return """🛒 **Grocery Shopping Excellence Resolution**
            
**We Apologize for Your Shopping Experience**

**Immediate Resolution:**
- Full refund for affected items: processed
- Fresh product replacement delivery scheduled
- $12 Grab Mart credits added to account
- Premium customer service activated

**Your Account Benefits:**
- VIP shopping experience enrollment
- Personal shopper assignment
- Quality guarantee program
- Freshness satisfaction guarantee

**Next Steps:**
- Replacement delivery within 3 hours
- Quality assurance investigation
- Customer satisfaction follow-up
- Shopping preference optimization

Your grocery needs and satisfaction are our commitment."""

        elif actor == Actor.DARK_HOUSE:
            return """📦 **Warehouse Operations Enhancement**
            
**Inventory Management Alert**

**Operational Issue Identified:**
- Customer order fulfillment impacted
- Warehouse efficiency improvement required
- Quality control measures enhancement needed

**Immediate Actions Required:**
1. Inventory accuracy audit and verification
2. Quality control protocol reinforcement
3. Staff training on picking accuracy
4. Temperature control system check

**Performance Standards:**
- Inventory accuracy: 99.5% target
- Order fulfillment rate: >98%
- Quality compliance: 100%
- Customer satisfaction correlation

**Process Improvements:**
- Enhanced quality inspection procedures
- Automated inventory tracking
- Staff performance monitoring
- Continuous improvement implementation

Warehouse excellence ensures customer satisfaction and operational efficiency."""

        elif actor == Actor.DELIVERY_AGENT:
            return """🚛 **Grocery Delivery Excellence**
            
**Delivery Performance Enhancement**

**Delivery Issue Analysis:**
- Customer delivery experience below standards
- Grocery handling improvement required
- Professional service training needed

**Mandatory Training Program:**
1. Grocery handling best practices (45 minutes)
2. Cold chain delivery protocols
3. Customer service excellence
4. Bulk order management techniques

**Performance Requirements:**
- Delivery time optimization: 35-45 minutes
- Product handling excellence: zero damage
- Customer satisfaction: >4.5 stars
- Temperature control compliance: 100%

**Equipment and Support:**
- Professional delivery equipment provided
- Temperature monitoring tools
- Customer service training resources
- Performance coaching and mentorship

Professional grocery delivery creates customer loyalty and success."""

    def _get_cabs_actor_response(self, actor: Actor, category: IssueCategory, description: str) -> str:
        """Grab Cabs actor-specific responses"""
        if actor == Actor.CUSTOMER:
            return """🚗 **Ride Experience Excellence**
            
**Your Safety and Comfort Are Our Priority**

**Immediate Resolution:**
- Full ride refund processed
- $10 Grab Cabs credits added to account
- Driver performance review initiated
- VIP ride service activation

**Your Protection and Benefits:**
- Premium driver assignment priority
- Enhanced safety features activated
- Direct customer service access
- Ride quality guarantee program

**Quality Assurance:**
- Incident investigation completed
- Driver accountability measures applied
- Service excellence standards reinforced
- Continuous safety monitoring

Your trust and safety drive our commitment to ride excellence."""

        elif actor == Actor.DRIVER:
            return """🚙 **Driver Performance Development**
            
**Performance Improvement and Support**

**Performance Issue Review:**
- Customer feedback received and analyzed
- Performance accountability measures applied
- Training and development opportunity provided

**Mandatory Development Program:**
1. Professional conduct training (45 minutes)
2. Customer service excellence course
3. Route optimization and efficiency
4. Vehicle maintenance and standards

**Performance Recovery Plan:**
- Complete training within 48 hours
- Maintain >4.5 star rating for next 20 rides
- Zero behavior complaints tolerance
- Performance monitoring and support

**Support Resources:**
- One-on-one coaching session
- Driver excellence program enrollment
- Equipment maintenance assistance
- Earnings optimization guidance

Your success as a Grab driver partner depends on professional service excellence."""

        return "Actor-specific response not available."
    
    def _show_services(self) -> str:
        """Show available Grab services"""
        return """Welcome to Grab Customer Service! 🚗🍔🛒

Please tell me which Grab service you need help with:

**1. 🍔 Grab Food** - Food delivery service
**2. 🛒 Grab Mart** - Grocery & retail delivery  
**3. 🚗 Grab Cabs** - Ride-hailing service

You can type keywords like:
- "food delivery problem"
- "grocery missing items"  
- "ride driver issue"

How can I assist you today?"""
    
    def _show_actors(self) -> str:
        """Show actors for current service"""
        if not self.current_service or self.current_service not in SERVICE_ACTORS:
            return "Please select a service first."
        
        service_name = self.current_service.value.replace('_', ' ').title()
        actors = SERVICE_ACTORS[self.current_service]
        
        actors_text = f"**{service_name} - Who Are You?**\n\n"
        
        for i, actor in enumerate(actors, 1):
            actor_name = self._get_actor_display_name(actor)
            actor_desc = self._get_actor_description(actor, self.current_service)
            actors_text += f"**{i}. {actor_name}** - {actor_desc}\n"
        
        actors_text += f"\nPlease select your role (1-{len(actors)}):"
        return actors_text
    
    def _get_actor_display_name(self, actor: Actor) -> str:
        """Get user-friendly actor names"""
        display_names = {
            Actor.CUSTOMER: "Customer",
            Actor.RESTAURANT: "Restaurant Partner", 
            Actor.DELIVERY_AGENT: "Delivery Agent",
            Actor.DRIVER: "Driver Partner",
            Actor.DARK_HOUSE: "Warehouse Operations"
        }
        return display_names.get(actor, actor.name.title())
    
    def _get_actor_description(self, actor: Actor, service: GrabService) -> str:
        """Get actor description based on service context"""
        descriptions = {
            (Actor.CUSTOMER, GrabService.GRAB_FOOD): "I'm a customer with a food delivery issue",
            (Actor.RESTAURANT, GrabService.GRAB_FOOD): "I'm a restaurant partner needing support",
            (Actor.DELIVERY_AGENT, GrabService.GRAB_FOOD): "I'm a delivery agent with performance questions",
            
            (Actor.CUSTOMER, GrabService.GRAB_MART): "I'm a customer with a grocery shopping issue", 
            (Actor.DARK_HOUSE, GrabService.GRAB_MART): "I'm from warehouse operations needing guidance",
            (Actor.DELIVERY_AGENT, GrabService.GRAB_MART): "I'm a grocery delivery agent with questions",
            
            (Actor.CUSTOMER, GrabService.GRAB_CABS): "I'm a customer with a ride experience issue",
            (Actor.DRIVER, GrabService.GRAB_CABS): "I'm a driver partner needing support"
        }
        return descriptions.get((actor, service), "Actor description not available")
    
    def _show_categories(self) -> str:
        """Show categories for current service and actor"""
        service_actor_key = (self.current_service, self.current_actor)
        if service_actor_key not in ACTOR_ISSUE_MAPPING:
            return "No categories available for this service and actor combination."
        
        service_name = self.current_service.value.replace('_', ' ').title()
        actor_name = self._get_actor_display_name(self.current_actor)
        actor_issues = ACTOR_ISSUE_MAPPING[service_actor_key]
        
        categories_text = f"**{service_name} - {actor_name} Issues:**\n\n"
        
        for i, category in enumerate(actor_issues.keys(), 1):
            category_name = self._get_category_display_name(category)
            categories_text += f"**{i}.** {category_name}\n"
        
        categories_text += f"\nPlease select a category (1-{len(actor_issues)}):"
        return categories_text
    
    def _get_category_display_name(self, category: IssueCategory) -> str:
        """Get user-friendly category name"""
        display_names = {
            IssueCategory.ORDER_NOT_RECEIVED: "Order/Delivery Issues",
            IssueCategory.PORTION_INADEQUATE: "Portion Size Concerns",
            IssueCategory.ITEMS_MISSING: "Missing Items",
            IssueCategory.POOR_QUALITY: "Quality Issues",
            IssueCategory.PRODUCT_QUALITY: "Product Quality & Freshness",
            IssueCategory.RIDE_ISSUES: "Ride Experience Issues",
            IssueCategory.DRIVER_BEHAVIOR: "Professional Conduct",
            IssueCategory.SAFETY_INCIDENT: "Safety Concerns",
            IssueCategory.PAYMENT_BILLING: "Payment & Billing"
        }
        return display_names.get(category, category.name.replace('_', ' ').title())
    
    def _show_sub_issues(self) -> str:
        """Show sub-issues for current service, actor, and category"""
        service_actor_key = (self.current_service, self.current_actor)
        if service_actor_key not in ACTOR_ISSUE_MAPPING:
            return "No issues available."
        
        actor_issues = ACTOR_ISSUE_MAPPING[service_actor_key]
        sub_issues = actor_issues[self.current_category]
        
        category_name = self._get_category_display_name(self.current_category)
        actor_name = self._get_actor_display_name(self.current_actor)
        
        sub_text = f"**{category_name} - {actor_name} Specific Issues:**\n\n"
        
        for i, sub_issue in enumerate(sub_issues, 1):
            sub_text += f"• {sub_issue.name}\n"
        
        sub_text += "\nPlease describe your specific issue and I'll provide targeted assistance!"
        return sub_text
    
    def reset_conversation(self):
        """Reset conversation state"""
        self.current_service = None
        self.current_actor = None
        self.current_category = None
        self.conversation_history = []
        logger.info("Conversation reset")


def main():
    """Run the actor-aware orchestration system"""
    orchestrator = ActorAwareOrchestrator()
    
    print("🎭 Grab Actor-Aware Customer Service System")
    print("=" * 55)
    print("Type 'exit' to quit or 'reset' to start over.\n")
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() == 'exit':
                print("\n🙏 Thank you for using Grab services. Goodbye!")
                break
            
            if user_input.lower() == 'reset':
                orchestrator.reset_conversation()
                print("\n🔄 Conversation reset. How can I help you today?")
                continue
            
            if not user_input:
                continue
            
            # Process the message
            response = orchestrator.process_message(user_input)
            print(f"\n🎭 Grab Support: {response}")
            
        except KeyboardInterrupt:
            print("\n\n🙏 Thank you for using Grab services. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again or type 'reset' to start over.")


if __name__ == "__main__":
    main()