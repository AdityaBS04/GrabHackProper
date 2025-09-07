#!/usr/bin/env python3
"""Simple test for image processing with the correct model"""
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def test_maverick_model():
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    # Simple test image (1x1 red pixel)
    test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What color do you see in this image?"},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{test_image}"}
                        }
                    ]
                }
            ],
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            temperature=0.0,
            max_tokens=100
        )
        
        print("SUCCESS: Image processing works!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    test_maverick_model()