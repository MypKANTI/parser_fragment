import logging

from bs4 import BeautifulSoup
from prettytable import PrettyTable

from src.config import Config
from src.utils import (
    ClientParser,
    Colors,
    InfoFullPrint,
    check_input,
    clear_screen,
    generate_headers,
    hendler_error,
    is_object,
    status_color,
)


class NumberParser:
    @staticmethod
    def banner_main_input(clear: bool = True) -> int:
        """
        Главный банер

        Args:
            clear (bool): очищать эран или нет

        Return:
            int: возрашаем ведённое число
        """
        if clear:
            clear_screen()

        print("""
    1. Узнать статус номера +888 (через фрагмент)
    2. Информация о номере +888 (кратко)
    3. Информация о номере +888 (фул)
    """)

        return check_input("Ваш выбор")

    @staticmethod
    @hendler_error
    async def info_numder_short(
        endpoint: str, is_exactly: bool = True
    ) -> None:
        """
        Краткая информация о номере +888 с фрагмента

        Args:
            endpoint (str): каталок для парсинга
            is_exactly (bool): точно отображать TON или
            срезать цефры после запятой. Defaults to True.
        """
        numder = input("плиз номер: ")
        print()
        async with ClientParser.start() as session:
            async with session.get(
                url=f"{Config.URL_BASE}{endpoint}?query={numder}",
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

                        for blok in pars0:
                            numder_ = blok.find(
                                "div", class_="table-cell-value tm-value"
                            )
                            icon_ton = [
                                "table-cell-value",
                                "tm-value",
                                "icon-before",
                                "icon-ton",
                            ]
                            ton = blok.find("div", class_=" ".join(icon_ton))
                            status_avail = [
                                "table-cell-value",
                                "tm-value",
                                "tm-status-avail",
                            ]
                            status = blok.find(
                                "div",
                                class_=" ".join(status_avail),
                            )
                            time = blok.find("div", class_="tm-timer")

                            if status is None:
                                status_unavail = [
                                    "table-cell-value",
                                    "tm-value",
                                    "tm-status-unavail",
                                ]
                                status = blok.find(
                                    "div",
                                    class_=" ".join(status_unavail),
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
                        logging.error(
                            "content-type не текст не могу обработать"
                        )
                else:
                    logging.error("несмог извлечь content-type")

    @staticmethod
    @hendler_error
    async def check_status_number_fragment(number: str, endpoint: str) -> str:
        """
        узнаём статус номера на фрагменте

        Args:
            number (str): номир которого мы хотим узнать статус в фрагменте

        Returns:
            str: статус номера в фрагменте
        """
        async with ClientParser.start() as session:
            async with session.get(
                f"{Config.URL_BASE}{endpoint}?query={number}",
                headers=generate_headers(),
            ) as resp:
                resp.raise_for_status()
                html = await resp.text()

                soup = BeautifulSoup(html, Config.PARSER)
                blok = soup.find("tr", class_="tm-row-selectable")
                status = blok.find(
                    "div", class_="table-cell-value tm-value tm-status-avail"
                )

                if status is None:
                    status = blok.find(
                        "div",
                        class_="table-cell-value tm-value tm-status-unavail",
                    )

                status = (
                    status.text
                    if status is not None
                    else Config.DEFAULT_STATUS
                )

                return status

    @staticmethod
    async def info_numder_full(url: str) -> None:
        """
        Функия для отображения полной информации о номере +888

        используються два вспомогательных класса это GetInfoFull
        он служит для сбора информации и InfoFullPrint служит для
        отображения информации в столбики через PrettyTable

        Args:
            url (str): сылка для парсинга
        """
        async with ClientParser.start() as session:
            async with session.get(
                url=url, headers=generate_headers()
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
                        deal_end_time = info_full_print.deal_end_time()
                        table_fixed = info_full_print.table_fixed()
                        table_0 = info_full_print.table(0)
                        table_1 = info_full_print.table(1)

                        # вывоим информацию
                        # статус
                        if status_and_ is not None:
                            print(status_and_)

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
        user_input = NumberParser.banner_main_input()

        if user_input == 1:
            number = input("Введите номер c (+888) ")
            status_number = await NumberParser.check_status_number_fragment(
                number, endpoint=endpoint
            )
            status_number = status_color(status_number)
            print()
            print(status_number)
            input("\nplease enter: ")
        elif user_input == 2:
            await NumberParser.info_numder_short(endpoint=endpoint)
            input("\nplease enter: ")
        elif user_input == 3:
            endpoint = "number"
            number = input("Введите номер c (+888) ")
            url = f"{Config.URL_BASE}{endpoint}/{number}"
            await NumberParser.info_numder_full(url=url)
            input("\nplease enter: ")
