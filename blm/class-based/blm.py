"""blw扩展
"""

import sys,time
import blw
from blw import GetDataError,WSClientError,log

class BiliLiveExp(blw.BiliLiveWS):
    """哔哩哔哩直播信息流一般基本扩展"""

    add_args:dict=[]

    def other_arg_add(self,argp:"argparse.ArgumentParser")->None:
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
                self.from_list_add_args(tg,i["list"])
            else:
                top_args.append(i)
        self.from_list_add_args(argp,top_args)

    def get_room_init(self)->dict:
        """获取直播间初始化信息，若需要主播uid或者将短号转为原始房间号必须调用"""
        d=self.get_rest_data("获取直播间初始化信息","https://api.live.bilibili.com/room/v1/Room/room_init?id="+str(self.roomid))["data"]
        self.roomid=d["room_id"]
        self.up_uid=d["uid"]
        return d
    def get_room_info(self)->dict:
        """获取直播间信息"""
        return self.get_rest_data("获取直播间信息","https://api.live.bilibili.com/room/v1/Room/get_info?room_id="+str(self.up_uid))["data"]
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
        d=get_playurl(rmid)
        self.p("当前画质代码:",d["current_quality"])
        self.p("可选画质:",d["accept_quality"])
        for i in d["durl"]:
            self.p(f"线路{i['order']}链接:",i["url"])

class BiliLiveMsg(BiliLiveExp):
    """启用"""

    add_args=[
        {"name":"no-show-room-info","help":"不显示房间信息","action":"store_false"},
        {"name":"no-show-master-info","help":"不显示主播信息","action":"store_false"},
        {"name":"get-room-playurl","help":"获取直播视频流","action":"store_true"},
        {"name":"--add-time","help":"建议命令处理添加时间显示","nargs":"?","const":"datetime","choices":["datetime","time","timestamp"]},
    ]

    def pct(self,name:str,*data)->None:
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
        if a.sessdata:
            self.cookies["SESSDATA"]=a.sessdata
            self.get_uid()
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
            sys.exit(0)
