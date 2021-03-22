import re
from typing import Dict, List, Tuple, Union
from .annotations import Token
from .exceptions import ExtractorError

# 用于提取，组1是匹配到的文本，支持“\uUUUU”，“\xXX”
_STR_RE_STRING = r'"((?:[^"\\]|\\[^ux]|\\u[\dA-Fa-f]{4}|\\x[\dA-Fa-f]{2})*)"'

_RE_STRING = re.compile(_STR_RE_STRING, re.MULTILINE)
_RE_STRING2 = re.compile(_STR_RE_STRING.replace('"', '\''), re.MULTILINE)
_RE_OTHERS = re.compile(r'[^\'\"]+')
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

    rules = (('s', _RE_STRING), ('s', _RE_STRING2), ('o', _RE_OTHERS))
    source_length = len(source)

    from_ = 0
    while from_ < source_length:
        matched: Union[re.Match[str], None] = None

        for type_, rule in rules:
            matched = rule.match(source, from_)

            if matched:
                break

        if not matched:
            raise ExtractorError(f'Unexpected char \'{source[from_]}\'')

        from_ = matched.end(0)

        if type_ == 's':
            raw = matched.group(0)
            text = matched.group(1)

            if _RE_WHITESPACE.match(text) or _RE_ASCII.match(text):
                tokens.append((TYPE_OTHERS, raw))
            else:
                if text not in string_map:
                    string_map[text] = string_id
                    string_list.append(text)
                    string_id += 1

                tokens.append((TYPE_REFERENCE, string_map[text]))
        elif type_ == 'o':
            raw = matched.group(0)
            tokens.append((TYPE_OTHERS, raw))
        else:
            raise ExtractorError('Unknown Error!')

    tokens.insert(0, (TYPE_DEFINE, string_list))

    return string_list, tokens
