import httpx
import logging
from typing import List, Dict

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config.settings import settings

logger = logging.getLogger(__name__)


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
                "extra": {
                    "model": self.model,
                    "messages_count": len(messages)
                }
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

        if not data.get("choices") or len(data["choices"]) == 0:
            raise ValueError("Ответ LLM не содержит choices")

        answer = data['choices'][0]['message']['content']
        logger.info("LLM API response received")
        return answer