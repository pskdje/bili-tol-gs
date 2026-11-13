from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GroupMedalBrief(_message.Message):
    __slots__ = ("medal_id", "name", "is_lighted")
    MEDAL_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_LIGHTED_FIELD_NUMBER: _ClassVar[int]
    medal_id: int
    name: str
    is_lighted: int
    def __init__(self, medal_id: _Optional[int] = ..., name: _Optional[str] = ..., is_lighted: _Optional[int] = ...) -> None: ...
