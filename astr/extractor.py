import re
import json

from typing import Dict, List, Tuple
from .annotations import Token
from .exceptions import ExtractorError



# 用于提取，组1是匹配到的文本，支持“\uUUUU”，“\xXX”
_STR_RE_STRING = r'"((?:[^"\\]|\\[^ux]|\\u[\dA-Fa-f]{4}|\\x[\dA-Fa-f]{2})*)"'

_RE_STRING = re.compile(_STR_RE_STRING, re.MULTILINE)
_RE_STRING2 = re.compile(_STR_RE_STRING.replace('"', '\''), re.MULTILINE)
# 用于判断，这里的文本是全部匹配
_RE_WHITESPACE = re.compile(r'^(\s+)?$')
_RE_ASCII = re.compile(r'^([\x00-\x7f]+)$')

TYPE_DEFINE = 0
TYPE_REFERENCE = 1
TYPE_OTHERS = 2


def normalize_quote(source: str) -> str:
    return _RE_STRING2.sub(lambda match: f'{json.dumps(match.group(1))}', source)


def extract(source: str) -> Tuple[List[str], List[Token]]:
    tokens: List[Token] = []
    string_id: int = 0
    string_map: Dict[str, int] = {}  # [string] -> string_id
    string_list: List[str] = []  # [string_id] -> string

    source = normalize_quote(source)

    s = ''
    i = 0  # 当前
    j = 0  # 预查
    l = len(source)
    while i < l:
        j = source.find('"', i)

        if j == -1:
            # 没有引号
            s = source[i:l]

            if s:  # 忽略空白
                tokens.append((TYPE_OTHERS, s))

            break

        # 引号左侧
        s = source[i:j]

        if s:  # 忽略空白
            tokens.append((TYPE_OTHERS, s))

        i = j
        m = _RE_STRING.match(source, i)

        if not m:  # 未匹配的引号
            raise ExtractorError(f'Unexpected char \'{source[i]}\'')

        # 引号内部
        s = eval(m.group(0))
        i = m.end(0)

        # 过滤掉空白符和ASCII码
        if _RE_WHITESPACE.match(s) or _RE_ASCII.match(s):
            tokens.append((TYPE_OTHERS, '"' + s + '"'))
        else:
            if s not in string_map:  # 字符串第一次出现
                string_map[s] = string_id
                string_list.append(s)
                string_id += 1

            tokens.append((TYPE_REFERENCE, string_map[s]))

    if string_id:  # 如果有字符串
        tokens.insert(0, (TYPE_DEFINE, string_list))

    return string_list, tokens
