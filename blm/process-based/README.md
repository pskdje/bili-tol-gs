# 基于流程的 bili live ws danmu

这是基于流程的blm项目，因为维护难度和其它原因现已弃用，请改为其它类型的blm项目。

这个项目将消极的更新。除了漏洞修复，不会刻意进行更新。

## 文件

### [bili_live_ws.py]

直播信息流

**仅实现核心功能**

> 需要依赖: `requests` , `websockets`

> 可选依赖: `brotli`

具体的选项请输入 `-h` 或 `--help` 来查看帮助。部分信息也可以查看[bili_live_ws.md](bili_live_ws.md)。

一些异常并未进行捕捉，遇到解释器打印异常时，请不用惊慌，这是正常现象。因为该程序并未考虑用户交互，也不完善。

如果存在cmd_handle.py文件，将会自动导入。但如果本文件不是**顶层代码环境**，默认提供的color_cmd_handle.py可能会出现异常，需要注意顶层代码环境的变量。

2023/10/05**增**: 现在需要登录才能获得用户昵称，所以增加了 `--sessdata` 和 `--uid` 参数。
当 `--sessdata` 存在时必须使用 `--uid` 参数，否则连接将被关闭。
使用某个UID登录后获取的SESSDATA拿到这里使用时必须正确填写这个UID，否则连接将关闭。

参数 `--sessdata` 支持直接输入SESSDATA和从文件中读取两种方式。

```shell
python bili_live_ws.py -h
```

注: 实际使用可能出现一些shell命令调用，并且使用的是无效命令。此情况很可能是本人将自用的文件直接复制过来。遇到此情况可打开issue来通知，但不保证会进行修正。

**非BUG相关请开讨论！**

### [bili_live_msg.py]

在 bili_live_ws.py 的基础上增加了信息获取。

> 需要依赖: `requests` 

> **bili_live_ws.py 要在同一个目录下** 

> 还要保证 bili_live_ws.py 的依赖有处理好

如果文件夹内同时存在cmd_handle.py文件，需要处理好命名空间。

### [color_cmd_handle.py]

从bili_live_ws.py中分离出的命令处理。

将本文件重命名为cmd_handle.py即可在部分shell享受到额外的着色。

如果bili_live_ws.py不是顶层代码环境，则需要保证顶层代码环境存在需要的变量。

> 技术细节：因为必要的变量是从`__main__`导入的。而bili_live_ws.py不为顶层代码环境时，再导入这个名称会导致引用问题。

也许还能实现更强大的功能。

## [bili_live_tool.py]

开播组件。
