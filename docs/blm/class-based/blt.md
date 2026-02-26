# blt

文件: `blt.py`

直播工具，提供一些接口给其它组件调用。

接口均为获取数据封装，返回值若无特别备注均表示返回接口信息本体。如何处理返回信息请自行研究或者寻找文档。

本文档并不会告诉你哪些接口需要登录哪些不需要。想知道的话自己查看源代码并在其它地方如[已失效项目](https://github.com/SocialSisterYi/bilibili-API-collect)中搜索，实在看不懂那就登录吧。

## 依赖

Python:

- \>=3.13

本目录:

- blw.py
- blm.py

## 使用

本文件无法直接使用，请继承或调用接口。

## 接口

### 常量 `DEFAULT_APPkey`

默认提供的 APP key 。

### 常量 `DEFAULT_APPsec`

默认提供的 APP sec 。

### 类 `APPSign`

包装APP签名返回数据，由[appsign](#函数-appsign)函数返回。

#### 属性 `APPSign.query`

查询参数，一般已进行过URL编码。

#### 属性 `APPSign.signed_params`

查询字典，经过签名的参数字典。

#### 属性 `APPSign.sign`

签名字符串。

#### 方法 `APPSign.__init__`

初始化所有属性。

参数名与属性名相同，作用相同。不建议直接实例该对象，除非你要重写签名算法。

#### 方法 `APPSign.__str__`

返回 `query` 属性。

#### 方法 `APPSign.__repr__`

返回构造表达式。

#### 静态方法 `APPSign.app_sign`

调用 appsign 签名参数，使用默认的 APP key 和 APP sec 。

### 函数 `appsign`

进行APP查询参数签名。

代码来自 https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/misc/sign/APP.md (已失效)

*参数* `params` : 要被签名的查询参数字典

*参数* `appkey` : APP key

*参数* `appsec` : APP sec

**返回值:** [APPSign](#类-appsign)的实例

### 类 `DMColor`

存储弹幕颜色数据。

#### 属性 `DMColor.name`

颜色名称。

#### 属性 `DMColor.color`

十进制颜色值。

#### 属性 `DMColor.color_hex`

十六进制颜色值。

#### 属性 `DMColor.status`

颜色可用状态。（因登录信息而异）

#### 方法 `DMColor.__init__`

初始化所有属性。

参数名与属性名相同，作用相同。

#### 方法 `DMColor.__str__`

返回颜色值，目前为 `color_hex` 属性。

#### 方法 `DMColor.__repr__`

返回自身构造伪代码。

### 类 `LiveLink`

直播推流地址容纳，是一个具名元组。

**继承:** `typing.NamedTuple`

#### 方法 `LiveLink.__str__`

返回完整推流地址。

### 类 `ToolBase`

提供基本工具。

**继承:** `blm.BiliLiveExp`

#### 属性 `ToolBase.appkey`

类的默认 APP key ，默认值从 DEFAULT_APPkey 常量获取。

#### 属性 `ToolBase.appsec`

类的默认 APP sec ，默认值从 DEFAULT_APPsec 常量获取。

#### 方法 `ToolBase.set_cookie`

设置cookie。若输入 `None` 将清除所有已存在的cookie。

目前 `dict` 、 `http.cookiejar.CookieJar` 为设置cookie所支持的类型。

*参数* `data` : 新的cookie对象或 `None`

**返回值:** 代表操作结果的字符串

#### 方法 `ToolBase.split_kv_cookie`

从字符串获取cookie。

委托给[blw.split_kv_cookie](blw.md#函数-split_kv_cookie)解析。

*参数* `data` : 符合要求的cookie字符串

**返回值:** 解析后的cookie字典

#### 方法 `ToolBase.split_cookietxt`

处理cookie.txt格式的数据。

*参数* `data` : 文件内容

**返回值:** 解析后的cookie字典

#### 方法 `ToolBase.split_file_cookie`

处理存储在文件的cookie，需要提供[`http.cookiejar.FileCookieJar`](https://docs.python.org/zh-cn/3/library/http.cookiejar.html)的子类才能解析。

该方法将会直接更新 `cookies` 属性所指向的cookies对象。

*参数* `path` : 文件路径

*参数* `cj` : FileCookieJar子类的类对象

**返回值:** 代表操作结果的字符串

#### 方法 `ToolBase.split_biliup_cookie`

处理[biliup](https://github.com/biliup/biliup)的[cookies.json](https://github.com/biliup/biliup-rs)存储的cookie数据。

若参数输入为`Path`对象将尝试读取该路径指向的文件（异常将会传播）。

该方法将会直接更新cookies属性数据。

*参数* `data` : JSON解析后的dict数据或`Path`对象

*可能抛出异常* `TypeError` : 读取文件后的数据或原始输入数据的类型不是dict类型时抛出

#### 方法 `ToolBase.read_cookie`

读取cookie并解析。

*参数* `data` : cookie字符串或cookie文件路径

**返回值:** 解析后的cookie字典

*可能抛出异常* `ValueError` : 超过文件大小限制

#### 方法 `ToolBase.add_csrf`

为参数字典添加csrf参数。

*参数* `odic` : 要添加csrf的参数字典

**返回值:** 输入的参数字典，已添加csrf

#### 方法 `ToolBase.appsign`

进行APP签名。

若不提供 appkey 或 appsec ，将从类中读取。

*参数* `params` : 要进行APP签名的参数字典

*参数* `appkey` : APP key

*参数* `appsec` : APP sec

**返回值:** [APPSign](#类-appsign)实例

### 类 `DanmuTools`

弹幕工具。

**继承:** `ToolBase`

#### 属性 `DanmuTools.send_danmu_time`

弹幕发送时间，用于速率限制。初始值 `0` 。

#### 属性 `DanmuTools.send_danmu_lock`

发送弹幕锁，防止并发发送导致发送失败。

#### 属性 `DanmuTools.send_danmu_block`

发送弹幕分块大小，用于防止因字数限制导致发送失败。

#### 属性 `DanmuTools.dm_color`

弹幕颜色数据，由[DanmuTools.get_dm_config](#方法-danmutoolsget_dm_config)设置。

键为弹幕颜色名称，值为[DMColor](#类-dmcolor)实例。

#### 属性 `DanmuTools.dm_mode`

弹幕模式数据，由[DanmuTools.get_dm_config](#方法-danmutoolsget_dm_config)设置。

键为弹幕模式名称，值为弹幕模式。

#### 方法 `DanmuTools.on_send_danmu_start`

**事件**，开始发送弹幕，传入要发送的弹幕。

#### 方法 `DanmuTools.on_send_danmu_res`

**事件**，发送弹幕的响应，传入弹幕信息。

#### 方法 `DanmuTools.erron_send_danmu`

**错误事件**，发送弹幕失败，传入错误对象。

#### 方法 `DanmuTools.send_danmu`

发送弹幕。

*参数* `msg` : 弹幕内容

*参数* `reply_mid` : 被回复者的uid

*参数* `replay_dmid` : 要回复的弹幕id

*参数* `return_type` : 返回值类别，详见源代码的重载注解

**返回值:** 依照 `return_type` 参数决定，详见源代码的重载注解

#### 异步方法 `DanmuTools.send_msg_and_restrict`

发送弹幕并进行一些限制，将限制发送速率并视消息长度进行分割。

*参数* `msg` : 弹幕内容，若超出弹幕分块大小将进行分块

*参数* `rate_limit` : 是否启用基于发送时间的速率限制，触发限制将丢弃弹幕

*剩余位置参数* `an` : 其它传递给send_danmu函数的参数

*剩余关键字参数* `ad` : 其它传递给send_danmu函数的参数

**返回值:** 错误提示，成功时为 `None`

#### 方法 `DanmuTools.send_msg`

创建异步发送弹幕任务。

*参数* `msg` : 弹幕内容

*剩余位置参数* `an` : 其它传递给send_msg_and_restrict函数的参数

*剩余关键字参数* `ad` : 其它传递给send_msg_and_restrict函数的参数

**返回值:** 异步任务对象

#### 方法 `DanmuTools.get_dm_config`

获取当前直播间弹幕可选配置。

读取 `roomid` 属性。

设置 `dm_color` 、 `dm_mode` 属性。

#### 方法 `DanmuTools.set_dm_config`

设置当前直播间的弹幕配置。

参数color和mode必须选一个提供，并且不能同时存在。

读取 `roomid` 属性。

*参数* `color` : 十六进制颜色值，从[DanmuTools.get_dm_config](#方法-danmutoolsget_dm_config)获取可用值

*参数* `mode` 弹幕模式，从[DanmuTools.get_dm_config](#方法-danmutoolsget_dm_config)获取可用值

#### 方法 `DanmuTools.get_dm_history`

获取历史弹幕。

读取 `roomid` 属性。

### 类 `SpectatorTools`

观众操作。

**继承:** `ToolBase`

#### 方法 `SpectatorTools.getInfoByUser`

获取用户在某个直播间的状态信息，此接口将会使服务器下发进入直播间信息。

此方法还会设置弹幕分块长度。

### 类 `LiveTools`

开关播工具。

调用开播接口获取推流信息进行推流，要下播时记得调用关播接口。

**继承:** `ToolBase`

#### 方法 `LiveTools.startLive`

开始直播。

<docs-warn>该接口目前只能使用<code>"pc_link"</code>直播平台，使用其它开播平台大概率报错。缺失手机端开播参数信息。</docs-warn>

根据开播账号和各种使用情况来填写参数，具体看它要不要给你通过。

读取 `roomid` 属性。

*参数* `area` : 直播分区id

*参数* `platform` : 直播平台

*参数* `build` : 直播姬构建编号

*参数* `version` : 直播姬版本号

*参数* `buvid` : 直播姬buvid

*参数* `return_type` : 返回数据类别，详见源代码

**返回值:** 依照 `return_type` 参数决定，详见源代码

#### 方法 `LiveTools.stopLive`

停止直播。

读取 `roomid` 属性。

*参数* `platform` : 直播平台

### 类 `LiveDataTools`

直播数据工具。

**继承:** `ToolBase`

#### 方法 `LiveDataTools.stopLiveData`

获取停止直播场次的数据。

若提供live_key将使用这个key，否则从self.live_key读取。

若还是没有将抛出错误，由getattr抛出。

*参数* `live_key` : 标记直播场次的key

### 类 `RoomTools`

直播间管理。

**继承:** `ToolBase`

#### 方法 `RoomTools.room_update`

更新直播间信息。

除了 `add_tag` 和 `del_tag` 参数互斥（准确来说是部分不生效），其它参数均可同时存在。

*参数* `title` : 直播标题

*参数* `area` : 直播分区

*参数* `add_tag` : 要添加的标签

*参数* `del_tag` : 要删除的标签

#### 方法 `RoomTools.updatePreLiveInfo`

预更新直播信息。

*参数* `cover` : 直播封面URL，必须为ac站图片CDN(hdslb.com)

*参数* `title` : 直播标题

*关键字参数* `platform` : 直播平台

### 类 `LiveReplay`

直播回放相关接口。

**继承:** `ToolBase`

#### 方法 `LiveReplay.get_replay_list`

获取回放列表。

*参数* `page` : 页码

*参数* `page_size` : 页面内容数量

#### 方法 `LiveReplay.get_video_slice_list`

获取已发布片段列表。

*参数* `page` : 页码

*参数* `page_size` : 页面内容数量

#### 方法 `LiveReplay.get_draft_list`

获取草稿列表。

*参数* `page` : 页码

*参数* `page_size` : 页面内容数量

#### 方法 `LiveReplay.delete_slice_draft`

删除某个草稿。

*参数* `draft_id` : 草稿id

#### 方法 `LiveReplay.get_slice_stream`

获取切片视频流。

*参数* `live_key` : 标记直播场次的key

*参数* `start_time` : 起始时间戳

*参数* `end_time` : 结束时间戳

#### 方法 `LiveReplay.get_live_session_data`

获取直播会话数据。

参数 `start_tm` 和 `end_tm` 的取值对实际无影响，格式为 `年 + "-" + 月 + "-" + 日 + "+" + 时 + ":" + 分 + ":" + 秒` 。由于是直接拼接在查询参数上，实际上是长这样 `2000-01-01 08:00:00` （记得按照格式传递，不要用实际）。

*参数* `live_key` : 标记直播场次的key

*参数* `start_tm` : 开始时间

*参数* `end_tm` : 结束时间

#### 方法 `LiveReplay.publish_video_slice`

发布回放片段

从av_title参数开始，建议使用关键字参数

*参数* `live_key` : 标记直播场次的key

*参数* `start_ts` : 片段起始时间戳

*参数* `end_time` : 片段结束时间戳

*参数* `av_title` : 视频标题

*参数* `av_cover` : 视频封面，必须为ac站图片CDN(hdslb.com)

*参数* `av_highlight` : 高光绑定

*参数* `with_subtitle` : 是否携带字幕

*参数* `with_danmaku` : 是否携带弹幕

*参数* `with_reserve` : 是否携带下场直播提醒

*参数* `av_speed` : 使用倍速投稿，格式 `速率 + "x"`

### 类 `LiveVote`

直播投票。

**继承:** `ToolBase`

#### 方法 `LiveVote.live_votePanel`

查询直播投票信息。

读取 `roomid` 属性。

#### 方法 `LiveVote.live_voteHistory`

查询直播投票历史。

读取 `roomid` 属性。

#### 方法 `LiveVote.live_createVote`

创建直播投票。

*参数* `duration` : 投票持续时长(单位:分钟)

*参数* `question` : 投票问题

*参数* `options_a` : 投票选项a

*参数* `options_b` : 投票选项b

*参数* `template_id` : 投票模板id

#### 方法 `LiveVote.live_terminateVote`

中断直播投票。

读取 `roomid` 属性。

*参数* `vote_id` : 投票互动id

### 类 `BiliLiveTools`

本模块提供的全部工具集合。

**继承:** 所有工具类
