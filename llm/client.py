import httpx
import logging
from typing import List, Dict

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config.settings import settings

logger = logging.getLogger("llm_service")


class LLMClient:
    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.base_url = settings.LLM_BASE_URL
        self.model = settings.LLM_MODEL
        self.timeout = settings.LLM_TIMEOUT
        self.temperature = settings.TEMPERATURE

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_exception_type((
            httpx.RequestError,
            httpx.TimeoutException,
            httpx.RemoteProtocolError,
            httpx.HTTPStatusError
        )),
        reraise=True
    )
    async def call_llm(self, messages: List[Dict[str, str]]) -> str:
        if not self.api_key:
            raise RuntimeError("LLM_API_KEY не задан в .env")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }

        logger.info(
            "LLM API call",
            extra={
                "model": self.model,
                "messages_count": len(messages)
            }
        )

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.base_url,
                json=payload,
                headers=headers,
            )

        # Проверяем статус ответа
        response.raise_for_status()
        data = response.json()
        
        # Надежная проверка структуры ответа
        if not data:
            raise ValueError("Пустой ответ от LLM")
            
        # Попробуем разные возможные структуры ответа
        answer = None
        
        # Попытка 1: Стандартная структура OpenAI
        if 'choices' in data and len(data['choices']) > 0:
            choice = data['choices'][0]
            if 'message' in choice and 'content' in choice['message']:
                answer = choice['message']['content']
            elif 'text' in choice:
                answer = choice['text']
                
        # Попытка 2: Прямой ответ (некоторые API возвращают текст напрямую)
        if not answer and 'content' in data:
            answer = data['content']
            
        # Попытка 3: Поле response или answer
        if not answer and 'response' in data:
            answer = data['response']
        if not answer and 'answer' in data:
            answer = data['answer']
            
        if not answer:
            raise ValueError(f"Не удалось извлечь ответ из данных LLM: {data}")

        logger.info(
           "LLM API response received",
            extra={
                "event": "llm_response",
                "model": self.model,
                "answer": answer,
                "completion_tokens": data.get("usage", {}).get("completion_tokens"),
                }
        )
        
        return answer