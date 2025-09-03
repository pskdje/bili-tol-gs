# main

文件: `main.py`

直播信息流启动入口。

需要所有的依赖文件，单独的启动文件无法启动直播信息流程序。

## 依赖

Python:

- \>3.11
- 未测试是否可在低版本中使用

本目录:

- blw.py
- blm.py
- all_cmd_handle.py
- color_cmd_handle.py

另请注意各个依赖的依赖，参阅 [blw依赖](blw.md#依赖) [all处理依赖](all_cmd_handle.md#依赖) [color处理依赖](color_cmd_handle.md#依赖) [protobuf处理依赖](protobuf_cmd_handle.md#依赖)

## 使用

启动入口将会依照第一个参数的指示来决定启动哪一个cmd处理，你可以提供一个启动指示，或者其它默认启动支持的命令行参数。

启动指示可选值： `all` , `color`

若未提供启动指示，将启动： `color`

## 参数

```
python main.py [启动指示] ...命令行参数
```

`启动指示` : 可选，用于指定启动的cmd处理，未指定将启动默认选择的cmd处理

`命令行参数` : 提供给cmd处理的其它参数

若cmd处理具有从blw继承的默认命令行参数，将会存在以下选项：

```
位置参数:
  roomid                      直播间ID

选项:
  -h, --help                  显示帮助信息并退出
  -d, --debug                 开启调试模式
  --cookie Cookie|FILE        使用Cookie登录
  --no-print-enable           不打印不支持的信息
  --pack-error-no-exit        数据包处理异常时不退出

调试功能:
  -u, --save-unknow-datapack  保存未知的数据包
  -C, --print-pack-count      打印数据包计数
  -c, --count-cmd CMD         对某个cmd进行计数
  -s, --save-cmd CMD          保存某个cmd数据包
```

## 示例

一般启动:

```shell
python main.py --cookie "buvid3=xxx;SESSDATA=xxx" 3
```

启动all处理:

```shell
python main.py all -u -C 3
```

启动color处理:

```shell
python main.py color --add-time time 3
```

## 接口

为节省文档维护工作量，接口的类型标注可能会省略，参见源代码获取类型标注。

### 类 `S`

为启动入口专门定制的特化启动逻辑。

对启动方法做了调整。

**继承:** `blm.BiliLiveMsg,blm.BiliLiveSaveExp`

### 类 `StartAllCmdHandle`

启动all_cmd_handle。

**继承:** `all_cmd_handle.BiliLiveAllCmdHandle,S`

### 类 `StartColorCmdHandle`

启动color_cmd_handle。

**继承:** `color_cmd_handle.AllCmdHandle,all_cmd_handle.BiliLiveAllCmdHandle,S`

### 顶层启动逻辑

将根据第一个命令行参数决定启动哪一个cmd处理。
