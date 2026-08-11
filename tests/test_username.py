from src.usernames import UsernameParser


def test_check_valid_username_local():
    """тест функции check_valid_username_local"""
    assert (
        UsernameParser.check_valid_username_local("usernameл") is False
    )  # Проверка с рускими буквами

    assert (
        UsernameParser.check_valid_username_local("username*") is False
    )  # Проверка на спец симвулы

    assert (
        UsernameParser.check_valid_username_local("u sername") is False
    )  # Провека на пробелы

    assert (
        UsernameParser.check_valid_username_local("1username") is False
    )  # Проверка цифра в начале

    assert (
        UsernameParser.check_valid_username_local("_username") is False
    )  # Проверка есть ли в начале _

    assert (
        UsernameParser.check_valid_username_local("username_") is False
    )  # Проверка есть ли в конце _

    assert (
        UsernameParser.check_valid_username_local("usr") is False
    )  # Проверка если менише 4 симвула

    assert (
        UsernameParser.check_valid_username_local("u" * 33) is False
    )  # Проверка на привышения
    
    assert (
        UsernameParser.check_valid_username_local("username") is True
    )  # Проверка на валидный юзернейм
    
    assert (
        UsernameParser.check_valid_username_local("Username") is True
    )  # Проверка на валидный юзернейм с большой буквы
    
    assert (
        UsernameParser.check_valid_username_local("@username") is True
    )  # Проверка на валидный юзернейм который начинаеться с @
    
    assert (
        UsernameParser.check_valid_username_local("username123") is True
    )  # Проверка на валидный юзернейм который содержит цифры в конце

