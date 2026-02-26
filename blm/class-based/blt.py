"""直播工具
提供一些接口给其它组件调用
"""

import blw,blm
import time,json,asyncio
import http.cookiejar as cookiejar
from pathlib import Path
from dataclasses import dataclass
from typing import NamedTuple,Any,Self,Literal,overload,TYPE_CHECKING
from blw import GetDataError,log,BiliRESTReturn

__all__=[
    # 常量
    "DEFAULT_APPkey",
    "DEFAULT_APPsec",
    # 数据类
    "DMColor",
    "LiveLink",
    # 低层类
    "ToolBase",
    # 分类接口
    "DanmuTools",
    "SpectatorTools",
    "LiveTools",
    "LiveDataTools",
    "RoomTools",
    "LiveReplay",
    # 接口合并
    "BiliLiveTools"
]

if TYPE_CHECKING:
    import bili_types.blt as blt_T

DEFAULT_APPkey="1d8b6e7d45233436"
DEFAULT_APPsec="560c52ccd288fed045859ed18bffd973"

class APPSign:
    """APP签名返回"""
    query:str
    """查询参数"""
    signed_params:dict[str,Any]
    """查询字典"""
    sign:str
    """签名字符串"""
    def __str__(self):
        """返回签名结果字符串"""
        return self.query

    @staticmethod
    def app_sign(params:dict,appkey:str=DEFAULT_APPkey,appsec:str=DEFAULT_APPsec)->Self:
        """签名"""
        return appsign(params,appkey,appsec)

def appsign(params:dict[str,Any],appkey:str,appsec:str)->APPSign:
    """APP签名
    代码来自 [链接已失效](https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/misc/sign/APP.md)
    """# 这玩意也不想自己写
    from urllib.parse import urlencode
    from hashlib import md5
    pr=params.copy()
    pr.update({"appkey":appkey})
    pr=dict(sorted(pr.items()))
    qu=urlencode(pr)
    sign=md5((qu+appsec).encode()).hexdigest()
    pr["sign"]=sign
    return APPSign(
        urlencode(pr),
        pr,
        sign
    )

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

    def set_cookie(self,data:dict[str,str]|Any|None)->str:
        """设置cookie，只支持特定类型。若输入None将清除所有已存在的cookie"""
        cks=self.cookies
        if data is None:
            cks.clear()
            return "clear"
        if isinstance(data,dict):
            for ck,cv in data.items():
                if ck=="SESSDATA":
                    cks.set(ck,cv,domain=".bilibili.com",secure=True)
                    continue
                cks.set(ck,cv,domain=".bilibili.com")
            return "dict_to_cookie"
        if isinstance(data,cookiejar.CookieJar):
            cks.update(data)
            return "cookiejar"
        return "none"

    # 处理基本cookie存储数据
    def split_kv_cookie(self,data:str)->dict[str,str]:
        """从字符串获取cookie"""
        return self.set_cookie(blw.split_kv_cookie(data))
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
    def split_file_cookie(self,path:str,cj:type[cookiejar.FileCookieJar]):
        """处理存储在文件的cookie
        path: 文件路径
        cj: FileCookieJar子类的类对象
        """
        c=cj()
        try:
            c.load(path)
        except cookiejar.LoadError:
            return "LoadError"
        else:
            self.cookies.update(c)
            return "update"

    # 处理其它cookie存储数据
    def split_biliup_cookie(self,data:dict|Path):
        """处理biliup的cookies.json文件"""
        if isinstance(data,Path):
            with data.open("rt")as f:
                d=json.load(f)
        else:
            d=data
        if not isinstance(d,dict):raise TypeError("数据不是dict对象")
        for i in d["cookie_info"]["cookies"]:
            self.cookies.set(i["name"],i["value"],domain=".bilibili.com",secure=bool(i["secure"]),expires=i["expires"],rest={"HttpOnly":i["http_only"]})
        return "set"

    # 读取cookie
    def read_cookie(self,data:str)->dict[str,str]|None:
        """读取常见cookie数据"""
        p=Path(data)
        if not p.is_file():
            return self.split_kv_cookie(data)
        if p.stat().st_size>1048575:
            raise ValueError("文件大小超过1MB")
        sfcs="update"
        if self.split_file_cookie(data,cookiejar.MozillaCookieJar)==sfcs:return "MozillaCookieJar"
        if self.split_file_cookie(data,cookiejar.LWPCookieJar)==sfcs:return "LWPCookieJar"
        try:
            d=p.read_text()
        except:
            log.exception("读取cookie文件失败")
            return
        if "\t" in d:
            return self.split_cookietxt(d)
        else:
            return self.split_kv_cookie(d)

    appkey=DEFAULT_APPkey
    appsec=DEFAULT_APPsec

    def add_csrf[D:dict[str,str]](self,odic:D)->D:
        """为dict添加csrf"""
        odic["csrf"]=self.cookies["bili_jct"]
        return odic

    def appsign(self,params:dict,appkey:str=None,appsec:str=None)->APPSign:
        """APP签名。"""
        if appkey is None:
            appkey=self.appkey
        if appsec is None:
            appsec=self.appsec
        return appsign(params,appkey,appsec)

