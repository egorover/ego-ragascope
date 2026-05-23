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
from ragas.metrics import (
    AnswerRelevancy,
    ContextPrecision,
    Faithfulness,
    answer_relevancy,
    context_precision,
    faithfulness,
)

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
        from ragas.embeddings import LangchainEmbeddingsWrapper
        from ragas.llms import LangchainLLMWrapper

        langchain_embeddings = OpenAIEmbeddings(
            model=config.EMBEDDING_MODEL,
            **langchain_config,
        )
        langchain_llm = ChatOpenAI(
            model_name=config.CHAT_MODEL,
            **langchain_config,
            temperature=0,
        )

        ragas_embeddings = LangchainEmbeddingsWrapper(langchain_embeddings)
        ragas_llm = LangchainLLMWrapper(langchain_llm)

        faithfulness_metric = Faithfulness(llm=ragas_llm)
        answer_relevancy_metric = AnswerRelevancy(
            llm=ragas_llm, embeddings=ragas_embeddings
        )
        try:
            context_precision_metric = ContextPrecision(
                llm=ragas_llm, embeddings=ragas_embeddings
            )
        except TypeError:
            context_precision_metric = ContextPrecision(llm=ragas_llm)

        return [
            faithfulness_metric,
            answer_relevancy_metric,
            context_precision_metric,
        ]

    except ImportError:
        print(
            "Обёртки RAGAS недоступны, используем встроенные метрики "
            "с переменными окружения"
        )
        return [faithfulness, answer_relevancy, context_precision]
    except Exception as exc:
        print(f"Используем встроенные метрики (предупреждение: {exc})")
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
    result = evaluate(dataset=dataset, metrics=metrics_to_use)

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
            ar_val = result["answer_relevancy"][i]
            cp_val = result["context_precision"][i]
        except (KeyError, TypeError):
            f_val = getattr(result, "faithfulness", [0])[i]
            ar_val = getattr(result, "answer_relevancy", [float("nan")])[i]
            cp_val = getattr(result, "context_precision", [0])[i]

        print(f"  Faithfulness: {f_val:.4f}")
        if not math.isnan(ar_val):
            print(f"  Answer Relevancy: {ar_val:.4f}")
        else:
            print("  Answer Relevancy: не удалось вычислить")
        print(f"  Context Precision: {cp_val:.4f}")

    print("\n" + "=" * 60)
    print("Оценка завершена!")
    print("=" * 60)


if __name__ == "__main__":
    evaluate_rag_system()
