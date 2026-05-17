import logging
from fastapi import FastAPI

from api.routes import router
from config.logger import logger

app = FastAPI(
    title="LLM Service",
    description="Минимальный устойчивый сервис с LLM, кешем, retry и fallback",
    version="0.1.0"
)

app.include_router(router)

from middleware import log_middleware
app.middleware("http")(log_middleware)

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"status": "ok",
            "service": "LLM Service"}


@app.get("/health")
async def health():
    logger.info("Health check performed")
    return {"status": "healthy"}
