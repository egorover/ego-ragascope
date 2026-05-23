# -*- coding: utf-8 -*-
"""Проверяет, попадал ли .env или похожие секреты в историю Git."""
from __future__ import annotations

import subprocess
import sys


def main() -> int:
    checks = [
        (["git", "log", "--all", "--oneline", "--", ".env"], ".env в истории коммитов"),
        (
            ["git", "log", "-p", "--all", "-S", "sk-", "--", "*.env", ".env"],
            "паттерн OpenAI sk- в истории .env",
        ),
    ]
    issues = 0

    for cmd, label in checks:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        output = (result.stdout or "").strip()
        if output:
            issues += 1
            print(f"[WARN] {label}:")
            print(output[:2000])
            if len(output) > 2000:
                print("... (обрезано)")
            print()

    if issues:
        print(
            "Действия: ротируйте ключи (см. SECURITY.md), "
            "запустите pre-commit, при необходимости — git filter-repo."
        )
        return 1

    print("История Git: явных следов .env / sk- в diff не найдено.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
