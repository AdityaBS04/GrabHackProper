"""
Grab Service-Aware Customer Service Orchestration Agent
Routes queries to appropriate service-specific handlers based on Grab subsidiary
"""

import os
import logging
import importlib
from typing import List, Optional, Dict, Any
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import StdOutCallbackHandler

# Import modular components
from models import GrabService, IssueCategory, ISSUE_MAPPING
from safety_checker import SafetyChecker
from utils import create_placeholder_tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GrabServiceOrchestrator:
    """Service-aware orchestration agent for Grab customer service"""
    
    def __init__(self, groq_api_key: str):
        self.groq_api_key = groq_api_key
        self.safety_checker = SafetyChecker(groq_api_key)
        
        # Cache for loaded handlers
        self._handler_cache = {}
        
        # Initialize main LLM
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=1000
        )
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Track conversation state
        self.current_service = None
        self.current_category = None
        self.current_sub_issue = None
        
        # Create tools and agent
        self.tools = self._create_tools()
        self.agent = self._create_agent()
    
    def _load_handler(self, handler_module: str, handler_class: str):
        """Dynamically load a handler class from a module"""
        if handler_module in self._handler_cache:
            return self._handler_cache[handler_module]
        
        try:
            module = importlib.import_module(handler_module)
            handler_class_obj = getattr(module, handler_class)
            handler = handler_class_obj(self.groq_api_key)
            self._handler_cache[handler_module] = handler
            return handler
        except Exception as e:
            logger.error(f"Failed to load handler {handler_class} from {handler_module}: {str(e)}")
            return None
    
    def _create_tools(self) -> List[Tool]:
        """Create all tools for service-specific sub-issues"""
        tools = []
        
        # Create tools for each service and their issues
        for service, service_issues in ISSUE_MAPPING.items():
            for category, sub_issues in service_issues.items():
                for sub_issue in sub_issues:
                    # Try to load specialized handler
                    handler_class_name = self._get_handler_class_name(sub_issue.handler_module)
                    handler = self._load_handler(sub_issue.handler_module, handler_class_name)
                    
                    if handler:
                        # Get the appropriate method name from the handler
                        method_name = sub_issue.tool_name
                        if hasattr(handler, method_name):
                            tool = Tool(
                                name=f"{service.value}_{sub_issue.tool_name}",
                                func=getattr(handler, method_name),
                                description=f"[{service.value.upper()}] {sub_issue.description}"
                            )
                        else:
                            # Fallback to placeholder
                            tool = create_placeholder_tool(
                                f"{service.value}_{sub_issue.tool_name}",
                                f"[{service.value.upper()}] {sub_issue.description}"
                            )
                    else:
                        # Use placeholder if handler loading failed
                        tool = create_placeholder_tool(
                            f"{service.value}_{sub_issue.tool_name}",
                            f"[{service.value.upper()}] {sub_issue.description}"
                        )
                    
                    tools.append(tool)
        
        # Add service selection tool
        tools.append(Tool(
            name="show_services",
            func=lambda x: self._format_services(),
            description="Show available Grab services to the customer"
        ))
        
        # Add category selection tool for each service
        for service in GrabService:
            tools.append(Tool(
                name=f"show_{service.value}_categories",
                func=lambda x, svc=service: self._format_categories(svc),
                description=f"Show issue categories for {service.value.replace('_', ' ').title()}"
            ))
        
        # Add sub-issue selection tools
        for service in GrabService:
            tools.append(Tool(
                name=f"show_{service.value}_sub_issues",
                func=lambda category, svc=service: self._format_sub_issues(svc, category),
                description=f"Show sub-issues for a category in {service.value.replace('_', ' ').title()}"
            ))
        
        return tools
    
    def _get_handler_class_name(self, handler_module: str) -> str:
        """Generate handler class name from module path"""
        parts = handler_module.split('.')
        service = parts[0].replace('grab_', '').title()
        handler_type = parts[1].replace('_handler', '').title()
        return f"Grab{service}{handler_type}Handler"
    
    def _format_services(self) -> str:
        """Format Grab services for display"""
        services_text = "Welcome to Grab Customer Service! Please select your service:\n\n"
        
        service_names = {
            GrabService.GRAB_FOOD: "🍔 Grab Food - Food delivery service",
            GrabService.GRAB_MART: "🛒 Grab Mart - Grocery & retail delivery",
            GrabService.GRAB_CABS: "🚗 Grab Cabs - Ride-hailing service"
        }
        
        for i, (service, name) in enumerate(service_names.items(), 1):
            services_text += f"**{i}. {name}**\n"
        
        return services_text
    
    def _format_categories(self, service: GrabService) -> str:
        """Format issue categories for a specific service"""
        if service not in ISSUE_MAPPING:
            return f"No categories available for {service.value}"
        
        categories_text = f"Please select your {service.value.replace('_', ' ').title()} issue category:\n\n"
        
        service_issues = ISSUE_MAPPING[service]
        for i, category in enumerate(service_issues.keys(), 1):
            category_name = self._get_category_display_name(category, service)
            categories_text += f"**{i}. {category_name}**\n"
        
        return categories_text
    
    def _get_category_display_name(self, category: IssueCategory, service: GrabService) -> str:
        """Get user-friendly category names based on service context"""
        display_names = {
            (IssueCategory.ORDER_NOT_RECEIVED, GrabService.GRAB_FOOD): "I did not receive my food order",
            (IssueCategory.ORDER_NOT_RECEIVED, GrabService.GRAB_MART): "My grocery delivery is delayed/missing",
            (IssueCategory.PORTION_INADEQUATE, GrabService.GRAB_FOOD): "Food portion size is inadequate",
            (IssueCategory.ITEMS_MISSING, GrabService.GRAB_MART): "Items are missing from my order",
            (IssueCategory.POOR_QUALITY, GrabService.GRAB_FOOD): "Food quality is poor",
            (IssueCategory.POOR_QUALITY, GrabService.GRAB_MART): "Products are damaged/incorrect",
            (IssueCategory.PRODUCT_QUALITY, GrabService.GRAB_MART): "Product freshness/quality issues",
            (IssueCategory.RIDE_ISSUES, GrabService.GRAB_CABS): "Issues with my ride",
            (IssueCategory.DRIVER_BEHAVIOR, GrabService.GRAB_CABS): "Driver behavior concerns",
            (IssueCategory.SAFETY_INCIDENT, GrabService.GRAB_CABS): "Safety incident during ride",
            (IssueCategory.PAYMENT_BILLING, GrabService.GRAB_CABS): "Payment or billing issues",
        }
        
        return display_names.get((category, service), category.name.replace('_', ' ').title())
    
    def _format_sub_issues(self, service: GrabService, category_name: str) -> str:
        """Format sub-issues for a service category"""
        try:
            if service not in ISSUE_MAPPING:
                return f"No issues available for {service.value}"
            
            # Find category by name/number
            service_issues = ISSUE_MAPPING[service]
            categories = list(service_issues.keys())
            
            # Try to match by position (if number provided)
            try:
                category_index = int(category_name) - 1
                if 0 <= category_index < len(categories):
                    category = categories[category_index]
                else:
                    return "Invalid category number. Please select a valid option."
            except ValueError:
                # Try to match by name
                category = None
                for cat in categories:
                    if cat.name.lower() in category_name.lower():
                        category = cat
                        break
                
                if not category:
                    return "Category not found. Please select a valid option."
            
            self.current_service = service
            self.current_category = category
            sub_issues = service_issues[category]
            
            if not sub_issues:
                return f"No sub-issues available for this {service.value} category."
            
            sub_text = f"Please specify your {service.value.replace('_', ' ').title()} issue:\n\n"
            for i, sub_issue in enumerate(sub_issues, 1):
                sub_text += f"{i}. {sub_issue.name}\n"
            
            return sub_text
            
        except Exception as e:
            logger.error(f"Error formatting sub-issues: {str(e)}")
            return "Error retrieving sub-issues. Please try again."
    
    def _create_agent(self) -> AgentExecutor:
        """Create the main service-aware agent"""
        
        prompt_template = """You are a helpful Grab customer service assistant. Your role is to:
1. Help customers identify which Grab service they need assistance with (Food, Mart, or Cabs)
2. Guide them through selecting the appropriate issue category
3. Route their concern to the right service-specific resolution tool
4. Provide empathetic and professional responses

Available tools: {tool_names}

Chat History:
{chat_history}

Current conversation:
Human: {input}

You have access to the following tools:
{tools}

To use a tool, use this format:
Thought: I need to [explain your reasoning]
Action: [tool_name]
Action Input: [input for the tool]
Observation: [tool response]

After receiving the tool's response, format it nicely for the customer.

If the customer hasn't selected a Grab service yet, start by showing them the available services.
Always be empathetic and acknowledge their frustration if they express any.

{agent_scratchpad}

Begin! Remember to be friendly and helpful across all Grab services.
"""
        
        prompt = PromptTemplate(
            input_variables=["input", "tools", "tool_names", "chat_history", "agent_scratchpad"],
            template=prompt_template
        )
        
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
            callbacks=[StdOutCallbackHandler()]
        )
    
    def process_message(self, user_input: str) -> str:
        """Process a user message with safety checks and service routing"""
        try:
            # Check input safety
            is_safe, safety_reason = self.safety_checker.check_safety(user_input)
            if not is_safe:
                logger.warning(f"Unsafe input blocked: {safety_reason}")
                return "I apologize, but I cannot process that request. Please rephrase your concern in a respectful manner."
            
            # Process with agent
            response = self.agent.invoke({"input": user_input})
            agent_response = response.get("output", "I apologize, but I'm having trouble processing your request.")
            
            # Check output safety
            is_safe, safety_reason = self.safety_checker.check_safety(agent_response)
            if not is_safe:
                logger.warning(f"Unsafe output blocked: {safety_reason}")
                return "I apologize for the confusion. Let me help you with your Grab service issue."
            
            return agent_response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return "I apologize for the technical difficulty. Please try again or contact support directly."
    
    def reset_conversation(self):
        """Reset the conversation state"""
        self.memory.clear()
        self.current_service = None
        self.current_category = None
        self.current_sub_issue = None
        logger.info("Conversation reset")
    
    def add_new_service_handler(self, service: GrabService, handler_module: str, handler_class: str, issues: Dict[IssueCategory, List]):
        """Add a new service with its handlers dynamically"""
        # Load the handler
        handler = self._load_handler(handler_module, handler_class)
        
        if handler:
            # Add to issue mapping
            ISSUE_MAPPING[service] = issues
            
            # Recreate tools to include new service
            self.tools = self._create_tools()
            self.agent = self._create_agent()
            
            logger.info(f"Added new service: {service.value} with {len(issues)} issue categories")


def main():
    """Example usage of the GrabServiceOrchestrator"""
    
    # Set your Groq API key
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")
    
    # Initialize the service-aware orchestrator
    orchestrator = GrabServiceOrchestrator(GROQ_API_KEY)
    
    print("Grab Customer Service Bot initialized. Type 'exit' to quit or 'reset' to start over.\n")
    
    while True:
        user_input = input("Customer: ").strip()
        
        if user_input.lower() == 'exit':
            print("Thank you for using Grab services. Goodbye!")
            break
        
        if user_input.lower() == 'reset':
            orchestrator.reset_conversation()
            print("Conversation reset. How can I help you with your Grab service today?")
            continue
        
        # Process the message
        response = orchestrator.process_message(user_input)
        print(f"\nGrab Agent: {response}\n")


if __name__ == "__main__":
    main()