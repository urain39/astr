import sys

from configparser import ConfigParser
from .command import execute


if __name__ == '__main__':
    argv = sys.argv
    argc = len(argv)

    if argc == 2:
        cfg = ConfigParser()
        cfg.read('astr.ini', encoding='utf-8')

        execute(sys.argv[1], cfg)
    else:
        print(
            'Usage: python -m astr <x|extract|i|inject|u|update>\n' + \
            '    x, extract   extract strings from source\n' + \
            '    i, inject    inject translated strings to source\n' + \
            '    u, update    update translated strings mtime in database'
        )
