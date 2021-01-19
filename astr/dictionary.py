from typing import List, Tuple
from .anotations import Dictionary


def parse_dictionary(source: str) -> Tuple[List[Tuple[int, str]], Dictionary]:
    dictionary = {}
    unmatched_list = []
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
                unmatched_list.append((i, key))
                break

            if line:
                dictionary[key] = line
            else:
                unmatched_list.append((i, key))

        i += 1

    return unmatched_list, dictionary
