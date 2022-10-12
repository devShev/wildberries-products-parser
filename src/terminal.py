from enum import Enum


class Terminal(str, Enum):
    NORMAL = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[31m'
    GREEN = '\033[32m'

    WARN = f'{RED}{BOLD}[WARNING] {NORMAL}{RED}'
    INFO = f'{GREEN}{BOLD}[INFO] {NORMAL}{GREEN}'
