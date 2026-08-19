"""
Grab Cabs Customer Experience Handler
Uses AI models for intelligent complaint resolution
"""

import logging
import os
import sys
import sqlite3
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

    def handle_app_booking_issues(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle app or booking issues with strict 5-step workflow"""
        logger.info(f"Processing app/booking issue: {query[:100]}...")

        # Step 1: Analyze the app or booking issue type from the query
        analysis = self.analyze_app_booking_issue(query)
        logger.info(f"Analysis: {analysis}")

        # Step 2: Check account status and booking context
        context = self.check_booking_context(analysis, query)
        logger.info(f"Context: {context}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Credibility: {credibility_score}/10")

        # Step 4: Decide resolution based on issue type and credibility
        decision = self.decide_app_booking_resolution(analysis, context, credibility_score)
        logger.info(f"Decision: {decision}")

        # Step 5: Generate response with troubleshooting steps and support info
        response = self.generate_app_booking_response(decision, analysis, query, image_data)
        logger.info("App/booking issue response generated successfully")

        return response

    def handle_cancellation_refund_policy_complications(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle cancellation/refund policy complications with strict 5-step workflow"""
        logger.info(f"Processing cancellation/refund policy issue: {query[:100]}...")

        # Step 1: Analyze the cancellation or refund issue type from the query
        analysis = self.analyze_cancellation_refund_issue(query)
        logger.info(f"Analysis: {analysis}")

        # Step 2: Check policy compliance and charge records
        policy_check = self.check_policy_and_charges(analysis, query)
        logger.info(f"Policy check: {policy_check}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Credibility: {credibility_score}/10")

        # Step 4: Decide on refund, waiver, or policy explanation
        decision = self.decide_cancellation_refund_resolution(analysis, policy_check, credibility_score)
        logger.info(f"Decision: {decision}")

        # Step 5: Generate response with policy clarification and resolution
        response = self.generate_cancellation_refund_response(decision, analysis, query, image_data)
        logger.info("Cancellation/refund response generated successfully")

        return response

    def handle_airport_booking_problems(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle airport booking problems with strict 5-step workflow"""
        logger.info(f"Processing airport booking problem: {query[:100]}...")

        # Step 1: Analyze the airport issue type and severity impact
        analysis = self.analyze_airport_issue(query)
        logger.info(f"Analysis: {analysis}")

        # Step 2: Check flight and booking timeline details
        flight_check = self.check_flight_booking_details(analysis, query)
        logger.info(f"Flight check: {flight_check}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Credibility: {credibility_score}/10")

        # Step 4: Decide on compensation and service recovery
        decision = self.decide_airport_resolution(analysis, flight_check, credibility_score)
        logger.info(f"Decision: {decision}")

        # Step 5: Generate priority response with compensation and escalation
        response = self.generate_airport_response(decision, analysis, query, image_data)
        logger.info("Airport booking response generated successfully")

        return response

    def handle_driver_harassment_complaint(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle driver harassment complaints with strict 5-step workflow"""
        logger.info(f"Processing driver harassment complaint: {query[:100]}...")

        # Step 1: Analyze the harassment type and incident severity
        analysis = self.analyze_harassment_incident(query)
        logger.info(f"Analysis: {analysis}")

        # Step 2: Check incident evidence and driver record
        evidence_check = self.check_harassment_evidence(analysis, query, image_data)
        logger.info(f"Evidence check: {evidence_check}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Credibility: {credibility_score}/10")

        # Step 4: Decide driver action and customer support measures
        decision = self.decide_harassment_resolution(analysis, evidence_check, credibility_score)
        logger.info(f"Decision: {decision}")

        # Step 5: Generate empathetic response with safety resources and case actions
        response = self.generate_harassment_response(decision, analysis, query, image_data)
        logger.info("Driver harassment response generated successfully")

        return response

    # ===== SUPPORTING METHODS FOR STRICT WORKFLOWS =====

    def _db_path(self) -> Optional[str]:
        """Resolve the path to the GrabHack database, or None if it cannot be found"""
        paths = ['grabhack.db', '../grabhack.db', 'GrabHack/grabhack.db',
                 os.path.join(os.path.dirname(__file__), '../../../grabhack.db')]
        return next((p for p in paths if os.path.exists(p)), None)

    def get_credibility_score(self, username: str) -> int:
        base_score = 7
        if not username or username == "anonymous":
            return max(1, base_score - 2)
        try:
            db_path = self._db_path()
            if not db_path:
                return base_score
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT credibility_score FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else base_score
        except Exception as e:
            logger.error(f"Error fetching credibility: {e}")
            return base_score

    def analyze_app_booking_issue(self, query: str) -> str:
        query_lower = query.lower()
        if any(w in query_lower for w in ['payment', 'charge', 'fare', 'billed']):
            return "payment_issue"
        elif any(w in query_lower for w in ['crash', 'freeze', 'not working', 'app']):
            return "app_technical_issue"
        elif any(w in query_lower for w in ['gps', 'tracking', 'location']):
            return "gps_tracking_issue"
        elif any(w in query_lower for w in ['book', 'booking', 'failed', 'unable']):
            return "booking_failure"
        else:
            return "general_app_issue"

    def check_booking_context(self, analysis: str, query: str) -> str:
        if analysis == "payment_issue":
            return "payment_context_flagged_for_review"
        elif analysis == "app_technical_issue":
            return "technical_team_notified"
        elif analysis == "booking_failure":
            return "booking_system_check_initiated"
        return "standard_support_context"

    def decide_app_booking_resolution(self, analysis: str, context: str, credibility_score: int) -> str:
        # A confirmed system-side failure is ours to fix regardless of rider standing
        if context == "booking_system_check_initiated":
            return "rebooking_with_discount"
        elif context == "technical_team_notified" and credibility_score >= 5:
            return "priority_technical_support"
        elif credibility_score >= 7:
            if analysis == "payment_issue":
                return "immediate_refund_investigation"
            elif analysis == "app_technical_issue":
                return "priority_technical_support"
            elif analysis == "booking_failure":
                return "rebooking_with_discount"
            return "full_support_with_escalation"
        else:
            return "standard_support_with_review"

    def generate_app_booking_response(self, decision: str, analysis: str, query: str, image_data: Optional[str] = None) -> str:
        if self.ai_engine:
            try:
                ai_context = f"""
                ISSUE TYPE: {analysis}
                USER DESCRIPTION: {query}
                RESOLUTION DECISION: {decision}

                Generate a technical support response that:
                1. Acknowledges their specific technical issue
                2. Provides immediate troubleshooting steps
                3. Offers workarounds if available
                4. Shows understanding of the inconvenience
                5. Provides clear next steps for resolution

                Be technical but helpful, and specific to their app/booking issue.
                """
                ai_response = self.ai_engine.process_complaint(
                    function_name="handle_app_booking_technical_support",
                    user_query=ai_context,
                    service=self.service,
                    user_type=self.actor,
                    image_data=image_data
                )
                return f"""{ai_response}

📞 **Technical Support Available:**
- 24/7 App Support: Available in your Grab app
- Email: techsupport@grab.com
- Live Chat: Available 24/7

**Immediate Actions:**
✅ Technical team notified
✅ Issue logged for app improvement
✅ Account credited if applicable
✅ Priority support activated

**Case Reference:** GC-TECH-{analysis.upper()}-001"""
            except Exception as e:
                logger.error(f"AI processing failed: {e}")

        return f"""I understand you're experiencing an issue with our app. We're here to resolve this immediately.

**Quick troubleshooting steps:**
1. Force close and restart the Grab app
2. Check your internet connection
3. Update to the latest app version
4. Clear app cache if the problem persists

**Your issue has been escalated to our technical team.** Based on your description: "{query[:100]}{'...' if len(query) > 100 else ''}", we're investigating this immediately.

📞 **Immediate Support:** 1-800-GRAB-TECH
**Case Reference:** GC-TECH-{analysis.upper()}-001"""

    def analyze_cancellation_refund_issue(self, query: str) -> str:
        query_lower = query.lower()
        if any(w in query_lower for w in ['fee', 'charged', 'unfair', 'penalt']):
            return "unfair_cancellation_fee"
        elif any(w in query_lower for w in ['refund not', 'not received', 'not processed']):
            return "refund_not_processed"
        elif any(w in query_lower for w in ['wrong amount', 'incorrect', 'less than']):
            return "incorrect_refund_amount"
        elif any(w in query_lower for w in ['policy', 'explain', 'understand']):
            return "policy_not_clear"
        elif any(w in query_lower for w in ['cancel', 'unable', "can't cancel"]):
            return "unable_to_cancel"
        return "general_cancellation_issue"

    def check_policy_and_charges(self, analysis: str, query: str) -> str:
        if analysis == "unfair_cancellation_fee":
            return "cancellation_fee_policy_applies_within_5_minutes"
        elif analysis == "refund_not_processed":
            return "refund_processing_time_3_to_5_business_days"
        elif analysis == "incorrect_refund_amount":
            return "refund_amount_flagged_for_manual_verification"
        return "standard_policy_applies"

    def decide_cancellation_refund_resolution(self, analysis: str, policy_check: str, credibility_score: int) -> str:
        # An amount our own check flagged is corrected without waiting on standing
        if policy_check == "refund_amount_flagged_for_manual_verification":
            return "full_refund_investigation_and_correction"
        elif policy_check == "refund_processing_time_3_to_5_business_days" and credibility_score >= 5:
            return "priority_refund_processing"
        elif credibility_score >= 7:
            if analysis == "unfair_cancellation_fee":
                return "waive_cancellation_fee_as_goodwill"
            elif analysis == "refund_not_processed":
                return "priority_refund_processing"
            elif analysis == "incorrect_refund_amount":
                return "full_refund_investigation_and_correction"
            return "full_policy_review_with_resolution"
        else:
            return "standard_policy_explanation_with_review"

    def generate_cancellation_refund_response(self, decision: str, analysis: str, query: str, image_data: Optional[str] = None) -> str:
        if self.ai_engine:
            try:
                ai_context = f"""
                POLICY ISSUE TYPE: {analysis}
                USER DESCRIPTION: {query}
                RESOLUTION DECISION: {decision}

                Generate a policy support response that:
                1. Acknowledges their policy concern
                2. Explains relevant policies clearly
                3. Provides resolution or compensation if appropriate
                4. Shows understanding of their frustration
                5. Offers clear next steps for resolution

                Be empathetic but clear about policies, specific to their cancellation/refund issue.
                """
                ai_response = self.ai_engine.process_complaint(
                    function_name="handle_cancellation_refund_policy_support",
                    user_query=ai_context,
                    service=self.service,
                    user_type=self.actor,
                    image_data=image_data
                )
                return f"""{ai_response}

💰 **Policy & Billing Support:**
- 24/7 Billing Support: Available in your Grab app
- Email: billing@grab.com
- Policy Center: Available in app under "Help"

**Immediate Actions:**
✅ Policy team reviewing your case
✅ Account flagged for manual review
✅ Refund processing if applicable
✅ Policy clarification provided

**Case Reference:** GC-POLICY-{analysis.upper()}-001"""
            except Exception as e:
                logger.error(f"AI processing failed: {e}")

        return f"""I understand your concern about your cancellation/refund. Our policies should be clear and fair, and we're here to resolve this for you.

**We're reviewing your case immediately.** Based on your description: "{query[:100]}{'...' if len(query) > 100 else ''}", our policy team will investigate this matter.

**What we're doing:**
1. Manual review of your case
2. Policy clarification if needed
3. Refund processing if applicable
4. Account adjustment if warranted

💰 **Immediate Support:** 1-800-GRAB-BILLING
**Case Reference:** GC-POLICY-{analysis.upper()}-001"""

    def analyze_airport_issue(self, query: str) -> str:
        query_lower = query.lower()
        if any(w in query_lower for w in ['missed flight', 'late', 'delayed arrival']):
            return "missed_flight_due_to_late_driver"
        elif any(w in query_lower for w in ['wrong terminal', 'wrong airport']):
            return "wrong_terminal_or_airport"
        elif any(w in query_lower for w in ['sync', 'flight update', 'not updated']):
            return "flight_sync_issue"
        elif any(w in query_lower for w in ['pickup', 'driver not found', 'no driver']):
            return "airport_pickup_problem"
        elif any(w in query_lower for w in ['delay', 'flight delay', 'rebooking']):
            return "flight_delay_complication"
        return "general_airport_issue"

    def check_flight_booking_details(self, analysis: str, query: str) -> str:
        if analysis == "missed_flight_due_to_late_driver":
            return "critical_impact_flight_missed_full_compensation_review"
        elif analysis == "wrong_terminal_or_airport":
            return "navigation_error_driver_accountability_check"
        elif analysis == "airport_pickup_problem":
            return "driver_dispatch_logs_reviewed"
        return "standard_airport_case_review"

    def decide_airport_resolution(self, analysis: str, flight_check: str, credibility_score: int) -> str:
        # A missed flight is an unrecoverable loss, and a driver navigation error is
        # provable from our own dispatch data, so neither waits on a credibility score
        if flight_check == "critical_impact_flight_missed_full_compensation_review":
            return "full_compensation_for_rebooking_and_losses"
        elif flight_check == "navigation_error_driver_accountability_check":
            return "full_refund_plus_additional_compensation"
        elif flight_check == "driver_dispatch_logs_reviewed" and credibility_score >= 5:
            return "priority_refund_and_service_credit"
        elif credibility_score >= 6:
            if analysis == "missed_flight_due_to_late_driver":
                return "full_compensation_for_rebooking_and_losses"
            elif analysis == "wrong_terminal_or_airport":
                return "full_refund_plus_additional_compensation"
            elif analysis == "airport_pickup_problem":
                return "priority_refund_and_service_credit"
            return "premium_service_recovery_with_compensation"
        else:
            return "standard_investigation_with_partial_compensation"

    def generate_airport_response(self, decision: str, analysis: str, query: str, image_data: Optional[str] = None) -> str:
        if self.ai_engine:
            try:
                ai_context = f"""
                AIRPORT ISSUE TYPE: {analysis}
                USER DESCRIPTION: {query}
                RESOLUTION DECISION: {decision}

                Generate an airport support response that:
                1. Acknowledges the severe impact of airport/flight issues
                2. Takes full responsibility for the service failure
                3. Provides immediate compensation/solution
                4. Shows understanding of travel stress and costs
                5. Offers premium service recovery

                Be very apologetic and generous with compensation for airport issues.
                """
                ai_response = self.ai_engine.process_complaint(
                    function_name="handle_airport_booking_priority_support",
                    user_query=ai_context,
                    service=self.service,
                    user_type=self.actor,
                    image_data=image_data
                )
                return f"""{ai_response}

✈️ **Airport Priority Support:**
- 24/7 Airport Support: 1-800-GRAB-AIRPORT
- Priority Email: airport@grab.com
- Emergency Travel Support: Available 24/7

**Immediate Actions:**
✅ Airport team escalating your case
✅ Compensation being processed
✅ Premium service recovery activated
✅ Future airport bookings prioritized

**Case Reference:** GC-AIRPORT-{analysis.upper()}-001"""
            except Exception as e:
                logger.error(f"AI processing failed: {e}")

        return f"""I am deeply sorry about this airport issue. Airport incidents are our highest priority and we take full responsibility for this disruption.

**Immediate compensation being processed.** Based on your description: "{query[:100]}{'...' if len(query) > 100 else ''}", our airport team is handling your case with maximum priority.

**What we're doing right now:**
1. Processing immediate compensation
2. Reviewing additional costs you incurred
3. Providing premium service recovery
4. Ensuring this doesn't happen again

✈️ **Emergency Airport Support:** 1-800-GRAB-AIRPORT
**Case Reference:** GC-AIRPORT-{analysis.upper()}-001"""

    def analyze_harassment_incident(self, query: str) -> str:
        query_lower = query.lower()
        if any(w in query_lower for w in ['threat', 'threaten', 'dangerous']):
            return "threats"
        elif any(w in query_lower for w in ['verbal', 'shout', 'scream', 'insult', 'abuse']):
            return "verbal_abuse"
        elif any(w in query_lower for w in ['physical', 'hit', 'push', 'touch', 'assault']):
            return "physical_abuse"
        elif any(w in query_lower for w in ['stalk', 'follow', 'tracking', 'watching']):
            return "stalking"
        elif any(w in query_lower for w in ['inappropriate', 'uncomfortable', 'harass', 'sexual']):
            return "inappropriate_behaviour"
        return "general_harassment"

    def check_harassment_evidence(self, analysis: str, query: str, image_data: Optional[str] = None) -> str:
        has_image = image_data is not None
        if analysis == "physical_abuse":
            return f"critical_severity_immediate_escalation_image_evidence={'yes' if has_image else 'no'}"
        elif analysis == "threats":
            return f"high_severity_safety_team_alert_image_evidence={'yes' if has_image else 'no'}"
        elif analysis in ["verbal_abuse", "inappropriate_behaviour"]:
            return f"medium_severity_driver_review_triggered_image_evidence={'yes' if has_image else 'no'}"
        return f"standard_review_image_evidence={'yes' if has_image else 'no'}"

    def decide_harassment_resolution(self, analysis: str, evidence_check: str, credibility_score: int) -> str:
        if analysis in ["physical_abuse", "threats"]:
            return "immediate_driver_suspension_emergency_escalation"
        # Submitted image evidence carries the case further than standing alone would
        elif evidence_check.endswith("image_evidence=yes"):
            return "driver_suspended_pending_investigation_full_support"
        elif credibility_score >= 6:
            if analysis in ["verbal_abuse", "inappropriate_behaviour"]:
                return "driver_suspended_pending_investigation_full_support"
            return "driver_review_initiated_customer_support_provided"
        else:
            return "standard_investigation_with_customer_support"

    def generate_harassment_response(self, decision: str, analysis: str, query: str, image_data: Optional[str] = None) -> str:
        if self.ai_engine:
            try:
                ai_context = f"""
                HARASSMENT TYPE: {analysis}
                USER DESCRIPTION: {query}
                RESOLUTION DECISION: {decision}
                IMAGE PROVIDED: {"Yes - analyze for evidence" if image_data else "No"}

                Generate a personalized, empathetic response that:
                1. Acknowledges their specific situation with genuine care
                2. {"Analyzes the provided evidence and incorporates findings" if image_data else "Processes text description thoroughly"}
                3. Provides relevant safety advice for their harassment type
                4. Offers specific next steps based on their description
                5. Shows understanding of the emotional impact
                6. Provides tailored safety resources

                Be conversational, supportive, and specific to their situation.
                """
                ai_response = self.ai_engine.process_complaint(
                    function_name="handle_driver_harassment_personalized",
                    user_query=ai_context,
                    service=self.service,
                    user_type=self.actor,
                    image_data=image_data
                )
                return f"""{ai_response}

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

**Case Reference:** GC-HARASSMENT-{analysis.upper()}-001

**Action Taken:**
✅ Driver immediately suspended pending investigation
✅ Incident escalated to safety team
✅ Case opened with reference number above
✅ You will receive follow-up within 2 hours"""
            except Exception as e:
                logger.error(f"AI processing failed: {e}")

        return f"""I understand you experienced {analysis.replace('_', ' ')} from your driver. This is absolutely unacceptable and we take this very seriously.

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
- Case Reference: GC-HARASSMENT-{analysis.upper()}-001"""
