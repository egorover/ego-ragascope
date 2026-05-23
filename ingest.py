# -*- coding: utf-8 -*-
"""
Скрипт для загрузки документов, создания эмбеддингов и сохранения в ChromaDB.
Поддержка: Российский Proxy API (основной) и OpenAI API (опционально).
"""
from pathlib import Path

import chromadb
from chromadb.config import Settings

import config
from text_processing import chunk_text, clean_text
from utils.console import configure_stdio_utf8
from utils.openai_client import create_openai_client

configure_stdio_utf8()

client = create_openai_client()


def get_embedding(text: str) -> list[float]:
    """Получение эмбеддинга для текста через OpenAI-совместимый API."""
    response = client.embeddings.create(
        model=config.EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


def ingest_documents() -> None:
    """Индексация документов из DATA_DIR в ChromaDB."""
    print("Начало индексации документов...")

    chroma_client = chromadb.PersistentClient(
        path=config.CHROMA_DB_PATH,
        settings=Settings(anonymized_telemetry=False),
    )

    try:
        chroma_client.delete_collection("rag_collection")
    except (ValueError, Exception):
        pass

    collection = chroma_client.create_collection(
        name="rag_collection",
        metadata={"description": "RAG collection for demo project"},
    )

    data_path = Path(config.DATA_DIR)
    txt_files = list(data_path.glob("*.txt"))

    if not txt_files:
        print(f"Не найдено txt файлов в папке {config.DATA_DIR}")
        return

    print(f"Найдено {len(txt_files)} файлов для индексации")

    all_chunks: list[str] = []
    all_embeddings: list[list[float]] = []
    all_metadatas: list[dict] = []
    all_ids: list[str] = []

    chunk_counter = 0

    for file_path in txt_files:
        print(f"Обработка файла: {file_path.name}")

        with open(file_path, encoding="utf-8") as f:
            text = f.read()

        cleaned_text = clean_text(text)
        chunks = chunk_text(cleaned_text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
        print(f"  Создано {len(chunks)} чанков")

        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)

            all_chunks.append(chunk)
            all_embeddings.append(embedding)
            all_metadatas.append({"source": file_path.name, "chunk_id": i})
            all_ids.append(f"{file_path.stem}_chunk_{i}")

            chunk_counter += 1
            if chunk_counter % 10 == 0:
                print(f"  Обработано {chunk_counter} чанков...")

    print(f"\nСохранение {len(all_chunks)} чанков в ChromaDB...")
    collection.add(
        embeddings=all_embeddings,
        documents=all_chunks,
        metadatas=all_metadatas,
        ids=all_ids,
    )

    print(f"Индексация завершена! Всего чанков: {len(all_chunks)}")
    print(f"ChromaDB сохранена в: {config.CHROMA_DB_PATH}")


if __name__ == "__main__":
    ingest_documents()
