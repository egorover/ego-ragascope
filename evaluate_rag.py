# -*- coding: utf-8 -*-
"""
Скрипт для оценки качества RAG-системы через RAGAS.
Поддержка: Российский Proxy API (основной) и OpenAI API (опционально).
"""
import math
import os

from datasets import Dataset
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas import evaluate
from ragas.metrics._faithfulness import faithfulness
from ragas.metrics._answer_relevance import answer_relevancy
from ragas.metrics._context_precision import context_precision

import config
from rag_assistant import ask_assistant
from utils.console import configure_stdio_utf8
from utils.openai_client import get_langchain_openai_kwargs

configure_stdio_utf8()

EVALUATION_QUESTIONS = [
    "Какие правила работы сервисной службы?",
    "Как восстановить доступ к аккаунту?",
    "Какое время ответа на обращение клиента?",
    "Можно ли использовать продукт на нескольких устройствах?",
    "Как экспортировать данные из системы?",
]


def prepare_dataset(questions: list[str]) -> Dataset:
    """Подготовка датасета для RAGAS из вопросов."""
    questions_list = []
    answers_list = []
    contexts_list = []
    ground_truths_list = []

    print("Получение ответов от ассистента...")

    for i, question in enumerate(questions, 1):
        print(f"  Обработка вопроса {i}/{len(questions)}: {question}")

        result = ask_assistant(question)

        questions_list.append(question)
        answers_list.append(result["answer"])
        contexts_list.append([chunk["document"] for chunk in result["context"]])
        ground_truths_list.append("")

    return Dataset.from_dict(
        {
            "question": questions_list,
            "answer": answers_list,
            "contexts": contexts_list,
            "ground_truth": ground_truths_list,
        }
    )


def _build_metrics():
    """Собирает метрики RAGAS с учётом выбранного API-провайдера."""
    langchain_config = get_langchain_openai_kwargs()

    if config.API_PROVIDER == "openai":
        os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY
    else:
        os.environ["OPENAI_API_KEY"] = config.PROXY_API_KEY
        os.environ["OPENAI_API_BASE"] = config.PROXY_API_URL

    try:
        # Используем современные фабрики RAGAS для LLM
        from ragas.llms import llm_factory
        from ragas.embeddings import LangchainEmbeddingsWrapper
        from openai import OpenAI
        from langchain_openai import OpenAIEmbeddings as LangchainOpenAIEmbeddings

        print("  Создаём OpenAI клиент...")
        # Создаём клиент OpenAI с кастомными настройками
        openai_client = OpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
            base_url=os.environ.get("OPENAI_API_BASE"),
        )

        print(f"  Создаём LLM: {config.CHAT_MODEL}...")
        # Используем llm_factory для создания современного InstructorLLM
        ragas_llm = llm_factory(
            model=config.CHAT_MODEL,
            provider="openai",
            client=openai_client,
            temperature=0,
        )

        print(f"  Создаём эмбеддинги: {config.EMBEDDING_MODEL}...")
        # Используем Langchain эмбеддинги с обёрткой RAGAS
        langchain_embeddings = LangchainOpenAIEmbeddings(
            model=config.EMBEDDING_MODEL,
            **langchain_config,
        )
        ragas_embeddings = LangchainEmbeddingsWrapper(langchain_embeddings)

        print("  Инициализируем метрики...")
        # Инициализируем старые метрики с LLM и эмбеддингами
        faithfulness.llm = ragas_llm
        faithfulness.embeddings = ragas_embeddings
        answer_relevancy.llm = ragas_llm
        answer_relevancy.embeddings = ragas_embeddings
        context_precision.llm = ragas_llm
        context_precision.embeddings = ragas_embeddings

        print("  Метрики успешно созданы!")
        return [
            faithfulness,
            answer_relevancy,
            context_precision,
        ]

    except Exception as exc:
        print(f"  Ошибка создания метрик через llm_factory: {exc}")
        print("  Используем метрики без кастомизации LLM/эмбеддингов")
        return [faithfulness, answer_relevancy, context_precision]


def _metric_values(result, name: str) -> list[float]:
    """Извлекает числовые значения метрики из результата RAGAS."""
    try:
        values = result[name]
    except (KeyError, TypeError):
        values = getattr(result, name, [])
    return [v for v in values if not math.isnan(v)]


def evaluate_rag_system() -> None:
    """Оценка RAG-системы по предопределённым вопросам."""
    print("=" * 60)
    print("Оценка качества RAG-системы через RAGAS")
    print("=" * 60)
    print(f"Используемый провайдер: {config.API_PROVIDER.upper()}")

    dataset = prepare_dataset(EVALUATION_QUESTIONS)

    print("\nЗапуск оценки метрик...")
    print("Метрики: faithfulness, answer_relevancy, context_precision")

    metrics_to_use = _build_metrics()
    # Запускаем оценку без column_map (поля датасета имеют правильные имена)
    result = evaluate(
        dataset=dataset,
        metrics=metrics_to_use,
        raise_exceptions=False,
    )

    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ОЦЕНКИ")
    print("=" * 60)

    faithfulness_values = _metric_values(result, "faithfulness")
    answer_relevancy_values = _metric_values(result, "answer_relevancy")
    context_precision_values = _metric_values(result, "context_precision")

    avg_faithfulness = (
        sum(faithfulness_values) / len(faithfulness_values)
        if faithfulness_values
        else 0.0
    )
    avg_answer_relevancy = (
        sum(answer_relevancy_values) / len(answer_relevancy_values)
        if answer_relevancy_values
        else float("nan")
    )
    avg_context_precision = (
        sum(context_precision_values) / len(context_precision_values)
        if context_precision_values
        else 0.0
    )

    print(f"\nFaithfulness (верность ответа): {avg_faithfulness:.4f}")
    if not math.isnan(avg_answer_relevancy):
        print(f"Answer Relevancy (релевантность ответа): {avg_answer_relevancy:.4f}")
    else:
        print(
            "Answer Relevancy (релевантность ответа): "
            "не удалось вычислить (ошибка с эмбеддингами)"
        )
    print(f"Context Precision (точность контекста): {avg_context_precision:.4f}")

    print("\n" + "=" * 60)
    print("ДЕТАЛИ ПО ВОПРОСАМ")
    print("=" * 60)

    for i, question in enumerate(EVALUATION_QUESTIONS):
        print(f"\nВопрос {i + 1}: {question}")
        try:
            f_val = result["faithfulness"][i]
            if math.isnan(f_val):
                print("  Faithfulness: не удалось вычислить")
            else:
                print(f"  Faithfulness: {f_val:.4f}")
        except (KeyError, TypeError, IndexError, ValueError):
            print("  Faithfulness: ошибка вычисления")

        try:
            ar_val = result["answer_relevancy"][i]
            if math.isnan(ar_val):
                print("  Answer Relevancy: не удалось вычислить")
            else:
                print(f"  Answer Relevancy: {ar_val:.4f}")
        except (KeyError, TypeError, IndexError, ValueError):
            print("  Answer Relevancy: ошибка вычисления")

        try:
            cp_val = result["context_precision"][i]
            if math.isnan(cp_val):
                print("  Context Precision: не удалось вычислить")
            else:
                print(f"  Context Precision: {cp_val:.4f}")
        except (KeyError, TypeError, IndexError, ValueError):
            print("  Context Precision: ошибка вычисления")

    print("\n" + "=" * 60)
    print("Оценка завершена!")
    print("=" * 60)


if __name__ == "__main__":
    evaluate_rag_system()
