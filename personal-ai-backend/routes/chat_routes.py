from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.llm_service import get_llm_response
from services.redis_service import store_message, get_messages
from services.mongo_services import save_to_ltm

router = APIRouter(tags=["Chat"])

# REST endpoint for chat
@router.post("/chat")
async def chat(message: dict):
    user_input = message.get("message", "").strip()
    session_id = message.get("threadId", "default_session")
    user_id = "default_user"

    if not user_input:
        return {"error": "No message provided"}

    store_message(session_id, "user", user_input)
    save_to_ltm(user_id, "user", user_input)
    conversation = get_messages(session_id)

    return {
        "status": "success",
        "stored_message": user_input,
        "conversation": conversation
    }

# WebSocket endpoint for live chat
@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            user_message = await websocket.receive_text()
            print(f"User message: {user_message}")
            
            llm_response = get_llm_response(user_message)
            await websocket.send_text(llm_response)
    except WebSocketDisconnect:
        print("Client disconnected.")
