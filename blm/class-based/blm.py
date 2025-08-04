"""blw扩展
"""

import blw
import sys,time,re,argparse
from blw import GetDataError,WSClientError,log
from collections.abc import Generator
from typing import Any,Self

__all__=[
    "add_no_cmd_args",
    "read_text_continue_h",
    "SaveToFile",
    "BiliLiveExp",
    "BiliLiveBlackWordExp",
    "BiliLiveSaveExp",
    "BiliLiveMsg",
]

def add_no_cmd_args(cmd_args:list[dict],cmd_name_list:dict[str,str],help:Any=None)->list[dict]:
    """为cmd_args附加cmd参数
    cmd_args: 被附加参数选项字典的对象
    cmd_name_list: 一个cmd名称为键，帮助内容为值所组成的字典
    返回值: cmd_args参数输入的列表
    """
    if not isinstance(cmd_name_list,dict):
        raise TypeError("cmd_name_list需要一个键值对的字典")
    for name in cmd_name_list:
        cmd_args.append({
            "name":"--no-"+str(name),
            "help":f"关闭{cmd_name_list[name]}信息",
            "action":"store_true",
        })
    return cmd_args

def read_text_continue_h(path:str)->Generator[str,None,str]:
    """读取文件，并在读取过程中忽略#开头的文本"""
    i=0
    with open(path,"rt")as f:
        for l in f:
            t=l.rstrip("\r\n")
            if not t:
                continue
            if t[0]=="#":
                continue
            yield t
            i+=1
            if i>65535:
                return "条目过多"

class SaveToFile:
    """保存到文件，用于在print之类直接写入到文件的地方对写入的内容做点处理"""

    def __init__(self,path:str)->None:
        """初始化"""
        self.file=open(path,"at",encoding=blw.ENCODING,errors="xmlcharrefreplace",newline="\n")
        self.temp=""
    def __del__(self)->None:
        """删除时关闭文件"""
        self.close()
    def __enter__(self)->Self:
        """返回自身给上下文管理器"""
        return self
    def __exit__(self,exc_type,exc_val,exc_tb)->bool:
        """上下文管理器退出时关闭文件"""
        self.close()
        return False

    def close(self)->None:
        """关闭关联的文件"""
        self.file.close()
        self.temp=""
    @property
    def closed(self)->bool:
        """获取关联文件的关闭状态"""
        return self.file.closed
    def flush(self)->None:
        """刷新关联文件的写入缓冲区"""
        return self.file.flush()

    def format(self,data:str)->str:
        """处理字符串，默认直接返回"""
        return data
    def write(self,data:str)->int:
        """写入文件，调用format处理字符串"""
        self.temp+=data
        if (not self.temp.endswith(("\r","\n")))and len(self.temp)<8192:
            return len(data)
        d=self.format(self.temp)
        self.temp=""
        if isinstance(d,str):
            return self.file.write(d)
        return 0

