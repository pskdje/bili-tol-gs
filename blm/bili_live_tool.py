# 开始结束直播
"""bili live tool
因为网页开播太消耗性能所以开发的开播关播脚本
除此之外还集成了一些功能。
参考: https://github.com/SocialSisterYi/bilibili-API-collect
"""

import sys
import typing
import argparse
from pathlib import Path
import requests
import bili_live_msg as blm
import bili_live_ws as blw

__path__=[]
DEBUG=blw.DEBUG
log=blw.log
ls_uid=-65536
head={
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.6",
    "DNT": "1",
    "Origin": "https://live.bilibili.com/",
    "Referer": "https://live.bilibili.com/",
    "User-Agent": blw.UA,
}

def __getattr__(name):
    log.debug(f"在blt获取blw的'{name}'",stacklevel=2)
    return getattr(blw,name)

class LiveLink(typing.NamedTuple):
    """哔哩哔哩直播推流地址容纳"""
    addr:str
    code:str
    def __str__(self):
        return self.addr+self.code

def get_cookie(path:str,type:str):
    """获取cookie数据"""
    p=Path(path)
    log.info(f"cookie文件的路径: {p}")
    if not p.is_file():
        raise ValueError("不是有效的文件路径: "+str(p))
    if p.stat().st_size>1048576:
        raise ValueError("文件大小大于1兆字节")
    d=p.read_text()
    log.debug(f"cookie文件内容:\n{d}")
    t=type
    if not isinstance(t,str):
        raise TypeError("解析类型错误")
    if t=="wkv":
        return cookie_KV(d)
    else:
        raise TypeError("未知的解析类型")

def cookie_KV(t:str):
    """document.cookie或Cookie头这类的解析器"""
    d={}
    for i in t.split(";"):
        k,v=i.strip().split("=",1)
        d[k]=v
    return d

def post_rest_data(url:str,data:dict|bytes,tip:str="",header:dict=None,**oa)->dict:
    """发送POST请求
	url: 目标链接
	data: 要发送的数据
	tip: 在日志和异常中使用的提示
	header: 请求头
    """
    he={}
    if isinstance(header,dict):
        he=header
    try:
        r=requests.post(
            url,
            headers=head|he,
            data=data,
            **oa
        )
    except Exception:
        blw.error()
        exit(f"获取{tip}信息失败")
    log.debug(r.text,stacklevel=2)
    if r.status_code!=200:
        print(r.text)
        blw.save_http_error(r,"状态码")
        exit("服务器错误")
    try:
        d=r.json()
    except:
        blw.save_http_error(r,f"{tip}json数据")
        exit(f"无法解析{tip}数据")
    if d["code"]!=0:
        print(f"{tip}接口返回的code不为0")
        blw.save_http_error(r,"键code")
        exit(f"{d['code']} - {d['message']}")
    return d["data"]

