# blm_ui

文件: `blm_ui.py`

信息流信息转发到UI。

启动和管理UI。

## 依赖

Python:

- \>3.14
- 未测试是否可在低版本中使用

blm项目:

- blw.py
- blm.py

本目录:

- blm_tkui.py

## 使用

文件允许直接在命令行中启动。

```shell
python blm_ui.py 23058
```

可使用 `-h` 或 `--help` 获取基本命令行参数。

命令行参数与blw.py相同（直接继承）。

## 接口

为节省文档维护工作量，接口的类型标注可能会省略，参见源代码获取类型标注。

所有的cmd处理实现接口均不会在此列出。

### 类 `CmdHandle`

部分cmd处理，启动与管理UI。

**继承:** `blm.BiliLiveExp`

#### 属性 `CmdHandle.blm_ui_thread`

UI线程容纳。

#### 属性 `CmdHandle.blm_ui_obj`

UI对象容纳。

#### 属性 `CmdHandle.add_args`

添加网页端的屏蔽参数。

#### 方法 `CmdHandle.error`

记录异常，附带该类的部分变量。

#### 方法 `CmdHandle.close`

执行关闭流程。

关闭blm_ui，同时调用父类的关闭函数。

#### 属性 `CmdHandle.has_running`

指示UI是否运行。

#### 方法 `CmdHandle.start_blm_ui`

用于启动blm_ui的主要方法，注入记录函数。

每次调用将产生新的UI，且丢失旧的UI引用，不要重复调用。

#### 方法 `CmdHandle.send_msg_to_ui`

发送信息到UI。

字典必须存在`t`键。

若UI未启动，输入的信息将丢弃。

*参数* `msg` : 要发送的信息

### 类 `WindowCloseExit`

此类实现了窗口关闭就退出程序的逻辑。

**继承:** `CmdHandle`

#### 方法 `WindowCloseExit.on_cert_pack_reply`

在原有的基础上添加`信息流连接`的提示发送到UI。

#### 方法 `WindowCloseExit.print_popularity`

打印人气值，但检测到窗口关闭后退出。

#### 方法 `WindowCloseExit.send_msg_to_ui`

发送信息到UI，但检测到窗口关闭后退出。

### 顶层启动逻辑

当处于顶层环境时，将创建[WindowCloseExit类](#类-windowcloseexit)，随后调用[start_blm_ui方法](#方法-cmdhandlestart_blm_ui)，最后启动[start方法](../../blm/class-based/blw.md#方法-bililivewsstart)。
