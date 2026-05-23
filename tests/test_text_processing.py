# -*- coding: utf-8 -*-
"""Офлайн-тесты обработки текста (без API и ChromaDB)."""
import unittest

from text_processing import chunk_text, clean_text


class TestCleanText(unittest.TestCase):
    def test_collapses_whitespace(self):
        self.assertEqual(clean_text("  привет   мир\n\n"), "привет мир")

    def test_preserves_cyrillic(self):
        text = "Правила работы сервисной службы"
        self.assertEqual(clean_text(text), text)


class TestChunkText(unittest.TestCase):
    def test_single_short_chunk(self):
        text = "Короткий текст"
        chunks = chunk_text(text, chunk_size=500, overlap=50)
        self.assertEqual(chunks, ["Короткий текст"])

    def test_multiple_chunks_with_overlap(self):
        text = "а" * 1000
        chunks = chunk_text(text, chunk_size=400, overlap=100)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(c) <= 400 for c in chunks))

    def test_invalid_chunk_size(self):
        with self.assertRaises(ValueError):
            chunk_text("текст", chunk_size=0, overlap=0)

    def test_invalid_overlap(self):
        with self.assertRaises(ValueError):
            chunk_text("текст", chunk_size=100, overlap=100)


if __name__ == "__main__":
    unittest.main()
