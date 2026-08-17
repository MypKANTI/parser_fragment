import pytest

from src.usernames import UsernameParser


@pytest.mark.parametrize(
    "username, status",
    [
        ("usernameл", False),  # Проверка с рускими буквами
        ("username*", False),  # Проверка на спец симвулы
        ("u sername", False),  # Проверка на пробелы
        ("1username", False),  # Проверка цифра в начале
        ("_username", False),  # Проверка есть ли в начале _
        ("username_", False),  # Проверка есть ли в конце _
        ("u" * 33, False),  # Проверка на привышения симвулов
        ("usr", False),  # Проверка если менише 4 симвула
        ("username", True),  # Проверка на валидный юзернейм
        ("Username", True),  # Проверка на валидный юзернейм с большой буквы
        ("UsErNaMe", True),  # test на валидность юз заглавные буквами
        ("@username", True),  # Проверка на валидный юзернейм начинающийся с @
        (
            "username123",
            True
        ),  # Проверка на валидный юзернейм который содержит цифры в конце
    ],
)
def test_check_valid_username_local(username, status):
    """
    тест функции check_valid_username_local

    Args:
        (str) username: юзернейм для тестов
        (bool) status: вернёт True если юзерней соотвествует 
        правилам сотавления юза telegram иначе вернёт False

    """
    assert UsernameParser.check_valid_username_local(username) is status
