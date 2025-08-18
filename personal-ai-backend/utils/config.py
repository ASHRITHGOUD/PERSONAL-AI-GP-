from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
REDIS_URL = os.getenv("REDIS_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
