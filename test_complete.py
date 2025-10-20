import httpx
import asyncio
from datetime import datetime
import json
import os

async def test_system():
    base_url = "http://localhost:8000"
    test_user = "test_user_" + datetime.now().strftime("%H%M%S")
    test_session = "test_session_" + datetime.now().strftime("%H%M%S")

    print(f"Testing with user_id: {test_user}, session_id: {test_session}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Initial conversation to build context
        messages = [
            "Hi! My name is Alice and I love reading science fiction books.",
            "I recently finished reading 'Dune' by Frank Herbert, it was amazing!",
            "I also enjoy programming, especially in Python and JavaScript.",
            "Could you remind me what books we discussed?",
            "What do you remember about my programming interests?"
        ]

        print("\n=== Test 1: Building Conversation Context ===")
        for msg in messages:
            print(f"\nUser: {msg}")
            try:
                response = await client.post(
                    f"{base_url}/api/chat",
                    json={
                        "user_id": test_user,
                        "session_id": test_session,
                        "message": msg
                    }
                )
                result = response.json()
                print(f"Assistant: {result['reply']}")
                print(f"Memory Used: {json.dumps(result['memory_used'], indent=2)}")
            except Exception as e:
                print(f"Error: {str(e)}")

        # Test 2: Check memory state
        print("\n=== Test 2: Checking Memory State ===")
        try:
            response = await client.get(f"{base_url}/api/memory/{test_user}")
            memory_state = response.json()
            print(json.dumps(memory_state, indent=2))
        except Exception as e:
            print(f"Error: {str(e)}")

        # Test 3: Check aggregated data
        print("\n=== Test 3: Checking Aggregated Data ===")
        try:
            response = await client.get(f"{base_url}/api/aggregate/{test_user}")
            aggregate_data = response.json()
            print(json.dumps(aggregate_data, indent=2))
        except Exception as e:
            print(f"Error: {str(e)}")

        # Test 4: Start new session and test memory persistence
        new_session = "test_session_" + datetime.now().strftime("%H%M%S")
        print(f"\n=== Test 4: Testing Memory Persistence (New Session: {new_session}) ===")
        try:
            response = await client.post(
                f"{base_url}/api/chat",
                json={
                    "user_id": test_user,
                    "session_id": new_session,
                    "message": "What do you remember about me from our previous conversation?"
                }
            )
            result = response.json()
            print(f"Assistant: {result['reply']}")
            print(f"Memory Used: {json.dumps(result['memory_used'], indent=2)}")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_system())