class BiliLive:
    """基本开播功能"""
    uid:int=0
    def __init__(self,roomid:int,cookie:dict[str,str]):
        """init"""
        c=cookie
        self.roomid=roomid
        self.cookie={
            "SESSDATA": cookie["SESSDATA"],
            "bili_jct": cookie["bili_jct"]
        }
        def ac(k):
            if k not in c:return
            self.cookie[k]=c[k]
        ac("bili_ticket")
        ac("buvid3")
        ac("buvid4")
        ac("b_nut")
    @property
    def csrf(self)->str:
        return self.cookie["bili_jct"]
    def pm(self,*a,**p)->typing.NoReturn:
        """打印信息\n重写此方法可以控制输出方法"""
        print(*a,**p)
    def pause(self,info:str)->typing.NoReturn:
        """等待用户操作\n重写此方法可以实现其它等待方法"""
        input(info)
    def startLive(self,area:int)->LiveLink:
        """开始直播，参见: https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/live/manage.md#%E5%BC%80%E5%A7%8B%E7%9B%B4%E6%92%AD"""
        b={
            "room_id": self.roomid,
            "area_v2": area,
            "platform": "web_link",
            "csrf_token": self.csrf,
            "csrf": self.csrf,
        }
        d=post_rest_data("https://api.live.bilibili.com/room/v1/Room/startLive",
            b,"startLive",cookies=self.cookie)
        self.liveid:str=d["live_key"]
        return LiveLink(d["rtmp"]["addr"],d["rtmp"]["code"])
    def stopLive(self)->dict:
        """结束直播，参见: https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/live/manage.md#%E5%85%B3%E9%97%AD%E7%9B%B4%E6%92%AD"""
        b={
            "room_id": self.roomid,
            "platform": "web_link",
            "csrf_token": self.csrf,
            "csrf": self.csrf,
        }
        d=post_rest_data("https://api.live.bilibili.com/room/v1/Room/stopLive",
            b,"stopLive",cookies=self.cookie)
        return d
    def stopLiveData(self)->dict:
        """停止直播后的提示信息，分析自网页端开播。"""
        return blm.get_rest_data("https://api.live.bilibili.com/xlive/app-blink/v1/live/StopLiveData",
            "stopLiveData",head,cookies=self.cookie,params={"live_key":self.liveid})
    def connectDanm(self,args:argparse.Namespace)->typing.NoReturn:
        """连接信息流"""
        op=vars(args)
        op["sessdata"]=self.cookie["SESSDATA"]
        if self.uid>0:
            op["uid"]=self.uid
        if not op["roomid"]>0:
            op["roomid"]=self.roomid
        o=argparse.Namespace(**op)
        log.debug(f"经过替换的参数列表: {o}")
        blw.start(self.roomid,o)
    def get_myinfo(self):
        """获取登录用户信息，参见: https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/user/info.md#%E7%99%BB%E5%BD%95%E7%94%A8%E6%88%B7%E7%A9%BA%E9%97%B4%E8%AF%A6%E7%BB%86%E4%BF%A1%E6%81%AF"""
        d=blm.get_rest_data("https://api.bilibili.com/x/space/myinfo","get_myinfo",head,cookies=self.cookie)
        self.uid=int(d["mid"])
        return d
    def runDanmu(self)->None:
        """运行信息流组件"""
        run=True
        err=0
        while run:
            try:
                self.connectDanm(self.o)
            except SystemExit as e:
                err+=1
                log.info(f"错误提示: '{e}',信息流错误计数: {err}")
            except KeyboardInterrupt:
                run=False
                log.info("中断键按下，停止信息流组件")
                raise
            if err>1:
                self.pm("[danm]","错误次数过多，停止弹幕组件")
                break
            self.pm("[danm]","异常退出，重新启动信息流组件")
    def run(self,area:int,o:argparse.Namespace):
        """运行"""
        log.info(f"准备开始直播，直播间: {self.roomid},分区ID: {area}")
        self.o=o
        self.pm("[start]","分区ID:",area)
        sa=self.startLive(area)
        self.pm("[link]","推流地址:",sa.addr)
        self.pm("[link]","推流参数:",sa.code)
        if o.connect_danmu:
            if o.wait_clip:
                self.pause("等待复制推流信息")
            log.info("连接信息流")
            self.pm("[tip]","已启用信息流，按下中断键关闭信息流并继续执行。")
            self.pm("[danm]","连接信息流")
            try:
                self.runDanmu()
            except KeyboardInterrupt:
                pass
            else:
                self.pause("信息流组件退出，按下回车关闭直播间")
        else:
            log.info("等待关闭直播")
            self.pause("按下回车关闭直播间")
        log.info("进行停止直播")
        so=self.stopLive()
        self.pm("[stop]","停止直播，直播状态是否变化:",so["change"])
        sd=self.stopLiveData()
        self.pm("[liveData]",f"直播时长{self.liveTimeStr(sd['LiveTime'])}，新增关注{sd['AddFans']}人，新获得粉丝勋章{sd['NewFansClub']}人，直播收益{sd['HamsterRmb']}元，弹幕数量{sd['DanmuNum']}条，累计{sd['WatchedCount']}人观看，最大在线(推测)所有观众:{sd['MaxOnline']}")
    def liveTimeStr(self,time:int)->str:
        """计算直播时长"""
        h=int(time/3600%24)
        m=int(time/60%60)
        s=int(time%60)
        m=f"0{m}"if m<10 else str(m)
        s=f"0{s}"if s<10 else str(s)
        return f"{h}时{m}分{s}秒"

class BiliLiveTool(BiliLive):
    """哔哩哔哩直播复杂组件"""
    def __init__(self,cookie):
        """tool"""
        super().__init__(1,cookie)
        self.roomid=self.get_roomid()
    def get_roomid(self):
        """获取登录会话的直播间，直播个人中心获得。"""
        d=blm.get_rest_data("https://api.live.bilibili.com/xlive/app-blink/v1/streamingRelay/relayInfo",
            "get_roomid",head,cookies=self.cookie)
        return d["room_id"]

def pararg(s:list):
    """参数"""
    global DEBUG
    a=[
        {"name":"cookie","help":"提供cookie文件","required":True},
        {"name":"cookie-type","help":"指定cookie解析方法","default":"wkv"},
        {"name":"area","help":"要开播的分区ID","type":int},
        {"name":"connect-danmu","help":"连接信息流","action":"store_true"},
        {"name":"wait-clip","help":"等待复制","action":"store_true"},
    ]
    o=blw.pararg(a,args=s,
        desc="通过bili_live_tool的main启动的话，可以忽略直播间ID和用户会话要求。但是必须提供cookie文件，否则无法获取信息。")
    DEBUG=blw.DEBUG
    return o

def main():
    global ls_uid
    log.info("bili_live_tool 开始运行")
    o=pararg(sys.argv[1:]+["--","0"])# 使用blw的参数解析必须提供roomid，这是因为原本blw的设计就只是为了获取信息流。可以通过提供args参数绕过。
    c=get_cookie(o.cookie,o.cookie_type)
    log.debug(f"cookie解析类型:{o.cookie_type},解析结果:{c}")
    b=BiliLiveTool(c)
    if DEBUG:
        print("命令行参数:",o)
        blw.set_log()
        blw.set_wslog()
    if o.shielding_words:
        blw.shielding_words(o.shielding_words)
    if o.blocking_rules:
        blw.blocking_rules(o.blocking_rules)
    mi=b.get_myinfo()
    ls_uid=mi["mid"]
    if o.atirch:
        r_ich=blw.import_cmd_handle()
        blw.idp("导入命令处理的结果:",r_ich)
        del r_ich
    b.run(o.area,o)
    log.info("bili_live_tool 停止运行")

if __name__=="__main__":
    main()
