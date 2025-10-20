from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from typing import Dict, Any
import os
from datetime import datetime

from app.database import connect_to_mongo, close_mongo_connection
from app.models import ChatRequest, ChatResponse, MemoryRequest, MemoryResponse, AggregateResponse
from app.memory.short_term import short_term_memory
from app.memory.long_term import long_term_memory
from app.memory.episodic import episodic_memory
from app.services.ollama_client import ollama_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="AI Memory System",
    description="FastAPI system with short-term, long-term, and episodic memory",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AI Memory System"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint with full memory pipeline"""
    try:
        from app.database import get_database
        db = await get_database()
        
        # 1. Save user message
        user_message = {
            "user_id": request.user_id,
            "session_id": request.session_id,
            "role": "user",
            "content": request.message,
            "created_at": datetime.utcnow()
        }
        await db.messages.insert_one(user_message)
        
        # 2. Get short-term memory (recent messages)
        recent_messages = await short_term_memory.get_recent_messages(
            request.user_id, request.session_id
        )
        
        # 3. Get long-term memory (summaries)
        session_summary = await long_term_memory.get_latest_summary(
            request.user_id, "session", request.session_id
        )
        lifetime_summary = await long_term_memory.get_latest_summary(
            request.user_id, "user"
        )
        
        # 4. Get episodic memory (relevant facts)
        relevant_episodes = await episodic_memory.retrieve_relevant_episodes(
            request.user_id, request.message, request.session_id
        )
        
        # 5. Compose prompt for LLM
        system_prompt = "You are a helpful AI assistant. Give brief, helpful responses."
        
        # Build context from memory
        context_parts = []
        
        # Add lifetime summary if available
        if lifetime_summary:
            context_parts.append("User Profile: " + lifetime_summary['text'])
        
        # Add session summary if available
        if session_summary:
            context_parts.append("Session Summary: " + session_summary['text'])
        
        # Add recent conversation (limit to last 5 messages)
        if recent_messages:
            context_parts.append("Recent Conversation:")
            for msg in recent_messages[-5:]:  # Last 5 messages only
                context_parts.append(msg['role'] + ": " + msg['content'])
        
        # Add relevant episodic facts
        if relevant_episodes:
            facts = [ep["fact"] for ep in relevant_episodes]
            context_parts.append("Relevant Facts: " + "; ".join(facts))
        
        # Compose full prompt
        context = "\n\n".join(context_parts)
        
        # 6. Call Ollama for response
        messages_for_llm = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context: {context}\n\nUser: {request.message}\n\nAssistant:"}
        ]
        
        print(f"DEBUG: Calling Ollama with {len(messages_for_llm)} messages")
        assistant_reply = await ollama_client.chat_completion(messages_for_llm)
        print(f"DEBUG: Ollama response length: {len(assistant_reply) if assistant_reply else 0}")
        print(f"DEBUG: Ollama response preview: {assistant_reply[:100] if assistant_reply else 'None'}...")
        
        # 7. Save assistant response
        assistant_message = {
            "user_id": request.user_id,
            "session_id": request.session_id,
            "role": "assistant",
            "content": assistant_reply,
            "created_at": datetime.utcnow()
        }
        await db.messages.insert_one(assistant_message)
        
        # 8. Extract and store episodes from user message
        await episodic_memory.extract_and_store_episodes(
            request.user_id, request.session_id, request.message
        )
        
        # 9. Check if we should generate session summary
        if await long_term_memory.should_generate_session_summary(request.user_id, request.session_id):
            await long_term_memory.generate_session_summary(request.user_id, request.session_id)
        
        # 10. Occasionally generate lifetime summary (every 5 sessions)
        user_message_count = await short_term_memory.get_user_message_count(request.user_id, request.session_id)
        if user_message_count % 25 == 0:  # Every 25 user messages
            await long_term_memory.generate_lifetime_summary(request.user_id)
        
        # Prepare response
        memory_used = {
            "short_term_count": len(recent_messages),
            "long_term_summary": lifetime_summary["text"] if lifetime_summary else None,
            "episodic_facts": [ep["fact"] for ep in relevant_episodes]
        }
        
        return ChatResponse(
            reply=assistant_reply,
            memory_used=memory_used
        )
        
    except Exception as e:
        import traceback
        print("=== FULL ERROR TRACEBACK ===")
        traceback.print_exc()
        print("=== ERROR DETAILS ===")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
        print("=== END ERROR ===")
        raise HTTPException(status_code=500, detail=f"Internal server error: {type(e).__name__}: {str(e)}")

@app.get("/api/memory/{user_id}", response_model=MemoryResponse)
async def get_memory(user_id: str, session_id: str = "default"):
    """Get memory state for a user"""
    try:
        # Get recent messages
        recent_messages = await short_term_memory.get_recent_messages(user_id, session_id, limit=16)
        
        # Get summaries
        session_summary = await long_term_memory.get_latest_summary(user_id, "session", session_id)
        lifetime_summary = await long_term_memory.get_latest_summary(user_id, "user")
        
        # Get recent episodes
        recent_episodes = await episodic_memory.get_recent_episodes(user_id, session_id, limit=20)
        episode_facts = [ep["fact"] for ep in recent_episodes]
        
        return MemoryResponse(
            user_id=user_id,
            session_id=session_id,
            recent_messages=recent_messages,
            session_summary=session_summary["text"] if session_summary else None,
            lifetime_summary=lifetime_summary["text"] if lifetime_summary else None,
            recent_episodes=episode_facts
        )
        
    except Exception as e:
        print("Error in memory endpoint:", str(e))
        raise HTTPException(status_code=500, detail="Internal server error: " + str(e))

@app.get("/api/aggregate/{user_id}", response_model=AggregateResponse)
async def get_aggregate(user_id: str):
    """Get aggregated data for a user"""
    try:
        # Get daily message counts
        daily_counts = await long_term_memory.get_daily_message_counts(user_id)
        
        # Get recent summaries
        summaries = await long_term_memory.get_all_summaries(user_id)
        
        # Format session summaries
        session_summaries = []
        for summary in summaries["sessions"][:5]:  # Last 5 sessions
            session_summaries.append({
                "session_id": summary["session_id"],
                "text": summary["text"],
                "created_at": summary["created_at"]
            })
        
        return AggregateResponse(
            user_id=user_id,
            daily_message_counts=daily_counts,
            recent_summaries={
                "lifetime": summaries["lifetime"]["text"] if summaries["lifetime"] else None,
                "sessions": session_summaries
            }
        )
        
    except Exception as e:
        print("Error in aggregate endpoint:", str(e))
        raise HTTPException(status_code=500, detail="Internal server error: " + str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("FASTAPI_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
