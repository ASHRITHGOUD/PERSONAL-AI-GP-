# backend/memory/short_term_memory.py
from ..models.database import redis_client # <--- NEW IMPORT

async def get_conversation_context(user_id: str):
    """Fetch short-term context from Redis."""
    # Since redis_client is initialized with decode_responses=True (in models/database.py),
    # the result is ALREADY a string (or None).
    short_term_string = await redis_client.get(f"context:{user_id}")
    
    # FIX: Check if the string is None, and return the string directly (no decode needed).
    return short_term_string if short_term_string is not None else ""

async def save_conversation_context(user_id: str, context: str):
    """Save dialogue context into Redis (short-term)."""
    # This remains correct as setex accepts strings when decode_responses=True
    await redis_client.setex(f"context:{user_id}", 300, context)