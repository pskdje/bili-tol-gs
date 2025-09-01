# color_cmd_handle

文件: `color_cmd_handle.py`

提供命令行颜色显示工具，并处理绝大部分cmd。

## 依赖

Python:

- \>3.12
- 未测试是否可在低版本中使用

本目录:

- blw.py
- blm.py
- cmd_pb/protobuf_cmd_handle.py

若想要在Windows系统控制台中显示颜色，请自行添加 colorama 或其它可在控制台显示颜色的库。

## 使用说明

若想要在Windows系统控制台中显示颜色，请自行安装所需的库，并在源代码中添加对应的初始化代码。

示例：使用colorama库来显示颜色（示例采用diff格式）

```diff
 # 源码的其它导入逻辑
+
+import colorama
+colorama.init()
 
 # 源码的实现逻辑
```

## 接口

为节省文档维护工作量，接口的类型标注可能会省略，参见源代码获取类型标注。

所有的cmd处理实现接口均不会在此列出。

### 函数 `cbt`

生成颜色格式操作，终端需要支持ANSI编码。

*参数* `n` : 操作编码

**返回值:** `f"\33[{n}m"` 格式的字符串

### 函数 `cfc`

生成前景颜色，终端需要支持 ANSI 88/256 颜色。

*参数* `n` : 操作编码

**返回值:** `f"\33[38;5;{n}m"` 格式的字符串

### 函数 `cfb`

生成背景颜色，终端需要支持 ANSI 88/256 颜色。

*参数* `n` : 操作编码

**返回值:** `f"\33[48;5;{n}m"` 格式的字符串

### 常量 `DF`

重置全部

### 常量 `DB`

加粗

### 常量 `DD`

变暗

### 常量 `DI`

斜体

### 常量 `DU`

下划线

### 常量 `DC`

闪烁

### 常量 `EB`

重置加粗

### 常量 `ED`

重置变暗

### 常量 `EI`

重置斜体

### 常量 `EU`

重置下划线

### 常量 `EC`

重置闪烁

### 常量 `CD`

重置为默认字体颜色

### 常量 `C_00` ~ `C_07`

字体颜色：黑、红、绿、黄、蓝、品红、青、浅灰

### 常量 `C_10` ~ `C_17`

字体颜色：深灰、亮红、亮绿、亮黄、浅蓝、浅品红、亮青、白

### 常量 `BD`

重置为默认背景颜色

### 常量 `B_00` ~ `B_07`

背景颜色：黑、红、绿、黄、蓝、品红、青、浅灰

### 常量 `B_10` ~ `B_17`

背景颜色：深灰、亮红、亮绿、亮黄、浅蓝、浅品红、亮青、白

### 常量 `TRTG`

最前面的那个[]的颜色

### 常量 `TUSR`

用户名

### 常量 `TNUM`

数字、数量

### 常量 `TRMI`

房间号

### 常量 `TVER`

cmd版本标记

### 常量 `TKEY`

key

### 常量 `TSTR`

string

### 常量 `TBOL`

boolean

### 常量 `RGPL`

已编译的正则表达式，用于匹配 `<%(.+?)%>` 的内容。

### 类 `BLMColor`

带有颜色输出的框架。

**继承:** `blm.BiliLiveExp`

#### 方法 `BLMColor.cbt`

调用模块的[cbt](#函数-cbt)函数。

#### 方法 `BLMColor.cfc`

调用模块的[cfc](#函数-cfc)函数。

#### 方法 `BLMColor.cfb`

调用模块的[cfb](#函数-cfb)函数。

#### 方法 `BLMColor.cuse`

渲染用户颜色，使用[RGPL](#常量-rgpl)正则表达式，使用[TUSR](#常量-tusr)颜色。

#### 方法 `BLMColor.pct`

统一按照一定样式输出cmd处理后文本，额外拥有添加时间的功能，可用位置参数b来定义背景色(理论上)。

*参数* `name` : 输出提示名称

*剩余位置参数* `d` : 其它要输出的信息

*关键字参数* `b` : 背景色

*剩余关键字参数* `t` : 提供给print的参数

### 类 `CoreCmdHandle`

核心cmd处理。

**继承:** `BLMColor,blm.BiliLiveBlackWordExp`

#### 属性 `CoreCmdHandle.cmd_args`

该类可关闭的cmd处理。

#### 方法 `CoreCmdHandle.print_popularity`

对默认的人气值打印添加颜色。

#### 方法 `CoreCmdHandle.on_no_support_cmd_tip`

带颜色的不支持提示。

### 类 `FrequentCmdHandle`

频繁常见下发数据包的处理。

**继承:** `BLMColor,blm.BiliLiveBlackWordExp`

#### 属性 `FrequentCmdHandle.cmd_args`

该类可关闭的cmd处理。

### 类 `ConditionsFrequentCmdHandle`

特定条件时高频下发的数据包处理。

**继承:** `BLMColor`

#### 属性 `ConditionsFrequentCmdHandle.cmd_args`

该类可关闭的cmd处理。

#### 属性 `ConditionsFrequentCmdHandle.clr_dm_inter_task`

清除已过期的交互合并任务。

#### 属性 `ConditionsFrequentCmdHandle.dm_inter_list`

交互合并暂存。

字典的键为 交互合并id 。

#### 异步方法 `ConditionsFrequentCmdHandle.clr_dm_inter`

任务，清理长时间无变化的信息。

每次循环等待60秒，如果某一项的上一次更新时间与当前时间相比小于30秒，将删除该记录。

#### 方法 `ConditionsFrequentCmdHandle.dm_inter_min`

控制交互合并的打印，防止打印过于频繁。

初次调用将会创建 `clr_dm_inter` 任务。

如果某个id未记录，将记录，同时将当前计数(cnt)和当前时间记录进缓冲，然后返回 `False` 。

如果某个id输入的计数大于缓冲记录或时间大于缓冲时间，将返回 `False`

若未命中条件，将返回 `True` 。

*参数* `id` : 交互合并id

*参数* `cnt` : 交互计数

**返回值:** 是否阻止打印， `True` 阻止， `False` 不阻止

### 类 `RareCmdHandle`

低频少见特定条件的数据包处理。

**继承:** `BLMColor`

#### 属性 `RareCmdHandle.cmd_args`

该类可关闭的cmd处理。

#### 属性 `RareCmdHandle.only_count_cmd`

该类的仅计数cmd列表。

### 类 `PKCmdHandle`

PK相关数据包。

**继承:** `BLMColor`

#### 属性 `PKCmdHandle.cmd_args`

该类可关闭的cmd处理。

#### 方法 `PKCmdHandle.pk_id_status`

处理PK的id和status。

*参数* `d` : 数据包

**返回值:** 带有样式的id和status信息

### 类 `ModuleAllCmdHandle`

该模块全部cmd的集合。

**继承:** 该模块全部cmd处理类

#### 属性 `ModuleAllCmdHandle.cmd_args`

该类可关闭的cmd处理。

合并了继承的 cmd_args 参数内容。

#### 属性 `ModuleAllCmdHandle.only_count_cmd`

该类的仅计数cmd列表。

合并了继承的 only_count_cmd 参数内容。

### 类 `AllCmdHandle`

添加protobuf相关cmd的处理。

**继承:** `ModuleAllCmdHandle,ParseProtobufPack`
