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
