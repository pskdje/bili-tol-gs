from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HaveMedalType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Medal_Common: _ClassVar[HaveMedalType]
    Medal_Group: _ClassVar[HaveMedalType]

class MedalType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Medal_Wear: _ClassVar[MedalType]
    Medal_Spec: _ClassVar[MedalType]

class RiskPolicyEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RP_NORMAL: _ClassVar[RiskPolicyEnum]
    RP_POLICY: _ClassVar[RiskPolicyEnum]
    RP_SILENCE: _ClassVar[RiskPolicyEnum]
    RP_CNY: _ClassVar[RiskPolicyEnum]
    RP_BIGEV: _ClassVar[RiskPolicyEnum]

class RoomAnonTypeEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RA_ALL: _ClassVar[RoomAnonTypeEnum]
    RA_With_Subject: _ClassVar[RoomAnonTypeEnum]
Medal_Common: HaveMedalType
Medal_Group: HaveMedalType
Medal_Wear: MedalType
Medal_Spec: MedalType
RP_NORMAL: RiskPolicyEnum
RP_POLICY: RiskPolicyEnum
RP_SILENCE: RiskPolicyEnum
RP_CNY: RiskPolicyEnum
RP_BIGEV: RiskPolicyEnum
RA_ALL: RoomAnonTypeEnum
RA_With_Subject: RoomAnonTypeEnum

class AccountInfo(_message.Message):
    __slots__ = ("name", "face")
    NAME_FIELD_NUMBER: _ClassVar[int]
    FACE_FIELD_NUMBER: _ClassVar[int]
    name: str
    face: str
    def __init__(self, name: _Optional[str] = ..., face: _Optional[str] = ...) -> None: ...

class Base(_message.Message):
    __slots__ = ("name", "face", "name_color", "is_mystery", "risk_ctrl_info", "origin_info", "official_info", "name_color_str")
    NAME_FIELD_NUMBER: _ClassVar[int]
    FACE_FIELD_NUMBER: _ClassVar[int]
    NAME_COLOR_FIELD_NUMBER: _ClassVar[int]
    IS_MYSTERY_FIELD_NUMBER: _ClassVar[int]
    RISK_CTRL_INFO_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_INFO_FIELD_NUMBER: _ClassVar[int]
    OFFICIAL_INFO_FIELD_NUMBER: _ClassVar[int]
    NAME_COLOR_STR_FIELD_NUMBER: _ClassVar[int]
    name: str
    face: str
    name_color: int
    is_mystery: bool
    risk_ctrl_info: RiskCtrlInfo
    origin_info: AccountInfo
    official_info: OfficialInfo
    name_color_str: str
    def __init__(self, name: _Optional[str] = ..., face: _Optional[str] = ..., name_color: _Optional[int] = ..., is_mystery: _Optional[bool] = ..., risk_ctrl_info: _Optional[_Union[RiskCtrlInfo, _Mapping]] = ..., origin_info: _Optional[_Union[AccountInfo, _Mapping]] = ..., official_info: _Optional[_Union[OfficialInfo, _Mapping]] = ..., name_color_str: _Optional[str] = ...) -> None: ...

class BaseOption(_message.Message):
    __slots__ = ("need_mystery", "risk_ctrl", "room_anon_ctrl", "risk_ctrl_handles")
    NEED_MYSTERY_FIELD_NUMBER: _ClassVar[int]
    RISK_CTRL_FIELD_NUMBER: _ClassVar[int]
    ROOM_ANON_CTRL_FIELD_NUMBER: _ClassVar[int]
    RISK_CTRL_HANDLES_FIELD_NUMBER: _ClassVar[int]
    need_mystery: bool
    risk_ctrl: RiskCtrl
    room_anon_ctrl: RoomAnonCtrl
    risk_ctrl_handles: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, need_mystery: _Optional[bool] = ..., risk_ctrl: _Optional[_Union[RiskCtrl, _Mapping]] = ..., room_anon_ctrl: _Optional[_Union[RoomAnonCtrl, _Mapping]] = ..., risk_ctrl_handles: _Optional[_Iterable[int]] = ...) -> None: ...

class Guard(_message.Message):
    __slots__ = ("level", "expired_str")
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    EXPIRED_STR_FIELD_NUMBER: _ClassVar[int]
    level: int
    expired_str: str
    def __init__(self, level: _Optional[int] = ..., expired_str: _Optional[str] = ...) -> None: ...

class GuardLeader(_message.Message):
    __slots__ = ("is_guard_leader",)
    IS_GUARD_LEADER_FIELD_NUMBER: _ClassVar[int]
    is_guard_leader: bool
    def __init__(self, is_guard_leader: _Optional[bool] = ...) -> None: ...

