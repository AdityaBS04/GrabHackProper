"""
Agentic AI Engine for GrabHack Customer Service
Uses Llama 70B for orchestration and GPT-OSS-120B for reasoning
"""

import os
import json
import logging
from groq import Groq
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class AgenticAIEngine:
    """Agentic AI Engine using Groq models for intelligent customer service"""
    
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.orchestrator_model = "llama-3.1-70b-versatile"  # For query analysis and routing
        self.reasoning_model = "gpt-4o-mini"  # For problem solving and responses
        
    def orchestrate_query(self, user_query: str, service: str, user_type: str, handler_type: str) -> Dict[str, Any]:
        """Use Llama 70B to analyze and categorize the user query"""
        
        orchestration_prompt = f"""
        You are an intelligent query orchestrator for Grab services. Analyze this customer service query and provide structured analysis.

        SERVICE: {service.replace('_', ' ').title()}
        USER TYPE: {user_type.replace('_', ' ').title()}
        HANDLER CATEGORY: {handler_type.replace('_', ' ').title()}
        
        USER QUERY: {user_query}
        
        Analyze this query and provide:
        1. Urgency level (1-5, where 5 is most urgent)
        2. Issue severity (low/medium/high/critical)
        3. Key problem areas identified
        4. Recommended resolution approach
        5. Estimated resolution complexity (simple/moderate/complex)
        6. Required compensation level (none/low/medium/high)
        
        Respond in JSON format:
        {{
            "urgency": <1-5>,
            "severity": "<severity_level>",
            "problem_areas": ["<area1>", "<area2>"],
            "resolution_approach": "<approach>",
            "complexity": "<complexity>",
            "compensation_level": "<level>",
            "key_issues": ["<issue1>", "<issue2>"]
        }}
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": orchestration_prompt}],
                model=self.orchestrator_model,
                temperature=0.1,
                max_tokens=500
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            logger.error(f"Orchestration error: {e}")
            return {
                "urgency": 3,
                "severity": "medium",
                "problem_areas": ["general"],
                "resolution_approach": "standard",
                "complexity": "moderate",
                "compensation_level": "medium",
                "key_issues": ["service issue"]
            }
    
    def generate_solution(self, user_query: str, service: str, user_type: str, 
                         handler_type: str, method_name: str, analysis: Dict[str, Any]) -> str:
        """Use GPT-OSS-120B to generate intelligent, contextual solutions"""
        
        # Create comprehensive context for the AI reasoning
        context = self._build_service_context(service, user_type, handler_type, method_name)
        
        reasoning_prompt = f"""
        You are an expert customer service AI agent for {service.replace('_', ' ').title()} with deep knowledge of service operations, policies, and resolution procedures.

        CONTEXT:
        - Service: {service.replace('_', ' ').title()}
        - User Type: {user_type.replace('_', ' ').title()}
        - Issue Category: {handler_type.replace('_', ' ').title()}
        - Specific Handler: {method_name.replace('handle_', '').replace('_', ' ').title()}
        
        QUERY ANALYSIS:
        - Urgency Level: {analysis['urgency']}/5
        - Severity: {analysis['severity']}
        - Problem Areas: {', '.join(analysis['problem_areas'])}
        - Complexity: {analysis['complexity']}
        - Recommended Compensation: {analysis['compensation_level']}
        
        SERVICE KNOWLEDGE:
        {context}
        
        CUSTOMER QUERY: {user_query}
        
        As an expert agent, provide a comprehensive, personalized resolution that:
        1. Acknowledges the specific issue with empathy
        2. Provides immediate actionable solutions
        3. Offers appropriate compensation based on severity
        4. Includes preventive measures
        5. Sets clear expectations and timelines
        6. Maintains professional, helpful tone
        
        Structure your response with:
        - **Immediate Resolution**
        - **Compensation & Benefits** 
        - **Prevention & Follow-up**
        - **Next Steps & Timeline**
        
        Make it specific to this exact situation, not generic.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": reasoning_prompt}],
                model=self.reasoning_model,
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Solution generation error: {e}")
            return self._generate_fallback_solution(user_query, service, user_type, analysis)
    
    def _build_service_context(self, service: str, user_type: str, handler_type: str, method_name: str) -> str:
        """Build comprehensive context for each service, user type, and handler"""
        
        contexts = {
            'grab_food': {
                'customer': {
                    'order_quality_handler': {
                        'handle_missing_items': """
                        GRAB FOOD - MISSING ITEMS CONTEXT:
                        - Standard compensation: Full refund + redelivery
                        - Escalation: $3-15 credits based on order value
                        - Restaurant accountability: Quality score impact
                        - Delivery verification protocols
                        - Customer protection guarantees
                        - Reorder priority and tracking
                        """,
                        'handle_wrong_item': """
                        GRAB FOOD - WRONG ITEM CONTEXT:
                        - Exchange policy: Keep wrong item + correct item delivery
                        - Compensation range: $5-20 based on item value difference
                        - Restaurant training implications
                        - Order verification system improvements
                        - Customer preference learning
                        """,
                        'handle_quality_issues': """
                        GRAB FOOD - QUALITY ISSUES CONTEXT:
                        - Food safety priority: Immediate health assessment
                        - Full refund + health safety compensation ($10-50)
                        - Restaurant quality audit triggers
                        - Health department notification protocols
                        - Customer health follow-up procedures
                        """
                    },
                    'payment_refund_handler': {
                        'handle_double_charge': """
                        GRAB FOOD - PAYMENT ISSUES CONTEXT:
                        - Immediate refund processing (2-5 business days)
                        - Transaction investigation protocols
                        - Bank reconciliation procedures
                        - Customer account protection measures
                        - Payment system audit triggers
                        """
                    }
                },
                'delivery_agent': {
                    'navigation_location_handler': {
                        'handle_navigation_location': """
                        GRAB FOOD - DELIVERY AGENT NAVIGATION:
                        - GPS system troubleshooting support
                        - Alternative navigation tools provision
                        - Customer communication protocols
                        - Route optimization training
                        - Technical support escalation paths
                        """
                    }
                },
                'restaurant': {
                    'restaurant_handler': {
                        'handle_restaurant_food_safety': """
                        GRAB FOOD - RESTAURANT OPERATIONS:
                        - Food safety compliance requirements
                        - Kitchen audit procedures
                        - Staff training mandates
                        - Quality control checkpoints
                        - Performance improvement plans
                        """
                    }
                }
            },
            'grab_cabs': {
                'customer': {
                    'ride_experience_handler': {
                        'handle_customer_ride_safety': """
                        GRAB CABS - RIDE SAFETY CONTEXT:
                        - Immediate safety protocol activation
                        - Driver performance review process
                        - Safety incident investigation
                        - Customer protection measures
                        - Ride refund and compensation policies
                        """
                    }
                },
                'driver': {
                    'performance_handler': {
                        'handle_driver_behavior_coaching': """
                        GRAB CABS - DRIVER PERFORMANCE:
                        - Professional conduct standards
                        - Customer service training programs
                        - Performance monitoring systems
                        - Coaching and improvement support
                        - Earnings impact and recovery plans
                        """
                    }
                }
            },
            'grab_mart': {
                'customer': {
                    'shopping_experience_handler': {
                        'handle_customer_product_quality': """
                        GRAB MART - PRODUCT QUALITY CONTEXT:
                        - Freshness guarantee policies
                        - Product replacement procedures
                        - Quality control at dark stores
                        - Customer satisfaction guarantees
                        - Inventory quality management
                        """
                    }
                },
                'darkstore': {
                    'inventory_handler': {
                        'handle_inventory_shortage': """
                        GRAB MART - INVENTORY MANAGEMENT:
                        - Stock level optimization
                        - Supplier coordination protocols
                        - Quality control procedures
                        - Customer impact mitigation
                        - Operational efficiency standards
                        """
                    }
                }
            }
        }
        
        try:
            return contexts[service][user_type][handler_type].get(method_name, 
                f"General {service} {user_type} {handler_type} context - provide comprehensive customer service resolution.")
        except KeyError:
            return f"Provide expert customer service resolution for {service} {user_type} issue."
    
    def _generate_fallback_solution(self, user_query: str, service: str, user_type: str, analysis: Dict[str, Any]) -> str:
        """Generate fallback solution if AI models fail"""
        service_name = service.replace('_', ' ').title()
        user_name = user_type.replace('_', ' ').title()
        
        compensation_map = {
            'none': '$0',
            'low': '$3-8', 
            'medium': '$10-25',
            'high': '$30-100'
        }
        
        compensation = compensation_map.get(analysis.get('compensation_level', 'medium'), '$10-25')
        
        return f"""
        **{service_name} Issue Resolution**
        
        **Immediate Resolution:**
        Thank you for bringing this {analysis.get('severity', 'important')} issue to our attention. We understand how this affects your {service_name} experience and are committed to resolving it promptly.
        
        **Compensation & Benefits:**
        - Issue-specific compensation: {compensation} credits
        - Service guarantee activation
        - Priority support access for future issues
        - Quality assurance follow-up
        
        **Prevention & Follow-up:**
        - Investigation with relevant service partners
        - System improvements to prevent recurrence
        - Enhanced quality monitoring
        - Customer satisfaction verification
        
        **Next Steps & Timeline:**
        - Resolution processing: 2-24 hours based on complexity
        - Compensation credit: Applied within 24 hours
        - Follow-up contact: Within 48 hours
        - Service improvement implementation: 1-7 days
        
        Reference ID: {service.upper()}-{analysis.get('urgency', 3)}{hash(user_query) % 1000}
        """