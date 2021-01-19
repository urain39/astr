from typing import List, Union, cast
from .anotations import Dictionary, Token, DefineToken, ReferenceToken, NormalToken
from .exceptions import InjectorError
from .extractor import TYPE_DEFINE, TYPE_REFERENCE, TYPE_OTHERS


def inject(tokens: List[Token], dictionary: Dictionary, strict: bool = False) -> str:
    buffer: List[str] = []

    if not tokens:
        return ''

    define_token = tokens[0]

    if define_token[0] != TYPE_DEFINE:
        raise InjectorError('First token is not <type_define>')

    string_list = cast(DefineToken, define_token)[1]
    tokens = tokens[1:]

    # pylint: disable=unsubscriptable-object
    value: Union[int, str]
    for token in tokens:
        type_ = token[0]

        if type_ == TYPE_DEFINE:
            raise InjectorError('Unexpected token <type_define>')

        if type_ == TYPE_REFERENCE:
            value = cast(ReferenceToken, token)[1]
            string = string_list[value]

            translated = dictionary.get(string)

            if not translated:
                if strict:
                    raise InjectorError(
                        f'Cannot find "{string}" in dictionary')

                print(f'WARNING: cannot find "{string}" in dictionary')

                translated = string

            buffer.append('"' + translated + '"')
        elif type_ == TYPE_OTHERS:
            value = cast(NormalToken, token)[1]
            buffer.append(value)
        else:
            raise InjectorError('Invalid token type')

    return ''.join(buffer)
