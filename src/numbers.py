import logging

import aiohttp
from bs4 import BeautifulSoup
from prettytable import PrettyTable

from src.config import Config
from src.utils import (
    ClientParser,
    Colors,
    HTMLClasses,
    InfoFullPrint,
    check_input,
    generate_headers,
    hendler_error,
    is_clear_decorator,
    is_object,
    status_color,
)


class NumberParser:
    """
    staticmethod класс для работы с номирами +888
    """

    @staticmethod
    @is_clear_decorator(True)
    def banner_main_input() -> int:
        """
        Главный банер

        Return:
            int: возрашаем ведённое число
        """
        print("""
    1. Узнать статус номера +888 (через фрагмент)
    2. Информация о номере +888 (кратко)
    3. Информация о номере +888 (фул)
    """)

        return check_input("Ваш выбор")

    @staticmethod
    @hendler_error
    async def info_numder_short(
        session: aiohttp.ClientSession,
        number: str,
        endpoint: str,
        is_exactly: bool = True,
    ) -> None:
        """
        Краткая информация о номере +888 с фрагмента

        Args:
            session (aiohttp.ClientSession): сессия aiohttp
            endpoint (str): каталок для парсинга
            is_exactly (bool): точно отображать TON или
            срезать цефры после запятой. Defaults to True.
        """

        async with session.get(
            url=f"{Config.URL_BASE}{endpoint}?query={number}",
            headers=generate_headers(),
        ) as resp:
            resp.raise_for_status()
            content = resp.headers.get("content-type", "").strip().lower()
            if content:
                if content.startswith("text/html"):
                    html = await resp.text()
                    soup = BeautifulSoup(html, Config.PARSER)
                    pars0 = soup.find_all("tr", class_="tm-row-selectable")

                    table = PrettyTable()  # для создании таблиц

                    for block in pars0:
                        numder_ = block.find(
                            "div", class_="table-cell-value tm-value"
                        )
                        ton = block.find("div", class_=HTMLClasses.icon_ton())
                        status = block.find(
                            "div",
                            class_=HTMLClasses.status_avail(),
                        )
                        time = block.find("div", class_="tm-timer")

                        if status is None:
                            status = block.find(
                                "div",
                                class_=HTMLClasses.status_unavail(),
                            )

                        numder_ = is_object(numder_, Colors.GAY)
                        ton = is_object(ton, Colors.BLUE)
                        time = is_object(time, Colors.YELLOW)

                        status = (
                            status.text
                            if status is not None
                            else Config.DEFAULT_STATUS
                        )

                        if not is_exactly and ton:
                            ton = ton.split(",")[0]

                        table.field_names = [
                            Colors.GAY + "Numder" + Colors.RESET,
                            Colors.BLUE + "Ton" + Colors.RESET,
                            Colors.GREEN + "Status" + Colors.RESET,
                            Colors.YELLOW + "Time-Data" + Colors.RESET,
                        ]

                        table.add_row(
                            [numder_, ton, status_color(status), time]
                        )

                    print(table)
                else:
                    logging.error("content-type не текст не могу обработать")
            else:
                logging.error("несмог извлечь content-type")

    @staticmethod
    @hendler_error
    async def check_status_number_fragment(
        session: aiohttp.ClientSession, number: str, endpoint: str
    ) -> str:
        """
        узнаём статус номера на фрагменте

        Args:
            session (aiohttp.ClientSession): сессия aiohttp
            endpoint (str): эдпоинт для url
            number (str): номир которого мы хотим узнать статус в фрагменте

        Returns:
            str: статус номера в фрагменте
        """
        async with session.get(
            f"{Config.URL_BASE}{endpoint}?query={number}",
            headers=generate_headers(),
        ) as resp:
            resp.raise_for_status()
            html = await resp.text()

            soup = BeautifulSoup(html, Config.PARSER)
            block = soup.find("tr", class_="tm-row-selectable")
            status = block.find("div", class_=HTMLClasses.status_avail())

            if status is None:
                status = block.find(
                    "div",
                    class_=HTMLClasses.status_unavail(),
                )

            status = (
                status.text if status is not None else Config.DEFAULT_STATUS
            )

            return status

    @staticmethod
    async def info_numder_full(
        session: aiohttp.ClientSession, number: str, endpoint: str
    ) -> None:
        """
        Функия для отображения полной информации о номере +888

        используються два вспомогательных класса это GetInfoFull
        он служит для сбора информации и InfoFullPrint служит для
        отображения информации в столбики через PrettyTable

        Args:
            url (str): сылка для парсинга
        """
        async with session.get(
            url=f"{Config.URL_BASE}{endpoint}/{number}",
            headers=generate_headers(),
        ) as resp:
            resp.raise_for_status()
            content = resp.headers.get("content-type", "").strip().lower()
            if content:
                if content.startswith("text/html"):
                    html = await resp.text()
                    soup = BeautifulSoup(html, Config.PARSER)
                    info_full_print = InfoFullPrint(soup)

                    # получаем таблицы
                    status_and_ = info_full_print.status_and_()
                    tm_bid_info_text = info_full_print.tm_bid_info_text()
                    deal_end_time = info_full_print.deal_end_time()
                    table_fixed = info_full_print.table_fixed()
                    table_0 = info_full_print.table(0)
                    table_1 = info_full_print.table(1)

                    # вывоим информацию
                    # статус
                    if status_and_ is not None:
                        print(status_and_)

                    if tm_bid_info_text is not None:
                        print(tm_bid_info_text)

                    # время до конца аукциона
                    if deal_end_time is not None:
                        print(deal_end_time)

                    if table_fixed is not None:
                        print(table_fixed)

                    if table_0 is not None:
                        print(table_0)

                    if table_1 is not None:
                        print(table_1)
                else:
                    logging.error(
                        f"не могу работать с Content-type: {content}"
                    )
            else:
                logging.error("не смог найти Content-type")

    @staticmethod
    async def run() -> None:
        endpoint = "numbers"
        user_input: int = NumberParser.banner_main_input()

        async with ClientParser.start() as session:
            if user_input in (1, 2, 3):
                number: str = input("Введите номер c (+888) ")

            if user_input == 1:
                status_number = (
                    await NumberParser.check_status_number_fragment(
                        session, number, endpoint=endpoint
                    )
                )
                status_number: str = status_color(status_number)
                print(f"\n{status_number}")
            elif user_input == 2:
                await NumberParser.info_numder_short(
                    session, number, endpoint=endpoint
                )
            elif user_input == 3:
                endpoint = "number"
                await NumberParser.info_numder_full(
                    session, number, endpoint=endpoint
                )
            input("\nplease enter: ")
