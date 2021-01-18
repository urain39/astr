from typing import Dict, List, Tuple, Union

# 0 - TYPE_DEFINE
# 1 - TYPE_REFERENCE
# 2 - TYPE_OTHERSs

# 因为Literal类型mypy下推导错误，所以这里我们全部使用int类型
DefineToken = Tuple[int, List[str]]
ReferenceToken = Tuple[int, int]
NormalToken = Tuple[int, str]
Token = Union[DefineToken, ReferenceToken, NormalToken]

Dictionary = Dict[str, str]
