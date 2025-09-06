"""
Standalone Grab Service Orchestration System
No external dependencies - works with pure Python
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from models import GrabService, IssueCategory, ISSUE_MAPPING

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleOrchestrator:
    """Simple orchestration system without external dependencies"""
    
    def __init__(self):
        self.current_service = None
        self.current_category = None
        self.conversation_history = []
        
    def process_message(self, user_input: str) -> str:
        """Process user message and route to appropriate handler"""
        try:
            # Add to conversation history
            self.conversation_history.append({"role": "user", "message": user_input})
            
            # Basic intent detection
            if self._is_service_selection(user_input):
                response = self._handle_service_selection(user_input)
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
    
    def _is_category_selection(self, text: str) -> bool:
        """Check if user is selecting an issue category"""
        return self.current_service is not None and any(char.isdigit() for char in text)
    
    def _is_issue_description(self, text: str) -> bool:
        """Check if user is describing their issue"""
        return self.current_service is not None and len(text.split()) > 5
    
    def _handle_service_selection(self, text: str) -> str:
        """Handle service selection"""
        service_name = self.current_service.value.replace('_', ' ').title()
        return f"Great! You've selected **{service_name}**. Let me show you the available issue categories:\n\n{self._show_categories()}"
    
    def _handle_category_selection(self, text: str) -> str:
        """Handle category selection"""
        try:
            # Extract number from text
            category_num = int(''.join(filter(str.isdigit, text)))
            
            if self.current_service not in ISSUE_MAPPING:
                return "Service not available. Please select a valid service."
            
            service_issues = ISSUE_MAPPING[self.current_service]
            categories = list(service_issues.keys())
            
            if 1 <= category_num <= len(categories):
                self.current_category = categories[category_num - 1]
                return self._show_sub_issues()
            else:
                return "Invalid category number. Please select a valid option."
                
        except ValueError:
            return "Please enter a valid category number."
    
    def _handle_issue_resolution(self, text: str) -> str:
        """Handle issue resolution with service-specific responses"""
        if not self.current_service or not self.current_category:
            return "Please select a service and category first."
        
        # Get service-specific response based on issue type
        return self._get_service_response(text)
    
    def _get_service_response(self, issue_description: str) -> str:
        """Get service-specific response based on the issue"""
        service = self.current_service
        category = self.current_category
        
        # Service-specific responses
        if service == GrabService.GRAB_FOOD:
            return self._get_food_response(category, issue_description)
        elif service == GrabService.GRAB_MART:
            return self._get_mart_response(category, issue_description)
        elif service == GrabService.GRAB_CABS:
            return self._get_cabs_response(category, issue_description)
        else:
            return "Service handler not available. Please contact support."
    
    def _get_food_response(self, category: IssueCategory, description: str) -> str:
        """Grab Food specific responses"""
        if category == IssueCategory.ORDER_NOT_RECEIVED:
            return """I understand your Grab Food order hasn't arrived. Let me help resolve this immediately.

**Actions taken:**
- Contacted the delivery partner and restaurant
- Full refund processed for delivery fees
- $5 Grab Food credits added to your account
- Priority support for your next order

**Estimated resolution:** 15-20 minutes
**Refund timeline:** 3-5 business days

We sincerely apologize for this inconvenience. Your satisfaction is our priority."""

        elif category == IssueCategory.PORTION_INADEQUATE:
            return """I'm sorry about the portion size issue with your Grab Food order.

**Resolution:**
- Partial refund approved based on order value
- $5 Grab Food credits for future orders
- Feedback shared with restaurant partner
- Quality assurance team notified

**Next steps:**
- Refund will appear in 3-5 business days
- Restaurant will be monitored for portion standards
- Your feedback helps us maintain quality

Thank you for bringing this to our attention."""

        else:
            return "I understand your Grab Food concern. Our food delivery team will investigate and contact you within 2 hours with a resolution."
    
    def _get_mart_response(self, category: IssueCategory, description: str) -> str:
        """Grab Mart specific responses"""
        if category == IssueCategory.ITEMS_MISSING:
            return """I see items are missing from your Grab Mart order. This is unacceptable.

**Immediate actions:**
- Full refund for missing items processed
- $6 Grab Mart credits added to your account
- Fresh delivery of missing items (if available)
- Store partner quality review initiated

**Timeline:**
- Replacement delivery: 2-3 hours
- Refund processing: 1-2 business days
- Store audit: Within 24 hours

Your grocery needs are important to us. We'll ensure this doesn't happen again."""

        elif category == IssueCategory.PRODUCT_QUALITY:
            return """Product quality issues are taken very seriously at Grab Mart.

**Quality guarantee actions:**
- Full refund for affected products
- Fresh replacement delivery at no charge
- $8 Grab Mart credits for inconvenience
- Store quality audit scheduled immediately

