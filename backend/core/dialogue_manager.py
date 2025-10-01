# backend/core/dialogue_manager.py
from ..models.database import users_collection, get_user_preferences
from ..memory.short_term_memory import get_conversation_context, save_conversation_context
from ..services.language_model_service import ask_gemini # <-- The function being imported
from .natural_language_understanding import detect_task

class DialogueManager:
    def __init__(self):
        # The class is initialized without specific DB clients here (cleaner design)
        pass 

    async def get_context(self, user_id: str):
        """Fetch short-term + long-term context + preferences."""
        short_term = await get_conversation_context(user_id) 
        user_profile = await users_collection.find_one({"_id": user_id}) or {}
        preferences = await get_user_preferences(user_id)
        
        return short_term or "", user_profile, preferences.get("preferences", {})

    async def save_context(self, user_id: str, context: str):
        """Save dialogue context into Redis (short-term)."""
        await save_conversation_context(user_id, context)

    async def handle_message(self, user_id: str, msg: str) -> str:
        """Main dialogue pipeline (COPIED FROM OLD FILE)"""
        short_term, user_profile, prefs = await self.get_context(user_id)

        # --- Task detection ---
        task_result = detect_task(msg)
        if hasattr(task_result, 'get') and callable(task_result.get):
             try:
                 # NOTE: Blocks the event loop, but preserves original logic
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
        reply = ask_gemini(prompt) # <-- Call that was failing

        # --- Save updated context ---
        new_context = f"{trimmed_short_term} | User: {msg} | Assistant: {reply}"
        await self.save_context(user_id, new_context)

        return reply