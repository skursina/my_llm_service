import logging
import time
from fastapi import Request

logger = logging.getLogger("llm_service")


async def log_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Логируем входящий запрос
    logger.info(
        "Incoming request",
        extra={
            "method": request.method,
            "url": str(request.url),
            "client_host": request.client.host,
        }
    )
    
    try:
        response = await call_next(request)
        
        # Логируем ответ
        duration = time.time() - start_time
        logger.info(
            "Request completed",
            extra={
                "status_code": response.status_code,
                "duration_sec": round(duration, 3)
            }
        )
        
        return response
        
    except Exception as exc:
        # Логируем ошибку
        duration = time.time() - start_time
        logger.error(
            "Request failed",
            extra={
                "error": str(exc),
                "duration_sec": round(duration, 3)
            }
        )
        raise