from fastapi import APIRouter
from services.redis_service import store_message, get_messages
from services.mongo_services import save_to_ltm

router = APIRouter(tags=["Chat"])

@router.post("/chat")
async def chat(message: dict):
    """
    Receive message from frontend, store in Redis & MongoDB, return conversation
    """
    user_input = message.get("message", "").strip()
    session_id = message.get("threadId", "default_session")
    user_id = "default_user"

    if not user_input:
        return {"error": "No message provided"}

    # Store in Redis
    store_message(session_id, "user", user_input)

    # Store in MongoDB
    save_to_ltm(user_id, "user", user_input)

    # Get full conversation from Redis
    conversation = get_messages(session_id)

    return {
        "status": "success",
        "stored_message": user_input,
        "conversation": conversation
    }
# routes/chat_routes.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.llm_service import get_llm_response # Import the LLM service function

router = APIRouter()

@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # 1. Receive the user's message
            user_message = await websocket.receive_text()
            print(f"User message: {user_message}")
            
            # 2. Call the LLM service with the user's message
            llm_response = get_llm_response(user_message)
            
            # 3. Send the LLM's response back to the client
            await websocket.send_text(llm_response)
            
    except WebSocketDisconnect:
        print("Client disconnected.")
