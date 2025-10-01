# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# --- Security/Auth Settings (from auth.py) ---
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# --- Database/Broker Settings (from database.py & celery_app.py) ---
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
# REDIS_URL from database.py and celery_app.py must be unified
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0") 

# --- LLM Settings (from llm_handler.py) ---
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

# --- External Service Settings (from tasks.py) ---
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")