class DanmuTools(ToolBase):
    """弹幕"""

    send_danmu_time:float=0
    """弹幕发送时间，用于速率限制。"""
    send_danmu_lock=asyncio.Lock()
    """发送弹幕锁，防止并发发送导致发送失败。"""
    send_danmu_block=30
    """发送弹幕分块大小，用于防止因字数限制导致发送失败。"""

    def on_send_danmu_start(s,m)->None:
        """开始发送弹幕，传入要发送的弹幕"""
    def on_send_danmu_res(s,d)->None:
        """发送弹幕的响应，传入弹幕信息"""

    def erron_send_danmu(s,e)->None:
        """发送弹幕失败，传入错误对象"""

    # 发送弹幕
    @overload
    def send_danmu(self,msg:str,reply_mid:int,replay_dmid:str,*,return_type:Literal["extra"])->dict: ...
    @overload
    def send_danmu(self,msg:str,reply_mid:int,replay_dmid:str,*,return_type:Literal["extra_raw"])->str: ...
    @overload
    def send_danmu(self,msg:str,reply_mid:int,replay_dmid:str,*,return_type:Literal["raw"])->BiliRESTReturn["blt_T.SendLiveDanmuRes"]: ...
    @overload
    def send_danmu(self,msg:str,reply_mid:int,replay_dmid:str,*,return_type:Literal["data"])->"blt_T.SendLiveDanmuRes": ...
    @overload
    def send_danmu(self,msg:str,reply_mid:int,replay_dmid:str,*,return_type:str)->dict: ...
    def send_danmu(self,msg:str,reply_mid:int=0,replay_dmid:str="",*,return_type:str="extra"):
        """发送弹幕\n\nmsg: 弹幕内容\n\nreply_mid: 被回复者的uid\n\nreplay_dmid: 要回复的弹幕id"""
        r:BiliRESTReturn["blt_T.SendLiveDanmuRes"]=self.get_rest_data("发送弹幕","https://api.live.bilibili.com/msg/send",self.add_csrf({
            "roomid":self.roomid,
            "msg":msg,
            "rnd":int(time.time()),
            "fontsize":25,
            "color":16777215,
            "mode":1,
            "reply_mid":reply_mid,
            "replay_dmid":replay_dmid,
        }))
        t=return_type
        if t=="extra_raw":return r["data"]["mode_info"]["extra"]
        elif t=="raw":return r
        elif t=="data":return r["data"]
        return json.loads(r["data"]["mode_info"]["extra"])
    async def send_msg_and_restrict(self,msg:str,rate_limit:bool=True,*an:Any,**ad:Any)->None|str:
        """发送弹幕并进行一些限制
        将限制发送速率并视消息长度进行分割\n
        msg: 弹幕内容，若超出弹幕分块大小将进行分块\n
        rate_limit: 是否启用基于发送时间的速率限制，触发限制将丢弃弹幕\n
        ad: 其它传递给`send_danmu`的参数"""
        m=str(msg)
        ml=len(m)
        idx=0
        block=30
        if self.send_danmu_time+5>time.time()and rate_limit:
            log.debug(f"触发弹幕发送速率限制，丢弃消息。消息内容: {repr(m)}")
            return "发送速率限制，丢弃消息"
        self.send_danmu_time=time.time()
        log.debug(f"""准备发送弹幕: {repr(m)} ,长度: {ml}{' 预计进行分割发送'if ml>block else ''}""")
        async with self.send_danmu_lock:
            self.on_send_danmu_start(msg)
            while idx<ml:
                try:
                    r=await asyncio.to_thread(self.send_danmu,m[idx:idx+block],*an,**ad)
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
    def get_dm_config(self)->"blt_T.GetDMConfigByGroup":
        """获取当前直播间弹幕可选配置"""
        r=self.get_rest_data("获取弹幕可选配置",f"https://api.live.bilibili.com/xlive/web-room/v1/dM/GetDMConfigByGroup?room_id={self.roomid}")
        d:"blt_T.GetDMConfigByGroup"=r["data"]
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
    def set_dm_config(self,color:str=None,mode:int=None)->BiliRESTReturn["blt_T.SetDMConfig"]:
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

    def get_dm_history(self)->BiliRESTReturn["blt_T.GetDMHistory"]:
        """获取历史弹幕"""
        return self.get_rest_data("获取历史弹幕",f"https://api.live.bilibili.com/xlive/web-room/v1/dM/gethistory?roomid={self.roomid}")

