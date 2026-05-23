# Политика безопасности

## Секреты и `.env`

- Никогда не коммитьте `.env`, ключи API, сертификаты (`.pem`, `.key`).
- Используйте только [`.env.example`](.env.example) с плейсхолдерами.
- Перед `git push` запускайте: `pre-commit run --all-files`

## Ротация ключей (обязательно при утечке)

Файл `.env` **ранее попадал в историю Git** (удалён коммитом `f48e51f`). Если репозиторий когда-либо был публичным или `.env` содержал реальные ключи:

1. **Proxy API:** отзовите старый ключ в [console.proxyapi.ru/keys](https://console.proxyapi.ru/keys) и создайте новый.
2. **OpenAI:** отзовите ключ в [platform.openai.com/api-keys](https://platform.openai.com/api-keys).
3. Обновите локальный `.env` новыми значениями.
4. Не коммитьте `.env` повторно.

Проверка истории локально:

```bash
python scripts/check_git_secrets_history.py
```

## Очистка истории Git (только при подтверждённой утечке)

Если реальные секреты попали в remote, одной ротации ключей может быть недостаточно — нужно удалить секреты из истории:

```bash
# Установите git-filter-repo, затем (ОСТОРОЖНО — переписывает историю):
git filter-repo --path .env --invert-paths
git push --force-with-lease
```

Согласуйте force-push с командой. Подробнее: [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).

## Pre-commit

```bash
pip install pre-commit detect-secrets
pre-commit install
pre-commit run --all-files
```

## Сообщить об уязвимости

Создайте приватный issue или свяжитесь с maintainer репозитория.
