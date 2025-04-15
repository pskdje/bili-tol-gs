# bilibili live websocket danmaku (?)

## 声明

请勿滥用！本文件夹内的文件仅用于学习和测试。上传至GitHub仅为了方便和备份。

使用或修改本文件夹内的文件所引发的争议及后果与本人无关。

一旦出现任何情况，本人随时可删除本文件夹。

**程序并不考虑交互**

使用的编程语言: [Python](https://www.python.org/)

**不能保证已存在的信息能及时更新**

## 文件夹/文件

### [process-based/]

基于流程的旧程序。

已弃用。

### [class-based/]

基于类的新程序。

### [requirement.txt]

内容为需要的依赖库，必须和可选的依赖都会包括在内。

### [default_args.txt]

~~默认命令行参数~~ ~~(我也不知道这是什么，只是想有一个名称有 default 的文件)~~

### [bili_args.txt]

仿照互动区域可能显示的内容来显示信息。

### [msg_args.txt]

只显示弹幕或留言(理论上是这样)

### [my_args.txt]

给我自己使用的命令行参数。

### [nda.txt]

用于调试，在不使用`--debug`参数时使用。在不需要很多细节的情况下使用此文件内的参数可以减少一些多余的输出。

### [bili live msg.py]

获取信息流，保存数据包。

仅支持zlib解压缩！

自动切割数据包。

bili_live_ws.py 就是从这拓展出来的。

用法:
```shell
python "bili live msg.py" [roomid]
```
> 参数: roomid可选,输入实际房间号

### [bilibili live data.py]

从保存的数据包中找出未知的命令。

### [save pack filter.py]

从保存的数据包中筛选出需要的数据。

## 参考

[SocialSisterYi/bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect) 提供数据包格式和URL
