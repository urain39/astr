import re

from typing import Dict, List, Tuple
from .anotations import Token
from .exceptions import ExtractorError

# 用于提取，组1是匹配到的文本，支持“\uUUUU”，“\xXX”
_RE_STRING = re.compile(
    r'"((?:[^"\\]|\\[^ux]|\\u[\dA-Fa-f]{4}|\\x[\dA-Fa-f]{2})*)"', re.MULTILINE)
# 用于判断，这里的文本是全部匹配
_RE_WHITESPACE = re.compile(r'^(\s+)?$')
_RE_ASCII = re.compile(r'^([\x00-\x7f]+)$')

TYPE_DEFINE = 0
TYPE_REFERENCE = 1
TYPE_OTHERS = 2


def extract(source: str) -> Tuple[List[str], List[Token]]:
    tokens: List[Token] = []
    string_id: int = 0
    string_map: Dict[str, int] = {}  # [string] -> string_id
    string_list: List[str] = []  # [string_id] -> string

    # 转义换行符（Python3会处理换行符兼容性问题的）
    source = source.replace('\n', '\\n')

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

        # 过滤掉空白符和ASCII码
        if _RE_WHITESPACE.match(s) or _RE_ASCII.match(s):
            # 理论上字符串里不应该存在显式的换行符，
            # 即使存在， 我们以转义的形式输出也不会出错。
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
