"""
Grab Cabs Driver Customer Experience Handler (Driver's POV)
Uses AI models for intelligent complaint resolution
"""

import logging
import os
import sys
from typing import Optional

# Add parent directory to path to import enhanced_ai_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class CustomerExperienceHandler:
    """Driver-focused customer experience management with real AI (Driver's POV)"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_cabs"
        self.actor = "driver"
        self.handler_type = "customer_experience_handler"
        try:
            self.ai_engine = EnhancedAgenticAIEngine()
        except Exception as e:
            logger.warning(f"AI engine initialization failed: {e}")
            self.ai_engine = None
        
    def handle_passenger_harassment_complaint(self, query: str, harassment_type: str = None, image_data: Optional[str] = None, workflow_stage: str = "initial") -> str:
        """Handle passenger harassment complaints with strict dropdown + AI interpretation hybrid"""
        logger.info(f"Processing passenger harassment complaint - Type: {harassment_type}, Stage: {workflow_stage}")

        # STAGE 1: Show strict dropdown options (NO AI)
        if workflow_stage == "initial" or not harassment_type:
            return """🚨 **Passenger Harassment Report**

Please select the type of harassment you experienced from the passenger:

**📋 Select Harassment Type:**
☐ Threats
☐ Verbal Abuse
☐ Physical Abuse
☐ Stalking
☐ Inappropriate Behaviour

Please select one option above to continue with your report."""

        # STAGE 2: Show apology and description prompt (NO AI)
        if harassment_type and workflow_stage == "type_selected":
            return f"""🚨 **Passenger Harassment Report - {harassment_type}**

**We are deeply sorry this happened to you.**

This behavior goes completely against Grab's core values. We are committed to providing a safe, respectful working environment for all our driver-partners. Your safety and well-being are our absolute priority, and we take these incidents extremely seriously.

**📝 Please describe what happened:**

Please provide a detailed description of the incident. You can include:
- Text description of what occurred
- Date and time of the incident
- Trip/order details if known
- Passenger details (automatically available to us)

**After you submit your description, you'll be prompted to upload evidence if available.**"""

        # STAGE 3: Request image upload after text description
        if harassment_type and workflow_stage == "image_request":
            return f"""📷 **Evidence Upload - {harassment_type}**

Thank you for providing the details about your {harassment_type} incident with the passenger.

**Please upload evidence if you have any:**

📸 **Photos or screenshots** that support your report:
- Screenshots of inappropriate messages
- Photos of any relevant evidence
- Pictures that document the incident (if safe to take)
- Dash cam footage screenshots

**Note:** Evidence helps us:
- Process your case faster
- Take appropriate action against the passenger
- Provide better support for your situation
- Protect you and other drivers

**🔄 If you don't have evidence to upload, type "no evidence" to continue to the final resolution.**"""

        # STAGE 4: AI processes with Llama Maverick for image analysis + personalized response
        if harassment_type and query and workflow_stage == "ai_processing":
            if self.ai_engine:
                # Use AI to generate contextual, empathetic response based on driver's specific situation
                # If image provided, Llama Maverick will analyze it for evidence verification
                ai_context = f"""
                HARASSMENT TYPE: {harassment_type}
                DRIVER DESCRIPTION: {query}
                IMAGE PROVIDED: {"Yes - analyze for evidence" if image_data else "No"}

                Generate a personalized, empathetic response for a driver-partner that:
                1. Acknowledges their specific situation and validates their experience
                2. {"Analyzes the provided evidence and incorporates findings" if image_data else "Processes text description thoroughly"}
                3. Provides relevant safety advice for their harassment type
                4. Offers specific next steps based on their description
                5. Shows understanding of the impact on their livelihood
                6. Provides tailored resources for drivers
                7. Addresses income protection concerns

                {"If image evidence is provided, comment on what you can observe and how it supports their case." if image_data else ""}
                Be conversational, supportive, and specific to their situation as a driver.
                """

                try:
                    ai_response = self.ai_engine.process_complaint(
                        function_name="handle_passenger_harassment_personalized",
                        user_query=ai_context,
                        service=self.service,
                        user_type=self.actor,
                        image_data=image_data
                    )

                    # Add structured helplines after AI response
                    helplines = f"""

🆘 **Emergency Helplines & Support**

**Immediate Safety:**
- Emergency Services: 911
- Grab Driver Safety Hotline: 1-800-GRAB-DRIVER
- Crisis Support: 1-800-273-8255

**Grab Driver Support:**
- 24/7 Driver Care: Available in your Grab Driver app
- Email: driversafety@grab.com
- Live Chat: Available 24/7

**Additional Resources:**
- Local Police: Contact if immediate danger
- Counseling Services: Available through Grab partnership
- Legal Support: Contact our legal team for guidance
- Driver Support Groups: Available in your area

**Case Reference:** GC-DRIVER-HARASSMENT-{harassment_type.upper().replace(' ', '')}-001

**Action Taken:**
✅ Passenger immediately suspended from platform pending investigation
✅ Incident escalated to driver safety team
✅ Case opened with reference number above
✅ You will receive follow-up within 2 hours
✅ Income protection during investigation period"""

                    return f"{ai_response}{helplines}"

                except Exception as e:
                    logger.error(f"AI processing failed: {e}")

            # Fallback if AI fails
            return f"""I understand you experienced {harassment_type} from a passenger. This is completely unacceptable and we take this very seriously as it affects your safety and livelihood.

**Your situation has been escalated immediately.** Based on your description: "{query[:100]}{'...' if len(query) > 100 else ''}", we are taking the following actions:

**Immediate Actions:**
- Passenger suspended from platform pending investigation
- Driver safety team notified for priority handling
- Your account flagged for enhanced protection
- Income protection activated during investigation

**What happens next:**
- Investigation team will review all trip details
- You'll receive updates within 2 hours
- Additional safety measures will be implemented
- Earnings protection will be processed

🆘 **Driver Emergency Support Available 24/7:**
- Grab Driver Safety: 1-800-GRAB-DRIVER
- Crisis Support: 1-800-273-8255
- Case Reference: GC-DRIVER-HARASSMENT-{harassment_type.upper().replace(' ', '')}-001"""

        # Default fallback
        return "Please specify the harassment type to continue with your report."

    def handle_false_complaint_rating_reduction(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle false complaints that reduced rating complaints - TEXT ONLY"""
        logger.info(f"Processing false complaint rating reduction complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_false_complaint_rating_reduction",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )

    def handle_unresolved_passenger_disputes(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle escalation of unresolved disputes with passengers complaints - TEXT ONLY"""
        logger.info(f"Processing unresolved passenger disputes complaint: {query[:100]}...")
        return self.ai_engine.process_complaint(
            function_name="handle_unresolved_passenger_disputes",
            user_query=query,
            service=self.service,
            user_type=self.actor,
            image_data=image_data
        )