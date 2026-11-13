from bilibili.live.component.common_model import fans_club_pb2 as _fans_club_pb2
from bilibili.live.component.common_model import user_dagw_pb2 as _user_dagw_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class InteractWord(_message.Message):
    __slots__ = ("uid", "uname", "uname_color", "identities", "msg_type", "roomid", "timestamp", "score", "fans_medal", "is_spread", "spread_info", "contribution", "spread_desc", "tail_icon", "trigger_time", "privilege_type", "core_user_type", "tail_text", "contribution_v2", "group_medal", "is_mystery", "uinfo", "relation_tail")
    class ContributionInfo(_message.Message):
        __slots__ = ("grade",)
        GRADE_FIELD_NUMBER: _ClassVar[int]
        grade: int
        def __init__(self, grade: _Optional[int] = ...) -> None: ...
    class ContributionInfoV2(_message.Message):
        __slots__ = ("grade", "rank_type", "text")
        GRADE_FIELD_NUMBER: _ClassVar[int]
        RANK_TYPE_FIELD_NUMBER: _ClassVar[int]
        TEXT_FIELD_NUMBER: _ClassVar[int]
        grade: int
        rank_type: str
        text: str
        def __init__(self, grade: _Optional[int] = ..., rank_type: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...
    class FansMedalInfo(_message.Message):
        __slots__ = ("target_id", "medal_level", "medal_name", "medal_color", "medal_color_start", "medal_color_end", "medal_color_border", "is_lighted", "guard_level", "special", "icon_id", "anchor_roomid", "score")
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        MEDAL_LEVEL_FIELD_NUMBER: _ClassVar[int]
        MEDAL_NAME_FIELD_NUMBER: _ClassVar[int]
        MEDAL_COLOR_FIELD_NUMBER: _ClassVar[int]
        MEDAL_COLOR_START_FIELD_NUMBER: _ClassVar[int]
        MEDAL_COLOR_END_FIELD_NUMBER: _ClassVar[int]
        MEDAL_COLOR_BORDER_FIELD_NUMBER: _ClassVar[int]
        IS_LIGHTED_FIELD_NUMBER: _ClassVar[int]
        GUARD_LEVEL_FIELD_NUMBER: _ClassVar[int]
        SPECIAL_FIELD_NUMBER: _ClassVar[int]
        ICON_ID_FIELD_NUMBER: _ClassVar[int]
        ANCHOR_ROOMID_FIELD_NUMBER: _ClassVar[int]
        SCORE_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        medal_level: int
        medal_name: str
        medal_color: int
        medal_color_start: int
        medal_color_end: int
        medal_color_border: int
        is_lighted: int
        guard_level: int
        special: str
        icon_id: int
        anchor_roomid: int
        score: int
        def __init__(self, target_id: _Optional[int] = ..., medal_level: _Optional[int] = ..., medal_name: _Optional[str] = ..., medal_color: _Optional[int] = ..., medal_color_start: _Optional[int] = ..., medal_color_end: _Optional[int] = ..., medal_color_border: _Optional[int] = ..., is_lighted: _Optional[int] = ..., guard_level: _Optional[int] = ..., special: _Optional[str] = ..., icon_id: _Optional[int] = ..., anchor_roomid: _Optional[int] = ..., score: _Optional[int] = ...) -> None: ...
    class UserAnchorRelation(_message.Message):
        __slots__ = ("tail_icon", "tail_guide_text", "tail_type")
        TAIL_ICON_FIELD_NUMBER: _ClassVar[int]
        TAIL_GUIDE_TEXT_FIELD_NUMBER: _ClassVar[int]
        TAIL_TYPE_FIELD_NUMBER: _ClassVar[int]
        tail_icon: str
        tail_guide_text: str
        tail_type: int
        def __init__(self, tail_icon: _Optional[str] = ..., tail_guide_text: _Optional[str] = ..., tail_type: _Optional[int] = ...) -> None: ...
    UID_FIELD_NUMBER: _ClassVar[int]
    UNAME_FIELD_NUMBER: _ClassVar[int]
    UNAME_COLOR_FIELD_NUMBER: _ClassVar[int]
    IDENTITIES_FIELD_NUMBER: _ClassVar[int]
    MSG_TYPE_FIELD_NUMBER: _ClassVar[int]
    ROOMID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    FANS_MEDAL_FIELD_NUMBER: _ClassVar[int]
    IS_SPREAD_FIELD_NUMBER: _ClassVar[int]
    SPREAD_INFO_FIELD_NUMBER: _ClassVar[int]
    CONTRIBUTION_FIELD_NUMBER: _ClassVar[int]
    SPREAD_DESC_FIELD_NUMBER: _ClassVar[int]
    TAIL_ICON_FIELD_NUMBER: _ClassVar[int]
    TRIGGER_TIME_FIELD_NUMBER: _ClassVar[int]
    PRIVILEGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CORE_USER_TYPE_FIELD_NUMBER: _ClassVar[int]
    TAIL_TEXT_FIELD_NUMBER: _ClassVar[int]
    CONTRIBUTION_V2_FIELD_NUMBER: _ClassVar[int]
    GROUP_MEDAL_FIELD_NUMBER: _ClassVar[int]
    IS_MYSTERY_FIELD_NUMBER: _ClassVar[int]
    UINFO_FIELD_NUMBER: _ClassVar[int]
    RELATION_TAIL_FIELD_NUMBER: _ClassVar[int]
    uid: int
    uname: str
    uname_color: str
    identities: _containers.RepeatedScalarFieldContainer[int]
    msg_type: int
    roomid: int
    timestamp: int
    score: int
    fans_medal: InteractWord.FansMedalInfo
    is_spread: int
    spread_info: str
    contribution: InteractWord.ContributionInfo
    spread_desc: str
    tail_icon: int
    trigger_time: int
    privilege_type: int
    core_user_type: int
    tail_text: str
    contribution_v2: InteractWord.ContributionInfoV2
    group_medal: _fans_club_pb2.GroupMedalBrief
    is_mystery: bool
    uinfo: _user_dagw_pb2.UserInfo
    relation_tail: InteractWord.UserAnchorRelation
    def __init__(self, uid: _Optional[int] = ..., uname: _Optional[str] = ..., uname_color: _Optional[str] = ..., identities: _Optional[_Iterable[int]] = ..., msg_type: _Optional[int] = ..., roomid: _Optional[int] = ..., timestamp: _Optional[int] = ..., score: _Optional[int] = ..., fans_medal: _Optional[_Union[InteractWord.FansMedalInfo, _Mapping]] = ..., is_spread: _Optional[int] = ..., spread_info: _Optional[str] = ..., contribution: _Optional[_Union[InteractWord.ContributionInfo, _Mapping]] = ..., spread_desc: _Optional[str] = ..., tail_icon: _Optional[int] = ..., trigger_time: _Optional[int] = ..., privilege_type: _Optional[int] = ..., core_user_type: _Optional[int] = ..., tail_text: _Optional[str] = ..., contribution_v2: _Optional[_Union[InteractWord.ContributionInfoV2, _Mapping]] = ..., group_medal: _Optional[_Union[_fans_club_pb2.GroupMedalBrief, _Mapping]] = ..., is_mystery: _Optional[bool] = ..., uinfo: _Optional[_Union[_user_dagw_pb2.UserInfo, _Mapping]] = ..., relation_tail: _Optional[_Union[InteractWord.UserAnchorRelation, _Mapping]] = ...) -> None: ...
