from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=1000,
        description="Сообщение пользователя для LLM, до 1000 символов",
    )


@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        result = await chat_service.process_message(request.message)
        return result

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
