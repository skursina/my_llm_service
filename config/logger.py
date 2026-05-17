import logging
import os
import json


class JsonFormatter(logging.Formatter):
    def format(self, record):
        # Создаем базовую запись
        log_record = {
            "level": record.levelname,
            "message": record.getMessage(),
        }
        
        extra_fields = [
            'event',
            'user_message',
            'answer',
            'source',
            'execution_time_sec',
            'status_code',
            'duration_sec',
            'method',
            'url',
            'model',
            'messages_count',
            'completion_tokens',
        ]

        for field in extra_fields:
            if hasattr(record, field):
                log_record[field] = getattr(record, field)
        
        return json.dumps(log_record, ensure_ascii=False)


os.makedirs("logs", exist_ok=True)

# Создаём отдельный логгер для приложения
logger = logging.getLogger("llm_service")
logger.setLevel(logging.INFO)

# Предотвращаем дублирование логов
logger.propagate = False

# Обработчик для консоли
console_handler = logging.StreamHandler()
console_handler.setFormatter(JsonFormatter())

# Обработчик для файла
file_handler = logging.FileHandler("logs/app.log", encoding='utf-8')
file_handler.setFormatter(JsonFormatter())

# Добавляем обработчики, если их ещё нет
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
