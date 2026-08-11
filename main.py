#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
программа парсер маркета fragment.com
получение и сбора информацию такой как:
UsernameParser
numders
Prеm
NFT
stars

Сори за опечатки я просто двоешник полный пхпхпхпхпх
"""

import asyncio
import logging
import os
import sys

from src.gifts import GiftParser
from src.numbers import NumberParser
from src.premiums import PremiumParser
from src.stars import StarParser
from src.usernames import UsernameParser
from src.utils import banner, check_input

# создаём папку если её нету
os.makedirs('logs', exist_ok=True)

# определяем полный путь
PATH = os.path.dirname(os.path.abspath(__file__))
PATH_FILE_FULL = os.path.join(PATH, 'logs', "parser.log")

logging.basicConfig(
    level=logging.ERROR,  # уровень логирование
    format="| %(asctime)s | %(levelname)s | %(message)s |",
    encoding="UTF-8",  # чтобы не было такого �
    handlers=[
        logging.FileHandler(PATH_FILE_FULL),
        logging.StreamHandler(),
    ],
)  # для логирование настройка


async def main() -> None:
    """
    главная функция выбора типа парсинга ну что парсить
    звёзды, премки, юзы, нфт, номера
    """
    while True:
        print(banner())

        user_input = check_input("ваш выбор")

        if user_input == 1:
            await GiftParser.run()
        elif user_input == 2:
            await StarParser.run()
        elif user_input == 3:
            await NumberParser.run()
        elif user_input == 4:
            await UsernameParser.run()
        elif user_input == 5:
            await PremiumParser.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit, EOFError):
        sys.exit(1)
