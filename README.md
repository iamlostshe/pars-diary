# PARS-DIARY

Проект для упрощения жизни школьников.

### Установка / Installation

1. **Клонируем репозиторий:**

``` bash
git clone https://github.com/iamlostshe/PARS-DIARY
```

2. **Переходим в дирректорию с проектом:**

``` bash
cd PARS-DIARY
```

3. **Заполняем поля в `.env.dist` и переименовываем его в `.env`**

4. **Устанавливаем зависимости и запускаем бота:**

<details>
<summary>
Через poetry (рекомендуется)
</summary>

**Устанавливаем `poetry` (если еще не установлен):**

Linux:

``` bash
curl -sSL https://install.python-poetry.org | python3 -
```

Windows:

``` bash
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

**Устанавливаем зависимости:**

``` bash
poetry install
```

**Запускаем бота:**

``` bash
poetry run python3 -m bot
```

</details>

<details>
<summary>
Через `requirements.txt`
</summary>

**Создаём виртуальное окружение:**

``` bash
python3 -m venv venv
```

**Активируем виртуальное окружение:**

``` bash
. venv/bin/activate
```

> Последняя команда для Windows:
>
> ``` bash
> venv\Scripts\activate
> ```

**Устанавливаем зависимости:**

``` bash
pip3 install -r requirements.txt
```

**Запускаем бота:**

``` bash
python3 bot.py
```

</details>
