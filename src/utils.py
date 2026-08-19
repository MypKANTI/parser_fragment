import asyncio
import functools
import getpass
import logging
import os
import random
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Callable, List

import aiohttp
from bs4 import BeautifulSoup
from faker import Faker
from prettytable import PrettyTable

from src.config import Config


@dataclass(frozen=True)
class Colors:
    """Палитра цветов для текста"""

    RED = "\033[31m"  # красный
    GREEN = "\033[32m"  # зелёный
    BLUE = "\033[34m"  # синий
    YELLOW = "\033[33m"  # жёлтый
    RESET = "\033[39m"  # сброс цвета
    GAY = "\033[38;5;39m"  # послание для читатилей


def generate_headers() -> dict:
    """
    функция для генерации headers

    генерирует
    Accept
    User-Agent

    Returns:
        dict: вернёт headers
    """
    fake = Faker()  # для генерации юзерагентов

    random_accept = random.choice(
        ["*/*", "text/html, */*;q=0.8", "text/plain, */*;q=0.9"]
    )
    headers = {
        "Accept": random_accept,
        "User-Agent": fake.user_agent(),
    }

    return headers


def clear_screen() -> None:
    """Очистка экрана в незовисимости от ОС"""
    # os.system('cls' if os.name == 'nt' else 'clear')
    subprocess.run("cls" if os.name == "nt" else "clear", shell=True)


def banner(clear: bool = True) -> str:
    """
    главный банер выбора что именно парсить

    Args:
        clear (bool):
    """
    if clear:
        clear_screen()

    return f"""
Я инструмент для парсинга фрагмента
готов помочь тебе в парсинге

+{'=' * Config.CH_BANNER}+
|{'        1 >>> gifts'}           |
|{'        2 >>> Stars'}           |
|{'        3 >>> Numders'}         |
|{'        4 >>> Username'}        |
|{'        5 >>> Premium'}         |
+{'=' * Config.CH_BANNER}+

пожалуйста выбирите что парсить
"""


def check_input(text: str) -> int:
    """Проверка правильности видёного числа пользователем

    Args:
        text (str): допалнительные текст для понимание что водишь

    Returns:
        int: если чесло правильное возращаем его
    """

    text = text.strip()

    while True:
        try:
            user_input = int(input(f"{text} {getpass.getuser()}: "))
            return user_input
        except ValueError:
            logging.info("потльзователь вёл не число | func check_input")
            print(
                "хм это не похоже на число попробуй ещё раз дружище :)",
                end="\n\n",
            )
            time.sleep(1.5)
        except (KeyboardInterrupt, SystemExit, EOFError):
            logging.info(
                "пользователь прервал работу программы | func check_input"
            )
            print("\nну ладно пока жду твоего возращение ;)")
            sys.exit(1)


def replace_nft(text: str) -> str:
    """
    Функция для удаления лишних симвулом таких как ( -’)

    Args:
        text (str): строка для проверки

    Return:
        text (str): вернёт исправленую строку
    """
    return text.lower().strip().translate(str.maketrans("", "", " -’"))


def status_color(status: str) -> str:
    """
    перекрашиваем статус в зависимости от его статуса
    пример Unavailable это крассный On auction это
    зелённый Taken это жёлтый
    привязанно к классу Colors

    Args:
        status (str): статус юза

    Returns:
        str: вернёт тоже статус но с перекрашеным
        цветом взависимости от статуса
    """

    if status == "Unavailable":
        return Colors.RED + "Unavailable" + Colors.RESET
    elif status == "On auction":
        return Colors.GREEN + "On auction" + Colors.RESET
    elif status == "Available":
        return Colors.GREEN + "Available" + Colors.RESET
    elif status == "For sale":
        return Colors.GREEN + "For sale" + Colors.RESET
    elif status == "Taken":
        return Colors.YELLOW + "Taken" + Colors.RESET
    elif status == "Sold":
        return Colors.RED + "Sold" + Colors.RESET
    elif status == "Resale":
        return Colors.BLUE + "Resale" + Colors.RESET
    elif status == Config.DEFAULT_STATUS:
        return Colors.RED + f"{Config.DEFAULT_STATUS}" + Colors.RESET
    else:
        return "other"


