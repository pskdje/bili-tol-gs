# 基于类的 bili live ws danmu

这是基于类的blm项目，因为旧程序不好维护，所以重写了全部。

## 文件

### [main.py]

基于类的blm项目的运行入口点。

需要以下的全部文件。

（你不会指望单独的main.py就能运行吧？）

### [blw.py]

主程序框架，实现了命令行参数处理和连接，cmd处理需要自行继承实现。

绝大部分接口在源码内都有注释。

### [blm.py]

主程序框架的扩展，加了一些接口和功能。

请参见注释来了解功能。

### [blt.py]

直播工具扩展，提供一些接口来做一些操作。

参见代码、注释和BAC项目来了解如何使用。

### [all_cmd_handle.py]

该项目全部已知cmd的处理。

只有cmd处理实现，没有运行入口。

### [color_cmd_handle.py]

带有颜色的cmd处理输出。

只有处理实现，没有运行入口。
