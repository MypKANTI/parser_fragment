import asyncio
import logging

import aiohttp
from bs4 import BeautifulSoup
from prettytable import PrettyTable

from src.config import Config
from src.utils import (
    ClientParser,
    Colors,
    check_input,
    generate_headers,
    hendler_error,
    is_clear_decorator,
    is_object,
)


class StarParser:
    @staticmethod
    @hendler_error
    async def stars_price(
        session: aiohttp.ClientSession,
        endpoint: str,
        explanation: bool = False,
    ) -> None:
        """
        функция парсинга прайса на звёзды с сайта фрагмент

        Args:
            session (aiohttp.ClientSession) это сесия aiohttp
            explanation (bool): включить пояснение?
            это пояснение будет писать после цены
            что это за валюта по дефолту не включено. Defaults to False.
            endpoint (str): это эдпоинт какой отдел сайта парсить
        """

        async with session.get(
            url=f"{Config.URL_BASE}{endpoint}", headers=generate_headers()
        ) as resp:
            resp.raise_for_status()
            content = resp.headers.get("content-type", False).lower().strip()
            if content:
                if content.startswith("text/html"):
                    html = await resp.text()
                    soup = BeautifulSoup(html, Config.PARSER)

                    pars0 = soup.find(
                        "div", class_="tm-form-radio-items"
                    )  # находим нужный блок
                    pars1 = pars0.find_all(
                        "div", class_="tm-form-radio-item-wrap"
                    )  # итерируемся по блоку
                    pars1.pop(-1)  # удаляем лишнее

                    print()

                    table = PrettyTable()  # для создании таблиц

                    for block in pars1:
                        star = block.find(
                            "div", class_="tm-radio-label"
                        )  # Получаем количество звёзд
                        icon_ton = [
                            "tm-radio-desc",
                            "wide-only",
                            "icon-before",
                            "icon-ton",
                        ]
                        ton = block.find(
                            "div",
                            class_=" ".join(icon_ton),
                        )  # Получаем тоны
                        dollar = block.find(
                            "div", class_="tm-value icon-before icon-usd"
                        )

                        if star is not None:
                            star = star.text
                            star = star.split()[0].strip()
                            star = Colors.YELLOW + star + Colors.RESET
                        else:
                            star = (
                                Colors.RED
                                + Config.DEFAULT_STATUS
                                + Colors.RESET
                            )

                        ton = is_object(ton, Colors.BLUE)
                        dollar = is_object(dollar, Colors.GREEN)

                        table.field_names = [
                            Colors.YELLOW + "Star" + Colors.RESET,
                            Colors.BLUE + "TON" + Colors.RESET,
                            Colors.GREEN + "$" + Colors.RESET,
                        ]

                        if explanation:
                            if star:
                                star = f"{star} Star"
                            if ton:
                                ton = f"{ton} TON"

                        table.add_row([star, ton, dollar])

                    print(table)
                else:
                    logging.error(
                        f"не могу работать с Content-type: {content}"
                    )
            else:
                logging.error("не смог найти Content-type")

    @staticmethod
    @is_clear_decorator(True)
    def banner_main_input() -> int:
        """
        Главный банер выбора из типа звёзд

        Return
            (int): число ведённое пользователем
        """
        print("""
        1 Звезды Telegram цены
        2 Звезды цены на розыгрыш
        """)

        return check_input("ваш выбор")

    @staticmethod
    async def run() -> None:
        endpoint = "stars"
        user_input: int = StarParser.banner_main_input()

        try:
            async with ClientParser.start() as session:
                if user_input <= 1:
                    endpoint = f"{endpoint}/buy"
                elif user_input >= 2:
                    endpoint = f"{endpoint}/giveaway"
                logging.debug(f"использую эдпоинт {endpoint}")
                await StarParser.stars_price(session, endpoint)
                input("\nplease enter: ")
        except asyncio.exceptions.CancelledError:
            logging.warning("соединение было разорвано")
            return
