# [PARS-DIARY](https://t.me/pars_diary_bot)

Проект для упрощения жизни школьников.

Бот запущен и вы можете пользоваться им здесь:

https://t.me/pars_diary_bot

### Установка / Installation

1. **Клонируем репозиторий:**

``` bash
git clone https://github.com/iamlostshe/PARS-DIARY
cd PARS-DIARY
```

2. **Заполняем поля в `.env.dist` и переименовываем его в `.env`**

3. **Устанавливаем зависимости и запускаем бота:**

<details>
<summary>
Через uv (рекомендуется)
</summary>

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
uv run -m pars_diary
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
python3 -m pars_diary
```

</details>
