# 信息流转发到Minecraft基岩版聊天

该组件可以帮你把直播信息流通过WS服务器转发到Minecraft基岩版内，默认使用say命令广播到已连接的客户端。

文件 `mcws_cmd_handle.py` 为cmd处理框架，无法直接启动，可作为依赖使用。

文件 `blmmcwsp.py` 为根据URL附加的直播间ID来推送直播信息流，每个直播间ID有着各自的客户端列表和直播信息流。

前往docs目录查看文档: [docs/blm_app/blm_to_mcws](../../docs/blm_app/blm_to_mcws/) 或者对应的线上页面。
