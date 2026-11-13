from bilibili.live.common.proto import user_dagw_pb2 as _user_dagw_pb2
from bilibili.live.common.proto import effect_pb2 as _effect_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SendGiftBroadcast(_message.Message):
    __slots__ = ("uid", "uname", "face", "name_color", "guard_level", "svga_block", "send_master", "medal_info", "blind_gift", "gift_list", "switch", "test", "wealth_info", "group_medal", "sender_uinfo")
    class SendMaster(_message.Message):
        __slots__ = ("uid", "uname")
        UID_FIELD_NUMBER: _ClassVar[int]
        UNAME_FIELD_NUMBER: _ClassVar[int]
        uid: int
        uname: str
        def __init__(self, uid: _Optional[int] = ..., uname: _Optional[str] = ...) -> None: ...
    class MedalInfo(_message.Message):
        __slots__ = ("target_id", "special", "anchor_uname", "anchor_roomid", "medal_level", "medal_name", "medal_color", "medal_color_start", "medal_color_end", "medal_color_border", "is_lighted", "guard_level")
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        SPECIAL_FIELD_NUMBER: _ClassVar[int]
        ANCHOR_UNAME_FIELD_NUMBER: _ClassVar[int]
        ANCHOR_ROOMID_FIELD_NUMBER: _ClassVar[int]
        MEDAL_LEVEL_FIELD_NUMBER: _ClassVar[int]
        MEDAL_NAME_FIELD_NUMBER: _ClassVar[int]
        MEDAL_COLOR_FIELD_NUMBER: _ClassVar[int]
        MEDAL_COLOR_START_FIELD_NUMBER: _ClassVar[int]
        MEDAL_COLOR_END_FIELD_NUMBER: _ClassVar[int]
        MEDAL_COLOR_BORDER_FIELD_NUMBER: _ClassVar[int]
        IS_LIGHTED_FIELD_NUMBER: _ClassVar[int]
        GUARD_LEVEL_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        special: str
        anchor_uname: str
        anchor_roomid: int
        medal_level: int
        medal_name: str
        medal_color: int
        medal_color_start: int
        medal_color_end: int
        medal_color_border: int
        is_lighted: int
        guard_level: int
        def __init__(self, target_id: _Optional[int] = ..., special: _Optional[str] = ..., anchor_uname: _Optional[str] = ..., anchor_roomid: _Optional[int] = ..., medal_level: _Optional[int] = ..., medal_name: _Optional[str] = ..., medal_color: _Optional[int] = ..., medal_color_start: _Optional[int] = ..., medal_color_end: _Optional[int] = ..., medal_color_border: _Optional[int] = ..., is_lighted: _Optional[int] = ..., guard_level: _Optional[int] = ...) -> None: ...
    class BlindGift(_message.Message):
        __slots__ = ("blind_gift_config_id", "original_gift_id", "original_gift_name", "gift_action", "original_gift_price", "gift_tip_price")
        BLIND_GIFT_CONFIG_ID_FIELD_NUMBER: _ClassVar[int]
        ORIGINAL_GIFT_ID_FIELD_NUMBER: _ClassVar[int]
        ORIGINAL_GIFT_NAME_FIELD_NUMBER: _ClassVar[int]
        FROM_FIELD_NUMBER: _ClassVar[int]
        GIFT_ACTION_FIELD_NUMBER: _ClassVar[int]
        ORIGINAL_GIFT_PRICE_FIELD_NUMBER: _ClassVar[int]
        GIFT_TIP_PRICE_FIELD_NUMBER: _ClassVar[int]
        blind_gift_config_id: int
        original_gift_id: int
        original_gift_name: str
        gift_action: str
        original_gift_price: int
        gift_tip_price: int
        def __init__(self, blind_gift_config_id: _Optional[int] = ..., original_gift_id: _Optional[int] = ..., original_gift_name: _Optional[str] = ..., gift_action: _Optional[str] = ..., original_gift_price: _Optional[int] = ..., gift_tip_price: _Optional[int] = ..., **kwargs) -> None: ...
    class GiftItem(_message.Message):
        __slots__ = ("gift_id", "gift_name", "num", "demarcation", "price", "discount_price", "total_coin", "coin_type", "tid", "timestamp", "super_batch_gift_num", "batch_combo_id", "combo_resources_id", "combo_total_coin", "combo_stay_time", "magnification", "show_batch_combo_send", "action", "effect_block", "is_special_batch", "float_sc_resource_id", "tag_image", "crit_prob", "rcost", "test", "face_effect_type", "face_effect_id", "is_naming", "receive_user_info", "is_join_receiver", "bag_gift", "gift_tag", "receiver_uinfo", "face_effect_v2", "gift_info", "gift_tip_price", "face_effect", "benefits", "effect_config")
        GIFT_ID_FIELD_NUMBER: _ClassVar[int]
        GIFT_NAME_FIELD_NUMBER: _ClassVar[int]
        NUM_FIELD_NUMBER: _ClassVar[int]
        DEMARCATION_FIELD_NUMBER: _ClassVar[int]
        PRICE_FIELD_NUMBER: _ClassVar[int]
        DISCOUNT_PRICE_FIELD_NUMBER: _ClassVar[int]
        TOTAL_COIN_FIELD_NUMBER: _ClassVar[int]
        COIN_TYPE_FIELD_NUMBER: _ClassVar[int]
        TID_FIELD_NUMBER: _ClassVar[int]
        TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
        SUPER_BATCH_GIFT_NUM_FIELD_NUMBER: _ClassVar[int]
        BATCH_COMBO_ID_FIELD_NUMBER: _ClassVar[int]
        COMBO_RESOURCES_ID_FIELD_NUMBER: _ClassVar[int]
        COMBO_TOTAL_COIN_FIELD_NUMBER: _ClassVar[int]
        COMBO_STAY_TIME_FIELD_NUMBER: _ClassVar[int]
        MAGNIFICATION_FIELD_NUMBER: _ClassVar[int]
        SHOW_BATCH_COMBO_SEND_FIELD_NUMBER: _ClassVar[int]
        ACTION_FIELD_NUMBER: _ClassVar[int]
        EFFECT_BLOCK_FIELD_NUMBER: _ClassVar[int]
        IS_SPECIAL_BATCH_FIELD_NUMBER: _ClassVar[int]
        FLOAT_SC_RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
        TAG_IMAGE_FIELD_NUMBER: _ClassVar[int]
        CRIT_PROB_FIELD_NUMBER: _ClassVar[int]
        RCOST_FIELD_NUMBER: _ClassVar[int]
        TEST_FIELD_NUMBER: _ClassVar[int]
        FACE_EFFECT_TYPE_FIELD_NUMBER: _ClassVar[int]
        FACE_EFFECT_ID_FIELD_NUMBER: _ClassVar[int]
        IS_NAMING_FIELD_NUMBER: _ClassVar[int]
        RECEIVE_USER_INFO_FIELD_NUMBER: _ClassVar[int]
        IS_JOIN_RECEIVER_FIELD_NUMBER: _ClassVar[int]
        BAG_GIFT_FIELD_NUMBER: _ClassVar[int]
        GIFT_TAG_FIELD_NUMBER: _ClassVar[int]
        RECEIVER_UINFO_FIELD_NUMBER: _ClassVar[int]
        FACE_EFFECT_V2_FIELD_NUMBER: _ClassVar[int]
        GIFT_INFO_FIELD_NUMBER: _ClassVar[int]
        GIFT_TIP_PRICE_FIELD_NUMBER: _ClassVar[int]
        FACE_EFFECT_FIELD_NUMBER: _ClassVar[int]
        BENEFITS_FIELD_NUMBER: _ClassVar[int]
        EFFECT_CONFIG_FIELD_NUMBER: _ClassVar[int]
        gift_id: int
        gift_name: str
        num: int
        demarcation: int
        price: int
        discount_price: int
        total_coin: int
        coin_type: str
        tid: str
        timestamp: int
        super_batch_gift_num: int
        batch_combo_id: str
        combo_resources_id: int
        combo_total_coin: int
        combo_stay_time: int
        magnification: float
        show_batch_combo_send: bool
        action: str
        effect_block: int
        is_special_batch: int
        float_sc_resource_id: int
        tag_image: str
        crit_prob: int
        rcost: int
        test: int
        face_effect_type: int
        face_effect_id: int
        is_naming: bool
        receive_user_info: SendGiftBroadcast.ReceiveUserInfo
        is_join_receiver: bool
        bag_gift: SendGiftBroadcast.BagGiftInfo
        gift_tag: _containers.RepeatedScalarFieldContainer[int]
        receiver_uinfo: _user_dagw_pb2.UserInfo
        face_effect_v2: SendGiftBroadcast.FaceEffectV2
        gift_info: GiftMaterialSnapShot
        gift_tip_price: int
        face_effect: SendGiftBroadcast.FaceEffect
        benefits: GiftBenefits
        effect_config: _effect_pb2.EffectConfigItem
        def __init__(self, gift_id: _Optional[int] = ..., gift_name: _Optional[str] = ..., num: _Optional[int] = ..., demarcation: _Optional[int] = ..., price: _Optional[int] = ..., discount_price: _Optional[int] = ..., total_coin: _Optional[int] = ..., coin_type: _Optional[str] = ..., tid: _Optional[str] = ..., timestamp: _Optional[int] = ..., super_batch_gift_num: _Optional[int] = ..., batch_combo_id: _Optional[str] = ..., combo_resources_id: _Optional[int] = ..., combo_total_coin: _Optional[int] = ..., combo_stay_time: _Optional[int] = ..., magnification: _Optional[float] = ..., show_batch_combo_send: _Optional[bool] = ..., action: _Optional[str] = ..., effect_block: _Optional[int] = ..., is_special_batch: _Optional[int] = ..., float_sc_resource_id: _Optional[int] = ..., tag_image: _Optional[str] = ..., crit_prob: _Optional[int] = ..., rcost: _Optional[int] = ..., test: _Optional[int] = ..., face_effect_type: _Optional[int] = ..., face_effect_id: _Optional[int] = ..., is_naming: _Optional[bool] = ..., receive_user_info: _Optional[_Union[SendGiftBroadcast.ReceiveUserInfo, _Mapping]] = ..., is_join_receiver: _Optional[bool] = ..., bag_gift: _Optional[_Union[SendGiftBroadcast.BagGiftInfo, _Mapping]] = ..., gift_tag: _Optional[_Iterable[int]] = ..., receiver_uinfo: _Optional[_Union[_user_dagw_pb2.UserInfo, _Mapping]] = ..., face_effect_v2: _Optional[_Union[SendGiftBroadcast.FaceEffectV2, _Mapping]] = ..., gift_info: _Optional[_Union[GiftMaterialSnapShot, _Mapping]] = ..., gift_tip_price: _Optional[int] = ..., face_effect: _Optional[_Union[SendGiftBroadcast.FaceEffect, _Mapping]] = ..., benefits: _Optional[_Union[GiftBenefits, _Mapping]] = ..., effect_config: _Optional[_Union[_effect_pb2.EffectConfigItem, _Mapping]] = ...) -> None: ...
    class ReceiveUserInfo(_message.Message):
        __slots__ = ("uname", "uid")
        UNAME_FIELD_NUMBER: _ClassVar[int]
        UID_FIELD_NUMBER: _ClassVar[int]
        uname: str
        uid: int
        def __init__(self, uname: _Optional[str] = ..., uid: _Optional[int] = ...) -> None: ...
    class BagGiftInfo(_message.Message):
        __slots__ = ("show_price", "price_for_show")
        SHOW_PRICE_FIELD_NUMBER: _ClassVar[int]
        PRICE_FOR_SHOW_FIELD_NUMBER: _ClassVar[int]
        show_price: int
        price_for_show: int
        def __init__(self, show_price: _Optional[int] = ..., price_for_show: _Optional[int] = ...) -> None: ...
    class FaceEffectV2(_message.Message):
        __slots__ = ("id", "type")
        ID_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        id: int
        type: int
        def __init__(self, id: _Optional[int] = ..., type: _Optional[int] = ...) -> None: ...
    class FaceEffect(_message.Message):
        __slots__ = ("face_effect_type", "candidate_face_effects")
        FACE_EFFECT_TYPE_FIELD_NUMBER: _ClassVar[int]
        CANDIDATE_FACE_EFFECTS_FIELD_NUMBER: _ClassVar[int]
        face_effect_type: int
        candidate_face_effects: _containers.RepeatedCompositeFieldContainer[SendGiftBroadcast.FaceEffectItem]
        def __init__(self, face_effect_type: _Optional[int] = ..., candidate_face_effects: _Optional[_Iterable[_Union[SendGiftBroadcast.FaceEffectItem, _Mapping]]] = ...) -> None: ...
    class FaceEffectItem(_message.Message):
        __slots__ = ("effect_id", "source")
        EFFECT_ID_FIELD_NUMBER: _ClassVar[int]
        SOURCE_FIELD_NUMBER: _ClassVar[int]
        effect_id: int
        source: int
        def __init__(self, effect_id: _Optional[int] = ..., source: _Optional[int] = ...) -> None: ...
    class WealthInfo(_message.Message):
        __slots__ = ("level",)
        LEVEL_FIELD_NUMBER: _ClassVar[int]
        level: int
        def __init__(self, level: _Optional[int] = ...) -> None: ...
    UID_FIELD_NUMBER: _ClassVar[int]
    UNAME_FIELD_NUMBER: _ClassVar[int]
    FACE_FIELD_NUMBER: _ClassVar[int]
    NAME_COLOR_FIELD_NUMBER: _ClassVar[int]
    GUARD_LEVEL_FIELD_NUMBER: _ClassVar[int]
    SVGA_BLOCK_FIELD_NUMBER: _ClassVar[int]
    SEND_MASTER_FIELD_NUMBER: _ClassVar[int]
    MEDAL_INFO_FIELD_NUMBER: _ClassVar[int]
    BLIND_GIFT_FIELD_NUMBER: _ClassVar[int]
    GIFT_LIST_FIELD_NUMBER: _ClassVar[int]
    SWITCH_FIELD_NUMBER: _ClassVar[int]
    TEST_FIELD_NUMBER: _ClassVar[int]
    WEALTH_INFO_FIELD_NUMBER: _ClassVar[int]
    GROUP_MEDAL_FIELD_NUMBER: _ClassVar[int]
    SENDER_UINFO_FIELD_NUMBER: _ClassVar[int]
    uid: int
    uname: str
    face: str
    name_color: str
    guard_level: int
    svga_block: int
    send_master: SendGiftBroadcast.SendMaster
    medal_info: SendGiftBroadcast.MedalInfo
    blind_gift: SendGiftBroadcast.BlindGift
    gift_list: _containers.RepeatedCompositeFieldContainer[SendGiftBroadcast.GiftItem]
    switch: bool
    test: int
    wealth_info: SendGiftBroadcast.WealthInfo
    group_medal: GroupMedalBrief
    sender_uinfo: _user_dagw_pb2.UserInfo
    def __init__(self, uid: _Optional[int] = ..., uname: _Optional[str] = ..., face: _Optional[str] = ..., name_color: _Optional[str] = ..., guard_level: _Optional[int] = ..., svga_block: _Optional[int] = ..., send_master: _Optional[_Union[SendGiftBroadcast.SendMaster, _Mapping]] = ..., medal_info: _Optional[_Union[SendGiftBroadcast.MedalInfo, _Mapping]] = ..., blind_gift: _Optional[_Union[SendGiftBroadcast.BlindGift, _Mapping]] = ..., gift_list: _Optional[_Iterable[_Union[SendGiftBroadcast.GiftItem, _Mapping]]] = ..., switch: _Optional[bool] = ..., test: _Optional[int] = ..., wealth_info: _Optional[_Union[SendGiftBroadcast.WealthInfo, _Mapping]] = ..., group_medal: _Optional[_Union[GroupMedalBrief, _Mapping]] = ..., sender_uinfo: _Optional[_Union[_user_dagw_pb2.UserInfo, _Mapping]] = ...) -> None: ...

