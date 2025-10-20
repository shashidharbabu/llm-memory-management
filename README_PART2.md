# llm-memory-management (Part 2)

A FastAPI-based AI Memory system implementing short-term, long-term (summary), and episodic memory using MongoDB and Ollama local LLM.

## Features

- **Short-term Memory**: Sliding window of recent conversation messages
- **Long-term Memory**: Automatic summarization of conversations and user profiles
- **Episodic Memory**: Extraction and retrieval of important facts with vector embeddings
- **Ollama Integration**: Local LLM for chat completions and embeddings
- **MongoDB Storage**: Persistent storage with optimized indexes

## Prerequisites

1. **Python 3.8+**
2. **MongoDB** (running on localhost:27017)
3. **Ollama** installed and running locally
4. **Required Ollama models**:
   ```bash
   ollama pull phi3:mini
   ollama pull nomic-embed-text
   ```

## Installation

1. **Navigate to Part2 directory**:
   ```bash
   cd /Users/spartan/Documents/DistributedSystems/Assignment06/Part2
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Ollama** (if not already running):
   ```bash
   ollama serve
   ```

4. **Start the FastAPI server**:
   ```bash
   python -m app.main
   # or
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

## API Endpoints

### 1. POST /api/chat
Send a message and get AI response with memory context.

**Request:**
```json
{
  "user_id": "user123",
  "session_id": "session456",
  "message": "Hello, I'm working on a Python project"
}
```

**Response:**
```json
{
  "reply": "Hello! I see you're working on a Python project. How can I help you with it?",
  "memory_used": {
    "short_term_count": 5,
    "long_term_summary": "User is a Python developer working on various projects...",
    "episodic_facts": ["User works on Python projects", "User is a developer"]
  }
}
```

### 2. GET /api/memory/{user_id}
Get memory state for a user.

**Query Parameters:**
- `session_id` (optional, default="default")

**Response:**
```json
{
  "user_id": "user123",
  "session_id": "session456",
  "recent_messages": [...],
  "session_summary": "Recent conversation about Python development...",
  "lifetime_summary": "User profile: Python developer, interested in AI...",
  "recent_episodes": ["User works on Python projects", "User likes AI development"]
}
```

### 3. GET /api/aggregate/{user_id}
Get aggregated data and analytics.

**Response:**
```json
{
  "user_id": "user123",
  "daily_message_counts": [
    {"date": "2024-10-20", "count": 15},
    {"date": "2024-10-21", "count": 8}
  ],
  "recent_summaries": {
    "lifetime": "User profile summary...",
    "sessions": [
      {
        "session_id": "session456",
        "text": "Session summary...",
        "created_at": "2024-10-20T10:30:00Z"
      }
    ]
  }
}
```

## Memory System Details

### Short-term Memory
- Maintains sliding window of recent messages (configurable, default: 10)
- Used for immediate conversation context
- Automatically managed per session

### Long-term Memory
- **Session Summaries**: Generated every 5 user messages
- **Lifetime Summaries**: Generated every 25 user messages
- Stored in MongoDB `summaries` collection
- Used for broader context and user profiling

### Episodic Memory
- Extracts up to 3 important facts per user message
- Generates vector embeddings for semantic search
- Retrieves top-k relevant facts for each conversation turn
- Stored in MongoDB `episodes` collection with embeddings

## Configuration

Environment variables in `.env`:
```
MONGODB_URI=mongodb://localhost:27017/taskmanagement
FASTAPI_PORT=8000
OLLAMA_BASE_URL=http://localhost:11434
CHAT_MODEL=phi3:mini
EMBED_MODEL=nomic-embed-text
SHORT_TERM_N=10
SUMMARIZE_EVERY_USER_MSGS=5
EPISODIC_TOP_K=5
```

## Testing

### Manual Testing with curl

1. **Health Check**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Send a chat message**:
   ```bash
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "test_user",
       "session_id": "test_session",
       "message": "Hello, I am working on a machine learning project"
     }'
   ```

3. **Get memory state**:
   ```bash
   curl "http://localhost:8000/api/memory/test_user?session_id=test_session"
   ```

4. **Get aggregated data**:
   ```bash
   curl http://localhost:8000/api/aggregate/test_user
   ```

### Testing Memory Features

1. **Send 8-10 messages** to trigger summarization
2. **Verify episode extraction** by checking episodic facts in responses
3. **Check MongoDB collections** for stored data:
   - `messages`: Conversation history
   - `summaries`: Session and lifetime summaries
   - `episodes`: Extracted facts with embeddings

## MongoDB Collections

### messages
- `user_id`, `session_id`, `role`, `content`, `created_at`
- Indexed for efficient querying

### summaries
- `user_id`, `session_id`, `scope`, `text`, `created_at`
- `scope`: "session" or "user"
- `session_id`: null for lifetime summaries

### episodes
- `user_id`, `session_id`, `fact`, `importance`, `embedding`, `created_at`
- `embedding`: Vector array for semantic search
- `importance`: Float between 0.0 and 1.0

## Architecture

```
FastAPI App
├── Database Layer (Motor + MongoDB)
├── Memory Modules
│   ├── Short-term (message retrieval)
│   ├── Long-term (summarization)
│   └── Episodic (extraction + retrieval)
├── Services
│   ├── Ollama Client (chat + embeddings)
│   └── Embeddings (cosine similarity)
└── API Endpoints
    ├── POST /api/chat
    ├── GET /api/memory/{user_id}
    └── GET /api/aggregate/{user_id}
```

## Notes

- Reuses the same MongoDB database as Part 1 (`taskmanagement`)
- Part 1 `tasks` collection remains untouched
- Both servers can run simultaneously (Node.js on :3000, FastAPI on :8000)
- Requires Ollama running locally with specified models
