from typing import List, Dict, Any
from datetime import datetime
from app.database import get_database
import os

class ShortTermMemory:
    def __init__(self):
        self.window_size = int(os.getenv("SHORT_TERM_N", "10"))
    
    async def get_recent_messages(self, user_id: str, session_id: str = "default", limit: int = None) -> List[Dict[str, Any]]:
        """Get recent messages for short-term memory"""
        db = await get_database()
        
        if limit is None:
            limit = self.window_size
        
        cursor = db.messages.find(
            {"user_id": user_id, "session_id": session_id}
        ).sort("created_at", -1).limit(limit)
        
        messages = await cursor.to_list(length=limit)
        
        # Reverse to get chronological order (oldest first)
        messages.reverse()
        
        return messages
    
    async def get_message_count(self, user_id: str, session_id: str = "default") -> int:
        """Get total message count for a session"""
        db = await get_database()
        
        count = await db.messages.count_documents({
            "user_id": user_id, 
            "session_id": session_id
        })
        
        return count
    
    async def get_user_message_count(self, user_id: str, session_id: str = "default") -> int:
        """Get count of user messages (not assistant) in a session"""
        db = await get_database()
        
        count = await db.messages.count_documents({
            "user_id": user_id, 
            "session_id": session_id,
            "role": "user"
        })
        
        return count

# Global instance
short_term_memory = ShortTermMemory()