class GroupMedalBrief(_message.Message):
    __slots__ = ("medal_id", "name", "is_lighted")
    MEDAL_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_LIGHTED_FIELD_NUMBER: _ClassVar[int]
    medal_id: int
    name: str
    is_lighted: int
    def __init__(self, medal_id: _Optional[int] = ..., name: _Optional[str] = ..., is_lighted: _Optional[int] = ...) -> None: ...

class GiftMaterialSnapShot(_message.Message):
    __slots__ = ("img_basic", "webp", "effect_id", "has_imaged_gift")
    IMG_BASIC_FIELD_NUMBER: _ClassVar[int]
    WEBP_FIELD_NUMBER: _ClassVar[int]
    EFFECT_ID_FIELD_NUMBER: _ClassVar[int]
    HAS_IMAGED_GIFT_FIELD_NUMBER: _ClassVar[int]
    img_basic: str
    webp: str
    effect_id: int
    has_imaged_gift: int
    def __init__(self, img_basic: _Optional[str] = ..., webp: _Optional[str] = ..., effect_id: _Optional[int] = ..., has_imaged_gift: _Optional[int] = ...) -> None: ...

class GiftBenefits(_message.Message):
    __slots__ = ("easter_egg", "fans_light_animation")
    EASTER_EGG_FIELD_NUMBER: _ClassVar[int]
    FANS_LIGHT_ANIMATION_FIELD_NUMBER: _ClassVar[int]
    easter_egg: EasterEggBenefit
    fans_light_animation: FansLightAnimation
    def __init__(self, easter_egg: _Optional[_Union[EasterEggBenefit, _Mapping]] = ..., fans_light_animation: _Optional[_Union[FansLightAnimation, _Mapping]] = ...) -> None: ...

