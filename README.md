# Parser Fragment

данная программа умеет парсить такие данные как

- Username
- NFT
- Start
- Numbers
- Premium

## Install 
```bash
git clone https://github.com/MypKANTI/parser_fragment.git

cd parser_fragment

pip3 install requirements.txt

python3 main.py
```

## если lxml не работает
в таком случае вам нужно **отредактировать** конфиг по пути **src/config.py** *(я с этим столкнулся когда тестировал программу в termux)*
```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    TCP_LIMIT = 1  # лимит TCP соединений
    LIMIT_PER = 1  # лимит TCP на один хост
    RESPONSE_TIME = 1.6  # время между запросами
    PARSER = "lxml"  # парсер для bs4
    CH_BANNER = 30  # количество симвулов в банере
    TIMEOUT = 5  # таймаут
    URL_BASE = "https://fragment.com/"  # сылка её лудше не менять
    DEFAULT_STATUS = "нет"  # статус если не нашёл такойто элемент/данные
```
замените *```PARSER = "lxml"```* на *```PARSER = "html.parser"```*

## если у вас Windows
советую вам установить этот проект не через git а через архив перейдите в нужную папку это **parser_fragment** и там выполните команду ```pip3 install requirements.txt``` и после этого запустите файл **start.bat**

## особенность
этот парсер не просто проверяет занят ли юзер или нет он узнаёт его точный статус такой как продано или на продажу или занят или не занят или активный

## о парсере
я не планирую вести этот проект я считаю его просто проектом для портфолио так что улучшений не будет выложил в открытый доступ поскольку посчитал что этот проект может быть полезен кому-то
