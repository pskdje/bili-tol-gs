from bilibili.live.component.common_model import user_dagw_pb2 as _user_dagw_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GoldRankBroadcast(_message.Message):
    __slots__ = ("rank_type", "list", "online_list")
    class GoldRankBrodcastItem(_message.Message):
        __slots__ = ("uid", "face", "score", "uname", "rank", "guard_level", "is_mystery", "uinfo")
        UID_FIELD_NUMBER: _ClassVar[int]
        FACE_FIELD_NUMBER: _ClassVar[int]
        SCORE_FIELD_NUMBER: _ClassVar[int]
        UNAME_FIELD_NUMBER: _ClassVar[int]
        RANK_FIELD_NUMBER: _ClassVar[int]
        GUARD_LEVEL_FIELD_NUMBER: _ClassVar[int]
        IS_MYSTERY_FIELD_NUMBER: _ClassVar[int]
        UINFO_FIELD_NUMBER: _ClassVar[int]
        uid: int
        face: str
        score: str
        uname: str
        rank: int
        guard_level: int
        is_mystery: bool
        uinfo: _user_dagw_pb2.UserInfo
        def __init__(self, uid: _Optional[int] = ..., face: _Optional[str] = ..., score: _Optional[str] = ..., uname: _Optional[str] = ..., rank: _Optional[int] = ..., guard_level: _Optional[int] = ..., is_mystery: _Optional[bool] = ..., uinfo: _Optional[_Union[_user_dagw_pb2.UserInfo, _Mapping]] = ...) -> None: ...
    RANK_TYPE_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    ONLINE_LIST_FIELD_NUMBER: _ClassVar[int]
    rank_type: str
    list: _containers.RepeatedCompositeFieldContainer[GoldRankBroadcast.GoldRankBrodcastItem]
    online_list: _containers.RepeatedCompositeFieldContainer[GoldRankBroadcast.GoldRankBrodcastItem]
    def __init__(self, rank_type: _Optional[str] = ..., list: _Optional[_Iterable[_Union[GoldRankBroadcast.GoldRankBrodcastItem, _Mapping]]] = ..., online_list: _Optional[_Iterable[_Union[GoldRankBroadcast.GoldRankBrodcastItem, _Mapping]]] = ...) -> None: ...
