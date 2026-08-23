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

## О парсере
Программа не использует API она парсит все данные через bs4 написанно одним человеком на python используеться aiohttp и asyncio

## Структура проекта
```bash
parser_fragment
├───logs
│   └───parser.log
├───src
│   ├───__init__.py
│   ├───config.py
│   ├───gifts.py
│   ├───numbers.py
│   ├───premiums.py
│   ├───stars.py
│   ├───usernames.py
│   └───utils.py
├───tests
│   ├───__init__.py
│   ├───test_username.py
│   └───test_utils.py
├───.codespellrc
├───.gitignore
├───.pre-commit-config.yaml
├───LICENSE
├───main.py
├───README.md
├───requirements.txt
└───start.bat
```

# Хорошего дня тебе дружище :)