class SpectatorTools(ToolBase):
    """观众操作"""

    def getInfoByUser(self)->dict:
        """获取用户在某个直播间的状态信息，此接口将会使服务器下发进入直播间信息"""
        d=self.get_rest_data("进入直播间",f"https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByUser?room_id={self.roomid}")["data"]
        try:
            self.send_danmu_block=int(d["property"]["danmu"]["length"])
        except(KeyError,ValueError):
            log.warning("设置弹幕分块长度失败",exc_info=True)
            if self.debug:
                self.p("无法设置弹幕分块长度")
        return d

class LiveTools(ToolBase):
    """开关播"""

    def startLive(self,area:int,platform:str="pc_link",build:str|int="",version:str="",buvid:str=None,*,return_type:str="LiveLink")->LiveLink|BiliRESTReturn["blt_T.StartLive"]|"blt_T.StartLive":
        """开始直播\n
        area: 直播分区\n
        platform: 直播平台\n
        build: 直播姬构建编号\n
        version: 直播姬版本号\n
        buvid: 直播姬buvid\n
        return_type: 返回数据类型('raw':原始响应,'data':信息本体,其它值:LiveLink对象)\n
        根据开播账号和各种使用情况来填写参数，具体看它要不要给你通过。
        """
        # 构建请求头
        h={}
        if isinstance(buvid,str):
            h["buvid"]=buvid
        # 构建请求体
        b=self.add_csrf({
            "room_id":self.roomid,
            "area_v2":area,
            "platform":platform,
            "build":build,
            "version":version,
            "access_key":"",
        })
        b=self.appsign(b,"aae92bc66f3edfab","af125a0d5279fd576c1b4418a3e8276d").signed_params
        # 处理流程
        r=self.get_rest_data("开始直播","https://api.live.bilibili.com/room/v1/Room/startLive",b,headers=h)
        d=r["data"]
        self.live_key=d["live_key"]
        rt=return_type
        if rt=="raw":
            return r
        elif rt=="data":
            return d
        return LiveLink(d["rtmp"]["addr"],d["rtmp"]["code"])
    def stopLive(self,platform:str="pc_link")->"blt_T.StopLive":
        """停止直播\n
        platform: 直播平台"""
        b=self.add_csrf({
            "room_id":self.roomid,
            "platform":platform,
        })
        r=self.get_rest_data("停止直播","https://api.live.bilibili.com/room/v1/Room/stopLive",b)
        return r["data"]

class LiveDataTools(ToolBase):
    """直播数据"""

    def stopLiveData(self,live_key:str=None)->"blt_T.StopLiveData":
        """获取停止直播场次的数据
        若提供live_key将使用这个key，否则从self.live_key读取
        若还是没有将抛出错误，由getattr抛出"""
        k=live_key
        if not isinstance(k,str):
            k=getattr(self,"live_key")# 通常是调用startLive记录live_key
        return self.get_rest_data("获取停止直播场次的数据",f"https://api.live.bilibili.com/xlive/app-blink/v1/live/StopLiveData?live_key={k}")["data"]

class RoomTools(ToolBase):
    """直播间管理"""

    def room_update(self,title:str=None,area:int=None,add_tag:str=None,del_tag:str=None)->"blt_T.RoomUpdate":
        """更新直播间信息\n
        title: 直播标题\n
        area: 直播分区\n
        add_tag: 要添加的标签\n
        del_tag: 要删除的标签"""
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

    def updatePreLiveInfo(self,cover:str=None,title:str=None,*,platform:str="web")->"blt_T.UpdatePreLiveInfo":
        """预更新直播信息\n
        cover: 直播封面URL\n
        title: 直播标题\n
        platform: 直播平台"""
        b=self.add_csrf({
            "platform":platform,
            "mobi_app":platform,
            "build":1,
        })
        if cover is not None:
            b["cover"]=cover
        if title is not None:
            b["title"]=title
        return self.get_rest_data("预更新直播信息","https://api.live.bilibili.com/xlive/app-blink/v1/preLive/UpdatePreLiveInfo",b)["data"]

