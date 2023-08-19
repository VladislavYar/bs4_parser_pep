import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL,
                       PEP_TABLE_INFO_URL)
from outputs import control_output
from utils import find_tag, get_response


def _output_mismatches_log(non_matching_statuses: list) -> None:
    """Выводит в лог сообщение с несовпадающими статусами."""
    message_log = ''
    if not non_matching_statuses:
        return
    for non_matching_status in non_matching_statuses:
        message_log += ('Несовпадающие статусы:\n'
                        f'{non_matching_status["url_detail"]}\n'
                        'Статус в карточке: '
                        f'{non_matching_status["status_detail"]}\n'
                        'Ожидаемые статусы: '
                        f'{non_matching_status["status_table"]}\n')
    logging.info(message_log)


def _forms_result_pep(count_status: dict) -> list:
    """Формирует данные по парсинку PEP для вывода."""
    results = [('Статус', 'Количество')]
    total = 0
    for status, count in count_status.items():
        results.append((status, count))
        total += count
    results.append(('Total', total))
    return results


def pep(session: requests_cache.CachedSession) -> list:
    """Парсит статусы PEP."""
    response = get_response(session, PEP_TABLE_INFO_URL)
    if response is None:
        return
    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.text, features='lxml')
    section_pep_table = find_tag(soup, 'section',
                                 attrs={'id': 'numerical-index'})
    tbody_pep_table = find_tag(section_pep_table, 'tbody')
    tr_tags_pep_table = tbody_pep_table.find_all('tr')

    non_matching_statuses = []
    count_status = {'Active': 0, 'Accepted': 0,
                    'Deferred': 0, 'Final': 0,
                    'Provisional': 0, 'Rejected': 0,
                    'Superseded': 0, 'Withdrawn': 0,
                    'Draft': 0, 'Active': 0, }
    for tr_tag_pep_table in tqdm(tr_tags_pep_table):
        a_tag_pep_table = find_tag(tr_tag_pep_table, 'a', attrs={'class':
                                   'pep reference internal'})
        status_code = find_tag(tr_tag_pep_table, 'abbr').text[1:]
        status_table = EXPECTED_STATUS.get(status_code)
        url_pep_detail = urljoin(PEP_TABLE_INFO_URL,
                                 a_tag_pep_table.get('href'))

        response = get_response(session, url_pep_detail)
        if response is None:
            return
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, features='lxml')
        dt_tags_pep_detail = soup.find_all('dt', {'class': 'field-even'})
        for dt_tag_pep_detail in dt_tags_pep_detail:
            is_status = dt_tag_pep_detail.find(string='Status')
            if is_status is None:
                continue
            dd_tag_pep_detail = dt_tag_pep_detail.find_next_sibling(
                'dd', {'class': 'field-even'}
                )
            status = dd_tag_pep_detail.text

            if status in status_table:
                count_status[status] += 1
                continue
            non_matching_statuses.append(
                {'status_detail': status,
                    'status_table': status_table,
                    'url_detail': url_pep_detail}
                )

    _output_mismatches_log(non_matching_statuses)
    return _forms_result_pep(count_status)


def whats_new(session: requests_cache.CachedSession) -> list:
    """
    Парсит автора, заголовок и ссылку на статью
    в разделах 'What’s New in Python'
    """
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div',
                           attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all('li',
                                              attrs={'class': 'toctree-l1'})

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag.get('href')
        version_link = urljoin(whats_new_url, href)
        response = session.get(version_link)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))
    return results


def latest_versions(session: requests_cache.CachedSession) -> list:
    """Парсит ссылки на документацию, версии и статусы Python."""
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    sidebar = find_tag(soup, 'div', attrs={'class':
                                           'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all(name='ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        result = re.search(pattern, a_tag.text)
        link = a_tag.get('href')
        if result:
            version = result.group('version')
            status = result.group('status')
        else:
            version = a_tag.text
            status = ''

        results.append((link, version, status))
    return results


def download(session: requests_cache.CachedSession) -> None:
    """Ищет ссылку для скачивания документации и качает её."""
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')

    table = find_tag(soup, 'table', attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(table, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag.get('href')
    archive_url = urljoin(downloads_url, pdf_a4_link)

    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main() -> None:
    """Главная фукция."""
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode

    results = MODE_TO_FUNCTION.get(parser_mode)(session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
