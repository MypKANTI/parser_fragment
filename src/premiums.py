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


class PremiumParser:
    @staticmethod
    @is_clear_decorator(True)
    def banner_main_input() -> int:
        """
        банер и проверка вода с возрашение результата

        Return:
            int: возрашаем ведённое число
        """
        print("""
    1 Telegram Премиум цены
    2 Премиум-раздачи цены
    """)

        return check_input("ваш выбор")

    @staticmethod
    @hendler_error
    async def telegram_premium_price(
        session: aiohttp.ClientSession, endpoint: str
    ) -> None:
        """
        получаем прайс и прочию информацию о тг премиум

        Args:
            session (aiohttp.ClientSession): сесия aiohttp

        """
        async with session.get(
            url=f"{Config.URL_BASE}premium/{endpoint}",
            headers=generate_headers(),
        ) as resp:
            content = resp.headers.get("content-type", "").lower().strip()
            if content:
                if content.startswith("text/html"):
                    resp.raise_for_status()
                    html = await resp.text()
                    soup = BeautifulSoup(html, Config.PARSER)

                    blocks = soup.find_all("div", class_="tm-form-radio-label")

                    table = PrettyTable()  # для создании таблиц

                    for block in blocks:
                        ton = block.find(
                            "div", class_="tm-value icon-before icon-ton"
                        )
                        dollar = block.find("div", class_="tm-radio-desc")
                        subscription_time = block.find(
                            "div", class_="tm-radio-label"
                        )

                        ton = is_object(ton, Colors.BLUE)
                        dollar = is_object(dollar, Colors.GREEN)

                        subscription_time = (
                            subscription_time.text
                            if subscription_time is not None
                            else Config.DEFAULT_STATUS
                        )

                        if subscription_time:
                            subscription_time_split = subscription_time.split(
                                "-"
                            )
                            if len(subscription_time_split) == 2:
                                subscription_time, discount = (
                                    subscription_time_split
                                )
                                subscription_time = (
                                    Colors.YELLOW
                                    + subscription_time
                                    + Colors.RESET
                                )
                                discount = (
                                    Colors.GREEN + discount + Colors.RESET
                                )
                        else:
                            subscription_time = (
                                Colors.RED + subscription_time + Colors.RESET
                            )
                            discount = (
                                Colors.RED
                                + Config.DEFAULT_STATUS
                                + Colors.RESET
                            )

                        table.field_names = [
                            Colors.YELLOW + "время подписки" + Colors.RESET,
                            Colors.GREEN + "скидка %" + Colors.RESET,
                            Colors.BLUE + "ton" + Colors.RESET,
                            Colors.GREEN + "$" + Colors.RESET,
                        ]

                        table.add_row(
                            [subscription_time, discount, ton, dollar]
                        )

                    print(table)
                else:
                    logging.error(
                        f"не могу работать с Content-type: {content}"
                    )
            else:
                logging.error("не смог найти Content-type")

    @staticmethod
    async def run(endpoint=None) -> None:
        """запуск выбора парсинга премки"""
        print("Парсинг premium...")

        user_input = PremiumParser.banner_main_input()

        async with ClientParser.start() as sessions:
            dict_funcs = {
                1: (PremiumParser.telegram_premium_price, "gift"),
                2: (PremiumParser.telegram_premium_price, "giveaway"),
            }

            func_name = dict_funcs.get(user_input, None)

            if func_name is not None:
                endpoint: str = func_name[1]
                await func_name[0](sessions, endpoint)
        input("\nplease enter: ")
