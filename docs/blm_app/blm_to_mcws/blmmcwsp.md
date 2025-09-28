# blmmcwsp

文件: `blmmcwsp.py`

可以连接多个直播间并转发的程序。

上游的直播信息流将会处理为Minecraft命令数据包后转发给连接这个直播间的客户端。

## 依赖

Python:

- \>3.11
- 未测试是否可在低版本中使用

第三方库:

- websockets

blm项目:

- blw.py

文件:

- [mcws.py](https://github.com/pskdje/pskdcerepo/blob/main/files/Minecraft%E5%9F%BA%E5%B2%A9%E7%89%88WS%E6%9C%8D%E5%8A%A1%E5%99%A8%E6%A1%86%E6%9E%B6/mcws.py) ([指导页面](https://github.com/pskdje/pskdcerepo/tree/main/files/Minecraft%E5%9F%BA%E5%B2%A9%E7%89%88WS%E6%9C%8D%E5%8A%A1%E5%99%A8%E6%A1%86%E6%9E%B6))

本目录:

- mcws_cmd_handle.py

## 使用

不使用`--cookie`参数直接启动可能出现绝大部分直播间的信息不完整，例如用户名大部分不显示。

启动后可在游戏内使用 [/wsserver 命令](https://zh.minecraft.wiki/w/%E5%91%BD%E4%BB%A4/wsserver) 来连接服务器，通过URL决定加入哪个直播间。

命令格式示例： `"/connect ws://localhost:19134/" + room_id`

命令示例： `/wsserver ws://127.0.0.1:19134/6`

### 参数

`-c` 、 `--cookie` 使用提供的cookie登录信息流，所有直播间都会使用该登录信息

`-d` 、 `--debug` 启用调试模式

`-p` 、 `--port` 指定 Minecraft WebSocket 服务器监听的端口

`-a` 、 `--blm-args` 指定blm的运行参数，具体可用的参数取决于cmd处理，实际传递时会提供其它参数

### 示例

直接启动:

```shell
python blmmcwsp.py
```

使用cookie登录:

```shell
python blmmcwsp.py --cookie "SESSDATA=xxx"
# or
python blmmcwsp.py --cookie "your/path/cookie.txt"
```

指定端口:

```shell
python blmmcwsp.py --port 19134
```

使用blm运行参数:

```shell
python blmmcwsp.py --blm-args "your/path/blmarg.txt"
```

## 接口

不打算详细写该部分，具体逻辑请查看源代码。

变量 `sess_list` : 记录MCWSP会话列表，需要手动添加，只是为了统一追踪

类 `BLM` : 定制的信息流转换逻辑

类 `MCWSP` : Minecraft WebSocket 服务器实现

函数 `stop` : 当该文件为顶层启动时自动安装在 SIGINT 信号的清理函数

顶层启动逻辑: 安装 SIGINT 信号处理，启动MCWSP服务器
