# bili\_live\_ws.py 的文档

> **注意**：程序使用了Python 3.10的语法，不向下兼容。

提示: 目前不登录将不显示用户昵称。

提示: 现在心跳包回复视情况显示人气值。

## 依赖

除了Python运行环境外，还需以下Python模块。

**必须**: `requests` , `websockets`

可选: `brotli`

## 参数

见帮助信息，此处仅写下帮助信息里不好描述的参数选项。

程序允许使用 `@` 来引入参数文件。

### --sessdata

会话数据

支持直接传入和文件路径。

使用该参数必须同时使用 `--uid` 参数，否则依然处于未登录状态。

目前文件支持单纯存储SESSDATA和cookie.txt。相关解析代码比较简单，请注意确认格式是否正确。

**注意**: SESSDATA会记录在错误文件内！

示例:

```shell
# 直接传入
python bili_live_ws.py --sessdata SESSDATA --uid 0 23058

# 使用文件
python bili_live_ws.py --sessdata FILEPATH --uid 0 23058
```

**注意**: 文件过大将拒绝执行。

### --uid

用户UID(mid)

默认值: 0

使用该参数时必须同时提供 `--sessdata` 参数，否则连接将关闭。

使用某个UID登录后获取的SESSDATA拿到这里使用时必须正确填写这个UID，否则连接将关闭。
这里不提供获取教程，你可以不使用登录信息。

### --shielding-words

屏蔽词，要完全匹配弹幕文本。

一行一条，遇到空行将停止解析。

允许使用 `#` 来写入注释文本。注意： `#` 前面不能有其它字符。

### --blocking-rules

屏蔽规则，使用正则表达式。

一行一条，遇到空行将停止解析。

允许使用 `#` 来写入注释文本。注意： `#` 前面不能有其它字符。

## 可能引起连接关闭的情况

### 网络问题

最常见的引起连接关闭的情况就是网络问题。包括网络连接缓慢、切换网络、连接不稳定等。

### 服务器问题

当前已知提供的UID和会话SESSDATA信息不匹配时会引发连接关闭，包括会话信息过期。

一旦提供了UID，就必须提供SESSDATA。经测试，只提供了SESSDATA不会使连接关闭，但会处于未登录状态（即使提供了无效的数据也一样）。只提供UID却会使连接关闭。

## 提示

程序会自动记录错误信息，包括因网络问题导致的关闭。所以，如果你使用时经常因为网络波动而关闭连接时，要记得定期删除错误记录文件。

## 路径使用

程序只会在自身所在的路径里创建数据，不会在其它路径修改数据。若出现在其它路径修改数据的情况，请检查文件来源；若来源未见异常，请审查代码，必要时可开issue，带上文件。

文件夹 bili\_live\_ws\_err ：在出现错误时创建，存储错误信息。

文件夹 bili\_live\_ws\_pack ：当需要保存数据包时创建，存储数据包。

文件夹 bili\_live\_ws\_log ：当需要存储日志时创建，存储日志，主要为`--debug`参数所使用，也可以被其它组件启用。

有可能会出现名为"bili live msg data"的文件夹，这个是运行"bili live msg.py"时所产生，不在本文件的讨论范围。

\_\_pycache\_\_ 由Python解释器产生，不做描述。

若除了这些路径，还多出了其它路径的话，请审查源代码。可能的原因：文件被修改、新增了某个功能但忘记在此增加条目、出现漏洞(bug)。

## 接口使用信息

大部分的接口都可以阅读源代码来使用，这里只对部分接口进行描述。

### `pararg`

类型标注（以源代码为准）:

```python
def pararg(aarg: list[dict] | tuple[dict,...] = None)-> argparse.Namespace:
```

参数 `aarg` 只接受以[`dict`](https://docs.python.org/zh-cn/3/library/stdtypes.html#mapping-types-dict)类型为内容的可迭代数据。

字典除了`name`是**必须**的，其它参数都是可选的。

除了`name`，其它键的用法可在[Python argparse 文档](https://docs.python.org/zh-cn/3/library/argparse.html#the-add-argument-method)找到。

允许使用的参数: \[`help`, `action`, `const`, `default`, `type`, `choices`, `metavar`, `dest`\]

键 `name`: (必须)指定参数名称，若开头没有 `--` 将会自动添加。若开头为 `-` ，可能会出现未知的问题，后果自负。

注: `name`会保存起来，用于调试。
