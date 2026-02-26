# bilibili live websocket danmaku (?)

## 声明

请勿滥用！本文件夹内的文件仅用于学习和测试。上传至GitHub仅为了方便和备份。

使用或修改本文件夹内的文件所引发的争议及后果与本人无关。

一旦出现任何情况，本人随时可删除本文件夹。

**程序并不考虑交互**

使用的编程语言: [Python](https://www.python.org/)

**不能保证已存在的信息能及时更新**

## 依赖

无法保证依赖对所有的架构逻辑有效，之后可能会删除该部分。

### 必须

`requests`: 网络请求

`websockets`: WS库

`protobuf`: protobuf数据解析，部分数据包强制需要

### 可选

`brotli`: 数据解压

## 文档

现已添加部分文档，见[docs/blm](../docs/blm/index.md)（[线上页面](https://pskdje.github.io/bili-tol-gs/blm/)）

## 文件夹/文件

当前维护的主程序目录: class-based

### [process-based/]

基于流程的旧程序。

已弃用。

### [class-based/]

基于类的新程序。

### [requirement.txt]

内容为需要的依赖库，必须和可选的依赖都会包括在内。

### [nda.txt]

用于调试，在不使用`--debug`参数时使用。在不需要很多细节的情况下使用此文件内的参数可以减少一些多余的输出。

### [bili live msg.py]

获取信息流，保存数据包。

仅支持zlib解压缩！

自动切割数据包。

主程序 就是从这拓展出来的。

已不适应最新情况。

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

[SocialSisterYi/bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect)(已失效) 提供数据包格式和URL

[open-live.bilibili.com](https://open-live.bilibili.com/document/) 新版数据包解析逻辑支持，提供开放API
