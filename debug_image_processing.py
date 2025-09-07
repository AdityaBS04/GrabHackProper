#!/usr/bin/env python3
"""
Debug script to test image processing in the AI engine
"""
import os
import base64
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def test_image_models():
    """Test different image processing models available in Groq"""
    
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    # Test with a simple base64 image (1x1 pixel red image)
    test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    models_to_test = [
        "llama-3.2-90b-vision-preview",  # Vision model
        "llama-3.2-11b-vision-preview",  # Alternative vision model (might be deprecated)  
    ]
    
    for model in models_to_test:
        try:
            print(f"\nTesting model: {model}")
            
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "What do you see in this image?"},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{test_image}"}
                            }
                        ]
                    }
                ],
                model=model,
                temperature=0.0,
                max_tokens=100
            )
            
            print(f"Success with {model}:")
            print(f"   Response: {response.choices[0].message.content}")
            
        except Exception as e:
            print(f"Error with {model}: {e}")
    
    # Test image security screening
    print(f"\n\nTesting image security screening...")
    try:
        security_response = client.chat.completions.create(
            messages=[
                {
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": "Is this image appropriate for customer service? Respond with SAFE or UNSAFE only."},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{test_image}"}
                        }
                    ]
                }
            ],
            model="llama-3.2-90b-vision-preview",  # Use vision model for security
            temperature=0.0,
            max_tokens=10
        )
        
        print(f"Security screening works:")
        print(f"   Response: {security_response.choices[0].message.content}")
        
    except Exception as e:
        print(f"Security screening failed: {e}")

if __name__ == "__main__":
    test_image_models()