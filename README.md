# Pars diary (Telegram bot)

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
![GitHub Repo stars](https://img.shields.io/github/stars/iamlostshe/pars-diary)

Проект для упрощения жизни школьников.
Позволяет просматривать информацию из школьного дневника.

**Основные функции**:
- Автоматические уведомления об изменениях.
- Просмотр текущих и итоговых оценок.
- Совместимость с Bars API.

> Бот запущен и вы можете пользоваться им здесь:
[@pars_diary_bot](https://t.me/pars_diary_bot?start=from_github_repo)

## Установка / Installation
Для того чтобы запустить бота локально.

1. Клонируем репозиторий.

``` bash
git clone https://github.com/iamlostshe/PARS-DIARY
cd PARS-DIARY
```

2. копируем `.env.dist` в `.env` и заполняем поля.

3. **Устанавливаем зависимости** и запускаем бота:

<details>
<summary>Через uv (рекомендуется)</summary>

**Устанавливаем `uv` (если еще не установлен):**

Linux:

``` bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows:

``` bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```


**Устанавливаем зависимости**:

``` bash
uv sync
```

**Компилируем перевод**:

```bash
uv run pybabel compile -d locales -D messages
```

**Запускаем бота**:

```bash
uv run python -m pars_diary
```

</details>

<details>
<summary>Через venv + `requirements.txt`</summary>

**Создаём виртуальное окружение**:

``` bash
python -m venv .venv
```

**Активируем виртуальное окружение**:

``` bash
. .venv/bin/activate
```

> Последняя команда для Windows:
>
> ``` bash
> .venv\Scripts\activate
> ```

**Устанавливаем зависимости**:

``` bash
pip install -r requirements.txt
```

**Компилируем перевод**:

```bash
pybabel compile -d locales -D messages
```

**Запускаем бота**:

```bash
pip install -r requirements.txt
```
</details>

Для последующего запуска повторите шаги *активация виртуального окружения*
(только для venv) и *запуск бота*.


## Перевод / Translate

Бот может работать на нескольких языках.

> Здесь будут примеры команд для `uv`.
> В случае `venv`, просто убираем `uv run` из команды.

Для начала извлекаем все переводимые строки:

```sh
uv run pybabel extract --input-dirs=. -o locales/messages.pot
```

Теперь, добавляем перевод для нужного языка. Например Русского (`ru`):

```sh
uv run pybabel init -i locales/messages.pot -d locales -D messages -l ru
```

Открываем файл `locales/ru/LC_MESSAGES/messages.po` и начинаем переводить
все строки.

Ну и наконец, компилируем полученный перевод:

## Поддержка / Contribute

Если вам понравился проект, можете отметить репозиторий звёздочкой.

При возникновении проблем/вопросов можете обращаться в issue.

Также вы можете сделать форк проекта со своими улучшениями.
