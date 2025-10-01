# backend/models/api_models.py
from pydantic import BaseModel

# From old schemas.py
class DialogueRequest(BaseModel):
    user_id: str
    text: str

class DialogueResponse(BaseModel):
    user_id: str
    response: str