"""protobuf cmd 处理
部分数据包已强制使用protobuf数据，此处将实现该数据的解析，并调用旧的解析逻辑（假如结构不变）。
"""

import blw
import sys,base64
from pathlib import Path
from blw import log
from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message

basepath=Path(sys.path[0]).absolute()
log.debug(f"基础运行路程: {basepath}")
cpb_path=basepath/"cmd_pb"
log.debug(f"protobuf数据解析模块的路径: {cpb_path}")
sys.path.append(str(cpb_path))

# 数据解析导入
from bilibili.live.xuserreward.v1_pb2 import InteractWord
from bilibili.live.rankdb.v1_pb2 import GoldRankBroadcast
from bilibili.live.gift.v1_pb2 import SendGiftBroadcast

class ParseProtobufPack(blw.BiliLiveWS):
    """解析 protobuf 数据的中间件

    解析方法统一按 `dc_` 开头，用代码表述： `"dc_"+cmd`

    除此之外还有一些工具方法。
    """

    def protobufToDict(self,message:bytes,mClass:type[Message])->dict:
        """将protobuf数据处理为字典"""
        c=mClass()
        c.ParseFromString(message)
        return MessageToDict(c,True,True,False)

    def decodePB(self,data:str,mClass:type[Message])->dict:
        """解析pb数据"""
        return self.protobufToDict(base64.b64decode(data),mClass)

    def dc_INTERACT_WORD_V2(s,p):
        p["data"]=s.decodePB(p["data"]["pb"],InteractWord)
        return p["data"]

    def dc_ONLINE_RANK_V3(s,p):
        p["data"]=s.decodePB(p["data"]["pb"],GoldRankBroadcast)
        return p["data"]

    def dc_SEND_GIFT_V2(s,p):
        d=s.decodePB(p["data"]["pb"],SendGiftBroadcast)
        del p["data"]["pb"]
        p["data"]|=d
        return p["data"]
