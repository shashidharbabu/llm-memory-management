from typing import List, Dict, Any, Optional
from datetime import datetime
from app.database import get_database
from app.services.ollama_client import ollama_client
from app.memory.short_term import short_term_memory
import os

class LongTermMemory:
    def __init__(self):
        self.summarize_every = int(os.getenv("SUMMARIZE_EVERY_USER_MSGS", "5"))
    
    async def get_latest_summary(self, user_id: str, scope: str, session_id: str = None) -> Optional[Dict[str, Any]]:
        """Get latest summary for user (session or lifetime)"""
        db = await get_database()
        
        query_filter = {"user_id": user_id, "scope": scope}
        if session_id and scope == "session":
            query_filter["session_id"] = session_id
        elif scope == "user":
            query_filter["session_id"] = None
        
        summary = await db.summaries.find_one(
            query_filter,
            sort=[("created_at", -1)]
        )
        
        return summary
    
    async def should_generate_session_summary(self, user_id: str, session_id: str) -> bool:
        """Check if we should generate a session summary"""
        user_message_count = await short_term_memory.get_user_message_count(user_id, session_id)
        return user_message_count > 0 and user_message_count % self.summarize_every == 0
    
    async def generate_session_summary(self, user_id: str, session_id: str) -> Optional[Dict[str, Any]]:
        """Generate and store session summary"""
        # Get recent messages for summarization (last 20-30 messages)
        recent_messages = await short_term_memory.get_recent_messages(user_id, session_id, limit=30)
        
        if not recent_messages:
            return None
        
        # Convert to format for LLM
        messages_for_llm = []
        for msg in recent_messages:
            messages_for_llm.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Generate summary
        summary_text = await ollama_client.generate_session_summary(messages_for_llm)
        
        if not summary_text.strip():
            return None
        
        # Store summary
        db = await get_database()
        summary_doc = {
            "user_id": user_id,
            "session_id": session_id,
            "scope": "session",
            "text": summary_text,
            "created_at": datetime.utcnow()
        }
        
        # Upsert (update if exists, insert if not)
        result = await db.summaries.update_one(
            {"user_id": user_id, "session_id": session_id, "scope": "session"},
            {"$set": summary_doc},
            upsert=True
        )
        
        return summary_doc
    
    async def generate_lifetime_summary(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Generate and store lifetime summary from session summaries"""
        # Get all session summaries for user
        db = await get_database()
        cursor = db.summaries.find(
            {"user_id": user_id, "scope": "session"}
        ).sort("created_at", -1).limit(10)  # Last 10 session summaries
        
        session_summaries = await cursor.to_list(length=10)
        
        if not session_summaries:
            return None
        
        # Extract summary texts
        summary_texts = [summary["text"] for summary in session_summaries]
        
        # Generate lifetime summary
        lifetime_text = await ollama_client.generate_lifetime_summary(summary_texts)
        
        if not lifetime_text.strip():
            return None
        
        # Store lifetime summary
        lifetime_doc = {
            "user_id": user_id,
            "session_id": None,
            "scope": "user",
            "text": lifetime_text,
            "created_at": datetime.utcnow()
        }
        
        # Upsert lifetime summary
        result = await db.summaries.update_one(
            {"user_id": user_id, "scope": "user"},
            {"$set": lifetime_doc},
            upsert=True
        )
        
        return lifetime_doc
    
    async def get_all_summaries(self, user_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get all summaries for a user"""
        db = await get_database()
        
        # Get session summaries
        session_cursor = db.summaries.find(
            {"user_id": user_id, "scope": "session"}
        ).sort("created_at", -1)
        
        session_summaries = await session_cursor.to_list(length=None)
        
        # Get lifetime summary
        lifetime_summary = await self.get_latest_summary(user_id, "user")
        
        return {
            "sessions": session_summaries,
            "lifetime": lifetime_summary
        }
    
    async def get_daily_message_counts(self, user_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily message counts for a user"""
        db = await get_database()
        
        # MongoDB aggregation pipeline for daily counts
        pipeline = [
            {"$match": {"user_id": user_id}},
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$created_at"},
                        "month": {"$month": "$created_at"},
                        "day": {"$dayOfMonth": "$created_at"}
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}
            },
            {"$limit": days}
        ]
        
        cursor = db.messages.aggregate(pipeline)
        results = await cursor.to_list(length=days)
        
        # Format results
        daily_counts = []
        for result in results:
            date_obj = result["_id"]
            year = date_obj['year']
            month = date_obj['month']
            day = date_obj['day']
            date_str = f"{year}-{month:02d}-{day:02d}"
            daily_counts.append({
                "date": date_str,
                "count": result["count"]
            })
        
        return daily_counts

# Global instance
long_term_memory = LongTermMemory()
