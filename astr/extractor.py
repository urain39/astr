import re

from typing import List, Dict
from .anotations import Token
from .exceptions import ExtractorError

# 用于提取，组1是匹配到的文本，支持“\uUUUU”，“\xXX”
_RE_STRING = re.compile(
    r'"((?:[^"\\]|\\[^ux]|\\u[\dA-Fa-f]{4}|\\x[\dA-Fa-f]{2})*)"', re.MULTILINE)
# 用于判断，这里的文本是全部匹配
_RE_WHITESPACE = re.compile(r'^(\s+)$')
_RE_ASCII = re.compile(r'^([\x00-\x7f]+)$')

TYPE_DEFINE = 0
TYPE_REFERENCE = 1
TYPE_OTHERS = 2


def extract(source: str) -> List[Token]:
    tokens: List[Token] = []
    stringId: int = 0
    stringMap: Dict[str, int] = {}  # [string] -> stringId
    stringList: List[str] = []  # [stringId] -> string

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
        s = m.group(1)
        i = m.end(0)

        if s \
                and not _RE_WHITESPACE.match(s) \
                and not _RE_ASCII.match(s):
            if not s in stringMap:  # 字符串第一次出现
                stringMap[s] = stringId
                stringList.append(s)
                stringId += 1

            tokens.append((TYPE_REFERENCE, stringMap[s]))

    if stringId:  # 如果有字符串
        tokens.insert(0, (TYPE_DEFINE, stringList))

    return tokens
