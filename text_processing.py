# -*- coding: utf-8 -*-
"""Разбиение и очистка текста для индексации."""
import re


def clean_text(text: str) -> str:
    """Удаляет лишние пробелы и переносы строк."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """
    Разбивает текст на чанки с overlap.

    Args:
        text: исходный текст
        chunk_size: размер чанка в символах
        overlap: размер overlap между чанками в символах

    Returns:
        список чанков
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size должен быть положительным")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap должен быть в диапазоне [0, chunk_size)")

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        if end < len(text):
            space_pos = text.rfind(" ", start, end)
            if space_pos != -1:
                end = space_pos

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap
        if start <= 0:
            start = end

    return chunks
