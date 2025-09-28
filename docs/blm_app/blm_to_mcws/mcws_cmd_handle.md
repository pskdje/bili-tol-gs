# mcws_cmd_handle

文件: `mcws_cmd_handle.py`

允许通过Minecraft基岩版WS服务器来获取直播信息流文本。

中文 Minecraft Wiki 与基岩版WebSocket有关的页面: [教程:WebSocket](https://zh.minecraft.wiki/w/Tutorial:WebSocket)

## 依赖

Python:

- \>3.11
- 未测试是否可在低版本中使用

blm项目:

- blm.py
- cmd_pb/protobuf_cmd_handle.py

文件:

- [mcws.py](https://github.com/pskdje/pskdcerepo/blob/main/files/Minecraft%E5%9F%BA%E5%B2%A9%E7%89%88WS%E6%9C%8D%E5%8A%A1%E5%99%A8%E6%A1%86%E6%9E%B6/mcws.py) ([指导页面](https://github.com/pskdje/pskdcerepo/tree/main/files/Minecraft%E5%9F%BA%E5%B2%A9%E7%89%88WS%E6%9C%8D%E5%8A%A1%E5%99%A8%E6%A1%86%E6%9E%B6))

## 使用

本文件无法直接使用，请继承或调用接口。

若直接通过 `StartMCWS` 类启动MCWS服务器，将监听 `19134` 端口。

可通过在游戏内使用[`wsserver`](https://zh.minecraft.wiki/w/%E5%91%BD%E4%BB%A4/wsserver)命令连接服务器，示例命令：

```minecraft-commend
/connect ws://localhost:19134/
```

## 接口

为节省文档维护工作量，接口的类型标注可能会省略，参见源代码获取类型标注。

所有的cmd处理实现接口均不会在此列出。

### 颜色格式代码常量

以 `MC_` 开头的是颜色代码常量，以 `MF_` 开头的是格式代码常量。

从 `MC_0` ~ `MC_f` 为基岩版Java版通用颜色，其余为仅基岩版，请参照源代码的注释来决定。

部分格式代码只能用于Java版，请参照源代码的注释。

参见 *中文 Minecraft Wiki* 的[格式化代码](https://zh.minecraft.wiki/w/%E6%A0%BC%E5%BC%8F%E5%8C%96%E4%BB%A3%E7%A0%81)页面。

### 某种情况统一使用的颜色常量

以 `T` 开头，后面接3个字符。

一般在什么情况使用请查看源代码。

### 正则表达式常量

以 `R` 开头，后面接3个字符。

### 函数 `cuse`

渲染用户颜色，使用 `RGPL` 正则表达式，颜色 `TUSR` ，末尾自动重置。

### 类 `BLM_to_MCWS`

直播信息流到MCWS。

**继承:** `blm.BiliLiveBlackWordExp,ParseProtobufPack,mcws.MinecraftWS`

#### 属性 `BLM_to_MCWS.add_args`

添加了 `blm.BiliLiveBlackWordExp` 和 `blm.BiliLiveMsg` 的参数。

#### 属性 `BLM_to_MCWS.cmd_args`

该类的cmd参数。

#### 方法 `BLM_to_MCWS.error`

记录异常，附带该类的部分变量。

#### 方法 `BLM_to_MCWS.push_msg`

推送消息到已连接的客户端，通过调用 `broadcast_say` 方法实现。

*参数* `msg` : 要发送的消息

#### 异步方法 `BLM_to_MCWS.mcws_start`

启动MCWS服务器。

*参数* `port` : 指定监听的端口

#### 异步方法 `BLM_to_MCWS.mcws_join_event`

处理MCWS客户端加入事件。

#### 异步方法 `BLM_to_MCWS.mcws_exit_event`

处理MCWS客户端退出事件。

### 类 `StartMCWS`

自动启动MCWS，在默认端口开放。

**继承:** `BLM_to_MCWS`

#### 方法 `StartMCWS.on_cert_pack_reply`

通过认证回复事件启动MCWS服务器。