class GuardLeaderOption(_message.Message):
    __slots__ = ("ruid", "room_id")
    RUID_FIELD_NUMBER: _ClassVar[int]
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    ruid: int
    room_id: int
    def __init__(self, ruid: _Optional[int] = ..., room_id: _Optional[int] = ...) -> None: ...

class GuardOption(_message.Message):
    __slots__ = ("ruid", "use_local_cache", "strong_depend")
    RUID_FIELD_NUMBER: _ClassVar[int]
    USE_LOCAL_CACHE_FIELD_NUMBER: _ClassVar[int]
    STRONG_DEPEND_FIELD_NUMBER: _ClassVar[int]
    ruid: int
    use_local_cache: bool
    strong_depend: bool
    def __init__(self, ruid: _Optional[int] = ..., use_local_cache: _Optional[bool] = ..., strong_depend: _Optional[bool] = ...) -> None: ...

class Medal(_message.Message):
    __slots__ = ("name", "level", "color_start", "color_end", "color_border", "color", "id", "typ", "is_light", "ruid", "guard_level", "score", "guard_icon", "honor_icon", "v2_medal_color_start", "v2_medal_color_end", "v2_medal_color_border", "v2_medal_color_text", "v2_medal_color_level", "user_receive_count")
    NAME_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    COLOR_START_FIELD_NUMBER: _ClassVar[int]
    COLOR_END_FIELD_NUMBER: _ClassVar[int]
    COLOR_BORDER_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    TYP_FIELD_NUMBER: _ClassVar[int]
    IS_LIGHT_FIELD_NUMBER: _ClassVar[int]
    RUID_FIELD_NUMBER: _ClassVar[int]
    GUARD_LEVEL_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    GUARD_ICON_FIELD_NUMBER: _ClassVar[int]
    HONOR_ICON_FIELD_NUMBER: _ClassVar[int]
    V2_MEDAL_COLOR_START_FIELD_NUMBER: _ClassVar[int]
    V2_MEDAL_COLOR_END_FIELD_NUMBER: _ClassVar[int]
    V2_MEDAL_COLOR_BORDER_FIELD_NUMBER: _ClassVar[int]
    V2_MEDAL_COLOR_TEXT_FIELD_NUMBER: _ClassVar[int]
    V2_MEDAL_COLOR_LEVEL_FIELD_NUMBER: _ClassVar[int]
    USER_RECEIVE_COUNT_FIELD_NUMBER: _ClassVar[int]
    name: str
    level: int
    color_start: int
    color_end: int
    color_border: int
    color: int
    id: int
    typ: HaveMedalType
    is_light: int
    ruid: int
    guard_level: int
    score: int
    guard_icon: str
    honor_icon: str
    v2_medal_color_start: str
    v2_medal_color_end: str
    v2_medal_color_border: str
    v2_medal_color_text: str
    v2_medal_color_level: str
    user_receive_count: int
    def __init__(self, name: _Optional[str] = ..., level: _Optional[int] = ..., color_start: _Optional[int] = ..., color_end: _Optional[int] = ..., color_border: _Optional[int] = ..., color: _Optional[int] = ..., id: _Optional[int] = ..., typ: _Optional[_Union[HaveMedalType, str]] = ..., is_light: _Optional[int] = ..., ruid: _Optional[int] = ..., guard_level: _Optional[int] = ..., score: _Optional[int] = ..., guard_icon: _Optional[str] = ..., honor_icon: _Optional[str] = ..., v2_medal_color_start: _Optional[str] = ..., v2_medal_color_end: _Optional[str] = ..., v2_medal_color_border: _Optional[str] = ..., v2_medal_color_text: _Optional[str] = ..., v2_medal_color_level: _Optional[str] = ..., user_receive_count: _Optional[int] = ...) -> None: ...

class MedalOption(_message.Message):
    __slots__ = ("typ", "ruid", "need_guard", "strong_depend", "need_group")
    TYP_FIELD_NUMBER: _ClassVar[int]
    RUID_FIELD_NUMBER: _ClassVar[int]
    NEED_GUARD_FIELD_NUMBER: _ClassVar[int]
    STRONG_DEPEND_FIELD_NUMBER: _ClassVar[int]
    NEED_GROUP_FIELD_NUMBER: _ClassVar[int]
    typ: MedalType
    ruid: int
    need_guard: bool
    strong_depend: bool
    need_group: bool
    def __init__(self, typ: _Optional[_Union[MedalType, str]] = ..., ruid: _Optional[int] = ..., need_guard: _Optional[bool] = ..., strong_depend: _Optional[bool] = ..., need_group: _Optional[bool] = ...) -> None: ...

