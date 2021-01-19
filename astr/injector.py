from typing import List, Union, cast
from .anotations import Dictionary, Token, DefineToken, ReferenceToken, NormalToken
from .exceptions import InjectorError


def inject(tokens: List[Token], dictionary: Dictionary) -> str:
    buffer: List[str] = []

    if not tokens:
        return ''

    define_token = tokens[0]

    if define_token[0] != 0:
        raise InjectorError('First token is not <type_define>')

    string_list = cast(DefineToken, define_token)[1]
    tokens = tokens[1:]

    # pylint: disable=unsubscriptable-object
    value: Union[int, str]
    for token in tokens:
        type_ = token[0]

        if type_ == 0:
            raise InjectorError('Unexpected token <type_define>')

        if type_ == 1:
            value = cast(ReferenceToken, token)[1]
            string = string_list[value]
            buffer.append('"' + (dictionary.get(string) or string) + '"')
        elif type_ == 2:
            value = cast(NormalToken, token)[1]
            buffer.append(value)
        else:
            raise InjectorError('Invalid token type')

    return ''.join(buffer).replace('\\n', '\n')
