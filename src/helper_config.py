"""
Файл для помощи конфигу в обработке данных
работает как посредним межды config.json и
сonfig.py (описание написал спокльку мне
кажеться что не очевидно делать helper_config.py)

фукция get_parser() получает подходящий парсер
не пренимает никаких аргументов

декоратор  check_except() вернёт переданное значение
при любом исключение пренимает аргумент запосное значение

декоратор validate_type проверяет значение по его типу данных
если тип данных не совпал то вызывает исключение TypeError и
тогда обрабатываться декоратор check_except() который вернёт
резервное запланированое значение

класс ConfigGetJson нужен для работы с фалом .json он читает его
и выводит данные по значению и типу которые находяться в файле .json

ConfigGetJson. _read_file() читаем файл и возращаем это в формате json

ConfigGetJson.Get нужно для получения интересующих нас данных
"""

import functools
import json
import logging
import os

PATH = os.path.dirname(os.path.abspath(__file__))
PATH_FILE_JSON = os.path.join(PATH, "config.json")


def get_parser() -> str:
    """
    Функция для определения парсера
    если lxml установлен используем его
    иначе используем html.parser

    Returns:
        str: парсер подходящий
    """
    try:
        PARSER = "lxml"
        __import__(PARSER)
    except (ImportError, ModuleNotFoundError):
        PARSER = "html.parser"
    return PARSER


def check_except(DEFAULT: int | float | str | bool):
    """
    Декаратор для вывода конфига
    если файла нету или прозишла ошибка
    работает так если произойдёт люое исключение вернёт
    DEFAULT

    Args:
        DEFAULT (Any): пренимает
        float, str, int, bool
        эти данные он вернёт если произошла ошибка
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.warning(f"ошибка при обработке файла .json {e}")
                return DEFAULT

        return wrapper

    return decorator


def validate_type(type: int | float | str | bool):
    """
    декоратор для определения типа обьекта

    Args:
        type (_type_): пренимает такие значение
        str, float, int, bool
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(result, type):
                return result
            else:
                raise TypeError("не подходящий формат")

        return wrapper

    return decorator


class ConfigGetJson:
    """класс для работы с .json"""

    @staticmethod
    def _read_file() -> dict:
        """
        функция чтения и возращение данных как словарь

        Returns:
            str: вернёт всё в формате json
        """
        with open(PATH_FILE_JSON, "r", encoding="UTF-8") as file:
            return json.load(file)

    class Get:
        """
        Кдасс для возращение данных из файла .json
        """

        @staticmethod
        @check_except(1)
        @validate_type(int)
        def tcp_limit(
            type: str = "network", meaning: str = "max_concurrent_connections"
        ) -> int:
            return ConfigGetJson._read_file()[type][meaning]

        @staticmethod
        @check_except(1)
        @validate_type(int)
        def limit_per(
            type: str = "network", meaning: str = "limit_per_host"
        ) -> int:
            return ConfigGetJson._read_file()[type][meaning]

        @staticmethod
        @check_except(1.6)
        @validate_type(float)
        def response_time(
            type: str = "network", meaning: str = "response_timeout_seconds"
        ) -> float:
            return ConfigGetJson._read_file()[type][meaning]

        @staticmethod
        @check_except(5)
        @validate_type(int)
        def timeout(
            type: str = "network", meaning: str = "connection_timeout_seconds"
        ) -> int:
            return ConfigGetJson._read_file()[type][meaning]

        @staticmethod
        @check_except("нет")
        @validate_type(str)
        def default_status(
            type: str = "visual", meaning: str = "default_status"
        ) -> str:
            return ConfigGetJson._read_file()[type][meaning]
