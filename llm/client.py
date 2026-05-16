import asyncio
import httpx
import logging

from config.settings import settings

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.base_url = settings.LLM_BASE_URL
        self.model = settings.LLM_MODEL
        self.timeout = settings.LLM_TIMEOUT
        self.temperature = settings.TEMPERATURE

    async def call_llm(self, messages: list[dict]) -> str:
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

        last_error = None

        for attempt in range(1, 4):
            try:
                logger.info({
                    "event": "LLM API call",
                    "attempt": attempt,
                    "model": self.model,
                    "messages": messages,
                })

                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        self.base_url, 
                        json=payload, 
                        headers=headers,
                    )
                    
                if response.status_code >= 500:
                    raise httpx.HTTPStatusError(
                        "Server error", 
                        request=response.request, 
                        response=response,
                    )
                
                response.raise_for_status()
                data = response.json()

                answer = data['choices'][0]['message']['content']
                logger.info({
                    "event": "LLM API response",
                    "attempt": attempt,
                })

                return answer
            
            except (
                httpx.RequestError, 
                httpx.HTTPStatusError
            ) as error:
                last_error = error

                logger.error({
                    "event": "LLM API error",
                    "attempt": attempt,
                    "error": str(error),
                })

                if attempt < 3:
                    delay = 2 ** attempt
                    await asyncio.sleep(delay)

        raise RuntimeError(f"LLM недоступна после ретраев: {last_error}")
                           