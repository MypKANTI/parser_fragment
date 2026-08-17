from bs4 import BeautifulSoup
from prettytable import PrettyTable

from src.config import Config
from src.utils import (
    ClintParser,
    Colors,
    check_input,
    clear_screen,
    generate_headers,
    hendler_error,
    is_object,
)


class StarParser:
    @staticmethod
    @hendler_error
    async def stars_price(endpoint: str, explanation: bool = False) -> None:
        """
        функция по парсингу цен на звёзды через фрагмент

        Args:
            explanation (bool): включить пояснение?. Defaults to False.
        """
        async with ClintParser.start() as session:
            async with session.get(
                url=f"{Config.URL_BASE}{endpoint}", headers=generate_headers()
            ) as resp:
                resp.raise_for_status()
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

                for blok in pars1:
                    star = blok.find(
                        "div", class_="tm-radio-label"
                    )  # Получаем количество звёзд
                    ton = blok.find(
                        "div",
                        class_="tm-radio-desc wide-only icon-before icon-ton",
                    )  # Получаем тоны
                    dollor = blok.find(
                        "div", class_="tm-value icon-before icon-usd"
                    )

                    if star is not None:
                        star = star.text
                        star = star.split()[0].strip()
                        star = Colors.YELLOW + star + Colors.RESET
                    else:
                        star = (
                            Colors.RED + Config.DEFAULT_STATUS + Colors.RESET
                        )

                    ton = is_object(ton, Colors.BLUE)
                    dollor = is_object(dollor, Colors.GREEN)

                    table.field_names = [
                        Colors.YELLOW + "StarParser" + Colors.RESET,
                        Colors.BLUE + "TON" + Colors.RESET,
                        Colors.GREEN + "$" + Colors.RESET,
                    ]

                    if explanation:
                        if star:
                            star = f"{star} StarParser"
                        if ton:
                            ton = f"{ton} TON"

                    table.add_row([star, ton, dollor])

                print(table)

    @staticmethod
    def banner_main_input(clear: bool = True) -> int:
        """
        Главный банер выбора из типа звёзд

        Args:
            clear (bool): очищать экран или нет

        Return
            (int): число ведённое пользователем
        """
        if clear:
            clear_screen()

        print("""
        1 Звезды Telegram цены
        2 Звезды цены на розыгрыш
        """)

        return check_input("ваш выбор")

    @staticmethod
    async def run() -> None:
        endpoint = "stars"
        user_input = StarParser.banner_main_input()

        if user_input == 1:
            endpoint = f"{endpoint}/buy"
            await StarParser.stars_price(endpoint)
            input("\nplease enter: ")
        elif user_input == 2:
            endpoint = f"{endpoint}/giveaway"
            await StarParser.stars_price(endpoint)
            input("\nplease enter: ")
