# all_cmd_handle

文件: `all_cmd_handle.py`

项目的所有已知cmd。

## 依赖

Python:

- \>3.11
- 未测试是否可在低版本中使用

本目录:

- blw.py
- cmd_pb/protobuf_cmd_handle.py

## 编写指引

本文件应作为保底使用，所有的cmd实现均为简单实现，详细数据包信息请自行抓取或查找资料。

在 [`no_run_enable_cmd`](blw.md#属性-bililivewsno_run_enable_cmd) 属性不为 `True` 时，可通过调试模式或 `--save-unknow-datapack` 默认参数启用数据包保存。

查看 [blw编写指引](blw.md#编写指引) 和 [blm编写指引](blm.md#编写指引) 来编写处理逻辑。

## 接口

### 类 `BiliLiveAllCmdHandle`

所有该项目已知cmd处理。

不可能真给你把所有的cmd都列出来，查看源代码了解信息。
