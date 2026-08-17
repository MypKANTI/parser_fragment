import pytest

from src.utils import replace_nft


@pytest.mark.parametrize(
    'nft_name, nft_name_result',
    [
        ('Artisan Bricks', 'artisanbricks'),
        ('Durov’s Caps', 'durovscaps'),
        ('Jacks-in-the-Box', 'jacksinthebox'),
        (' ’-', '')
])
def test_replace_nft(nft_name: str, nft_name_result: str) -> None:
    """
    Функция для тестирование коректности работы replace_nft
    она сравнивает ожидаймый результат с входными данными
    
    Args:
        nft_name (str): тестовое nft название
        nft_name_result (str): ожидаймый результата
    """
    assert replace_nft(nft_name) == nft_name_result
