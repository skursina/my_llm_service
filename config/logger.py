import logging
import os
import json


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, 'extra'):
            log_record.update(record.extra)
        # Поддержка вложенных extra
        if getattr(record, 'extra', None) and isinstance(record.extra, dict):
            log_record.update(record.extra)
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