class BiliLiveExp(blw.BiliLiveWS):
    """哔哩哔哩直播信息流一般基本扩展"""

    add_args:dict=[]
    """添加其它命令行参数"""
    up_uid:int=-65536
    """主播UID"""

    def error(self,d:Any=None,**v:Any)->None:
        """记录异常，附带该类的部分变量"""
        nodefkey={}
        if hasattr(self,"wbi_imgKey"):
            nodefkey["wbi_imgKey"]=self.wbi_imgKey
        if hasattr(self,"wbi_subKey"):
            nodefkey["wbi_subKey"]=self.wbi_subKey
        super().error(d,up_uid=self.up_uid,**nodefkey,**v)

    def other_arg_add(self,argp:argparse.ArgumentParser)->None:
        """添加其它命令行参数
        从self.add_args读取数据来添加
        """
        top_args=[]
        for i in self.add_args:
            if not isinstance(i,dict):
                continue
            if i.get("type")=="group" and len(i["list"])>0:
                tg=argp.add_argument_group(
                    title=i.get("title"),
                    description=i.get("desc")
                )
                blw.from_list_add_args(tg,i["list"])
            else:
                top_args.append(i)
        blw.from_list_add_args(argp,top_args)

    def get_room_init(self)->dict:
        """获取直播间初始化信息，若需要主播uid或者将短号转为原始房间号必须调用"""
        d=self.get_rest_data("获取直播间初始化信息","https://api.live.bilibili.com/room/v1/Room/room_init?id="+str(self.roomid))["data"]
        self.roomid=d["room_id"]
        self.up_uid=d["uid"]
        return d
    def get_room_info(self)->dict:
        """获取直播间信息"""
        return self.get_rest_data("获取直播间信息","https://api.live.bilibili.com/room/v1/Room/get_info?room_id="+str(self.roomid))["data"]
    def get_master_info(self)->dict:
        """获取主播信息"""
        return self.get_rest_data("获取主播信息","https://api.live.bilibili.com/live_user/v1/Master/info?uid="+str(self.up_uid))["data"]
    def get_play_url(self)->dict:
        """获取直播视频流"""
        return self.get_rest_data("获取直播视频流",f"https://api.live.bilibili.com/room/v1/Room/playUrl?cid={self.roomid}&platform=web&quality=4")["data"]

    def print_room_info(self)->None:
        """打印直播间信息"""
        ru=self.get_room_info()
        self.p("标题:",ru["title"])
        self.p("封面:",ru["user_cover"])
        self.p("背景图:",ru["background"])
        self.p("关键帧:",ru["keyframe"])
        self.p("《简介》:`",ru["description"],"`")
        self.p("分区:",ru["parent_area_name"],">",ru["area_name"])
        self.p("开始时间:",ru["live_time"])
        self.p("观看人数:",ru["online"])
        self.p("标签:",ru["tags"])
    def print_master_info(self)->None:
        """打印主播信息"""
        mi=self.get_master_info()
        mif=mi["info"]
        self.p("主播:",mif["uid"],f"({mif['uname']})")
        gdr=mif["gender"]
        if gdr==-1:
            gdr="保密"
        elif gdr==0:
            gdr="女"
        elif gdr==1:
            gdr="男"
        self.p("性别:",gdr)
        oflv=mif["official_verify"]
        self.p("认证:","无"if oflv["type"]==-1 else oflv["desc"])
        self.p("等级:",mi["exp"]["master_level"]["level"])
        self.p("粉丝数量:",mi["follower_num"])
        self.p("粉丝勋章:",mi["medal_name"])
        self.p("荣誉数量:",mi["glory_count"])
        self.p("直播间头像框:",mi["pendant"])
        rnw=mi["room_news"]
        self.p("主播公告:`",rnw["content"],"`",rnw["ctime"])
    def print_playurl(self)->None:
        """打印直播视频流信息"""
        d=self.get_play_url()
        self.p("当前画质代码:",d["current_quality"])
        self.p("可选画质:",d["accept_quality"])
        for i in d["durl"]:
            self.p(f"线路{i['order']}链接:",i["url"])

    def set_buvid3_4(self)->dict[str,str]:
        """设置buvid3和buvid4这两个Cookie，并返回数据本体"""
        d=self.get_rest_data("获取buvid3和buvid4","https://api.bilibili.com/x/frontend/finger/spi")["data"]
        self.cookies["buvid3"]=d["b_3"]
        self.cookies["buvid4"]=d["b_4"]
        return d

class BiliLiveBlackWordExp(BiliLiveExp):
    """屏蔽词命令行参数扩展"""

    def from_file_handle_shielding_words(self,path:str)->list[str]:
        """从文件处理屏蔽词"""
        l=[]
        try:
            for t in read_text_continue_h(path):
                l.append(t)
        except OSError as e:
            log.exception("读取屏蔽词时出现错误")
            raise ValueError("读取屏蔽词失败: "+str(e))
        return l
    def from_file_handle_blocking_rules(self,path:str)->list[re.Pattern[str]]:
        """从文件处理屏蔽规则"""
        l=[]
        try:
            for t in read_text_continue_h(path):
                l.append(re.compile(t))
        except OSError as e:
            log.exception("读取屏蔽规则时出现错误")
            raise ValueError("读取屏蔽规则失败: "+str(e))
        return l

    add_args=[
        {"name":"--shielding-words","help":"屏蔽词(完全匹配)","default":[],"type":from_file_handle_shielding_words,"metavar":"FILE"},
        {"name":"--blocking-rules","help":"屏蔽规则","default":[],"type":from_file_handle_blocking_rules,"metavar":"FILE"},
    ]

    @property
    def swd(self)->list[str]:
        """返回屏蔽词列表"""
        return self.args.shielding_words
    @property
    def brs(self)->list[re.Pattern[str]]:
        """返回屏蔽规则列表"""
        return self.args.blocking_rules

    def is_blocked_msg(self,msg:str)->bool:
        """检查输入的信息是否命中屏蔽规则"""
        if msg in self.swd:
            return True
        for si in self.swd:
            if si in msg:
                return True
        for bi in self.brs:
            if bi.search(msg):
                return True
        return False

