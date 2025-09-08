"""
Grab Food Customer Order Quality Handler
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
    """Customer-focused order accuracy and quality management with real AI"""
    
    def __init__(self, groq_api_key: str = None):
        self.service = "grab_food"
        self.actor = "customer"
        self.handler_type = "order_quality_handler"
        self.ai_engine = EnhancedAgenticAIEngine()
        
    def handle_missing_items(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle missing items - REQUIRES IMAGE for verification"""
        logger.info(f"Processing missing items complaint: {query[:100]}...")
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_missing_items",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            logger.info(f"AI response generated successfully")
            return result
        except Exception as e:
            logger.error(f"Error in handle_missing_items: {e}")
            return f"🚨 Processing Error: {str(e)}"

    def handle_wrong_item(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle wrong item delivered - REQUIRES IMAGE for verification"""
        logger.info(f"Processing wrong item complaint: {query[:100]}...")
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_wrong_item",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            logger.info(f"AI response generated successfully")
            return result
        except Exception as e:
            logger.error(f"Error in handle_wrong_item: {e}")
            return f"🚨 Processing Error: {str(e)}"

    def handle_quality_issues(self, query: str, image_data: Optional[str] = None, username: str = "anonymous") -> str:
        """Handle expired/damaged/poor quality items with strict workflow - REQUIRES IMAGE for assessment"""
        logger.info(f"Processing quality issues complaint: {query[:100]}...")
        
        # Step 1: Validate if image is provided
        if not image_data:
            return "Please upload an image of the food quality issue so we can assess your complaint properly."
        
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
        Analyze this food quality complaint with image evidence:
        
        Customer Complaint: {query}
        Image: [IMAGE PROVIDED]
        
        Analyze the image and determine if there are visible quality issues:
        - Check for spoilage, mold, discoloration
        - Look for physical damage, contamination
        - Assess if food appears fresh or expired
        - Verify if complaint matches visual evidence
        
        Respond with ONLY one of:
        CLEARLY_SPOILED - Obvious quality issues visible (mold, rot, severe discoloration)
        POSSIBLY_COMPROMISED - Some quality concerns but not definitive
        APPEARS_NORMAL - Food looks normal, complaint may be subjective
        INSUFFICIENT_EVIDENCE - Cannot determine quality from image
        """
        
        try:
            # Use the AI engine with image to validate
            result = self.ai_engine.process_complaint(
                function_name="validate_food_quality",
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
                WHERE username = ? AND service = 'grab_food' AND user_type = 'customer'
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
                WHERE username = ? AND service = 'grab_food' 
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
        Make a final decision on a food quality complaint based on:
        
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
            return """We sincerely apologize for the food quality issue. After reviewing the image evidence, we can see there are clear quality problems with your order. 

We are processing a FULL REFUND of your order amount immediately. The refund will be credited to your original payment method within 2-3 business days.

We are also reporting this issue to the restaurant to prevent similar problems. Thank you for bringing this to our attention."""
        
        elif decision == "REPLACEMENT_ORDER":
            return """We apologize for the quality concerns with your order. Based on the image you provided, we can see there may be quality issues.

We are arranging a REPLACEMENT ORDER for you at no additional cost. A fresh order will be prepared and delivered within 45-60 minutes.

We will also ensure the restaurant addresses the quality control issue. Your replacement order is being prioritized."""
        
        elif decision == "PARTIAL_REFUND":
            return """Thank you for reporting the quality issue with your order. We have reviewed the image evidence you provided.

While the issue may not be severe, we want to make this right. We are processing a PARTIAL REFUND of 50% of your order amount as compensation for the inconvenience.

We will also share your feedback with the restaurant to improve their quality standards. The refund will be processed within 24 hours."""
        
        elif decision == "REQUEST_BETTER_IMAGE":
            return """Thank you for reporting the quality issue. To properly assess your complaint, we need a clearer image of the food in question.

Please upload a better quality photo showing:
- Clear view of the food items
- Good lighting to show details
- Close-up of the specific quality issue

Once we receive a clearer image, we can provide an appropriate resolution."""
        
        else:  # FEEDBACK_ONLY
            return """Thank you for sharing your feedback about the food quality. We have reviewed your complaint and the image provided.

While we understand your concern, we will pass this feedback to the restaurant for their quality improvement. For any further queries, please contact our support team at food.support@grabfood.com.

We appreciate your patience and continued trust in our service."""

    def handle_substitution_issues(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle substituted item not acceptable - TEXT ONLY (no image required)"""
        logger.info(f"Processing substitution issues complaint: {query[:100]}...")
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_substitution_issues",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            logger.info(f"AI response generated successfully")
            return result
        except Exception as e:
            logger.error(f"Error in handle_substitution_issues: {e}")
            return f"🚨 Processing Error: {str(e)}"

    def handle_quantity_mismatch(self, query: str, image_data: Optional[str] = None) -> str:
        """Handle quantity mismatch - REQUIRES IMAGE to verify portions"""
        logger.info(f"Processing quantity mismatch complaint: {query[:100]}...")
        try:
            result = self.ai_engine.process_complaint(
                function_name="handle_quantity_mismatch",
                user_query=query,
                service=self.service,
                user_type=self.actor,
                image_data=image_data
            )
            logger.info(f"AI response generated successfully")
            return result
        except Exception as e:
            logger.error(f"Error in handle_quantity_mismatch: {e}")
            return f"🚨 Processing Error: {str(e)}"