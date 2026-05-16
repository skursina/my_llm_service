import time
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class TTLCache:
    def __init__(self, ttl_seconds: int):
        self.ttl_seconds = ttl_seconds
        self.storage = {}

    def make_key(self, message: str, model: str, temperature: float, system_prompt: str) -> str:
        raw_key = {
            "message": message,
            "model": model,
            "temperature": temperature,
            "system_prompt": system_prompt,
        }
        key_string = json.dumps(raw_key, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(key_string.encode("utf-8")).hexdigest()

    def get(self, key: str):
        item = self.storage.get(key)

        if not item:
            logger.info({"event": "cache_miss", "key": key})
            return None

        value, created_at = item

        if time.time() - created_at > self.ttl_seconds:
            logger.info({"event": "cache_expired", "key": key})
            del self.storage[key]
            return None

        logger.info({"event": "cache_hit", "key": key})
        return value

    def set(self, key: str, value: str):
        self.storage[key] = (value, time.time())
        logger.info({"event": "cache_set", "key": key})