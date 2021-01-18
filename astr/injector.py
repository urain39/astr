from typing import List, Tuple, Union, cast
from .anotations import Dictionary, Token, DefineToken, ReferenceToken, NormalToken
from .exceptions import InjectorError


def parseDictionary(source: str) -> Tuple[List[str], Dictionary]:
    dictionary = {}
    unmatchedList = []
    lines = source.split('\n')

    i = 0
    l = len(lines)
    while i < l:
        line = lines[i]

        if line:
            key = line
            i += 1

            if i < l:
                line = lines[i]
            else:
                unmatchedList.append(key)
                break

            if line:
                dictionary[key] = line
            else:
                unmatchedList.append(key)

        i += 1

    return unmatchedList, dictionary

def inject(tokens: List[Token], dictionary: Dictionary) -> str:
    buffer: List[str] = []

    if not tokens:
        return ''

    defineToken = tokens[0]

    if defineToken[0] != 0:
        raise InjectorError('first token is not <type_define>')

    stringList = cast(DefineToken, defineToken)[1]
    tokens = tokens[1:]

    value: Union[int, str]
    for token in tokens:
        type_ = token[0]

        if type_ == 0:
            raise InjectorError('unexpected token <type_define>')
        elif type_ == 1:
            value = cast(ReferenceToken, token)[1]
            string = stringList[value]
            buffer.append('"' + (dictionary.get(string) or string) + '"')
        elif type_ == 2:
            value = cast(NormalToken, token)[1]
            buffer.append(value)
        else:
            raise InjectorError('Invalid token type')

    return ''.join(buffer).replace('\\n', '\n')
