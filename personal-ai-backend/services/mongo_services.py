# services/mongo_service.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# MongoDB Config
MONGO_URI = os.getenv("MONGODB_URI", "")
MONGO_DB = os.getenv("MONGO_DB", "personal_ai")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "long_term_memory")


def get_mongo_client():
    return MongoClient(MONGO_URI)


# Save a message to LTM
def save_to_ltm(user_id, role, message):
    client = get_mongo_client()
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    
    entry = {
        "user_id": user_id,
        "role": role,
        "message": message,
        "timestamp": datetime.utcnow()
    }
    collection.insert_one(entry)


# Get all stored history for a user
def get_ltm_history(user_id, limit=50):
    client = get_mongo_client()
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    
    return list(collection.find({"user_id": user_id}).sort("timestamp", -1).limit(limit))


# Delete a user's stored history
def delete_ltm_history(user_id):
    client = get_mongo_client()
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    
    collection.delete_many({"user_id": user_id})


# Test connection
if __name__ == "__main__":
    try:
        client = get_mongo_client()
        client.admin.command('ping')
        print("✅ Connected to MongoDB (LTM)")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