class BiliLiveSaveExp(BiliLiveExp):
    """保存打印内容"""

    add_args=[
        {"name":"save-to-file","help":"保存打印内容到文件","type":SaveToFile,"metavar":"PATH"},
    ]

    def p(self,*t:Any)->None:
        """输出文本"""
        print(*t)
        if self.args.save_to_file:
            print(*t,file=self.args.save_to_file)

class BiliLiveMsg(BiliLiveExp):
    """启用"""

    add_args=[
        {"name":"no-show-room-info","help":"不显示房间信息","action":"store_false"},
        {"name":"no-show-master-info","help":"不显示主播信息","action":"store_false"},
        {"name":"get-room-playurl","help":"获取直播视频流","action":"store_true"},
        {"name":"--add-time","help":"建议命令处理添加时间显示","nargs":"?","const":"datetime","choices":["datetime","time","timestamp"]},
    ]

    def pct(self,name:str,*data:Any)->None:
        """统一按照一定样式输出cmd处理后文本
        额外拥有添加时间的功能
        """
        if not isinstance(name,str):
            raise TypeError("name必须为str")
        if isinstance(self.args.add_time,str):
            at=self.args.add_time
            if at=="datetime":
                t=time.strftime(blw.TIMEFORMAT)
            elif at=="time":
                t=time.strftime("%H:%M:%S")
            elif at=="timestamp":
                t=str(int(time.time()))
            else:
                t=""
            if t:
                self.p(t,f"[{name}]",*data)
                return
        self.p(f"[{name}]",*data)
    def start(self)->None:
        """带信息启动"""
        log.info("使用信息启动函数开始运行")
        log.debug(f"版本信息: {blw.VERSIONINFO}")
        a=self.pararg()
        self.p("获取数据…")
        if a.cookie:
            self.cookies.update(a.cookie)
        self.get_login_nav()
        if "buvid3" not in self.cookies:
            self.set_buvid3_4()
        try:
            ri=self.get_room_init()
        except GetDataError as e:
            self.p(str(e))
            sys.exit(1)
        self.p("直播间:",ri["room_id"],""if ri["short_id"]==0 else f"({ri['short_id']})")
        self.p("用户ID:",ri["uid"])
        lis=ri["live_status"]
        lsm=str(lis)
        if lis==0:
            lsm="未开播"
        elif lis==1:
            lsm="直播中"
        elif lis==2:
            lsm="轮播中"
        self.p("状态:",lsm)
        ltt=""
        if ri["live_time"]>0:
            ltt=time.strftime(blw.TIMEFORMAT,time.localtime(ri["live_time"]))
        else:
            ltt="0 (未开播)"
        self.p("开播时间:",ltt)
        del lis,lsm,ltt,ri
        if a.no_show_room_info:
            self.print_room_info()
        if a.no_show_master_info:
            self.print_master_info()
        if a.get_room_playurl:
            self.print_playurl()
        try:
            info=self.get_ws_info()
        except GetDataError as e:
            self.p(str(e))
            sys.exit(1)
        except KeyboardInterrupt:
            self.p("获取信息流操作被中断")
            sys.exit(0)
        self.p("启动客户端…")
        try:
            self.run_blw_client(info["wss_host"],info["token"])
        except WSClientError as e:
            self.p(str(e))
            sys.exit(1)
        except KeyboardInterrupt:
            self.p("关闭")
            self.print_cmd_count()
            sys.exit(0)
