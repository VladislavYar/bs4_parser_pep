import logging

from bs4 import BeautifulSoup
from requests import RequestException
from requests_cache import CachedSession
from requests_cache.models.response import OriginalResponse

from constants import ENCODING
from exceptions import ParserFindTagException


def get_response(session: CachedSession, url: str) -> OriginalResponse:
    """Делает запрос к странице."""
    try:
        response = session.get(url)
        response.encoding = ENCODING
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )


def find_tag(soup: BeautifulSoup,
             tag: str, attrs: dict = None) -> BeautifulSoup:
    """Ищет тег HTML, в случае отсутсвия выдаёт исключение."""
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag
