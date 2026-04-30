# start_blm_ui

文件: `start_blm_ui.py`

启动BLM UI。

本文件高度定制，不建议作为模块导入。

可将扩展名从 .py 改为 .pyw 来避免启动时弹出终端窗口，但这将意味着无法看到运行细节，风险自负。

## 依赖

Python:

- \>3.14
- 未测试是否可在低版本中使用

blm项目:

- blw.py
- blt.py

本目录:

- blm_ui.py

## 使用

文件允许直接在命令行中启动，且支持双击直接运行（需要打开绑定）。

虽然支持直接运行，但详细的操作定制还是需要通过命令行进行。

## 参数

```
python start_blm_ui.py [运行参数]
```

此处仅列出部分参数，详细信息使用帮助(`-h`)启动即可查看。

`--roomid ROOMID` : 直播间ID。提供此值将不显示直播间ID输入弹窗

`--cookie Cookie|FILE` : 使用Cookie登录。提供此值将不显示Cookie输入弹窗

若不提供`--cookie`参数且不在Cookie输入弹窗里输入SESSDATA将以未登录启动，此时将会受到B站限制。

## 示例

```shell
# 直接不带参数启动
python start_blm_ui.py
# 这将会显示2个对话框让你输入直播间ID和Cookie

# 提供直播间ID和Cookie启动
python start_blm_ui.py --roomid 3 --cookie "SESSDATA=xxx"
# 不会额外弹出输入框
```

## 接口

本文件高度定制，接口信息仅供参考，不建议调用。

为节省文档维护工作量，接口的类型标注可能会省略，参见源代码获取类型标注。

### 类 `GUI`

最终用户界面。

**继承:** `blm_ui.WindowCloseExit,blt.DanmuTools`

#### 方法 `GUI.build_argparser`

专用定制的构造命令行参数解析方法。

#### 方法 `GUI.check_CWD`

检查当前工作目录。

当处于错误的工作目录时修改回文件的父目录。目前在双击启动时出现。

#### 方法 `GUI.handle_errdirlist`

处理错误记录列表。

只使用UI的话大概不会太管错误记录目录，所以加了清理方法。

#### 方法 `GUI.start`

启动用户界面。

本函数高度定制，输入弹窗和启动处理均由该方法负责，详见源代码。

若不输入直播间ID将退出程序。

若不输入Cookie将以未登录启动。

循环重试。

### 顶层启动逻辑

调用[GUI](#类-gui).[start](#方法-guistart)方法。
