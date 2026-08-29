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

# определяем полный путь
PATH = os.path.dirname(os.path.abspath(__file__))
PATH_DIR_LOG = os.path.join(PATH, "logs")
PATH_FILE_LOG = os.path.join(PATH, "logs", "parser.log")

# создаём папку если её нету
os.makedirs(PATH_DIR_LOG, exist_ok=True)

logging.basicConfig(
    level=logging.ERROR,  # уровень логирование
    format="%(asctime)s %(levelname)s %(filename)s %(funcName)s %(message)s",
    handlers=[
        logging.FileHandler(filename=PATH_FILE_LOG, encoding="UTF-8"),
        logging.StreamHandler(),
    ],
    force=True,
)  # для логирование настройка


async def main() -> None:
    """
    главная функция выбора типа парсинга ну что парсить
    звёзды, премки, юзы, нфт, номера
    """
    while True:
        print(banner())

        user_input: int = check_input("ваш выбор")

        dict_funcs = {
            1: GiftParser.run,
            2: StarParser.run,
            3: NumberParser.run,
            4: UsernameParser.run,
            5: PremiumParser.run,
        }

        func_name = dict_funcs.get(user_input, None)
        if func_name is not None:
            await func_name()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit, EOFError):
        sys.exit(1)
