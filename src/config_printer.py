from src.config import Config
from src.utils import is_clear_decorator


class ConfigPrinter:
    @staticmethod
    @is_clear_decorator(True)
    def banner() -> str:
        return f"""
    {"Config":.^50}
        Ссылка парсинга: {Config.URL_BASE}
        Парсер: {Config.PARSER}
        Значение дефолт: {Config.DEFAULT_STATUS}
        Искусственная задержка: {Config.RESPONSE_TIME}
        Таймаут: {Config.TIMEOUT}
        Лимит на один хост: {Config.LIMIT_PER}
        TCP лимит: {Config.TCP_LIMIT}

        Если хотите заменить какое-то значение откройте файл config.json
        но прежде прочитайте в документации что за что отвечает
    {"." * 50}
    """

    @staticmethod
    def run() -> None:
        print(ConfigPrinter.banner())
        input("\nplease enter: ")
