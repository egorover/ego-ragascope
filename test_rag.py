# -*- coding: utf-8 -*-
"""
Простой тест RAG-ассистента
"""
from rag_assistant import ask_assistant

# Тестовые вопросы
questions = [
    "Какое время ответа на обращение клиента?",
    "Какие правила работы сервисной службы?",
    "Как восстановить доступ к аккаунту?",
]

print("=" * 60)
print("Тест RAG-ассистента")
print("=" * 60)

for i, question in enumerate(questions, 1):
    print(f"\n[Вопрос {i}] {question}")
    print("-" * 60)
    
    result = ask_assistant(question)
    
    print(f"\n[Ответ]\n{result['answer']}")
    print(f"\n[Найдено чанков: {len(result['context'])}]")
    
    if result['context']:
        print(f"  - {result['context'][0]['metadata']['source']}")

print("\n" + "=" * 60)
print("Тест завершен!")
print("=" * 60)