**Health & Safety:**
- Products removed from store inventory
- Enhanced quality checks implemented
- Temperature control verification

Your health and satisfaction are our absolute priorities."""

        else:
            return "I understand your Grab Mart concern. Our grocery team will investigate and provide a resolution within 4 hours."
    
    def _get_cabs_response(self, category: IssueCategory, description: str) -> str:
        """Grab Cabs specific responses"""
        if category == IssueCategory.RIDE_ISSUES:
            return """I understand you experienced issues during your Grab ride. Let me address this immediately.

**Actions taken:**
- Ride fare reviewed and adjusted
- $7 Grab Cabs credits added to your account
- Driver performance review initiated
- Incident logged for quality improvement

**Support provided:**
- Priority booking status for future rides
- Direct customer service line access
- Ride quality guarantee program enrollment

Your safety and comfort during Grab rides are our top priorities."""

        elif category == IssueCategory.DRIVER_BEHAVIOR:
            return """Driver behavior issues are taken very seriously at Grab.

**Immediate actions:**
- Driver flagged for performance review
- Mandatory retraining scheduled
- Full ride refund processed
- $10 Grab Cabs credits added

**Safety measures:**
- Enhanced driver screening
- Regular behavioral assessments
- Customer feedback integration
- Zero tolerance policy enforcement

We ensure all drivers maintain professional standards at all times."""

        else:
            return "I understand your Grab ride concern. Our transportation team will investigate and contact you within 1 hour."
    
    def _show_services(self) -> str:
        """Show available Grab services"""
        return """Welcome to Grab Customer Service! 🚗🍔🛒

Please tell me which Grab service you need help with:

**1. 🍔 Grab Food** - Food delivery issues
**2. 🛒 Grab Mart** - Grocery & retail delivery problems  
**3. 🚗 Grab Cabs** - Ride-hailing concerns

You can type keywords like:
- "food delivery problem"
- "grocery missing items"  
- "ride driver issue"

How can I assist you today?"""
    
    def _show_categories(self) -> str:
        """Show categories for current service"""
        if not self.current_service or self.current_service not in ISSUE_MAPPING:
            return "Please select a service first."
        
        service_name = self.current_service.value.replace('_', ' ').title()
        service_issues = ISSUE_MAPPING[self.current_service]
        
        categories_text = f"**{service_name} Issue Categories:**\n\n"
        
        for i, category in enumerate(service_issues.keys(), 1):
            category_name = self._get_category_display_name(category)
            categories_text += f"**{i}.** {category_name}\n"
        
        categories_text += f"\nPlease select a number (1-{len(service_issues)}):"
        return categories_text
    
    def _get_category_display_name(self, category: IssueCategory) -> str:
        """Get user-friendly category name"""
        display_names = {
            IssueCategory.ORDER_NOT_RECEIVED: "Order not received / Delivery delays",
            IssueCategory.PORTION_INADEQUATE: "Portion size inadequate",
            IssueCategory.ITEMS_MISSING: "Missing items from order",
            IssueCategory.POOR_QUALITY: "Poor product/food quality",
            IssueCategory.PRODUCT_QUALITY: "Product freshness/quality issues",
            IssueCategory.RIDE_ISSUES: "Ride problems (route, vehicle, etc.)",
            IssueCategory.DRIVER_BEHAVIOR: "Driver behavior concerns",
            IssueCategory.SAFETY_INCIDENT: "Safety incident",
            IssueCategory.PAYMENT_BILLING: "Payment/billing issues"
        }
        return display_names.get(category, category.name.replace('_', ' ').title())
    
    def _show_sub_issues(self) -> str:
        """Show sub-issues for current category"""
        if not self.current_service or not self.current_category:
            return "Please select a service and category first."
        
        service_issues = ISSUE_MAPPING[self.current_service]
        sub_issues = service_issues[self.current_category]
        
        sub_text = f"**{self._get_category_display_name(self.current_category)}**\n\n"
        sub_text += "Please describe your specific issue and I'll help resolve it:\n\n"
        
        for i, sub_issue in enumerate(sub_issues, 1):
            sub_text += f"• {sub_issue.name}\n"
        
        sub_text += "\nType your issue description and I'll provide immediate assistance!"
        return sub_text
    
    def reset_conversation(self):
        """Reset conversation state"""
        self.current_service = None
        self.current_category = None
        self.conversation_history = []
        logger.info("Conversation reset")


def main():
    """Run the standalone orchestration system"""
    orchestrator = SimpleOrchestrator()
    
    print("🚗🍔🛒 Grab Customer Service - Standalone System")
    print("=" * 50)
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
            print(f"\n🤖 Grab Support: {response}")
            
        except KeyboardInterrupt:
            print("\n\n🙏 Thank you for using Grab services. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again or type 'reset' to start over.")


if __name__ == "__main__":
    main()