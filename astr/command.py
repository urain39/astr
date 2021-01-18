import sys
import json

from configparser import ConfigParser
from pathlib import Path
from typing import List, cast
from .anotations import Token, DefineToken
from .extractor import extract as _extract
from .injector import inject as _inject, parseDictionary

_CONST_MAIN = 'main'
_CONST_INCLUDE = 'include'
_CONST_ENCODING = 'encoding'
_CONST_DIRECTORY = 'directory'
_CONST_ASTRCACHE = '__astrcache__'


def extract(config: ConfigParser) -> None:
    inc = config.get(_CONST_MAIN, _CONST_INCLUDE)
    enc = config.get(_CONST_MAIN, _CONST_ENCODING)
    dir = config.get(_CONST_MAIN, _CONST_DIRECTORY)

    work_dir = Path('.')
    extract_dir = work_dir / dir
    cache_dir = extract_dir / _CONST_ASTRCACHE

    database: List[str] = []
    for i in work_dir.glob(inc):
        if i.is_file():
            text = i.read_text(encoding=enc)

            cache_file = cache_dir / (str(i) + '.json')
            # 注意：这里cache文件可能有父目录
            cache_file.parent.mkdir(parents=True, exist_ok=True)

            stringList, tokens = _extract(text)

            # 仅缓存含有字符串的脚本
            if stringList:
                cache_file.write_text(json.dumps(tokens), encoding=enc)

                text_file = extract_dir / (str(i) + '.txt')
                text_file.parent.mkdir(parents=True, exist_ok=True)
                text_file.write_text(
                    # 排序后方便翻译
                    '\n\n\n'.join(sorted(stringList)), encoding=enc
                )

                database.append(str(i))

    database_file = extract_dir / 'database.json'
    database_file.write_text(json.dumps(database))

def inject(config: ConfigParser) -> None:
    inc = config.get(_CONST_MAIN, _CONST_INCLUDE)
    enc = config.get(_CONST_MAIN, _CONST_ENCODING)
    dir = config.get(_CONST_MAIN, _CONST_DIRECTORY)

    work_dir = Path('.')
    extract_dir = work_dir / dir
    cache_dir = extract_dir / _CONST_ASTRCACHE

    database_file = extract_dir / 'database.json'
    database = json.loads(database_file.read_text())

    for i in database:
        text_file = extract_dir / (str(i) + '.txt')
        text = text_file.read_text(encoding=enc)

        unmatchedList, dictionary = parseDictionary(text)

        if unmatchedList:
            print('WARNING: untranslated string detected!')
            
            for t in unmatchedList:
                print(f'    unmatched: {t}')

        cache_file = cache_dir / (str(i) + '.json')

        text = _inject(json.loads(cache_file.read_text()), dictionary)
        Path(i).write_text(text, encoding=enc)


def execute(cmd: str, config: ConfigParser) -> None:
    if cmd in ('extract', 'x'):
        extract(config)
    elif cmd in ('inject', 'i'):
        inject(config)
    else:
        print(
            f'Unsupported command \'{cmd}\'\n' + \
            '\n' + \
            'Usage:\n' + \
            '    astr <x|i|extract|inject>'
        )