class OfficialInfo(_message.Message):
    __slots__ = ("role", "title", "desc", "type")
    ROLE_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESC_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    role: int
    title: str
    desc: str
    type: int
    def __init__(self, role: _Optional[int] = ..., title: _Optional[str] = ..., desc: _Optional[str] = ..., type: _Optional[int] = ...) -> None: ...

class RiskCtrl(_message.Message):
    __slots__ = ("room_id", "policy")
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_FIELD_NUMBER: _ClassVar[int]
    room_id: int
    policy: RiskPolicyEnum
    def __init__(self, room_id: _Optional[int] = ..., policy: _Optional[_Union[RiskPolicyEnum, str]] = ...) -> None: ...

class RiskCtrlInfo(_message.Message):
    __slots__ = ("name", "face")
    NAME_FIELD_NUMBER: _ClassVar[int]
    FACE_FIELD_NUMBER: _ClassVar[int]
    name: str
    face: str
    def __init__(self, name: _Optional[str] = ..., face: _Optional[str] = ...) -> None: ...

class RoomAnonCtrl(_message.Message):
    __slots__ = ("type",)
    TYPE_FIELD_NUMBER: _ClassVar[int]
    type: RoomAnonTypeEnum
    def __init__(self, type: _Optional[_Union[RoomAnonTypeEnum, str]] = ...) -> None: ...

class Title(_message.Message):
    __slots__ = ("old_title_css_id", "title_css_id")
    OLD_TITLE_CSS_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_CSS_ID_FIELD_NUMBER: _ClassVar[int]
    old_title_css_id: str
    title_css_id: str
    def __init__(self, old_title_css_id: _Optional[str] = ..., title_css_id: _Optional[str] = ...) -> None: ...

class TitleOption(_message.Message):
    __slots__ = ("room_id", "strong_depend")
    ROOM_ID_FIELD_NUMBER: _ClassVar[int]
    STRONG_DEPEND_FIELD_NUMBER: _ClassVar[int]
    room_id: int
    strong_depend: bool
    def __init__(self, room_id: _Optional[int] = ..., strong_depend: _Optional[bool] = ...) -> None: ...

class UserHeadFrame(_message.Message):
    __slots__ = ("id", "frame_img")
    ID_FIELD_NUMBER: _ClassVar[int]
    FRAME_IMG_FIELD_NUMBER: _ClassVar[int]
    id: int
    frame_img: str
    def __init__(self, id: _Optional[int] = ..., frame_img: _Optional[str] = ...) -> None: ...

class UserInfo(_message.Message):
    __slots__ = ("uid", "base", "medal", "wealth", "title", "guard", "uhead_frame", "guard_leader")
    UID_FIELD_NUMBER: _ClassVar[int]
    BASE_FIELD_NUMBER: _ClassVar[int]
    MEDAL_FIELD_NUMBER: _ClassVar[int]
    WEALTH_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    GUARD_FIELD_NUMBER: _ClassVar[int]
    UHEAD_FRAME_FIELD_NUMBER: _ClassVar[int]
    GUARD_LEADER_FIELD_NUMBER: _ClassVar[int]
    uid: int
    base: Base
    medal: Medal
    wealth: Wealth
    title: Title
    guard: Guard
    uhead_frame: UserHeadFrame
    guard_leader: GuardLeader
    def __init__(self, uid: _Optional[int] = ..., base: _Optional[_Union[Base, _Mapping]] = ..., medal: _Optional[_Union[Medal, _Mapping]] = ..., wealth: _Optional[_Union[Wealth, _Mapping]] = ..., title: _Optional[_Union[Title, _Mapping]] = ..., guard: _Optional[_Union[Guard, _Mapping]] = ..., uhead_frame: _Optional[_Union[UserHeadFrame, _Mapping]] = ..., guard_leader: _Optional[_Union[GuardLeader, _Mapping]] = ...) -> None: ...

class Wealth(_message.Message):
    __slots__ = ("level", "dm_icon_key")
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    DM_ICON_KEY_FIELD_NUMBER: _ClassVar[int]
    level: int
    dm_icon_key: str
    def __init__(self, level: _Optional[int] = ..., dm_icon_key: _Optional[str] = ...) -> None: ...

class WealthOption(_message.Message):
    __slots__ = ("roomid", "view_uid", "ruid", "strong_depend")
    ROOMID_FIELD_NUMBER: _ClassVar[int]
    VIEW_UID_FIELD_NUMBER: _ClassVar[int]
    RUID_FIELD_NUMBER: _ClassVar[int]
    STRONG_DEPEND_FIELD_NUMBER: _ClassVar[int]
    roomid: int
    view_uid: int
    ruid: int
    strong_depend: bool
    def __init__(self, roomid: _Optional[int] = ..., view_uid: _Optional[int] = ..., ruid: _Optional[int] = ..., strong_depend: _Optional[bool] = ...) -> None: ...
