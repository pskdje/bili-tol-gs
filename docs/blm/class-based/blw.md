# blw

文件: `blw.py`

直播信息流主程序。

仅有基本的认证鉴权，没有cmd处理实现。请继承`BiliLiveWS`类并进行扩展，详见[编写指引](#编写指引)。

## 依赖

Python:

- \>3.11
- 未测试是否可在低版本中使用

第三方库:

- `requests`
- `websockets`
- `brotli` (建议)

## 使用

文件允许直接在命令行中启动，但建议使用其它文件如`main.py`启动以获得更多功能。

```shell
python blw.py 23058
```

可使用 `-h` 或 `--help` 获取基本命令行参数。

注：若通过本文件启动，直播间ID必须提供真实ID。

## 编写指引

无论你想要基于此文件实现什么功能，都必须导入本文件，或者其它基于本文件的扩展。

编写指引部分提到“重写”都是指你通过继承 `BiliLiveWS` 后的那个类。

- 若想要添加其它命令行参数，可通过重写 `other_arg_add` 方法，blm.py也有提供其它方案。
- 若要处理某个cmd，请按照 `"l_" + pack["data"]` 的命名规则来添加方法。
  - 示例：

```python
class cmd处理示例(blw.BiliLiveWS):# 继承基本组件
  def l_DANMU_MSG(self,pack):# 添加弹幕cmd处理
    self.pct("弹幕",pack["info"][1])# 打印弹幕内容
```

- 通过重写 `start` 方法，可以自定义启动逻辑。但请注意，重写启动逻辑时建议进行：
  - 调用 `pararg` 获取命令行参数
  - 设置 `cookies` 属性
  - 调用 `get_login_nav` 获取wbi信息，登录时还会设置uid
  - 必须调用 `get_ws_info` 获取信息流地址
  - 调用 `run_blw_client` 运行信息流客户端
    - 调用后将会阻塞于此，直到信息流客户端退出
  - 调用 `print_cmd_count` 在特定参数下打印计数

## 接口

为节省文档维护工作量，接口的类型标注可能会省略，参见源代码获取类型标注。

### 常量 `__version__`

版本标识，随缘更新，**不作为版本指示**。

### 变量 `DEBUG`

指定是否启用调试模式，部分逻辑会修改该变量。

会由以下情况自动启动调试模式：

- `sys.flags.debug` 计算为 `True`
- `sys.flags.dev_mode` 计算为 `True`

可通过修改源代码将自动启动调试模式的第一个判断改为 `True` 来阻止。

### 常量 `TIMEFORMAT`

用于时间格式化。

### 常量 `UA`

默认的用户代理字符串。

### 常量 `VERSIONINFO`

记录Python和依赖的版本信息。

### 常量 `LOGDIRPATH`

日志目录。

### 常量 `ENCODING`

指定大部分运行文件保存编码。

### 常量 `starttime`

启动时间，不要修改。

### 变量 `log`

日志记录。

### 变量 `cumulative_error_count`

累计错误数量。由 `error` 函数修改。

### 常量 `wbi_mixinKeyEncTab`

wbi重排映射表。

### 函数 `error`

记录错误数据，保存在 `bili_live_ws_err` 目录。

若无法保存错误信息将会在控制台打印异常堆栈。

处于调试模式时打印错误信息存储路径。

*参数* `v` : 额外的变量列表

*参数* `d` : 额外信息

### 函数 `pr`

打印并返回输入的值。用于调试。

*参数* `d` : 要打印并返回的内容

### 函数 `bst`

将字节串处理成16进制内容的字符串。

*参数* `b` : 要被处理的字节串

*参数* `sep` : 指定字节之间的分隔(默认值: `" "` )

### 函数 `res_log`

*参数* `res` : requests库的响应对象或类似格式的对象

*参数* `stacklevel` : 日志内要跳过的堆栈数，不可少于2(默认值: `2` )

### 异常 `BLWException`

直播信息流根异常。

**继承:** `Exception`

### 异常 `DataError`

数据因为某些原因出现错误或不符合条件时抛出。

若某些情况可用内置异常表示的话最好还是抛出内置异常。

**继承:** `BLWException`

#### 属性 `DataError.datas`

构造函数的所有关键字字典，由__init__初始化。

#### 方法 `DataError.__init__`

记录数据异常，将所有位置参数传递给基类的初始化函数，将所有关键字参数保存到 `datas` 属性。

*剩余位置参数* `args` : 异常提示信息

**剩余关键字参数* `kw` : 其它信息

### 异常 `GetDataError`

获取数据时出现的错误，包括网络错误和无效数据。

**继承:** `DataError`

### 异常 `WSClientError`

blw ws 客户端异常。

**继承:** `BLWException`

### 异常 `SavePack`

保存数据包。

在数据包处理时抛出该异常，表示需要保存该数据包。

**继承:** `BLWException`

### 函数 `from_list_add_args`

从列表添加命令行选项。

*参数* `argobj` : 参数解析对象

*参数* `arg_list` : 一个或多个参数解析方法的列表

**返回值:** 一个添加成功的参数名称列表

#### 参数解析方法字典

*参数* `arg_list` 列表中的那个字典。

键名称均为 `argparse.ArgumentParser.add_argument` 方法可接受的参数。

*键* `name` : 必须，指定参数名称，若不以 `--` 开头，最终添加的参数将会在开头加上 `--` 。

允许的键: `help`,`action`,`nargs`,`const`,`default`,`type`,`choices`,`required`,`metavar`,`dest`

### 函数 `split_kv_cookie`

分割键值对的cookie信息。

输入格式类似为 “key1=value1;key=value2” 的cookie文本，常见于 WebAPI document.cookie 和 Cookie 请求头。

若输入的数据格式错误可能会导致出现赋值异常。

*参数* `data` : 要分割的cookie文本

**返回值:** 一个格式为 `{"key1":"value1","key2":"value2"}` 的字典。

### 函数 `bilipack`

返回要发送的数据包。

*参数* `op` : 操作码

*参数* `data` : 数据包内容

*参数* `seq` : 每次递增

**返回值:** 一个数据包字节串

### 函数 `savepack`

保存数据包，保存在 `bili_live_ws_pack` 目录。

*参数* `d` : 数据包内容

### 函数 `wbi_getMixinKey`

对 imgKey + subKey 的字符串顺序打乱编码，详见[wbi_encode函数](#函数-wbi_encode)的说明。

*参数* `orig` : `imgKey + subKey` 后的字符串

**返回值:** 打乱重排后的字符串

### 函数 `wbi_encode`

为请求参数进行 wbi 签名。

代码来自 https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/misc/sign/wbi.md

*参数* `params` : 要被签名的参数字典

*参数* `imgKey` : imgKey

*参数* `subKey` : subKey

**返回值:** 使用 `argparse.Namespace` 包装的数据。

*属性* `query` : 签名后编码的URL查询参数

*属性* `signed_params` : 签名后的参数字典

*属性* `curr_time` : 签名时间

### 类 `LiveMsgProto`

信息流数据包映射。是一个具名元组。

*属性* `length` (0) : 数据包总长度

*属性* `headerLength` (1) : 头部长度

*属性* `ver` (2) : 协议版本

*属性* `op` (3) : 操作码

*属性* `seq` (4): 每次递增

*属性* `body` (5) : 正文

#### 类方法 `LiveMsgProto.unpack`

解析服务器下发的数据包。

*参数* `pk` : 原始数据包字节串

**返回值:** 类自身的实例

### 类 `ArgsParser`

参数解析，覆盖部分默认行为。

#### 方法 `convert_arg_line_to_args`

处理一行参数。

支持使用 `#` 注释。

注：查argparse模块的源代码可得知，本方法需要参数输入一行文件，返回可迭代对象。

### 类 `CookiesAgent`

代理从参数输入的Cookie信息。

支持 `__len__` 、 `__getitem__` 、 `__iter__` 、 `__contains__` 、 `key` 字典操作。

更多操作请访问 `cookies` 属性。

#### 方法 `CookiesAgent.__init__`

初始化Cookie信息代理。

*参数* `cookies` : cookie字典

若输入的不是字典，将抛出 `TypeError` 错误。

#### 方法 `CookiesAgent.__repr__`

给出不清晰的Cookie信息。

#### 属性 `cookies`

在初始化类时输入的cookie字典。

### 类 `MsgWSInfo`

直播信息流的地址信息容纳。

#### 方法 `MsgWSInfo.__init__`

初始化信息流的地址信息容纳。

*参数* `token` : 信息流认证Token

*参数* `wss_host` : 加密的WS服务器地址

*关键字参数* `data` : 可选，原始响应

*关键字参数* `other` : 可选，其它信息

#### 方法 `MsgWSInfo.__repr__`

返回token信息。

#### 方法 `MsgWSInfo.__getitem__`

获取实例的属性，主要用于向下兼容。

#### 方法 `MsgWSInfo.__setitem__`

设置实例的属性，主要用于向下兼容。

#### 方法 `MsgWSInfo.__contains__`

实现in操作符。

### 类 `BiliLiveWS`

直播信息流主程序框架。

#### 常量 `BiliLiveWS.UA`

类用户代理常量，默认值来自[常量UA](#常量-ua)。

#### 属性 `BiliLiveWS.sequence`

数据包递增，初始值 `0` ，由[create_pack](#方法-bililivewscreate_pack)递增。

#### 属性 `BiliLiveWS.roomid`

直播间ID，初始值 `0` ，默认值由[pararg](#方法-bililivewspararg)设置。

#### 属性 `BiliLiveWS.uid`

登录用户的UID，初始值 `0` ，由[get_uid](#方法-bililivewsget_uid)或[get_login_nav](#方法-bililivewsget_login_nav)设置，也可自行设置。

#### 属性 `BiliLiveWS.hpst`

循环发送心跳包任务暂存，初始值 `None` ，由[ws_client](#异步方法-bililivewsws_client)设置。

#### 属性 `BiliLiveWS.args`

命令行参数存储，初始值 `None` ，由[pararg](#方法-bililivewspararg)设置。

#### 属性 `BiliLiveWS.no_run_enable_cmd`

不运行不支持某个cmd的回退操作，默认值 `False` ，由[pac_cmd_call](#方法-bililivewspac_cmd_call)使用。

设置为 `True` 将取消cmd的回退操作。

#### 属性 `BiliLiveWS.cmd_args`

添加给cmd处理使用的命令行参数，决定要关闭哪个cmd的处理，实际由子类决定，初始值 `[]` ，由[build_argparser](#方法-bililivewsbuild_argparser)使用。

#### 属性 `BiliLiveWS.only_count_cmd`

只计数cmd的列表，初始值 `[]` 。

#### 属性 `BiliLiveWS.save_cmd`

要被保存的cmd列表，由__init__初始化为 `[]` 。

#### 属性 `BiliLiveWS.count_cmd`

要被计数的cmd列表，由__init__初始化为 `[]` 。

#### 属性 `BiliLiveWS.pack_count`

cmd计数容纳，由__init__初始化为 `[]` 。

#### 属性 `BiliLiveWS.headers`

HTTP请求头容纳，由__init__初始化为携带2个请求头的字典。

#### 属性 `BiliLiveWS.cookies`

Cookie容纳，由__init__初始化为 `{}` 。

#### 属性 `BiliLiveWS.wbi_imgKey`

wbi 的 imgKey ，由[get_login_nav](#方法-bililivewsget_login_nav)设置。

#### 属性 `BiliLiveWS.wbi_subKey`

wbi 的 subKey ，由[get_login_nav](#方法-bililivewsget_login_nav)设置。

#### 属性 `BiliLiveWS.debug`

只读，返回blw的全局调试状态。

#### 方法 `BiliLiveWS.__init__`

初始化blw的一些必要变量。

#### 方法 `BiliLiveWS.__repr__`

返回对象概述，有类名、roomid、uid。

#### 方法 `BiliLiveWS.error`

调用[error函数](#函数-error)记录异常，附带该类的部分变量。

可通过剩余参数扩展变量列表。

*参数* `d` : 额外信息

*剩余关键字参数* `v` : 其它要被记录的变量

#### 方法 `BiliLiveWS.p`

输出文本。

*剩余位置参数* `t` : 传递给`print`的内容

#### 方法 `BiliLiveWS.pct`

统一按照一定样式输出cmd处理后文本，然后由[p](#方法-bililivewsp)输出。

*参数* `name` : 类别名称，输出时会放在 `[]` 内

*剩余位置参数* `data` : 其它信息

#### 方法 `BiliLiveWS.on_conn_ws_server`

**事件**，服务器连接开始。

#### 方法 `BiliLiveWS.on_conn_ws_server_ok`

**事件**，服务器连接完成。

#### 方法 `BiliLiveWS.on_live_msg_init_ok`

**事件**，信息流初始化信息发送完成。

#### 方法 `BiliLiveWS.on_cert_pack_reply`

**事件**，认证包回复，传入数据包内容。

#### 方法 `BiliLiveWS.on_no_packlist`

**事件**，数据包处理没有信息。

#### 方法 `BiliLiveWS.on_no_support_cmd_tip`

**事件**，不支持某个cmd的提示，传入cmd名称。

#### 方法 `BiliLiveWS.erron_split_pack`

**错误事件**，分割数据包时出现错误的提示信息，将传入原始字节串。

#### 方法 `BiliLiveWS.get_rest_data`

获取API数据，任意发送数据参数不为None时将使用POST请求

*参数* `tip` : 操作提示，用于生成错误和日志

*参数* `url` : 要请求的URL

*参数* `data` : 要发送的数据，类型urlencode或其它（需自定义请求头的内容类型）

*参数* `json` : 要发送的数据，类型JSON

*参数* `headers` : 本次请求要合并一起使用的请求头，通过拷贝[headers](#属性-bililivewsheaders)属性后合并得出要使用的请求头

*参数* `cookies` : 本次请求要合并一起使用的cookie，通过拷贝[cookies](#属性-bililivewscookies)属性后合并得出要使用的cookie

*参数* `err_code_raise` : 若为真值，响应内容的code不为0时将抛出错误，最好使用位置参数传递。

**返回值:** 经过json解析后的响应内容

**异常:** `TypeError` , `KeyboardInterrupt` , `DataError` , `GetDataError`

当抛出 `DataError` 时，将保留当前合并操作的headers和cookies

当抛出 `GetDataError` 时，将保留一些可供程序读取的请求状态参数：

| 属性 | 在哪个type存在 | 描述 | 备注 |
| ---- | ---- | ---- | ---- |
| type | 所有 | 提示异常源 | 部分异常源可能除了 `type` 属性就无其它属性 |
| status_code | `response` | 响应状态码 |  |
| text | `json` | json解析失败的原始文本 |  |
| code | `api` | REST API的code值 | 通常为非 `0` 值（若为0通常不会抛出错误） |
| message | `api` | 错误提示 | 提示的详细程度取决于服务器 |

注意：这些状态参数并不详细，想要详细信息请[启用日志](#函数-set_log)或者尝试复现错误。

#### 方法 `BiliLiveWS.wbi_encode`

为请求参数进行 wbi 签名， `imgKey` 和 `subKey` 分别从实例的 `wbi_imgKey` 和 `wbi_subKey` 读取。

详见[同名模块级函数](#函数-wbi_encode)的说明。

注意： `wbi_imgKey` 和 `wbi_subKey` 不存在初始值，也不被初始化。也就是说，当你初始化实例后是无法读取这两个属性。

*参数* `params` : 要被签名的参数字典

*可能抛出异常* `AttributeError` : 当 `wbi_imgKey` 或 `wbi_subKey` 不存在时由解释器引发。

#### 方法 `BiliLiveWS.from_list_add_args`

不要使用该函数，请调用[blw对应名称的函数](#函数-from_list_add_args)。暂无弃用计划。

#### 方法 `BiliLiveWS.get_Cookie`

获取Cookie数据。

若存在名为 `read_cookie` 的方法，将委托该方法来处理cookie数据。

自身内置了一些简单的cookie处理逻辑。

主要是提供给 argparse.ArgumentParser.add_argument 的 type 参数使用。

*参数* `s` : 一个cookie字符串或指向cookie文件的字符串

**返回值:** 一个 `CookiesAgent` 代理对象或 `None` 。

*可能抛出异常* `ValueError` : 表示内容解析失败

#### 方法 `BiliLiveWS.build_argparser`

构造命令行参数解析。

将会添加一些模块所需的参数；并添加关闭某个cmd的显示的参数（需自行实现）。

将从 `cmd_args` 属性读取，并委托 `from_list_add_args` 添加到“关闭某个cmd的显示”组中。（blm.py有方便创建cmd_args的函数）

*参数* `desc` : 放在前面的描述

*参数* `epil` : 放在后面的说明

**返回值:** `ArgsParser` 实例

#### 方法 `BiliLiveWS.other_arg_add`

当 pararg 执行时会额外调用该函数，重写该方法来添加额外的命令行解析。

默认无实现。

#### 方法 `BiliLiveWS.pararg`

分析命令行数据。

可以提供参数列表让它解析该列表而不是从命令行参数读取。可用于调试或某些特殊目的。

此方法将会在 `-d` 或 `--debug` 参数存在且 `DEBUG` 变量为 `False` 时修改 `DEBUG` 为 `True` ，若已经处于调试模式，将不做修改。

此方法将会修改 `args` 、 `roomid` 、 `save_cmd` 、 `count_cmd` 属性。

*参数* `args` : 使用参数列表解析

**返回值:** 参数解析结果 argparse.Namespace 实例

#### 方法 `BiliLiveWS.get_uid`

获取登录会话对应的uid。

需要提前于属性 `cookies` 字典内填入 `SESSDATA` 键。

若需要登录信息流则必须调用此接口获取uid，或者自行提供uid填入 `uid` 属性。

**返回值:** 登录会话信息的uid

#### 方法 `BiliLiveWS.get_login_nav`

获取nav信息。若只需 wbi 信息，无需登录。

因为获取信息流地址出现需要 wbi 签名的情况，所以给它加了设置 uid 变量的功能。

**返回值:** 解析过的原始响应数据

#### 方法 `BiliLiveWS.get_ws_info`

获取信息流地址，直播间ID从 `roomid` 属性读取。

子类的实现应返回MsgWSInfo类。

**返回值:** 信息流地址数据

#### 方法 `BiliLiveWS.create_pack`

创建数据包。

对 `sequence` 属性自增，然后调用 `bilipack` 函数创建数据包。

*参数* `op` : 操作码

*参数* `data` : 数据包内容

**返回值:** 数据包字节串

#### 方法 `BiliLiveWS.join_room_pack`

创建加入直播间数据包。

*参数* `token` : 信息流认证token

*参数* `uid` : 用户uid

**返回值:** 加入直播间用的数据包

#### 方法 `BiliLiveWS.create_heartbeat`

创建心跳包。

**返回值:** 直播间心跳包

#### 异步方法 `BiliLiveWS.loop_send_hp`

循环发送心跳包。

用于ws_client方法创建一个循环发送心跳包的任务。

*参数* `ws` : WebSockets客户端会话实例

若出现非正常关闭的异常将记录错误。

#### 方法 `BiliLiveWS.compute_popularity`

从心跳包回复计算人气值。

*参数* `data` : 存有人气值的字节串，长度为4字节，传递多余的数据将会导致计算错误。

**返回值:** 计算出的人气值

#### 方法 `BiliLiveWS.print_popularity`

打印人气值。

*参数* `data` : 存有人气值的字节串，同 `BiliLiveWS.compute_popularity` 的要求。

**返回值:** 人气值

#### 方法 `BiliLiveWS.split_datapack`

分割压缩数据包的内容。

分割算法处于能跑就行的状态。

*参数* `msg` : 需要分割的数据包

**返回值:** 经过分割并解析的数据列表，若数据包无内容将返回 `None`

#### 方法 `BiliLiveWS.cmd_count_add`

添加某个cmd的计数。

*参数* `cmd` : 数据包的cmd

**返回值:** 无( `None` )

#### 方法 `BiliLiveWS.print_cmd_count`

打印数据包计数。

**返回值:** `pack_count` 属性

#### 方法 `BiliLiveWS.pac_cmd_call`

查找cmd对应的处理函数。

将会读取 `save_cmd` 、 `count_cmd` 、 `only_count_cmd` 并执行对应操作。

cmd处理函数应按照 `"l_" + cmd` 来命名，区分大小写。若存在特殊字符可考虑实现 `__getattr__` 方法来处理。

当找到cmd对应的处理函数时将调用该函数处理cmd，传递一个数据包参数。数据包为 `pack` 参数输入的内容。

若未找到cmd对应的处理函数将执行未支持的操作，可使用 `no_run_enable_cmd` 属性取消该回退操作。

使用 `--no-print-enable` 命令行参数来关闭不支持信息的打印。属于回退操作。

使用 `--save-unknow-datapack` 命令行参数来保存未实现的cmd处理。属于回退操作。

详见源代码。

*参数* `pack` : 数据包内容

**返回值:** 无( `None` )

#### 方法 `BiliLiveWS.for_packlist`

循环遍历数据包列表给后续函数。

*参数* `packlist` : 数据包列表

**返回值:** 无( `None` )

*可能抛出异常* `WSClientError` : 处理数据包时出现异常

#### 异步方法 `BiliLiveWS.ws_client`

直播信息流ws客户端，拥有连接、认证、心跳包发送、数据包分类、基础处理功能，详见源代码。

连接完成认证包发送后，将创建[重复发送心跳包](#异步方法-bililivewsloop_send_hp)任务，引用保存在[hpst](#属性-bililivewshpst)属性。

若想退出，可按下中断键引发中断键按下异常退出。若是通过asyncio任务启动，可通过调用任务的cancel关闭。若通过其它方法启动请自行研究如何退出。

*参数* `url` : WS链接

*参数* `token` : 信息流认证token

**返回值:** 不存在

#### 方法 `BiliLiveWS.close_hpst`

关闭重复发送心跳包任务。

若 hpst 属性不为 `None` 将调用它的 cancel 方法，然后重置属性为 `None` 。

*参数* `msg` : 传递给 cancel 方法的信息

**返回值:** 无( `None` )

#### 方法 `BiliLiveWS.run_blw_client`

运行ws客户端。

该方法将使用 `asyncio.run` 启动[`ws_client`](#异步方法-bililivewsws_client)。

将大部分异常封装为 `WSClientError` 并抛出，同时记录原始错误信息。

*参数* `host` : 直播信息流的域名和端口

*参数* `token` : 信息流认证token

**返回值:** 不存在

*可能抛出异常* `WSClientError` : 表示WS客户端出现错误

#### 方法 `BiliLiveWS.start`

一般启动函数，只有简单的启动行为。

查看源代码以了解如何启动。

### 函数 `create_log_handle`

创建日志保存处理。

由此函数创建的日志保存处理都存储在 `LOGDIRPATH` 常量所指示的目录下。

最大文件大小 `2097152` 字节 ( `2MB` )，最多 `3` 备份，日志级别 `DEBUG` 。

*参数* `path` : 日志保存路径

**返回值:** logging.handlers.RotatingFileHandler 的实例

### 函数 `set_logpath`

检查由 `LOGDIRPATH` 常量所指示的日志路径，若不存在将自动创建。

**返回值:** `False` 日志目录已存在； `True` 日志目录已新建

### 函数 `set_log`

保存 `log` 变量的日志在 `ms.log` 文件。

### 函数 `set_wslog`

保存ws客户端日志。

### 函数 `set_reqlog`

保存请求日志(urllib3)。

### 函数 `set_asyncio_log`

保存asyncio日志。

### 函数 `save_log`

配置保存日志。

*可能抛出异常* `RuntimeError` : 不可重复配置保存日志

### 函数 `print_HTTPClient_log`

设置http.client库的调试打印，传入一个布尔值来控制是否打印响应调试(因为响应已经在其它地方有记录到日志)。

### 顶层启动逻辑

当处于顶层环境时，将直接启动 [BiliLiveWS](#类-bililivews).[start](#方法-bililivewsstart)

其它信息请查看源代码。

## 可用的参考资料

[bilibili-API-collect的直播信息流](https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/live/message_stream.md)文档（或者我的更新分支）
