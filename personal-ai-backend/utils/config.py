import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB configuration
MONGO_URI = os.getenv("MONGODB_URI", "")
MONGO_DB = os.getenv("MONGO_DB", "personal_ai")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "ltm")

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_USERNAME = os.getenv("REDIS_USERNAME") or None
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD") or None

# Short-Term Memory (STM) settings
STM_TTL_SECONDS = 60 * 30  # 30 minutes
STM_MAX_MESSAGES = 20

# Optional: API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
