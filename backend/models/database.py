# backend/models/database.py
import motor.motor_asyncio
import redis.asyncio as aioredis
from bson.objectid import ObjectId # Needed for get_user_by_id in auth helpers
from ..config import MONGO_URI, MONGO_DB, REDIS_URL # <--- NEW IMPORT

# --- MongoDB Client (from database.py) ---
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB]

# --- Collections (used for user/preferences/context) ---
users_collection = db["users"]
preferences_collection = db["preferences"]

# --- Redis Client (from database.py) ---
redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)

# --- Preference Helpers (from database.py) ---
async def get_user_preferences(user_id: str):
    prefs = await preferences_collection.find_one({"user_id": user_id})
    return prefs or {}

async def save_user_preferences(user_id: str, preferences: dict):
    await preferences_collection.update_one(
        {"user_id": user_id},
        {"$set": {"preferences": preferences}},
        upsert=True
    )

# --- Auth Database Helpers (from auth.py) ---
async def get_user_by_username(username: str):
    return await users_collection.find_one({"username": username})

async def get_user_by_id(user_id: str):
    # Ensure ObjectId import is handled
    return await users_collection.find_one({"_id": ObjectId(user_id)})