from fastapi import APIRouter
from dm.dialogue_manager import handle_message

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/")
async def chat(message: dict):
    user_input = message.get("text")
    response = await handle_message(user_input)
    return {"response": response}
