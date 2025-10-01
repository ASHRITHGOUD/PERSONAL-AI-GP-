# backend/models/memory_model.py
from pydantic import BaseModel
from typing import Optional, Dict

# From old schemas.py
class UserPreferences(BaseModel):
    tone: Optional[str] = "neutral"
    style: Optional[str] = "short"
    language: Optional[str] = "en"
    nickname: Optional[str] = None
    topics: Optional[Dict[str, int]] = {}