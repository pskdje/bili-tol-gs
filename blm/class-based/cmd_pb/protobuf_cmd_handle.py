"""protobuf cmd 处理
部分数据包已强制使用protobuf数据，此处将实现该数据的解析，并调用旧的解析逻辑（假如结构不变）。
"""

import blw
import sys,base64
from pathlib import Path
from blw import log
from google.protobuf.json_format import MessageToDict

basepath=Path(sys.path[0]).absolute()
log.debug(f"基础运行路程: {basepath}")
cpb_path=basepath/"cmd_pb"
log.debug(f"protobuf数据解析模块的路径: {cpb_path}")
sys.path.append(str(cpb_path))

# 数据解析导入
from bilibili.live.xuserreward.v1_pb2 import InteractWord
from bilibili.live.rankdb.v1_pb2 import GoldRankBroadcast

class ParseProtobufPack(blw.BiliLiveWS):
    

    def protobufToDict(self,message:bytes,mClass)->dict:
        """将protobuf数据处理为字典"""
        c=mClass()
        c.ParseFromString(message)
        return MessageToDict(c,True,True,False)

    def decodePB(self,data:str,mClass)->dict:
        """解析pb数据"""
        return self.protobufToDict(base64.b64decode(data),mClass)

    def dc_INTERACT_WORD_V2(s,p):
        p["data"]=s.decodePB(p["data"]["pb"],InteractWord)

    def dc_ONLINE_RANK_V3(s,p):
        p["data"]=s.decodePB(p["data"]["pb"],GoldRankBroadcast)
