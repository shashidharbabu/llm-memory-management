import httpx
import json
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class OllamaClient:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.chat_model = os.getenv("CHAT_MODEL", "phi3:mini")
        self.embed_model = os.getenv("EMBED_MODEL", "nomic-embed-text")
    
    async def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Generate chat completion using Ollama"""
        try:
            # Convert messages to a single prompt for Ollama's completion endpoint
            prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.chat_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()
                content = result.get("response", "")
                
                # Handle empty responses
                if not content or not content.strip():
                    print("Empty response from Ollama chat completion")
                    return "I apologize, but I'm having trouble processing your request right now."
                
                return content
        except Exception as e:
            print("Error in chat completion:", str(e))
            return "I apologize, but I'm having trouble processing your request right now."
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Ollama"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": self.embed_model,
                        "prompt": text
                    }
                )
                response.raise_for_status()
                result = response.json()
                return result["embedding"]
        except Exception as e:
            print("Error generating embedding:", str(e))
            return []
    
    async def extract_episodes(self, message: str) -> List[Dict[str, Any]]:
        """Extract important facts from user message"""
        prompt = f"""Extract up to 3 important facts from this message that would be useful to remember for future conversations. 
        Return only a JSON array of objects with 'fact' and 'importance' fields. 
        Importance should be a number between 0.0 and 1.0.
        
        Message: "{message}"
        
        Return format: [{{"fact": "extracted fact", "importance": 0.8}}, ...]"""
        
        messages = [
            {"role": "system", "content": "You are a fact extraction assistant. Extract important, memorable facts from user messages. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.chat_completion(messages, temperature=0.3)
            
            # Handle empty or invalid responses
            if not response or not response.strip():
                print("Empty response from Ollama for episode extraction")
                return []
            
            # Try to parse JSON response
            episodes = json.loads(response)
            if isinstance(episodes, list):
                return episodes[:3]  # Limit to 3 episodes
            return []
        except (json.JSONDecodeError, Exception) as e:
            print("Error extracting episodes:", str(e))
            print(f"Response was: '{response}'")
            return []
    
    async def generate_session_summary(self, messages: List[Dict[str, str]]) -> str:
        """Generate session summary from recent messages"""
        if not messages:
            return ""
        
        # Format messages for summarization
        conversation = "\n".join([msg['role'] + ": " + msg['content'] for msg in messages])
        
        prompt = f"""Summarize this conversation in 3-5 concise bullet points focusing on key topics, decisions, and important information:
        
        {conversation}
        
        Summary:"""
        
        messages_for_llm = [
            {"role": "system", "content": "You are a conversation summarizer. Create concise, informative summaries."},
            {"role": "user", "content": prompt}
        ]
        
        return await self.chat_completion(messages_for_llm, temperature=0.3)
    
    async def generate_lifetime_summary(self, session_summaries: List[str]) -> str:
        """Generate lifetime summary from session summaries"""
        if not session_summaries:
            return ""
        
        summaries_text = "\n".join(["Session " + str(i+1) + ": " + summary for i, summary in enumerate(session_summaries)])
        
        prompt = f"""Create a concise user profile summary by condensing these session summaries into key characteristics, preferences, and important information about the user:
        
        {summaries_text}
        
        User Profile:"""
        
        messages_for_llm = [
            {"role": "system", "content": "You are a user profile generator. Create concise profiles from conversation summaries."},
            {"role": "user", "content": prompt}
        ]
        
        return await self.chat_completion(messages_for_llm, temperature=0.3)

# Global instance
ollama_client = OllamaClient()
