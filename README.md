# 🚀 LLM Service

Высоконадёжный микросервис для работы с LLM с поддержкой кеширования, автоматических повторных попыток и fallback-механизмов.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 📋 Оглавление

- [🚀 LLM Service](#-llm-service)
  - [📋 Оглавление](#-оглавление)
  - [✨ Особенности](#-особенности)
    - [🏗 Архитектура Pipeline](#-архитектура-pipeline)
    - [🛡 Устойчивость](#-устойчивость)
    - [⚡️ Кеширование](#️-кеширование)
    - [📊 Наблюдаемость](#-наблюдаемость)
    - [🔒 Безопасность](#-безопасность)
  - [🏗 Архитектура](#-архитектура)
    - [Структура проекта](#структура-проекта)
  - [🚀 Быстрый старт](#-быстрый-старт)
    - [Требования](#требования)
    - [Установка](#установка)
    - [Запуск](#запуск)

## ✨ Особенности

### 🏗 Архитектура Pipeline
- **Clean Architecture** с чётким разделением слоёв
- **Модульность** - каждый компонент легко заменяем
- **Асинхронность** - высокая производительность на asyncio

### 🛡 Устойчивость
- **Retry механизм** - 3 попытки с экспоненциальной задержкой
- **Timeout control** - настраиваемые таймауты для всех внешних вызовов
- **Fallback ответы** - graceful degradation при недоступности LLM
- **Валидация входных данных** - защита от некорректных запросов

### ⚡️ Кеширование
- **TTL кеш** - результаты хранятся 10 минут (настраивается)
- **Умный ключ** - учитывает запрос, модель, температуру и системный промпт
- **Автоочистка** - истекшие записи автоматически удаляются

### 📊 Наблюдаемость
- **Структурированные JSON-логи** - легко интегрируются с ELK, Loki, Datadog
- **Детальное логирование** - каждый этап pipeline логируется с временными метками
- **Cache hit/miss tracking** - мониторинг эффективности кеша

### 🔒 Безопасность
- **API ключ в переменных окружения** - никаких секретов в коде
- **Валидация всех входных данных** - защита от инъекций
- **CORS готов** - легко настраивается для production

## 🏗 Архитектура
```
┌─────────────────────────────────────────────────────────────┐
│ Client                                                      │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTP/JSON
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ API Layer (FastAPI)                                         │
│ • Валидация входных данных (Pydantic)                       │
│ • Маршрутизация                                             │
│ • Middleware (логирование, CORS)                            │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ Business Logic Layer                                        │
│ (ChatService)                                               │
│ • Координация pipeline                                      │
│ • Управление кешем                                          │
│ • Обработка ошибок → fallback                               │
└─────────────────┬───────────────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
┌──────────────┐ ┌──────────────┐
│ Cache Layer  │ │ LLM Layer    │
│ (TTLCache)   │ │ (LLMClient)  │
│              │ │              │
│ • In-memory  │ │ • Retry      │
│ • TTL        │ │ • Timeout    │
│ • Auto-clean │ │ • Fallback   │
└──────────────┘ └──────────────┘
                      │
                      ▼
                  ┌─────────────┐
                  │ LLM API     │
                  │ (OpenAI,    │
                  │ etc.)       │
                  └─────────────┘
```

### Структура проекта

```
llm_service/
├── api/ # API слой
│   └── routes.py # Эндпоинты FastAPI
├── services/ # Бизнес-логика
│   └── chat_service.py # Основной pipeline
├── llm/ # LLM интеграция
│   ├── client.py # HTTP клиент с retry
│   └── prompts.py # Промпт инжиниринг
├── cache/ # Кеширование
│   └── ttl_cache.py # TTL кеш в памяти
├── config/ # Конфигурация
│   ├── settings.py # Настройки из .env
│   └── logger.py # JSON логгер
├── middleware.py # HTTP middleware
├── main.py # Точка входа
├── requirements.txt # Зависимости
├── .env.example # Пример конфигурации
└── README.md # Документация
```


## 🚀 Быстрый старт

### Требования

- Python 3.9 или выше
- API ключ LLM провайдера (OpenAI, Anthropic, и т.д.)

### Установка

1. **Клонируйте репозиторий**

```bash
git clone https://github.com/yourusername/llm-service.git
cd llm-service
```

2. **Создайте виртуальное окружение**
```bash
python -m venv venv

# Активация на Linux/Mac
source venv/bin/activate

# Активация на Windows
venv\Scripts\activate
```

3. **Установите зависимости**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Настройте переменные окружения**
```bash
cp .env.example .env

# Отредактируйте .env файл
nano .env  # или любой другой редактор
```

`.env.example`:
```
# LLM Configuration
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.openai.com/v1/chat/completions
LLM_MODEL=gpt-4o-mini
LLM_TIMEOUT=10

# Cache Configuration
CACHE_TTL_SECONDS=600
```
### Запуск
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```