class EasterEggBenefit(_message.Message):
    __slots__ = ("material_url", "material_md5", "effect_num", "effect_num_audience", "unlock_text", "web_material_url", "web_material_md5")
    MATERIAL_URL_FIELD_NUMBER: _ClassVar[int]
    MATERIAL_MD5_FIELD_NUMBER: _ClassVar[int]
    EFFECT_NUM_FIELD_NUMBER: _ClassVar[int]
    EFFECT_NUM_AUDIENCE_FIELD_NUMBER: _ClassVar[int]
    UNLOCK_TEXT_FIELD_NUMBER: _ClassVar[int]
    WEB_MATERIAL_URL_FIELD_NUMBER: _ClassVar[int]
    WEB_MATERIAL_MD5_FIELD_NUMBER: _ClassVar[int]
    material_url: str
    material_md5: str
    effect_num: int
    effect_num_audience: int
    unlock_text: str
    web_material_url: str
    web_material_md5: str
    def __init__(self, material_url: _Optional[str] = ..., material_md5: _Optional[str] = ..., effect_num: _Optional[int] = ..., effect_num_audience: _Optional[int] = ..., unlock_text: _Optional[str] = ..., web_material_url: _Optional[str] = ..., web_material_md5: _Optional[str] = ...) -> None: ...

class FansLightAnimation(_message.Message):
    __slots__ = ("medal_name",)
    MEDAL_NAME_FIELD_NUMBER: _ClassVar[int]
    medal_name: str
    def __init__(self, medal_name: _Optional[str] = ...) -> None: ...