class LiveReplay(ToolBase):
    """直播回放"""

    def get_replay_list(self,page:int=1,page_size:int=12)->dict:
        """获取回放列表"""
        return self.get_rest_data("获取直播回放列表",f"https://api.live.bilibili.com/xlive/app-blink/v1/anchorVideo/AnchorGetReplayList?page={page}&page_size={page_size}")["data"]
    def get_video_slice_list(self,page:int=1,page_size:int=12)->dict:
        """获取已发布片段列表"""
        return self.get_rest_data("获取已发布片段列表",f"https://api.live.bilibili.com/xlive/app-blink/v1/anchorVideo/AnchorGetVideoSliceList?page={page}&page_size={page_size}")["data"]
    def get_draft_list(self,page:int=1,page_size:int=12)->dict:
        """获取草稿列表"""
        return self.get_rest_data("获取回放剪辑草稿列表",f"https://api.live.bilibili.com/xlive/app-blink/v1/anchorVideo/GetDraftList?page={page}&page_size={page_size}")["data"]

    def delete_slice_draft(self,draft_id:int)->dict:
        """删除某个草稿"""
        b=self.add_csrf({
            "draft_id":draft_id,
        })
        return self.get_rest_data("删除回放剪辑草稿","https://api.live.bilibili.com/xlive/app-blink/v1/anchorVideo/DeleteSliceDraft",b)

    def get_slice_stream(self,live_key:str,start_time:int,end_time:int)->dict:
        """获取切片视频流"""
        return self.get_rest_data("获取切片视频流",f"https://api.live.bilibili.com/xlive/app-blink/v1/anchorVideo/GetSliceStream?live_key={live_key}&start_time={start_time}&end_time={end_time}")["data"]
    def get_live_session_data(self,live_key:str,start_tm:str="2000-01-01+08:00:00",end_tm:str="2030-01-01+08:00:00")->dict:
        """获取直播会话数据"""
        return self.get_rest_data("获取直播会话数据",f"https://api.live.bilibili.com/xlive/app-blink/v1/anchorVideo/GetLiveSessionData?live_key={live_key}&start_tm={start_tm}&end_tm={end_tm}")["data"]

    def publish_video_slice(self,live_key:str,start_ts:int,end_ts:int,av_title:str,av_cover:str="https://i0.hdslb.com/bfs/live/59fc254c1f51a962dbf69ae85e4920f2f6fb8dcd.png",av_highlight:int=0,with_subtitle:int=0,with_danmaku:int=0,with_reserve:int=0,av_speed:str="")->dict[str,int]:
        """发布回放片段
        从av_title参数开始，建议使用关键字参数
        参数解释见[BAC资料](https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/live/live_replay.md#%E6%8A%95%E7%A8%BF%E7%9B%B4%E6%92%AD%E5%9B%9E%E6%94%BE%E7%89%87%E6%AE%B5)"""
        b=self.add_csrf({
            "live_key":live_key,
            "start_ts":start_ts,
            "end_ts":end_ts,
            "av_title":av_title,
            "av_cover":av_cover,
            "av_highlight":av_highlight,
            "with_subtitle":with_subtitle,
            "with_danmaku":with_danmaku,
            "with_reserve":with_reserve,
            "av_speed":av_speed,
        })
        return self.get_rest_data("发布直播回放片段","https://api.live.bilibili.com/xlive/app-blink/v1/anchorVideo/AnchorPublishVideoSlice",b)["data"]

class LiveVote(ToolBase):
    """直播投票"""

    def live_votePanel(self)->dict|None:
        """查询直播投票信息"""
        return self.get_rest_data("查询投票信息",f"https://api.live.bilibili.com/xlive/app-room/v1/dm/interaction/votePanel?room_id={self.roomid}")["data"]

    def live_voteHistory(self)->dict:
        """查询直播投票历史"""
        return self.get_rest_data("查询投票历史",f"https://api.live.bilibili.com/xlive/app-room/v1/dm/interaction/voteHistory?room_id={self.roomid}")["data"]

    def live_createVote(self,duration:int,question:str,options_a:str,options_b:str,template_id:int=0)->dict:
        """创建直播投票"""
        b={
            "duration":duration,
            "question":question,
            "options_a":options_a,
            "options_b":options_b,
        }
        if template_id:
            b["template_id"]=template_id
        return self.get_rest_data("创建直播投票","https://api.live.bilibili.com/xlive/app-room/v1/dm/interaction/createVote",self.add_csrf(b))["data"]

    def live_terminateVote(self,vote_id:int)->dict:
        """中断直播投票"""
        b=self.add_csrf({
            "interaction_id":vote_id,
            "room_id":self.roomid,
        })
        return self.get_rest_data("中断直播投票","https://api.live.bilibili.com/xlive/app-room/v1/dm/interaction/terminateVote",b)

class BiliLiveTools(DanmuTools,SpectatorTools,LiveTools,LiveDataTools,RoomTools,LiveReplay,LiveVote):
    """全部工具"""