def hendler_error(func):
    """
    Декоратор обработка ошибок для избежание дублирование кода

    Args:
        func (_type_): пренимаем функцию

    Returns:
        _type_: вернёт None (заглушка временная)
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except aiohttp.ClientResponseError as e:
            logging.error(f"{e.message, e.status}")
            return e
        except aiohttp.ContentTypeError as e:
            logging.error(f"{e}")
            return e
        except aiohttp.ClientHttpProxyError as e:
            logging.error(f"{e}")
            return e
        except aiohttp.ClientConnectorSSLError as e:
            logging.error(f"{e}")
            return e
        except aiohttp.ClientConnectionError as e:
            logging.error(f"{e}")
            return e
        except aiohttp.ServerDisconnectedError as e:
            logging.error(f"{e}")
            return e
        except ConnectionResetError as e:
            logging.error(e)      
            return e
        except aiohttp.ClientError as e:
            logging.error(f"{e}")
            return e
        except asyncio.TimeoutError as e:
            logging.error(f"{e}")
            return e
        except IndexError as e:
            logging.error(f"IndexError: {e}")
            return e
        except AttributeError as e:
            logging.error(f"AttributeError: {e}")
            return e
        except (KeyboardInterrupt, SystemExit, EOFError):
            logging.info("KeyboardInterrupt")
            return None
        except Exception as e:
            logging.error(f"{e}")
            return e

    return wrapper


def is_object(object: str, color: Callable) -> str:
    """
    Проверяем обект если он не None значит он что-то содержит
    если всё же None то вернёт деволтный статус из конфига

    Args:
        object: (None | Any): обект который проверяем на None
        color: (Class): Обект класса цветов например Colors.RED

    Return:
        воращаем обект с цветным выводом если он None
        то значение берём из Config
    """
    if object is not None:
        return color + object.text + Colors.RESET
    else:
        return Colors.RED + Config.DEFAULT_STATUS + Colors.RESET


class ClientParser:
    @staticmethod
    def _timeout() -> aiohttp.ClientTimeout:
        """настройка ClientTimeout"""
        return aiohttp.ClientTimeout(
            total=Config.TIMEOUT, connect=Config.TIMEOUT
        )

    @staticmethod
    def _connector() -> aiohttp.TCPConnector:
        """Настройка TCPConnector"""
        return aiohttp.TCPConnector(
            limit=Config.TCP_LIMIT, limit_per_host=Config.LIMIT_PER
        )

    @staticmethod
    def start() -> aiohttp.ClientSession:
        """
        создание нового aiohttp клиента
        с настроенными параметрами
        TCPConnector и ClientTimeout
        """
        return aiohttp.ClientSession(
            connector=ClientParser._connector(), timeout=ClientParser._timeout()
        )


class GetInfoFull:
    """
    Класс для сбора информации с странифы
    через платформу fragmet.com (парсинг html)

    работает в двух режимах парсинг номеров +888
    илиже парсинг юзов полный сбор информации
    """

    def __init__(self, soup: BeautifulSoup):
        self.soup: BeautifulSoup = soup

    def get_head_status(self) -> list[str, str]:
        """
        получаем заголовок в фрагменте а точнее номер и статус или юз и статус

        Returns:
            list[str, str]: номер и статус или юз и статус
        """
        # переходим по пути до нужных заголовков
        section = self.soup.find(
            "section", class_="tm-section tm-auction-section"
        )
        try:
            div = section.find("div", class_="tm-section-header")
        except AttributeError:
            return []
        h2 = div.find("h2", class_="tm-section-header-text")

        # парсим интересующие нас заголовки
        number_or_username = h2.find(
            "span", class_="tm-section-header-domain"
        )  # получаем номер например +888 0000 1312 или юз
        status = h2.find(
            "span", class_="tm-section-header-status tm-status-avail"
        )  # получаем статус например On auction

        # если не нащёл tm-status-avail то пробуе найти класс tm-status-unavail
        if status is None:
            status = h2.find(
                "span", class_="tm-section-header-status tm-status-unavail"
            )

        # форматируем текс под удобный формат
        number_or_username = (
            number_or_username.text
            if number_or_username is not None
            else Config.DEFAULT_STATUS
        )
        status = status.text if status is not None else Config.DEFAULT_STATUS

        return [status, number_or_username]

    def table_fixed_head(self) -> List:
        """
        Получаемзаголовок таблицы fixed
        чтобы знать сколько таблиц создавать для гибкости

        Returns:
            list: название таблиц fixed
        """
        # переходим по нужному пути
        try:
            main_ = self.soup.find("main", class_="tm-main js-main-content")
            section = main_.find(
                "section", class_="tm-section tm-auction-section"
            )
            div = section.find(
                "div", class_="tm-section-box tm-section-bid-info"
            )
        except AttributeError:
            return []
        table = div.find("table", class_="table tm-table tm-table-fixed")
        thead = table.find("thead")
        tr = thead.find("tr")

        # парсим интересующие нас элементы
        highest_bid = tr.find("th", style="--width:37%")  # Highest Bid
        bid_step = tr.find("th", style="--width:28%")  # Bid Step
        minimum_bid = tr.find("th", style="--width:35%")  # Minimum Bid

        # проверяем какие элементы есть и смотря какие есть такие записываем
        if minimum_bid is not None:
            if highest_bid is not None:
                if bid_step is not None:
                    return [highest_bid.text, bid_step.text, minimum_bid.text]
                else:
                    return [highest_bid.text, minimum_bid.text]
            else:
                minimum_bid = tr.find_all("th")[
                    0
                ]  # Minimum Bid если не нашли --width:35%

                owner = tr.find_all("th")[1]

                if owner is not None and minimum_bid is not None:
                    return [minimum_bid.text, owner.text]

                return [minimum_bid.text]
        else:
            minimum_bid = tr.find("th")

            if minimum_bid is not None:
                return [minimum_bid.text]
            return []

    def table_fixed_price(self) -> List:
        """
        Получаем прайс

        Returns:
            (list): список из цен
        """
        # переходим по нужному пути
        main_content = self.soup.find("main", class_="tm-main js-main-content")
        try:
            section = main_content.find(
                "section", class_="tm-section tm-auction-section"
            )

            div = section.find(
                "div", class_="tm-section-box tm-section-bid-info"
            )
        except AttributeError:
            return []
        try:
            table = div.find("table", class_="table tm-table tm-table-fixed")
            tbody = table.find("tbody")
            td = tbody.find_all("td")
        except AttributeError:
            return None

        price_list = []  # весь прайс в список

        for i in td:
            div_table_cell = i.find(
                "div", class_="table-cell table-cell-oneline table-cell-wide"
            )  # если этот блок есть логика парсинга меняеться

            if div_table_cell is not None:
                # получаем интересующие нас элементы
                ton = div_table_cell.find(
                    "div",
                    class_="table-cell-value tm-value icon-before icon-ton",
                )
                dollor = div_table_cell.find("div", class_="table-cell-desc")
                wallet = div_table_cell.find("a", class_="tm-wallet")

                # выводим только то что есть
                if ton is not None:
                    if dollor is not None:
                        return [ton.text, dollor.text.split("$")[-1]]
                    return [ton.text]
                return []

            else:
                # переходим по пути до элемента
                table_cell = i.find("div", class_="table-cell")

                # парсим нужные элементы
                ton = table_cell.find(
                    "div",
                    class_="table-cell-value tm-value icon-before icon-ton",
                )  # получаем цену в крипте
                dollor = table_cell.find(
                    "div", class_="table-cell-desc"
                )  # получаем цену в доларах
                wallet = table_cell.find(
                    "a", class_="tm-wallet"
                )  # получаем адрес крипто кошелька

                # сортеруем и удобно выводим
                if ton is not None:
                    if dollor is not None:
                        price_list.append(f"TON {ton.text}")
                        price_list.append(f"${dollor.text.split('$')[-1]}")
                    else:
                        price_list.append(ton.text)

                # проверяем есть ли адрес крипто кошелька
                if wallet is not None:
                    price_list.append(wallet["href"].split("/")[-1])

        return price_list

    def deal_end_time(self) -> List:
        """
        Ввывод актуального времени окончание аукциона на номер +888

        Returns:
            str: строка в которой юудет написанно точнее время окончание ставок
        """
        # переходим по нужному пути
        tm_main = self.soup.find("main", class_="tm-main js-main-content")
        try:
            tm_section = tm_main.find(
                "section", class_="tm-section tm-auction-section"
            )
            # вынес отдельно изза длины более 79 симвулов получаеться
            tm_box = "tm-section-box tm-section-countdown-wrap js-timer-wrap"
            div_box = tm_section.find(
                "div",
                class_=tm_box,
            )
            div_countdown = div_box.find("div", class_="tm-section-countdown")
        except AttributeError:
            return None
        tm_countdown = div_countdown.find("time", class_="tm-countdown-timer")
        reels = tm_countdown.find_all("span", class_="reel")

        list_time_end = []  # Список в котором будет время аукциона

        for reels in reels:
            timer_d = reels.find("b", class_="digit timer-d")  # дни

            # часы
            timer_h0 = reels.find("b", class_="digit timer-h0")
            timer_h1 = reels.find("b", class_="digit timer-h1")

            # миныты
            timer_m0 = reels.find("b", class_="digit timer-m0")
            timer_m1 = reels.find("b", class_="digit timer-m1")

            # секунды
            timer_s0 = reels.find("b", class_="digit timer-s0")
            timer_s1 = reels.find("b", class_="digit timer-s1")

            # если есть день то записываем его
            if timer_d is not None:
                list_time_end.append(timer_d["data-val"])

            # если есть часы то записываем
            if timer_h0 is not None:
                if timer_h1 is not None:
                    list_time_end.append(
                        f"{timer_h0['data-val']}{timer_h1['data-val']}"
                    )

            # добавляем минуты если они есть
            if timer_m0 is not None:
                if timer_m1 is not None:
                    list_time_end.append(
                        f"{timer_m0['data-val']}{timer_m1['data-val']}"
                    )

            # добавляем секунды
            if timer_s0 is not None:
                if timer_s1 is not None:
                    list_time_end.append(
                        f"{timer_s0['data-val']}{timer_s1['data-val']}"
                    )

        if list_time_end:
            return list_time_end

    def table_head(self, index_table: int) -> List:
        """
        получаем заголовок таблици Bid History

        Args:
            index_table (int): индекс таблици
            он может быть 0 или  1

        Returns:
            list[str, str, str]: возращаем заголовки
        """
        # переходи по пути до интересующих нас блоков
        tm_main = self.soup.find("main", class_="tm-main js-main-content")
        try:
            tm_section = tm_main.find_all(
                "section", class_="tm-section clearfix"
            )[index_table]
        except IndexError:
            return None
        except AttributeError:
            return None
        tm_table = tm_section.find("div", class_="tm-table-wrap")
        table_tm = tm_table.find(
            "table", class_="table tm-table tm-table-fixed"
        )
        thead = table_tm.find("thead")
        tr = thead.find("tr")
        ths = tr.find_all("th")

        list_bid_history = []  # список для заголвков таблици

        for th in ths:
            list_bid_history.append(th.text)

        return list_bid_history

    def table_price(self, index_table: int) -> List:
        """
        Получаем весь прайс в таблицы bid history

        Args:
            index_table (int): индекс таблици
            он может быть 0 или  1

        Returns:
            List: список со всем содержимом таблицы
        """
        # идём по пути ищем элементы которые нас интересуют
        tm_main = self.soup.find("main", class_="tm-main js-main-content")
        try:
            tm_section = tm_main.find_all(
                "section", class_="tm-section clearfix"
            )[index_table]
        except IndexError:
            return None
        except AttributeError:
            return None
        div_wrap = tm_section.find("div", class_="tm-table-wrap")
        table_fixed = div_wrap.find(
            "table", class_="table tm-table tm-table-fixed"
        )
        tbody = table_fixed.find("tbody")
        trs = tbody.find_all("tr")

        price_list = []  # список со всем содержимым таблицы

        for tr in trs:
            tds = tr.find_all("td")
            for td in tds:
                table_cell = td.find("div", class_="table-cell")
                ton = table_cell.find(
                    "div",
                    class_="table-cell-value tm-value icon-before icon-ton",
                )  # получаем TON

                div_tm_value = table_cell.find(
                    "div", class_="table-cell-value tm-value"
                )  # для получение Transferred

                time_ = table_cell.find("time")  # Время

                tm_wallet = table_cell.find(
                    "a", class_="tm-wallet"
                )  # получаем адрес крипто кошелька

                if ton is not None:
                    price_list.append(ton.text)
                else:
                    if div_tm_value is not None:
                        price_list.append(div_tm_value.text)

                if time_ is not None:
                    price_list.append(time_.text)

                if tm_wallet is not None:
                    price_list.append(tm_wallet["href"].split("/")[-1])

        return price_list


class InfoFullPrint:
    """
    класс для удобного отображение иформации в таблицах
    связанно с классом GetInfoFull
    """

    def __init__(self, soup):
        self.soup: BeautifulSoup = soup

    def table_fixed(
        self,
        count=None,
        bid_history_price_line1=None,
        bid_history_price_line2=None,
    ) -> None:
        """
        Функция для удобного отображение данных
        отоброзит заголовки и сому таблицу

        Args:
            index_table (int): индекс таблици
            он может быть 0 или  1
            count (_type_, optional): счётчи. Defaults to None.
            bid_history_price_1 (None): список первой строки таблици.
            Defaults None.
            bid_history_price_2 (None): список второй строки таблици.
            Defaults None.
        """
        table = PrettyTable()  # иницализация таблиц
        info_full = GetInfoFull(self.soup)  # иницализация фул парсинга

        table_fixed_head: list = (
            info_full.table_fixed_head()
        )  # заголовки таблици table fixed

        # получаем весь прайс (table_fixed) в формате списка
        bid_history_price: List = info_full.table_fixed_price()

        # счётчик
        if count is None:
            count = 0

        # список для кажного первого элемента
        if bid_history_price_line1 is None:
            bid_history_price_line1 = []

        # список для каждого второго элемента
        if bid_history_price_line2 is None:
            bid_history_price_line2 = []

        # пишем гаголовок если он есть
        if len(table_fixed_head) > 0:
            table.field_names = [*table_fixed_head]

            # алгоритм для форматирование списка в удобный формат
            if bid_history_price is not None:
                if len(bid_history_price) > 2:
                    for i in bid_history_price:
                        count += 1  # счётчик
                        result = count / 2
                        result = str(result)  # превращаем int в str для split

                        # если есть в конце % значит знак $ не нужен
                        if i.endswith("%"):
                            i = i.replace("$", "")

                        # проверяем чётное или не чётное через костыль
                        if result.split(".")[-1] == "5":
                            bid_history_price_line1.append(
                                i
                            )  # если не делиться на 2
                        else:
                            bid_history_price_line2.append(
                                i
                            )  # если делитьсяна 2

                    # пише таблишу если в ней 3 элемента
                    if len(bid_history_price_line1) == 3:
                        table.add_row([*bid_history_price_line1])  # линия 1

                        # пише таблишу если в ней 3 элемента
                        if len(bid_history_price_line2) == 3:
                            table.add_row(
                                [*bid_history_price_line2]
                            )  # линия 2
                    else:
                        # пишем прайс
                        for i in bid_history_price:
                            table.add_row([i])
                else:
                    try:
                        if len(bid_history_price) >= 2:
                            bid_history_price[0] = (
                                f"TON {bid_history_price[0]}"
                            )
                            bid_history_price[1] = f"${bid_history_price[1]}"
                            for i in bid_history_price:
                                table.add_row([i])
                    except ValueError as e:
                        # эта ошибка евляеться нормальной
                        logging.warning(e)

    def deal_end_time(self, bloks: bool = True) -> PrettyTable:
        """
        функция для отображение времени в столбиках (таблицах)
        есть два вида меняеться он через измениния bloks на другой статус bool

        Args:
            bloks (bool): делить ли время на блоки или
            вывести в одном блоке. Defaults to True.
        """
        # иницализация
        table = PrettyTable()
        info_full = GetInfoFull(self.soup)

        # получаем и форматируем время
        deal_end_time: List = info_full.deal_end_time()

        if deal_end_time is not None:
            if bloks:
                head_table = ["days", "hour", "minutes", "seconds"]

                if len(deal_end_time) == len(head_table):
                    # заголовок таблиц
                    table.field_names = [*head_table]
                    # таблица
                    table.add_row([*deal_end_time])
            else:
                deal_end_time = ":".join(
                    deal_end_time
                ).strip()  # форматируем в удобный формат

                table.field_names = ["data-time"]  # заголовок
                table.add_row([deal_end_time])  # таблица

        if deal_end_time:
            return table

    def status_and_(self) -> PrettyTable:
        """
        Функция для удобного отображение статуса и
        ещё либо номера либо юза в столбике
        """
        table = PrettyTable()  # иницализация таблиц
        info_full = GetInfoFull(self.soup)  # иницализация фул парсинга

        status_and_: List[str, str] = (
            info_full.get_head_status()
        )  # получаем статус и ...
        # ВНИМАНИЕ
        # переменная может содердать список в котором
        # статус и юз или статус и номер
        status_and_: List[str, str]
        try:
            status = status_and_[0].strip()
            date = status_and_[1].strip()
        except IndexError:
            return []

        table_head = ["status"]  # заголовки таблы

        # определяем это номер или юз и по смыслу добавляем заголовок
        if date.startswith("+888") or date.startswith("888"):
            table_head.append("numder")
        else:
            table_head.append("username")

        table.field_names = [*table_head]
        table.add_row([status, date])

        return table

    def table(self, index_table: int) -> PrettyTable:
        """
        Функция для отображение таблици

        Args:
            index_table (int): индекс таблици
            он может быть 0 или  1
        """
        table = PrettyTable()  # иницализация таблиц
        info_full = GetInfoFull(self.soup)  # иницализация фул парсинга

        table_head: List[str, str, str] = info_full.table_head(index_table)
        table_price: List = info_full.table_price(index_table)
        count = 0  # Счётчик
        # Список по три эемента
        list_line_3 = []  # ['Transfer', 2025:00', 'EQC1gUr']

        if table_head is not None:
            table.field_names = [*table_head]

            for t_p in table_price:
                count += 1
                list_line_3.append(t_p)
                if count == 3:
                    count = 0
                    table.add_row(list_line_3)
                    list_line_3 = []
                    continue

            return table
