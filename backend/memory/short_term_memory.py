# backend/memory/short_term_memory.py
from ..models.database import redis_client # <--- NEW IMPORT

async def get_conversation_context(user_id: str):
    """Fetch short-term context from Redis."""
    # From old dialogue_manager.py: short_term_bytes = await self.redis.get(...)
    short_term_bytes = await redis_client.get(f"context:{user_id}")
    return short_term_bytes.decode('utf-8') if short_term_bytes else ""

async def save_conversation_context(user_id: str, context: str):
    """Save dialogue context into Redis (short-term)."""
    # From old dialogue_manager.py: await self.redis.setex(...)
    await redis_client.setex(f"context:{user_id}", 300, context)