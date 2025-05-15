"""直播工具
提供一些接口给其它组件调用
"""

import blw,blm
import time,json,asyncio
from pathlib import Path
from typing import NamedTuple,Any
from blw import GetDataError,log

__all__=[
    # 数据类
    "DMColor",
    "LiveLink",
    # 低层类
    "ToolBase",
    # 分类接口
    "DanmuTools",
    "LiveTools",
    # 接口合并
    "BiliLiveTools"
]

class DMColor:
    """弹幕颜色"""
    def __init__(self,name:str,color:int,color_hex:str,status:int):
        """初始化"""
        self.name=name
        self.color=color
        self.color_hex=color_hex
        self.status=status
    def __str__(self):
        """返回颜色"""
        return self.color_hex
    def __repr__(self):
        """返回自身构造伪代码"""
        return f"DMColor({repr(self.name)},{repr(self.color)},{repr(self.color_hex)},{repr(self.status)})"

class LiveLink(NamedTuple):
    """直播推流地址容纳"""
    addr:str
    code:str
    def __str__(self):
        return self.addr+self.code

class ToolBase(blm.BiliLiveExp):
    """基本工具"""

    def set_cookie(self,data:dict[str,str])->dict[str,str]:
        """设置cookie，通过|=操作。若输入None将重新创建一个dict给cookies变量"""
        if data is None:
            c={}
            self.cookies=c
            return c
        if not isinstance(data,dict):
            raise TypeError("输入的不是dict类型")
        self.cookies|=data
        return data

    def split_kv_cookie(self,data:str)->dict[str,str]:
        """从字符串获取cookie"""
        return self.set_cookie(blm.split_kv_cookie(data))
    def split_cookietxt(self,data:str)->dict[str,str]:
        """处理cookie.txt格式的数据"""
        c={}
        l=data.splitlines()
        for i in l:
            if len(i)<8:
                continue
            m=i.split("\t")
            if m[0]==".bilibili.com":
                c[m[-2]]=m[-1]
        return self.set_cookie(c)

    def read_cookie(self,data:str)->dict[str,str]|None:
        """读取cookie"""
        p=Path(data)
        if not p.is_file():
            return self.split_kv_cookie(data)
        if p.stat().st_size>1048575:
            raise ValueError("文件大小超过1MB")
        try:
            d=p.read_text()
        except:
            log.exception("读取cookie文件失败")
            return
        if "\t" in d:
            return self.split_cookietxt(d)
        else:
            return self.split_kv_cookie(d)

    add_args=[
        {"name":"cookie","help":"使用cookie","type":str},
    ]

    def add_csrf(self,odic:dict[str,str])->dict:
        """为dict添加csrf"""
        odic["csrf"]=self.cookies["bili_jct"]
        return odic

