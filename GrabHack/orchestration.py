"""
Customer Service Orchestration Agent with LangChain and Groq
Handles customer service inquiries with safety checks via Llama Guard
"""

import os
import logging
from typing import List, Optional
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import StdOutCallbackHandler

# Import modular components
from models import IssueCategory, ISSUE_MAPPING
from safety_checker import SafetyChecker
from handlers.portion_handler import PortionInadequateHandler
from utils import create_placeholder_tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomerServiceOrchestrator:
    """Main orchestration agent for customer service"""
    
    def __init__(self, groq_api_key: str):
        self.groq_api_key = groq_api_key
        self.safety_checker = SafetyChecker(groq_api_key)
        
        # Initialize specialized handlers
        self.portion_handler = PortionInadequateHandler(groq_api_key)
        
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
        
        # Create tools and agent
        self.tools = self._create_tools()
        self.agent = self._create_agent()
        
        # Track conversation state
        self.current_category = None
        self.current_sub_issue = None
        
    def _create_tools(self) -> List[Tool]:
        """Create all tools for sub-issues with specialized handlers where implemented"""
        tools = []
        
        # Create tools for each unique sub-issue
        for category, sub_issues in ISSUE_MAPPING.items():
            for sub_issue in sub_issues:
                # Use specialized handler for portion size issues
                if sub_issue.tool_name == "handle_portion_size":
                    tool = Tool(
                        name=sub_issue.tool_name,
                        func=self.portion_handler.handle_portion_complaint,
                        description=sub_issue.description
                    )
                else:
                    # Use placeholder for other tools
                    tool = create_placeholder_tool(
                        sub_issue.tool_name,
                        sub_issue.description
                    )
                tools.append(tool)
        
        # Add category selection tool
        tools.append(Tool(
            name="show_categories",
            func=lambda x: self._format_categories(),
            description="Show available issue categories to the customer"
        ))
        
        # Add sub-issue selection tool
        tools.append(Tool(
            name="show_sub_issues",
            func=lambda category: self._format_sub_issues(category),
            description="Show sub-issues for a selected category"
        ))
        
        return tools
    
    def _format_categories(self) -> str:
        """Format main categories for display"""
        categories_text = "Please select your issue category:\n\n"
        
        category_names = {
            IssueCategory.ORDER_NOT_RECEIVED: "I did not receive the order",
            IssueCategory.PORTION_INADEQUATE: "Item portion is not adequate",
            IssueCategory.SAFETY_INCIDENT: "Report a safety incident",
            IssueCategory.ITEMS_MISSING: "Items are missing in my order",
            IssueCategory.POOR_QUALITY: "Item quality is poor",
            IssueCategory.SPILLAGE: "Item has spillage",
            IssueCategory.FRAUD: "Report a fraud incident",
            IssueCategory.COUPON_QUERY: "I have a coupon related query",
            IssueCategory.PAYMENT_BILLING: "Payment and billing related query"
        }
        
        for cat in IssueCategory:
            categories_text += f"**{cat.value}. {category_names[cat]}**\n"
        
        return categories_text
    
    def _format_sub_issues(self, category_num: str) -> str:
        """Format sub-issues for a category"""
        try:
            category = None
            for cat in IssueCategory:
                if cat.value == category_num:
                    category = cat
                    break
            
            if not category:
                return "Invalid category number. Please select a valid option."
            
            self.current_category = category
            sub_issues = ISSUE_MAPPING[category]
            
            if not sub_issues:
                return "No sub-issues available for this category."
            
            sub_text = f"Please specify your issue:\n\n"
            for i, sub_issue in enumerate(sub_issues, 1):
                sub_text += f"{i}. {sub_issue.name}\n"
            
            return sub_text
            
        except Exception as e:
            logger.error(f"Error formatting sub-issues: {str(e)}")
            return "Error retrieving sub-issues. Please try again."
    
    def _create_agent(self) -> AgentExecutor:
        """Create the main agent with prompt"""
        
        prompt_template = """You are a friendly and helpful customer service assistant. Your role is to:
1. Understand the customer's issue
2. Guide them through selecting the appropriate category and sub-issue
3. Route their concern to the right resolution tool
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

If the customer hasn't selected a category yet, start by showing them the categories.
Always be empathetic and acknowledge their frustration if they express any.

{agent_scratchpad}

Begin! Remember to be friendly and helpful.
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
        """
        Process a user message with safety checks
        
        Args:
            user_input: The user's message
            
        Returns:
            The agent's response
        """
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
                return "I apologize for the confusion. Let me help you with your customer service issue."
            
            return agent_response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return "I apologize for the technical difficulty. Please try again or contact support directly."
    
    def reset_conversation(self):
        """Reset the conversation state"""
        self.memory.clear()
        self.current_category = None
        self.current_sub_issue = None
        logger.info("Conversation reset")
    
    def add_new_handler(self, handler_class, issue_category: IssueCategory, tool_name: str):
        """
        Add a new specialized handler for a specific issue type
        This allows easy extension of the system
        """
        # Initialize the handler
        handler = handler_class(self.groq_api_key)
        
        # Create tool and add to tools list
        for category, sub_issues in ISSUE_MAPPING.items():
            if category == issue_category:
                for sub_issue in sub_issues:
                    if sub_issue.tool_name == tool_name:
                        # Replace placeholder tool with specialized handler
                        tool = Tool(
                            name=sub_issue.tool_name,
                            func=handler.handle_complaint,  # Assume standard interface
                            description=sub_issue.description
                        )
                        # Update tools list
                        self.tools = [t for t in self.tools if t.name != tool_name]
                        self.tools.append(tool)
                        logger.info(f"Added specialized handler for {tool_name}")
                        break


def main():
    """Example usage of the CustomerServiceOrchestrator"""
    
    # Set your Groq API key
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")
    
    # Initialize the orchestrator
    orchestrator = CustomerServiceOrchestrator(GROQ_API_KEY)
    
    print("Customer Service Bot initialized. Type 'exit' to quit or 'reset' to start over.\n")
    
    while True:
        user_input = input("Customer: ").strip()
        
        if user_input.lower() == 'exit':
            print("Thank you for using our service. Goodbye!")
            break
        
        if user_input.lower() == 'reset':
            orchestrator.reset_conversation()
            print("Conversation reset. How can I help you today?")
            continue
        
        # Process the message
        response = orchestrator.process_message(user_input)
        print(f"\nAgent: {response}\n")


if __name__ == "__main__":
    main()