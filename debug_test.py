#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.ollama_client import ollama_client
from app.database import get_database
from app.memory.short_term import short_term_memory
from app.memory.episodic import episodic_memory
from app.memory.long_term import long_term_memory

async def test_components():
    """Test each component individually"""
    print("=== Testing Ollama Client ===")
    try:
        response = await ollama_client.chat_completion([
            {"role": "user", "content": "Hello, this is a test"}
        ])
        print(f"✅ Ollama chat working: {response[:50]}...")
    except Exception as e:
        print(f"❌ Ollama chat failed: {e}")
        return
    
    print("\n=== Testing Database Connection ===")
    try:
        db = await get_database()
        print("✅ Database connected")
    except Exception as e:
        print(f"❌ Database failed: {e}")
        return
    
    print("\n=== Testing Short-term Memory ===")
    try:
        messages = await short_term_memory.get_recent_messages("test_user", "session_1", limit=5)
        print(f"✅ Short-term memory working: {len(messages)} messages")
    except Exception as e:
        print(f"❌ Short-term memory failed: {e}")
        return
    
    print("\n=== Testing Episodic Memory ===")
    try:
        episodes = await episodic_memory.extract_and_store_episodes("test_user", "session_1", "I am working on a distributed systems project")
        print(f"✅ Episodic memory working: {len(episodes)} episodes extracted")
    except Exception as e:
        print(f"❌ Episodic memory failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n=== Testing Long-term Memory ===")
    try:
        summary = await long_term_memory.get_latest_summary("test_user", "session")
        print(f"✅ Long-term memory working: summary = {summary is not None}")
    except Exception as e:
        print(f"❌ Long-term memory failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n=== All components working! ===")

if __name__ == "__main__":
    asyncio.run(test_components())
