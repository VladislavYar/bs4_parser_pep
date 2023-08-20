from enum import Enum
from pathlib import Path

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
ENCODING = 'utf-8'
PARSER_LIBRARY = 'lxml'
MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_TABLE_INFO_URL = 'https://peps.python.org/'
BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}

# Регулярное выражение, определяющая в строках версии и статусу Python.
REGULAR_PYTHON_VERSION_STATUS = (r'Python (?P<version>\d\.\d+) '
                                 r'\((?P<status>.*)\)')

# Определяет документ в нужном формате по ссылке в href.
REGULAR_PYTHON_DOC = r'.+pdf-a4\.zip$'


class OuputType(str, Enum):
    """Определяет варианты вывода данных."""
    PRETTY = 'pretty'
    FILE = 'file'


class HTMLTag(str, Enum):
    """Определяет теги HTML."""
    TBODY = 'tbody'
    SECTION = 'section'
    TR = 'tr'
    A = 'a'
    ABBR = 'abbr'
    DT = 'dt'
    DD = 'dd'
    DIV = 'div'
    LI = 'li'
    H1 = 'h1'
    DL = 'dl'
    UL = 'ul'
    TABLE = 'table'
