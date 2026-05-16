import logging
import json
from fastapi import FastAPI

from api.routes import router

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(log_record, ensure_ascii=False)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(JsonFormatter())

file_handler = logging.FileHandler("logs/app.log", encoding='utf-8')
file_handler.setFormatter(JsonFormatter())

logger.addHandler(console_handler)
logger.addHandler(file_handler)


app = FastAPI(
    title="LLM Service",
    description="Минимальный устойчивый сервис с LLM, кешем, retry и fallback",
    version="0.1.0"
)

app.include_router(router)

@app.get("/")
async def root():
    return {"status": "ok",
            "service": "LLM Service"}
