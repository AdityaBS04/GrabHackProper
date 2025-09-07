#!/usr/bin/env python3

import os
import sys
sys.path.append('GrabHack')

from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

print("=== Environment Variables ===")
print(f"GROQ_API_KEY: {os.getenv('GROQ_API_KEY')}")
print(f"GROQ_API_KEY length: {len(os.getenv('GROQ_API_KEY', ''))}")

print("\n=== Testing AI Engine Import ===")
try:
    from GrabHack.enhanced_ai_engine import EnhancedAgenticAIEngine
    print("SUCCESS: Successfully imported EnhancedAgenticAIEngine")
except Exception as e:
    print(f"ERROR: Failed to import: {e}")
    sys.exit(1)

print("\n=== Testing AI Engine Initialization ===")
try:
    ai_engine = EnhancedAgenticAIEngine()
    print("SUCCESS: Successfully initialized AI engine")
except Exception as e:
    print(f"ERROR: Failed to initialize AI engine: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n=== Testing AI Engine Process ===")
try:
    solution = ai_engine.process_complaint(
        function_name="food_quality",
        user_query="My food was cold",
        service="grab_food",
        user_type="customer",
        image_data=None
    )
    print(f"SUCCESS: Successfully processed complaint. Solution length: {len(solution)}")
    print(f"Solution preview: {solution[:200]}...")
except Exception as e:
    print(f"ERROR: Failed to process complaint: {e}")
    import traceback
    traceback.print_exc()

print("\nDone!")