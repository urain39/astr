import sys

from configparser import ConfigParser
from pathlib import Path
from .command import execute


def main() -> None:
    argv = sys.argv
    argc = len(argv)

    if argc == 2:
        cfg = ConfigParser()
        cfg.read('astr.ini', encoding='utf-8')

        execute(argv[1], cfg)
    else:
        print(
            f'Usage: {Path(argv[0]).name} <x|extract|i|inject|u|update>\n' +
            '    x, extract   extract strings from source\n' +
            '    i, inject    inject translated strings to source\n' +
            '    u, update    update modified time in database\n' +
            '\n' +
            'NOTE: do NOT use "u, update", if you don\'t understand'
        )


if __name__ == '__main__':
    main()
