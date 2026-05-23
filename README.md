# ego-ragascope
ego-ragascope: Microscopic insights into your RAG pipeline quality.

## О проекте
Проект для микроскопического анализа качества RAG-пайплайна: retrieval, генерация, источники и метрики.

Минимальный проект для демонстрации работы RAG-системы с локальной векторной базой ChromaDB и оценкой качества через RAGAS.

**Поддержка API:**
- 🇷🇺 **Российский Proxy API** (основной по умолчанию)
- 🌐 **OpenAI API** (опционально)

## Что внутри
- Оценка качества генерации.
- Анализ retrieval-части.
- Сравнение ответов с источниками.
- Отчёты и метрики.
- Полный цикл RAG: индексация, поиск контекста, генерация ответов.

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

## Запуск

### 1. Индексация документов
Запустите скрипт для загрузки документов из папки `data/` и создания векторной базы:
```bash
python ingest.py
```

### 2. Задать вопрос ассистенту
Запустите интерактивный режим ассистента:
```bash
python rag_assistant.py
```

### 3. Оценка качества через RAGAS
Запустите скрипт оценки:
```bash
python evaluate_rag.py
```

## Метрики оценки
Скрипт оценки автоматически рассчитывает метрики:
- **Faithfulness** - верность ответа (насколько ответ основан на контексте)
- **Answer Relevancy** - релевантность ответа вопросу
- **Context Precision** - точность выбранного контекста

## Структура проекта

```
ego-ragascope/
├── data/              # Исходные документы
├── chroma_db/         # Локальная база ChromaDB (создаётся автоматически)
├── ingest.py          # Скрипт индексации
├── rag_assistant.py   # RAG-ассистент
├── evaluate_rag.py    # Оценка через RAGAS
├── config.py          # Конфигурация
├── requirements.txt   # Зависимости
├── .env               # Переменные окружения (не коммитить!)
└── README.md          # Документация
```

