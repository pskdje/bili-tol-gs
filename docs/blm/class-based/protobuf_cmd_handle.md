# protobuf_cmd_handle

文件: `cmd_pb/protobuf_cmd_handle.py`

实现 base64 protobuf 的解析。

导入该模块将会把cmd_pb模块路径给添加进模块查找路径。

## 依赖

Python:

- \>3.11
- 未测试是否可在低版本中使用

第三方库:

- protobuf

本目录:

- blw.py
- cmd_pb中的proto解析逻辑

## 接口

为节省文档维护工作量，接口的类型标注可能会省略，参见源代码获取类型标注。

### 类 `ParseProtobufPack`

解析protobuf数据包。

**继承:** `blw.BiliLiveWS`

#### 方法 `ParseProtobufPack.protobufToDict`

将protobuf数据处理为字典。

*参数* `message` : protobuf数据

*参数* `mClass` : proto解析类

**返回值:** 解析后数据，proto类型 `int64` 在解析结果可能转为Python的 `str` 类型

#### 方法 `ParseProtobufPack.decodePB`

解析pb数据。

pb数据是指使用base64编码protobuf数据后的那个字符串。

*参数* `data` : pb数据

*参数* `mClass` : proto解析类

**返回值:** 方法[protobufToDict](#方法-parseprotobufpackprotobuftodict)的返回值

#### 方法 `ParseProtobufPack.dc_INTERACT_WORD_V2`

解析 `INTERACT_WORD_V2` cmd的protobuf数据，写回data。

*参数* `p` : 数据包

#### 方法 `ParseProtobufPack.dc_ONLINE_RANK_V3`

解析 `ONLINE_RANK_V3` cmd的protobuf数据，写回data。

*参数* `p` : 数据包
