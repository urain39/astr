import sys
import json

from configparser import ConfigParser
from pathlib import Path
from typing import List, cast
from .anotations import Token, DefineToken
from .extractor import extract as _extract, TYPE_DEFINE, TYPE_REFERENCE, TYPE_OTHERS
from .injector import inject as _inject

_CONST_EXTRACT = 'extract'
_CONST_TRANSLATE = 'translate'
_CONST_INCLUDE = 'include'
_CONST_ENCODING = 'encoding'
_CONST_DIRECTORY = 'directory'
_CONST_ASTRCACHE = '__astrcache__'


def extract(config: ConfigParser) -> None:
    inc = config.get(_CONST_EXTRACT, _CONST_INCLUDE)
    enc = config.get(_CONST_EXTRACT, _CONST_ENCODING)
    dir = config.get(_CONST_EXTRACT, _CONST_DIRECTORY)

    work_dir = Path('.')
    extract_dir = work_dir / dir
    cache_dir = extract_dir / _CONST_ASTRCACHE

    cache: List[Token]
    cache_file: Path
    token: Token
    for i in work_dir.glob(inc):
        if i.is_file():
            text = i.read_text(encoding=enc)

            cache_file = (cache_dir / (i.name + '.json'))
            # 注意：这里cache文件可能有父目录
            cache_file.parent.mkdir(parents=True, exist_ok=True)

            cache = _extract(text)

            # 仅缓存含有字符串的脚本
            if cache:
                token = cache[0]

                if token[0] == TYPE_DEFINE:
                    token = cast(DefineToken, token)

                    cache_file.write_text(json.dumps(cache), encoding='utf-8')

                    (extract_dir / (i.name + '.txt')).write_text(
                        # 排序后方便翻译
                        '\n\n\n'.join(sorted(token[1])), encoding='utf-8'
                    )


def inject(config: ConfigParser) -> None:
    inc = config.get(_CONST_TRANSLATE, _CONST_INCLUDE)
    enc = config.get(_CONST_EXTRACT, _CONST_ENCODING)
    dir = config.get(_CONST_EXTRACT, _CONST_DIRECTORY)

    work_dir = Path('.')
    inject_dir = work_dir / dir

    pass


def execute(cmd: str, config: ConfigParser) -> None:
    if cmd in ('extract', 'x'):
        extract(config)
    elif cmd in ('inject', 'i'):
        inject(config)
    else:
        print(f'Unsupported command \'{cmd}\'')
