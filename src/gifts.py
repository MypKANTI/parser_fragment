import sys

from bs4 import BeautifulSoup
from prettytable import PrettyTable

from src.config import Config
from src.utils import (
    ClientParser,
    Colors,
    generate_headers,
    hendler_error,
    replace_nft,
    status_color,
)


class GiftParser:
    @staticmethod
    async def parsing_market(url: str) -> None:
        """
        парсим рынок gift/NFT

        выводи такие данные как
        name nft
        num nft (#)
        time data
        price ton
        status nft

        Args:
            url (str): link парсинга
        """
        async with ClientParser.start() as session:
            async with session.get(
                url=url, headers=generate_headers()
            ) as resp:
                resp.raise_for_status()
                html = await resp.text()
                soup = BeautifulSoup(html, Config.PARSER)

                # переходим по пути
                main = soup.find("main", class_="tm-main tm-main-catalog")
                div_wrap = main.find("div", class_="tm-main-catalog-wrap")
                div_content = div_wrap.find(
                    "div", class_="tm-main-catalog-content"
                )
                section_results = div_content.find(
                    "section", class_="tm-section clearfix js-search-results"
                )
                div_autoscrollable = section_results.find(
                    "div", class_="tm-catalog-grid-wrap js-autoscrollable"
                )
                div_body = div_autoscrollable.find(
                    "div", class_="tm-catalog-grid js-autoscroll-body"
                )

                # получаем список NFT
                gifts = div_body.find_all("a", class_="tm-grid-item")

                table = PrettyTable()

                # бежим по gifts
                for gifts in gifts:
                    div_content = gifts.find(
                        "div", class_="tm-grid-item-content"
                    )

                    # парсим блок name and num
                    num_name = div_content.find(
                        "div", class_="tm-grid-item-name wide-only"
                    )
                    span_name = num_name.find(
                        "span", class_="item-name"
                    )  # пример Artisan Brick
                    span_num = num_name.find(
                        "span", class_="item-num"
                    )  # пример  #2178

                    # парсим дату
                    data = div_content.find(
                        "div", class_="tm-grid-item-desc wide-only"
                    )
                    time_data = data.find(
                        "time", class_="short"
                    )  # Jul 24, 2025 at 21:43

                    # парсим статус и цену в ton
                    ton_status = div_content.find(
                        "div", class_="tm-grid-item-values"
                    )
                    # вынес иза привышение 79 симвулов
                    t = "tm-grid-item-value tm-value icon-before icon-ton"
                    div_ton = ton_status.find(
                        "div",
                        class_=t,
                    )  # 30,000
                    div_status = ton_status.find(
                        "div", class_="tm-grid-item-status tm-status-unavail"
                    )  # Sold
                    # проверка на avail статус
                    if div_status is None:
                        div_status = ton_status.find(
                            "div", class_="tm-grid-item-status tm-status-avail"
                        )

                    # поправляем формат
                    if span_name is not None:
                        span_name = span_name.text  # name NFT

                    if span_num is not None:
                        span_num = span_num.text  # NFT num

                    if time_data is not None:
                        time_data = time_data.text  # Дата и время

                    if div_ton is not None:
                        div_ton = div_ton.text  # цена в TON

                    # получаем статусы типа sold, for sale, on auc
                    if div_status is not None:
                        div_status = div_status.text

                    # создаём заголовок таблицы
                    table.field_names = [
                        Colors.GAY + "NFT" + Colors.RESET,
                        Colors.YELLOW + "Number" + Colors.RESET,
                        Colors.BLUE + "TON" + Colors.RESET,
                        Colors.GREEN + "Status" + Colors.RESET,
                    ]

                    table.add_row(
                        [
                            Colors.GAY + span_name + Colors.RESET,
                            Colors.YELLOW + span_num + Colors.RESET,
                            Colors.BLUE + div_ton + Colors.RESET,
                            status_color(div_status),
                        ]
                    )

                print(table)

    @staticmethod
    @hendler_error
    async def get_list_gifts(url: str, count: bool = False) -> None:
        """
        Функция для вывода списка
        Gift/NFT с выбором что парсить

        Args:
            url (str): ссылку на ресурс для парсинга
            count (bool) показывать ли количество
        """
        async with ClientParser.start() as session:
            async with session.get(
                url=url, headers=generate_headers()
            ) as resp:
                resp.raise_for_status()
                html = await resp.text()
                soup = BeautifulSoup(html, Config.PARSER)
                tm_main = soup.find("div", class_="tm-main-filters-list")
                gifts_list = tm_main.find_all("a")

                dict_gift = {}  # славарь для gift

                for e, gift in enumerate(gifts_list, start=1):
                    name_gift = gift.find(
                        "div", class_="tm-main-filters-name"
                    )  # получаем имя gift
                    count_gift = gift.find(
                        "div", class_="tm-main-filters-count"
                    )  # получаем количество gift

                    name_gift = (
                        name_gift.text
                        if name_gift is not None
                        else Config.DEFAULT_STATUS
                    )
                    count_gift = (
                        count_gift.text
                        if count_gift is not None
                        else Config.DEFAULT_STATUS
                    )

                    dict_gift[e] = gift[
                        "href"
                    ]  # получаем сылку перенаправления

                    if count:
                        print(f"{e:03} {name_gift} | count: {count_gift}")
                    else:
                        print(f"{e:03} {name_gift}")

                while True:
                    try:
                        user_input = int(input("\nваш выбор: "))
                        break
                    except (KeyboardInterrupt, SystemExit, EOFError):
                        print("пока ещё встретимся ;)")
                        sys.exit(1)
                    except Exception:
                        print("хм это не похоже на число")

                nft_name = dict_gift.get(user_input, Config.DEFAULT_STATUS)

                if nft_name != Config.DEFAULT_STATUS:
                    url = (
                        f"{url.replace('/gifts/', '')}{replace_nft(nft_name)}"
                    )
                    await GiftParser.parsing_market(url)

    @staticmethod
    async def run() -> None:
        """
        Главная функция запускa
        парсинга NFT/gift
        """
        url = "https://fragment.com/gifts/"
        print("\nПарсинг Gifts...", end="\n\n")
        # получаем список NFT/gift
        await GiftParser.get_list_gifts(url)
        input("\nplease enter: ")
