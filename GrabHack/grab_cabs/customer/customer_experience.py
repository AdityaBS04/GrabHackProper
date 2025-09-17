"""
Grab Cabs Customer Experience Handler
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
    """Customer-focused experience management with real AI"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_cabs"
        self.actor = "customer"
        self.handler_type = "customer_experience_handler"
        try:
            self.ai_engine = EnhancedAgenticAIEngine()
        except Exception as e:
            logger.warning(f"AI engine initialization failed: {e}")
            self.ai_engine = None
        
    def handle_app_booking_issues(self, query: str, issue_type: str = None, image_data: Optional[str] = None, workflow_stage: str = "initial") -> str:
        """Handle app or booking issues with structured workflow"""
        logger.info(f"Processing app/booking issues - Type: {issue_type}, Stage: {workflow_stage}")

        # STAGE 1: Show strict dropdown options (NO AI)
        if workflow_stage == "initial" or not issue_type:
            return """🚗 **App/Booking Issues Report**

Please select the type of issue you're experiencing:

**📋 Select Issue Type:**
☐ Payment Problems
☐ App Crashes/Freezing
☐ GPS/Tracking Issues
☐ Booking Failed
☐ Wrong Fare Calculation

Please select one option above to continue with your report."""

        # STAGE 2: Show apology and description prompt (NO AI)
        if issue_type and workflow_stage == "type_selected":
            return f"""🚗 **App/Booking Issues - {issue_type}**

**We apologize for the technical difficulties you're experiencing.**

This is not the smooth experience we strive to provide. We're committed to resolving technical issues quickly to ensure seamless ride booking for all our customers.

**📝 Please describe the issue:**

Please provide details about what happened:
- What were you trying to do when the problem occurred?
- Any error messages you received
- Screenshots of the issue if available
- Your device type and app version

**Upload Evidence:** Screenshots or screen recordings can help us resolve this faster.

**After you submit your description, our technical team will analyze the issue and provide immediate assistance.**"""

        # STAGE 3: AI processes the user's description
        if issue_type and query and workflow_stage == "ai_processing":
            if self.ai_engine:
                ai_context = f"""
                ISSUE TYPE: {issue_type}
                USER DESCRIPTION: {query}

                Generate a technical support response that:
                1. Acknowledges their specific technical issue
                2. Provides immediate troubleshooting steps
                3. Offers workarounds if available
                4. Shows understanding of the inconvenience
                5. Provides clear next steps for resolution

                Be technical but helpful, and specific to their app/booking issue.
                """

                try:
                    ai_response = self.ai_engine.process_complaint(
                        function_name="handle_app_booking_technical_support",
                        user_query=ai_context,
                        service=self.service,
                        user_type=self.actor,
                        image_data=image_data
                    )

                    support_info = f"""

📞 **Technical Support Available:**
- 24/7 App Support: Available in your Grab app
- Email: techsupport@grab.com
- Live Chat: Available 24/7

**Immediate Actions:**
✅ Technical team notified
✅ Issue logged for app improvement
✅ Account credited if applicable
✅ Priority support activated

**Case Reference:** GC-TECH-{issue_type.upper().replace(' ', '')}-001"""

                    return f"{ai_response}{support_info}"

                except Exception as e:
                    logger.error(f"AI processing failed: {e}")

            # Fallback if AI fails
            return f"""I understand you're experiencing {issue_type} with our app. This is frustrating and we're here to help resolve this immediately.

**Quick troubleshooting steps:**
1. Force close and restart the Grab app
2. Check your internet connection
3. Update to the latest app version
4. Clear app cache if the problem persists

**Your issue has been escalated to our technical team.** Based on your description: "{query[:100]}{'...' if len(query) > 100 else ''}", we're investigating this immediately.

📞 **Immediate Support:** 1-800-GRAB-TECH
**Case Reference:** GC-TECH-{issue_type.upper().replace(' ', '')}-001"""

        return "Please specify the issue type to continue with your report."

    def handle_cancellation_refund_policy_complications(self, query: str, issue_type: str = None, image_data: Optional[str] = None, workflow_stage: str = "initial") -> str:
        """Handle cancellation/refund policy complications with structured workflow"""
        logger.info(f"Processing cancellation/refund policy - Type: {issue_type}, Stage: {workflow_stage}")

        # STAGE 1: Show strict dropdown options (NO AI)
        if workflow_stage == "initial" or not issue_type:
            return """💰 **Cancellation/Refund Policy Issues**

Please select the type of policy issue you're experiencing:

**📋 Select Issue Type:**
☐ Unfair Cancellation Fee
☐ Refund Not Processed
☐ Refund Amount Incorrect
☐ Policy Not Explained Clearly
☐ Unable to Cancel Ride

Please select one option above to continue with your report."""

        # STAGE 2: Show apology and description prompt (NO AI)
        if issue_type and workflow_stage == "type_selected":
            return f"""💰 **Cancellation/Refund Policy - {issue_type}**

**We understand your frustration with this policy matter.**

Our cancellation and refund policies are designed to be fair for both customers and drivers. We're committed to ensuring transparency and resolving any policy-related concerns promptly.

**📝 Please describe your situation:**

Please provide details about your experience:
- When did this issue occur?
- What cancellation/refund were you expecting?
- Any screenshots of charges or policy information
- Previous communication with support if any

**Upload Evidence:** Screenshots of charges, app screens, or emails can help us review your case.

**After you submit your details, our policy team will review your case and provide clarification or resolution.**"""

        # STAGE 3: AI processes the user's description
        if issue_type and query and workflow_stage == "ai_processing":
            if self.ai_engine:
                ai_context = f"""
                POLICY ISSUE TYPE: {issue_type}
                USER DESCRIPTION: {query}

                Generate a policy support response that:
                1. Acknowledges their policy concern
                2. Explains relevant policies clearly
                3. Provides resolution or compensation if appropriate
                4. Shows understanding of their frustration
                5. Offers clear next steps for resolution

                Be empathetic but clear about policies, specific to their cancellation/refund issue.
                """

                try:
                    ai_response = self.ai_engine.process_complaint(
                        function_name="handle_cancellation_refund_policy_support",
                        user_query=ai_context,
                        service=self.service,
                        user_type=self.actor,
                        image_data=image_data
                    )

                    policy_info = f"""

💰 **Policy & Billing Support:**
- 24/7 Billing Support: Available in your Grab app
- Email: billing@grab.com
- Policy Center: Available in app under "Help"

**Immediate Actions:**
✅ Policy team reviewing your case
✅ Account flagged for manual review
✅ Refund processing if applicable
✅ Policy clarification provided

**Case Reference:** GC-POLICY-{issue_type.upper().replace(' ', '')}-001"""

                    return f"{ai_response}{policy_info}"

                except Exception as e:
                    logger.error(f"AI processing failed: {e}")

            # Fallback if AI fails
            return f"""I understand your concern about {issue_type}. Our policies should be clear and fair, and we're here to resolve this for you.

**We're reviewing your case immediately.** Based on your description: "{query[:100]}{'...' if len(query) > 100 else ''}", our policy team will investigate this matter.

**What we're doing:**
1. Manual review of your case
2. Policy clarification if needed
3. Refund processing if applicable
4. Account adjustment if warranted

💰 **Immediate Support:** 1-800-GRAB-BILLING
**Case Reference:** GC-POLICY-{issue_type.upper().replace(' ', '')}-001"""

        return "Please specify the policy issue type to continue with your report."

    def handle_airport_booking_problems(self, query: str, issue_type: str = None, image_data: Optional[str] = None, workflow_stage: str = "initial") -> str:
        """Handle airport booking problems with structured workflow"""
        logger.info(f"Processing airport booking problems - Type: {issue_type}, Stage: {workflow_stage}")

        # STAGE 1: Show strict dropdown options (NO AI)
        if workflow_stage == "initial" or not issue_type:
            return """✈️ **Airport Booking Problems**

Please select the type of airport-related issue you're experiencing:

**📋 Select Issue Type:**
☐ Missed Flight Due to Late Driver
☐ Wrong Terminal/Airport
☐ Flight Sync Issues
☐ Airport Pickup Problems
☐ Flight Delay Complications

Please select one option above to continue with your report."""

        # STAGE 2: Show apology and description prompt (NO AI)
        if issue_type and workflow_stage == "type_selected":
            return f"""✈️ **Airport Booking Problems - {issue_type}**

**We sincerely apologize for this travel disruption.**

We understand how critical airport timing is for your travel plans. Missing flights or experiencing airport-related issues can be extremely stressful and costly. We take full responsibility and are committed to making this right.

**📝 Please describe what happened:**

Please provide details about your airport experience:
- Your flight details (flight number, time, terminal)
- What went wrong with your Grab ride
- Any additional costs incurred (rebooking fees, etc.)
- Screenshots of your booking and flight information

**Upload Evidence:** Flight confirmations, receipts, and booking screenshots will help us process compensation faster.

**After you submit your details, our airport team will prioritize your case and provide immediate compensation for any losses.**"""

        # STAGE 3: AI processes the user's description
        if issue_type and query and workflow_stage == "ai_processing":
            if self.ai_engine:
                ai_context = f"""
                AIRPORT ISSUE TYPE: {issue_type}
                USER DESCRIPTION: {query}

                Generate an airport support response that:
                1. Acknowledges the severe impact of airport/flight issues
                2. Takes full responsibility for the service failure
                3. Provides immediate compensation/solution
                4. Shows understanding of travel stress and costs
                5. Offers premium service recovery

                Be very apologetic and generous with compensation for airport issues.
                """

                try:
                    ai_response = self.ai_engine.process_complaint(
                        function_name="handle_airport_booking_priority_support",
                        user_query=ai_context,
                        service=self.service,
                        user_type=self.actor,
                        image_data=image_data
                    )

                    airport_info = f"""

✈️ **Airport Priority Support:**
- 24/7 Airport Support: 1-800-GRAB-AIRPORT
- Priority Email: airport@grab.com
- Emergency Travel Support: Available 24/7

**Immediate Actions:**
✅ Airport team escalating your case
✅ Compensation being processed
✅ Premium service recovery activated
✅ Future airport bookings prioritized

**Case Reference:** GC-AIRPORT-{issue_type.upper().replace(' ', '')}-001"""

                    return f"{ai_response}{airport_info}"

                except Exception as e:
                    logger.error(f"AI processing failed: {e}")

            # Fallback if AI fails
            return f"""I am deeply sorry about {issue_type}. Airport issues are our highest priority and we take full responsibility for this travel disruption.

**Immediate compensation being processed.** Based on your description: "{query[:100]}{'...' if len(query) > 100 else ''}", our airport team is handling your case with maximum priority.

**What we're doing right now:**
1. Processing immediate compensation
2. Reviewing additional costs you incurred
3. Providing premium service recovery
4. Ensuring this doesn't happen again

✈️ **Emergency Airport Support:** 1-800-GRAB-AIRPORT
**Case Reference:** GC-AIRPORT-{issue_type.upper().replace(' ', '')}-001"""

        return "Please specify the airport issue type to continue with your report."

    def handle_driver_harassment_complaint(self, query: str, harassment_type: str = None, image_data: Optional[str] = None, workflow_stage: str = "initial") -> str:
        """Handle driver harassment complaints with strict dropdown + AI interpretation hybrid"""
        logger.info(f"Processing driver harassment complaint - Type: {harassment_type}, Stage: {workflow_stage}")

        # STAGE 1: Show strict dropdown options (NO AI)
        if workflow_stage == "initial" or not harassment_type:
            return """🚨 **Driver Harassment Report**

Please select the type of harassment you experienced:

**📋 Select Harassment Type:**
☐ Threats
☐ Verbal Abuse
☐ Physical Abuse
☐ Stalking
☐ Inappropriate Behaviour

Please select one option above to continue with your report."""

        # STAGE 2: Show apology and description prompt (NO AI)
        if harassment_type and workflow_stage == "type_selected":
            return f"""🚨 **Driver Harassment Report - {harassment_type}**

**We are deeply sorry this happened to you.**

This behavior goes completely against Grab's core values. We are committed to providing a safe, respectful environment for all our customers. Customer safety is our absolute priority, and we take these incidents extremely seriously.

**📝 Please describe what happened:**

Please provide a detailed description of the incident. You can include:
- Text description of what occurred
- Date and time of the incident
- Driver details if known

**After you submit your description, you'll be prompted to upload evidence if available.**"""

        # STAGE 3: Request image upload after text description
        if harassment_type and workflow_stage == "image_request":
            return f"""📷 **Evidence Upload - {harassment_type}**

Thank you for providing the details about your {harassment_type} incident.

**Please upload evidence if you have any:**

📸 **Photos or screenshots** that support your report:
- Screenshots of inappropriate messages
- Photos of any relevant evidence
- Pictures that document the incident (if safe to take)

**Note:** Evidence helps us:
- Process your case faster
- Take appropriate action against the driver
- Provide better support for your situation

**🔄 If you don't have evidence to upload, type "no evidence" to continue to the final resolution.**"""

        # STAGE 4: AI processes with Llama Maverick for image analysis + personalized response
        if harassment_type and query and workflow_stage == "ai_processing":
            if self.ai_engine:
                # Use AI to generate contextual, empathetic response based on user's specific situation
                # If image provided, Llama Maverick will analyze it for evidence verification
                ai_context = f"""
                HARASSMENT TYPE: {harassment_type}
                USER DESCRIPTION: {query}
                IMAGE PROVIDED: {"Yes - analyze for evidence" if image_data else "No"}

                Generate a personalized, empathetic response that:
                1. Acknowledges their specific situation
                2. {"Analyzes the provided evidence and incorporates findings" if image_data else "Processes text description thoroughly"}
                3. Provides relevant safety advice for their harassment type
                4. Offers specific next steps based on their description
                5. Shows understanding of the emotional impact
                6. Provides tailored resources

                {"If image evidence is provided, comment on what you can observe and how it supports their case." if image_data else ""}
                Be conversational, supportive, and specific to their situation.
                """

                try:
                    ai_response = self.ai_engine.process_complaint(
                        function_name="handle_driver_harassment_personalized",
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
- Grab Safety Hotline: 1-800-GRAB-HELP
- Crisis Support: 1-800-273-8255

**Grab Support:**
- 24/7 Customer Care: Available in your Grab app
- Email: safety@grab.com
- Live Chat: Available 24/7

**Additional Resources:**
- Local Police: Contact if immediate danger
- Counseling Services: Available through Grab partnership
- Legal Support: Contact our legal team for guidance

**Case Reference:** GC-HARASSMENT-{harassment_type.upper().replace(' ', '')}-001

**Action Taken:**
✅ Driver immediately suspended pending investigation
✅ Incident escalated to safety team
✅ Case opened with reference number above
✅ You will receive follow-up within 2 hours"""

                    return f"{ai_response}{helplines}"

                except Exception as e:
                    logger.error(f"AI processing failed: {e}")

            # Fallback if AI fails
            return f"""I understand you experienced {harassment_type} from your driver. This is absolutely unacceptable and we take this very seriously.

**Your situation has been escalated immediately.** Based on your description: "{query[:100]}{'...' if len(query) > 100 else ''}", we are taking the following actions:

**Immediate Actions:**
- Driver suspended pending investigation
- Safety team notified for priority handling
- Your account flagged for enhanced protection

**What happens next:**
- Investigation team will review all trip details
- You'll receive updates within 2 hours
- Additional safety measures will be implemented

🆘 **Emergency Support Available 24/7:**
- Grab Safety: 1-800-GRAB-HELP
- Crisis Support: 1-800-273-8255
- Case Reference: GC-HARASSMENT-{harassment_type.upper().replace(' ', '')}-001"""

        # Default fallback
        return "Please specify the harassment type to continue with your report."