# backend/llm_handler.py

import os
import google.generativeai as genai
# Corrected import: Only HarmCategory and HarmBlockThreshold are reliably exposed here
from google.generativeai.types import HarmCategory, HarmBlockThreshold 
from dotenv import load_dotenv

# --- Load .env ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("⚠️ No Gemini API key found. Please set GOOGLE_API_KEY or GEMINI_API_KEY in .env")

genai.configure(api_key=api_key)

# --- List supported models (for debug / dynamic selection) ---
def list_models():
    """Returns a list of model names or an error message."""
    try:
        models = genai.list_models()
        return [m.name for m in models]
    except Exception as e:
        return [f"⚠️ Error listing models: '{type(e).__name__}' - {e}"]

print("Supported Gemini models:", list_models())

# --- Pick first model that supports generateContent (Text/Chat) ---
def get_first_working_model():
    """Picks a suitable model, prioritizing flash for fast chat."""
    preferred_models = ["models/gemini-2.5-flash", "models/gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-pro"]
    
    try:
        available_models = {m.name for m in genai.list_models()}
    except Exception:
        available_models = set()

    for model_name in preferred_models:
        if model_name in available_models:
            return model_name
            
    return "models/gemini-2.5-flash"

MODEL_NAME = get_first_working_model()
print("Using Gemini model:", MODEL_NAME)

# --- Define Safety Settings ---
# FIX: Defined as a list of dictionaries as expected by the SDK when the explicit class is not available
safety_settings = [
    {
        "category": HarmCategory.HARM_CATEGORY_HARASSMENT,
        "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    },
    {
        "category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    },
    {
        "category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    },
    {
        "category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        "threshold": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    },
]

# --- Ask Gemini safely ---
def ask_gemini(prompt: str) -> str:
    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME, 
            safety_settings=safety_settings
        )
        response = model.generate_content(prompt)
        
        if response.prompt_feedback.block_reason:
            return f"🚫 Your request was blocked due to safety policy: {response.prompt_feedback.block_reason.name}"
            
        return response.text or "⚠️ No meaningful text response from Gemini."
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "⚠️ Sorry, the AI service is currently unavailable (API Error or Quota Exceeded)."

# The following code relies on imports from your other backend files:
from backend.database import redis_client, users_collection, get_user_preferences
from backend.task_utils import detect_task 

class DialogueManager:
    def __init__(self):
        self.redis = redis_client
        self.users = users_collection

    async def get_context(self, user_id: str):
        """Fetch short-term + long-term context + preferences."""
        short_term_bytes = await self.redis.get(f"context:{user_id}")
        short_term = short_term_bytes.decode('utf-8') if short_term_bytes else ""
        
        user_profile = await self.users.find_one({"_id": user_id}) or {}
        preferences = await get_user_preferences(user_id)
        return short_term, user_profile, preferences.get("preferences", {})

    async def save_context(self, user_id: str, context: str):
        """Save dialogue context into Redis (short-term)."""
        await self.redis.setex(f"context:{user_id}", 300, context)

    async def handle_message(self, user_id: str, msg: str) -> str:
        """Main dialogue pipeline."""
        short_term, user_profile, prefs = await self.get_context(user_id)

        # --- Task detection ---
        task_result = detect_task(msg) 
        if hasattr(task_result, 'get') and callable(task_result.get):
             try:
                 return task_result.get(timeout=30)  
             except Exception as e:
                 return f"⚠️ Task Error: {e}"
        elif task_result:
             return task_result

        # --- Build contextual prompt ---
        profile_str = f"""
User Preferences:
- Tone: {prefs.get('tone', 'neutral')}
- Style: {prefs.get('style', 'short')}
- Language: {prefs.get('language', 'en')}
- Nickname: {prefs.get('nickname', 'Friend')}
- Topics: {prefs.get('topics', 'None specified')}
"""
        max_context_len = 1000 
        trimmed_short_term = short_term[-max_context_len:] if len(short_term) > max_context_len else short_term
        
        prompt = f"""
You are an intelligent assistant. Follow the user's preferences strictly.
Conversation history: {trimmed_short_term}

{profile_str}

User: {msg}
Assistant:"""

        # --- Query Gemini safely ---
        reply = ask_gemini(prompt)

        # --- Save updated context ---
        new_context = f"{trimmed_short_term} | User: {msg} | Assistant: {reply}"
        await self.save_context(user_id, new_context)

        return reply