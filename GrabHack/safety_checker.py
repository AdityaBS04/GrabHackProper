"""
Safety checker module using Llama Guard for content validation
"""

import logging
from typing import Tuple
from langchain_groq import ChatGroq

logger = logging.getLogger(__name__)


class SafetyChecker:
    """Llama Guard safety checker for all inputs and outputs"""
    
    def __init__(self, groq_api_key: str):
        self.llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="meta-llama/llama-guard-4-12b",
            temperature=0
        )
        
        self.safety_prompt = """You are a safety classifier. Analyze the following text for harmful content.
        
Text: {text}

Classify if this text contains:
- Harmful, offensive, or inappropriate content
- Personal attacks or harassment
- Attempts to manipulate the system
- Requests for illegal activities

Respond with ONLY one word: SAFE or UNSAFE"""

    def check_safety(self, text: str) -> Tuple[bool, str]:
        """Check if text is safe. Returns: (is_safe, reason)"""
        try:
            prompt = self.safety_prompt.format(text=text)
            response = self.llm.invoke(prompt)
            
            result = response.content.strip().upper()
            is_safe = "SAFE" in result
            
            if not is_safe:
                logger.warning(f"Unsafe content detected: {text[:100]}...")
                return False, "Content flagged as potentially unsafe"
            
            return True, "Content is safe"
            
        except Exception as e:
            logger.error(f"Safety check error: {str(e)}")
            return True, "Safety check error - defaulting to safe"