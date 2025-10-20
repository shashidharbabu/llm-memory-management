#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.ollama_client import ollama_client

async def test_simple_chat():
    """Test simple chat completion"""
    print("Testing simple chat completion...")
    
    try:
        response = await ollama_client.chat_completion([
            {"role": "user", "content": "Hello, this is a test message"}
        ])
        print(f"Response: '{response}'")
        print(f"Response length: {len(response)}")
        print(f"Response type: {type(response)}")
        
        if not response or not response.strip():
            print("❌ Empty response!")
        else:
            print("✅ Got valid response!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_chat())
