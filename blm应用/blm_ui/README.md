# 直播信息流简单图形界面

一个简单的图形界面，基于tkinter。

由于看不懂tkinter的文档，所以UI部分是使用AI写的加上手动调整。

## 使用

将本目录的`.py`文件和[blm](../../blm/class-based/)放在同一目录，运行`start_blm_ui.py`即可。

可将`start_blm_ui.py`的扩展名改为pyw如`start_blm_ui.pyw`来在支持的平台以无终端窗口运行。这将意味着无法看到运行细节，风险自负。

其它信息详见文档。

## 文档

前往docs目录查看文档: [docs/blm_app/blm_ui](../../docs/blm_app/blm_ui/) 或者对应的线上页面。

## 文件

`blm_ui.py` 提供启动和管理UI的接口，也提供了部分cmd处理。

`blm_tkui.py` 基于Tkinter的UI，大部分使用AI编写，部分函数我写。

`start_blm_ui.py` 用于启动 blm_ui.py ，同时把一些原先只能通过命令行传递的参数改为弹窗输入。
