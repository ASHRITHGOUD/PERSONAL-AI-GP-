from services.llm_service import ask_llm

async def handle_message(user_input: str):
    # For now, just forward to LLM
    response = await ask_llm(user_input)
    return response
