# 🔍 Parser Fragment

![Telegram](https://img.shields.io/badge/KANTI-Telegram-blue?logo=telegram&link=https://t.me/Myp_KANTI)
![Python](https://img.shields.io/badge/Python-3.12.6-yellow?logo=python)
![Python3](https://img.shields.io/badge/Python3-3.11.9-yellow?logo=python)

Парсер сайта **[fragment](https://fragment.com/)**

<img onerror="logo fragment" src="https://static47.tgcnt.ru/posts/_0/5d/5db86f8329523286e4ed10ad29d3f467.jpg">

## Доступно для парсинга
Данные которые можем парсить благодаря этому парсеру
- NFT
- Stars
- Numbers
- Username
- Premium

## Особенность
Парсер определет точный статус

Статусы бывают такие:

- Sold<br>
- For sale<br>
- On auction<br>
- Unavailable<br>
- Available<br>
- Taken<br>

## Объяснения статусов

**Sold** - Продано 🤝<br>
**For sale** - На продаже 🛒<br>
**On auction** - На аукционе 🏷️<br>
**Unavailable** - Недоступен 🔴<br>
**Available** - Доступный 🟢<br>
**Taken** - Занят 📅<br>

``Вы сможете занять username если только статус его Unavailable``

На [fragment](https://fragment.com/) статус Unavailable означает, что владелец не выставил имя на торги, но технически оно свободно для назначения цены. Именно этот статус позволяет вам занять юзернейм. Поскольку технически владелец не назначен

## Поддерживает
Проверенно на личном опыте
| platform | status |
|----------|--------|
| Windows  | work ✅|
|  Ubuntu  | work ✅|
|  Termux  | work ✅|

## Требование для запуска
-  *OS*
-  *Python* ---> **version 3.11+**
-  *Установить зависимости с* **requirements.txt**

## install
Универсальная установка программы
```bash
git clone https://github.com/MypKANTI/parser_fragment.git

cd parser_fragment

pip3 install -r requirements.txt

python3 main.py
```

## install через [uv](https://github.com/astral-sh/uv)
Установка через uv (не универсальная)

```pip install uv```


## установка программы
```bash
git clone https://github.com/MypKANTI/parser_fragment.git

cd parser_fragment

uv sync

uv run main.py
```

## О парсере
Программа не использует API она парсит все данные через bs4 написанно одним человеком на python используеться aiohttp и asyncio

## Config.json
Конфигурация вынесена в отдельный файл config.json чтобы не хранить конфиг в коде и можно было быстро заменить не залезая в код

Теперь разберем за что отвечает каждый параметр

**max_concurrent_connections** - это максимальное количество подключений нужно для асинхронности

**limit_per_host** - это почти то же самое что и max_concurrent_connections только limit_per_host это лимит подключений на один хост

**response_timeout_seconds** - это искусственная задержка между запросами чтобы не перегружать сервер (если хатите ускорить генерацию юзов можите поставить задержку например 0.4 или вообще 0.1)

**connection_timeout_seconds** - это время на весь запрос если оно истечет программа выдаст ошибку timeout

**default_status** - если нужные данные не будут найдены напишет это

Теперь разберем что будет если указать неправильное значение или конфига не будет вообще если конфига нет или вы указали неверное значение программа отработает как надо она проигнорирует то что вы ввели и возьмет запланированное значение в коде

```json
{
    "network": {
        "_comment": "данные которые относяться к запросам",
        "max_concurrent_connections": 1,
        "limit_per_host": 1,
        "response_timeout_seconds": 1.6,
        "connection_timeout_seconds": 5
    },
    "visual": {
        "_comment": "визуальное изменение",
        "default_status": "нету"
    }
}
```

## Структура проекта
```bash
parser_fragment
│   .codespellrc
│   .gitignore
│   .pre-commit-config.yaml
│   LICENSE
│   main.py
│   pyproject.toml
│   README.md
│   requirements.txt
│   start.bat
│   uv.lock
│
├───logs
│       parser.log
│
├───src
│   │   config.json
│   │   config.py
│   │   gifts.py
│   │   helper_config.py
│   │   numbers.py
│   │   premiums.py
│   │   stars.py
│   │   usernames.py
│   │   utils.py
│   │   __init__.py
│   │
│   ├───parser_fragment
│   │       __init__.py
│   │
│   └───__pycache__
│
└───tests
        test_gifts.py
        test_username.py
        __init__.py
```

# Хорошего дня тебе дружище :)
