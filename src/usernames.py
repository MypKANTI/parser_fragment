import asyncio
import getpass
import logging
import random
import sys
from itertools import product
from typing import Iterator

from bs4 import BeautifulSoup
from prettytable import PrettyTable

from src.config import Config
from src.numbers import NumberParser
from src.utils import (
    ClientParser,
    Colors,
    check_input,
    clear_screen,
    generate_headers,
    hendler_error,
    is_object,
    status_color,
)


class UsernameParser:
    @staticmethod
    def banner(clear: bool = True) -> str:
        """
        банер для выбора действик

        Args:
            clear (bool) очищать экран или нет

        Return:
            str: банер выбора действий
        """
        if clear:
            clear_screen()

        return """
    1 получить список юзов
    2 проверить юз на аукционе
    3 генератов юзов с проверкой
    4 информация о юзе (фул)
    """

    @staticmethod
    def banner_sort_filter(clear=True) -> str:
        """
        банер для выбора действик

        Args:
            clear (bool) очищать экран или нет

        Return:
            str: банер выбора действий
        """
        if clear:
            clear_screen()

        return """
    1 На аукционе
    2 Продано
    3 На продажу
    """

    @staticmethod
    def banner_sort_sort(clear=True) -> str:
        """
        банер для выбора действик

        Args:
            clear (bool) очищать экран или нет

        Return:
            str: банер выбора действий
        """
        if clear:
            clear_screen()

        return """
    1 Цена от высокой до низкой
    2 Цена от низкой к высокой
    3 Недавно перечисленные
    4 Заканчиваясь в ближайшее
    """

    @staticmethod
    def banner_generate_username(clear=True) -> str:
        """
        бБанер выбора типа генерации юзов

        Args:
            clear (bool) очищать экран или нет

        Return:
            str: банер выбора действий
        """
        if clear:
            clear_screen()

        return """
    1 генерация олгоритм (рандом)
    2 генерация олгоритм (последовательность)
    """

    @staticmethod
    def end_filter(numder: int) -> str:
        """
        выбор типа аукцион продажа или проданное

        шпаргалка
        на аукционе filter=auction
        на продаже filter=sold
        проданное filter=sale

        Args:
            numder (int): номер варианта

        Returns:
            str: возрашаем подходящий эдпоинт
        """

        if numder == 1:
            return "filter=auction"
        elif numder == 2:
            return "filter=sold"
        elif numder == 3:
            return "filter=sale"

    @staticmethod
    def end_sort(numder: int) -> str:
        """
        сортировка  по цене и времени

        шпаргалка
        Цена от высокой до низкой ?sort=price_desc&
        Цена от низкой к высокой ?sort=price_asc&
        Недавно перечисленные ?sort=listed&
        Время окончания ?sort=ending&

        Args:
            numder (int): номер варинта ответа

        Returns:
            str: возрашаем этпоинт сортировки
        """

        if numder == 1:
            return "?sort=price_desc&"
        elif numder == 2:
            return "?sort=price_asc&"
        elif numder == 3:
            return "?sort=listed&"
        elif numder == 4:
            return "?sort=ending&"

    class GenerateUsernames:
        """
        Класс генерации юзов

        Yields:
            str: возращает юзернейм
        """

        @staticmethod
        def random(numder: int, count: int) -> Iterator[str]:
            """
            Генерация юзернейма через рандом

            Args:
                numder (int): количество симвулов в юзе
                count (int): количество юзов сколько надо сгенерировать

            Returns:
                Iterator[str]: генератор выдающий юзернеймы вида @
            """
            try:
                for _ in range(count):
                    username = [
                        random.choice(Config.en_list) for _ in range(numder)
                    ]
                    username = f"@{''.join(username)}"
                    yield username

            except (KeyboardInterrupt, SystemExit, EOFError):
                logging.info("прервал программу | func random")
                sys.exit(1)

        @staticmethod
        def algorithm(generations: int, len_usename: int) -> Iterator[str]:
            """
            Генерация юзернеймов через алгоритм последовательности
            с элементом рандома генерации списка для уникальности

            Args:
                generations (int): количество генераций
                len_usename (int): длина юза без @

            Returns:
                Iterator[str]: генератор выдающий юзернеймы вида @
            """
            try:
                en_list_random = [
                    random.choice(Config.en_list) for _ in range(4)
                ]

                count = 0  # счётчик

                for username in product(en_list_random, repeat=len_usename):
                    count += 1
                    username = "@" + "".join(username)
                    yield username
                    if count == generations:
                        break

            except (KeyboardInterrupt, SystemExit, EOFError):
                logging.info("прервал программу | func algorithm")
                sys.exit(1)

    @staticmethod
    @hendler_error
    async def market_parsing() -> None:
        """парсим главную страницу юзов и выводи результата в таблицах"""
        print(UsernameParser.banner_sort_sort())

        start_link = check_input("")

        print(UsernameParser.banner_sort_filter())

        end_link = check_input("")

        if end_link in [1, 2, 3]:
            end_link = UsernameParser.end_filter(end_link)
            start_link = UsernameParser.end_sort(start_link)
            url = f"{Config.URL_BASE}{start_link}{end_link}"
            async with ClientParser.start() as session:
                async with session.get(
                    url=url, headers=generate_headers()
                ) as resp:
                    resp.raise_for_status()
                    content = (
                        resp.headers.get("content-type", "").strip().lower()
                    )
                    if content:
                        if content.startswith("text/html"):
                            html = await resp.text()
                            soup = BeautifulSoup(html, Config.PARSER)
                            pars0 = soup.find_all(
                                "tr", class_="tm-row-selectable"
                            )

                            table = PrettyTable()

                            for blok in pars0:
                                username = blok.find(
                                    "div", class_="table-cell-value tm-value"
                                ).text  # Получаем юз типа @feds
                                status_avail = [
                                    "table-cell-value",
                                    "tm-value",
                                    "tm-status-avail",
                                ]
                                status = blok.find(
                                    "div",
                                    class_=" ".join(status_avail),
                                )  # Получаем статус например Resale
                                dollar = blok.find(
                                    "div", "table-cell-desc wide-only"
                                )  # получаем стоймость в $ типа 23,665
                                time_data = blok.find(
                                    "div", "tm-timer"
                                )  # Получить время окончание рынк
                                icon_ton = [
                                    "table-cell-value",
                                    "tm-value",
                                    "icon-before",
                                    "icon-ton",
                                ]
                                ton = blok.find(
                                    "div",
                                    class_=" ".join(icon_ton),
                                )

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
                                if status is None:
                                    status = blok.find(
                                        "div", class_="table-cell-status-thin"
                                    )
                                if status is None:
                                    status_taken = [
                                        "table-cell-value",
                                        "tm-value",
                                        "tm-status-taken",
                                    ]
                                    status = blok.find(
                                        "div",
                                        class_=" ".join(status_taken),
                                    )

                                ton = is_object(ton, Colors.BLUE)
                                dollar = is_object(dollar, Colors.GREEN)
                                time_data = is_object(time_data, Colors.YELLOW)

                                status = (
                                    status.text
                                    if status is not None
                                    else "нет"
                                )
                                username = (
                                    Colors.GAY + username + Colors.RESET
                                    if username is not None
                                    else Colors.RED + "нет" + Colors.RESET
                                )

                                table.field_names = [
                                    Colors.GAY + "username" + Colors.RESET,
                                    Colors.GREEN + "status" + Colors.RESET,
                                    Colors.GREEN + "$" + Colors.RESET,
                                    Colors.BLUE + "ton" + Colors.RESET,
                                    Colors.YELLOW + "time-data" + Colors.RESET,
                                ]

                                table.add_row(
                                    [
                                        username,
                                        status_color(status),
                                        dollar,
                                        ton,
                                        time_data,
                                    ]
                                )

                            print(table)
                        else:
                            logging.error(
                                "content-type не текст не могу обработать"
                            )
                    else:
                        logging.error("несмог извлечь content-type")
        else:
            print(f"такой флаг не предусмотрен {end_link}")

    @staticmethod
    @hendler_error
    async def сheck_username_market(username: str, is_exactly: bool) -> None:
        """
        проверка есть ли юз на рынке и также узнаём его статус

        Args:
            username (str): юз для проверки на марките
            is_exactly (bool): точное совпадение или нет
        """
        username = username.lower().strip()

        async with ClientParser.start() as session:
            async with session.get(
                url=f"https://fragment.com/?query={username}",
                headers=generate_headers(),
            ) as resp:
                content = resp.headers.get("content-type", "").strip().lower()
                if content:
                    if content.startswith("text/html"):
                        html = await resp.text()
                        soup = BeautifulSoup(html, Config.PARSER)

                        bloks = soup.find_all("tr", class_="tm-row-selectable")

                        table = PrettyTable()

                        print()

                        for blok in bloks:
                            get_username = blok.find(
                                "div", class_="table-cell-value tm-value"
                            )
                            icon_ton = [
                                "table-cell-value",
                                "tm-value",
                                "icon-before",
                                "icon-ton",
                            ]
                            ton = blok.find(
                                "div",
                                class_=" ".join(icon_ton),
                            )
                            status_avail = [
                                "table-cell-value",
                                "tm-value",
                                "tm-status-avail",
                            ]
                            status = blok.find(
                                "div",
                                class_=" ".join(status_avail),
                            )

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
                            if status is None:
                                status = blok.find(
                                    "div", class_="table-cell-status-thin"
                                )

                            if status is None:
                                status_taken = [
                                    "table-cell-value",
                                    "tm-value",
                                    "tm-status-taken",
                                ]
                                status = blok.find(
                                    "div",
                                    class_=" ".join(status_taken),
                                )

                            username_ = (
                                get_username.text
                                if get_username is not None
                                else Config.DEFAULT_STATUS
                            )
                            ton = (
                                Colors.BLUE + ton.text + Colors.RESET
                                if ton is not None
                                else Colors.RED
                                + Config.DEFAULT_STATUS
                                + Colors.RESET
                            )
                            status = (
                                status.text
                                if status is not None
                                else Config.DEFAULT_STATUS
                            )

                            table.field_names = [
                                Colors.GAY + "username" + Colors.RESET,
                                Colors.BLUE + "ton" + Colors.RESET,
                                Colors.GREEN + "status" + Colors.RESET,
                            ]

                            # точное совпадение
                            if is_exactly:
                                username_ = (
                                    Colors.GAY + username_ + Colors.RESET
                                    if username_.replace("@", "") == username
                                    else Config.DEFAULT_STATUS
                                )

                            table.add_row(
                                [username_, ton, status_color(status)]
                            )

                            # прерывание если решим поиска точный
                            if is_exactly:
                                print(table)
                                input("\nplease enter: ")
                                break

                        print(table)
                    else:
                        logging.error(
                            "content-type не текст не могу обработать"
                        )
                else:
                    logging.error("несмог извлечь content-type")

    @staticmethod
    @hendler_error
    async def is_username_busy(username: str) -> str:
        """
        проверяем занят ли юз и получаем его статус по фрагменту

        Args:
            username (str): юз который мы проверяем статус

        Return:
            status (str): статус юза
        """
        async with ClientParser.start() as session:
            async with session.get(
                url=f"https://fragment.com/?query={username}",
                headers=generate_headers(),
            ) as resp:
                resp.raise_for_status()
                content = resp.headers.get("content-type", "").strip().lower()
                if content:
                    if content.startswith("text/html"):
                        html = await resp.text()
                        soup = BeautifulSoup(html, Config.PARSER)

                        bloks = soup.find_all("tr", class_="tm-row-selectable")

                        for blok in bloks:
                            status_avail = [
                                "table-cell-value",
                                "tm-value",
                                "tm-status-avail",
                            ]
                            status = blok.find(
                                "div",
                                class_=" ".join(status_avail),
                            )

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
                            if status is None:
                                status = blok.find(
                                    "div", class_="table-cell-status-thin"
                                )

                            if status is None:
                                status_taken = [
                                    "table-cell-value",
                                    "tm-value",
                                    "tm-status-taken",
                                ]
                                status = blok.find(
                                    "div",
                                    class_=" ".join(status_taken),
                                )
                            if status is None:
                                status_unavail = [
                                    "tm-section-header-status"
                                    "tm-status-unavail"
                                ]
                                status = blok.find(
                                    "div",
                                    class_=" ".join(status_unavail),
                                )

                            status = (
                                status.text
                                if status is not None
                                else Config.DEFAULT_STATUS
                            )

                            await asyncio.sleep(
                                Config.RESPONSE_TIME
                            )  # искуственная задежка между запросами

                            return status
                    else:
                        logging.error(
                            "content-type не текст не могу обработать"
                        )
                else:
                    logging.error("несмог извлечь content-type")

    @staticmethod
    def check_start_username(username: str) -> None:
        """
        проверяет и изменяет формат с сылки на юз
        username - юз который надо проверить

        Args:
            username (str): юз сылка которорый мы превращаем в юз

        Return:
            username (str): исправленный юз
        """
        if username.startswith("http://t.me/"):
            username = username.replace("http://t.me/", "")
        elif username.startswith("https://t.me/"):
            username = username.replace("https://t.me/", "")
        elif username.startswith("t.me/"):
            username = username.replace("t.me/", "")
        elif username.startswith("@"):
            username = username.replace("@", "")
        return username

    @staticmethod
    def check_valid_username_local(username: str) -> bool:
        """
        Функция для проверки юза по правилам составления юза
        локально без доступа к интеренету

        Args:
            username (str): юз который мы проверяем

        Returns:
            (bool): если юз прощел проверку то вернёт True иначе False
        """
        try:
            username = username.lower().strip()
        except AttributeError:
            logging.warning(f"юз {username} не может быть пустым")
            return False

        # проверка на русские буквы
        if any(r_c in username for r_c in Config.ru_chars):
            logging.info("юз не может содержать русских букв")
            return False

        # проверка на спец симвулы
        if any(s_c in username for s_c in Config.special_chars):
            logging.info("в юзе не может быть с спец симвулов")
            return False

        # проверяем содержет ли юз пробелов
        for i in username:
            if i == " ":
                logging.info("юз не может содержать пробелов")
                return False

        # проверка начинаеться ли юз с цифры
        if username[0].isdigit():
            logging.info("юз не може начинаться с цифры")
            return False

        # проверка конца и начало на содержание "_"
        if username.startswith("_") or username.endswith("_"):
            logging.info('юз не может начинатьс или заканчиваться "_"')
            return False

        # проверка на недостаточную длину
        if len(username) < 4:
            logging.info("юз не может быть короче четырёх симвулов")
            return False

        # проверка на привышение длины
        if len(username) > 32:
            logging.info("длина юза не может привышать 32 симвула")
            return False

        return True

    @staticmethod
    async def get_username(text: str) -> str:
        """
        проверка юза на валидность полная

        Args:
            text (str): текст для пояснение что водить

        Returns:
            str: возращаем юз если он правельный
        """
        while True:
            username = input(f"{text} {getpass.getuser()}: ")
            username = UsernameParser.check_start_username(
                username
            )  # удаляем лишние симвулы типа t.me/
            if UsernameParser.check_valid_username_local(
                username
            ):  # проверяем по правилам составление юза
                return username
            else:
                await asyncio.sleep(0.2)  # искуственная задержка

    async def full_info_username(url: str) -> None:
        """
        функция для получения полной информации
        о юзе создал эту фукцию из-за DRY

        Args:
            url (str): ссылка для парсинга
        """
        await NumberParser.info_numder_full(url)

    @staticmethod
    async def run() -> None:
        """
        Какой тип парсинга юза

        Raises:
            Exception: если не соотвествует длине
            Exception: если не соотвествует длине
        """
        try:
            print(UsernameParser.banner())

            user_input = check_input("")

            if user_input == 1:
                await UsernameParser.market_parsing()  # парсим рынок юзов
                input("\nplease enter: ")
            elif user_input == 2:
                username = await UsernameParser.get_username(text="Введите юз")
                is_exactly = check_input("точное совпадение? 1=Дa/2=Нет")

                if is_exactly <= 1:
                    is_exactly = True
                elif is_exactly >= 2:
                    is_exactly = False

                await UsernameParser.сheck_username_market(
                    username=username, is_exactly=is_exactly
                )  # проверяем есть ли юз на рынке
                input("\nplease enter: ")
            elif user_input == 3:
                print(UsernameParser.banner_generate_username())

                user_input = check_input("ваш выбор")

                if user_input == 1:
                    "Вынести в отдельную функцию"
                    while True:
                        try:
                            numder = check_input(
                                "введите количество симвулов"
                            )  # количество симвулов для генерации
                            if numder < 4 or numder > 32:
                                raise Exception
                            else:
                                break
                        except Exception:
                            print(
                                "число не может быть меньше 4 или больше 32",
                                end="\n\n",
                            )

                    count = check_input("количество генераций")
                    print()
                    for username in UsernameParser.GenerateUsernames.random(
                        numder=numder, count=count
                    ):
                        status = await UsernameParser.is_username_busy(
                            username=username
                        )
                        print(status_color(status), username)
                    input("\nplease enter: ")
                elif user_input == 2:
                    "Вынести в отдельную функцию"
                    while True:
                        try:
                            len_usename = check_input(
                                "введите количество симвулов"
                            )  # количество симвулов для генерации
                            if len_usename < 4 or len_usename > 32:
                                raise Exception
                            else:
                                break
                        except Exception:
                            print(
                                "число не может быть меньше 4 или больше 32",
                                end="\n\n",
                            )

                    generations = check_input("количество генераций ")
                    print()

                    unavailable = 0  # не занятые
                    on_auction = 0  # на аукционе
                    available = 0  # активные (сам хз что значит)
                    for_sale = 0  # продаёться
                    taken = 0  # занятых
                    sold = 0  # проданые
                    other = 0  # не определёные

                    for username in UsernameParser.GenerateUsernames.algorithm(
                        generations, len_usename
                    ):
                        status = await UsernameParser.is_username_busy(
                            username=username
                        )

                        print(status_color(status=status), username)

                        if status == "Unavailable":
                            unavailable += 1
                        elif status == "On auction":
                            on_auction += 1
                        elif status == "Available":
                            available += 1
                        elif status == "For sale":
                            for_sale += 1
                        elif status == "Taken":
                            taken += 1
                        elif status == "Sold":
                            sold += 1
                        else:
                            other += 1

                    print()
                    print(
                        Colors.RED
                        + f"не занятые юзы: {unavailable} | Unavailable"
                        + Colors.RESET
                    )
                    print(
                        Colors.GREEN
                        + f"на аукционе: {on_auction} | On auction"
                        + Colors.RESET
                    )
                    print(
                        Colors.GREEN
                        + f"активных: {available} | Available"
                        + Colors.RESET
                    )
                    print(
                        Colors.GREEN
                        + f"продоёться: {for_sale} | For sale"
                        + Colors.RESET
                    )
                    print(
                        Colors.YELLOW
                        + f"занятых юзов {taken} | taken"
                        + Colors.RESET
                    )
                    print(
                        Colors.RED + f"проданные: {sold} | Sold" + Colors.RESET
                    )
                    print(
                        Colors.RED
                        + f"не определённые: {other} | не определил статус"
                        + Colors.RESET
                    )
                    input("\nplease enter: ")
            elif user_input == 4:
                endpoint = "username"
                username = input("Введите юз: ")
                if UsernameParser.check_valid_username_local(username):
                    url = f"{Config.URL_BASE}{endpoint}/{username}"
                    await UsernameParser.full_info_username(url)
                else:
                    print(Colors.RED + "не похоже на юз" + Colors.RESET)
                input("\nplease enter: ")
        except (KeyboardInterrupt, SystemExit, EOFError):
            sys.exit(1)
