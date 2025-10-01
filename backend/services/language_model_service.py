# backend/services/language_model_service.py
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold 
from ..config import GEMINI_API_KEY # <-- Configuration setting

# --- Global State ---
# Use global variables to track initialization state
MODEL_NAME = "models/gemini-2.5-flash" # Default model
_model_instance = None
_config_attempted = False

# --- List supported models (from old llm_handler.py) ---
def list_models():
    # FIX: global must be the first line where the variable is used/modified
    global _config_attempted
    
    """Returns a list of model names or an error message."""
    # NOTE: Configuration must be done before listing models
    if not _config_attempted and GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        _config_attempted = True
        
    try:
        models = genai.list_models()
        return [m.name for m in models]
    except Exception as e:
        return [f"⚠️ Error listing models: '{type(e).__name__}' - {e}"]

# --- Pick first model (from old llm_handler.py) ---
def get_first_working_model():
    """Picks a suitable model, prioritizing flash for fast chat."""
    preferred_models = ["models/gemini-2.5-flash", "models/gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-pro"]
    
    try:
        available_models = {m.name for m in list_models()} # Use the local list_models()
    except Exception:
        available_models = set()

    for model_name in preferred_models:
        if model_name in available_models:
            return model_name
            
    return "models/gemini-2.5-flash" # Fallback

# --- Determine final model name early (but configuration is still lazy) ---
MODEL_NAME = get_first_working_model()

# --- Define Safety Settings (from old llm_handler.py) ---
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

# --- Core Initialization Function ---
def _initialize_model():
    # FIX: global must be the first line where the variable is used/modified
    global _model_instance, _config_attempted
    
    if _model_instance is not None:
        return # Already done

    if not GEMINI_API_KEY:
        # We allow the module to load, but mark it as unusable
        _model_instance = False
        return
    
    try:
        # Run configuration if not done already (list_models may have done this)
        if not _config_attempted:
            genai.configure(api_key=GEMINI_API_KEY)
            _config_attempted = True
            
        _model_instance = genai.GenerativeModel(
            model_name=MODEL_NAME, 
            safety_settings=safety_settings
        )
    except Exception as e:
        # Mark as unusable if initialization fails
        print(f"FATAL Gemini Configuration Error: {e}")
        _model_instance = False

# --- Ask Gemini safely (The core function) ---
def ask_gemini(prompt: str) -> str:
    """Queries the Gemini API safely, initializing the model if necessary."""
    # FIX: global must be the first line where the variable is used/modified
    global _model_instance
    
    if _model_instance is None:
        _initialize_model()

    if _model_instance is False:
        return "⚠️ Sorry, the AI service failed to initialize."
        
    try:
        # Use the initialized model instance
        response = _model_instance.generate_content(prompt)
        
        if response.prompt_feedback.block_reason:
            return f"🚫 Your request was blocked due to safety policy: {response.prompt_feedback.block_reason.name}"
            
        return response.text or "⚠️ No meaningful text response from Gemini."
    except Exception as e:
        print(f"Gemini API Runtime Error: {e}")
        return "⚠️ Sorry, the AI service is currently unavailable (API Error or Quota Exceeded)."