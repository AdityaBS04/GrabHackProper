"""
Grab Express Customer Technical Handler
Handles technical issues for express delivery service
"""

import logging
import os
import sys
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine_fixed import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class TechnicalHandler:
    """Express delivery technical issues management with strict workflows"""

    def __init__(self):
        self.service = "grab_express"
        self.actor = "customer"
        self.handler_type = "technical_handler"
        try:
            self.ai_engine = EnhancedAgenticAIEngine()
        except Exception as e:
            logger.warning(f"AI engine initialization failed: {e}")
            self.ai_engine = None

    def handle_auto_cancellation(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle delivery auto-cancelled without reason with strict 5-step workflow"""
        logger.info(f"Processing auto-cancellation complaint: {query[:100]}...")

        # Step 1: Identify the type of auto-cancellation scenario
        cancellation_analysis = self.analyze_auto_cancellation(query)
        logger.info(f"Cancellation analysis: {cancellation_analysis}")

        # Step 2: Check if the cancellation caused significant disruption
        disruption_assessment = self.assess_cancellation_disruption(cancellation_analysis, query)
        logger.info(f"Disruption assessment: {disruption_assessment}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on rebooking and compensation action
        decision = self.decide_auto_cancellation_resolution(cancellation_analysis, disruption_assessment, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with rebooking confirmation and compensation
        response = self.generate_auto_cancellation_response(decision, cancellation_analysis, query)
        logger.info("Auto-cancellation response generated successfully")
        return response

    def handle_delivery_status_error(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle app showing delivered but package not received with strict 5-step workflow"""
        logger.info(f"Processing delivery status error complaint: {query[:100]}...")

        # Step 1: Identify the status error scenario
        status_analysis = self.analyze_delivery_status_error(query)
        logger.info(f"Status analysis: {status_analysis}")

        # Step 2: Validate actual delivery status against GPS and partner records
        gps_validation = self.validate_status_with_records(status_analysis, username)
        logger.info(f"GPS validation: {gps_validation}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on package investigation and resolution action
        decision = self.decide_status_error_resolution(status_analysis, gps_validation, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with investigation and redelivery details
        response = self.generate_status_error_response(decision, status_analysis, query)
        logger.info("Delivery status error response generated successfully")
        return response

    def handle_tracking_status_error(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle wrong or stuck tracking status with strict 5-step workflow"""
        logger.info(f"Processing tracking status error complaint: {query[:100]}...")

        # Step 1: Identify the tracking error type
        tracking_analysis = self.analyze_tracking_error(query)
        logger.info(f"Tracking analysis: {tracking_analysis}")

        # Step 2: Check the actual delivery progress in backend systems
        backend_check = self.check_backend_delivery_status(tracking_analysis, username)
        logger.info(f"Backend check: {backend_check}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on tracking fix and ETA update
        decision = self.decide_tracking_resolution(tracking_analysis, backend_check, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with corrected tracking information
        response = self.generate_tracking_response(decision, tracking_analysis, query)
        logger.info("Tracking status error response generated successfully")
        return response

    def handle_coupon_offers_error(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle coupons or offers not applied correctly with strict 5-step workflow"""
        logger.info(f"Processing coupon/offer error complaint: {query[:100]}...")

        # Step 1: Identify the coupon or offer application error type
        coupon_analysis = self.analyze_coupon_error(query)
        logger.info(f"Coupon analysis: {coupon_analysis}")

        # Step 2: Validate coupon eligibility and application rules
        coupon_validation = self.validate_coupon_eligibility(coupon_analysis, username)
        logger.info(f"Coupon validation: {coupon_validation}")

        # Step 3: Check customer credibility score
        credibility_score = self.get_credibility_score(username)
        logger.info(f"Customer credibility: {credibility_score}/10")

        # Step 4: Decide on retroactive discount application or credit
        decision = self.decide_coupon_resolution(coupon_analysis, coupon_validation, credibility_score)
        logger.info(f"Resolution decision: {decision}")

        # Step 5: Generate response with discount correction and credit details
        response = self.generate_coupon_response(decision, coupon_analysis, query)
        logger.info("Coupon/offer error response generated successfully")
        return response

    # ===== SUPPORTING METHODS FOR STRICT WORKFLOWS =====

    def _db_path(self) -> Optional[str]:
        """Resolve the path to the GrabHack database, or None if it cannot be found"""
        paths = ['grabhack.db', '../grabhack.db', 'GrabHack/grabhack.db',
                 os.path.join(os.path.dirname(__file__), '../../../grabhack.db')]
        return next((p for p in paths if os.path.exists(p)), None)

    def get_credibility_score(self, username: str) -> int:
        """Get customer credibility score from database"""
        import sqlite3
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

    def analyze_auto_cancellation(self, query: str) -> str:
        """Identify the auto-cancellation scenario"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['no driver', 'driver not found', 'partner unavailable']):
            return "NO_PARTNER_AVAILABLE"
        elif any(w in query_lower for w in ['system', 'app', 'technical', 'glitch']):
            return "SYSTEM_TECHNICAL_ERROR"
        elif any(w in query_lower for w in ['payment', 'card', 'declined']):
            return "PAYMENT_PROCESSING_FAILURE"
        return "UNKNOWN_AUTO_CANCELLATION"

    def assess_cancellation_disruption(self, analysis: str, query: str) -> str:
        """Assess how disruptive the auto-cancellation was"""
        if any(w in query.lower() for w in ['urgent', 'important', 'time-sensitive']):
            return "HIGH_DISRUPTION"
        return "MODERATE_DISRUPTION"

    def decide_auto_cancellation_resolution(self, analysis: str, disruption: str, credibility: int) -> str:
        """Decide resolution for auto-cancellation"""
        if disruption == "HIGH_DISRUPTION" and credibility >= 6:
            return "PRIORITY_REBOOKING_FULL_COMPENSATION"
        # A cancellation caused by our own systems is compensated without a credibility bar
        elif analysis == "SYSTEM_TECHNICAL_ERROR" and disruption == "HIGH_DISRUPTION":
            return "PRIORITY_REBOOKING_FULL_COMPENSATION"
        elif analysis == "SYSTEM_TECHNICAL_ERROR":
            return "IMMEDIATE_REBOOKING_VOUCHER"
        elif credibility >= 5:
            return "IMMEDIATE_REBOOKING_VOUCHER"
        return "REBOOKING_AND_APOLOGY"

    def generate_auto_cancellation_response(self, decision: str, analysis: str, query: str) -> str:
        """Generate auto-cancellation response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_auto_cancellation",
                    user_query=f"DECISION: {decision} | CANCELLATION: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "PRIORITY_REBOOKING_FULL_COMPENSATION": "We sincerely apologize for the unexpected cancellation. Your delivery has been immediately rebooked with priority status and full compensation has been applied to your account.",
            "IMMEDIATE_REBOOKING_VOUCHER": "We have rebooked your delivery immediately. A voucher credit has been added to your account as compensation for the inconvenience.",
            "REBOOKING_AND_APOLOGY": "We are sorry for the auto-cancellation. Your delivery has been rebooked and should be completed within the standard timeframe. We are investigating the cause of the cancellation."
        }
        return responses.get(decision, "System auto-cancellations are being investigated. We have rebooked your delivery immediately and added compensation to your account.")

    def analyze_delivery_status_error(self, query: str) -> str:
        """Identify the type of delivery status discrepancy"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['shows delivered', 'marked delivered', 'says delivered']):
            return "FALSE_DELIVERED_STATUS"
        elif any(w in query_lower for w in ['wrong status', 'incorrect status']):
            return "INCORRECT_STATUS_DISPLAY"
        return "GENERAL_STATUS_DISCREPANCY"

    def validate_status_with_records(self, analysis: str, username: str) -> str:
        """Validate delivery status against the order record and its drop coordinates"""
        import sqlite3
        db_path = self._db_path()
        if not db_path or not username or username == "anonymous":
            return "RECORDS_UNAVAILABLE"
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''SELECT status, end_latitude, end_longitude FROM orders
                              WHERE username = ? AND service = ?
                              ORDER BY date DESC LIMIT 1''',
                           (username, self.service))
            row = cursor.fetchone()
            conn.close()
            if not row:
                return "RECORDS_UNAVAILABLE"
            status, end_lat, end_lng = row
            # A completed order with no drop coordinates logged means the partner
            # never registered arrival at the destination
            if (status or "").lower() == 'completed' and (end_lat is None or end_lng is None):
                return "DELIVERY_UNCONFIRMED_BY_GPS"
            elif (status or "").lower() == 'completed':
                return "DELIVERY_CONFIRMED_BY_GPS"
            return "ORDER_NOT_MARKED_DELIVERED"
        except Exception as e:
            logger.error(f"Error validating status with records: {e}")
            return "RECORDS_UNAVAILABLE"

    def decide_status_error_resolution(self, analysis: str, gps_check: str, credibility: int) -> str:
        """Decide resolution for delivery status error"""
        # GPS never confirming the drop backs the customer's account outright
        if gps_check == "DELIVERY_UNCONFIRMED_BY_GPS":
            return "IMMEDIATE_INVESTIGATION_REPLACEMENT_DELIVERY"
        elif analysis == "FALSE_DELIVERED_STATUS" and credibility >= 6:
            return "IMMEDIATE_INVESTIGATION_REPLACEMENT_DELIVERY"
        elif gps_check == "ORDER_NOT_MARKED_DELIVERED":
            return "STATUS_CORRECTED_REDELIVERY_ARRANGED"
        elif gps_check == "DELIVERY_CONFIRMED_BY_GPS" and credibility < 6:
            return "FULL_INVESTIGATION_INITIATED"
        elif credibility >= 5:
            return "STATUS_CORRECTED_REDELIVERY_ARRANGED"
        return "FULL_INVESTIGATION_INITIATED"

    def generate_status_error_response(self, decision: str, analysis: str, query: str) -> str:
        """Generate delivery status error response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_delivery_status_error",
                    user_query=f"DECISION: {decision} | STATUS_ERROR: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "IMMEDIATE_INVESTIGATION_REPLACEMENT_DELIVERY": "We are urgently investigating the incorrect delivery status. A replacement delivery has been arranged and our team is tracing the whereabouts of your original package.",
            "STATUS_CORRECTED_REDELIVERY_ARRANGED": "We have corrected the delivery status error in our system. A redelivery has been arranged and you will receive accurate tracking shortly.",
            "FULL_INVESTIGATION_INITIATED": "Your delivery status discrepancy has been escalated. We are reviewing GPS data, delivery partner logs, and system records to resolve this within 4 hours."
        }
        return responses.get(decision, "Delivery status discrepancies are being resolved. We are verifying the actual delivery status and will arrange redelivery if needed.")

    def analyze_tracking_error(self, query: str) -> str:
        """Identify the type of tracking error"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['stuck', 'not updating', 'no update']):
            return "TRACKING_STUCK_NO_UPDATE"
        elif any(w in query_lower for w in ['wrong location', 'wrong place', 'incorrect']):
            return "WRONG_LOCATION_IN_TRACKING"
        return "GENERAL_TRACKING_ERROR"

    def check_backend_delivery_status(self, analysis: str, username: str) -> str:
        """Check actual delivery progress in backend systems"""
        import sqlite3
        db_path = self._db_path()
        if not db_path or not username or username == "anonymous":
            return "BACKEND_STATUS_UNAVAILABLE"
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''SELECT status FROM orders
                              WHERE username = ? AND service = ?
                              ORDER BY date DESC LIMIT 1''',
                           (username, self.service))
            row = cursor.fetchone()
            conn.close()
            if not row:
                return "BACKEND_STATUS_UNAVAILABLE"
            status = (row[0] or "").lower()
            if status in ('in_progress', 'active'):
                return "BACKEND_SHOWS_IN_TRANSIT"
            elif status == 'completed':
                return "BACKEND_SHOWS_DELIVERED"
            return "BACKEND_SHOWS_NOT_DISPATCHED"
        except Exception as e:
            logger.error(f"Error checking backend delivery status: {e}")
            return "BACKEND_STATUS_UNAVAILABLE"

    def decide_tracking_resolution(self, analysis: str, backend_check: str, credibility: int) -> str:
        """Decide resolution for tracking error"""
        # If the backend has a live position, the app just needs a refresh
        if backend_check == "BACKEND_SHOWS_IN_TRANSIT":
            return "TRACKING_REFRESHED_ETA_UPDATED"
        elif analysis == "TRACKING_STUCK_NO_UPDATE" and credibility >= 5:
            return "TRACKING_REFRESHED_ETA_UPDATED"
        elif backend_check in ("BACKEND_SHOWS_DELIVERED", "BACKEND_SHOWS_NOT_DISPATCHED"):
            return "MANUAL_STATUS_UPDATE_PROVIDED"
        elif credibility >= 4:
            return "MANUAL_STATUS_UPDATE_PROVIDED"
        return "TECHNICAL_INVESTIGATION_INITIATED"

    def generate_tracking_response(self, decision: str, analysis: str, query: str) -> str:
        """Generate tracking error response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_tracking_status_error",
                    user_query=f"DECISION: {decision} | TRACKING_ERROR: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "TRACKING_REFRESHED_ETA_UPDATED": "We have refreshed your delivery tracking. The correct status and updated ETA is now showing in your app. Your delivery is on its way as expected.",
            "MANUAL_STATUS_UPDATE_PROVIDED": "We have manually updated your delivery status. Based on our backend records, your package is currently with the delivery partner and expected within 2 hours.",
            "TECHNICAL_INVESTIGATION_INITIATED": "Our technical team is investigating the tracking system error. Real-time updates will resume shortly and you will receive notifications when the status changes."
        }
        return responses.get(decision, "Tracking system errors are being fixed. We will provide accurate real-time updates and ensure proper delivery completion.")

    def analyze_coupon_error(self, query: str) -> str:
        """Identify the type of coupon or offer error"""
        query_lower = query.lower()
        if any(w in query_lower for w in ['not applied', 'not working', "didn't work"]):
            return "COUPON_NOT_APPLIED"
        elif any(w in query_lower for w in ['expired', 'invalid', 'not valid']):
            return "COUPON_INVALID_OR_EXPIRED"
        elif any(w in query_lower for w in ['wrong discount', 'less discount', 'partial']):
            return "INCORRECT_DISCOUNT_AMOUNT"
        return "GENERAL_COUPON_ERROR"

    def validate_coupon_eligibility(self, analysis: str, username: str) -> str:
        """Validate coupon eligibility against the customer's order history"""
        import sqlite3
        db_path = self._db_path()
        if not db_path or not username or username == "anonymous":
            return "ELIGIBILITY_UNVERIFIED"
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM orders WHERE username = ? AND service = ?',
                           (username, self.service))
            order_count = cursor.fetchone()[0]
            conn.close()
            # An expired or invalid code is a terms issue no matter the history
            if analysis == "COUPON_INVALID_OR_EXPIRED":
                return "COUPON_TERMS_NOT_MET"
            elif order_count > 0:
                return "CUSTOMER_ELIGIBLE_FOR_OFFER"
            return "NO_QUALIFYING_ORDER_FOUND"
        except Exception as e:
            logger.error(f"Error validating coupon eligibility: {e}")
            return "ELIGIBILITY_UNVERIFIED"

    def decide_coupon_resolution(self, analysis: str, validation: str, credibility: int) -> str:
        """Decide resolution for coupon or offer error"""
        if validation == "COUPON_TERMS_NOT_MET":
            return "COUPON_ELIGIBILITY_REVIEWED"
        elif analysis == "INCORRECT_DISCOUNT_AMOUNT":
            return "DIFFERENCE_CREDITED_TO_ACCOUNT"
        elif validation == "CUSTOMER_ELIGIBLE_FOR_OFFER" and analysis == "COUPON_NOT_APPLIED":
            return "DISCOUNT_APPLIED_RETROACTIVELY"
        elif analysis == "COUPON_NOT_APPLIED" and credibility >= 6:
            return "DISCOUNT_APPLIED_RETROACTIVELY"
        elif credibility >= 5:
            return "EQUIVALENT_VOUCHER_ISSUED"
        return "COUPON_ELIGIBILITY_REVIEWED"

    def generate_coupon_response(self, decision: str, analysis: str, query: str) -> str:
        """Generate coupon error response"""
        if self.ai_engine:
            try:
                return self.ai_engine.process_complaint(
                    function_name="handle_coupon_offers_error",
                    user_query=f"DECISION: {decision} | COUPON_ERROR: {analysis} | QUERY: {query}",
                    service=self.service, user_type=self.actor
                )
            except Exception as e:
                logger.error(f"AI failed: {e}")
        responses = {
            "DISCOUNT_APPLIED_RETROACTIVELY": "We have applied the discount retroactively to your order. The savings have been credited to your GrabPay account and will be available immediately.",
            "DIFFERENCE_CREDITED_TO_ACCOUNT": "We identified the discount discrepancy. The correct difference has been credited to your account and will be available for your next order.",
            "EQUIVALENT_VOUCHER_ISSUED": "We are unable to retroactively apply the coupon but an equivalent voucher credit has been issued to your account for future use.",
            "COUPON_ELIGIBILITY_REVIEWED": "Our promotions team has reviewed your coupon eligibility. A detailed explanation of the terms has been sent to your registered email."
        }
        return responses.get(decision, "Promotional offer errors will be corrected immediately. The discount will be applied retroactively and credited to your account within 24 hours.")
