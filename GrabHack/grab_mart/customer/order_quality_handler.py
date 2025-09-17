"""
Grab Mart Customer Order Quality Handler
Uses AI models for intelligent complaint resolution
"""

import logging
import os
import sys
from typing import Optional

# Add parent directory to path to import enhanced_ai_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from enhanced_ai_engine import EnhancedAgenticAIEngine

logger = logging.getLogger(__name__)


class OrderQualityHandler:
    """Customer-focused order accuracy and quality management for grocery delivery with real AI"""

    def __init__(self, groq_api_key: str = None):
        self.service = "grab_mart"
        self.actor = "customer"
        self.handler_type = "order_quality_handler"

        # Initialize AI engine for structured analysis
        try:
            self.ai_engine = EnhancedAgenticAIEngine(groq_api_key)
            logger.info("AI engine initialized successfully for grocery order quality handler")
        except Exception as e:
            logger.warning(f"AI engine initialization failed: {e}. Falling back to basic processing.")
            self.ai_engine = None
        
    def handle_missing_items(self, query: str, image_data: Optional[str] = None, username: str = "anonymous", order_id: str = None) -> str:
        """Handle missing items with database validation and interactive selection"""
        logger.info(f"Processing missing items complaint: {query[:100]}...")

        # Step 1: Get actual order data from database
        actual_order_data = self.get_actual_order_data(username, order_id)
        if not actual_order_data:
            return "❌ Unable to find your order details. Please provide your order ID or contact support."

        # Step 2: Check if this is a follow-up response (customer selected specific items)
        if self._is_item_selection_response(query):
            return self.process_selected_missing_items(query, actual_order_data, username)

        # Step 3: ALWAYS show selection interface first (regardless of image)
        return self.show_missing_items_selection_interface(actual_order_data, image_data, username)

    def handle_wrong_item(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle wrong item delivered with strict 5-step workflow - REQUIRES IMAGE for verification"""
        logger.info(f"Processing wrong item complaint: {query[:100]}...")

        # Step 1: Validate image requirement
        if not image_data:
            return "📷 Please upload a photo of the wrong item you received so we can verify the delivery error."

        # Step 2: Identify what was ordered vs what was received
        item_comparison = self.analyze_wrong_item_delivery(query, image_data)
        logger.info(f"Item comparison result: {item_comparison}")

        # Step 3: Assess severity and value impact of wrong item
        error_severity = self.assess_wrong_item_severity(item_comparison, query)
        logger.info(f"Error severity assessment: {error_severity}")

        # Step 4: Check customer credibility and delivery patterns
        credibility_score = self.get_customer_credibility_score(username)
        delivery_pattern = self.check_wrong_item_complaint_history(username)
        logger.info(f"Customer credibility: {credibility_score}/10, Pattern: {delivery_pattern}")

        # Step 5: Make resolution decision and generate response
        decision = self.decide_wrong_item_resolution(error_severity, credibility_score, delivery_pattern)
        response = self.generate_wrong_item_response(decision, item_comparison, query)
        logger.info(f"Wrong item resolution: {decision}")

        return response

    def handle_quality_issues(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle expired/damaged/poor quality items with strict workflow - REQUIRES IMAGE for assessment"""
        logger.info(f"Processing quality issues complaint: {query[:100]}...")
        
        # Step 1: Validate if image is provided
        if not image_data:
            return "Please upload an image of the product quality issue so we can assess your complaint properly."
        
        # Step 2: Validate the quality issue through image analysis
        validation_result = self.validate_quality_issue_with_image(query, image_data)
        logger.info(f"Validation result: {validation_result}")
        
        # Step 3: Get customer credibility score
        credibility_score = self.get_customer_credibility_score(username)
        logger.info(f"Customer credibility score: {credibility_score}/10")
        
        # Step 4: Use GPT to make final decision based on validation and credibility
        decision = self.reason_with_gpt_quality(validation_result, credibility_score)
        logger.info(f"Final decision: {decision}")
        
        # Step 5: Generate appropriate response
        response = self.generate_quality_response(decision, query)
        logger.info(f"Response generated successfully")
        
        return response
    
    def validate_quality_issue_with_image(self, query: str, image_data: str) -> str:
        """Use AI to validate quality issue from image"""
        validation_prompt = f"""
        Analyze this product quality complaint with image evidence:
        
        Customer Complaint: {query}
        Image: [IMAGE PROVIDED]
        
        Analyze the image and determine if there are visible quality issues:
        - Check for spoilage, mold, discoloration
        - Look for physical damage, contamination
        - Assess if products appear fresh or expired
        - Verify if complaint matches visual evidence
        
        Respond with ONLY one of:
        CLEARLY_SPOILED - Obvious quality issues visible (mold, rot, severe discoloration)
        POSSIBLY_COMPROMISED - Some quality concerns but not definitive
        APPEARS_NORMAL - Products look normal, complaint may be subjective
        INSUFFICIENT_EVIDENCE - Cannot determine quality from image
        """
        
        try:
            # Use the AI engine with image to validate
            result = self.ai_engine.process_complaint(
                function_name="validate_product_quality",
                user_query=validation_prompt,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            
            # Extract validation result from AI response
            if "CLEARLY_SPOILED" in result:
                return "CLEARLY_SPOILED"
            elif "POSSIBLY_COMPROMISED" in result:
                return "POSSIBLY_COMPROMISED"
            elif "APPEARS_NORMAL" in result:
                return "APPEARS_NORMAL"
            else:
                return "INSUFFICIENT_EVIDENCE"
                
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return "INSUFFICIENT_EVIDENCE"
    
    def get_customer_credibility_score(self, username: str) -> int:
        """Calculate customer credibility score based on actual database history"""
        import sqlite3
        import os
        from datetime import datetime, timedelta
        
        base_score = 7  # Start with neutral-high credibility
        
        # Handle anonymous users
        if not username or username == "anonymous":
            return max(1, base_score - 2)
        
        try:
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
                # Fallback to simulated scoring if no database
                return self._get_simulated_credibility_score(username)
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get user's current credibility score from users table
            cursor.execute('''
                SELECT credibility_score 
                FROM users 
                WHERE username = ?
            ''', (username,))
            
            user_result = cursor.fetchone()
            if user_result:
                base_score = user_result[0]
            else:
                base_score = 7  # Default if user not found
            
            # Get user's order history from the new database schema
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_orders,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_orders,
                    COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_orders,
                    AVG(price) as avg_order_value,
                    MIN(date) as first_order_date,
                    MAX(date) as last_order_date
                FROM orders 
                WHERE username = ? AND service = 'grab_mart' AND user_type = 'customer'
            ''', (username,))
            
            result = cursor.fetchone()
            if result:
                total_orders, completed_orders, cancelled_orders, avg_order_value, first_order_date, last_order_date = result
                
                # Calculate credibility based on actual data
                if total_orders > 0:
                    completion_rate = completed_orders / total_orders
                    cancellation_rate = cancelled_orders / total_orders if total_orders > 0 else 0
                    
                    # Adjust score based on completion rate
                    if completion_rate >= 0.9:
                        base_score += 2
                    elif completion_rate >= 0.7:
                        base_score += 1
                    elif completion_rate < 0.5:
                        base_score -= 2
                    
                    # Adjust based on cancellation rate
                    if cancellation_rate > 0.3:
                        base_score -= 2
                    elif cancellation_rate > 0.2:
                        base_score -= 1
                    
                    # Adjust based on order frequency (established customer)
                    if total_orders >= 20:
                        base_score += 2
                    elif total_orders >= 10:
                        base_score += 1
                    
                    # Adjust based on average order value (higher value = more credible)
                    if avg_order_value and avg_order_value >= 50:
                        base_score += 1
                    elif avg_order_value and avg_order_value >= 30:
                        base_score += 0.5
                    
                    # Account tenure bonus
                    if first_order_date:
                        try:
                            first_date = datetime.strptime(first_order_date, '%Y-%m-%d')
                            days_since_first = (datetime.now() - first_date).days
                            if days_since_first > 365:  # More than a year
                                base_score += 1
                            elif days_since_first > 180:  # More than 6 months
                                base_score += 0.5
                        except:
                            pass  # Date parsing failed, skip tenure bonus
            
            # Check for recent complaint history
            cursor.execute('''
                SELECT COUNT(*) 
                FROM complaints 
                WHERE username = ? AND service = 'grab_mart' 
                AND created_at >= datetime('now', '-30 days')
            ''', (username,))
            
            recent_complaints = cursor.fetchone()[0] if cursor.fetchone() else 0
            if recent_complaints > 5:
                base_score -= 2
            elif recent_complaints > 2:
                base_score -= 1
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error calculating credibility score: {e}")
            # Fallback to simulated scoring
            return self._get_simulated_credibility_score(username)
        
        # Ensure score is between 1-10
        final_score = max(1, min(10, int(base_score)))
        
        # Update the credibility score in the database if it has changed significantly
        self._update_credibility_score_if_changed(username, final_score)
        
        return final_score
    
    def _update_credibility_score_if_changed(self, username: str, new_score: int) -> None:
        """Update user's credibility score in database if it has changed"""
        try:
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
                return
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Update the credibility score
            cursor.execute('''
                UPDATE users 
                SET credibility_score = ?
                WHERE username = ?
            ''', (new_score, username))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating credibility score: {e}")
    
    def _get_simulated_credibility_score(self, username: str) -> int:
        """Fallback simulated credibility scoring when database is unavailable"""
        base_score = 7
        
        if "test" in username.lower():
            base_score -= 1
        
        if len(username) > 8:
            base_score += 1
            
        return max(1, min(10, base_score))
    
    def reason_with_gpt_quality(self, validation_result: str, credibility_score: int) -> str:
        """Use GPT to make final decision on quality complaint based on validation and credibility"""
        reasoning_prompt = f"""
        Make a final decision on a product quality complaint based on:
        
        Image Validation Result: {validation_result}
        Customer Credibility Score: {credibility_score}/10
        
        Decision Rules:
        1. If validation = "CLEARLY_SPOILED" AND credibility >= 5: FULL_REFUND
        2. If validation = "POSSIBLY_COMPROMISED" AND credibility >= 7: REPLACEMENT_ORDER
        3. If validation = "POSSIBLY_COMPROMISED" AND credibility < 7: PARTIAL_REFUND
        4. If validation = "APPEARS_NORMAL" AND credibility >= 8: FEEDBACK_ONLY
        5. If validation = "APPEARS_NORMAL" AND credibility < 8: FEEDBACK_ONLY
        6. If validation = "INSUFFICIENT_EVIDENCE": REQUEST_BETTER_IMAGE
        
        Respond with ONLY one of: FULL_REFUND, REPLACEMENT_ORDER, PARTIAL_REFUND, FEEDBACK_ONLY, REQUEST_BETTER_IMAGE
        """
        
        try:
            result = self.ai_engine.process_complaint(
                function_name="reason_quality_decision",
                user_query=reasoning_prompt,
                service=self.service,
                user_type=self.actor
            )
            
            # Extract decision from AI response
            if "FULL_REFUND" in result:
                return "FULL_REFUND"
            elif "REPLACEMENT_ORDER" in result:
                return "REPLACEMENT_ORDER"
            elif "PARTIAL_REFUND" in result:
                return "PARTIAL_REFUND"
            elif "REQUEST_BETTER_IMAGE" in result:
                return "REQUEST_BETTER_IMAGE"
            else:
                return "FEEDBACK_ONLY"
                
        except Exception as e:
            logger.error(f"GPT reasoning error: {str(e)}")
            return "FEEDBACK_ONLY"  # Default to most conservative response
    
    def generate_quality_response(self, decision: str, original_query: str) -> str:
        """Generate appropriate customer response based on decision"""
        if decision == "FULL_REFUND":
            return """We sincerely apologize for the product quality issue. After reviewing the image evidence, we can see there are clear quality problems with your order. 

We are processing a FULL REFUND of your order amount immediately. The refund will be credited to your original payment method within 2-3 business days.

We are also reporting this issue to our supplier to prevent similar problems. Thank you for bringing this to our attention."""
        
        elif decision == "REPLACEMENT_ORDER":
            return """We apologize for the quality concerns with your order. Based on the image you provided, we can see there may be quality issues.

We are arranging a REPLACEMENT ORDER for you at no additional cost. Fresh products will be prepared and delivered within 45-60 minutes.

We will also ensure our supplier addresses the quality control issue. Your replacement order is being prioritized."""
        
        elif decision == "PARTIAL_REFUND":
            return """Thank you for reporting the quality issue with your order. We have reviewed the image evidence you provided.

While the issue may not be severe, we want to make this right. We are processing a PARTIAL REFUND of 50% of your order amount as compensation for the inconvenience.

We will also share your feedback with our supplier to improve their quality standards. The refund will be processed within 24 hours."""
        
        elif decision == "REQUEST_BETTER_IMAGE":
            return """Thank you for reporting the quality issue. To properly assess your complaint, we need a clearer image of the products in question.

Please upload a better quality photo showing:
- Clear view of the product items
- Good lighting to show details
- Close-up of the specific quality issue

Once we receive a clearer image, we can provide an appropriate resolution."""
        
        else:  # FEEDBACK_ONLY
            return """Thank you for sharing your feedback about the product quality. We have reviewed your complaint and the image provided.

While we understand your concern, we will pass this feedback to our supplier for their quality improvement. For any further queries, please contact our support team at mart.support@grabmart.com.

We appreciate your patience and continued trust in our service."""

    def handle_substitution_issues(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle substituted item not acceptable with strict 4-step workflow - IMAGE OPTIONAL for verification"""
        logger.info(f"Processing substitution issues complaint: {query[:100]}...")

        # Step 1: Extract substitution details from complaint
        substitution_details = self.extract_substitution_details(query)
        if not substitution_details["original_item"] or not substitution_details["substitute_item"]:
            return "📝 Please specify what item you ordered and what substitution you received so we can address your concern properly."

        # Step 2: Assess substitution appropriateness and value difference
        substitution_assessment = self.evaluate_substitution_appropriateness(substitution_details, image_data)
        logger.info(f"Substitution assessment: {substitution_assessment}")

        # Step 3: Check customer preference history and credibility
        credibility_score = self.get_customer_credibility_score(username)
        preference_history = self.analyze_customer_substitution_preferences(username)
        logger.info(f"Customer credibility: {credibility_score}/10, Preferences: {preference_history}")

        # Step 4: Make resolution decision based on appropriateness and customer profile
        decision = self.decide_substitution_resolution(substitution_assessment, credibility_score, preference_history)
        response = self.generate_substitution_response(decision, substitution_details, query)
        logger.info(f"Substitution resolution: {decision}")

        return response

    def handle_quantity_mismatch(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle quantity mismatch with strict 6-step workflow - REQUIRES IMAGE to verify portions"""
        logger.info(f"Processing quantity mismatch complaint: {query[:100]}...")

        # Step 1: Validate image requirement for portion verification
        if not image_data:
            return "📷 Please upload a photo of the product quantities you received so we can verify the quantity mismatch."

        # Step 2: Extract expected vs received quantities from complaint
        quantity_details = self.extract_quantity_expectations(query)
        if not quantity_details["items_with_quantities"]:
            return "📝 Please specify which items had incorrect quantities and what you expected vs received."

        # Step 3: Analyze image to measure actual portions/quantities
        portion_analysis = self.analyze_product_portions_from_image(query, image_data, quantity_details)
        logger.info(f"Portion analysis: {portion_analysis}")

        # Step 4: Calculate quantity deviation and monetary impact
        deviation_assessment = self.calculate_quantity_deviation_impact(quantity_details, portion_analysis)
        logger.info(f"Deviation assessment: {deviation_assessment}")

        # Step 5: Validate complaint credibility and check for patterns
        credibility_score = self.get_customer_credibility_score(username)
        quantity_complaint_pattern = self.check_quantity_complaint_history(username)
        logger.info(f"Customer credibility: {credibility_score}/10, Pattern: {quantity_complaint_pattern}")

        # Step 6: Make compensation decision based on deviation severity and credibility
        decision = self.decide_quantity_mismatch_resolution(deviation_assessment, credibility_score, quantity_complaint_pattern)
        response = self.generate_quantity_mismatch_response(decision, deviation_assessment, query)
        logger.info(f"Quantity mismatch resolution: {decision}")

        return response

    # ===== SUPPORTING METHODS FOR STRICT WORKFLOWS =====

    def get_actual_order_data(self, username: str, order_id: str = None) -> dict:
        """Get actual order data from database"""
        import sqlite3

        try:
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
                logger.error("Database not found")
                return None

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get order data - use order_id if provided, otherwise get most recent
            if order_id:
                cursor.execute('''
                    SELECT id, food_items, restaurant_name, price, status, date
                    FROM orders
                    WHERE id = ? AND username = ? AND service = 'grab_mart' AND user_type = 'customer'
                ''', (order_id, username))
            else:
                cursor.execute('''
                    SELECT id, food_items, restaurant_name, price, status, date
                    FROM orders
                    WHERE username = ? AND service = 'grab_mart' AND user_type = 'customer'
                    ORDER BY date DESC LIMIT 1
                ''', (username,))

            result = cursor.fetchone()
            conn.close()

            if not result:
                return None

            order_id_db, items, store_name, price, status, date = result

            # Parse items into a list
            if items:
                # Split by common delimiters and clean up
                items_list = []
                for item in items.replace(',', '\n').replace(';', '\n').split('\n'):
                    item = item.strip()
                    if item:
                        items_list.append(item)
            else:
                items_list = []

            # Format items for display
            formatted_items = '\n'.join([f"• {item}" for item in items_list])

            return {
                'order_id': order_id_db,
                'items_list': items_list,
                'formatted_items': formatted_items,
                'store_name': store_name,
                'price': price,
                'status': status,
                'date': date,
                'total_items_count': len(items_list)
            }

        except Exception as e:
            logger.error(f"Error getting order data: {e}")
            return None

    def _is_item_selection_response(self, query: str) -> bool:
        """Check if the query is a response to item selection (not initial complaint)"""
        query_lower = query.lower()

        # Check for item selection patterns
        selection_patterns = [
            r'item\s*\d+',  # "item 1", "item 2"
            r'items\s*\d+',  # "items 1, 2, 3"
            r'\d+\s*(and|,|\&)',  # "1 and 2", "1, 2, 3"
            r'missing.*\d+',  # "missing 1 and 2"
            r'confirm ai',  # "confirm ai suggestions"
            r'ai analysis',  # "ai analysis is correct"
            r'all items present',  # "all items are present"
            r'nothing missing',  # "nothing is missing"
            r'everything is here',  # "everything is here"
            r'all here',  # "all here"
        ]

        # Also check for specific product item names being selected
        product_keywords = ['bread', 'milk', 'eggs', 'cheese', 'yogurt', 'meat', 'vegetables', 'fruits', 'cereal', 'juice']

        import re

        # Check selection patterns
        for pattern in selection_patterns:
            if re.search(pattern, query_lower):
                return True

        # If it contains product keywords AND selection language, it's probably a selection
        if any(product in query_lower for product in product_keywords):
            if any(word in query_lower for word in ['missing', 'didn\'t receive', 'not get', 'absent', 'only']):
                return True

        # If query is very short and specific (likely a selection response)
        if len(query.strip()) < 50 and any(word in query_lower for word in ['missing', 'present', 'confirm', 'yes', 'no']):
            return True

        return False

    def show_missing_items_selection_interface(self, actual_order_data: dict, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Show interactive interface for customers to select missing items"""
        order_id = actual_order_data['order_id']
        store_name = actual_order_data['store_name']
        items_list = actual_order_data['items_list']

        # If image is provided, run AI analysis and show suggestions
        if image_data:
            try:
                received_items_analysis = self.analyze_received_items_from_image_with_database(
                    "Missing items complaint with image", image_data, actual_order_data
                )
                ai_identified_missing = received_items_analysis.get('items_missing', [])
                ai_confidence = received_items_analysis.get('confidence', 'medium')

                # Create selection format with AI suggestions
                items_with_suggestions = []
                for i, item in enumerate(items_list, 1):
                    if item in ai_identified_missing:
                        items_with_suggestions.append(f"❌ {i}. {item} *(AI suggests: MISSING)*")
                    else:
                        items_with_suggestions.append(f"✅ {i}. {item} *(AI suggests: Present)*")

                confidence_text = f"🎯 High" if ai_confidence == "high" else f"🤔 Medium" if ai_confidence == "medium" else f"❓ Low"

                return f"""🤖 **AI Analysis + Item Selection**

**Your Order:** {order_id} from {store_name}
**AI Confidence:** {confidence_text}

**📝 Select which items are actually missing:**

{chr(10).join(items_with_suggestions)}

**💡 Quick Selection Options:**
- **"Confirm AI suggestions"** - Use AI analysis above
- **"Items 1, 3, 5 are missing"** - Select by numbers
- **"Only the Milk and Bread are missing"** - Select by name
- **"All items are present"** - Nothing is missing

**Choose any method above and I'll process your resolution immediately!**"""

            except Exception as e:
                logger.error(f"AI analysis failed: {e}")
                # Fallback to basic selection if AI fails

        # Create basic selection format (no AI analysis)
        items_with_checkboxes = []
        for i, item in enumerate(items_list, 1):
            items_with_checkboxes.append(f"☐ {i}. {item}")

        return f"""🔍 **Missing Items Selection**

**Your Order:** {order_id} from {store_name}
**Status:** {actual_order_data.get('status', 'completed')}

**📝 Which items are missing from your order?**

{chr(10).join(items_with_checkboxes)}

**💡 How to select missing items:**
- **"Items 1 and 3 are missing"** - Select by numbers
- **"I didn't receive the Milk and Bread"** - Select by name
- **"Missing items 2, 4, and 5"** - Multiple items
- **"All items are present"** - Nothing missing

**📷 Tip:** Upload a photo for AI-assisted selection!

**Select your missing items above and I'll process your refund immediately!**"""

    def process_selected_missing_items(self, query: str, actual_order_data: dict, username: str) -> str:
        """Process customer's selection of missing items"""
        logger.info("Processing customer-selected missing items...")

        # Extract selected missing items from customer response
        selected_missing_items = self.extract_selected_missing_items(query, actual_order_data)

        if not selected_missing_items['items']:
            return """❓ **Please clarify which items are missing**

I couldn't understand which specific items are missing. Please try:
- "Item 1 and 3 are missing"
- "I didn't receive the Milk and Bread"
- "All items are present" (if nothing is missing)
- "Confirm AI analysis" (if you agree with the AI suggestions)

Please be specific so I can help you quickly!"""

        # If customer says no items are missing
        if selected_missing_items['all_present']:
            return f"""✅ **All Items Confirmed Present**

Great! I'm glad to hear that all items from your order {actual_order_data['order_id']} are present.

If you have any other concerns about quality, freshness, or other issues, please let me know and I can help with those separately."""

        # Calculate impact and get credibility
        missing_count = len(selected_missing_items['items'])
        total_count = len(actual_order_data['items_list'])
        missing_percentage = round((missing_count / total_count) * 100, 1) if total_count > 0 else 0
        credibility_score = self.get_customer_credibility_score(username)

        # Make resolution decision
        decision = self.decide_resolution_for_selected_items(
            missing_count, missing_percentage, credibility_score, selected_missing_items
        )

        # Generate final response
        response = self.generate_response_for_selected_items(
            decision, selected_missing_items, actual_order_data, missing_percentage
        )

        logger.info(f"Resolution for selected missing items: {decision}")
        return response

    def extract_selected_missing_items(self, query: str, actual_order_data: dict) -> dict:
        """Extract which items customer selected as missing"""
        items_list = actual_order_data['items_list']
        query_lower = query.lower()

        # Check if customer says all items are present
        if any(phrase in query_lower for phrase in ['all items present', 'nothing missing', 'all here', 'everything is here']):
            return {'items': [], 'all_present': True, 'method': 'explicit_all_present'}

        # Check if customer confirms AI analysis - run AI analysis now
        if 'confirm ai' in query_lower or 'ai suggestions' in query_lower or 'ai analysis' in query_lower:
            return {'items': [], 'all_present': False, 'method': 'confirm_ai_requested', 'needs_image_analysis': True}

        selected_items = []

        # Method 1: Extract by item numbers (e.g., "item 1 and 3", "items 2, 4, 5")
        import re
        number_matches = re.findall(r'item\s*(\d+)|(\d+)', query_lower)
        item_numbers = []
        for match in number_matches:
            if match[0]:  # "item X" format
                item_numbers.append(int(match[0]))
            elif match[1]:  # standalone number
                item_numbers.append(int(match[1]))

        # Add items by number
        for num in item_numbers:
            if 1 <= num <= len(items_list):
                item_name = items_list[num - 1]
                if item_name not in selected_items:
                    selected_items.append(item_name)

        # Method 2: Extract by item names mentioned in query
        for item in items_list:
            # Check if item name (or parts of it) are mentioned in the query
            item_words = item.lower().split()
            if len(item_words) >= 2:  # For multi-word items
                if item.lower() in query_lower:
                    if item not in selected_items:
                        selected_items.append(item)
            else:  # For single word items, be more careful
                # Check if the word appears as a separate word (not part of another word)
                if re.search(r'\b' + re.escape(item.lower()) + r'\b', query_lower):
                    if item not in selected_items:
                        selected_items.append(item)

        return {
            'items': selected_items,
            'all_present': False,
            'method': 'manual_selection',
            'item_numbers': item_numbers
        }

    def decide_resolution_for_selected_items(self, missing_count: int, missing_percentage: float,
                                           credibility_score: int, selected_missing_items: dict) -> str:
        """Decide resolution based on customer-selected missing items"""

        if missing_count == 0:
            return "NO_ITEMS_MISSING"
        elif missing_percentage >= 70 and credibility_score >= 7:
            return "FULL_REFUND_MAJOR"
        elif missing_percentage >= 50 and credibility_score >= 6:
            return "REPLACEMENT_ORDER"
        elif missing_percentage >= 30 and credibility_score >= 5:
            return "PARTIAL_REFUND_SIGNIFICANT"
        elif missing_count == 1 and credibility_score >= 5:
            return "SINGLE_ITEM_REFUND"
        elif missing_count <= 2 and credibility_score >= 4:
            return "MULTIPLE_ITEM_REFUND"
        elif credibility_score <= 3:
            return "VERIFICATION_REQUIRED"
        else:
            return "STORE_CREDIT"

    def generate_response_for_selected_items(self, decision: str, selected_missing_items: dict,
                                           actual_order_data: dict, missing_percentage: float) -> str:
        """Generate response based on customer's item selection"""
        missing_items = selected_missing_items['items']
        missing_count = len(missing_items)
        order_id = actual_order_data['order_id']
        store_name = actual_order_data['store_name']

        if decision == "FULL_REFUND_MAJOR":
            return f"""💰 **FULL REFUND APPROVED**

**Missing Items Confirmed:**
📋 Order: {order_id} from {store_name}
❌ **Missing Items ({missing_count} items - {missing_percentage}% of order):**
{chr(10).join([f"• {item}" for item in missing_items])}

**✅ Resolution:**
💵 **FULL REFUND** of ${actual_order_data.get('price', 0):.2f} processing now
⏰ Refund will appear in 2-3 business days
🔴 Store has been notified for immediate review

This is a serious delivery failure. We sincerely apologize and are investigating this incident."""

        elif decision == "REPLACEMENT_ORDER":
            return f"""🛒 **REPLACEMENT ORDER APPROVED**

**Missing Items Confirmed:**
📋 Order: {order_id} from {store_name}
❌ **Missing Items ({missing_count} items - {missing_percentage}% of order):**
{chr(10).join([f"• {item}" for item in missing_items])}

**✅ Resolution:**
🚚 **FRESH REPLACEMENT ORDER** being prepared now
⏰ Delivery in 45-60 minutes
🆓 No additional charges
📞 Store contacted to prevent future issues"""

        elif decision == "PARTIAL_REFUND_SIGNIFICANT":
            return f"""💳 **PARTIAL REFUND APPROVED**

**Missing Items Confirmed:**
📋 Order: {order_id} from {store_name}
❌ **Missing Items ({missing_count} items):**
{chr(10).join([f"• {item}" for item in missing_items])}

**✅ Resolution:**
💰 **PARTIAL REFUND** of {missing_percentage}% (${(actual_order_data.get('price', 0) * missing_percentage / 100):.2f})
⏰ Refund processed within 24 hours
📝 Store feedback submitted for quality improvement"""

        elif decision == "SINGLE_ITEM_REFUND":
            return f"""💵 **ITEM REFUND APPROVED**

**Missing Item Confirmed:**
📋 Order: {order_id} from {store_name}
❌ **Missing Item:** {missing_items[0]}

**✅ Resolution:**
🛵 **REPLACEMENT DELIVERY** of missing item OR refund for item value
⏰ Replacement within 30 minutes OR refund within 2 hours
🆓 No additional charges
Thank you for bringing this to our attention!"""

        elif decision == "MULTIPLE_ITEM_REFUND":
            return f"""💳 **REFUND APPROVED**

**Missing Items Confirmed:**
📋 Order: {order_id} from {store_name}
❌ **Missing Items ({missing_count} items):**
{chr(10).join([f"• {item}" for item in missing_items])}

**✅ Resolution:**
💰 **REFUND** for missing items value
⏰ Processed within 4 hours
🔄 Can also arrange replacement if you prefer
📞 Store has been notified"""

        elif decision == "VERIFICATION_REQUIRED":
            return f"""🔍 **Additional Verification Needed**

**Reported Missing Items:**
📋 Order: {order_id} from {store_name}
❓ **Items you reported missing ({missing_count} items):**
{chr(10).join([f"• {item}" for item in missing_items])}

**📷 Next Step:**
Please upload a photo of what you received to help us verify and process your refund quickly.

**Reference ID:** VER-{hash(str(missing_items)) % 10000:04d}"""

        else:  # STORE_CREDIT
            return f"""💳 **STORE CREDIT APPROVED**

**Missing Items Noted:**
📋 Order: {order_id} from {store_name}
📝 **Missing Items ({missing_count} items):**
{chr(10).join([f"• {item}" for item in missing_items])}

**✅ Resolution:**
🎁 **STORE CREDIT** equivalent to missing items value
⏰ Applied to your account within 1 hour
🛒 Use on your next order
🔄 Store feedback submitted for improvement"""

    def analyze_received_items_from_image_with_database(self, query: str, image_data: str, actual_order_data: dict) -> dict:
        """Analyze image to identify received items, comparing against actual order"""
        # For now, return a mock analysis to test the selection interface
        # TODO: Implement AI image analysis once import issues are resolved

        try:
            # Mock analysis - assume some items are missing for testing
            items_list = actual_order_data['items_list']

            # For testing, assume first 2 items are present, others are missing
            items_present = items_list[:2] if len(items_list) > 2 else items_list[:1]
            items_missing = items_list[2:] if len(items_list) > 2 else items_list[1:]

            return {
                "items_present": items_present,
                "items_missing": items_missing,
                "extra_items": [],
                "confidence": "medium",
                "analysis_notes": "Mock analysis for testing - AI engine temporarily disabled"
            }

        except Exception as e:
            logger.error(f"Failed to analyze received items with database: {e}")
            return {
                "items_present": [],
                "items_missing": actual_order_data['items_list'],
                "extra_items": [],
                "confidence": "low",
                "analysis_notes": f"Analysis error: {str(e)}"
            }

    def analyze_wrong_item_delivery(self, query: str, image_data: str) -> dict:
        """Analyze what was ordered vs what was delivered"""
        analysis_prompt = f"""
        Analyze this wrong item delivery complaint:

        Customer Complaint: {query}
        Image: [ATTACHED - showing what they received]

        Identify:
        1. What item did the customer expect to receive?
        2. What item did they actually receive (from image)?
        3. Is this a complete wrong item or a variation/substitution?
        4. Value difference (higher/lower/similar)?

        Return ONLY JSON: {{"expected_item": "item", "received_item": "item", "error_type": "wrong_item/substitution/variant", "value_difference": "higher/lower/similar"}}
        """

        try:
            result = self.ai_engine.process_complaint(
                function_name="analyze_wrong_item",
                user_query=analysis_prompt,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )

            import json
            if "{" in result and "}" in result:
                json_start = result.find("{")
                json_end = result.rfind("}") + 1
                json_str = result[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"expected_item": "unknown", "received_item": "unknown", "error_type": "analysis_failed", "value_difference": "unknown"}

        except Exception as e:
            logger.error(f"Failed to analyze wrong item: {e}")
            return {"expected_item": "unknown", "received_item": "unknown", "error_type": "analysis_error", "value_difference": "unknown"}

    def assess_wrong_item_severity(self, item_comparison: dict, query: str) -> str:
        """Assess severity of wrong item delivery"""
        error_type = item_comparison.get("error_type", "unknown")
        value_difference = item_comparison.get("value_difference", "unknown")

        # Check for allergen/dietary concerns
        query_lower = query.lower()
        dietary_concern = any(word in query_lower for word in ['allerg', 'vegetarian', 'vegan', 'halal', 'kosher', 'gluten', 'lactose'])

        if dietary_concern:
            return "SEVERE_DIETARY"
        elif error_type == "wrong_item" and value_difference == "lower":
            return "SEVERE_VALUE"
        elif error_type == "wrong_item":
            return "MODERATE_WRONG"
        elif error_type == "substitution":
            return "MINOR_SUBSTITUTION"
        else:
            return "UNCLEAR"

    def check_wrong_item_complaint_history(self, username: str) -> str:
        """Check if customer has pattern of wrong item complaints"""
        # Simplified pattern check - in real implementation would query database
        if username == "anonymous":
            return "UNKNOWN_PATTERN"
        elif "test" in username.lower():
            return "HIGH_FREQUENCY"
        else:
            return "NORMAL_PATTERN"

    def decide_wrong_item_resolution(self, error_severity: str, credibility_score: int, delivery_pattern: str) -> str:
        """Decide resolution for wrong item delivery"""
        if error_severity == "SEVERE_DIETARY":
            return "FULL_REFUND_PRIORITY"
        elif error_severity == "SEVERE_VALUE" and credibility_score >= 6:
            return "REPLACEMENT_PLUS_CREDIT"
        elif error_severity == "MODERATE_WRONG" and credibility_score >= 5:
            return "FULL_REPLACEMENT"
        elif error_severity == "MINOR_SUBSTITUTION" and credibility_score >= 7:
            return "PARTIAL_REFUND"
        elif delivery_pattern == "HIGH_FREQUENCY" and credibility_score <= 4:
            return "ESCALATE_REVIEW"
        else:
            return "STANDARD_REPLACEMENT"

    def generate_wrong_item_response(self, decision: str, item_comparison: dict, query: str) -> str:
        """Generate response for wrong item delivery"""
        expected = item_comparison.get("expected_item", "your ordered item")
        received = item_comparison.get("received_item", "the delivered item")

        if decision == "FULL_REFUND_PRIORITY":
            return f"""We sincerely apologize for this serious error. You ordered {expected} but received {received}, which may involve dietary restrictions or allergies.

We are processing an IMMEDIATE FULL REFUND and flagging this as a priority incident. The refund will be processed within 1 hour.

We are also investigating this delivery error to prevent future occurrences involving dietary concerns."""

        elif decision == "REPLACEMENT_PLUS_CREDIT":
            return f"""We apologize for delivering {received} instead of your ordered {expected}. This is clearly a significant error on our part.

We are sending you the correct item ({expected}) immediately at no charge, plus providing additional store credit as compensation for the inconvenience.

Estimated delivery time for correct item: 30-45 minutes."""

        elif decision == "FULL_REPLACEMENT":
            return f"""Thank you for reporting this delivery error. You ordered {expected} but received {received}.

We are sending you the correct item ({expected}) as a replacement at no additional cost. The correct order will be prioritized for delivery.

We apologize for the mix-up and have notified the store."""

        elif decision == "PARTIAL_REFUND":
            return f"""We understand you received {received} instead of {expected}. While this appears to be a reasonable substitution, we want to make it right.

We are providing a partial refund for the difference and will note your preference for future orders.

The refund will be processed within 24 hours."""

        elif decision == "ESCALATE_REVIEW":
            return f"""Your wrong item complaint has been forwarded to our quality assurance team for detailed review.

Reference ID: WRG-{hash(query) % 10000:04d}

You will receive a response within 4-6 hours with a comprehensive resolution."""

        else:  # STANDARD_REPLACEMENT
            return f"""We apologize for the error in your delivery. You ordered {expected} but received {received}.

We are arranging a replacement delivery with the correct item at no additional charge. Estimated delivery time: 45-60 minutes.

Thank you for your patience."""

    def extract_substitution_details(self, query: str) -> dict:
        """Extract substitution details from complaint"""
        extraction_prompt = f"""
        Extract substitution details from this complaint:

        Complaint: {query}

        Identify:
        1. What item was originally ordered?
        2. What substitution was made?
        3. Why is the customer unhappy with the substitution?

        Return ONLY JSON: {{"original_item": "item", "substitute_item": "item", "complaint_reason": "reason"}}
        """

        try:
            result = self.ai_engine.process_complaint(
                function_name="extract_substitution",
                user_query=extraction_prompt,
                service=self.service,
                user_type=self.actor
            )

            import json
            if "{" in result and "}" in result:
                json_start = result.find("{")
                json_end = result.rfind("}") + 1
                json_str = result[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"original_item": "", "substitute_item": "", "complaint_reason": "extraction_failed"}

        except Exception as e:
            logger.error(f"Failed to extract substitution details: {e}")
            return {"original_item": "", "substitute_item": "", "complaint_reason": "extraction_error"}

    def evaluate_substitution_appropriateness(self, substitution_details: dict, image_data: Optional[str] = None) -> dict:
        """Evaluate if the substitution was appropriate"""
        original = substitution_details.get("original_item", "")
        substitute = substitution_details.get("substitute_item", "")
        reason = substitution_details.get("complaint_reason", "")

        # Simple evaluation logic (would be more sophisticated in real implementation)
        if "cheaper" in reason.lower() or "lower quality" in reason.lower():
            appropriateness = "INAPPROPRIATE_VALUE"
        elif "allergic" in reason.lower() or "dietary" in reason.lower():
            appropriateness = "INAPPROPRIATE_DIETARY"
        elif "different category" in reason.lower():
            appropriateness = "INAPPROPRIATE_CATEGORY"
        else:
            appropriateness = "REASONABLE_SUBSTITUTION"

        return {
            "appropriateness": appropriateness,
            "value_impact": "unknown",  # Would analyze from inventory/prices in real implementation
            "category_match": "unknown"
        }

    def analyze_customer_substitution_preferences(self, username: str) -> dict:
        """Analyze customer's historical substitution preferences"""
        # Simplified implementation - would query order history in real system
        return {
            "accepts_substitutions": "unknown",
            "preferred_categories": [],
            "rejected_substitutions": []
        }

    def decide_substitution_resolution(self, substitution_assessment: dict, credibility_score: int, preference_history: dict) -> str:
        """Decide resolution for substitution complaint"""
        appropriateness = substitution_assessment.get("appropriateness", "unknown")

        if appropriateness == "INAPPROPRIATE_DIETARY":
            return "FULL_REFUND_DIETARY"
        elif appropriateness == "INAPPROPRIATE_VALUE" and credibility_score >= 6:
            return "VALUE_DIFFERENCE_REFUND"
        elif appropriateness == "INAPPROPRIATE_CATEGORY" and credibility_score >= 5:
            return "REPLACEMENT_CORRECT_ITEM"
        elif appropriateness == "REASONABLE_SUBSTITUTION" and credibility_score >= 7:
            return "GOODWILL_CREDIT"
        else:
            return "EXPLANATION_ONLY"

    def generate_substitution_response(self, decision: str, substitution_details: dict, query: str) -> str:
        """Generate response for substitution complaint"""
        original = substitution_details.get("original_item", "your ordered item")
        substitute = substitution_details.get("substitute_item", "the substituted item")

        if decision == "FULL_REFUND_DIETARY":
            return f"""We sincerely apologize for substituting {substitute} for {original} without considering dietary requirements.

We are processing a FULL REFUND immediately and have flagged this for our dietary restrictions protocol review.

The refund will be processed within 1 hour."""

        elif decision == "VALUE_DIFFERENCE_REFUND":
            return f"""We understand your concern about receiving {substitute} instead of {original}. The substitution does appear to be of lower value.

We are refunding the price difference and providing additional store credit for the inconvenience.

Future orders will have a note about your substitution preferences."""

        elif decision == "REPLACEMENT_CORRECT_ITEM":
            return f"""You're right that {substitute} is not an appropriate substitution for {original}.

We are sending you the correct item ({original}) at no charge. Estimated delivery: 40-60 minutes.

We will also update our substitution guidelines to prevent similar issues."""

        elif decision == "GOODWILL_CREDIT":
            return f"""While {substitute} is generally considered a reasonable substitution for {original}, we understand it didn't meet your expectations.

We are providing goodwill store credit for your next order and will note your preference to avoid future substitutions.

Thank you for your feedback."""

        else:  # EXPLANATION_ONLY
            return f"""We understand you received {substitute} instead of {original}. This substitution was made due to availability.

Our substitution policy allows for comparable items when originals are unavailable. If you have specific preferences, please add notes to future orders.

We appreciate your understanding."""

    def extract_quantity_expectations(self, query: str) -> dict:
        """Extract quantity expectations from complaint"""
        extraction_prompt = f"""
        Extract quantity details from this complaint:

        Complaint: {query}

        Identify for each item mentioned:
        1. What was the expected quantity/portion size?
        2. What was actually received?
        3. Which specific items had quantity issues?

        Return ONLY JSON: {{"items_with_quantities": [{{"item": "name", "expected": "amount", "received": "amount"}}], "overall_issue": "description"}}
        """

        try:
            result = self.ai_engine.process_complaint(
                function_name="extract_quantities",
                user_query=extraction_prompt,
                service=self.service,
                user_type=self.actor
            )

            import json
            if "{" in result and "}" in result:
                json_start = result.find("{")
                json_end = result.rfind("}") + 1
                json_str = result[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"items_with_quantities": [], "overall_issue": "extraction_failed"}

        except Exception as e:
            logger.error(f"Failed to extract quantity expectations: {e}")
            return {"items_with_quantities": [], "overall_issue": "extraction_error"}

    def analyze_product_portions_from_image(self, query: str, image_data: str, quantity_details: dict) -> dict:
        """Analyze actual product portions from image"""
        analysis_prompt = f"""
        Analyze the product portions in this image:

        Customer expects: {quantity_details.get('items_with_quantities', [])}
        Customer complaint: {query}
        Image: [ATTACHED]

        Assess the actual portions/quantities visible in the image:
        1. Do the portions appear adequate for the price point?
        2. Do they match standard retail portions?
        3. Are there clear quantity deficiencies?

        Return ONLY JSON: {{"portion_assessment": "adequate/below_standard/significantly_low", "confidence": "high/medium/low", "notes": "details"}}
        """

        try:
            result = self.ai_engine.process_complaint(
                function_name="analyze_portions",
                user_query=analysis_prompt,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )

            import json
            if "{" in result and "}" in result:
                json_start = result.find("{")
                json_end = result.rfind("}") + 1
                json_str = result[json_start:json_end]
                return json.loads(json_str)
            else:
                return {"portion_assessment": "unclear", "confidence": "low", "notes": "analysis_failed"}

        except Exception as e:
            logger.error(f"Failed to analyze portions: {e}")
            return {"portion_assessment": "unclear", "confidence": "low", "notes": "analysis_error"}

    def calculate_quantity_deviation_impact(self, quantity_details: dict, portion_analysis: dict) -> dict:
        """Calculate the impact of quantity deviation"""
        items_count = len(quantity_details.get("items_with_quantities", []))
        portion_assessment = portion_analysis.get("portion_assessment", "unclear")
        confidence = portion_analysis.get("confidence", "low")

        if portion_assessment == "significantly_low":
            severity = "SEVERE"
            estimated_impact = "30-50%"
        elif portion_assessment == "below_standard":
            severity = "MODERATE"
            estimated_impact = "15-30%"
        elif portion_assessment == "adequate":
            severity = "MINIMAL"
            estimated_impact = "0-10%"
        else:
            severity = "UNCLEAR"
            estimated_impact = "unknown"

        return {
            "severity": severity,
            "estimated_value_impact": estimated_impact,
            "affected_items_count": items_count,
            "assessment_confidence": confidence
        }

    def check_quantity_complaint_history(self, username: str) -> str:
        """Check customer's history of quantity complaints"""
        # Simplified implementation - would query database in real system
        if username == "anonymous":
            return "UNKNOWN_PATTERN"
        elif "test" in username.lower():
            return "FREQUENT_COMPLAINTS"
        else:
            return "OCCASIONAL_COMPLAINTS"

    def decide_quantity_mismatch_resolution(self, deviation_assessment: dict, credibility_score: int, complaint_pattern: str) -> str:
        """Decide resolution for quantity mismatch"""
        severity = deviation_assessment.get("severity", "UNCLEAR")
        confidence = deviation_assessment.get("assessment_confidence", "low")

        if confidence == "low":
            return "REQUEST_BETTER_IMAGE"
        elif severity == "SEVERE" and credibility_score >= 6:
            return "PARTIAL_REFUND_MAJOR"
        elif severity == "MODERATE" and credibility_score >= 5:
            return "STORE_CREDIT_COMPENSATION"
        elif severity == "MINIMAL" and credibility_score >= 7:
            return "GOODWILL_CREDIT"
        elif complaint_pattern == "FREQUENT_COMPLAINTS" and credibility_score <= 4:
            return "ESCALATE_PATTERN_REVIEW"
        else:
            return "STORE_FEEDBACK_ONLY"

    def generate_quantity_mismatch_response(self, decision: str, deviation_assessment: dict, query: str) -> str:
        """Generate response for quantity mismatch complaint"""
        severity = deviation_assessment.get("severity", "unclear")
        estimated_impact = deviation_assessment.get("estimated_value_impact", "unknown")

        if decision == "PARTIAL_REFUND_MAJOR":
            return f"""After reviewing your photo, we can see that the portions are significantly below our standards. This is not acceptable.

We are processing a PARTIAL REFUND of 40% of your order value to compensate for the inadequate portions (estimated impact: {estimated_impact}).

We are also escalating this to the store for immediate portion size review and staff retraining."""

        elif decision == "STORE_CREDIT_COMPENSATION":
            return f"""Thank you for bringing the portion size issue to our attention. Your photo shows the portions are below our expected standards.

We are providing STORE CREDIT equivalent to 25% of your order value as compensation for the smaller portions.

The store has been notified about portion consistency requirements."""

        elif decision == "GOODWILL_CREDIT":
            return f"""While the portions appear to be within normal range, we understand your expectation for value.

We are providing a small goodwill credit for your next order and will share your feedback with the store.

Thank you for helping us maintain quality standards."""

        elif decision == "REQUEST_BETTER_IMAGE":
            return """To accurately assess the portion sizes, please upload a clearer photo showing:
- All product items with clear scale reference (coin, utensil, or hand for size)
- Good lighting to see portion details
- Full view of containers/packages

This will help us provide fair compensation if portions are indeed inadequate."""

        elif decision == "ESCALATE_PATTERN_REVIEW":
            return f"""Your quantity complaint has been forwarded to our customer experience team for pattern analysis and specialized review.

Reference ID: QTY-{hash(query) % 10000:04d}

You will receive a comprehensive response within 6-8 hours."""

        else:  # STORE_FEEDBACK_ONLY
            return f"""Thank you for your feedback about the portion sizes. We will share your comments with the store to ensure they maintain consistent portion standards.

While the portions appear to be within normal range based on your photo, we appreciate you taking the time to provide feedback.

For future orders, please don't hesitate to contact us immediately if you have concerns."""