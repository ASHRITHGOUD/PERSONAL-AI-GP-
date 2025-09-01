# services/redis_service.py

import redis
from utils.config import REDIS_HOST, REDIS_PORT, REDIS_USERNAME, REDIS_PASSWORD

def get_redis_client():
    """Create and return a Redis client."""
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        username=REDIS_USERNAME,
        password=REDIS_PASSWORD,
        decode_responses=True  # store as strings instead of bytes
    )

# -------------------------
# Short-Term Memory (STM)
# -------------------------

def store_message(session_id: str, role: str, message: str, ttl: int = 3600):
    """
    Store a message in Redis for a given session.
    TTL (in seconds) controls how long the message stays in memory.
    """
    r = get_redis_client()
    key = f"chat:{session_id}:messages"
    r.rpush(key, f"{role}:{message}")  # push to list
    r.expire(key, ttl)  # set expiry

def get_messages(session_id: str):
    """
    Retrieve all messages for a given session from Redis.
    Returns a list of strings like 'role:message'.
    """
    r = get_redis_client()
    key = f"chat:{session_id}:messages"
    return r.lrange(key, 0, -1)  # get all list items

def clear_session(session_id: str):
    """
    Delete all stored messages for a given session.
    """
    r = get_redis_client()
    key = f"chat:{session_id}:messages"
    r.delete(key)

# -------------------------
# Connection Test
# -------------------------
if __name__ == "__main__":
    try:
        r = get_redis_client()
        r.ping()
        print("✅ Connected to Redis (STM) successfully!")

        # Example test
        test_session = "test123"
        store_message(test_session, "user", "Hello Redis!")
        store_message(test_session, "assistant", "Hi, how can I help?")
        print("Messages in STM:", get_messages(test_session))

        clear_session(test_session)
        print("After clearing STM:", get_messages(test_session))

    except redis.ConnectionError as e:
        print(f"❌ Redis connection failed: {e}")
