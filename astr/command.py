import json

from configparser import ConfigParser
from pathlib import Path
from typing import Dict
from .exceptions import ASTRError
from .dictionary import parse_dictionary
from .extractor import extract as _extract
from .injector import inject as _inject

_CONST_MAIN = 'main'
_CONST_INCLUDE = 'include'
_CONST_ENCODING = 'encoding'
_CONST_DIRECTORY = 'directory'
_CONST_ASTRCACHE = '__astrcache__'
_CONST_STRICT = 'strict'

_STR_TO_BOOL = {'false': False, 'true': True}


def extract(config: ConfigParser) -> None:
    inc = config.get(_CONST_MAIN, _CONST_INCLUDE)
    enc = config.get(_CONST_MAIN, _CONST_ENCODING)
    dir_ = config.get(_CONST_MAIN, _CONST_DIRECTORY)

    work_dir = Path('.')
    extract_dir = work_dir / dir_
    cache_dir = extract_dir / _CONST_ASTRCACHE

    database: Dict[str, float] = {}
    for i in work_dir.glob(inc):
        if i.is_file():
            text = i.read_text(encoding=enc)

            cache_file = cache_dir / (str(i) + '.json')
            text_file = extract_dir / (str(i) + '.txt')

            string_list, tokens = _extract(text)

            # 仅缓存含有字符串的脚本
            if string_list:
                # 注意：这里cache文件可能有父目录
                cache_file.parent.mkdir(parents=True, exist_ok=True)
                cache_file.write_text(json.dumps(tokens), encoding=enc)

                text_file.parent.mkdir(parents=True, exist_ok=True)
                text_file.write_text(
                    '\n\n\n'.join(string_list), encoding=enc
                )

                # 注意：键是源码文件，值是文本文件的修改时间
                database[str(i)] = text_file.stat().st_mtime

                print(f'LOG: Extracted {i}')

    if database:
        database_file = cache_dir / 'database.json'
        database_file.write_text(json.dumps(database), encoding=enc)


def update(config: ConfigParser) -> None:
    enc = config.get(_CONST_MAIN, _CONST_ENCODING)
    dir_ = config.get(_CONST_MAIN, _CONST_DIRECTORY)

    work_dir = Path('.')
    extract_dir = work_dir / dir_
    cache_dir = extract_dir / _CONST_ASTRCACHE

    database_file = cache_dir / 'database.json'
    database: Dict[str, float]
    database = json.loads(database_file.read_text())

    for i in database:
        text_file = extract_dir / (str(i) + '.txt')

        database[i] = text_file.stat().st_mtime

    database_file.write_text(json.dumps(database), encoding=enc)

    print(f'LOG: Updated {database_file}')


def inject(config: ConfigParser) -> None:
    # pylint: disable=too-many-locals
    enc = config.get(_CONST_MAIN, _CONST_ENCODING)
    dir_ = config.get(_CONST_MAIN, _CONST_DIRECTORY)
    strict = _STR_TO_BOOL[config.get(_CONST_MAIN, _CONST_STRICT).lower()]

    work_dir = Path('.')
    extract_dir = work_dir / dir_
    cache_dir = extract_dir / _CONST_ASTRCACHE

    database_file = cache_dir / 'database.json'
    database: Dict[str, float]
    database = json.loads(database_file.read_text())

    need_update = False

    for i, mtime in database.items():
        text_file = extract_dir / (str(i) + '.txt')
        cache_file = cache_dir / (str(i) + '.json')

        if text_file.stat().st_mtime <= mtime:
            continue  # 跳过未更改文件

        text = text_file.read_text(encoding=enc)

        unmatched_list, dictionary = parse_dictionary(text)

        if unmatched_list:
            if strict:
                u = unmatched_list[0]

                raise ASTRError(
                    f'Untranslated string detected at {str(text_file)}:{u[0]}')

            print('WARNING: untranslated string detected!')

            for u in unmatched_list:
                print(f'    unmatched: {str(text_file)}:{u[0]}')

        text = _inject(json.loads(cache_file.read_text()),
                       dictionary, strict=strict)
        Path(i).write_text(text, encoding=enc)
        need_update = True

        print(f'LOG: Injected {i}')

    if need_update:
        update(config)  # 注入后更新数据库


def execute(cmd: str, config: ConfigParser) -> None:
    if cmd in ('x', 'extract'):
        extract(config)
    elif cmd in ('i', 'inject'):
        inject(config)
    elif cmd in ('u', 'update'):
        update(config)
    else:
        print(f'Unsupported command \'{cmd}\'')
