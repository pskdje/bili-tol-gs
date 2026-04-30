# blm_tkui

文件: `blm_tkui.py`

信息流图形用户界面。

基于Tkinter的UI，代码由AI生成后手动重构而来（因为看不懂文档）。

## 依赖

Python:

- \>3.14
- 未测试是否可在低版本中使用

blm项目:

- blw.py (可选)
- blt.py (可选)

## 使用

启动UI后调用方法把特定信息发给UI显示。

## 接口

为节省文档维护工作量，接口的类型标注可能会省略，参见源代码获取类型标注。

部分以`so_`开头的为信息处理函数，这类函数均不会在此列出。

### 类型 `insert_text`

插入文本格式。

用于底部文本。

### 类 `BLM_UI`

UI的实现。

#### 属性 `BLM_UI.MAX_MSG`

限制历史最多显示多少消息。

#### 属性 `BLM_UI.DEFAULT_FONT_NAME`

默认字体名称。

#### 属性 `BLM_UI.HIDE_DELAY`

底部默认隐藏时间。

#### 属性 `BLM_UI.TEXT_TAGS`

预定义文本标签。

#### 方法 `BLM_UI.__init__`

准备UI需要的属性和方法。

#### 属性 `BLM_UI.msg_queue`

消息队列。

#### 属性 `BLM_UI.running`

线程事件信号，表示是否运行。

#### 属性 `BLM_UI.env`

运行环境，提供一些接口调用之类的功能，需要手动注入。

#### 属性 `BLM_UI.root`

Tk根窗口。

#### 属性 `BLM_UI.frame`

主容器。

#### 属性 `BLM_UI.text`

主消息区。

#### 属性 `BLM_UI.bottom_frame`

底部文本容器。

#### 属性 `BLM_UI.bottom_text`

底部文本。

#### 属性 `BLM_UI.bottom_font`

底部文本格式。

#### 属性 `BLM_UI.context_menu`

右键菜单。

#### 属性 `BLM_UI.hide_timer`

隐藏底部文本定时器id。

#### 方法 `BLM_UI.p`

打印文本。

#### 方法 `BLM_UI.error`

记录错误，指向控制台打印错误堆栈。

一般由[blm_ui.py](blm_ui.md)覆盖为[blw.py](../../blm/class-based/blw.md)的错误记录函数。

#### 方法 `BLM_UI.create_ui`

创建UI。

创建UI部件并写入 `root` 、 `frame` 、 `text` 、 `bottom_font` 、 `bottom_text` 、 `context_menu` 属性，注册文本标签。

#### 方法 `BLM_UI.click_close_button`

点击关闭按钮的操作。

默认终止UI。

#### 方法 `BLM_UI.is_scrolled_to_end`

判断是否滚动到末尾。

**返回值:** 表示是否需要滚到末尾

#### 方法 `BLM_UI.show_context_menu`

显示右键菜单，是回调函数。

#### 方法 `BLM_UI.copy_all_text`

复制全部文本到剪贴板。

#### 方法 `BLM_UI.load_history_danmu`

加载历史弹幕。

需要在[env属性](#属性-blm_uienv)中提供 `blt.DanmuTools.get_dm_history` 接口。

#### 方法 `BLM_UI.send_danmu_dialog`

显示发送弹幕对话框，按下发送按钮将发送弹幕。

需要在[env属性](#属性-blm_uienv)中提供 `blt.DanmuTools.send_danmu` 接口。

#### 方法 `BLM_UI.show_error_dialog`

显示错误对话框。

*参数* `message` : 错误提示信息

#### 方法 `BLM_UI.calculate_text_width`

计算文本宽度(像素)。

*参数* `text` : 被计算的文本

**返回值:** 文本宽度，单位：像素

#### 方法 `BLM_UI.truncate_text_parts`

根据UI的X轴长度截断文本，并根据需要添加`…`。

*参数* `text_parts` : 文本分段

*可能抛出异常* `TypeError` : 类型错误

**返回值:** 截断后的文本分段

#### 方法 `BLM_UI.update_bottom_text`

更新底部文本。

*参数* `text_parts` : 要显示的文本分段

*参数* `hide_delay` : 显示时间

#### 方法 `BLM_UI.hide_bottom_text`

隐藏并清空底部文本。

#### 方法 `BLM_UI.add_color_text`

添加带颜色的文本。

只能使用预定义的样式。

*参数* `text` : 要在UI显示的文本

*参数* `tag` : 已注册的样式标签

#### 方法 `BLM_UI.add_temp_color_text`

添加带颜色的文本，颜色标签使用完就被删除。

*参数* `text` : 要在UI显示的文本

*剩余关键字参数* `kw` : 可被tag_configure接受的参数

#### 方法 `BLM_UI.add_end`

添加末尾换行，换行为`\n`。

#### 方法 `BLM_UI.add_time`

添加时间信息，格式见源代码。

#### 方法 `BLM_UI.add_msg`

添加信息到UI。

清理超出上限的文本，调用[format_msg](#方法-blm_uiformat_msg)处理输入的信息，根据情况决定是否滚动到末尾。

*参数* `msg` : 传递给format_msg的参数

#### 方法 `BLM_UI.format_msg`

处理信息。

根据输入字典的`t`键决定要调用的`so_`处理函数。

*参数* `msg` : 消息数据，必须存在`t`键

*可能抛出异常* `TypeError` : 类型错误

#### 方法 `BLM_UI.process_queue`

消息处理。

定时读取消息队列调用[add_msg](#方法-blm_uiadd_msg)处理。

#### 方法 `BLM_UI.send_msg`

发送信息。

若UI未运行或消息队列已满，将丢弃信息。

*参数* `msg` : 要发送的信息，需要可被[format_msg](#方法-blm_uiformat_msg)处理的信息

#### 方法 `BLM_UI.stop_sign`

发送停止信号。

#### 方法 `BLM_UI.stop`

停止UI运行，允许多次调用。将略微推迟然后调用[stop_quit](#方法-blm_uistop_quit)销毁UI。

#### 方法 `BLM_UI.stop_quit`

销毁UI。

`root` 属性可用时才会销毁。

#### 方法 `BLM_UI.start`

启动UI。

将会检查UI是否已在运行。

然后创建UI并进入消息循环。

#### 方法 `BLM_UI.mainloop`

进入UI主循环。

UI运行时才会进入主循环，否则直接返回。

### 函数 `thread_run_ui`

运行UI并做好清理。

本身是作为在子线程运行的函数，将会创建UI并进入主循环，退出时自动清理。

UI必须在守护线程内运行。

*参数* `obj` : UI实例

### 函数 `start_blm_ui`

在子线程运行UI。

创建UI实例并在守护线程运行，线程内运行[thread_run_ui](#函数-thread_run_ui)函数。

**返回值:** 线程对象,UI实例
