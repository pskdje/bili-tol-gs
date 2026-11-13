from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EffectConfigItem(_message.Message):
    __slots__ = ("type", "web_svga", "horizontal_svga", "vertical_svga", "web_mp4", "web_mp4_json", "horizontal_mp4", "vertical_mp4", "id", "plan_platform", "bind_gift_ids", "web_mp4_md5", "horizontal_mp4_md5", "vertical_mp4_md5", "web_mp4_crc32", "horizontal_mp4_crc32", "vertical_mp4_crc32", "web_mp4_file_size", "horizontal_mp4_file_size", "vertical_mp4_file_size", "h265_conf")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    WEB_SVGA_FIELD_NUMBER: _ClassVar[int]
    HORIZONTAL_SVGA_FIELD_NUMBER: _ClassVar[int]
    VERTICAL_SVGA_FIELD_NUMBER: _ClassVar[int]
    WEB_MP4_FIELD_NUMBER: _ClassVar[int]
    WEB_MP4_JSON_FIELD_NUMBER: _ClassVar[int]
    HORIZONTAL_MP4_FIELD_NUMBER: _ClassVar[int]
    VERTICAL_MP4_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    PLAN_PLATFORM_FIELD_NUMBER: _ClassVar[int]
    BIND_GIFT_IDS_FIELD_NUMBER: _ClassVar[int]
    WEB_MP4_MD5_FIELD_NUMBER: _ClassVar[int]
    HORIZONTAL_MP4_MD5_FIELD_NUMBER: _ClassVar[int]
    VERTICAL_MP4_MD5_FIELD_NUMBER: _ClassVar[int]
    WEB_MP4_CRC32_FIELD_NUMBER: _ClassVar[int]
    HORIZONTAL_MP4_CRC32_FIELD_NUMBER: _ClassVar[int]
    VERTICAL_MP4_CRC32_FIELD_NUMBER: _ClassVar[int]
    WEB_MP4_FILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    HORIZONTAL_MP4_FILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    VERTICAL_MP4_FILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    H265_CONF_FIELD_NUMBER: _ClassVar[int]
    type: int
    web_svga: str
    horizontal_svga: str
    vertical_svga: str
    web_mp4: str
    web_mp4_json: str
    horizontal_mp4: str
    vertical_mp4: str
    id: int
    plan_platform: _containers.RepeatedScalarFieldContainer[int]
    bind_gift_ids: _containers.RepeatedScalarFieldContainer[int]
    web_mp4_md5: str
    horizontal_mp4_md5: str
    vertical_mp4_md5: str
    web_mp4_crc32: int
    horizontal_mp4_crc32: int
    vertical_mp4_crc32: int
    web_mp4_file_size: int
    horizontal_mp4_file_size: int
    vertical_mp4_file_size: int
    h265_conf: H265Conf
    def __init__(self, type: _Optional[int] = ..., web_svga: _Optional[str] = ..., horizontal_svga: _Optional[str] = ..., vertical_svga: _Optional[str] = ..., web_mp4: _Optional[str] = ..., web_mp4_json: _Optional[str] = ..., horizontal_mp4: _Optional[str] = ..., vertical_mp4: _Optional[str] = ..., id: _Optional[int] = ..., plan_platform: _Optional[_Iterable[int]] = ..., bind_gift_ids: _Optional[_Iterable[int]] = ..., web_mp4_md5: _Optional[str] = ..., horizontal_mp4_md5: _Optional[str] = ..., vertical_mp4_md5: _Optional[str] = ..., web_mp4_crc32: _Optional[int] = ..., horizontal_mp4_crc32: _Optional[int] = ..., vertical_mp4_crc32: _Optional[int] = ..., web_mp4_file_size: _Optional[int] = ..., horizontal_mp4_file_size: _Optional[int] = ..., vertical_mp4_file_size: _Optional[int] = ..., h265_conf: _Optional[_Union[H265Conf, _Mapping]] = ...) -> None: ...

class H265Conf(_message.Message):
    __slots__ = ("horizontal_mp4", "vertical_mp4")
    HORIZONTAL_MP4_FIELD_NUMBER: _ClassVar[int]
    VERTICAL_MP4_FIELD_NUMBER: _ClassVar[int]
    horizontal_mp4: FileConfItem
    vertical_mp4: FileConfItem
    def __init__(self, horizontal_mp4: _Optional[_Union[FileConfItem, _Mapping]] = ..., vertical_mp4: _Optional[_Union[FileConfItem, _Mapping]] = ...) -> None: ...

class FileConfItem(_message.Message):
    __slots__ = ("mp4", "mp4_md5", "mp4_json", "mp4_crc32", "mp4_file_size")
    MP4_FIELD_NUMBER: _ClassVar[int]
    MP4_MD5_FIELD_NUMBER: _ClassVar[int]
    MP4_JSON_FIELD_NUMBER: _ClassVar[int]
    MP4_CRC32_FIELD_NUMBER: _ClassVar[int]
    MP4_FILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    mp4: str
    mp4_md5: str
    mp4_json: str
    mp4_crc32: int
    mp4_file_size: int
    def __init__(self, mp4: _Optional[str] = ..., mp4_md5: _Optional[str] = ..., mp4_json: _Optional[str] = ..., mp4_crc32: _Optional[int] = ..., mp4_file_size: _Optional[int] = ...) -> None: ...
