# -*- coding: utf-8 -*-
"""
Конфигурация проекта RAG с ChromaDB и RAGAS.
Поддержка: Российский Proxy API (основной) и OpenAI API (опционально).
"""
import os

from dotenv import load_dotenv

load_dotenv()

VALID_API_PROVIDERS = ("proxy", "openai")

# ==================== API НАСТРОЙКИ ====================

API_PROVIDER = os.getenv("API_PROVIDER", "proxy").lower()

PROXY_API_URL = os.getenv("PROXY_API_URL", "https://api.proxyapi.ru/openai/v1")
PROXY_API_KEY = os.getenv("PROXY_API_KEY", "")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

if API_PROVIDER not in VALID_API_PROVIDERS:
    raise ValueError(
        f"API_PROVIDER должен быть одним из: {', '.join(VALID_API_PROVIDERS)}"
    )

if API_PROVIDER == "proxy":
    if not PROXY_API_URL:
        raise ValueError("PROXY_API_URL не установлен в переменных окружения")
    if not PROXY_API_KEY:
        raise ValueError("PROXY_API_KEY не установлен в переменных окружения")

if API_PROVIDER == "openai" and not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY не установлен в переменных окружения")

# ==================== МОДЕЛИ ====================

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-3.5-turbo")

# ==================== CHROMADB НАСТРОЙКИ ====================

CHROMA_DB_PATH = "./chroma_db"

# ==================== ПАРАМЕТРЫ ЧАНКИНГА ====================

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))

# ==================== ПАРАМЕТРЫ ПОИСКА ====================

TOP_K = int(os.getenv("TOP_K", 5))

# ==================== ПУТЬ К ДАННЫМ ====================

DATA_DIR = os.getenv("DATA_DIR", "./data")
