# [PARS-DIARY](https://t.me/pars_diary_bot)

Проект для упрощения жизни школьников.

Бот запущен и вы можете пользоваться им здесь:
[@pars_diary_bot](https://t.me/pars_diary_bot)

## Установка / Installation

1. Клонируем репозиторий:

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

**Запускаем:**

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

``` bash
python -m pars_diary
```

</details>

## Перевод
Бот может работать на нескольких языках.

Чтобы добавить перевод на др


## Поддержка / Contribute

Если вам понравился проект, можете отметить репозиторий звёздочкой.

При возникновении проблем/вопросов можете обращаться в issue.

Также вы можете сделать форк проекта со своими улучшениями.
