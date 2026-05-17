import logging
import time

from cache.ttl_cache import TTLCache
from config.settings import settings
from llm.client import LLMClient
from llm.prompts import SYSTEM_PROMPT, build_prompt

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self):
        self.cache = TTLCache(ttl_seconds=settings.CACHE_TTL_SECONDS)
        self.llm_client = LLMClient()

    async def process_message(self, message: str) -> dict:
        start_time = time.time()

        logger.info(
            "Pipeline started",
            extra={
                "event": "pipeline_started",
                "message": message
            }
        )

        cache_key = self.cache.make_key(
            message=message,
            model=settings.LLM_MODEL,
            temperature=settings.TEMPERATURE,
            system_prompt=SYSTEM_PROMPT,
        )

        cached_answer = self.cache.get(cache_key)

        if cached_answer:
            result = {
                "answer": cached_answer,
                "source": "cache",
                "execution_time_sec": round(time.time() - start_time, 3),
            }
            logger.info(
                "Cache hit",
                extra={
                    "event": "cache_hit",
                    "message": message,
                    "answer": cached_answer
                }
            )
            return result

        messages = build_prompt(message)

        try:
            raw_answer = await self.llm_client.call_llm(messages)

            answer = self.postprocess(raw_answer)

            self.cache.set(cache_key, answer)

            logger.info(
                "Pipeline finished",
                extra={
                    "event": "pipeline_finished",
                    "source": "llm",
                    "execution_time_sec": round(time.time() - start_time, 3),
                    "answer": answer
                }
            )

            return {
                "answer": answer,
                "source": "llm",
                "execution_time_sec": round(time.time() - start_time, 3),
            }

        except Exception as error:
            logger.error({
                "event": "fallback",
                "error": str(error),
                "type": type(error).__name__
            })

            return {
                "answer": "Сервис временно недоступен, попробуйте позже.",
                "source": "fallback",
                "execution_time_sec": round(time.time() - start_time, 3),
            }

    def postprocess(self, answer: str) -> str:
        if not answer or not answer.strip():
            raise ValueError("Пустой ответ модели")

        return " ".join(answer.strip().split())