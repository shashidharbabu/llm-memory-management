from typing import List, Dict, Any
from datetime import datetime
from app.database import get_database
from app.services.ollama_client import ollama_client
from app.services.embeddings import find_top_similar_episodes
import os

class EpisodicMemory:
    def __init__(self):
        self.top_k = int(os.getenv("EPISODIC_TOP_K", "5"))
    
    async def extract_and_store_episodes(self, user_id: str, session_id: str, message: str) -> List[Dict[str, Any]]:
        """Extract episodes from user message and store them"""
        # Extract episodes using LLM
        episodes_data = await ollama_client.extract_episodes(message)
        
        if not episodes_data:
            return []
        
        db = await get_database()
        stored_episodes = []
        
        for episode_data in episodes_data:
            try:
                fact = episode_data.get("fact", "").strip()
                importance = float(episode_data.get("importance", 0.5))
                
                if not fact:
                    continue
                
                # Generate embedding for the fact
                embedding = await ollama_client.generate_embedding(fact)
                
                if not embedding:
                    continue
                
                # Store episode in database
                episode_doc = {
                    "user_id": user_id,
                    "session_id": session_id,
                    "fact": fact,
                    "importance": importance,
                    "embedding": embedding,
                    "created_at": datetime.utcnow()
                }
                
                result = await db.episodes.insert_one(episode_doc)
                episode_doc["_id"] = result.inserted_id
                stored_episodes.append(episode_doc)
                
            except Exception as e:
                print("Error storing episode:", str(e))
                continue
        
        return stored_episodes
    
    async def retrieve_relevant_episodes(self, user_id: str, query_message: str, session_id: str = None) -> List[Dict[str, Any]]:
        """Retrieve relevant episodes based on query message"""
        # Generate embedding for query
        query_embedding = await ollama_client.generate_embedding(query_message)
        
        if not query_embedding:
            return []
        
        db = await get_database()
        
        # Build query filter
        query_filter = {"user_id": user_id}
        if session_id:
            query_filter["session_id"] = session_id
        
        # Get all episodes for user (or session)
        cursor = db.episodes.find(query_filter)
        episodes = await cursor.to_list(length=None)
        
        if not episodes:
            return []
        
        # Find top similar episodes
        relevant_episodes = find_top_similar_episodes(query_embedding, episodes, self.top_k)
        
        return relevant_episodes
    
    async def get_recent_episodes(self, user_id: str, session_id: str = "default", limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent episodes for a user/session"""
        db = await get_database()
        
        cursor = db.episodes.find(
            {"user_id": user_id, "session_id": session_id}
        ).sort("created_at", -1).limit(limit)
        
        episodes = await cursor.to_list(length=limit)
        
        return episodes
    
    async def get_episode_count(self, user_id: str, session_id: str = "default") -> int:
        """Get episode count for a user/session"""
        db = await get_database()
        
        count = await db.episodes.count_documents({
            "user_id": user_id,
            "session_id": session_id
        })
        
        return count

# Global instance
episodic_memory = EpisodicMemory()
