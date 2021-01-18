from typing import Dict, List, Tuple, Union, Literal

# 0 - TYPE_DEFINE
# 1 - TYPE_REFERENCE
# 2 - TYPE_OTHERSs

# 因为这里Literal类型会在mypy下推导错误，所以这里
# 我们全部使用int类型代替
DefineToken = Tuple[int, List[str]]
ReferenceToken = Tuple[int, int]
NormalToken = Tuple[int, str]
Token = Union[DefineToken, ReferenceToken, NormalToken]

Dictionary = Dict[str, str]
