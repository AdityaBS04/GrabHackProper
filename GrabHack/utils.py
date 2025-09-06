"""
Utility functions for the customer service orchestration system
"""

from langchain.tools import Tool


def create_placeholder_tool(tool_name: str, description: str) -> Tool:
    """Create a placeholder tool that will be replaced with actual implementation"""
    
    def placeholder_func(query: str) -> str:
        return f"""[PLACEHOLDER TOOL: {tool_name}]
        
This is where the {tool_name} tool would process:
- Customer Query: {query}
- Tool Purpose: {description}

In production, this would:
1. Access relevant databases/APIs
2. Process the specific issue type
3. Take appropriate action (refund, reorder, escalation, etc.)
4. Return resolution details

[Simulated Response]: Issue logged and will be processed according to {tool_name} workflow."""
    
    return Tool(
        name=tool_name,
        func=placeholder_func,
        description=description
    )