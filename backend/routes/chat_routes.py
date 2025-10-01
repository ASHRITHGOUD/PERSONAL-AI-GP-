# backend/routes/chat_routes.py
# backend/routes/chat_routes.py
import json
from fastapi import APIRouter, WebSocket
from ..core.dialogue_manager import DialogueManager # <-- Now importing the complete class
from ..models.api_models import DialogueRequest, DialogueResponse 

router = APIRouter()
dm = DialogueManager() # Instantiate the manager

# ... (rest of the file is correct) ...

# --- REST API for Dialogue (from main.py) ---
@router.post("/chat", response_model=DialogueResponse)
async def chat(request: DialogueRequest):
    reply = await dm.handle_message(request.user_id, request.text)
    return DialogueResponse(user_id=request.user_id, response=reply)

# --- WebSocket for Dialogue (from main.py) ---
@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    while True:
        data = await ws.receive_text()
        try:
            data_json = json.loads(data)
            user_id = data_json.get("user_id", "guest")
            msg = data_json.get("text", "")
        except Exception:
            user_id, msg = "guest", data

        reply = await dm.handle_message(user_id, msg)
        await ws.send_text(reply)