"""
Конфигурация проекта RAG с ChromaDB и RAGAS
Поддержка: Российский Proxy API (основной) и OpenAI API (опционально)
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# ==================== API НАСТРОЙКИ ====================

# Выбор провайдера API: "proxy" (Российский Proxy API) или "openai" (OpenAI)
API_PROVIDER = os.getenv("API_PROVIDER", "proxy").lower()

# Российский Proxy API (основной по умолчанию)
PROXY_API_URL = os.getenv("PROXY_API_URL", "https://proxy.api.example.com/v1")
PROXY_API_KEY = os.getenv("PROXY_API_KEY", "")

# OpenAI API (опционально)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Валидация конфигурации
if API_PROVIDER == "proxy" and not PROXY_API_URL:
    raise ValueError("PROXY_API_URL не установлен в переменных окружения")

if API_PROVIDER == "openai" and not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY не установлен в переменных окружения")

# ==================== МОДЕЛИ ====================

# Модель для эмбеддингов
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# Модель для чата
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-3.5-turbo")

# ==================== CHROMADB НАСТРОЙКИ ====================

# Путь к ChromaDB
CHROMA_DB_PATH = "./chroma_db"

# ==================== ПАРАМЕТРЫ ЧАНКИНГА ====================

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))  # размер чанка в символах
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))  # overlap между чанками в символах

# ==================== ПАРАМЕТРЫ ПОИСКА ====================

TOP_K = int(os.getenv("TOP_K", 5))  # количество релевантных чанков для поиска

# ==================== ПУТЬ К ДАННЫМ ====================

DATA_DIR = os.getenv("DATA_DIR", "./data")

