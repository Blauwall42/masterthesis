from typing import TypedDict, Required

class ColumnSettings(TypedDict):
    bin: list[int] | int | bool
    replace: Required[dict[str | int, str | int] | bool]
    

class RoundSettings(TypedDict):
    digits: int
    to_half: Required[bool]