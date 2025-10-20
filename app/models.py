from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Scope(str, Enum):
    SESSION = "session"
    USER = "user"

# Request models
class ChatRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = "default"
    message: str

class MemoryRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = "default"

# Response models
class ChatResponse(BaseModel):
    reply: str
    memory_used: dict

class MemoryResponse(BaseModel):
    user_id: str
    session_id: str
    recent_messages: List[dict]
    session_summary: Optional[str]
    lifetime_summary: Optional[str]
    recent_episodes: List[str]

class DailyCount(BaseModel):
    date: str
    count: int

class SessionSummary(BaseModel):
    session_id: str
    text: str
    created_at: datetime

class RecentSummaries(BaseModel):
    lifetime: Optional[str]
    sessions: List[SessionSummary]

class AggregateResponse(BaseModel):
    user_id: str
    daily_message_counts: List[DailyCount]
    recent_summaries: RecentSummaries

# Database models
class Message(BaseModel):
    user_id: str
    session_id: str
    role: Role
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Summary(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    scope: Scope
    text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Episode(BaseModel):
    user_id: str
    session_id: str
    fact: str
    importance: float = Field(ge=0.0, le=1.0)
    embedding: List[float]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EpisodeExtraction(BaseModel):
    fact: str
    importance: float
