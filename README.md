# RAG с ChromaDB и RAGAS - Учебный проект

Минимальный проект для демонстрации работы RAG-системы с локальной векторной базой ChromaDB и оценкой качества через RAGAS.

**Поддержка API:**
- 🇷🇺 **Российский Proxy API** (основной по умолчанию)
- 🌐 **OpenAI API** (опционально)

## Что делает проект

Проект реализует полный цикл RAG:
1. Загрузка и индексация документов в ChromaDB
2. Поиск релевантного контекста по запросу
3. Генерация ответов через Proxy API или OpenAI
4. Оценка качества системы через RAGAS

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Создайте файл `.env` в корне проекта и настройте API:

### Вариант 1: Российский Proxy API (рекомендуется)
```
API_PROVIDER=proxy
PROXY_API_URL=https://proxy.api.example.com/v1
PROXY_API_KEY=your_proxy_api_key_here
```

### Вариант 2: OpenAI API (опционально)
```
API_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
```

### Дополнительные настройки (опционально):
```
EMBEDDING_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-3.5-turbo
CHUNK_SIZE=500
CHUNK_OVERLAP=100
TOP_K=5
DATA_DIR=./data
```

## Использование

### 1. Индексация документов

Запустите скрипт для загрузки документов из папки `data/` и создания векторной базы:

```bash
python ingest.py
```

Это создаст локальную базу ChromaDB в папке `chroma_db/`.

### 2. Задать вопрос ассистенту

Запустите интерактивный режим ассистента:

```bash
python rag_assistant.py
```

Введите вопрос и получите ответ на основе документов из базы. Для выхода введите `exit`.

### 3. Оценка качества через RAGAS

Запустите скрипт оценки:

```bash
python evaluate_rag.py
```

Скрипт автоматически задаст 5 предопределённых вопросов, получит ответы и рассчитает метрики:
- **Faithfulness** - верность ответа (насколько ответ основан на контексте)
- **Answer Relevancy** - релевантность ответа вопросу
- **Context Precision** - точность выбранного контекста

## Структура проекта

```
rag_chromadb_ragas_demo/
├── data/              # Исходные документы
├── chroma_db/         # Локальная база ChromaDB (создаётся автоматически)
├── ingest.py          # Скрипт индексации
├── rag_assistant.py   # RAG-ассистент
├── evaluate_rag.py    # Оценка через RAGAS
├── config.py          # Конфигурация
├── requirements.txt   # Зависимости
└── README.md          # Этот файл
```

