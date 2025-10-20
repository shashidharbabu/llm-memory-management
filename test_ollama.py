#!/usr/bin/env python3

import asyncio
import httpx
import json

async def test_ollama():
    """Test Ollama client directly"""
    base_url = "http://localhost:11434"
    chat_model = "phi3:mini"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("Testing Ollama chat API...")
            response = await client.post(
                f"{base_url}/api/chat",
                json={
                    "model": chat_model,
                    "messages": [
                        {"role": "user", "content": "Hello, this is a test message"}
                    ],
                    "stream": False,
                    "options": {
                        "temperature": 0.7
                    }
                }
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Message content: {result['message']['content']}")
            else:
                print(f"Error: {response.status_code} - {response.text}")
                
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ollama())
