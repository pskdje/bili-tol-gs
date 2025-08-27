# blm

文件: `blm.py`

blw的扩展，提供一些功能。

## 依赖

python:

- \>3.11
- 未测试是否可在低版本中使用

本目录:

- blw.py

## 使用

文件允许直接在命令行中启动，但建议使用其它文件如`main.py`启动以获得更多功能。

```shell
python blm.py 3
```

可使用 `-h` 或 `--help` 获取基本命令行参数。

## 编写指引

本文件在[blw](blw.md)的基础上扩展了一些功能，以节省一些麻烦。

请参照[blw的编写指引](blw.md#编写指引)来实现其它功能，查看本文件的接口文档来了解如何使用API。

本文件已继承实现了一些功能，可直接继承本文件的类来使用。

## 接口

为节省文档维护工作量，接口的类型标注可能会省略，参见源代码获取类型标注。

### 函数 `add_no_cmd_args`

为cmd_args附加cmd参数。

*参数* `cmd_args` : 被附加参数选项字典的对象

*参数* `cmd_name_list` : 一个cmd名称为键，帮助内容为值所组成的字典

**返回值:** cmd_args参数输入的列表

示例:

```python
>>> blm.add_no_cmd_args([],{
...   "SYS_MSG":"系统提示"
... })
[
  {
    "name":"--no-SYS_MSG",
    "help":"关闭系统提示信息",
    "action":"store_true"
  }
]
```

### 生成器 `read_text_continue_h`

读取文件，并在读取过程中忽略 `#` 开头的文本。

若读取的行数量超过 `65535` 将会立刻停止迭代。

*参数* `path` : 文件路径

**迭代返回:** 一行文本

### 类 `SaveToFile`

保存到文件，用于在 print 之类直接写入到文件的地方对写入的内容做点处理。

#### 属性 `SaveToFile.file`

文件引用，由__init__初始化为文件对象。

#### 属性 `SaveToFile.temp`

用于临时存储一行内容，由__init__初始化为 `""` 。

#### 属性 `SaveToFile.closed`

只读，获取关联文件的关闭状态。

#### 方法 `SaveToFile.__init__`

初始化，打开文件存储在 `file` 属性。

#### 方法 `SaveToFile.__del__`

删除变量引用时关闭文件，通过调用[close](#方法-savetofileclose)方法实现。

#### 方法 `SaveToFile.__enter__`

返回自身给上下文管理器。

#### 方法 `SaveToFile.__exit__`

上下文管理器退出时关闭文件，通过调用[close](#方法-savetofileclose)方法实现。

#### 方法 `SaveToFile.close`

关闭关联的文件，并清除行缓冲。

#### 方法 `SaveToFile.flush`

刷新关联文件的写入缓冲区。

#### 方法 `SaveToFile.format`

处理字符串，默认直接返回。

#### 方法 `SaveToFile.write`

写入文件，调用[format](#方法-savetofileformat)处理字符串。

输入的内容将会先写入行缓冲 `temp` 属性。若末尾不为 `\r` 或 `\n` ，将返回输入内容的长度；若末尾为前述的符号或行缓冲字符数大于等于 `8192` ，将调用 `format` 方法处理缓冲字符串并清空行缓冲，然后写入到文件并返回写入长度。

`format` 方法必须返回字符串，否则内容将会被丢弃。

### 类 `BiliLiveExp`

直播信息流一般基本扩展。

**继承:** `blw.BiliLiveWS`

#### 属性 `BiliLiveExp.add_args`

添加其它命令行参数，初始值 `[]` 。

#### 属性 `BiliLiveExp.up_uid`

主播UID，初始值 `-65536` 。

#### 方法 `BiliLiveExp.error`

调用基类的[error方法](blw.md#方法-bililivewserror)记录异常，附带该类的部分变量。

#### 方法 `BiliLiveExp.other_arg_add`

添加其它命令行参数

从 add_args 属性读取数据来添加。

由 [`blw.from_list_add_args`](blw.md#函数-from_list_add_args) 添加参数。

若某个字典的键 `type` == `"group"` 且键 `list` 大于 `0` 将会创建参数组，以键 `title` 为标题，键 `desc` 为介绍（可选），由 `blw.from_list_add_args` 添加参数。

#### 方法 `BiliLiveExp.get_room_init`

获取直播间初始化信息。

若需要主播uid或者将短号转为原始房间号必须调用。

从 `roomid` 属性读取输入的直播间ID。

设置 `roomid` 属性的内容为原始直播间ID。

设置 `up_uid` 为主播UID。

**返回值:** 直播间初始化信息

#### 方法 `BiliLiveExp.get_room_info`

获取直播间信息，返回信息内容。

读取 `roomid` 属性。

#### 方法 `BiliLiveExp.get_master_info`

获取主播信息，返回信息内容。

读取 `up_uid` 属性。

#### 方法 `BiliLiveExp.get_play_url`

获取直播视频流，返回信息内容。

读取 `roomid` 属性。

#### 方法 `BiliLiveExp.print_room_info`

打印直播间信息。

#### 方法 `BiliLiveExp.print_master_info`

打印主播信息。

#### 方法 `BiliLiveExp.print_playurl`

打印直播视频流信息。

#### 方法 `BiliLiveExp.set_buvid3_4`

设置buvid3和buvid4这两个Cookie，并返回数据本体。

### 类 `BiliLiveBlackWordExp`

屏蔽词命令行参数扩展。

**继承:** `BiliLiveExp`

#### 方法 `BiliLiveBlackWordExp.from_file_handle_shielding_words`

从文件处理屏蔽词。

**返回值:** 屏蔽词列表

*可能抛出异常* `ValueError` : 读取文件失败

#### 方法 `BiliLiveBlackWordExp.from_file_handle_blocking_rules`

从文件处理屏蔽规则。

**返回值:** 屏蔽规则正则列表

*可能抛出异常* `ValueError` : 读取文件失败

#### 属性 `BiliLiveBlackWordExp.add_args`

将会添加 `--shielding-words` 和 `--blocking-rules` 命令行参数。

#### 属性 `BiliLiveBlackWordExp.swd`

只读，返回屏蔽词列表。

#### 属性 `BiliLiveBlackWordExp.brs`

只读，返回屏蔽规则列表。

#### 属性 `BiliLiveBlackWordExp.is_blocked_msg`

检查输入的信息是否命中屏蔽规则。

**返回值:** `True` 命中规则， `False` 未命中规则

### 类 `BiliLiveSaveExp`

保存打印内容扩展。

**继承:** `BiliLiveExp`

#### 属性 `BiliLiveSaveExp.add_args`

将会添加 `--save-to-file` 命令行参数。

#### 属性 `BiliLiveSaveExp.p`

输出文本并保存。

### 类 `BiliLiveMsg`

调整启动逻辑。

**继承:** `BiliLiveExp`

#### 属性 `BiliLiveMsg.add_args`

将会添加 `--no-show-room-info` 、 `--no-show-master-info` 、 `--get-room-playurl` 、 `--add-time` 命令行参数。

#### 属性 `BiliLiveMsg.pct`

统一按照一定样式输出cmd处理后文本。

额外拥有添加时间的功能。

#### 方法 `BiliLiveMsg.start`

对原始的[start方法](blw.md#方法-bililivewsstart)做了扩展，在原有基础上添加了:

- Cookie不存在 `buvid3` 时调用 set_buvid3_4
- 调用 get_room_init
- 依照参数调用 print_room_info
- 依照参数调用 print_master_info
- 依照参数调用 print_playurl
