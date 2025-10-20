import httpx
import asyncio
from typing import Dict, Any
import json

async def test_chat_api():
    async with httpx.AsyncClient() as client:
        # Test data
        user_id = "test_user"
        session_id = "test_session"
        
        # Test /api/chat endpoint
        chat_data = {
            "user_id": user_id,
            "session_id": session_id,
            "message": "Hello! My name is Alice and I love reading science fiction books."
        }
        
        try:
            response = await client.post(
                "http://localhost:8000/api/chat",
                json=chat_data
            )
            print("\n=== Chat Response ===")
            print(json.dumps(response.json(), indent=2))
        except Exception as e:
            print("Error testing chat:", str(e))
        
        # Test /api/memory endpoint
        try:
            response = await client.get(f"http://localhost:8000/api/memory/{user_id}")
            print("\n=== Memory State ===")
            print(json.dumps(response.json(), indent=2))
        except Exception as e:
            print("Error testing memory:", str(e))
        
        # Test /api/aggregate endpoint
        try:
            response = await client.get(f"http://localhost:8000/api/aggregate/{user_id}")
            print("\n=== Aggregate Data ===")
            print(json.dumps(response.json(), indent=2))
        except Exception as e:
            print("Error testing aggregate:", str(e))

if __name__ == "__main__":
    asyncio.run(test_chat_api())