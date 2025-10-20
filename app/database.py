import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING
from dotenv import load_dotenv

load_dotenv()

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

async def get_database():
    if db.db is None:
        await connect_to_mongo()
    return db.db

async def connect_to_mongo():
    """Create database connection"""
    db.client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    db.db = db.client[os.getenv("DATABASE_NAME", "assignment06")]
    
    # Create indexes for better performance
    await create_indexes()
    print("Connected to MongoDB")

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")

async def create_indexes():
    """Create database indexes"""
    # Messages collection indexes
    messages_indexes = [
        IndexModel([("user_id", ASCENDING)]),
        IndexModel([("session_id", ASCENDING)]),
        IndexModel([("created_at", ASCENDING)]),
        IndexModel([("user_id", ASCENDING), ("session_id", ASCENDING), ("created_at", ASCENDING)])
    ]
    await db.db.messages.create_indexes(messages_indexes)
    
    # Summaries collection indexes
    summaries_indexes = [
        IndexModel([("user_id", ASCENDING)]),
        IndexModel([("scope", ASCENDING)]),
        IndexModel([("user_id", ASCENDING), ("scope", ASCENDING)]),
        IndexModel([("created_at", ASCENDING)])
    ]
    await db.db.summaries.create_indexes(summaries_indexes)
    
    # Episodes collection indexes
    episodes_indexes = [
        IndexModel([("user_id", ASCENDING)]),
        IndexModel([("session_id", ASCENDING)]),
        IndexModel([("created_at", ASCENDING)]),
        IndexModel([("user_id", ASCENDING), ("session_id", ASCENDING)])
    ]
    await db.db.episodes.create_indexes(episodes_indexes)
    
    print("Database indexes created")