class DanmuTools(ToolBase):
    """弹幕"""

    send_danmu_time:float=0
    send_danmu_lock=asyncio.Lock()

    def on_send_danmu_start(s,m)->None:
        """开始发送弹幕，传入要发送的弹幕"""
    def on_send_danmu_res(s,d)->None:
        """发送弹幕的响应，传入弹幕信息"""

    def erron_send_danmu(s,e)->None:
        """发送弹幕失败，传入错误对象"""

    # 发送弹幕
    def send_danmu(self,msg:str)->dict:
        """发送弹幕"""
        r=self.get_rest_data("发送弹幕","https://api.live.bilibili.com/msg/send",self.add_csrf({
            "roomid":self.roomid,
            "msg":msg,
            "rnd":int(time.time()),
            "fontsize":25,
            "color":16777215,
            "mode":1,
        }))
        return json.loads(r["data"]["mode_info"]["extra"])
    async def send_msg_and_restrict(self,msg:str,rate_limit:bool=True)->None|str:
        """发送弹幕并进行一些限制
        将限制发送速率并视消息长度进行分割"""
        m=str(msg)
        ml=len(m)
        idx=0
        block=30
        if self.send_danmu_time+5>time.time()and rate_limit:
            return "发送速率限制，丢弃消息"
        self.send_danmu_time=time.time()
        log.debug(f"""准备发送弹幕: {repr(m)} ,长度: {ml}{' 预计进行分割发送'if ml>block else ''}""")
        async with self.send_danmu_lock:
            self.on_send_danmu_start(msg)
            while idx<ml:
                try:
                    r=self.send_danmu(m[idx:idx+block])
                except GetDataError as e:
                    log.debug(f"发送弹幕失败: {e}")
                    self.erron_send_danmu(e)
                    return "出现错误"
                self.on_send_danmu_res(r)
                idx+=block
                await asyncio.sleep(3)
    def send_msg(self,msg:str,*an:Any,**ad:Any)->asyncio.Task:
        """创建异步发送弹幕任务"""
        return asyncio.create_task(self.send_msg_and_restrict(msg,*an,**ad),name="发送弹幕任务")

    # 弹幕配置
    def get_dm_config(self)->dict:
        """获取当前直播间弹幕可选配置"""
        r=self.get_rest_data("获取弹幕可选配置",f"https://api.live.bilibili.com/xlive/web-room/v1/dM/GetDMConfigByGroup?room_id={self.roomid}")
        d=r["data"]
        cl={}
        md={}
        for i1 in d["group"]:
            for i2 in i1["color"]:
                cl[i2["name"]]=DMColor(i2["name"],i2["color"],i2["color_hex"],i2["status"])
        for i in d["mode"]:
            md[i["name"]]=i["mode"]
        self.dm_color=cl
        self.dm_mode=md
        return d
    def set_dm_config(self,color:str=None,mode:int=None)->dict:
        """设置当前直播间的弹幕配置
        color和mode必须选一个提供，并且不能同时存在
        详见: [issue(comment)](https://github.com/SocialSisterYi/bilibili-API-collect/issues/1236#issuecomment-2849019923) [BAC资料](https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/live/danmaku.md#%E8%AE%BE%E7%BD%AE%E5%BC%B9%E5%B9%95%E6%A0%B7%E5%BC%8F)"""
        d=self.add_csrf({
            "room_id":self.roomid,
        })
        if color is not None:
            d["color"]=color
        if mode is not None:
            d["mode"]=mode
        return self.get_rest_data("设置弹幕配置","https://api.live.bilibili.com/xlive/web-room/v1/dM/AjaxSetConfig",data=d)

class LiveTools(ToolBase):
    """开关播"""

    def startLive(self,area:int,platform:str="web_link")->LiveLink:
        """开始直播"""
        b=self.add_csrf({
            "room_id":self.roomid,
            "area_v2":area,
            "platform":platform,
        })
        r=self.get_rest_data("开始直播","https://api.live.bilibili.com/room/v1/Room/startLive",b)
        d=r["data"]
        self.live_key=d["live_key"]
        return LiveLink(d["rtmp"]["addr"],d["rtmp"]["code"])
    def stopLive(self)->dict:
        """停止直播"""
        b=self.add_csrf({
            "room_id":self.roomid,
            #"platform":"web_link",
        })
        r=self.get_rest_data("停止直播","https://api.live.bilibili.com/room/v1/Room/stopLive",b)
        return r["data"]

class LiveDataTools(ToolBase):
    """直播数据"""

    def stopLiveData(self,live_key:str=None)->dict:
        """获取停止直播场次的数据
        若提供live_key将使用这个key，否则从self.live_key读取
        若还是没有将抛出错误，由getattr抛出"""
        k=live_key
        if not isinstance(k,str):
            k=getattr(self,"live_key")# 通常是调用startLive记录live_key
        return self.get_rest_data("获取停止直播场次的数据",f"https://api.live.bilibili.com/xlive/app-blink/v1/live/StopLiveData?live_key={k}")["data"]

class RoomTools(ToolBase):
    """直播间管理"""

    def room_update(self,title:str=None,area:int=None,add_tag:str=None,del_tag:str=None)->dict:
        """更新直播间信息"""
        b=self.add_csrf({
            "room_id":self.roomid,
        })
        if title is not None:
            b["title"]=title
        if area is not None:
            b["area_id"]=area
        if add_tag is not None:
            b["add_tag"]=add_tag
        if del_tag is not None:
            b["del_tag"]=del_tag
        return self.get_rest_data("更新直播间信息","https://api.live.bilibili.com/room/v1/Room/update",b)["data"]

class BiliLiveTools(DanmuTools,LiveTools,LiveDataTools,RoomTools):
    """全部工具"""
